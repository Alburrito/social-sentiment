from datetime import datetime
from dateutil.relativedelta import relativedelta
from resources.credentials import *
from resources.constants import *
from pymongo import MongoClient
import os
import tweepy

class Manager():
    def __init__(self):
        self.CLIENT = MongoClient(MONGO_URI)
        self.DATABASE = self.CLIENT[DB_NAME]
        self.C_UNLABELED = self.DATABASE[UNLABELED_COL] 
        self.C_LABELED = self.DATABASE[LABELED_COL] 
        self.C_INVALID = self.DATABASE[INVALID_COL]
        self.C_DATASET = self.DATABASE[DATASET_COL]

        if not os.path.isdir(LOG_DIR):
            print("WARNING: log directory not found. Creating directory...")
            try:
                os.mkdir(LOG_DIR)
            except OSERROR:
                print("ERROR: could not create directory " + LOG_DIR + "\nAborting...\n")
                exit(0)
            else:
                print("SUCCESS: log directory created in: " + LOG_DIR)
        try:
            logging.basicConfig(level = MM_LOG_LEVEL, filename=LOG_DB_FILE, filemode='a', format='%(asctime)s - %(filename)s -  %(levelname)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
            logging.info('Log Iniciado')
        except FileNotFoundError:
            logging.error('ERROR: No se encontró o no se pudo crear la carpeta log/')
            exit(0)

        self.api = self.connect_twitter_OAuth()

    def connect_twitter_OAuth(self):
        auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)
        return api

    def automanage(self):
        self.autoaccept_labeled()
        self.autodelete_invalid()

    def autoaccept_labeled(self):
        try:
            today = datetime.now()
            week_ago = today + relativedelta(days=-7)
            sentences = self.C_LABELED.find({
                "timestamp" : {
                    "$lt" : week_ago
                }
            })
            sentences = list(sentences)
            if len(sentences) > 0:
                self.C_DATASET.insert_many(sentences)
                self.C_LABELED.delete_many({
                    "timestamp" : {
                        "$lt" : week_ago
                    }
                })
                logging.info("Se aceptaron automáticamente {} documentos etiquetados".format(len(list(sentences))))
            else:
                logging.info("No se encontraron documentos etiquetados con antigüedad mayor a una semana")
        except:
            logging.info("No se encontraron documentos etiquetados con antigüedad mayor a una semana")

    def autodelete_invalid(self):
        try:
            today = datetime.now()
            week_ago = today + relativedelta(days=-7)
            sentences = self.C_INVALID.find({
                "timestamp" : {
                    "$lt" : week_ago
                }
            })
            sentences = list(sentences)
            if len(sentences) > 0:
                self.C_INVALID.delete_many({
                    "timestamp" : {
                        "$lt" : week_ago
                    }
                })
                logging.info("Se eliminaron automáticamente {} documentos invalidos".format(len(list(sentences))))
            else:
                logging.info('No se encontraron documentos invalidos con antigüedad mayor a una semana')
        except:
           logging.info('No se encontraron documentos invalidos con antigüedad mayor a una semana')

    def fill_unlabeled(self, elements, keyword):
        cursor = self.api.search(keyword, lang='es', locale='es', count = elements, tweet_mode = 'extended')
        tweets = []
        for t in cursor:
            try:
                tweets.append({'sentence':t.retweeted_status.full_text})
            except AttributeError:
                tweets.append({'sentence':t.full_text})
        self.C_UNLABELED.insert_many(tweets)
        logging.info("Se han introducido en Unlabeled: {} elementos con tema {}".format(len(tweets), keyword))
        return 1

if __name__ == '__main__':
    m = Manager()
    m.automanage()