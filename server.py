import logging
import os
from signal import signal, SIGINT
from queue import Queue
from tornado import web, ioloop
from tornado.options import define, options, parse_command_line
from client import PikaClient
from websocket_handler import WSHandler
from stream_listener import TweetStreamListener, AsyncThreadStreamListener

define("port", default=3000, help="run on the given port.", type=int)
define("debug", default=True, help="run in debug mode.", type=bool)


def main():
    def sig_exit(signum, frame):
        app.pc.connection.ioloop.add_callback_from_signal(stop_server)

    def stop_server():
        app.pc.stop()

    parse_command_line()

    logger = logging.getLogger(__name__)

    settings = {
        "debug": options.debug,
    }

    app = web.Application(
        [
            (r"/track", WSHandler),
        ],
        **settings
    )

    # Setup PikaClient and TweetListener
    app.pc = PikaClient()
    queue = Queue()
    app.queue = queue

    stream_listener = TweetStreamListener()
    async_stream_listener_thread = AsyncThreadStreamListener(
        queue, stream_listener)
    async_stream_listener_thread.start()

    app.listen(options.port)
    logger.info("Server running on http://localhost:{0}".format(options.port))

    app.pc.connect()
    signal(SIGINT, sig_exit)
    app.pc.run()

    async_stream_listener_thread.shutdown_flag.set()
    async_stream_listener_thread.stop_async_loop()
    async_stream_listener_thread.join()

    logger.info('Server shutting down.')


if __name__ == "__main__":
    main()
