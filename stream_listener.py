import logging
import asyncio
from contextlib import suppress
from constants import SETTINGS
from queue import Queue, Empty
from sentiment_analyzer import calculate_polarity_score, preprocess_tweet
from tweepy import StreamListener, OAuthHandler, Stream, API
from tornado import gen
from threading import Thread, Event

auth = OAuthHandler(
    SETTINGS["TWITTER_CONSUMER_API_KEY"], SETTINGS["TWITTER_CONSUMER_API_SECRET_KEY"])

auth.set_access_token(
    SETTINGS["TWITTER_ACCESS_KEY"], SETTINGS["TWITTER_ACCESS_SECRET_KEY"])

api = API(auth, wait_on_rate_limit=True)


"""
  The purpose of this class is very simple. The tornado dcoumentation states that if you start your own thread
  you must manually register an asyncio event loop. This is only done for the main thread. We want our stream api
  to be non blocking so when we start listening, tweepy will spawn a new thread and will not register a asyncio event
  loop. As a fix for this, all we need to do is extend the thread function and register the event loop ourselves and
  call the main thread function.
"""


class ASyncIOStream(Stream):
    def _run(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        super(ASyncIOStream, self)._run()


class TweetStreamListener(StreamListener):

    def __init__(self):
        self.api = api
        self.websockets = {}
        self.logger = logging.getLogger(__name__)
        self.current_searches = {}
        self.stream = ASyncIOStream(auth=self.api.auth, listener=self)

    def update_websockets(self, websockets):
        self.websockets = websockets

    def start_tracking(self, sess_id, track):
        # new tweet to listen to.
        self.current_searches[sess_id] = track.lower()

        # disconnect the stream momentarily. Now nobody is receiving tweets.
        if self.stream.running:
            self.stream.disconnect()

        # create new search term list
        search_terms = self.current_searches.values()
        # start listening for these tweets
        self.stream.filter(track=search_terms, is_async=True)

    @gen.coroutine
    def on_status(self, status):
        if not hasattr(status, 'retweeted_status'):
            clean_tweet = preprocess_tweet(status.text)

            # polarity = calculate_polarity_score(clean_tweet)

            # message = {
            # 'polarity': polarity,
            # 'timestamp': status.created_at
           # }

            sess_ids = []

            lowercase_tweet = clean_tweet.lower()

            for sess_id, topic in self.current_searches.items():
                if topic in lowercase_tweet:
                    sess_ids .append(sess_id)

            yield [self.websockets[sess_id].write_message(clean_tweet) for sess_id in sess_ids if self.websockets[sess_id]]

    # limit handling
    def on_limit(self, status):
        self.logger.debug(
            'Limit threshold exceeded. Status code: {0}'.format(status))

    def on_timeout(self, status):
        self.logger.error('Stream disconnected. continuing...')
        return True  # Don't kill the stream

    """
    Summary: Callback that executes for any error that may occur. Whenever we get a 420 Error code, we simply
    stop streaming tweets as we have reached our rate limit. This is due to making too many requests.

    Returns: False if we are sending too many tweets, otherwise return true to keep the stream going.
    """

    def on_error(self, status_code):
        if status_code == 420:
            self.logger.error(
                'Encountered error code 420. Disconnecting the stream')
            # returning False in on_data disconnects the stream
            return False
        else:
            self.logger.error('Encountered error with status code: {}'.format(
                status_code))
            return True  # Don't kill the stream


class AsyncThreadStreamListener(Thread):

    def __init__(self, queue, stream_listener):
        Thread.__init__(self)
        self.queue = queue
        self.stream_listener = stream_listener
        self.logger = logging.getLogger(__name__)
        self.async_loop = None
        self._queue_task = None
        self.shutdown_flag = Event()

    def run(self):
        self.async_loop = asyncio.new_event_loop()
        async_loop = self.async_loop
        asyncio.set_event_loop(async_loop)

        try:
            # create task:
            self._queue_task = asyncio.ensure_future(self._process_queue())

            # run loop:
            async_loop.run_forever()
            async_loop.run_until_complete(async_loop.shutdown_asyncgens())

            # cancel task:
            self._queue_task.cancel()

            with suppress(asyncio.CancelledError):
                async_loop.run_until_complete(self._queue_task)
        finally:
            async_loop.close()

    def stop_async_loop(self):
        self.async_loop.call_soon_threadsafe(self.async_loop.stop)

    async def _process_queue(self):
        self.logger.debug('Thread #{0} has started'.format(self.ident))

        while not self.shutdown_flag.is_set():
            try:
                message = self.queue.get(timeout=1)

                if message['event'] is 'track':
                    self.stream_listener.start_tracking(
                        message['sess_id'], message['track'])
                else:
                    self.stream_listener.update_websockets(
                        message['websockets'])

                self.queue.task_done()
            except Empty:
                continue

        self.stream_listener.stream.disconnect()

        self.logger.debug('Thread #{0} has stopped'.format(self.ident))
