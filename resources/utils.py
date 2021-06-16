import logging
from logging.config import dictConfig
import os
import datetime
from dotenv import load_dotenv
import json

load_dotenv()

#######################################
#               GENERAL               #
#######################################

class DateTimeEncoder(json.JSONEncoder):
    def default(self, z):
        if isinstance(z, datetime.datetime):
            return (str(z))
        else:
            return super().default(z)


#######################################
#                 API                 #
#######################################

FLASK_CONFIG = {
    "DEBUG": bool(os.getenv('API_DEBUG')),
    "HOST": str(os.getenv('API_HOST')),
    "PORT": str(os.getenv('API_PORT')),
}


#######################################
#             SUPERVISOR              #
#######################################

SUPERVISOR_CONFIG = {
    "API_URI": f'http://{FLASK_CONFIG["HOST"]}:{FLASK_CONFIG["PORT"]}'
}


#######################################
#               MONGODB               #
#######################################

MONGO_CONFIG = {
    "DB_HOST": str(os.getenv('DB_HOST')),
    "DB_PORT": int(os.getenv('DB_PORT')),
    "DB_NAME": os.getenv('DB_NAME'),
    "COL_USERS": os.getenv('COL_USERS'),
    "COL_RECORDS": os.getenv('COL_RECORDS'),
    "COL_TWEETS": os.getenv('COL_TWEETS')
}

#######################################
#               SCRAPPER              #
#######################################

SCRAPPER_CONFIG = {
    "TWITTER_API_KEY": os.getenv('TWITTER_API_KEY'),
    "TWITTER_API_SECRET_KEY": os.getenv('TWITTER_SECRET_API_KEY'),
    "TWITTER_BEARER_TOKEN": os.getenv('TWITTER_BEARER_TOKEN'),
    "TWITTER_ACCESS_TOKEN": os.getenv('TWITTER_ACCESS_TOKEN'),
    "TWITTER_ACCESS_TOKEN_SECRET": os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
    "SPAIN_WOEID": os.getenv('SPAIN_WOEID')
}


#######################################
#               PYSTATS               #
#######################################

SCORE_WEIGHTS = {
    "W_RRSS" : 0.20,
    "W_VERIFIED" : 0.35,
    "W_FOLLOWERS" : 0.45,
    "W_ENGAGEMENT" : 0.30,
    "W_POST_FREQUENCY" : 0.15,
    "W_RELEVANCE" : 0.30,
    "W_INITIAL_SCORE" : 0.15,
}

SENT_FILTER = {
    "pos" : 0.15,
    "neu" : 0.05,
    "neg" : -0.10 
}

#######################################
#               ANALYZER              #
#######################################

SENT_CODES = {
    1 : "Positiva",
    0 : "Neutra",
    -1 : "Negativa"
}

MODELS_PATH = {
    "VECTORIZER" : "resources/models/tfidf.pickle",
    "CLASSIFIER" : "resources/models/rfc.pickle"
}

#######################################
#               LOGGING               #
#######################################

# General
LOG_DIR = 'logs'
LOG_LEVEL = logging.INFO
LOG_FILE = os.path.join(LOG_DIR, 'api.log')

# Supervisor
SUPERVISOR_HANDLER = 'supervisor_hadler'
SUPERVISOR_LOGGER = 'supervisor_log'
SUPERVISOR_LOG_DIR = LOG_DIR
SUPERVISOR_LOG_LVL = logging.INFO
SUPERVISOR_LOG_FILE = os.path.join(SUPERVISOR_LOG_DIR, 'supervisor.log')


# Scrapper
SCRAPPER_HANDLER = 'scrapper_hadler'
SCRAPPER_LOGGER = 'scrapper_log'
SCRAPPER_LOG_DIR = LOG_DIR
SCRAPPER_LOG_LVL = logging.INFO
SCRAPPER_LOG_FILE = os.path.join(SCRAPPER_LOG_DIR, 'scrapper.log')

