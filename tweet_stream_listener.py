import logging
import asyncio
from tornado.websocket import WebSocketClosedError
from tweepy import StreamListener, OAuthHandler, Stream, API
from constants import SETTINGS
from tweet_sentiment_analyzer import get_polarity_index_from_tweet, \
    get_hashtag_frequencies_from_tweet, preprocess_tweet

auth = OAuthHandler(
    SETTINGS["TWITTER_CONSUMER_API_KEY"], SETTINGS["TWITTER_CONSUMER_API_SECRET_KEY"])

auth.set_access_token(
    SETTINGS["TWITTER_ACCESS_KEY"], SETTINGS["TWITTER_ACCESS_SECRET_KEY"])

api = API(auth, wait_on_rate_limit=True)


class TweetStreamListener(StreamListener):

    def __init__(self, queue):
        self.api = api
        self.queue = queue
        self.websockets = {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self.stream = Stream(auth=self.api.auth, listener=self,
                             tweet_mode='extended')
        self.current_searches = {}

    def start_tracking(self, sess_id, track):
        # New tweet to listen to.
        self.current_searches[sess_id] = track.lower()

        # Disconnect the stream momentarily to update track list.
        self.stop_tracking()

        '''
            Create a new search term list and put it all in a set to remove
            potential duplicate search terms.
        '''
        search_terms = set(self.current_searches.values())
        self.stream.filter(track=search_terms, languages=['en'])

    def stop_tracking(self):
        self.stream.disconnect()

    def on_status(self, status):
        # We are not processing retweets. Only new tweets.
        if getattr(status, 'retweeted_status', None):
            return

        self.queue.put(status)

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


def listen_for_tweets(listener, queue):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        message = queue.get()

        if message is None:
            break

        # We still have websockets to send this message to.
        if len(listener.websockets) > 0:
            task = asyncio.ensure_future(process_tweet(message, listener.current_searches,
                                                       listener.websockets))
            loop.run_until_complete(task)

        queue.task_done()

    loop.close()


async def process_tweet(status, current_searches, websockets):
    tweet = status.text.lower()

    # If extended_tweet exists, this the means that status.text is truncated.
    # We want the entire text.
    if getattr(status, 'extended_tweet', None):
        tweet = status.extended_tweet['full_text'].lower()

    polarity_tweet, filtered_hashtag_list = preprocess_tweet(tweet)

    polarityIndex = get_polarity_index_from_tweet(polarity_tweet)
    hashtag_freqs = get_hashtag_frequencies_from_tweet(filtered_hashtag_list)

    message = {
        'polarityIndex': polarityIndex,
        'hashtags': dict(hashtag_freqs)
    }

    sess_ids = []

    for sess_id, topic in current_searches.items():
        if topic in filtered_hashtag_list:
            sess_ids.append(sess_id)

    for sess_id in sess_ids:
        try:
            # We need this check and exception in case a websocket closes abruptly.
            if sess_id in websockets:
                await websockets[sess_id].write_message(message)
        except WebSocketClosedError:
            continue
