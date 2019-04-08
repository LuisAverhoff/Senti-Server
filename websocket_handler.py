import logging
import json
from constants import SETTINGS
from urllib.parse import urlparse
from uuid import uuid4
from tornado import ioloop, gen
from tornado.websocket import WebSocketHandler


class WSHandler(WebSocketHandler):

    LOGGER = logging.getLogger(__qualname__)
    WHITELISTED_DOMAINS = SETTINGS['WHITELISTED_DOMAINS'].split(",")

    def check_origin(self, origin):
        parsed_origin = urlparse(origin)

        if parsed_origin.hostname is 'localhost':
            return True

        domain = ".".join(parsed_origin.netloc.split(".")[1:])
        return domain in WSHandler.WHITELISTED_DOMAINS

    def open(self):
        self._sess_id = uuid4().hex
        WSHandler.LOGGER.debug(
            'Websocket with id {0} is now connected.'.format(self._sess_id))
        self.application.listener.websockets[self._sess_id] = self

    @gen.coroutine
    def on_message(self, body):
        WSHandler.LOGGER.debug(
            'Websocket {0} has received a message: {1}'.format(self._sess_id, body))

        message = json.loads(body)
        yield self.wait_still_stream_finishes(message['track'])

    @gen.coroutine
    def wait_still_stream_finishes(self, message):
        # Disconnect the stream momentarily.
        self.application.listener.stop_tracking()

        while self.application.listener.is_stream_running():
            yield gen.sleep(1)

        ioloop.IOLoop.current().run_in_executor(None,
                                                self.application.listener.start_tracking,
                                                self._sess_id, message)

    def on_close(self):
        WSHandler.LOGGER.debug(
            'Websocket with id {0} has disconnected.'.format(self._sess_id))
        self.application.listener.websockets.pop(self._sess_id)

        if(len(self.application.listener.websockets) is 0):
            WSHandler.LOGGER.debug(
                "No more connections to keep track of. Closing stream.")
            self.application.listener.stop_tracking()
