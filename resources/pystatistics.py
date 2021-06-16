import logging
import pandas as pd


from resources.utils import PYSTATS_LOGGER
from resources.utils import SCORE_WEIGHTS, SENT_FILTER
import resources.analyzer as analyzer

__LOGGER = logging.getLogger(PYSTATS_LOGGER)
__LOGGER.propagate = False

__LOGGER.info('Pystats started.')


#######################################
#               TWITTER               #
#######################################

def get_twitter_dashboard_stats(current_info: dict, top_tweets: list, last_stats: dict, sentiment_records: list) -> dict:
    """
    Args:
        current_info (dict): with keys [user_profile, user_stats, user_tweets]
        top_tweets (list): list of dicts with keys [tweet_id, text, date, sentiment, sent_score
        last_stats (dict): with keys [last_foll, last_fav, last_eng, last_score, last_rel, p_frequency]
        sentiment_records (list): list of dicts with keys [ date, pos, neu, neg]

    Returns:
        dict: keys -> [profile_info, stats, top_tweets, sentiment]
    """
    __LOGGER.info('Obtaining dashboard stats...')
    profile_info = current_info["user_profile"]
    last_tweets = current_info["user_tweets"]

    followers = current_info["user_stats"]["followers"]
    foll_diff = followers - last_stats["last_foll"]

    favourites = current_info["user_stats"]["fav_count"]
    favs_diff = favourites - last_stats["last_fav"]
    
    engagement = calculate_engagement(last_tweets, followers)
    eng_diff = engagement - last_stats["last_eng"]

    post_frequency = last_stats["p_frequency"]
    relevancy = last_stats["last_rel"]

    __LOGGER.info('Basic stats obtained')

    general_sentiment = __calculate_general_sentiment(sentiment_records)
    recent_sentiment = __get_recent_sentiment(sentiment_records)
    sentiment = {
        "general" : general_sentiment,
        "recent" : recent_sentiment,
        "records": sentiment_records
    }
    score_sentiment = {
        'pos': recent_sentiment[0]['percentage'],
        'neu': recent_sentiment[1]['percentage'],
        'neg': recent_sentiment[2]['percentage'],
    }

    __LOGGER.info('Sentiment obtained')

    score = calculate_score(profile_info, followers, post_frequency, relevancy, engagement, score_sentiment)
    score_diff = score - last_stats["last_score"]

    result = {
        "profile_info" : profile_info,
        "stats" : {
            "followers" : {
                "value":followers,
                "diff":foll_diff
            },
            "engagement" : {
                "value":engagement,
                "diff":eng_diff
            },
            "favourites" : {
                "value":favourites,
                "diff":favs_diff
            },
            "score" : {
                "value":score,
                "diff":score_diff
            }
        },
        "top_tweets" : top_tweets,
        "sentiment" : sentiment
    }
    __LOGGER.info('Dashboard info obtained. Done.')
    return result

def calculate_engagement(last_tweets:list, followers:int) -> float:
    """
    Args:
        last_tweets (list): List of dicts with keys { tweet_id, text, fav_count, rt_count, date }
        followers (int): user's number of followers

    Returns:
        float: engagement = number_of_interactions / followers
    """
    interactions = 0

    for t in last_tweets:
        interactions += t['fav_count'] + t['rt_count']
    
    if followers == 0:
        engagement =  0.01*interactions
    else:
        engagement = (interactions/followers) * 100
    return round(engagement,2)

def analyze_tweet_responses(tweets_and_responses: list) -> list:
    """
    Args:
        (tweets_and_responses) List of dicts with keys {tweet_id, text, date, responses}

    Return:
        (result): List of dicts with keys {tweet_id, text, date, sentiment, sent_score}
    """
    result = []
    for tweet in tweets_and_responses:
        sentiment = __analyze_sentiment(tweet['responses'])
        sent_score = __calculate_sentiment_score(sentiment)
        entry = {
            'tweet_id' : tweet['tweet_id'],
            'text' : tweet['text'],
            'date' : tweet['date'],
            'sentiment' : sentiment,
            'sent_score' : sent_score
        }
        result.append(entry)

    return result

