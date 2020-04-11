import toml
import logging
import wx
from pathlib import Path

config_path = Path('config')
user_file = config_path / Path('config.toml')

def get_workflow_path():
    dlg = wx.DirDialog(None, "Choose input directory", "", wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
    out = dlg.ShowModal()
    if out == wx.ID_OK:
        return dlg.GetPath()
    else:
        wx.MessageDialog(None, 'No directory chosen. The application will not monitor any workflow.', 'Warning',
                         wx.OK | wx.ICON_WARNING).ShowModal()
        return ''

def get_source():
    dlg = wx.SingleChoiceDialog(None, 'Please choose a source software', 'Source', ['Knime', 'Alteryx'], wx.OK)
    out = dlg.ShowModal()
    if out == wx.ID_OK:
        return dlg.GetStringSelection()


class Configuration:
    def __init__(self, path=user_file):
        self.logger = logging.getLogger(__name__)

        # If config file doesn't exist, create it with defaults
        if not config_path.exists():
            Path.mkdir(config_path)

        if not user_file.exists():
            app = wx.App()
            with open(user_file, 'w') as f:
                default_config = {'source': get_source(),
                                  'logging': {'level': 'ERROR'},

                                  'file_watch': {'paths': [get_workflow_path()]}}

                toml.dump(default_config, f)
                self.logger.info(f"Configuration file created in {user_file}")

        # Load configuration
        self.config = toml.load(path)
        source = self.config.get('source')
        if source == 'Knime':
            self.config['file_watch']['patterns'] = ['*.knime', '*.xml']
        elif source == 'Alteryx':
            self.config['file_watch']['patterns'] = ['*.yxwz', '*.yxmd', '*.yxmc']
        else:
            raise Exception(f'Source {source} unknown.')

    def get_configuration(self):
        return self.config


config = None

def read_configuration(path=user_file):
    global config
    if config is None:
        config = Configuration(path=user_file)
    return config.get_configuration()