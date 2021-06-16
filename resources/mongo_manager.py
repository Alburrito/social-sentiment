import datetime
from pymongo import MongoClient
import logging

from resources.utils import MONGO_LOGGER
from resources.utils import MONGO_CONFIG

__LOGGER = logging.getLogger(MONGO_LOGGER)

DB_HOST = MONGO_CONFIG["DB_HOST"]
DB_PORT = MONGO_CONFIG["DB_PORT"]
DB_NAME = MONGO_CONFIG["DB_NAME"]
DB_URI = f"mongodb://{DB_HOST}:{DB_PORT}/{DB_NAME}"
__LOGGER.info('Connecting to MongoDB...')
CLIENT = MongoClient(DB_HOST, int(DB_PORT))
DB = CLIENT[DB_NAME]
COL_USERS = DB[MONGO_CONFIG["COL_USERS"]]
COL_RECORDS = DB[MONGO_CONFIG["COL_RECORDS"]]
COL_TWEETS = DB[MONGO_CONFIG["COL_TWEETS"]]
__LOGGER.info(f'Connected to {DB_URI}')


#######################################
#                USERS                #
#######################################

def get_twitter_ids():
    __LOGGER.info('Retrieving twitter id list...')
    query = {"twitter_ids": { "$gt" : "-1"}}
    fields = {"_id":0, "twitter_ids": 1}
    result = COL_USERS.find(query, fields)
    __LOGGER.info('Twitter ID list retrieved.')
    return result


def update_profile(has_records, twitter_id , followers, favourites, engagement, current_sentiment, score, post_count, relevancy, top_tweets):
    __LOGGER.info(f'Updating {twitter_id} profile')
    today = datetime.datetime.today()
    today = today.strftime("%Y-%m-%d %H:%M:%S")

    if not has_records:
        __create_records(today, twitter_id , followers, favourites, engagement, current_sentiment, score, post_count, relevancy, top_tweets)
    else:
        __update_records(today, twitter_id, followers, favourites, engagement, current_sentiment, score, post_count, relevancy, top_tweets)

def __create_records(today, twitter_id , followers, favourites, engagement, current_sentiment, score, post_count, relevancy, top_tweets):
    records = dict()
    tmp = {
        'date': today,
        'value': followers
    }
    records['foll_records'] = []
    records['foll_records'].append(tmp)

    tmp = {
        'date': today,
        'value': favourites
    }
    records['fav_records'] = []
    records['fav_records'].append(tmp)

    tmp = {
        'date': today,
        'value': engagement
    }
    records['eng_records'] = []
    records['eng_records'].append(tmp)

    tmp = {
        'date': today,
        'value': score
    }
    records['score_records'] = []
    records['score_records'].append(tmp)

    tmp = {
        'date': today,
        'value': post_count
    }
    records['p_count_records'] = []
    records['p_count_records'].append(tmp)

    tmp = {
        'date': today,
        'value': relevancy
    }
    records['rel_records'] = []
    records['rel_records'].append(tmp)

    tmp = {
        'date': today,
        'pos': round(current_sentiment['pos'], 2),
        'neu': round(current_sentiment['neu'], 2),
        'neg': round(current_sentiment['neg'], 2)
    }
    records['sent_records'] = []
    records['sent_records'].append(tmp)
    records['twitter_id'] = twitter_id

    COL_RECORDS.insert_one(records)
    __LOGGER.info(f'Records of twitter user {twitter_id} created')

    top_tweets_doc = {'twitter_id':twitter_id, 'tweets':top_tweets}
    COL_TWEETS.insert_one(top_tweets_doc)
    __LOGGER.info(f'Top Tweets of twitter user {twitter_id} created')

