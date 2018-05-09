import atexit

from multiprocessing import Queue, Process, Event, freeze_support

from .log_process import stop_process, run_process
from .config import CONFIGS, basicConfig

__all__ = ['basicConfig', 'Logger']


freeze_support()


class Logger(object):

    root = None
    manager = None

    def __init__(self, name=None, level=None):
        self.name = name
        self.process_alive = Event()
        self.process_queue = Queue()
        self.process = None
        # self.start_process()

        if level is not None:
            self.setLevel(level)

    def start_process(self):
        """Start running the separate process which does the actual logging."""
        self.stop_process()

        # Create the separate Process
        self.process_alive.set()
        self.process = Process(name="Logger-"+self.name, target=run_process,
                               args=(self.process_alive, self.process_queue, self.name),
                               kwargs={'configs': CONFIGS})
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
        if not self.process:
            self.start_process()
        self.process_queue.put_nowait([cmd, args, kwargs])

    def __getattr__(self, item):
        """If an attribute is not found assume it is a logging.Logger attribute and make that a command to be run in
        the separate process.
        """
        def func(*args, **kwargs):
            self._add_command(item, *args, **kwargs)
        return func

    def __del__(self):
        try:
            self.stop_process()
        except:
            pass
