import asyncio
import uuid
import demjson
from telepot.namedtuple import InlineQueryResultAudio, InlineKeyboardMarkup, InlineKeyboardButton
from bot import user_steps, sender, get, downloader, is_group, is_mod, config
from message import Message
import telepot
import soundcloud
import redis
import os
from requests import get
import urllib.request as ur
import json


def download(url, file_name):
    # open in binary mode
    with open(file_name, "wb") as file:
        # get request
        response = get(url)
        # write to file
        file.write(response.content)


bot = telepot.Bot(config['token'])
# create a client object with your app credentials
client = soundcloud.Client(client_id='{}'.format(config['soundcloud_client_id']))
page_size = 100
r = redis.StrictRedis(host='localhost', port=6379, db=5, decode_responses=True)

# get first 100 tracks


async def search(query):
    tracks = client.get('/tracks', q=query, limit=page_size)
    res = []
    for track in tracks:
        res.append([track.title, track.permalink_url, track.artwork_url or None])
    return res


def getfile2(url):
    response = "https://api.soundcloud.com/resolve?url={}&client_id={}".format(url, config['soundcloud_client_id'])
    r = ur.urlopen(response).read().decode('utf-8')
    jdat = json.loads(r)
    return jdat['stream_url'] + "?client_id={}".format(config['soundcloud_client_id'])


@asyncio.coroutine
async def run(message, matches, chat_id, step):
    if is_mod(message):
        if matches[0] == 'music':
            show_keyboard = []
            i = 0
            user_steps[chat_id] = {"name": "Soundcloud", "step": 0, "data": {}, "cover": {}, "title": {}}
            for song in await search(matches[1]):
                title, link, cover = song[0], song[1], song[2]
                cover_music = ''
                if cover:
                    cover_music = cover.replace('large', 't500x500')
                else:
                    cover_music = 'https://www.apple.com/v/apple-music/e/images/shared/og_image.png?201802090801'
                user_steps[chat_id]['cover'][i] = cover_music
                user_steps[chat_id]['data'][i] = link
                user_steps[chat_id]['title'][i] = title
                show_keyboard.append([InlineKeyboardButton(text=title, callback_data='music {}'.format(i))])
                i += 1
                if i == 20:
                    break
            if len(show_keyboard) in [0, 1]:
                return [Message(chat_id).set_text('چیزی پیدا نکردم :(')]
            markup = InlineKeyboardMarkup(inline_keyboard=show_keyboard)
            bot.sendMessage(chat_id, "یکی از اینارو انتخاب کن 🙃👇🏻", reply_markup=markup)


@asyncio.coroutine
def callback(message, matches, chat_id):
    query_id, from_id, data = telepot.glance(message, flavor='callback_query')
    if matches[0] == 'music':
        msgid = (chat_id, message['message']['message_id'])
        bot.editMessageText(msgid, 'موزیک بزودی برای شما ارسال خواهد شد😊👌🏻')
        i = int(matches[1])
        link = user_steps[chat_id]['data'][i]
        cover = user_steps[chat_id]['cover'][i]
        title = user_steps[chat_id]['title'][i]
        file = getfile2(link)
        try:
            bot.sendPhoto(chat_id, cover, caption='{}\n@{}'.format(title, bot.getMe()['username']))
        except:
            pass
        bot.sendAudio(chat_id, file,title=title, performer="@{}".format(bot.getMe()['username']),
                      caption='@{}'.format(bot.getMe()['username']))
        del user_steps[chat_id]


plugin = {
    "name": "Soundcloud",
    "desc": "Download a Music From Sound Cloud\n\n"
            "*For Start :*\n`/sc michael jackson billie jean`",
    "usage": ["/music \\[`Search`]"],
    "run": run,
    "sudo": False,
    "callback": callback,
    "callback_patterns": [
        "^(music) (.*)",
    ],
    "patterns": [
        "^[/#!](music) (.*)"
    ]
}
