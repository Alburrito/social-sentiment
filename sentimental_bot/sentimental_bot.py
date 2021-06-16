from resources.credentials import *
from resources.constants import *
from mongo_manager import Manager
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, ParseMode
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
from pymongo import MongoClient
from random import choice
from threading import *
import os
from datetime import datetime
import re
import logging

CHOSE_MOD, VOTE, ADMIN, INVALID, LABELED, DB_MANAGEMENT = range(6)
CHATS = dict()
DB_SEM = Semaphore(1)

CLIENT = MongoClient(MONGO_URI)
DATABASE = CLIENT[DB_NAME]
C_UNLABELED = DATABASE[UNLABELED_COL] 
C_LABELED = DATABASE[LABELED_COL] 
C_INVALID = DATABASE[INVALID_COL]
C_DATASET = DATABASE[DATASET_COL]


def bot_start(update,context) -> int:
    reply_keyboard = [['VOTAR'],['ADMIN']]
    update.message.reply_text(
        text = START_MESSAGE,
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return CHOSE_MOD

def vote_examples(update,context) -> int:
    reply_keyboard = [['VOTAR'],['ADMIN']]
    update.message.reply_text(
        text = HELP_MESSAGE,
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        parse_mode = ParseMode.HTML
    )
    return CHOSE_MOD



def chose_mod(update, context) -> int:
    reply_keyboard = [['VOTAR'],['ADMIN']]
    update.message.reply_text(
        text = CHOSE_MESSAGE,
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return CHOSE_MOD

def vote_sentence(update, context) -> int:
    reply_keyboard = [['Positiva', 'Neutra', 'Negativa'], ['Invalida','Atras']]

    user_text = update.message.text
    user_id = update.effective_chat.id
    user_name = update.message.from_user.first_name
    
    try:
        if user_id in CHATS.keys():
            query = {'sentence' : { '$ne' : CHATS[user_id]}}
            c = C_UNLABELED.aggregate([
                {'$match': query},
                {'$sample': {'size':1}}
            ])
            sentence = list(c)[0]
        else:
            c = C_UNLABELED.find_one({})
            sentence = dict(c)
    except:
        if user_id in CHATS.keys():
            DB_SEM.acquire()
            if user_text in ['Positiva', 'Neutra', 'Negativa']:
                C_LABELED.insert_one({'sentence':CHATS[user_id], 'vote':user_text, 'timestamp': datetime.now()})
            elif user_text == 'Invalida':
                C_INVALID.insert_one({'sentence':CHATS[user_id]})

            if user_text != "Atras" and user_text != "VOTAR":
                C_UNLABELED.delete_one({"sentence":CHATS[user_id]})
                del CHATS[user_id] 
            else:
                update.message.reply_text(
                    text = "Ejemplos: -> /ejemplos\n-----------------------------------\n{}".format(CHATS[user_id]), 
                    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False),
                )
                DB_SEM.release()
                if user_text == "Atras":
                    return CHOSE_MOD
                elif user_text == "VOTAR":
                    return VOTE
            DB_SEM.release()

        update.message.reply_text(
            NO_SENTENCES, 
            reply_markup=ReplyKeyboardRemove()
        )
        return VOTE

    to_show_sentence = sentence['sentence']

    if user_text == 'VOTAR': 
        if user_id in CHATS.keys():
            to_show_sentence = CHATS[user_id]
            logging.info("ENTRA |{}| con frase |{}|".format(user_name, to_show_sentence))
        else:
            CHATS[user_id] = to_show_sentence
            logging.info("ENTRA |{}| sin frase".format(user_name))
    elif user_text in ['Positiva', 'Negativa','Neutra']: 
        to_vote_sentence = CHATS[user_id]
        DB_SEM.acquire()
        C_LABELED.insert_one({'sentence':to_vote_sentence, 'vote':user_text, 'timestamp' : datetime.now()})
        C_UNLABELED.delete_one({"sentence":to_vote_sentence}) 
        DB_SEM.release()
        CHATS[user_id] = to_show_sentence
        logging.info("USUARIO |{}| voto como |{}| la frase |{}|".format(user_name,user_text,to_vote_sentence))
    elif user_text == 'Invalida':
        to_vote_sentence = CHATS[user_id]
        DB_SEM.acquire()
        C_INVALID.insert_one({'sentence':to_vote_sentence, 'vote':user_text, 'timestamp' : datetime.now()})
        C_UNLABELED.delete_one({"sentence":to_vote_sentence}) 
        DB_SEM.release()
        CHATS[user_id] = to_show_sentence
        logging.info("USUARIO |{}| voto como INVALIDA la frase |{}|".format(user_name,to_vote_sentence))
    elif user_text == "Atras":
        return CHOSE_MOD

    update.message.reply_text(
        text = "Ejemplos: -> /ejemplos\n-----------------------------------\n{}".format(to_show_sentence),
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False),
    )

    return VOTE

