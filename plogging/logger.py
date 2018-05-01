import atexit

from multiprocessing import Queue, Process, Event

from .log_process import stop_process, run_process
from .config import CONFIGS, basicConfig

__all__ = ['ALL_LOGGERS', 'basicConfig', 'getLogger', 'Logger']


ALL_LOGGERS = {}


def getLogger(name=None):
    """Get or create the logger with the given name."""
    try:
        return ALL_LOGGERS[name]
    except KeyError:
        return Logger(name=name)  # Logger.set_name stores the logger in ALL_LOGGERS


class Logger(object):
    def __init__(self, name=None, level=None):
        self._name = name
        self.process_alive = Event()
        self.process_queue = Queue()
        self.process = None
        self.set_name(name)
        self.start_process(name=name)

        if level is not None:
            self.setLevel(level)

    def get_name(self):
        """Return the name."""
        return self._name

    def set_name(self, name):
        """Set the name."""
        self._name = name
        ALL_LOGGERS[self._name] = self
        if self.process:
            self._add_command('set_name', name)

    name = property(get_name, set_name)

    def start_process(self, name=None):
        """Start running the separate process which does the actual logging."""
        if name is not None:
            self.set_name(name)
        self.stop_process()

        # Create the separate Process
        self.process_alive.set()
        self.process = Process(name=self.name, target=run_process,
                               args=(self.process_alive, self.process_queue, self.get_name(),
                                     CONFIGS['basic_config'], CONFIGS['file_config'], CONFIGS['dict_config']))
        self.process.daemon = True
        self.process.start()

        atexit.register(self.stop_process)

    def stop_process(self):
        """Stop running the process.

        Warning:
            This will also stop the logging
        """
        try:
            atexit.unregister(self.stop_process)
        except:
            pass
        stop_process(self.process, self.process_alive, self.process_queue)

    def _add_command(self, cmd, *args, **kwargs):
        self.process_queue.put([cmd, args, kwargs])

    def __getattr__(self, item):
        """If an attribute is not found assume it is a logging.Logger attribute and make that a command to be run in
        the separate process.
        """
        def func(*args, **kwargs):
            self.process_queue.put([item, args, kwargs])
        return func

    def __del__(self):
        try:
            self.stop_process()
        except:
            pass
