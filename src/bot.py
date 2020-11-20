import configparser
import threading
import datetime
import logging
import time
import sys
import os


from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram import Bot

import bot_handlers as btc
import toggle_subs as tgs
import message_handlers as msh
import csv_utils

import requester as req
import analyzer as ana

API_Key = os.environ['API_Key']
LINK = os.environ["REQUEST_LINK"]

updater = Updater(API_Key, use_context=True)
dispatcher = updater.dispatcher

bot = Bot(token=API_Key)



logging.basicConfig(
        filename="data/events.log",
        level= logging.INFO,
        style="{",
        format="[{asctime}] [{levelname}] [{name}] {message}")


def send_update(date):
    cities = ["Adenau", "Altenahr", "Bad Breisig", "Brohltal", \
         "Grafschaft", "Bad Neuenahr-Ahrweiler", "Remagen", "Sinzig"]

    analyzer = ana.Analyzer(date)

    for city in cities:
        path = analyzer.visualize(city)

        for chat in writer.entries:
            s = chat.settings
            if s[city.lower()] or s["all"]:
                logging.info(f"Sending {city: <12} to {chat.id}")
                #print(path)
                bot.send_photo(chat.id, photo=open(path, 'rb'))
            else:
                logging.info(f"Ignoring {city: <11} on {chat.id} - {s[city.lower()]} ({type(s[city.lower()])}) - {s['all']} ({type(s['all'])})")

def make_request():
    while True:
        rq = req.Requester(LINK)
        if rq.success:
            logging.info('Got the requested data - starting dispatch')
            send_update(rq.date)
            logging.info("Sent all messages, sleeping until tomorrow")

            d = datetime.datetime.now()
            till_tomorrow = ((24 - d.hour - 1) * 60 * 60)\
            + ((60 - d.minute - 1) * 60)\
            + (60 - d.second)
            time.sleep(till_tomorrow)

        else:
            time.sleep(120)


reqest_thrd = threading.Thread(target=make_request)
reqest_thrd.start()


writer = csv_utils.Writer()
#passing writer object into other files
btc.setup(writer)
msh.setup(writer)
tgs.setup(writer)


start_handler = CommandHandler('start', btc.start)
dispatcher.add_handler(start_handler)

echo_handler = MessageHandler(Filters.text & (~Filters.command), msh.echo)
dispatcher.add_handler(echo_handler)

caps_handler = CommandHandler('caps', btc.caps)
dispatcher.add_handler(caps_handler)

help_handler = CommandHandler('hilfe', btc.help)
dispatcher.add_handler(help_handler)

help_handler = CommandHandler('help', btc.help)
dispatcher.add_handler(help_handler)

show_handler = CommandHandler('show', btc.show)
dispatcher.add_handler(show_handler)

#aliases for /show /help
sh_handler = CommandHandler('sh', btc.show)
dispatcher.add_handler(sh_handler)

hilfe_handler = CommandHandler('hilfe', btc.help)
dispatcher.add_handler(hilfe_handler)

h_handler = CommandHandler('h', btc.help)
dispatcher.add_handler(h_handler)

####
kreis_handler = CommandHandler('kreis', tgs.kreis)
dispatcher.add_handler(kreis_handler)

adenau_handler = CommandHandler('adenau', tgs.adenau)
dispatcher.add_handler(adenau_handler)

altenahr_handler = CommandHandler('altenahr', tgs.altenahr)
dispatcher.add_handler(altenahr_handler)

breisig_handler = CommandHandler('breisig', tgs.breisig)
dispatcher.add_handler(breisig_handler)

brohltal_handler = CommandHandler('brohltal', tgs.brohltal)
dispatcher.add_handler(brohltal_handler)

grafschaft_handler = CommandHandler('grafschaft', tgs.grafschaft)
dispatcher.add_handler(grafschaft_handler)

neuenahr_handler = CommandHandler('neuenahr', tgs.neuenahr)
dispatcher.add_handler(neuenahr_handler)

remagen_handler = CommandHandler('remagen', tgs.remagen)
dispatcher.add_handler(remagen_handler)

sinzig_handler = CommandHandler('sinzig', tgs.sinzig)
dispatcher.add_handler(sinzig_handler)

kreis_handler = CommandHandler('kreis', tgs.kreis)
dispatcher.add_handler(kreis_handler)

alle_handler = CommandHandler('alle', tgs.alle)
dispatcher.add_handler(alle_handler)


#bot.send_message(chat_id=402239048, text="Automated text")

updater.start_polling()
updater.idle()