import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk import FreqDist

analyser = SentimentIntensityAnalyzer()
default_stopwords = set(stopwords.words('english'))


def calculate_polarity_scores_from_tweet(text):
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
        from each tweet that we get and will be fed into a function that ntlk has called FreqDist to calculate the frequency
        distribution in a tweet.
    '''
    polarity_tweet = re.sub(r"[^a-zA-Z#!?']", " ", tweet)
    hashtag_tweet = re.sub(r"[^a-zA-Z#]", " ", tweet)

    tokenize_hashtag_list = hashtag_tweet.split()
    filtered_hashtag_list = [
        word for word in tokenize_hashtag_list if not word in default_stopwords]

    return (polarity_tweet, filtered_hashtag_list)


def extract_hashtags(tweet_list):
    hashtags = []

    for word in tweet_list:
        ht = re.findall(r"#(\w+)", word)
        hashtags.append(ht)

    return hashtags


def get_hashtag_frequencies_from_tweet(tweet_list):
    hashtags = extract_hashtags(tweet_list)
    return FreqDist(sum(hashtags, []))
