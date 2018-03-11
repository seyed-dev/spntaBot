import asyncio
import telepot
from message import Message
from bot import is_group, download
import os
bot = telepot.Bot('524062252:AAGVHYYvesW-bWoSvfGzgh7Jz2PI4tVdIOc')

@asyncio.coroutine
def run(message, matches, chat_id, step):
    if 'reply_to_message' in message:
        m = message['reply_to_message']
        content_type, chat_type, chat_id = telepot.glance(message['reply_to_message'])
        if matches == 'photo':
            if content_type == 'photo':
                bot.sendMessage(chat_id, 'خودش عکسه هاجی 😑')
            elif content_type == 'sticker':
                bot.download_file(m['sticker']['file_id'], 'tmp/{}.jpg'.format(message['from']['id']))
                bot.sendPhoto(chat_id, open('tmp/{}.jpg'.format(message['from']['id']), 'rb'))
                os.remove('tmp/{}.jpg'.format(message['from']['id']))
            elif content_type == 'document':
                bot.download_file(m['document']['file_id'], 'tmp/{}.jpg'.format(message['from']['id']))
                bot.sendPhoto(chat_id, open('tmp/{}.jpg'.format(message['from']['id']), 'rb'))
                os.remove('tmp/{}.jpg'.format(message['from']['id']))
        elif matches == 'sticker':
            if content_type == 'sticker':
                bot.sendMessage(chat_id, 'خودش استیکره هاجی 😑')
            elif content_type == 'photo':
                bot.download_file(m['photo'][1]['file_id'], 'tmp/{}.jpg'.format(message['from']['id']))
                bot.sendSticker(chat_id, open('tmp/{}.jpg'.format(message['from']['id']), 'rb'))
                os.remove('tmp/{}.jpg'.format(message['from']['id']))
            elif content_type == 'document':
                bot.download_file(m['document']['file_id'], 'tmp/{}.jpg'.format(message['from']['id']))
                bot.sendSticker(chat_id, open('tmp/{}.jpg'.format(message['from']['id']), 'rb'))
                os.remove('tmp/{}.jpg'.format(message['from']['id']))
        elif matches == 'file':
            if content_type == 'document':
                bot.sendMessage(chat_id, 'خودش فایله هاجی 😑')
            elif content_type == 'sticker':
                bot.download_file(m['sticker']['file_id'], 'tmp/{}.jpg'.format(message['from']['id']))
                bot.sendDocument(chat_id, open('tmp/{}.jpg'.format(message['from']['id']), 'rb'))
                os.remove('tmp/{}.jpg'.format(message['from']['id']))
            elif content_type == 'photo':
                bot.download_file(m['photo'][1]['file_id'], 'tmp/{}.jpg'.format(message['from']['id']))
                bot.sendDocument(chat_id, open('tmp/{}.jpg'.format(message['from']['id']), 'rb'))
                os.remove('tmp/{}.jpg'.format(message['from']['id']))

plugin = {
    "name": "photostick",
    "desc": "photostick",
    "usage": ["photostick"],
    "run": run,
    "sudo": False,
    "patterns": [
        "^[!/#](sticker)$",
        "^[!/#](photo)$",
        "^[!/#](file)$"
    ]
}