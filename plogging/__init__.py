import warnings
from logging import *

# ========== Override logging ==========
from .log_process import is_parent_process_alive, run_process, stop_process
from .logger import Logger
from .manager import Manager
from . import config
from . import handlers

# ========== Override config ==========
basicConfig = config.basicConfig
CONFIGS = config.CONFIGS
set_config_values = config.set_config_values
set_config_function = config.set_config_function

# ========== Override logging handlers ==========
Handler = handlers.Handler
StreamHandler = handlers.StreamHandler
FileHandler = handlers.FileHandler
NullHandler = handlers.NullHandler


# ========== Manager ==========
root = None
Logger.manager = Manager(root)
Logger.manager.setLoggerClass(Logger)
setLoggerClass = Logger.manager.setLoggerClass


def getLoggerClass():
    """
    Return the class to be used when instantiating a logger.
    """
    return Logger.manager.loggerClass


def getLogger(name=None):
    """
    Return a logger with the specified name, creating it if necessary.

    If no name is specified, return the root logger.
    """
    if not Logger.root:
        global root
        root = Logger('root')
        Logger.root = root
        Logger.manager.root = root

    if name:
        return Logger.manager.getLogger(name)
    else:
        return Logger.root


# ========== Override root logging functions ==========
# Custom standard format
STANDARD_FMT = {'format': '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                'datefmt': '%m/%d/%Y %H:%M:%S',}

STANDARD_FORMATTER = {'fmt': STANDARD_FMT['format'],
                      'datefmt': STANDARD_FMT['datefmt']}


def critical(msg, *args, **kwargs):
    """
    Log a message with severity 'CRITICAL' on the root logger. If the logger
    has no handlers, call basicConfig() to add a console handler with a
    pre-defined format.
    """
    getLogger().critical(msg, *args, **kwargs)


fatal = critical


def error(msg, *args, **kwargs):
    """
    Log a message with severity 'ERROR' on the root logger. If the logger has
    no handlers, call basicConfig() to add a console handler with a pre-defined
    format.
    """
    getLogger().error(msg, *args, **kwargs)


def exception(msg, *args, exc_info=True, **kwargs):
    """
    Log a message with severity 'ERROR' on the root logger, with exception
    information. If the logger has no handlers, basicConfig() is called to add
    a console handler with a pre-defined format.
    """
    error(msg, *args, exc_info=exc_info, **kwargs)


def warning(msg, *args, **kwargs):
    """
    Log a message with severity 'WARNING' on the root logger. If the logger has
    no handlers, call basicConfig() to add a console handler with a pre-defined
    format.
    """
    getLogger().warning(msg, *args, **kwargs)


def warn(msg, *args, **kwargs):
    warnings.warn("The 'warn' function is deprecated, "
        "use 'warning' instead", DeprecationWarning, 2)
    warning(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    """
    Log a message with severity 'INFO' on the root logger. If the logger has
    no handlers, call basicConfig() to add a console handler with a pre-defined
    format.
    """
    getLogger().info(msg, *args, **kwargs)


def debug(msg, *args, **kwargs):
    """
    Log a message with severity 'DEBUG' on the root logger. If the logger has
    no handlers, call basicConfig() to add a console handler with a pre-defined
    format.
    """
    getLogger().debug(msg, *args, **kwargs)


def log(level, msg, *args, **kwargs):
    """
    Log 'msg % args' with the integer severity 'level' on the root logger. If
    the logger has no handlers, call basicConfig() to add a console handler
    with a pre-defined format.
    """
    getLogger().log(level, msg, *args, **kwargs)