def admin_options(update, context) -> int:
    reply_keyboard = [['Invalidas','Etiquetadas'],['Gestionar DB', 'Atras']]
    user_id = update.effective_chat.id

    if str(user_id) != ADMIN_ID:
        reply_keyboard = [['VOTAR'],['ADMIN']]
        update.message.reply_text(
            text = NO_PERMISSION,
            reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
        return CHOSE_MOD

    update.message.reply_text(
        text = CHOSE_MESSAGE,
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return ADMIN

def admin_manage_invalid(update,context) -> int:
    reply_keyboard = [['Positiva','Neutra','Negativa'],['Borrar','Atras']]

    user_text = update.message.text
    user_id = update.effective_chat.id
    user_name = update.message.from_user.first_name

    try:
        if ADMIN_INVALID in CHATS.keys():
            query = {"sentence" : { "$ne" : CHATS[ADMIN_INVALID]}}
            sentence = dict(C_INVALID.find_one(query))
        else:
            sentence = dict(C_INVALID.find_one())           
    except:
        if ADMIN_INVALID in CHATS.keys():
            DB_SEM.acquire()
            if user_text in ['Positiva', 'Neutra', 'Negativa']:
                C_DATASET.insert_one({'sentence':CHATS[ADMIN_INVALID], 'vote':user_text})

            if user_text != "Atras" and user_text != "Invalidas":
                C_INVALID.delete_one({"sentence":CHATS[ADMIN_INVALID]}) 
                del CHATS[ADMIN_INVALID]
            else:
                update.message.reply_text(
                    text = CHATS[ADMIN_INVALID],
                    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False),
                )
                DB_SEM.release()
                return INVALID
            DB_SEM.release()

        update.message.reply_text(
            text = NO_INVALID_SENTENCES, 
            reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False),
        )

        return INVALID

    to_show_sentence = sentence['sentence']

    if user_text == 'Invalidas':
        if ADMIN_INVALID in CHATS.keys():
            to_show_sentence = CHATS[ADMIN_INVALID]
            logging.info("ENTRA |{}| con frase |{}|".format(user_name, to_show_sentence))
        else:
            CHATS[ADMIN_INVALID] = to_show_sentence
    elif user_text in ['Positiva', 'Negativa','Neutra']: 
        to_vote_sentence = CHATS[ADMIN_INVALID]
        DB_SEM.acquire()
        C_DATASET.insert_one({'sentence':to_vote_sentence, 'vote':user_text})
        C_INVALID.delete_one({"sentence":to_vote_sentence}) 
        DB_SEM.release()
        CHATS[ADMIN_INVALID] = to_show_sentence
        logging.info("ADMIN |{}| vota como |{}| la frase invalida |{}|".format(user_name,user_text,to_vote_sentence))
    elif user_text == 'Borrar':
        to_vote_sentence = CHATS[ADMIN_INVALID]
        DB_SEM.acquire()
        C_INVALID.delete_one({"sentence":to_vote_sentence}) 
        DB_SEM.release()
        CHATS[ADMIN_INVALID] = to_show_sentence
        logging.info("ADMIN |{}| borra la frase |{}|".format(user_name,to_vote_sentence))
    elif user_text == "Atras":
        reply_keyboard = [['Invalidas','Etiquetadas'],['Rellenar', 'Atras']]
        update.message.reply_text(
            text = ADMIN_OPTIONS_MESSAGE,
            reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
        return ADMIN

    update.message.reply_text(
        text = to_show_sentence,
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False),
    )
    return INVALID

