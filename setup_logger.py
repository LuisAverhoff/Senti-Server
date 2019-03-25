import logging.config
import os
from pathlib import Path

SERVER_LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
server_log_path = Path(SERVER_LOG_DIR)
server_log_path.mkdir(exist_ok=True)

SERVER_LOG_FILE = os.path.join(SERVER_LOG_DIR, 'server.log')
server_file_path = Path(SERVER_LOG_FILE)

if not server_file_path.is_file():
    server_file_path.open(mode='w+')

ERROR_FORMAT = "%(levelname)s at %(asctime)s in %(funcName)s in %(filename) at line %(lineno)d: %(message)s"
DEBUG_FORMAT = "%(lineno)d in %(filename)s at %(asctime)s: %(message)s"

ROOT_LOGGER = "server"

LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {'error': {'format': ERROR_FORMAT},
                   'debug': {'format': DEBUG_FORMAT}},
    'handlers': {'console': {'class': 'logging.StreamHandler',
                             'formatter': 'debug',
                             'level': 'DEBUG'},
                 'file': {'class': 'logging.handlers.RotatingFileHandler',
                          'filename': SERVER_LOG_FILE,
                          'formatter': 'error',
                          'level': 'ERROR'}},
    'loggers': {
        ROOT_LOGGER: {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False
        },
        'PikaClient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'TweetStreamListener': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'WSHandler': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

logging.config.dictConfig(LOG_CONFIG)