def get_top_words(last_tweets: list) -> list:
    """
    Args:
        last_tweets (list): List of dicts with keys { tweet_id, text, fav_count, rt_count, date }

    Returns:
        list: List of words(str) ordered by word occurrence
    """
    data = pd.DataFrame()
    for tweet in last_tweets:
        data = data.append(tweet,ignore_index=True)
    data = data[['text']]
    data = data.rename(columns={'text':'sentence'})
    data = analyzer.tokenize(data)

    join_str = ""
    i = 1
    for s in data['tokens']:
        if i == len(data['tokens']):
            join_str += s
        else:
            join_str += s + " "
        i+=1
    
    f = __get_word_frequency(join_str)
    fs = dict(sorted(f.items(), key=lambda item: item[1], reverse=True))
    topwords = list(fs.keys())[:50]
    return topwords

def compare_top_tweets(top_tweets: list, analyzed_tweets: list) -> list:
    """
    Args:
        top_tweets (list): List of dicts with keys ['tweet_id', 'text', 'date', 'sentiment', 'sent_score']
        analyzed_tweets (list): List of dicts with keys ['tweet_id', 'text', 'date', 'sentiment', 'sent_score']

    Returns:
        list: List of dicts with keys ['tweet_id', 'text', 'date', 'sentiment', 'sent_score'] based on sent_score.
        The first fives elements will be returned
    """
    tweet_list = top_tweets + analyzed_tweets
    ordered_list = sorted(tweet_list, key=lambda k: float(k['sent_score']), reverse=True)
    return ordered_list[:5]

def get_post_frequency(p_count_records:list)->float:
    """
    Args:
        p_count_records (list): List of dicts with keys { date, value }

    Returns:
        float: Daily posting average 
    """
    post_frequency = 0
    if len(p_count_records) > 0:
        for day in p_count_records:
            post_frequency += day['value']
        post_frequency /= len(p_count_records)
    return post_frequency

def get_relevancy(trending_topic: list, top_words: list) -> float:
    """
    Args:
        trending_topic (list): List of words (Trending Topic)
        top_words (list): top words of the last tweets

    Returns:
        float: Percentage of TT words which appear in TW words
    """
    data = pd.DataFrame({'sentence':trending_topic})
    data = analyzer.tokenize(data)

    count = 0
    for token in data['tokens']:
        if len(token) > 0:
            if token in top_words:
                count +=1
    relevancy = count/len(data['tokens']) * 100
    return relevancy

def calculate_score(profile_info, followers, post_frequency, relevancy, engagement, sentiment):
    __LOGGER.info('Calculating score...')

    rrss_score = __get_rrss_score(profile_info) * SCORE_WEIGHTS['W_RRSS']
    __LOGGER.info('Calculated RRSS score')

    verified_score = __get_verified_score(profile_info) * SCORE_WEIGHTS['W_VERIFIED']
    __LOGGER.info('Calculated verified score')

    followers_score = __get_followers_score(followers) * SCORE_WEIGHTS['W_FOLLOWERS']
    __LOGGER.info('Calculated followers score')

    initial_score = ((rrss_score + verified_score + followers_score) / 3) *  SCORE_WEIGHTS['W_INITIAL_SCORE']
    __LOGGER.info('Calculated initial score')

    p_frequency_score = __get_post_frequency_score(post_frequency) * SCORE_WEIGHTS['W_POST_FREQUENCY']
    __LOGGER.info('Calculated post frequency score')

    relevancy_score = __get_relevancy_score(relevancy) * SCORE_WEIGHTS['W_RELEVANCE']
    __LOGGER.info('Calculated relevancy score')

    engagement_score = __get_engagement_score(engagement) * SCORE_WEIGHTS['W_ENGAGEMENT']
    __LOGGER.info('Calculated engagement score')

    score = (initial_score + p_frequency_score + relevancy_score + engagement_score) / 4

    final_score = __apply_sentiment_to_score(score, sentiment)
    __LOGGER.info('Final Score obtained. Sentiment Applied. Done.')
    return final_score

def __get_recent_sentiment(sentimental_records: list) -> list:
    """
    Args:
        sentimental_records (list): sent_records from mongoDB

    Returns:
        list: of dicts with keys [sentiment, percentage]. Ready to chart.
    """
    pos_avg = sentimental_records['sent_records'][-1]['pos']
    neu_avg = sentimental_records['sent_records'][-1]['neu']
    neg_avg = sentimental_records['sent_records'][-1]['neg']

    result = [{
      "sentiment": "Positiva",
      "percentage": round(pos_avg, 2)
    }, {
      "sentiment": "Neutra",
      "percentage": round(neu_avg, 2)
    }, {
      "sentiment": "Negativa",
      "percentage": round(neg_avg, 2)
    }]

    return result

