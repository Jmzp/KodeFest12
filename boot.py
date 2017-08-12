import time
import configparser
import os
import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, update, ChatAction
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


logger = logging.getLogger(__name__)

# cargamos la configuración
config = configparser.ConfigParser()
config.read("etc/config.ini")


TO, SUBJECT, BODY, SEND = range(4)
TOKEN = config['KEYS']['bot_api']



def error(bot, update : update, error):
    logger.warning('Update "%s" causo el error "%s"' % (update, error))

def main():

    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states



    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()