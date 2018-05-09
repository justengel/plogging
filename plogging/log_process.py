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


def _run_configs(configs=None, config_funcs=None):
    """Run the config for the given configurations.

    Example:

        def my_func(option1=None, option2=None):
            print(option1, option2)

        configs = {'my_config': (my_func, [], {'option1': 1, 'option2': 2})}
        _run_configs(configs)

    Args:
        configs (dict)[None]: Dictionary of the configuration function and arguments.
    """
    if configs is None:
        return

    for opt, val in configs.items():
        func, args, kwargs = val
        if args or kwargs:
            if isinstance(func, str):
                func = getattr(logging, func, None)
            if func:
                func(*args, **kwargs)


def _run_cmd(logger, cmd, args, kwargs):
    """Get a command from the process queue and run the command with the logger.

    Args:
        logger (logging.Logger): Logger to run the command with
        cmd (str): Logger method name to run
        args (tuple): Positional arguments for the method
        kwargs (dict): Key word arguments for the method.

    Returns:
        was_command (bool): True if the cmd name was a logger function.
    """
    if cmd == 'addHandler':
        # Recreate the handler in this process (Handlers have a RLock which is not serializable/pickleable)
        args = (args[0].create_handler(), ) + args[1:]

    func = getattr(logger, cmd, None)
    if func:
        func(*args, **kwargs)
        return True
    return False


def run_process(alive_event, process_queue, name=None, configs=None):
    """Run the logging commands in a separate process."""
    # ===== Configure logging =====
    _run_configs(configs)

    # ===== get the logger =====
    if name == 'root':
        logger = logging.root
    else:
        logger = logging.getLogger(name)

    # ===== Run the logging event loop =====
    while alive_event.is_set() and is_parent_process_alive():
        cmd, args, kwargs = process_queue.get()
        _run_cmd(logger, cmd, args, kwargs)

    # ===== Finish logging before closing =====
    # Only handle the number of events at this point. Otherwise could run forever if queue.put is fast enough.
    for _ in range(process_queue.qsize()):
        cmd, args, kwargs = process_queue.get()
        _run_cmd(logger, cmd, args, kwargs)

    alive_event.clear()
