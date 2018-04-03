import asyncio
from telepot.namedtuple import InlineQueryResultAudio, InlineKeyboardMarkup, InlineKeyboardButton,\
    InlineQueryResultArticle, InputTextMessageContent
import uuid
from message import Message
import telepot
import re
import requests
from bs4 import BeautifulSoup
import redis
import string
import random
r = redis.StrictRedis(host='localhost', port=6379, db=5, decode_responses=True)

bot = telepot.Bot('524062252:AAGlpKb8hEKDhmiCpNSoY1qlUwGkJ-3_Z3c')


@asyncio.coroutine
def run(message, matches, chat_id, step):
    pass


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


@asyncio.coroutine
async def inline(message, matches, chat_id, step):
    query_id, from_id, query = telepot.glance(message, flavor='inline_query')
    mtext = matches[1].replace(' ', '+')
    link = 'http://www.faratext.com/?s={}'.format(mtext)
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")
    num = 1
    gg = []
    for x in soup.findAll("div", {"class": "col-sm-12 col-md-12 content"}):
        if num == 5:
            break
        more_link = x.find('a', {'class': 'more-link'})['href']
        idrand = id_generator(6)
        r.hset('music:data', idrand, more_link)
        key = [
            [
                InlineKeyboardButton(text='💠 متن ترانه 💠', callback_data='textmusic-{}'.format(idrand)),
            ]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=key)
        gg.append(InlineQueryResultArticle(
            id=str(uuid.uuid4()), title='{}'.format(x.get_text()),
            input_message_content=InputTextMessageContent(
                message_text= '{}\n\nبرای دریافت متن ترانه روی دکمه زیر کلیک کنید'.format(x.get_text())),
            reply_markup=markup,
            thumb_url=x.find('a', href=True)['href']))
        num += 1
    bot.answerInlineQuery(query_id, gg)


@asyncio.coroutine
def callback(message, matches, chat_id):
    query_id, from_id, data = telepot.glance(message, flavor='callback_query')
    res = requests.get(r.hget('music:data', matches[1]))
    ss = BeautifulSoup(res.text, "html.parser")
    mtext = ss.find('div', {'class': 'col-sm-12 col-md-12 content'})
    keys = [
        [
            InlineKeyboardButton(text='💠 سپنتا بوت 💠', url='t.me/spntaBot'),
        ]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keys)
    msgid = (message['inline_message_id'])
    bot.editMessageText(msgid, mtext.get_text(), parse_mode='html', reply_markup=markup)



plugin = {
    "name": "textmusic",
    "desc": "textmusic",
    "usage": ["/textmusic text"],
    "run": run,
    "sudo": False,
    "inline_patterns": [ "^(متن ترانه) (.*)$" ],
    "inline_query": inline,
    "callback": callback,
    "callback_patterns": [
        "^(textmusic)-(.*)",
    ],
    "patterns": []
}
