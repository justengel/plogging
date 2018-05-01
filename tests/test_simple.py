import sys
import io
import time

import plogging
# import logging as plogging


def test_getLogger():
    logger = plogging.getLogger('test_getLogger')
    logger.setLevel(plogging.DEBUG)

    handler = plogging.FileHandler('test.log')
    handler.setLevel(plogging.DEBUG)
    logger.addHandler(handler)

    logger.info("hello world")


def test_basicConfig():
    plogging.basicConfig(filename='test.log', filemode='a', level=plogging.DEBUG, **plogging.STANDARD_FMT)

    plogging.info("hello world")


def test_print_logging():
    logger = plogging.getLogger()
    logger.setLevel(plogging.DEBUG)

    # stream = io.StringIO()  # StringIo isn't working
    stream = sys.stdout
    handler = plogging.StreamHandler(stream)
    handler.setLevel(plogging.DEBUG)
    handler.setFormatter(plogging.Formatter(**plogging.STANDARD_FORMATTER))
    logger.addHandler(handler)

    logger.info("hello world")
    # print(stream.getvalue())


if __name__ == '__main__':
    test_getLogger()
    # test_basicConfig()
    # test_print_logging()
