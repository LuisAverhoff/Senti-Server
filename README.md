# Senti Server

Backend for the senti web application to analyze all incoming tweets using the Tweepy API. Data that get sent back to the client is a message of the form:

```
message = {
  polarityIndex: 'An index where 0 is positive sentiment, 1 is negative sentiment and 2 is neutral',
  hashtags: 'A dictionary of all the hashtags that were found and their frequency.'
}
```

It is important to note that the rate at which a user receives a message is entirely dependent on the query that the user makes and how well your internet connection is. If the user make a query for a popular topic that millions of users talk about like trump, then you can bet that the rate at which you receive your messages will be extremely fast. This is the opposite case for very obscure topics.

# Installing Dependencies

To successfully install all dependencies, make sure you have a python version 3.7 or higher. Then install a pip module called pipenv via `py -3 -m pip install pipenv` or `pip install pipenv`. This module is in charged of installing all dependencies that are listed in the `Pipfile`. Once you have pipenv installed, simply run `pipenv install` to install all dependencies.

# Setting up Your Environment

A `.env` file is required so that the correct environment settings can be loaded during runtime. A complete list of all the required environment variables can be found in the `.env.sample` file.
Before we continue, let us create a twitter developer account.

## Registering for a twitter developer account.

Follow this link <https://developer.twitter.com/en/apply-for-access.html> to apply for a twitter developer account and register your application. Once you have a developer account and have registered your application, if you go into the details section of your application, you should see your `TWITTER_CONSUMER_API_KEY` and `TWITTER_CONSUMER_API_SECRET_KEY` already generated for you. For the `TWITTER_ACCESS_KEY` and the `TWITTER_ACCESS_SECRET_KEY` you will need to follow these steps:

1. Login to your Twitter account on developer.twitter.com.
2. Navigate to the Twitter app dashboard and open the Twitter app for which you would like to generate access tokens.
3. Navigate to the "Keys and Tokens" page.
4. Select 'Create' under the "Access token & access token secret" section.

After that, simply paste these four keys in your `.env` file and you're done with this step.

## Downloading the Required NLTK Modules

Run this in your python intrepreter shell so you can download the required NTLK modules to run the server locally.

```
>>> import nltk
>>> nltk.download('stopwords')
>>> nltk.download('punkt')
```

If you are worried that these NLTK modules won't exist in production, don't worry. Heroku takes care of this for you by looking at the modules specified in the `nltk.txt` file.
Follow this link <https://devcenter.heroku.com/articles/python-nltk> if you want to find out more.

# Running the Server Locally

To run the server, type `pipenv shell` to start up your virtual environment. Then all you have to do is type `python server.py` for it to use the python interpreter that is in your virtual environment.

# Deploying to Production

Before deploying to production, we need to setup a free heroku account. Once you have created your free heroku account, there are three important things you need to do.

- First, go to the deploy page and connect your github repo to your heroku account. While you are
  there, enable automatic deployment so that every push to master is an automatic build. Do not enable the "wait for CI to pass before deploy" button unless you have CI setup.
- Lastly, go to your settings page and add all the environment variables that this application needs.

# Limitations

There is a chance that tweet might contain multiple search terms where a one search term has a positive sentiment and the other one has a negative sentiment or neutral or whatever. In this case,
the analyzer will return only a single sentiment for both search terms. Take for example the tweet, "I love pizza but not while watching sports". The search terms are pizza and sports. It is clear that pizza has a positives sentiment and sports has a negative sentiment but the analyzer only gives out a single score and assigns it to both search terms. A better way would be to figure out how to gives different polarity scores for the same tweet when it has multiple topics embedded in it and each topic has a different sentiment.

# License

The MIT License (MIT)

Copyright (c) 2019 Luis Manuel Averhoff

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
