import logging
from flask import Flask, jsonify, request
import json

import resources.mongo_manager as mgr
import resources.scrapper as ts
import resources.pystatistics as pystats
from resources.utils import FLASK_CONFIG, DateTimeEncoder

DAILY_TWEETS = 30


#######################################
#                 API                 #
#######################################

app = Flask(__name__)
logger = logging.getLogger(__name__)

#######################
#       ROUTES       #
#######################


@app.route('/')
def index():
    logger.info('INDEX')
    return jsonify({'campo1': 'una prueba',
                    'campo2': 2})


@app.route('/test', methods=['GET'])
def test():
    logger.info('-- STARTING TEST --')
    twitter_id = request.args["twitter_id"]
    result = ts.get_user_last_tweets_and_info(twitter_id)
    json_result = json.dumps(result, ensure_ascii=False, cls=DateTimeEncoder)
    logger.info('-- TEST FINISHED --')
    return json_result

#############
#  TWITTER  #
#############

@app.route('/twitter', methods=['GET'])
def index_twitter():
    return 'twitter index'


@app.route('/twitter/get_id', methods=['GET'])
def get_twitter_id_from_username():
    if request.args and 'username' in request.args.keys():
        username = request.args.get('username')
        profile_info = ts.get_profile_info(username)
        if profile_info != -1:
            result = {'id_str' : profile_info['user_id']}
            return json.dumps(result, ensure_ascii=False)
        else:
            logger.error(f'Error while retrieving id of {username}')
            data = {'message':' Internal server error'}
            return jsonify(data), 500
    else:
        logger.error("No 'username' parameter found")
        data = {'message':' Internal server error'}
        return jsonify(data), 500


@app.route('/twitter/profile_info', methods=['GET'])
def get_profile_info():
    """
    Returns obj with structure:
    {   
        photo:      str,    user's profile photo,
        name:       str,    user's nickname,
        username:   str,    user's @,
        bio:        str,    user's profile description,
        verified:   bool,   True if user is verified
    }
    """
    if request.args and 'twitter_id' in request.args.keys():
        twitter_id = request.args.get('twitter_id')
        profile_info = ts.get_profile_info(twitter_id)
        if profile_info != -1:
            return json.dumps(profile_info, ensure_ascii=False)
        else:
            logger.error(f'Error while retrieving profile of {twitter_id}')
            data = {'message':'Not found'}
            return jsonify(data), 404
    else:
        logger.error("No 'twitter_id' parameter found")
        data = {'message':'Bad Request'}
        return jsonify(data), 400


@app.route('/twitter/dashboard_stats', methods=['GET'])
def get_twitter_dashboard_stats():
    if request.args and 'twitter_id' in request.args.keys():
        twitter_id = request.args.get('twitter_id')
        current_info = ts.get_user_last_tweets_and_info(twitter_id)
        if current_info is not None:
            top_tweets = mgr.get_top_tweets(twitter_id)
            last_stats = mgr.get_last_values(twitter_id)
            sentiment_records = mgr.get_user_sentiment_records(twitter_id)
            if top_tweets is not None and last_stats is not None and sentiment_records is not None:
                result = pystats.get_twitter_dashboard_stats(current_info, top_tweets, last_stats, sentiment_records)
            else:
                data = {'message':'Not found'}
                return jsonify(data), 404
            return json.dumps(result, ensure_ascii=False, cls=DateTimeEncoder) 
        else:
            logger.error(f'Error while retrieving current info of {twitter_id}')
            data = {'message':'Not found'}
            return jsonify(data), 404
    else:
        logger.error("No 'twitter_id' parameter found")
        data = {'message':'Bad Request'}
        return jsonify(data), 400
        

@app.route('/twitter/record_stats', methods=['GET'])
def get_twitter_records():
    if request.args and 'twitter_id' in request.args.keys():
        twitter_id = request.args.get('twitter_id')
        records = mgr.get_user_stats_records(twitter_id)
        if records is not None:
            return json.dumps(records, ensure_ascii=False, cls=DateTimeEncoder) 
        else:
            logger.error("No 'twitter_id' parameter found")
            data = {'message':'Not found'}
            return jsonify(data), 404
    else:
        logger.error("No 'twitter_id' parameter found")
        data = {'message':'Bad Request'}
        return jsonify(data), 400


@app.route('/twitter/spain_trending_topic', methods=['GET'])
def get_trending_topic():
    result = ts.get_spain_trending_topics()
    return json.dumps(result, ensure_ascii=False, cls=DateTimeEncoder)


################
#  SUPERVISOR  #
################


@app.route('/twitter/twitter_ids', methods=['GET'])
def get_twitter_id_list():
    res = list(mgr.get_twitter_ids())
    result = {"twitter_ids":[]}
    for id in res:
        result['twitter_ids'].append(id["twitter_ids"])
    return json.dumps(result, ensure_ascii=False, cls=DateTimeEncoder)



