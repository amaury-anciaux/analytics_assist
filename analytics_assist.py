import logging
import sys
import argparse
from src.gui import launch
from src.configuration import read_configuration
from src.system import set_autostart, is_frozen_app


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


if __name__ == '__main__':
    args = parse_args(sys.argv)

    setup_logging()

    autostart()
    launch()