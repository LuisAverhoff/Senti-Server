# Senti Server

Backend for the senti web application to analyze all incoming tweets using the Tweepy API. Data that get sent back to the client is a message of the form:

```
message = {
  polarity: 'A value between -1.0 and 1.0. -1.0 is completely negative and 1.0 is completely positive.
}
```

It is important to note that the rate at which a user receives a message is entirely dependent on the query that the user makes. If the user make a query for a popular topic that millions of users talk about like trump, then you can bet that the rate at which you receive your messages will be extremely fast. This is the opposite case for very obscure topics.

# Installing Dependencies

To successfully install all dependencies, make sure you have a python version 3.7 or higher. Then install a pip module called pipenv via `py -3 -m pip install pipenv` or `pip install pipenv`. This module is in charged of installing all dependencies that are listed in the `Pipfile`. Once you have pipenv installed, simply run `pipenv install` to install all dependencies.

# Setting up Your Environment

A `.env` file is required so that the correct environment settings can be loaded during runtime. A complete list of all the required environment variables can be found in the `.env.sample` file.
Before we continue, let us setup our rabbitmq server and register a twitter developer account.

## Registering for a twitter developer account.

Follow this link <https://developer.twitter.com/en/apply-for-access.html> to apply for a twitter developer account and register your application. Once you have a developer account and have registered your application, if you go into the details section of your application, you should see your `TWITTER_CONSUMER_API_KEY` and `TWITTER_CONSUMER_API_SECRET_KEY` already generated for you. For the `TWITTER_ACCESS_KEY` and the `TWITTER_ACCESS_SECRET_KEY` you will need to follow these steps:

1. Login to your Twitter account on developer.twitter.com.
2. Navigate to the Twitter app dashboard and open the Twitter app for which you would like to generate access tokens.
3. Navigate to the "Keys and Tokens" page.
4. Select 'Create' under the "Access token & access token secret" section.

After that, simply these paste these four keys in your `.env` file and you're done with this step.

## Setting up a RabbitMQ Server.

If you go to this link <https://www.rabbitmq.com/download.html> you will see a bunch of different installation guides. Pick the guide that matches your current system. After you have gone through this process, you need to make sure that the following port is open and is not blocked by your firewall:

- 5672: used by AMQP 0-9-1 and 1.0 clients without and with TLS

For a full list of all the ports that RabbitMQ uses, follow this link <https://www.rabbitmq.com/networking.html#ports>

If you would like to use the RabbitMQ Admin Management UI(this uses port 15672 and make sure that this port is not blocked as well), you are going to need to enable the management plugin.

To enable this plugin, go to the directory where the RabbitMQ server was installed, go into the sbin folder and run this command `rabbitmq-plugins enable rabbitmq_management`

Now you should be able to go to `localhost:15672` and see the admin UI. You are going to need to login as guest when you first install RabbitMQ. The credentials for the guest user is:

- username: `guest`
- password: `guest`

You can use these credentials to connect your RabbitMQ server during development or create your own user with its own credentials and use those. Whichever one you choose, these credentials are what you enter for these environment variables:

- `RABBITMQ_USERNAME`
- `RABBITMQ_PASSWORD`

**Note** If you create your own user, make sure to set the value for the `virtual host` property. Whatever value you entered for this property make sure that you also initialize the `RABBITMQ_VIRTUAL_HOST` environment variable with that value as well.

`RABBITMQ_HOST` can be set to localhost during development so that it can connect to the RabbitMQ server that is running on your machine. During poduction, this should point to your live RabbitMQ server.

After this, you have officially setup your RabbitMQ server.

## Downloading the Required NLTK Modules
Run this in your python intrepreter shell so you can download the required NTLK modules to run the server.

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

This repo is connected to heroku and and any changes made in your master branch, heroku will catch those changes and build the project for you.

# TODO

- Create a wordcloud to showcase the frequency of all the hashtags for a specific query
- Create a nice deploy to heroku button for to people to use.