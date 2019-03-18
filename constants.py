"""
The settings module is where we are going to have all of our application settings inside a dict obj
for quick access. Any new settings that you would like to add should be added to the .env file and
loaded up here. Then all you need to do is import the module and index to the specific settings you
are looking for like so:

    SETTINGS["MYSETTING"]

Any other constants you like to add should be placed here as well.
"""
import logging.config
import os
from environs import Env

env = Env()
env.read_env()

SETTINGS = {
    'TWITTER_CONSUMER_API_KEY': env("TWITTER_CONSUMER_API_KEY"),
    'TWITTER_CONSUMER_API_SECRET_KEY': env("TWITTER_CONSUMER_API_SECRET_KEY"),
    'TWITTER_ACCESS_KEY': env("TWITTER_ACCESS_KEY"),
    'TWITTER_ACCESS_SECRET_KEY': env("TWITTER_ACCESS_SECRET_KEY"),
    'RABBITMQ_USERNAME': env("RABBITMQ_USERNAME"),
    'RABBITMQ_PASSWORD': env("RABBITMQ_PASSWORD"),
    'RABBITMQ_HOST': env("RABBITMQ_HOST"),
    'RABBITMQ_PORT': env("RABBITMQ_PORT")
}

ERROR_FORMAT = "%(levelname)s at %(asctime)s in %(funcName)s in %(filename) at line %(lineno)d: %(message)s"
DEBUG_FORMAT = "%(lineno)d in %(filename)s at %(asctime)s: %(message)s"

LOG_CONFIG = {'version': 1,
              'formatters': {'error': {'format': ERROR_FORMAT},
                             'debug': {'format': DEBUG_FORMAT}},
              'handlers': {'console': {'class': 'logging.StreamHandler',
                                       'formatter': 'debug',
                                       'level': logging.DEBUG},
                           'file': {'class': 'logging.FileHandler',
                                    'filename': "{0}/logs/app.log".format(os.getcwd()),
                                    'formatter': 'error',
                                    'level': logging.ERROR}},
              'loggers': {
                  'server': {  # root logger
                      'handlers': ['console', 'file'],
                      'level': 'INFO',
                      'propagate': True
                  },
                  'client': {
                      'handlers': ['console'],
                      'level': 'DEBUG',
                      'propagate': False
                  },
                  'stream_listener': {
                      'handlers': ['console'],
                      'level': 'DEBUG',
                      'propagate': False
                  },
                  'handlers': {
                      'handlers': ['console'],
                      'level': 'DEBUG',
                      'propagate': False
                  },
              }}

logging.config.dictConfig(LOG_CONFIG)