def admin_manage_labeled(update, context) -> int:
    reply_keyboard = [['Aceptar','Desetiquetar','Borrar'],['Atras']]

    user_text = update.message.text
    user_id = update.effective_chat.id
    user_name = update.message.from_user.first_name

    try:
        if ADMIN_LABELED in CHATS.keys():
            query = {"sentence" : { "$ne" : CHATS[ADMIN_LABELED]}}
            sentence = dict(C_LABELED.find_one(query))
        else:
            sentence = dict(C_LABELED.find_one())
    except:
        if ADMIN_LABELED in CHATS.keys():
            DB_SEM.acquire()
            if user_text == "Aceptar":
                labeled = C_LABELED.find_one({'sentence':CHATS[ADMIN_LABELED]})
                vote = labeled['vote']
                C_DATASET.insert_one({'sentence':CHATS[ADMIN_LABELED], 'vote':vote})
            elif user_text == "Desetiquetar":
                C_UNLABELED.insert_one({'sentence':CHATS[ADMIN_LABELED]})
            if user_text != "Atras" and user_text != "Etiquetadas":
                C_LABELED.delete_one({"sentence":CHATS[ADMIN_LABELED]}) 
                del CHATS[ADMIN_LABELED]
            else:
                labeled = C_LABELED.find_one({'sentence':CHATS[ADMIN_LABELED]})
                vote = labeled['vote']
                update.message.reply_text(
                    text = "Voto: {}\n-----------------------\n{}".format(vote,CHATS[ADMIN_LABELED]),
                    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False),
                )
                DB_SEM.release()
                return LABELED
            DB_SEM.release()

        update.message.reply_text(
            NO_LABELED_SENTENCES, 
            reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False),
        )
        
        return LABELED

    to_show_sentence = sentence['sentence']

    if user_text == 'Etiquetadas': 
        CHATS[ADMIN_LABELED] = to_show_sentence
    elif user_text == 'Aceptar': 
        to_vote_sentence = CHATS[ADMIN_LABELED]
        DB_SEM.acquire()
        labeled = C_LABELED.find_one({'sentence':to_vote_sentence})
        vote = labeled['vote']
        C_DATASET.insert_one({'sentence':to_vote_sentence, 'vote':vote})
        C_LABELED.delete_one({"sentence":to_vote_sentence}) 
        DB_SEM.release()
        CHATS[ADMIN_LABELED] = to_show_sentence
        logging.info("ADMIN |{}| ACEPTA la frase etiquetada |{}|".format(user_name,to_vote_sentence))
    elif user_text == 'Desetiquetar':
        to_vote_sentence = CHATS[ADMIN_LABELED]
        DB_SEM.acquire()
        C_UNLABELED.insert_one({'sentence':to_vote_sentence})
        C_LABELED.delete_one({"sentence":to_vote_sentence}) 
        DB_SEM.release()
        CHATS[ADMIN_LABELED] = to_show_sentence
        logging.info("ADMIN |{}| DESETIQUETA la frase etiquetada |{}|".format(user_name,to_vote_sentence))
    elif user_text == "Borrar":
        to_vote_sentence = CHATS[ADMIN_LABELED]
        CHATS[ADMIN_LABELED] = to_show_sentence
        logging.info("ADMIN |{}| BORRA la frase etiquetada |{}|".format(user_name,to_vote_sentence))
    elif user_text == "Atras":
        reply_keyboard = [['Invalidas','Etiquetadas'],['Rellenar', 'Atras']]
        update.message.reply_text(
            text = ADMIN_OPTIONS_MESSAGE,
            reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
        return ADMIN

    update.message.reply_text(
        text = "Voto: {}\n-----------------------\n{}".format(sentence['vote'],to_show_sentence),
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False),
    )
    return LABELED

