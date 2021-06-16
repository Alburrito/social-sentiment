import tweepy
import logging
from random import choice

from resources.utils import SCRAPPER_LOGGER
from resources.utils import SCRAPPER_CONFIG


__TWITTER_API_KEY = SCRAPPER_CONFIG["TWITTER_API_KEY"]
__TWITTER_API_SECRET_KEY = SCRAPPER_CONFIG["TWITTER_API_SECRET_KEY"]
__TWITTER_BEARER_TOKEN = SCRAPPER_CONFIG["TWITTER_BEARER_TOKEN"]
__TWITTER_ACCESS_TOKEN = SCRAPPER_CONFIG["TWITTER_ACCESS_TOKEN"]
__TWITTER_ACCESS_TOKEN_SECRET = SCRAPPER_CONFIG["TWITTER_ACCESS_TOKEN_SECRET"]
__SPAIN_WOEID = SCRAPPER_CONFIG["SPAIN_WOEID"]

__LOGGER = logging.getLogger(SCRAPPER_LOGGER)
__LOGGER.propagate = False


def __connect_twitter_OAuth():
    __LOGGER.info('Connecting via tweepy OAuth...')
    try:
        auth = tweepy.OAuthHandler(__TWITTER_API_KEY, __TWITTER_API_SECRET_KEY)
        auth.set_access_token(__TWITTER_ACCESS_TOKEN,
                              __TWITTER_ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)
        __LOGGER.info('Connected.')
        return api
    except Exception as e:
        __LOGGER.error(f'Could not authenticate in Twitter API: {e}')
        exit(-200)

__API = __connect_twitter_OAuth()


def get_profile_info(twitter_id: str) -> dict:
    """
    Args:
        (twitter_id : str)

    Returns:
        (userInfo : dict) - dict with keys ['user_id', 'photo' 'name', 'username', 'bio', 'verified']
    """
    __LOGGER.info(f'Retrieving user profile of: {twitter_id}...')
    try:
        user = __API.get_user(twitter_id)
        userInfo = {
            "user_id" : user.id_str,
            "photo": user.profile_image_url,
            "name": user.name,
            "username": user.screen_name,
            "bio": user.description,
            "verified": user.verified
        }
        __LOGGER.info(f'Profile {twitter_id} retrieved.')
        return userInfo
    except Exception as e:
        __LOGGER.error(f'Error while retrieving profile of {twitter_id}: {e}')
        return -201

def get_user_last_tweets_and_info(twitter_id:str, count:int = 10) -> dict:
    """
    Args:
        twitter_id (str): Twitter id of user
        count (int, optional): Number of tweets retrieved. Defaults to 10.

    Returns:
         dict: keys -> [user_profile(dict), user_stats(dict), user_tweets(list of dicts)]
    """
    __LOGGER.info(f'Retrieving last tweets of: {twitter_id}...')
    last_tweets = __API.user_timeline(user_id=twitter_id, count=count, include_rts=False, tweet_mode='extended')
    if len(last_tweets) == 0:
        __LOGGER.error(f'Error while retrieving last tweets of {twitter_id}. No tweets')
        return None
    processed_info = __process_tweet_list(twitter_id, last_tweets)
    __LOGGER.info(f'Last tweets of {twitter_id} retrieved.')
    return processed_info

def __process_tweet_list(twitter_id:str, last_tweets) -> dict:
    """
    Args:
        twitter_id (str): [description]
        last_tweets ([type]): [description]

    Returns:
        dict: keys -> [user_profile(dict), user_stats(dict), user_tweets(list of dicts)]
    """

    __LOGGER.info(f'Processing last tweets of: {twitter_id}...')

    user = last_tweets[0].user

    tweet_list = []
    for tweet in last_tweets:
        t = {}
        t['tweet_id'] = tweet.id_str
        t['text'] = tweet.full_text
        t['fav_count'] = tweet.favorite_count
        t['rt_count'] = tweet.retweet_count
        t['date'] = tweet.created_at
        tweet_list.append(t)

    urls = []
    if 'url' in list(user.entities.keys()):
        for u in user.entities['url']['urls']:
            urls.append(u['expanded_url'])
        for u in user.entities['description']['urls']:
            urls.append(u['expanded_url'])

    result = {
        "user_profile": {
            'user_id_str': user.id_str,
            'photo': user.profile_image_url,
            'name': user.name,
            'username': user.screen_name,
            'bio': user.description,
            'urls' : urls,
            'verified': user.verified
        },
        "user_stats": {
            'followers': user.followers_count,
            'fav_count': user.favourites_count
        },
        "user_tweets": tweet_list
    }
    __LOGGER.info(f'Processed last tweets of {twitter_id}')
    return result

def get_tweet_responses(screen_name: str, tweet_id: str) -> list:
    """
    Args:
        screen_name (str): @screenname of the user in Twitter
        tweet_id (str): id_str of the tweet whose responses we want

    Returns:
        list: list of responses (str)
    """
    responses = []
    for tweet in tweepy.Cursor(__API.search, q=f'to:{screen_name}', 
                                result_type='recent', tweet_mode='extended', 
                                timeout=999999).items(1000):
        if hasattr(tweet, 'in_reply_to_status_id_str'):
            if (tweet.in_reply_to_status_id_str==tweet_id):
                responses.append(tweet.full_text)
                if len(responses) == 3:
                    break
    
    return responses

def get_spain_trending_topics() -> list:
    """
    Returns:
        list: List of Spain Trending Topic (str)
    """
    __LOGGER.info(f'Retrieving Trending Topic of country SPAIN')
    result = []
    tt = __API.trends_place(__SPAIN_WOEID)
    for trend in tt[0]['trends']:
        result.append(trend['name'].lower())
    __LOGGER.info(f'Retrieved Spain Trending Topic')
    return result