def __update_records(today, twitter_id, followers, favourites, engagement, current_sentiment, score, post_count, relevancy, top_tweets):
    records = get_user_records(twitter_id)

    if len(records['foll_records']) >= 30:
        tmp = records['foll_records'].pop(0)
        tmp = records['fav_records'].pop(0)
        tmp = records['eng_records'].pop(0)
        tmp = records['score_records'].pop(0)
        tmp = records['p_count_records'].pop(0)
        tmp = records['rel_records'].pop(0)
        tmp = records['sent_records'].pop(0)

    records['foll_records'].append({'date':today, 'value':followers})
    records['fav_records'].append({'date':today, 'value':favourites})
    records['eng_records'].append({'date':today, 'value':engagement})
    records['score_records'].append({'date':today, 'value':score})
    records['p_count_records'].append({'date':today, 'value':post_count})
    records['rel_records'].append({'date':today, 'value':relevancy})

    pos = round(current_sentiment['pos'],2)
    neu = round(current_sentiment['neu'],2)
    neg = round(current_sentiment['neg'],2)
    records['sent_records'].append({'date':today, 'pos':pos, 'neu':neu, 'neg':neg})

    filter = {'twitter_id' : twitter_id}
    newrecords = {'$set':
                    {
                        'foll_records':records['foll_records'],
                        'fav_records':records['fav_records'],
                        'eng_records':records['eng_records'],
                        'score_records':records['score_records'],
                        'p_count_records':records['p_count_records'],
                        'rel_records':records['rel_records'],
                        'sent_records':records['sent_records']
                    }
                }
    
    COL_RECORDS.update_one(filter,newrecords)
    __LOGGER.info(f'Records of twitter user {twitter_id} updated')

    # Top Tweets
    newrecords = {'$set':{'tweets':top_tweets}}
    COL_TWEETS.update_one(filter,newrecords)
    __LOGGER.info(f'Top Tweets of twitter user {twitter_id} updated')


def has_records(twitter_id:str):
    __LOGGER.info(f'Checking {twitter_id} records...')
    query = {"twitter_id" : twitter_id}
    result = COL_RECORDS.find_one(query)
    if result is not None:
        __LOGGER.info(f'User {twitter_id} has records')
        return True
    else:
        __LOGGER.info(f'User {twitter_id} has no records')
        return False


#######################################
#             USER TWEETS             #
#######################################

def get_top_tweets(twitter_id):
    __LOGGER.info(f'Retrieving {twitter_id} top tweets...')
    query = {"twitter_id": twitter_id}
    fields = {'_id':0}
    result = COL_TWEETS.find_one(query, fields)
    __LOGGER.info(f'User {twitter_id} top tweets retrieved.')
    return result

#######################################
#             USER RECORDS            #
#######################################

def get_user_records(twitter_id):
    """
    Args:
        (twitter_id : str) ID de twitter en BD
    """
    __LOGGER.info(f'Retrieving {twitter_id} records...')
    query = {"twitter_id": twitter_id}
    fields = {'_id':0}
    result = COL_RECORDS.find_one(query, fields)
    __LOGGER.info(f'User {twitter_id} records retrieved.')
    return result

def get_user_stats_records(twitter_id):
    """
    Args:
        (twitter_id : str) ID de twitter en BD
    """
    __LOGGER.info(f'Retrieving {twitter_id} stats records...')
    query = {"twitter_id": twitter_id}
    fields = {'_id':0,  'sent_records' : 0}
    result = COL_RECORDS.find_one(query, fields)
    __LOGGER.info(f'User {twitter_id} stats retrieved.')
    return result

def get_user_follower_records(twitter_id):
    """
    Args:
        (twitter_id : str) ID de twitter en BD
    """
    __LOGGER.info(f'Retrieving {twitter_id} followers records...')
    query = {"twitter_id": twitter_id}
    fields = {'_id':0, 'twitter_id': 1, 'date': 1, 'foll_records' : 1}
    result = COL_RECORDS.find_one(query, fields)
    __LOGGER.info(f'User {twitter_id} followers records retrieved.')
    return result

