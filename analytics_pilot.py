from src.gui import launch
import coloredlogs
from src.configuration import read_configuration
import sys
import argparse
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

if __name__ == '__main__':
    client_config = ClientConfig()
    client = Client(client_config)
    client.refresh()

    client.add_progress_hook(print_status_info)
    app_update = client.update_check(client_config.APP_NAME, '0.1')
    print(app_update)
    if app_update is not None:

        app_update.download()
        if app_update.is_downloaded():
            print('downloaded, extracting')
            app_update.extract_overwrite()
        if app_update.is_downloaded():
            print('extracted, restarting')
            app_update.extract_restart()
    args = parse_args(sys.argv)

    config=read_configuration()
    coloredlogs.install(level=config.get('logging').get('level'), stream=sys.stdout, fmt='%(asctime)s %(name)s %(levelname)s %(message)s')

    launch()