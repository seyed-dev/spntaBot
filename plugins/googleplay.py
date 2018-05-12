import asyncio
import uuid
import demjson
from telepot.namedtuple import InlineQueryResultArticle, InlineKeyboardMarkup, InlineKeyboardButton, InputTextMessageContent
from bot import user_steps, sender, get, downloader, is_group, key, config
from message import Message
import telepot
import redis
import os
from gpapi.googleplay import GooglePlayAPI, RequestError
import sys
import argparse


r = redis.StrictRedis(host='localhost', port=6379, db=5, decode_responses=True)
bot = telepot.Bot(config['token'])
server = GooglePlayAPI('fa_IR', 'Asia/Tehran')
email = ''
password = ''
server.login(email, password, None, None)
gsfId = server.gsfId
authSubToken = server.authSubToken

server = GooglePlayAPI('fa_IR', 'Asia/Tehran')
server.login(None, None, gsfId, authSubToken)

async def search(query):
    apps = server.search(query, 20, None)
    res = []
    for a in apps:
        res.append([ a['title'], a['docId'], a['author'], a['images'][0]['url'], a['files'][0]['size']])
    return res


def getfile(docid):
    fl = server.download(docid)
    with open(docid + '.apk', 'wb') as apk_file:
        for chunk in fl.get('file').get('data'):
            apk_file.write(chunk)

def getfile2(docid):
    fl = server.download(docid)
    return fl.get('file').get('data')

@asyncio.coroutine
async def run(message, matches, chat_id, step):
    if not is_group(message):
        from_id = message[ 'from' ][ 'id' ]
        if step == 0:
            if message[ 'text' ] == '📱جستجوی برنامه' or message['text'] == '/start google_play':
                user_steps[ from_id ] = {"name": "googleplay", "step": 1, "docid": {}, "image": {}, "author": {}, "size": {}}
                hide_keyboard = {'hide_keyboard': True, "selective": True}
                return [ Message(chat_id).set_text("لطفا نام برنامه یا بازی خود را ارسال کنید",
                                                   reply_to_message_id=message[ 'message_id' ],
                                                   reply_markup=hide_keyboard) ]
            elif matches[0] == 'dlapp':
                app = matches[1].replace('_', '.')
                getfile(app)
                bot.sendDocument(chat_id, open(app + '.apk', 'rb'),
                                 caption='{}\n@spntaBot'.format(app))
                os.remove(app + '.apk')
        if step == 1:
            await sender(
                Message(chat_id).set_text("اومم یکم صبر کن برم جستجو کنم ببینم چی گیرم میاد 😘😬",
                                          parse_mode="markdown"))
            user_steps[ from_id ] = {"name": "googleplay", "step": 2, "docid": {}, "image": {}, "author": {}, "size": {}}
            i = 0
            show_keyboard = {'keyboard': [ ], "selective": True}
            for gplay in await search(message['text']):
                title, docid, author, image, size = gplay[ 0 ], gplay[1], gplay[2], gplay[3], gplay[4]
                user_steps[ from_id ][ 'docid' ][ title ] = docid
                user_steps[ from_id ][ 'image' ][ title ] = image
                user_steps[ from_id ][ 'size' ][ title ] = size
                user_steps[ from_id ][ 'author' ][ title ] = author


                show_keyboard[ 'keyboard' ].append([ title ])
                i += 1
                if i == 20:
                    break
            if len(show_keyboard[ 'keyboard' ]) in [ 0, 1 ]:
                hide_keyboard = {'hide_keyboard': True, 'selective': True}
                del user_steps[ from_id ]
                return [ Message(chat_id).set_text("چیزی نیافتم 😣",
                                                   reply_to_message_id=message[ 'message_id' ],
                                                   reply_markup=key,
                                                   parse_mode="markdown") ]
            return [ Message(chat_id).set_text("یکی از اینارو انتخاب کن 🙃👇🏻",
                                               reply_to_message_id=message[ 'message_id' ],
                                               reply_markup=show_keyboard) ]
        elif step == 2:
            try:

                await sender(Message(chat_id).set_text("خب یکم صبر کن تا برنامه دانلود کنم و برات بفرستم 🤓",
                                                       reply_to_message_id=message[ 'message_id' ],
                                                       reply_markup=key, parse_mode="markdown"))

                getfile(user_steps[ from_id ][ 'docid' ][ message[ 'text' ] ])
                size = int(user_steps[from_id]['size'][message['text']] / 1024 / 1024)
                cap = '''🔖نام : {}
👨‍💻سازنده : {}
▫️حجم : {} مگابایت
'''.format(message['text'], user_steps[from_id]['author'][message['text']], size)
                bot.sendPhoto(chat_id, user_steps[ from_id ][ 'image' ][ message[ 'text' ] ],
                              caption=cap)
                bot.sendDocument(chat_id, open(user_steps[from_id]['docid'][message['text']] + '.apk', 'rb'),
                                 caption='{}\n@spntaBot'.format(message['text']), reply_markup=key)
                os.remove(user_steps[from_id]['docid'][message['text']] + '.apk')
                del user_steps[from_id]
            except Exception as e:
                print(e)
                del user_steps[ from_id ]
                return [ Message(chat_id).set_text("داری اشتباه میزنی 😕", parse_mode="markdown", reply_markup=key) ]


@asyncio.coroutine
async def inline(message, matches, chat_id, step):
    query_id, from_id, query = telepot.glance(message, flavor='inline_query')
    app = [ ]
    i = 0
    for gplay in await search(matches[1]):
        title, docid, author, image, size = gplay[ 0 ], gplay[ 1 ], gplay[ 2 ], gplay[ 3 ], gplay[ 4 ]
        size = int(size / 1024 / 1024)
        cap = '''🔖نام : {}
👨‍💻سازنده : {}
▫️حجم : {} مگابایت
برای دانلود روی دکمه زیر کلیک کنید
'''.format(title, author, size)
        key = [
            [
                InlineKeyboardButton(text='📥 دانلود', url='t.me/spntabot?start=dlapp_{}'.format(docid.replace('.', '_'))),
            ]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=key)
        app.append(InlineQueryResultArticle(
            id=str(uuid.uuid4()), title=title,
            input_message_content=InputTextMessageContent(message_text=cap),
            reply_markup=markup,
            thumb_url=image))
        i += 1
        if i == 20:
            break
    bot.answerInlineQuery(query_id, app)


plugin = {
    "name": "googleplay",
    "desc": "Download a Android App From Google Play",
    "usage": "/google play" ,
    "run": run,
    "sudo": False,
    "inline_patterns": [ "^(googleplay) (.*)$" ],
    "inline_query": inline,
    "patterns": [
        "^📱جستجوی برنامه$",
        "^/start (google_play)$",
        "^/start (dlapp)_(.*)$"
    ]
}
