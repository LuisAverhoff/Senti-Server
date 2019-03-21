import logging
import asyncio
import json
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
  loop. As a fix for this, all we need to do is extend the _run function, register the event loop ourselves and
  call the main thread function.
"""


class ASyncIOStream(Stream):
    def __init__(self, auth, listener, **options):
        super().__init__(auth, listener, **options)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.async_loop = None
        self._stream_task = None

    def _run(self):
        self.async_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.async_loop)

        self.logger.debug('Stream is now listening for tweets.')

        try:
            # create task:
            self._stream_task = asyncio.ensure_future(self._start_streaming())

            # run loop:
            self.async_loop.run_forever()

            # cancel task:
            self._stream_task.cancel()

            with suppress(asyncio.CancelledError):
                self.async_loop.run_until_complete(self._stream_task)
        finally:
            self.async_loop.close()

        self.logger.debug(
            'The stream has stopped and is not listening for tweets at the moment.')

    def is_stream_running(self):
        return self.async_loop and self.async_loop.is_running()

    def stop_streaming(self):
        if self.is_stream_running():
            self.async_loop.call_soon_threadsafe(self.async_loop.stop)
            self.disconnect()

    async def _start_streaming(self):
        super()._run()


class TweetStreamListener(StreamListener):

    def __init__(self, api):
        self.api = api
        self.websockets = {}
        self.logger = logging.getLogger(__name__)
        self.current_searches = {}

    def generate_track_list(self, sess_id, track):
        # New tweet to listen to.
        self.current_searches[sess_id] = track.lower()

        '''
            Create a new search term list and put it all in a set to remove 
            potential duplicate search terms.
        '''
        return set(self.current_searches.values())

    def on_status(self, status):

        # We are not processing retweets. Only new tweets.
        if hasattr(status, 'retweeted_status'):
            return

        tweet = status.text

        # If extended_tweet exists, this the means that status.text is truncated.
        # We want the entire text.
        if hasattr(status, 'extended_tweet'):
            tweet = status.extended_tweet['full_text']

        clean_tweet = preprocess_tweet(tweet)

        polarity = calculate_polarity_score(clean_tweet)

        message = {
            'polarity': polarity,
            'timestamp': str(status.created_at)
        }

        sess_ids = []

        lowercase_tweet = clean_tweet.lower()

        for sess_id, topic in self.current_searches.items():
            if topic in lowercase_tweet:
                sess_ids.append(sess_id)

        for sess_id in sess_ids:
            if self.websockets[sess_id]:
                self.websockets[sess_id].write_message(message)

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

    def __init__(self, queue):
        super().__init__()
        self.queue = queue
        self.stream_listener = TweetStreamListener(api)
        self.stream = ASyncIOStream(
            auth=api.auth, listener=self.stream_listener, tweet_mode='extended')
        self.logger = logging.getLogger(self.__class__.__name__)
        self.async_loop = None
        self._queue_task = None
        self.shutdown_flag = Event()

    def run(self):
        self.async_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.async_loop)

        try:
            # create task:
            self._queue_task = asyncio.ensure_future(self._process_queue())

            # run loop:
            self.async_loop.run_forever()

            # cancel task:
            self._queue_task.cancel()

            with suppress(asyncio.CancelledError):
                self.async_loop.run_until_complete(self._queue_task)
        finally:
            self.async_loop.close()

    def stop_listening(self):
        self.async_loop.call_soon_threadsafe(self.async_loop.stop)

    async def _process_queue(self):
        self.logger.debug(
            'Thread #{0} has started and is now processing events in the queue'.format(self.ident))

        while not self.shutdown_flag.is_set():
            try:
                message = self.queue.get(timeout=1)

                if message['event'] is 'track':
                    # Stop the streaming momentarily when the user changes their search.
                    self.stream.stop_streaming()

                    '''
                        TODO(Luis) See if there is a better way to wait until the async loop
                        has finished. This needs to be done because if we don't, we risk starting
                        another thread and losing reference to the current async loop.
                    '''
                    while self.stream.is_stream_running():
                        pass

                    track_list = self.stream_listener.generate_track_list(
                        message['sess_id'], message['track'])

                    self.stream.filter(track=track_list, is_async=True)
                else:
                    self.stream_listener.websockets = message['websockets']

                    # If there are no more connections, then stop streaming.
                    if len(self.stream_listener.websockets) is 0:
                        self.stream.stop_streaming()

                self.queue.task_done()
            except Empty:
                continue

        self.stream.stop_streaming()

        self.logger.debug('Thread #{0} has stopped'.format(self.ident))
