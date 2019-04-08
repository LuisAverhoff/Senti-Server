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
  environment. You will want to add domains that you would like to be whitelisted by the server so
  that it can accept websocket connections from those domains. Each domain should be separated by a
  comma i.e netlify.com,herokuapp.com etc
'''

SETTINGS = {
    'TWITTER_CONSUMER_API_KEY': env("TWITTER_CONSUMER_API_KEY"),
    'TWITTER_CONSUMER_API_SECRET_KEY': env("TWITTER_CONSUMER_API_SECRET_KEY"),
    'TWITTER_ACCESS_KEY': env("TWITTER_ACCESS_KEY"),
    'TWITTER_ACCESS_SECRET_KEY': env("TWITTER_ACCESS_SECRET_KEY"),
    'WHITELISTED_DOMAINS': env("WHITELISTED_DOMAINS", ""),
    'CERTFILE': env("CERTFILE", None),
    'KEYFILE': env("KEYFILE", None)
}
