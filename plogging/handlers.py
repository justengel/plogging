import logging
import logging.handlers
import sys


RESERVED_KEYS = vars(object).keys()


class Handler(object):
    TYPE = "Handler"

    def __init__(self, level=None):
        self._pickle = {}
        self.TYPE = self.__class__.TYPE
        self.name = None
        self.level = level
        self.formatter = None

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def setLevel(self, level):
        self.level = level

    def setFormatter(self, fmt):
        self.formatter = fmt

    def format(self, record):
        return logging.Handler.format(self, record)

    def flush(self):
        pass

    def __repr__(self):
        level = logging.getLevelName(self.level)
        return '<%s (%s)>' % (self.__class__.__name__, level)

    def __getattr__(self, attr):
        if attr not in RESERVED_KEYS:
            return self._pickle[attr]

    def __setattr__(self, key, value):
        if key in RESERVED_KEYS:
            raise AttributeError("You cannot set a reserved name as attribute")
        if key != '_pickle' and key not in self.__dict__:
            self._pickle[key] = value
        else:
            super().__setattr__(key, value)

    def __getstate__(self):
        return self._pickle.copy()

    def __setstate__(self, state):
        self.__dict__['_pickle'] = {}

        type_ = state.get('TYPE', 'Handler')
        try:
            del state['TYPE']
        except KeyError:
            pass
        try:
            self._pickle['TYPE'] = type_
        except (AttributeError, ValueError, TypeError):
            pass

        try:
            self.set_name(state['name'])
            del state['name']
        except:
            pass
        try:
            self.setLevel(state['level'])
            del state['level']
        except:
            pass
        try:
            self.setFormatter(state['formatter'])
            del state['formatter']
        except:
            pass

        for key in state:
            setattr(self, key, state[key])

    def create_handler(self):
        """Create and return the handler from the settings in this class.

        This is used in the separate process.
        """
        try:
            handler_class = getattr(logging, self.TYPE)
        except AttributeError:
            handler_class = getattr(logging.handlers, self.TYPE)

        handler = handler_class()
        if self.level is not None:
            handler.setLevel(self.level)
        if self.name is not None:
            handler.name = self.name
        if self.formatter is not None:
            handler.setFormatter(self.formatter)
        return handler


class StreamHandler(Handler):
    TYPE = "StreamHandler"

    def __init__(self, stream=None):
        super().__init__()
        self.terminator = None
        self.stream = stream

    def create_handler(self):
        """Create and return the handler from the settings in this class.

        This is used in the separate process.
        """
        handler = logging.StreamHandler(stream=self.stream)
        if self.level is not None:
            handler.setLevel(self.level)
        if self.name is not None:
            handler.name = self.name
        if self.formatter is not None:
            handler.setFormatter(self.formatter)

        if self.terminator is not None:
            handler.terminator = self.terminator

        return handler

    def __getstate__(self):
        state = super().__getstate__()
        if state['stream'] == sys.stdout:
            state['stream'] = 'sys.stdout'
        elif state['stream'] == sys.stderr:
            state['stream'] = 'sys.stderr'
        return state

    def __setstate__(self, state):
        if state['stream'] == 'sys.stdout':
            state['stream'] = sys.stdout
        elif state['stream'] == 'sys.stderr':
            state['stream'] = sys.stderr
        super().__setstate__(state)


class FileHandler(StreamHandler):
    TYPE = "FileHandler"

    def __init__(self, filename, mode='a', encoding=None, delay=False):
        super().__init__()
        self.filename = filename
        self.mode = mode
        self.encoding = encoding
        self.delay = delay

    def create_handler(self):
        """Create and return the handler from the settings in this class.

        This is used in the separate process.
        """
        handler = logging.FileHandler(self.filename, self.mode, self.encoding, self.delay)
        if self.level is not None:
            handler.setLevel(self.level)
        if self.name is not None:
            handler.name = self.name
        if self.formatter is not None:
            handler.setFormatter(self.formatter)

        if self.terminator is not None:
            handler.terminator = self.terminator

        return handler


class NullHandler(Handler):
    TYPE = "NullHandler"

    def create_handler(self):
        """Create and return the handler from the settings in this class.

        This is used in the separate process.
        """
        handler = logging.NullHandler()
        if self.level is not None:
            handler.setLevel(self.level)
        if self.name is not None:
            handler.name = self.name
        if self.formatter is not None:
            handler.setFormatter(self.formatter)

        return handler


