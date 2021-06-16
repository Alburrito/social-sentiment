import logging
import pandas as pd
import re
import pickle

# Preprocessing
import spacy
from spacy.lang.es.stop_words import STOP_WORDS
nlp = spacy.load('es_core_news_md')
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
__STOPWORDS = stopwords.words('spanish')+list(STOP_WORDS)

# Feature extraction / Classifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

from resources.utils import ANALYZER_LOGGER, SENT_CODES, MODELS_PATH

__LOGGER = logging.getLogger(ANALYZER_LOGGER)
__LOGGER.info('Analyzer started.')


with open(MODELS_PATH["VECTORIZER"], 'rb') as file:
    __VECTORIZER = pickle.load(file)
__LOGGER.info('Loaded vectorizer')

with open(MODELS_PATH["CLASSIFIER"], 'rb') as file:
    __CLASSIFIER = pickle.load(file)
__LOGGER.info('Loaded classifier')


def get_sentiment(sentence_list: list) -> dict:
    """
    Args:
        sentence_list (list): List<String> of sentences

    Returns:
        dict: Sentiment Analysis result with keys {'pos', 'neu', 'neg'}
    """
    if len(sentence_list) == 0:
        __LOGGER.info(f'No responses to analyze => Neutral sentiment.')
        result = {
            'pos' : round(0, 2),
            'neu' : round(100, 2),
            'neg' : round(0, 2)
        }
        return result
        
    __LOGGER.info(f'Calculating sentiment of {len(sentence_list)} sentences')
    data = pd.DataFrame({'sentence':sentence_list})
    __LOGGER.info('Tokenizing sentences...')
    data = tokenize(data)
    tokens = data['tokens']
    __LOGGER.info('Extracting features...')
    features = __VECTORIZER.transform(tokens)
    __LOGGER.info('Classifying...')
    data["prediction"] = __CLASSIFIER.predict(features)
    n_values = data['prediction'].count()
    value_counts = dict(data['prediction'].value_counts())
    n_pos = 0
    n_neu = 0
    n_neg = 0
    if 1 in list(value_counts.keys()):
        n_pos = value_counts[1]
    if 0 in list(value_counts.keys()):
        n_neu = value_counts[0]
    if -1 in list(value_counts.keys()):
        n_neg = value_counts[-1]

    result = {
        'pos' : round(n_pos/n_values, 2),
        'neu' : round(n_neu/n_values, 2),
        'neg' : round(n_neg/n_values, 2)
    }
    __LOGGER.info('Classification completed.')
    return result

    
def tokenize(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Args:
        dataframe (pd.DataFrame): Must include 'sentence' column

    Returns:
        pd.DataFrame: Same Dataframe with 'tokens' column added
    """
    data = dataframe.copy()
    data['tokens'] = data['sentence'].str.lower()
    data['tokens'] = data['tokens'].apply(__only_words)
    data['tokens'] = data['tokens'].apply(__remove_stop_words)
    data['tokens'] = data['tokens'].apply(__lematize)
    data['tokens'] = data['tokens'].apply(__remove_accents)
    return data

def __only_words(sentence: str) -> str:
    """
    Args:
        sentence (str): sentence to clean

    Returns:
        str: sentence without url, html items or spaces
    """
    url_reg = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    html_reg = re.compile(r'<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    spaces_reg = re.compile(r'[ ]{2,}')
    
    result = url_reg.sub('', sentence)
    result = html_reg.sub('', result)
    result = spaces_reg.sub('', result)
    result = re.findall(r'\w+', result)
    result = [''.join(x for x in i if x.isalpha()) for i in result]
    result = ' '.join(result)
    
    return result

def __remove_stop_words(sentence: str) -> str:
    """
    Args:
        sentence (str): sentence to clean

    Returns:
        str: same sentence without stopwords
    """
    result = ""
    if sentence != None:
        sentence = sentence.split(" ")
        result = list(
        filter(lambda l: (l not in __STOPWORDS and len(l) > 2), sentence))
        result = ' '.join(result)
    return result

def __lematize(sentence: str) -> str:
    """
    Args:
        sentence (str): sentence to lematize

    Returns:
        str: sentences with words replaced by their lemma
    """
    doc = nlp(sentence)
    result = ""
    i = 1
    for token in doc:
        if i == len(doc):
            result += token.lemma_
        else:
            result += token.lemma_ + " "
        i+=1
    return result

def __remove_accents(sentence: str) -> str:
    """
    Args:
        sentence (str): sentence to clean

    Returns:
        str: same sentences without spanish accents
    """
    replacements = {
        "á" : "a",
        "é" : "e",
        "í" : "i",
        "ó" : "o",
        "ú" : "u",
    }
    for i,j in replacements.items():
        sentence = sentence.replace (i,j)
    return sentence



