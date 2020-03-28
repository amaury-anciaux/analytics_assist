import logging
import wx
import wx.dataview as dv
from src.configuration import read_configuration
from src.watcher import start_filewatch
import coloredlogs
import sys
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
        self.SetStatusText("Welcome to wxPython!")
        self.logger = logging.getLogger(__name__)

    def update_tree(self, workflow_path, data):
        self.tree.DeleteAllItems()
        if data != True:
            for i in data:
                self.tree.AppendItem([str(workflow_path), i['error_level'], i['location'], i['message'], i['rule']])
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
        helloItem = fileMenu.Append(-1, "&Hello...\tCtrl-H",
                "Help string shown in status bar for this menu item")
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


    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)


    def OnHello(self, event):
        """Say hello to the user."""
        wx.MessageBox("Hello again from wxPython")


    def OnAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox("This is a wxPython Hello World sample",
                      "About Hello World 2",
                      wx.OK|wx.ICON_INFORMATION)


def launch():
    # Fix the High DPI setting on Windows
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
    except:
        pass

    # Create app
    app = wx.App()
    frm = MainFrame(None, title='Analytics Pilot')
    frm.Show()

    # Start watcher
    thread = start_filewatch(frm.update_tree)

    app.MainLoop()
    thread.stop()
    thread.join() # Blocks main until observer thread terminates