# Mongo
MONGO_HANDLER = 'mongo_handler'
MONGO_LOGGER = 'mongo_log'
MONGO_LOG_DIR = LOG_DIR
MONGO_LOG_LVL = logging.INFO
MONGO_LOG_FILE = os.path.join(MONGO_LOG_DIR, 'mongo.log')

# Pystatistics
PYSTATS_HANDLER = 'pystats_handler'
PYSTATS_LOGGER = 'pystats_log'
PYSTATS_LOG_DIR = LOG_DIR
PYSTATS_LOG_LVL = logging.INFO
PYSTATS_LOG_FILE = os.path.join(PYSTATS_LOG_DIR, 'pystats.log')

# Analyzer
ANALYZER_HANDLER = 'analyzer_hadler'
ANALYZER_LOGGER = 'analyzer_log'
ANALYZER_LOG_DIR = LOG_DIR
ANALYZER_LOG_LVL = logging.INFO
ANALYZER_LOG_FILE = os.path.join(ANALYZER_LOG_DIR, 'analyzer.log')


# Check if log dir/file exists
if not os.path.isdir(LOG_DIR):
    print(f"WARNING: log directory not found. Creating directory...")
    try:
        os.mkdir(LOG_DIR)
    except:
        print("ERROR: could not create directory " + LOG_DIR + "\nAborting...\n")
        exit(0)
    else:
        print("SUCCESS: log directory created in: " + LOG_DIR)

if not os.path.isfile(LOG_FILE):
    os.mknod(LOG_FILE)

# Log config
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s',
    }},
    'handlers': {
        'default': {
            'class': 'logging.StreamHandler',
            'level': logging.INFO,
            'stream': 'ext://sys.stdout',
            'formatter': 'default',
        },
        'wsgi': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILE,
            'level': LOG_LEVEL,
            'formatter': 'default',
            'maxBytes': 65536,
            'backupCount': 5
        },
        MONGO_HANDLER: {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': MONGO_LOG_FILE,
            'level': MONGO_LOG_LVL,
            'formatter': 'default',
            'maxBytes': 65536,
            'backupCount': 5
        },
        SCRAPPER_HANDLER: {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': SCRAPPER_LOG_FILE,
            'level': SCRAPPER_LOG_LVL,
            'formatter': 'default',
            'maxBytes': 65536,
            'backupCount': 5
        },
        PYSTATS_HANDLER: {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': PYSTATS_LOG_FILE,
            'level': PYSTATS_LOG_LVL,
            'formatter': 'default',
            'maxBytes': 65536,
            'backupCount': 5
        },
        SUPERVISOR_HANDLER: {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': SUPERVISOR_LOG_FILE,
            'level': SUPERVISOR_LOG_LVL,
            'formatter': 'default',
            'maxBytes': 65536,
            'backupCount': 5
        },
        ANALYZER_HANDLER: {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': ANALYZER_LOG_FILE,
            'level': ANALYZER_LOG_LVL,
            'formatter': 'default',
            'maxBytes': 65536,
            'backupCount': 5
        }
    },
    'loggers': {
        "": {
            'level': LOG_LEVEL,
            'handlers': ['default', 'wsgi']
        },
        MONGO_LOGGER: {
            'level': MONGO_LOG_LVL,
            'handler': ['default', MONGO_HANDLER]
        },
        SCRAPPER_LOGGER: {
            'level': SCRAPPER_LOG_LVL,
            'handlers': ['default', SCRAPPER_HANDLER]
        },
        PYSTATS_LOGGER: {
            'level': PYSTATS_LOG_LVL,
            'handlers': ['default', PYSTATS_HANDLER]
        },
        SUPERVISOR_LOGGER: {
            'level': SUPERVISOR_LOG_LVL,
            'handlers': ['default', SUPERVISOR_HANDLER]
        },
        ANALYZER_LOGGER: {
            'level': ANALYZER_LOG_LVL,
            'handlers': ['default', ANALYZER_HANDLER]
        }
    }
})