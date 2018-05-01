# Process Logging - plogging

Log data quickly with a separate process.

This library was created to speed up python's logging by logging the data in a separate process.

## Background
I've worked with a lot of audio data where hardware streams data into a PySide user interface through a Serial Port or
TCP connection. Logging and plotting was really slow. I stopped using matplotlib and used pyqtgraph which drastically
improved the speed of the application. Another step I took to speed up the application was to replace slow file logging
by buffering a lot of data before manually writing to a file. This worked, but if the application crashed for any
reason I would lose all of the buffered data. I created this library to quickly send the data to another process where
the separate process could log the data without slowing the application.

## Use
This library works similar to the logging library.

Main differences:

    * Handlers
       * Handlers in this library only hold configuration data as a dictionary.
       * Logger.addHandler(handler) will pickle the configuration
       * In run_process 'addHandler' creates the actual handler with create_handler()
    * Logger
       * Loggers hold a process (Process), process_alive (Event), and process_queue (Queue)
       * Every function called by the Logger queues the action to be called in the separate process.
       * run_process actually calls the function that you called
         * logger.info('my message') - sends this to the queue to be called in run_process.


### Example - getLogger
Get a logger and set the handler to log data.
```python
import plogging as logging

logger = logging.getLogger('README.log')
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler('test.log')
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

logger.info("hello world")
```

Decide you don't like plogging
```python
# import plogging as logging
import logging

logger = logging.getLogger('README.log')
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler('test.log')
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

logger.info("hello world")
```


### Example - basicConfig
```python
import plogging

plogging.basicConfig(filename='test.log', filemode='a',
                     level=plogging.DEBUG, **plogging.STANDARD_FMT)

plogging.info("hello world")
```
