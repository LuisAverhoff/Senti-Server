import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords

analyser = SentimentIntensityAnalyzer()
default_stopwords = set(stopwords.words('english'))


def calculate_polarity_score_from_tweet(text):
    return analyser.polarity_scores(text)


def remove_pattern(text, pattern):
    matches = re.findall(pattern, text)

    for match in matches:
        text = re.sub(match, '', text)

    return text


def preprocess_tweet(tweet):
    # remove twitter handles (@xxx)
    tweet = remove_pattern(tweet, r"@[\w]*")

    # remove URL links (httpxxx)
    tweet = remove_pattern(tweet, r"https?://[A-Za-z0-9./]*")

    '''
        remove special characters, numbers and punctuations. Exceptions are #, !, ' and ? as vader uses both ! and ? 
        characters for emphasis and will affect our polarity score, vader also takes into account contractions and we 
        want to keep hashtags to calculate which hashtags were more frequent. Because of all these exceptions, we are 
        going to have two tweets. One tweet called polarity tweet that is feed into the vader analyzer and another tweet
        that only has letters and the hashtag. The second tweet is what we will use to calculate the frequency of a hashtag
        from each tweet that we get and will be feed into a function that ntlk has called FreqDist to calculate the frequency
        distribution in a tweet.
    '''
    polarity_tweet = re.sub(r"[^a-zA-Z#!?']", " ", tweet)
    frequency_tweet = re.sub(r"[^a-zA-Z#]", " ", tweet)

    return (polarity_tweet, frequency_tweet)

def get_hashtag_frequencies_from_tweet(tweet):
    pass