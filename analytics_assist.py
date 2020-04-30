import logging
import sys
import argparse
import wx
from src.gui import launch
from src import __version__
from src.configuration import read_configuration
from src.system import set_autostart, is_frozen_app
from pyupdater.client import Client
from client_config import ClientConfig

import schedule
import threading

def parse_args(argv):
    """
    Parse command-line args.
    """
    usage = ("%(prog)s [options]\n"
             "\n"
             "You can also run: python setup.py nosetests")
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument("--debug", help="increase logging verbosity",
                        action="store_true")
    parser.add_argument("-c", "--config",
                        help="specify config file")
    return parser.parse_args(argv[1:])


def update_progress(info, d):
    total = info.get(u'total')
    downloaded = info.get(u'downloaded')
    d.Update(downloaded/total*100)

def update():
    logger = logging.getLogger(__name__)
    if not is_frozen_app():
        logger.info('App not frozen, app update ignored.')
    else:
        app=wx.App()
        d=wx.ProgressDialog('Updating Analytics Assist', 'Checking for updates, the application will restart automatically.')
        d.Show()
        logger = logging.getLogger(__name__)
        client_config = ClientConfig()
        client = Client(client_config)
        client.refresh()

        client.add_progress_hook(lambda x: update_progress(x, d))
        app_update = client.update_check(client_config.APP_NAME, __version__)

        if app_update is not None:
            logger.info(f'There is an update for the app, current version: {__version__}, new version: {app_update.version}')
            app_update.download()
            if app_update.is_downloaded():
                logger.info('Extracting and restarting')
                app_update.extract_restart()
                d.Destroy()
        else:
            logger.info(
                f'App is up to date, current version: {__version__}')
            d.Destroy()

def get_stream_handler():
    for h in logging.getLogger().handlers:
        if isinstance(h, logging.StreamHandler):
            return h
    return logging.StreamHandler()

def setup_logging():
    log_format = '%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s'
    ch = get_stream_handler()
    logging_formatter = logging.Formatter(log_format)
    ch.setFormatter(logging_formatter)
    logging.getLogger().addHandler(ch)
    logger = logging.getLogger(__name__)

    config=read_configuration()
    logger.info(f"Logging level set to {config.get('logging').get('level')}")
    ch.setLevel(config.get('logging').get('level'))

    if config.get('logging').get('level') == 'DEBUG':
        fh = logging.FileHandler('analytics_assist.log')
        fh.setLevel(logging.DEBUG)
        logging_formatter = logging.Formatter(log_format)
        fh.setFormatter(logging_formatter)
        logging.getLogger().addHandler(fh)

def autostart():
    logger = logging.getLogger(__name__)
    config = read_configuration()
    if not is_frozen_app():
        logger.info('App not frozen, auto start ignored.')
    else:
        if config.get('auto_start', True):
            logger.info('Setting auto-start.')
            set_autostart(True)
        else:
            logger.info('Removing auto-start.')
            set_autostart(False)


def start_scheduled_update():
    schedule.run_pending()
    threading.Timer(60, start_scheduled_update).start()


if __name__ == '__main__':
    args = parse_args(sys.argv)

    setup_logging()
    update()

    schedule.every().day.at("04:00").do(update)
    start_scheduled_update()

    autostart()
    launch()