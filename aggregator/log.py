"""Logging configurations file."""
import logging
import sys


LOGGING_CONFIG_DEFAULTS = dict(
    version=1,
    disable_existing_loggers=False,

    loggers={
        "root": {
            "level": "DEBUG",
            "handlers": ["console"]
        },
        "sanic.error": {
            "level": "ERROR",
            "handlers": ["error_console"],
            "propagate": True,
            "qualname": "sanic.error"
        },

        "sanic.access": {
            "level": "DEBUG",
            "handlers": ["access_console"],
            "propagate": True,
            "qualname": "sanic.access"
        }
    },
    handlers={
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "generic",
            "stream": sys.stdout
        },
        "error_console": {
            "class": "logging.StreamHandler",
            "level": "ERROR",
            "formatter": "generic",
            "stream": sys.stderr
        },
        "access_console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "access",
            "stream": sys.stdout
        }
    },
    formatters={
        "generic": {
            "format": "%(asctime)s.%(msecs)03dZ [%(process)d] [%(levelname)s] %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
            "class": "logging.Formatter"
        },
        "access": {
            "format": "%(asctime)s.%(msecs)03dZ - (%(name)s)[%(levelname)s][%(host)s]: \
            %(request)s %(message)s %(status)d %(byte)d",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
            "class": "logging.Formatter"
        },
    }
)


logger = logging.getLogger('root')
error_logger = logging.getLogger('sanic.error')
access_logger = logging.getLogger('sanic.access')