# ========== Handler file ==========
DEFAULT_TCP_LOGGING_PORT    = 9020
DEFAULT_UDP_LOGGING_PORT    = 9021
DEFAULT_HTTP_LOGGING_PORT   = 9022
DEFAULT_SOAP_LOGGING_PORT   = 9023
SYSLOG_UDP_PORT             = 514
SYSLOG_TCP_PORT             = 514

_MIDNIGHT = 24 * 60 * 60  # number of seconds in a day


class BaseRotatingHandler(FileHandler):
    TYPE = 'BaseRotatingHandler'

    def __init__(self, filename, mode, encoding=None, delay=False):
        super().__init__(filename, mode, encoding, delay)
        self.namer = None
        self.rotator = None

    def create_handler(self):
        """Create and return the handler from the settings in this class.

        This is used in the separate process.
        """
        handler = logging.handlers.BaseRotatingHandler(self.filename, self.mode, self.encoding, self.delay)
        if self.level is not None:
            handler.setLevel(self.level)
        if self.name is not None:
            handler.name = self.name
        if self.formatter is not None:
            handler.setFormatter(self.formatter)

        if self.terminator is not None:
            handler.terminator = self.terminator

        if self.namer is not None:
            handler.namer = self.namer
        if self.rotator is not None:
            handler.rotator = self.rotator

        return handler


class RotatingFileHandler(BaseRotatingHandler):
    TYPE = 'RotatingFileHandler'

    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=False):
        super().__init__(filename, mode, encoding, delay)
        self.maxBytes = maxBytes
        self.backupCount = backupCount

    def create_handler(self):
        """Create and return the handler from the settings in this class.

        This is used in the separate process.
        """
        handler = logging.handlers.BaseRotatingHandler(self.filename, self.mode, self.encoding, self.delay)
        if self.level is not None:
            handler.setLevel(self.level)
        if self.name is not None:
            handler.name = self.name
        if self.formatter is not None:
            handler.setFormatter(self.formatter)

        if self.terminator is not None:
            handler.terminator = self.terminator

        if self.namer is not None:
            handler.namer = self.namer
        if self.rotator is not None:
            handler.rotator = self.rotator

        if self.maxBytes != 0:
            handler.maxBytes = self.maxBytes
        if self.backupCount != 0:
            handler.backupCount = self.backupCount

        return handler


class TimedRotatingFileHandler(BaseRotatingHandler):
    TYPE = 'TimedRotatingFileHandler'

    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False,
                 atTime=None):
        super().__init__(filename, 'a', encoding, delay)

        self.when = when
        self.backupCount = backupCount
        self.utc = utc
        self.atTime = atTime
        self.interval = interval

    def create_handler(self):
        """Create and return the handler from the settings in this class.

        This is used in the separate process.
        """
        handler = logging.handlers.TimedRotatingFileHandler(self.filename, self.when, self.interval, self.backupCount,
                                                            self.encoding, self.delay, self.utc)
        if self.level is not None:
            handler.setLevel(self.level)
        if self.name is not None:
            handler.name = self.name
        if self.formatter is not None:
            handler.setFormatter(self.formatter)

        if self.terminator is not None:
            handler.terminator = self.terminator

        if self.namer is not None:
            handler.namer = self.namer
        if self.rotator is not None:
            handler.rotator = self.rotator

        return handler


class WatchedFileHandler(FileHandler):
    TYPE = 'WatchedFileHandler'

    def __init__(self, filename, mode='a', encoding=None, delay=False):
        super().__init__(filename, mode, encoding, delay)

    def create_handler(self):
        """Create and return the handler from the settings in this class.

        This is used in the separate process.
        """
        handler = logging.handlers.WatchedFileHandler(self.filename, self.mode, self.encoding, self.delay)
        if self.level is not None:
            handler.setLevel(self.level)
        if self.name is not None:
            handler.name = self.name
        if self.formatter is not None:
            handler.setFormatter(self.formatter)

        if self.terminator is not None:
            handler.terminator = self.terminator

        return handler


class SocketHandler(Handler):
    TYPE = 'SocketHandler'

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port

    def create_handler(self):
        """Create and return the handler from the settings in this class.

        This is used in the separate process.
        """
        handler = logging.handlers.SocketHandler(self.host, self.port)
        if self.level is not None:
            handler.setLevel(self.level)
        if self.name is not None:
            handler.name = self.name
        if self.formatter is not None:
            handler.setFormatter(self.formatter)

        return handler


