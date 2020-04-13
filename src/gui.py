import logging
import wx
import wx.adv
import wx.dataview as dv
from src.configuration import read_configuration
from src.watcher import start_filewatch
from src.analyzer import analyze_workflow
from src import __version__
from pathlib import Path
import ctypes


class CheckResultModel(dv.PyDataViewModel):
    def __init__(self, data):
        dv.PyDataViewModel.__init__(self)
        self.data = data
        #self.objmapper.UseWeakRefs(True)

    #-------------------- REQUIRED FUNCTIONS -----------------------------
    def GetColumnCount(self):
        return 3

    def GetColumnType(self, col):
        mapper = { 0 : 'string',
                   1 : 'string',
                   2 : 'string',
                   }
        return mapper[col]

    def GetChildren(self, parent, children):
        if not parent:
            for check in self.data:
                children.append(self.ObjectToItem(check))
            return len(self.data)

        # node = self.ItemToObject(parent)
        # if isinstance(node, Genre):
        #     for song in node.songs:
        #         children.append(self.ObjectToItem(song))
        #     return len(node.songs)
        return 0

    def IsContainer(self, item):
        if not item:
            return True
        else:
            return False

    def GetParent(self, item):
        if not item:
            return dv.NullDataViewItem
        #parentObj = self.ItemToObject(item).parent
        #if parentObj is None:
        #    return wx.dataview.NullDataViewItem
        else:
            return dv.NullDataViewItem

    def GetValue(self, item, col):
        node = self.ItemToObject(item)
        if not item:
            return None
        else:
            return 'test'


class MainFrame(wx.Frame):
    """
    A Frame that says Hello World
    """

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(MainFrame, self).__init__(*args, **kw)
        icon = wx.Icon('icon.png')
        self.SetIcon(icon)
        self.source = config = read_configuration().get('source')


        # create a panel in the frame
        pnl = wx.Panel(self)
        self.SetSize(1000,800)
        # and create a sizer to manage the layout of child widgets
        sizer = wx.BoxSizer(wx.VERTICAL)

        # DataViewCtrl is the most flexible, but requires to bind a data model
        self.tree = dv.DataViewListCtrl(pnl, style=wx.dataview.DV_ROW_LINES)
        data = ['a', 'b']
        m = CheckResultModel(data)
        t2=dv.DataViewCtrl()
        #t2.AssociateModel(m)
        c1=self.tree.AppendTextColumn("Workflow", width= wx.COL_WIDTH_AUTOSIZE)
        c2 = self.tree.AppendTextColumn("Severity", width=wx.COL_WIDTH_AUTOSIZE)
        c2=self.tree.AppendTextColumn("Location", width= wx.COL_WIDTH_AUTOSIZE)
        c2 = self.tree.AppendTextColumn("Message", width=wx.COL_WIDTH_AUTOSIZE)
        c3=self.tree.AppendTextColumn("Rule", width= wx.COL_WIDTH_AUTOSIZE)

        #sizer.Add(tree, wx.SizerFlags().Border(wx.TOP | wx.LEFT, 25))
        sizer.Add(self.tree, 1, wx.EXPAND, 0)

        pnl.SetSizer(sizer)


        # create a menu bar
        self.makeMenuBar()

        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText("")
        self.Bind(wx.EVT_ICONIZE, self.onMinimize)
        self.Bind(wx.EVT_CLOSE, self.onMinimize)
        self.logger = logging.getLogger(__name__)

        self.tbIcon = TaskBarIcon(self, 'icon.png')

    def update_tree(self, workflow_path, data):
        nb_rows=self.tree.GetItemCount()
        to_delete=[]
        for i in range(nb_rows-1, -1, -1):
            if self.tree.GetTextValue(i, 0)==str(workflow_path):
                to_delete.append(i)

        for i in to_delete:
            self.tree.DeleteItem(i)

        if data != True:
            for i in data:
                self.tree.AppendItem([str(workflow_path), i['error_level'], i['location'], i['message'], i['rule']])
            self.tbIcon.ShowBalloon("Analytics Assist", f"{len(data)} error(s) were detected in workflow \"{workflow_path.name}\"",
                             flags=wx.ICON_ERROR)
            self.RequestUserAttention()
        self.tree.Refresh()


    def clear_tree(self):
        self.tree.DeleteAllItems()
        self.tree.Refresh()


    def makeMenuBar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        """

        # Make a file menu with Hello and Exit items
        fileMenu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        helloItem = fileMenu.Append(-1, "&Clear\tCtrl-C",
                "Clears all workflow information.")
        openItem = fileMenu.Append(-1, "&Scan workflow...\tCtrl-S",
                                    "Manually scan a workflow.")
        fileMenu.AppendSeparator()
        # When using a stock ID we don't need to specify the menu item's
        # label
        exitItem = fileMenu.Append(wx.ID_EXIT)

        # Now a help menu for the about item
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.OnHello, helloItem)
        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)
        self.Bind(wx.EVT_MENU, self.OnScan, openItem)


    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.tbIcon.Destroy()
        self.Close(True)


    def OnHello(self, event):
        """Say hello to the user."""
        self.clear_tree()


    def OnAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox(f"Analytics Assist by Data@Work\nhttps://www.data-at-work.ch\nVersion: {__version__}\nIcons by Icons8: https://icons8.com",
                      "Analytics Assist",
                      wx.OK|wx.ICON_INFORMATION)

    def onMinimize(self, event):
        """
        When minimizing, hide the frame so it "minimizes to tray"
        """
        self.Hide()

    def OnScan(self, event):
        if self.source == 'Alteryx':
            dlg = wx.FileDialog(self, "Choose workflow")
        else:
            dlg = wx.DirDialog(None, "Choose workflow directory", "", wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)

        out = dlg.ShowModal()
        if out == wx.ID_OK:
            self.update_tree(Path(dlg.GetPath()), analyze_workflow(dlg.GetPath()))


def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.Append(item)
    return item


class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame, path):
        self.frame = frame
        super(TaskBarIcon, self).__init__()
        icon = wx.Icon(path)
        self.SetIcon(icon, 'Restore')

        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Open', self.on_left_down)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu


    def on_left_down(self, event):
        self.frame.Show()
        self.frame.Raise()
        self.frame.Restore()


    def on_exit(self, event):
        self.frame.Destroy()
        wx.CallAfter(self.Destroy)
        self.frame.Close()


def launch():
    # Fix the High DPI setting on Windows
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
    except:
        pass

    # Create app
    app = wx.App()
    frm = MainFrame(None, title='Analytics Assist')
    frm.Show()

    # Start watcher
    thread = start_filewatch(frm.update_tree)

    app.MainLoop()
    thread.stop()
    thread.join() # Blocks main until observer thread terminates
