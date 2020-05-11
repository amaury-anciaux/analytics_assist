import logging
from pyupdater.client import Client
from client_config import ClientConfig
from src import __version__
import schedule
import threading
from src.system import is_frozen_app

def update_progress(info, d):
    total = info.get(u'total')
    downloaded = info.get(u'downloaded')
    d.Update(downloaded / total * 100)


def update():
    logger = logging.getLogger(__name__)
    if not is_frozen_app():
    #if False:
        logger.info('App not frozen, app update ignored.')
    else:
        #d = show_progress_window()
        # app=wx.GetApp()
        # d=wx.ProgressDialog('Updating Analytics Assist', 'Checking for updates, the application will restart automatically.')
        # d.Show()
        logger = logging.getLogger(__name__)
        client_config = ClientConfig()
        client = Client(client_config)
        client.refresh()

        client.add_progress_hook(lambda x: update_progress(x, d))
        app_update = client.update_check(client_config.APP_NAME, __version__)

        if app_update is not None:
            logger.info(
                f'There is an update for the app, current version: {__version__}, new version: {app_update.version}')
            app_update.download()
            if app_update.is_downloaded():
                logger.info('Extracting and restarting')
                app_update.extract_restart()
                #d.Destroy()
        else:
            logger.info(
                f'App is up to date, current version: {__version__}')
            #d.Destroy()


def start_scheduled_update():
    schedule.run_pending()
    threading.Timer(60, start_scheduled_update).start()

def init_update():
    update()
    schedule.every().day.at("04:00").do(update)
    start_scheduled_update()