def admin_manage_database(update, context) -> int:
    reply_keyboard = [['Rellenar','Informacion'],['Atras']]

    user_text = update.message.text
    user_id = update.effective_chat.id
    user_name = update.message.from_user.first_name

    if user_text == 'Rellenar':
        fill_unlabeled(update,context)
        return DB_MANAGEMENT
    elif user_text == 'Informacion':
        send_db_information(update,context)
    elif user_text == "Atras":
        reply_keyboard = [['Invalidas','Etiquetadas'],['Rellenar', 'Atras']]
        update.message.reply_text(
            text = ADMIN_OPTIONS_MESSAGE,
            reply_markup=ReplyKeyboardRemove()
        )
        return ADMIN

    update.message.reply_text(
        text = CHOSE_MESSAGE,
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False),
    )
    return DB_MANAGEMENT

def fill_unlabeled(update,context):
    reply_keyboard = [['Rellenar','Informacion'],['Atras']]
    user_text = update.message.text
    user_id = update.effective_chat.id
    user_name = update.message.from_user.first_name

    if user_text == 'Rellenar':
        update.message.reply_text(
            text = FILL_INSTRUCTIONS,
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        r = re.compile('[\d]+@[\w]+')
        if r.match(user_text):
            elements = user_text.split('@')[0]
            keyword = user_text.split('@')[1]
            manager = Manager()
            res = manager.fill_unlabeled(elements, keyword)
            context.bot.send_message(chat_id = user_id, text = "Se introdujeron {} elementos nuevos".format(res))
        else:
            context.bot.send_message(chat_id = user_id, text = FILL_COMMAND_ERROR)
        
        update.message.reply_text(
            text = CHOSE_MESSAGE,
            reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False),
        )

    return DB_MANAGEMENT

def send_db_information(update,context):
    user_text = update.message.text
    user_id = update.effective_chat.id
    user_name = update.message.from_user.first_name

    n_unlabeled = C_UNLABELED.count_documents({})
    n_invalid = C_INVALID.count_documents({})
    n_labeled = C_LABELED.count_documents({})
    n_dataset = C_DATASET.count_documents({})

    if n_labeled > 0:
        n_pos = C_LABELED.count_documents({'vote' : 'Positiva'})
        n_neu = C_LABELED.count_documents({'vote' : 'Neutra'})
        n_neg = C_LABELED.count_documents({'vote' : 'Negativa'})
        l_positive = round((100* n_pos/n_labeled),2)
        l_neutral = round((100* n_neu/n_labeled),2)
        l_negative = round((100* n_neg/n_labeled),2)
    else:
        l_positive, l_neutral, l_negative = 0, 0, 0

    if n_dataset > 0:
        n_pos = C_DATASET.count_documents({'vote' : 'Positiva'})
        n_neu = C_DATASET.count_documents({'vote' : 'Neutra'})
        n_neg = C_DATASET.count_documents({'vote' : 'Negativa'})
        d_positive = round((100* n_pos/n_dataset),2)
        d_neutral = round((100* n_neu/n_dataset),2)
        d_negative = round((100* n_neg/n_dataset),2)
    else:
        d_positive, d_neutral, d_negative = 0, 0, 0

    info = INFO_DB_MESSAGE.format(n_unlabeled, n_invalid, n_labeled, l_positive, l_neutral, l_negative, n_dataset, d_positive, d_neutral, d_negative)

    context.bot.send_message(chat_id=user_id, text = info)

    return DB_MANAGEMENT