def __calculate_general_sentiment(sentiment_records: list) -> list:
    """
    Args:
        sentimental_records (list): sent_records from mongoDB

    Returns:
        list: of dicts with keys [sentiment, percentage]. Ready to chart.
    """
    pos = 0
    neu = 0
    neg = 0

    for s in sentiment_records['sent_records']:
        pos += s['pos']
        neg += s['neg']
        neu += s['neu']
    
    datalen = len(sentiment_records['sent_records'])
    pos_avg =pos/datalen
    neg_avg =neg/datalen
    neu_avg =neu/datalen

    result = [{
      "sentiment": "Positiva",
      "percentage": round(pos_avg, 2)
    }, {
      "sentiment": "Neutra",
      "percentage": round(neu_avg, 2)
    }, {
      "sentiment": "Negativa",
      "percentage": round(neg_avg, 2)
    }]

    return result

def __analyze_sentiment(sentence_list: list) -> dict:
    """
    Args:
        sentence_list (list): List<String> of sentences

    Returns:
        dict: Sentiment Analysis result with keys {'pos', 'neu', 'neg'}
    """
    result = analyzer.get_sentiment(sentence_list)
    return result

def __calculate_sentiment_score(sentiment: dict) -> float:
    """
    Args:
        sentiment (dict): Sentiment Analysis result with keys {'pos', 'neu', 'neg'}

    Returns:
        float: Score calculated by: 2*pos + 0.5*neu - neg
    """
    pos = sentiment['pos']
    neu = sentiment['neu']
    neg = sentiment['neg']
    score = 2*pos + 0.5*neu - neg
    return score

def __get_word_frequency(string: str) -> list:
    """
    Args:
        string (str): string whose words we want to count

    Returns:
        list: List<dict> with words as keys and occurrences as values
    """
    string=string.lower()
    string=string.split(" ")
    word_frequency={}
    for i in string:
        if i in word_frequency:
            word_frequency[i]+=1
        else:
            word_frequency[i]=1
    return(word_frequency)

def __get_rrss_score(profile_info):
    urls = profile_info['urls']

    if len(urls) == 0:
        return 0

    for url in urls:
        if 'youtube' in url or 'twitch' in url:
            return 100
        elif 'tumblr' in url or 'facebook' in url or 'instagram' in url:
            return 50
    
    return 20

def __get_verified_score(profile_info):
    verified = profile_info['verified']
    if verified:
        return 100
    else:
        return 0

def __get_followers_score(followers: int):
    if   followers <= 5000:                            # User
        return 0
    elif followers > 5000    and followers <= 25000:   # Micro-influencer
        return 15
    elif followers > 25000   and followers <=100000:   # Small Influencer
        return 30
    elif followers > 100000  and followers <= 1000000: # Big Influencer
        return 50
    elif followers > 1000000 and followers <= 7000000: # Macro Influencer
        return 75
    elif followers > 7000000:                          # Celebrity
        return 100

def __get_post_frequency_score(post_frequency: float) -> int:
    
    if (5 <= post_frequency <= 15): # Optimal
        return 100
    elif 0 <= post_frequency < 5: # Frequency too low
        return 50
    elif 15 < post_frequency: # Frequency too high
        return 25

def __get_relevancy_score(relevancy: float) -> int:
    if 0 <= relevancy <= 5:
        return 10
    elif 5 < relevancy <= 25:
        return 25
    elif 25 < relevancy <= 75:
        return 50
    elif 75 < relevancy:
        return 100 

def __get_engagement_score(engagement: float) -> int:
    if 0 <= engagement <= 5:
        return 25
    elif 5 < engagement <= 25:
        return 50
    elif 25 < engagement <= 75:
        return 75
    elif 75 < engagement:
        return 100 

def __apply_sentiment_to_score(score: float, sentiment: dict) -> float:
    """This method checks if there is any feeling that prevails over the other two (at least 20%)

                - Positive: 15 % is added to the final score

                - Neutral: Nothing is done

                - Negative: 15 % is subtracted from the final score

    Args:
        score (float): score calculated previously (over 100)
        sentiment (dict): keys -> { pos, neu, neg}

    Returns:
        float: score after applying sentiment filter
    """
    highest_val = 0
    highest_key = ""
    for key in sentiment.keys():
        if sentiment[key] > highest_val:
            highest_val = sentiment[key]
            highest_key = key
    
    sent_score = score + score*SENT_FILTER[highest_key]
    if sent_score < 0:
        sent_score = 0
    elif sent_score > 100:
        sent_score = 100
    return sent_score