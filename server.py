import logging
import ssl
from queue import Queue
from setup_logger import ROOT_LOGGER
from tornado import web, ioloop
from tornado.options import define, options, parse_command_line
from websocket_handler import WSHandler
from constants import SETTINGS
from tweet_stream_listener import TweetStreamListener, listen_for_tweets

define("port", default=8000, help="run on the given port.", type=int)
define("debug", default=True, help="run in debug mode.", type=bool)


def main():
    parse_command_line()

    logger = logging.getLogger(ROOT_LOGGER)

    settings = {
        "debug": options.debug,
    }

    app = web.Application(
        [
            (r"/track", WSHandler),
        ],
        **settings
    )

    queue = Queue()
    app.listener = TweetStreamListener(queue)

    context = None

    if SETTINGS['CERTFILE'] and SETTINGS['KEYFILE']:
        context = ssl.SSLContext()
        context.load_cert_chain(SETTINGS['CERTFILE'], SETTINGS['KEYFILE'])

    app.listen(port=options.port, ssl_options=context)
    logger.info("Server listening on port: {0}".format(options.port))

    loop = ioloop.IOLoop.current()
    loop.run_in_executor(None, listen_for_tweets, app.listener, queue)

    try:
        loop.start()
    except KeyboardInterrupt:
        loop.stop()

     # This is a sentinel value to to the consumer queue that we are done.
    queue.put(None)
    app.listener.stop_tracking()

    logger.info('Server shutting down.')


if __name__ == "__main__":
    main()
