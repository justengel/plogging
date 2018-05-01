import logging
import logging.config


__all__ = ['CONFIGS', 'basicConfig', 'fileConfig', 'dictConfig']


CONFIGS = {
    'basic_config': None,
    'file_config': None,
    'dict_config': None,
    }


def basicConfig(**kwargs):
    CONFIGS['basic_config'] = kwargs.copy()
    logging.basicConfig(**kwargs.copy())


def fileConfig(fname, defaults=None, disable_existing_loggers=True):
    CONFIGS['file_config'] = [fname, defaults, disable_existing_loggers]
    logging.config.fileConfig(fname, defaults, disable_existing_loggers)


def dictConfig(config):
    CONFIGS['dict_config'] = config.copy()
    logging.config.dictConfig(config.copy())
