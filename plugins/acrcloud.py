import asyncio
import uuid
import demjson
from telepot.namedtuple import InlineQueryResultAudio, InlineKeyboardMarkup, InlineKeyboardButton
from bot import user_steps, sender, get, downloader, is_group, download, is_mod, key, config
from message import Message
import telepot
import soundcloud
import os, sys
from requests import get
import json
from acrcloud.recognizer import ACRCloudRecognizer

bot = telepot.Bot(config['token'])
#get from https://www.acrcloud.com/
config = {
        'host': '',
        'access_key': '',
        'access_secret': '',
        'timeout': 10
    }

acr = ACRCloudRecognizer(config)




@asyncio.coroutine
async def run(message, matches, chat_id, step):
    from_id = message['from']['id']
    if not is_group(message):
        if step == 0:
            user_steps[from_id] = {"name": "voice_search", "step": 1, "data": {}}
            hide_keyboard = {'hide_keyboard': True, "selective": True}
            return [Message(chat_id).set_text("لطفا 10 الی 15 ثانیه از موزیک را بصورت ویس ارسال کنید🎼",
                                              reply_to_message_id=message['message_id'],
                                              reply_markup=hide_keyboard)]
        elif step == 1:
            content_type, chat_type, chat_id = telepot.glance(message)
            bot.download_file(message['voice']['file_id'],
                              'tmp/{}.mp3'.format(message['from']['id']))
            req = acr.recognize_by_file('tmp/{}.mp3'.format(message['from']['id']), 0)
            os.remove('tmp/{}.mp3'.format(message['from']['id']))
            jdat = json.loads(req)
            if jdat['status']['msg'] == 'No result':
                del user_steps[from_id]
                return [Message(chat_id).set_text("چیزی پیدا نکردم ☹️", parse_mode="markdown",
                                                  reply_markup=key)]
            else:
                arc = jdat['metadata']['music'][0]
                text = '''🗣خواننده : {}
📆سال ساخت :‌ {}
🎼عنوان موزیک : {}
🎧نام آلبوم : {}
از بخش جستجوی موزیک با استفاده از نام موزیک و اسم خواننده موزیک را سرچ کنید 😉'''.format(arc['artists'][0]['name'] or '', arc['release_date'] or '', arc['title'] or '',
                                       arc['album']['name'] or '')
                bot.sendMessage(chat_id, text, reply_to_message_id=message['message_id'], reply_markup=key)
                del user_steps[from_id]
    else:
        if is_mod(message):
            m = message['reply_to_message']
            if 'audio' in m:
                bot.download_file(m['audio']['file_id'],
                              'tmp/{}.mp3'.format(message['from']['id']))
            elif 'voice' in m:
                bot.download_file(m['voice']['file_id'], 'tmp/{}.mp3'.format(message['from']['id']))
            elif 'video' in m:
                bot.download_file(m['video']['file_id'], 'tmp/{}.mp3'.format(message['from']['id']))
            elif 'video_note' in m:
                bot.download_file(m['video_note']['file_id'], 'tmp/{}.mp3'.format(message['from']['id']))
            req = acr.recognize_by_file('tmp/{}.mp3'.format(message['from']['id']), 0)
            os.remove('tmp/{}.mp3'.format(message['from']['id']))
            jdat = json.loads(req)
            if jdat['status']['msg'] == 'No result':
                return [Message(chat_id).set_text("چیزی پیدا نکردم ☹️", parse_mode="markdown")]
            else:
                arc = jdat['metadata']['music'][0]
                text = '''🗣خواننده : {}
            📆سال ساخت :‌ {}
            🎼عنوان موزیک : {}
            🎧نام آلبوم : {}
            از بخش جستجوی موزیک(در پیوی ربات) با استفاده از نام موزیک و اسم خواننده موزیک را سرچ کنید 😉'''.format(
                    arc['artists'][0]['name'] or '', arc['release_date'] or '', arc['title'] or '',
                    arc['album']['name'] or '')
                bot.sendMessage(chat_id, text, reply_to_message_id=message['message_id'])


plugin = {
    "name": "voice_search",
    "desc": "voice_search",
    "usage": "voice_search",
    "run": run,
    "sudo": False,
    "patterns": [
        "^🎼جستجوی با ویس$",
        "[/#!]search"
    ]
}
