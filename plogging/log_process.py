import os
import logging
import logging.config

from multiprocessing import Queue, Process, Event

try:
    import psutil
except ImportError as err:
    # _, _, exc_tb = sys.exc_info()
    # warning_msg = 'Please install psutil. The psutil library helps detect if the parent process has crashed.'
    # traceback.print_exception(ImportError, ImportError(warning_msg), exc_tb)
    psutil = None


__all__ = ['is_parent_process_alive', 'stop_process', 'run_process']


def is_parent_process_alive():
    """Return if the parent process is alive. This relies on psutil, but is optional."""
    if psutil is None:
        return True
    return psutil.pid_exists(os.getppid())


def stop_process(process, alive_event, process_queue):
    """Stop the process.

    Args:
        process (Process): Multiprocessing process to join and quit
        alive_event (Event): Event to signal that the process is closing and exit the loop.
        process_queue (Queue): Queue of events. Push a 'quit' command to exit out of the queue.get wait.
    """
    try:
        alive_event.clear()
        process_queue.put_nowait(['quit', (), {}])
        process.join()
    except AttributeError:
        pass


def run_process(alive_event, process_queue, name=None, basic_config=None, file_config=None, dict_config=None):
    """Run the logging commands in a separate process."""
    # ===== Set the Configuration =====
    if basic_config is not None:
        logging.basicConfig(**basic_config)
    if file_config is not None:
        logging.config.fileConfig(*file_config)
    if dict_config is not None:
        logging.config.dictConfig(dict_config)

    # ===== get the logger =====
    if name:
        logger = logging.getLogger(name)
    else:
        logger = logging.root

    # ===== Run the logging event loop =====
    while alive_event.is_set() and is_parent_process_alive():
        cmd, args, kwargs = process_queue.get()
        if cmd == 'addHandler':
            # Recreate the handler in this process (Handlers have a RLock which is not serializable/pickleable)
            args = (args[0].create_handler(), ) + args[1:]
        if cmd != 'quit':
            getattr(logger, cmd)(*args, **kwargs)

    # ===== Finish logging before closing =====
    while not process_queue.empty():
        cmd, args, kwargs = process_queue.get()
        if cmd == 'addHandler':
            # Recreate the handler in this process (Handlers have a RLock which is not serializable/pickleable)
            args = (args[0].create_handler(), ) + args[1:]
        if cmd != 'quit':
            getattr(logger, cmd)(*args, **kwargs)

    alive_event.clear()
