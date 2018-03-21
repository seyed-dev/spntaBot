# -*- coding: utf-8 -*-
import asyncio
import uuid
import demjson
from telepot.namedtuple import InlineQueryResultAudio, InlineKeyboardMarkup, InlineKeyboardButton,\
    InlineQueryResultArticle, InputTextMessageContent
from bot import user_steps, sender, get, downloader, is_group, config
from message import Message
import requests
import telepot
import json
import os
import urllib.request as ur
import re
bot = telepot.Bot(config['token'])


@asyncio.coroutine
async def run(message, matches, chat_id, step):
    if not is_group(message):
        return [Message(chat_id).set_text("test", parse_mode="markdown")]


@asyncio.coroutine
async def inline(message, matches, chat_id, step):
    query_id, from_id, query = telepot.glance(message, flavor='inline_query')
    ttt = matches[1].replace(" ", "+")
    vaje = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/39.0.2171.95 Safari/537.36'}

    req = requests.get('https://search.digikala.com/api/SearchApi/', params={'q': ttt}, headers=headers)
    jdat = json.loads(req.text)
    i = 0
    for s in jdat['hits']['hits']:
        x = s['_source']
        pic_url = 'https://file.digi-kala.com/digikala/{}'.format(x['ImagePath'])
        fa_title = x['Title']
        min_price = '{}'.format(x['MinPrice'])
        max_price = '{}'.format(x['MaxPrice'])
        price = ''
        if int(min_price) == int(max_price):
            min_p = float(min_price[:-1])
            price += '{:,f} تومان'.format(min_p).split('.')[0]
        else:
            min_p = float(min_price[:-1])
            max_p = float(max_price[:-1])
            mm = '{:,f}'.format(min_p).split('.')[0]
            nn = '{:,f}'.format(max_p).split('.')[0]
            price += '{} تومان ← {} تومان'.format(mm, nn)
        pid = re.findall(r'\d+', x['ImagePath'])[0]

        key = [
            [
                InlineKeyboardButton(text='🛍 مشاهده و خرید', url='digikala.com/p/{}'.format(pid)),
            ],
            [
                InlineKeyboardButton(text='جستجوی جدید', switch_inline_query_current_chat='digikala '),
                InlineKeyboardButton(text='انتخاب کالای دیگر', switch_inline_query_current_chat='digikala {}'.format(matches[1]))
            ]
        ]
        text = '''🔖 {}

@spntaBot

{}

[-]({})'''.format(fa_title, price, pic_url)
        markup = InlineKeyboardMarkup(inline_keyboard=key)
        vaje.append(InlineQueryResultArticle(
            id=str(uuid.uuid4()), title=fa_title,
            description=price,
            input_message_content=InputTextMessageContent(message_text=text, parse_mode='Markdown'),
            reply_markup=markup,
            thumb_url=pic_url))
        i += 1
        if i == 20:
            break
    bot.answerInlineQuery(query_id, vaje)


plugin = {
    "name": "digikala",
    "desc": "digikala",
    "usage": "digikala",
    "run": run,
    "sudo": False,
    "inline_patterns": ["^(digikala) (.*)$"],
    "inline_query": inline,
    "patterns": [
        "^digikala"
    ]
}
