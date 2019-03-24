import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyser = SentimentIntensityAnalyzer()


def calculate_polarity_score(text):
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
        remove special characters, numbers and punctuations (except for #, ! and ? as vader uses both ! and ? 
        characters for emphasis, apostrophe for contractions and we want to keep hashtags for further
        analsysis)
    '''
    tweet = re.sub(r"[^a-zA-Z#!?']", " ", tweet)

    return tweet
