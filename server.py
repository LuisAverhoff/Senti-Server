import logging
import os
import ssl
from setup_logger import ROOT_LOGGER
from signal import signal, SIGINT
from queue import Queue
from tornado import web, ioloop
from tornado.options import define, options, parse_command_line
from pika_client import PikaClient
from websocket_handler import WSHandler
from stream_listener import AsyncThreadStreamListener
from constants import SETTINGS

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

    # Setup PikaClient and start the Async Stream Listener thread.
    app.pc = PikaClient()
    queue = Queue()
    app.queue = queue

    async_stream_listener_thread = AsyncThreadStreamListener(queue)
    async_stream_listener_thread.start()

    context = None

    if SETTINGS['CERTFILE'] and SETTINGS['KEYFILE']:
        context = ssl.SSLContext()
        context.load_cert_chain(SETTINGS['CERTFILE'], SETTINGS['KEYFILE'])

    app.listen(port=options.port, ssl_options=context)
    logger.info("Server listening on port: {0}".format(options.port))

    app.pc.connect()
    signal(SIGINT, sig_exit)
    app.pc.run()

    async_stream_listener_thread.shutdown_flag.set()
    async_stream_listener_thread.stop_listening()
    async_stream_listener_thread.join()

    logger.info('Server shutting down.')


if __name__ == "__main__":
    main()