def get_user_engagement_records(twitter_id):
    """
    Args:
        (twitter_id : str) ID de twitter en BD
    """
    __LOGGER.info(f'Retrieving {twitter_id} engagement records...')
    query = {"twitter_id": twitter_id}
    fields = {'_id':0, 'twitter_id': 1, 'date': 1, 'eng_records' : 1 }
    result = COL_RECORDS.find_one(query, fields)
    __LOGGER.info(f'User {twitter_id} engagement records retrieved.')
    return result

def get_user_favourites_records(twitter_id):
    """
    Args:
        (twitter_id : str) ID de twitter en BD
    """
    __LOGGER.info(f'Retrieving {twitter_id} favourites records...')
    query = {"twitter_id": twitter_id}
    fields = {'_id':0, 'twitter_id': 1, 'date': 1, 'fav_records' : 1}
    result = COL_RECORDS.find_one(query, fields)
    __LOGGER.info(f'User {twitter_id} favourites records retrieved.')
    return result

def get_user_score_records(twitter_id):
    """
    Args:
        (twitter_id : str) ID de twitter en BD
    """
    __LOGGER.info(f'Retrieving {twitter_id} score records...')
    query = {"twitter_id": twitter_id}
    fields = {'_id':0, 'twitter_id': 1, 'date': 1, 'score_records' : 1 }
    result = COL_RECORDS.find_one(query, fields)
    __LOGGER.info(f'User {twitter_id} score records retrieved.')
    return result

def get_user_sentiment_records(twitter_id):
    """
    Args:
        (twitter_id : str) ID de twitter en BD
    """
    __LOGGER.info(f'Retrieving {twitter_id} sentiment records...')
    query = {"twitter_id": twitter_id}
    fields = {'_id':0, 'twitter_id': 1, 'date': 1, 'sent_records' : 1 }
    result = COL_RECORDS.find_one(query, fields)
    __LOGGER.info(f'User {twitter_id} sentiment records retrieved.')
    return result

def get_post_count_records(twitter_id):
    """
    Args:
        (twitter_id : str) ID de twitter en BD
    """
    __LOGGER.info(f'Retrieving {twitter_id} post count records...')
    query = {"twitter_id": twitter_id}
    fields = {'_id':0, 'twitter_id': 1, 'date': 1, 'p_count_records' : 1 }
    result = COL_RECORDS.find_one(query, fields)
    __LOGGER.info(f'User {twitter_id} post count records retrieved.')
    return result

def get_relevancy_records(twitter_id):
    """
    Args:
        (twitter_id : str) ID de twitter en BD
    """
    __LOGGER.info(f'Retrieving {twitter_id} relevancy records...')
    query = {"twitter_id": twitter_id}
    fields = {'_id':0, 'twitter_id': 1, 'date': 1, 'rel_records' : 1 }
    result = COL_RECORDS.find_one(query, fields)
    __LOGGER.info(f'User {twitter_id} score records retrieved.')
    return result

def get_last_values(twitter_id):
    """
    Args:
        (twitter_id : str) ID de twitter en BD
    """
    __LOGGER.info(f'Retrieving {twitter_id} last stat values...')
    query = {"twitter_id": twitter_id}
    fields = {'_id':0, 'sent_records':0}
    result = COL_RECORDS.find_one(query, fields)
    if result is None:
        return None
    last_stats = {}
    last_stats["last_foll"] = result['foll_records'][-1]['value']
    last_stats["last_fav"] = result['fav_records'][-1]['value']
    last_stats["last_eng"] = result['eng_records'][-1]['value']
    last_stats["last_rel"] = result['rel_records'][-1]['value']
    last_stats["p_frequency"] = 0
    for day in result['p_count_records']:
        last_stats["p_frequency"] += day['value']
    last_stats["p_frequency"]  /= len(result["p_count_records"] )
    last_stats["last_score"] = result['score_records'][-1]['value']
    __LOGGER.info(f'User {twitter_id} last stat values retrieved.')
    return last_stats