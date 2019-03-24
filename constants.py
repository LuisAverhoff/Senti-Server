"""
The settings module is where we are going to have all of our application settings inside a dict obj
for quick access. Any new settings that you would like to add should be added to the .env file and
loaded up here. Then all you need to do is import the module and index to the specific settings you
are looking for like so:

    SETTINGS["MYSETTING"]

Any other constants you like to add should be placed here as well.
"""
from environs import Env

env = Env()
env.read_env()

'''
  Both CERTFILE and KEYFILE will be provided via Heroku as using secured websockets in development
  isn't really necessary. You can add these to the .env file if you wish to add ssl to your development
  environment.
'''

SETTINGS = {
    'TWITTER_CONSUMER_API_KEY': env("TWITTER_CONSUMER_API_KEY"),
    'TWITTER_CONSUMER_API_SECRET_KEY': env("TWITTER_CONSUMER_API_SECRET_KEY"),
    'TWITTER_ACCESS_KEY': env("TWITTER_ACCESS_KEY"),
    'TWITTER_ACCESS_SECRET_KEY': env("TWITTER_ACCESS_SECRET_KEY"),
    'RABBITMQ_HOST': env("RABBITMQ_HOST"),
    'RABBITMQ_PORT': env("RABBITMQ_PORT"),
    'RABBITMQ_VIRTUAL_HOST': env('RABBITMQ_VIRTUAL_HOST'),
    'RABBITMQ_USERNAME': env("RABBITMQ_USERNAME"),
    'RABBITMQ_PASSWORD': env("RABBITMQ_PASSWORD"),
    'CERTFILE': env("CERTFILE", None),
    'KEYFILE': env("KEYFILE", None)
}
