import logging
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from pathlib import Path
from src.configuration import read_configuration
from src.analyzer import analyze_workflow


class MyHandler(PatternMatchingEventHandler):
    def __init__(self, source, callback, *args, **kw):
        # ensure the parent's __init__ is called
        super(MyHandler, self).__init__(*args, **kw)
        self.files_last_times_processed = {}
        self.logger = logging.getLogger(__name__)
        self.source = source
        self.callback = callback

    def on_modified(self, event):
        now = time.time()
        self.logger.debug(f'Event detected on file: {event.src_path}')
        if self.source == 'Knime':
            path = find_Knime_workflow_root(event.src_path)
        else:
            path = Path(event.src_path)
        self.logger.debug(f'Path used: {path}')
        last_time_processed = self.files_last_times_processed.get(path)

        if last_time_processed is not None:
            if now - last_time_processed > 1:
                self.files_last_times_processed[path] = now
                self.callback(path, analyze_workflow(path))
        else:
            self.files_last_times_processed[path] = now
            self.callback(path, analyze_workflow(path))


def start_filewatch(callback):
    logger = logging.getLogger(__name__)
    config = read_configuration()
    path = config.get('file_watch').get('paths')[0]
    patterns = config.get('file_watch').get('patterns')

    logger.info(f'Start watching files in {path}, patterns {patterns}')
    event_handler = MyHandler(patterns=patterns, source=config.get('analyzer').get('source'), callback=callback)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start() # Thread starts
    return observer


def find_Knime_workflow_root(path):
    p = Path(path)
    for i in p.parents:
        if (i / 'workflow.knime').exists() and not (i / 'settings.xml').exists():
            return i
    return False

