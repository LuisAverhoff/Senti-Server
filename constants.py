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