class DatagramHandler(SocketHandler):
    TYPE = 'DatagramHandler'

    def __init__(self, host, port):
        super().__init__(host, port)
        self.closeOnError = False

    def create_handler(self):
        """Create and return the handler from the settings in this class.

        This is used in the separate process.
        """
        handler = logging.handlers.DatagramHandler(self.host, self.port)
        if self.level is not None:
            handler.setLevel(self.level)
        if self.name is not None:
            handler.name = self.name
        if self.formatter is not None:
            handler.setFormatter(self.formatter)

        if self.closeOnError is not None:
            handler.closeOnError = self.closeOnError

        return handler


class SysLogHandler(Handler):
    TYPE = 'SysLogHandler'

    LOG_EMERG     = 0       #  system is unusable
    LOG_ALERT     = 1       #  action must be taken immediately
    LOG_CRIT      = 2       #  critical conditions
    LOG_ERR       = 3       #  error conditions
    LOG_WARNING   = 4       #  warning conditions
    LOG_NOTICE    = 5       #  normal but significant condition
    LOG_INFO      = 6       #  informational
    LOG_DEBUG     = 7       #  debug-level messages

    #  facility codes
    LOG_KERN      = 0       #  kernel messages
    LOG_USER      = 1       #  random user-level messages
    LOG_MAIL      = 2       #  mail system
    LOG_DAEMON    = 3       #  system daemons
    LOG_AUTH      = 4       #  security/authorization messages
    LOG_SYSLOG    = 5       #  messages generated internally by syslogd
    LOG_LPR       = 6       #  line printer subsystem
    LOG_NEWS      = 7       #  network news subsystem
    LOG_UUCP      = 8       #  UUCP subsystem
    LOG_CRON      = 9       #  clock daemon
    LOG_AUTHPRIV  = 10      #  security/authorization messages (private)
    LOG_FTP       = 11      #  FTP daemon

    #  other codes through 15 reserved for system use
    LOG_LOCAL0    = 16      #  reserved for local use
    LOG_LOCAL1    = 17      #  reserved for local use
    LOG_LOCAL2    = 18      #  reserved for local use
    LOG_LOCAL3    = 19      #  reserved for local use
    LOG_LOCAL4    = 20      #  reserved for local use
    LOG_LOCAL5    = 21      #  reserved for local use
    LOG_LOCAL6    = 22      #  reserved for local use
    LOG_LOCAL7    = 23      #  reserved for local use

    priority_names = {
        "alert":    LOG_ALERT,
        "crit":     LOG_CRIT,
        "critical": LOG_CRIT,
        "debug":    LOG_DEBUG,
        "emerg":    LOG_EMERG,
        "err":      LOG_ERR,
        "error":    LOG_ERR,        #  DEPRECATED
        "info":     LOG_INFO,
        "notice":   LOG_NOTICE,
        "panic":    LOG_EMERG,      #  DEPRECATED
        "warn":     LOG_WARNING,    #  DEPRECATED
        "warning":  LOG_WARNING,
        }

    facility_names = {
        "auth":     LOG_AUTH,
        "authpriv": LOG_AUTHPRIV,
        "cron":     LOG_CRON,
        "daemon":   LOG_DAEMON,
        "ftp":      LOG_FTP,
        "kern":     LOG_KERN,
        "lpr":      LOG_LPR,
        "mail":     LOG_MAIL,
        "news":     LOG_NEWS,
        "security": LOG_AUTH,       #  DEPRECATED
        "syslog":   LOG_SYSLOG,
        "user":     LOG_USER,
        "uucp":     LOG_UUCP,
        "local0":   LOG_LOCAL0,
        "local1":   LOG_LOCAL1,
        "local2":   LOG_LOCAL2,
        "local3":   LOG_LOCAL3,
        "local4":   LOG_LOCAL4,
        "local5":   LOG_LOCAL5,
        "local6":   LOG_LOCAL6,
        "local7":   LOG_LOCAL7,
        }

    #The map below appears to be trivially lowercasing the key. However,
    #there's more to it than meets the eye - in some locales, lowercasing
    #gives unexpected results. See SF #1524081: in the Turkish locale,
    #"INFO".lower() != "info"
    priority_map = {
        "DEBUG" : "debug",
        "INFO" : "info",
        "WARNING" : "warning",
        "ERROR" : "error",
        "CRITICAL" : "critical"
    }

    def __init__(self, address=('localhost', SYSLOG_UDP_PORT), facility=LOG_USER, socktype=None):
        super().__init__()
        self.address = address
        self.facility = facility
        self.socktype = self.socktype

    def create_handler(self):
        """Create and return the handler from the settings in this class.

        This is used in the separate process.
        """
        handler = logging.handlers.SysLogHandler(self.address, self.facility, self.socktype)
        if self.level is not None:
            handler.setLevel(self.level)
        if self.name is not None:
            handler.name = self.name
        if self.formatter is not None:
            handler.setFormatter(self.formatter)

        return handler


