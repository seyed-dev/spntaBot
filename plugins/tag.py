# -*- coding: utf-8 -*-
import asyncio
import uuid
import demjson
from telepot.namedtuple import InlineQueryResultAudio, InlineKeyboardMarkup, InlineKeyboardButton
from bot import user_steps, sender, get, downloader, is_group, download, is_mod, config
from message import Message
import telepot
import soundcloud
import os, sys
from requests import get
import json
import telepot
bot = telepot.Bot(config['token'])


@asyncio.coroutine
async def run(message, matches, chat_id, step):
    if is_mod(message):
        if 'reply_to_message' in message:
            reply = message['reply_to_message']
            if 'audio' in reply:
                await download(reply['audio']['file_id'], 'tmp/{}.mp3'.format(message['from']['id']))
                s = matches[1].split(':')
                title = s[0]
                performer = s[1]
                bot.sendChatAction(chat_id, 'upload_audio')
                bot.sendAudio(chat_id, open('tmp/{}.mp3'.format(message['from']['id']), 'rb'),
                              performer=performer, title=title, duration=reply['audio']['duration'])
                os.remove('tmp/{}.mp3'.format(message['from']['id']))


plugin = {
    "name": "tag",
    "desc": "tag",
    "usage": "tag",
    "run": run,
    "sudo": False,
    "patterns": [
        "^(tag) (.*)",
        "^(تگ)(.*)"
    ]
}