def bot_unknown(update, context):
    user_text = update.message.text
    user_id = update.effective_chat.id
    user_name = update.message.from_user.first_name

    context.bot.send_message(chat_id=user_id, text = UNKNOWN_MESSAGE)

def init_handlers(dispatcher):
    """
    Inicia las manejadoras de las funcioens del bot
    """

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', bot_start)],
        states={
            CHOSE_MOD: [MessageHandler(Filters.regex('^(VOTAR)$'), vote_sentence), # -> VOTE
                    MessageHandler(Filters.regex('^(ADMIN)$'), admin_options), # -> ADMIN
                    MessageHandler(Filters.regex('^(Atras)'),chose_mod), # -> CHOSE_MOD
                    CommandHandler('ejemplos', vote_examples)], # -> CHOSE_MOD

            VOTE: [MessageHandler(Filters.regex('^(VOTAR|Positiva|Neutra|Negativa|Invalida)$'), vote_sentence), # -> VOTE
                    MessageHandler(Filters.regex('^(Atras)$'), chose_mod), # -> CHOSE_MOD
                    CommandHandler('ejemplos', vote_examples)], # -> CHOSE_MOD
            
            ADMIN: [MessageHandler(Filters.regex('^(Invalidas)$'), admin_manage_invalid), # -> INVALID
                    MessageHandler(Filters.regex('^(Etiquetadas)$'), admin_manage_labeled), # -> LABELED
                    MessageHandler(Filters.regex('^(Gestionar DB)$'), admin_manage_database), # -> DB_MANAGEMENT
                    MessageHandler(Filters.regex('^(Atras)$'), chose_mod)], # -> CHOSE_MOD
            
            INVALID: [MessageHandler(Filters.regex('^(Invalidas|Positiva|Neutra|Negativa|Invalida|Borrar)$'), admin_manage_invalid), # -> INVALID
                    MessageHandler(Filters.regex('^(Atras)$'), admin_options)], # -> ADMIN
            
            LABELED: [MessageHandler(Filters.regex('^(Aceptar|Desetiquetar|Borrar)$'), admin_manage_labeled), # -> LABELED
                    MessageHandler(Filters.regex('^(Atras)$'), admin_options)], # -> ADMIN

            DB_MANAGEMENT: [MessageHandler(Filters.regex('^(Rellenar|Informacion)$'), admin_manage_database), # -> DB_MANAGEMENT
                    MessageHandler(Filters.regex('^(Atras)$'), admin_options), # -> ADMIN
                    MessageHandler(Filters.text, fill_unlabeled)],
        },
        fallbacks=[
            MessageHandler(Filters.text, bot_start)
        ],
        allow_reentry = True,
    )
    logging.info('Manejadora de Voto iniciada.')
    dispatcher.add_handler(conv_handler)

    unknown_handler = MessageHandler(Filters.text, bot_unknown)
    dispatcher.add_handler(unknown_handler)

    
def main():
    """
    Inicia el bot, arrancando los servicios y manejadoras necesarios
    """
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
        logging.basicConfig(level = TG_LOG_LEVEL, filename=LOG_FILE, filemode='a', format='%(asctime)s - %(filename)s -  %(levelname)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    except FileNotFoundError:
        logging.error('ERROR: No se encontró o no se pudo crear la carpeta log/')
        exit(0)

    logging.info('Iniciando bot...')
    updater = Updater(token=DEV_TOKEN, use_context=True)
    logging.info('Updater iniciado.')
    dispatcher = updater.dispatcher
    logging.info('Dispatcher iniciado.')

    logging.info('Iniciando manejadoras...')
    init_handlers(dispatcher)
    logging.info('Manejadoras iniciadas.')

    logging.info('Comenzando a sondear...')
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