class SMTPHandler(Handler):
    TYPE = 'SMTPHandler'

    def __init__(self, mailhost, fromaddr, toaddrs, subject,
                 credentials=None, secure=None, timeout=5.0):
        super().__init__()
        self.mailhost = mailhost
        self.fromaddr = fromaddr
        self.toaddrs = toaddrs
        self.subject = subject
        self.credentials = credentials
        self.secure = secure
        self.timeout = timeout

    def create_handler(self):
        """Create and return the handler from the settings in this class.

        This is used in the separate process.
        """
        handler = logging.handlers.SMTPHandler(self.mailhost, self.fromaddr, self.toaddrs, self.subject,
                                                 self.credentials, self.secure, self.timeout)
        if self.level is not None:
            handler.setLevel(self.level)
        if self.name is not None:
            handler.name = self.name
        if self.formatter is not None:
            handler.setFormatter(self.formatter)

        return handler


class NTEventLogHandler(Handler):
    TYPE = 'NTEventLogHandler'

    def __init__(self, appname, dllname=None, logtype='Application'):
        super().__init__()

        self.appname = appname
        self.dllname = dllname
        self.logtype = logtype

    def create_handler(self):
        """Create and return the handler from the settings in this class.

        This is used in the separate process.
        """
        handler = logging.handlers.NTEventLogHandler(self.appname, self.dllname, self.logtype)
        if self.level is not None:
            handler.setLevel(self.level)
        if self.name is not None:
            handler.name = self.name
        if self.formatter is not None:
            handler.setFormatter(self.formatter)

        return handler


class HTTPHandler(Handler):
    TYPE = 'HTTPHandler'

    def __init__(self, host, url, method="GET", secure=False, credentials=None,
                 context=None):
        super().__init__()

        self.host = host
        self.url = url
        self.method = method
        self.secure = secure
        self.credentials = credentials
        self.context = context

    def create_handler(self):
        """Create and return the handler from the settings in this class.

        This is used in the separate process.
        """
        handler = logging.handlers.HTTPHandler(self.host, self.url, self.method, self.secure, self.credentials,
                                                 self.context)
        if self.level is not None:
            handler.setLevel(self.level)
        if self.name is not None:
            handler.name = self.name
        if self.formatter is not None:
            handler.setFormatter(self.formatter)

        return handler


class BufferingHandler(Handler):
    TYPE = 'BufferingHandler'

    def __init__(self, capacity):
        super().__init__()

        self.capacity = capacity

    def create_handler(self):
        """Create and return the handler from the settings in this class.

        This is used in the separate process.
        """
        handler = logging.handlers.BufferingHandler(self.capacity)
        if self.level is not None:
            handler.setLevel(self.level)
        if self.name is not None:
            handler.name = self.name
        if self.formatter is not None:
            handler.setFormatter(self.formatter)

        return handler


class MemoryHandler(BufferingHandler):
    TYPE = 'MemoryHandler'

    def __init__(self, capacity, flushLevel=logging.ERROR, target=None,
                 flushOnClose=True):
        super().__init__(capacity)

        self.flushLevel = flushLevel
        self.target = target
        self.flushOnClose = flushOnClose

    def create_handler(self):
        """Create and return the handler from the settings in this class.

        This is used in the separate process.
        """
        handler = logging.handlers.MemoryHandler(self.capacity, self.flushLevel, self.target, self.flushOnClose)
        if self.level is not None:
            handler.setLevel(self.level)
        if self.name is not None:
            handler.name = self.name
        if self.formatter is not None:
            handler.setFormatter(self.formatter)

        return handler


class QueueHandler(Handler):
    TYPE = 'QueueHandler'

    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def enqueue(self, record):
        """
        Enqueue a record.

        The base implementation uses put_nowait. You may want to override
        this method if you want to use blocking, timeouts or custom queue
        implementations.
        """
        self.queue.put_nowait(record)

    def create_handler(self):
        """Create and return the handler from the settings in this class.

        This is used in the separate process.
        """
        handler = logging.handlers.QueueHandler(self.queue)
        if self.level is not None:
            handler.setLevel(self.level)
        if self.name is not None:
            handler.name = self.name
        if self.formatter is not None:
            handler.setFormatter(self.formatter)

        return handler
