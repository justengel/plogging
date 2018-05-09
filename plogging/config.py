import logging
import logging.config


__all__ = ['CONFIGS', 'set_config_values', 'set_config_function',
           'basicConfig', 'fileConfig', 'dictConfig']


# CONFIGS contains function args and kwargs to give to the matching config FUNCTIONS
CONFIGS = {}


def _no_func(*args, **kwargs):
    pass


def set_config_values(config_name, *args, **kwargs):
    """Set a configuration's values."""
    try:
        CONFIGS[config_name] = (CONFIGS[config_name][0], args, kwargs)
    except KeyError:
        CONFIGS[config_name] = (_no_func, args, kwargs)


def set_config_function(config_name, func, *args, **kwargs):
    """Set a configuration's function to run (must be pickleable).

    Example:

        ..code-block::python
            >>> def _print_func(*args, **kwargs):
            >>>     print(args, kwargs)
            >>>
            >>> set_config_function('custom_config', _print_func, 1, 2, 3)
            >>> # When a new logger is created this function will be run with the given arguments

    Args:
        config_name(str): Configuration name.
        func (function/method/str): Function to call or string name to getattr from logging.
            EXAMPLE: getattr(logging, 'config.fileConfig')
        args (tuple/object): Tuple of positional arguments to pass to the function
        kwargs (dict/object): Dictionary of named arguments to pass to the function
    """
    if not args and not kwargs and config_name in CONFIGS:
        args, kwargs = CONFIGS[config_name][1:3]
    CONFIGS[config_name] = (func, args, kwargs)


def basicConfig(**kwargs):
    set_config_function('basic_config', 'basicConfig', **kwargs)
    logging.basicConfig(**kwargs)


def fileConfig(fname, defaults=None, disable_existing_loggers=True):
    set_config_function('file_config', 'config.fileConfig', fname, defaults, disable_existing_loggers)
    logging.config.fileConfig(fname, defaults, disable_existing_loggers)


def dictConfig(config):
    set_config_function('dict_config', 'config.dictConfig', config.copy())
    logging.config.dictConfig(config)
