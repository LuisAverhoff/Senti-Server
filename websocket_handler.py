import logging
import asyncio
import json
from uuid import uuid4
from tornado import ioloop, gen
from tornado.websocket import WebSocketHandler


class WSHandler(WebSocketHandler):

    LOGGER = logging.getLogger(__qualname__)

    def check_origin(self, origin):
        return True

    def open(self):
        self._sess_id = uuid4().hex
        WSHandler.LOGGER.debug(
            'Websocket with id {0} is now connected.'.format(self._sess_id))
        self.application.pc.register_websocket(self._sess_id, self)
        self.application.listener.websockets[self._sess_id] = self

    @gen.coroutine
    def on_message(self, body):
        WSHandler.LOGGER.debug(
            'Websocket {0} has received a message: {1}'.format(self._sess_id, body))

        message = json.loads(body)

        if 'track' in message:
            yield ioloop.IOLoop.current().run_in_executor(None,
                                                          self.application.listener.start_tracking,
                                                          self._sess_id, message['track'])
        else:
            self.application.pc.redirect_incoming_message(
                self._sess_id, json.dumps(body))

        yield None

    def on_close(self):
        WSHandler.LOGGER.debug(
            'Websocket with id {0} has disconnected.'.format(self._sess_id))
        self.application.pc.unregister_websocket(self._sess_id)
        self.application.listener.websockets.pop(self._sess_id)

        if(len(self.application.listener.websockets) is 0):
            WSHandler.LOGGER.debug(
                "No more connections to keep track of. Closing stream.")
            self.application.listener.stop_tracking()