@app.route('/twitter/update', methods=['GET'])
def update():
    if request.args and 'twitter_id' in request.args.keys():
        twitter_id = request.args["twitter_id"]
        logger.info(f'Updating {twitter_id} profile...')
        result = update_user(twitter_id)
        if result != -1:
            logger.info(f'Update {twitter_id} profile.')
            return twitter_id
        else:
            logger.error(f"Could not update {twitter_id} profile.")
            data = {'message':' Internal server error'}
            return jsonify(data), 500
    else:
        logger.error("No 'twitter_id' parameter found")
        data = {'message':'Bad Request'}
        return jsonify(data), 400


def update_user(twitter_id: str) -> int:
    """
    Args:
        twitter_id (str): id_str of user's profile

    Returns:
        int: 0 if everything ok.
    """
    has_records = mgr.has_records(twitter_id)
    current_info = ts.get_user_last_tweets_and_info(twitter_id,DAILY_TWEETS)
    
    profile_info = current_info["user_profile"]
    screen_name = profile_info["username"]

    followers = current_info["user_stats"]["followers"]
    favourites = current_info["user_stats"]["fav_count"]

    user_tweets = current_info["user_tweets"]
    last_tweets = user_tweets.copy()
    logger.info(f'Extracted last_tweets of {twitter_id}')

    best_tweets = sorted(user_tweets, key=lambda x: x['fav_count'])
    logger.info(f'Extracted best_tweets of {twitter_id}')

    today_post_count = len(user_tweets)
    if has_records:
        top_tweets = mgr.get_top_tweets(twitter_id)["tweets"]
        logger.info(f'Extracted old top_tweets of {twitter_id}')

    if today_post_count >= 10:
        last_tweets = user_tweets[:10]
        best_tweets = best_tweets[:10]
    
    best_tweets_and_responses = []
    for tweet in best_tweets:
        entry = {"tweet_id": tweet["tweet_id"],
                "text" : tweet["text"],
                "date" : tweet["date"]}
        entry["responses"] = ts.get_tweet_responses(screen_name, tweet["tweet_id"])
        best_tweets_and_responses.append(entry)
    logger.info(f'Extracted best_tweets responses of {twitter_id}')

    analyzed_best_tweets_and_responses = pystats.analyze_tweet_responses(best_tweets_and_responses)
    if has_records:
        new_top_tweets = pystats.compare_top_tweets(top_tweets, analyzed_best_tweets_and_responses)
    else:
        new_top_tweets = analyzed_best_tweets_and_responses
    logger.info(f'New top_tweets calculated')

    engagement = pystats.calculate_engagement(last_tweets, followers)
    logger.info(f'Calculated engagement')

    last_tweets_and_responses = []
    for tweet in last_tweets:
        entry = {"tweet_id": tweet["tweet_id"],
                "text" : tweet["text"],
                "date" : tweet["date"]}
        entry["responses"] = ts.get_tweet_responses(screen_name, tweet["tweet_id"])
        last_tweets_and_responses.append(entry)
    logger.info(f'Extracted last_tweets responses of {twitter_id}')

    analyzed_last_tweets_and_responses = pystats.analyze_tweet_responses(last_tweets_and_responses)
    pos = 0
    neu = 0
    neg = 0
    for tweet in analyzed_last_tweets_and_responses:
        pos += tweet['sentiment']['pos']
        neu += tweet['sentiment']['neu']
        neg += tweet['sentiment']['neg']
    current_sentiment = {
        'pos' : pos/len(analyzed_last_tweets_and_responses),
        'neu' : neu/len(analyzed_last_tweets_and_responses),
        'neg' : neg/len(analyzed_last_tweets_and_responses)
    }
    logger.info(f'Obtained sentiment')

    trending_topic = ts.get_spain_trending_topics()
    top_words = pystats.get_top_words(last_tweets)
    relevancy = pystats.get_relevancy(trending_topic, top_words)
    logger.info(f'Relevancy calculated')
    
    if has_records:
        p_count_records = mgr.get_post_count_records(twitter_id)
    else:
        p_count_records = dict()
        p_count_records['p_count_records'] = []
        count_entry = {'value':today_post_count}
        p_count_records['p_count_records'].append(count_entry)
    post_frequency = pystats.get_post_frequency(p_count_records['p_count_records'])
    logger.info(f'Post frequency calculated')

    score = pystats.calculate_score(profile_info, followers, post_frequency, relevancy, engagement, current_sentiment)
    logger.info(f'Score calculated')
    
    mgr.update_profile(has_records, twitter_id, followers,favourites, engagement, current_sentiment, score, today_post_count, relevancy, new_top_tweets)
    logger.info(f'Updated {twitter_id} records in DB')

    return 0




if __name__ == "__main__":
    app.run(debug=FLASK_CONFIG["DEBUG"],
            host=FLASK_CONFIG["HOST"],
            port=FLASK_CONFIG["PORT"])
