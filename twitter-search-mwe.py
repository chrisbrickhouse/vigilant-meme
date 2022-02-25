import tweepy
from os import environ

__author__ = "Christian Brickhouse, Bran Papineau"
__copyright__ = "Copyright 2022, Christian Brickhouse and Bran Papineau"
__credits__ = []
__license__ = "BSD-3-clause"
__version__ = "0.0.1"
__maintainer__ = "Christian Brickhouse"
__email__ = "brickhouse@stanford.edu"
__status__ = "Development"

class Tweet():
    """Data class for tweets returned by our query

    This class organizes the data returned for each tweet into a better
    format and adds methods for printing and storing our data in the 
    correct locations.
    """
    def __init__(self, tweet, user = None):
        """Constructor for Tweet object

        Args:
            tweet (tweepy.Tweet): A tweet class returned by tweepy
            user (tweepy.User): A user class returned by tweepy
        """
        self.id = tweet.id
        self.text = tweet.text
        self.link = 'https://www.twitter.com/user/status/'+str(self.id)
        self.user_id = tweet.author_id
        self.user_resp = user
        self.user_name = user.data['username']
        self.time = tweet.created_at
        self.context = tweet.referenced_tweets

    def __str__(self):
        """Format the data for printing

        The __str__ method of a class is called by `print` and `str`
        so by defining it ourselves we are able to format the printing
        output and simply call `print(Tweet)` whenever needed.
        """
        string = ''
        if self.context:
            string = string + str(self.context) 
            string = string + '\n' 
        string = string + self.user_name + ' at ' + str(self.time) + ':\t'
        string = string + self.text + '\n'
        string = string + '\t' + self.link
        return(string)

class Query():
    """A wrapper for constructing and managing API queries

    One of the advantages here is that the Query object manages the
    associations between Queries and their responses which makes
    simultaneous searches easier. For example, we can have multiple 
    instances which all associate their own query, `Query.query`, with
    the corresponding response, `Query.response`, regardless of how
    many instances or queries we run.

    We can also overwrite queries using the `Query.new` method.
    """
    def __init__(self, client):
        self.client = client

    def new(self, constructor_function):
        """Construct a query using a callback function.

        The callback allows for the user to specify a pre-written
        function which returns a query string which this method
        then executes. This encourages programmatic construction
        of queries rather than directly passing strings.

        Args:
            constructor_function (function->str): A callback which returns
                the query string.
        """
        self.query = constructor_function()

    def run(self,**kwargs):
        """A wrapper for the recent tweet search.

        The **kwarg allows this method to take arbitrary keyword
        arguments which are then passed directly to `client.search_recent_tweets`

        For more info on unpacking see the Python documentation:
        https://docs.python.org/3/tutorial/controlflow.html#arbitrary-argument-lists
        """
        response = self.client.search_recent_tweets(
                self.query,
                **kwargs
            )
        # Automatically creates a Response object
        self.response = Response(self.client,response, response_cleaner)

class Response():
    """A wrapper for response objects

    Similar to `Tweet` objects, this class manages the cleaning and organization
    of responses to queries. It is directly called by `Query.run` so users should
    usually not need to interact with it directly.
    """
    def __init__(self, client, response, make_tweets_callback):
        """Construct a new response instance.

        Args:
            client (tweepy.Client): A tweepy client instance for accessing the API.
            response (tweepy.Response): The response data for a query.
            make_tweets_callback (function->list): A callback which takes a tweepy client and
                response object and returns a list of tweets in the user's prefered format.
        """
        self.client = client
        self.tweets = make_tweets_callback(client, response)

    def __str__(self):
        """Prints each tweet.
        """
        for tweet in self.tweets:
            print(tweet)


def response_cleaner(client, response):
    """Callback for `Response.__init__`.

    Returns:
        list: A list of Tweet objects from the response
    """
    tweet_list = []
    for tweet in response.data:
        # Get the user object for the tweet author and pass to Tweet as well
        uname = client.get_user(id=tweet.author_id)
        # Make the Tweet instance and add it to the list
        tweet_list.append(Tweet(tweet, user = uname))
    return tweet_list


def query_constructor():
    """Construct a query.

    Returns:
        string: A Twitter search query.
    """
    cons = ['c','d','g','j','k','l','m','n','q','r','t','v','x','y','z']
    querussy = '(' + " OR ".join([ x+'ussy' for x in cons]) + ') lang:en'
    return querussy

if __name__ == "__main__":
    # Load tokens from environment variables.
    try:
        bearer_token = environ['BEARER_TOKEN']
        consumer_secret = environ['CONSUMER_SECRET']
        consumer_key = environ['CONSUMER_KEY']
        access_token = environ['ACCESS_TOKEN']
        access_token_secret = environ['ACCESS_TOKEN_SECRET']
    except KeyError as e:
        msg = 'Tokens not found. Have you run `source .secrets`?'
        raise AttributeError(msg)

    # Start client
    client = tweepy.Client(
            bearer_token,
            consumer_key,
            consumer_secret,
            access_token,
            access_token_secret
        )

    query = Query(client)
    query.new(query_constructor)
    query.run(
            tweet_fields = [
                'author_id',
                'created_at',
                'referenced_tweets'
            ]
        )

    print(query.response)
