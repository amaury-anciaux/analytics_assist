import logging
import sys
import coloredlogs
import argparse

from src.gui import launch
import wx
from src import __version__
from src.configuration import read_configuration
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

if __name__ == '__main__':
    args = parse_args(sys.argv)

    # Set logs
    log_format = '%(asctime)s %(hostname)s %(name)s[%(process)d] %(levelname)s %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)

    coloredlogs.install(level=logging.INFO, stream=sys.stdout, fmt=log_format)
    logger = logging.getLogger(__name__)

    config=read_configuration()
    logger.info(f"Logging level set to {config.get('logging').get('level')}")
    coloredlogs.set_level(config.get('logging').get('level'))

    # Update the app
    update()

    launch()