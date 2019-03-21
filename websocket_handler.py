import logging
import json
from uuid import uuid4
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
        item = {'event': 'Connection Open',
                'websockets': self.application.pc.websockets}
        self.application.queue.put(item)

    def on_message(self, body):
        WSHandler.LOGGER.debug(
            'Websocket {0} has received a message: {1}'.format(self._sess_id, body))

        message = json.loads(body)

        if 'track' in message:
            item = {'event': 'track',
                    'sess_id': self._sess_id, 'track': message['track']}
            self.application.queue.put(item)
        else:
            self.application.pc.redirect_incoming_message(
                self._sess_id, json.dumps(message))

    def on_close(self):
        WSHandler.LOGGER.debug(
            'Websocket with id {0} has disconnected.'.format(self._sess_id))
        self.application.pc.unregister_websocket(self._sess_id)
        item = {'event': 'Connection Closed',
                'websockets': self.application.pc.websockets}
        self.application.queue.put(item)
