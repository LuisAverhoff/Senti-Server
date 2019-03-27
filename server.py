import logging
import os
import ssl
import asyncio
from queue import Queue
from setup_logger import ROOT_LOGGER
from signal import signal, SIGINT
from tornado import web, ioloop
from tornado.options import define, options, parse_command_line
from pika_client import PikaClient
from websocket_handler import WSHandler
from constants import SETTINGS
from tweet_stream_listener import TweetStreamListener, listen_for_tweets

define("port", default=8000, help="run on the given port.", type=int)
define("debug", default=True, help="run in debug mode.", type=bool)


def main():
    def sig_exit(signum, frame):
        app.pc.connection.ioloop.add_callback_from_signal(stop_server)

    def stop_server():
        app.pc.stop()

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

    loop = ioloop.IOLoop.current()

    # Setup PikaClient.
    app.pc = PikaClient(loop)
    queue = Queue()
    app.listener = TweetStreamListener(queue)

    context = None

    if SETTINGS['CERTFILE'] and SETTINGS['KEYFILE']:
        context = ssl.SSLContext()
        context.load_cert_chain(SETTINGS['CERTFILE'], SETTINGS['KEYFILE'])

    app.listen(port=options.port, ssl_options=context)
    logger.info("Server listening on port: {0}".format(options.port))

    app.pc.connect()
    signal(SIGINT, sig_exit)
    loop.run_in_executor(None, listen_for_tweets, app.listener, queue)
    app.pc.run()

    # This is a sentinel value to to the consumer queue that we are done.
    queue.put(None)
    app.listener.stop_tracking()

    logger.info('Server shutting down.')


if __name__ == "__main__":
    main()
