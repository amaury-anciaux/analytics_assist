import logging
import sys
import argparse
import os

from src.gui import launch
from src import __version__
from src.configuration import read_configuration
from src.system import set_autostart, is_frozen_app
from pyupdater.client import Client
from client_config import ClientConfig


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


def print_status_info(info):
    total = info.get(u'total')
    downloaded = info.get(u'downloaded')
    status = info.get(u'status')
    print(downloaded, total, status)

def update():
    logger = logging.getLogger(__name__)
    client_config = ClientConfig()
    client = Client(client_config)
    client.refresh()

    client.add_progress_hook(print_status_info)
    app_update = client.update_check(client_config.APP_NAME, __version__)

    if app_update is not None:
        logger.info(f'There is an update for the app, current version: {__version__}, new version: {app_update.version}')
        app_update.download()
        if app_update.is_downloaded():
            logger.info('Extracting and restarting')
            app_update.extract_restart()
    else:
        logger.info(
            f'App is up to date, current version: {__version__}')

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

    # fh = logging.FileHandler('debug.log')
    # fh.setLevel(logging.DEBUG)
    # logging_formatter = logging.Formatter(log_format)
    # fh.setFormatter(logging_formatter)
    # logging.getLogger().addHandler(fh)

    config=read_configuration()
    logger.info(f"Logging level set to {config.get('logging').get('level')}")
    logger.setLevel(config.get('logging').get('level'))

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

if __name__ == '__main__':
    # Changes to application directory, to ensure subsequent paths can be relative
    os.chdir(os.path.dirname(sys.argv[0]))

    args = parse_args(sys.argv)

    setup_logging()
    update()
    autostart()
    launch()