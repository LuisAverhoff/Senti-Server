import logging
import pika
from constants import SETTINGS
from pika import PlainCredentials, ConnectionParameters
from pika.adapters.tornado_connection import TornadoConnection


class PikaClient(object):
    INPUT_QUEUE_NAME = 'in_queue'

    def __init__(self, ioloop):
        self.connected = False
        self.connecting = False
        self.connection = None
        self.in_channel = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.out_channels = {}
        self.websockets = {}
        self.ioloop = ioloop

    def connect(self):
        if self.connecting:
            return

        self.connecting = True

        # Setup rabbitMQ connection
        credentials = PlainCredentials(
            SETTINGS['RABBITMQ_USERNAME'], SETTINGS['RABBITMQ_PASSWORD'])

        param = ConnectionParameters(
            host=SETTINGS['RABBITMQ_HOST'], port=SETTINGS['RABBITMQ_PORT'],
            virtual_host=SETTINGS['RABBITMQ_VIRTUAL_HOST'], credentials=credentials)

        self.connection = TornadoConnection(
            param, on_open_callback=self.on_connected, custom_ioloop=self.ioloop)

    def run(self):
        self.connection.ioloop.start()

    def stop(self):
        self.connected = self.connecting = False
        self.connection.ioloop.stop()

    def on_connected(self, unused_Connection):
        self.logger.debug('Tornado Connection successfully established')
        self.connected = True
        self.in_channel = self.connection.channel(self.on_conn_open)

    def on_connection_closed(self):
        self.logger.debug('Connection has been closed.')

    def on_conn_open(self, channel):
        self.connection.add_on_close_callback(self.on_connection_closed)
        self.in_channel.exchange_declare(
            exchange='tornado_input', exchange_type='topic')
        channel.queue_declare(
            callback=self.on_input_queue_declare, queue=self.INPUT_QUEUE_NAME)

    def on_input_queue_declare(self, queue):
        self.in_channel.queue_bind(
            callback=None, exchange='tornado_input', queue=self.INPUT_QUEUE_NAME, routing_key="#")

    def register_websocket(self, sess_id, ws):
        self.websockets[sess_id] = ws
        self.create_out_channel(sess_id)

    def unregister_websocket(self, sess_id):
        self.websockets.pop(sess_id)

        if sess_id in self.out_channels:
            self.out_channels[sess_id].close()

    def create_out_channel(self, sess_id):
        def on_output_channel_creation(channel):
            def on_output_queue_declaration(queue):
                channel.basic_consume(self.on_message, queue=sess_id)

            self.out_channels[sess_id] = channel
            channel.queue_declare(callback=on_output_queue_declaration,
                                  queue=sess_id, auto_delete=True, exclusive=True)

        self.connection.channel(on_output_channel_creation)

    def redirect_incoming_message(self, sess_id, message):
        self.in_channel.basic_publish(
            exchange='tornado_input', routing_key=sess_id, body=message)

    def on_message(self, channel, method, header, body):
        sess_id = method.routing_key

        if sess_id in self.websockets:
            self.websockets[sess_id].write_message(body)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        else:
            channel.basic_reject(delivery_tag=method.delivery_tag)
