# -*- coding: utf-8 -*-
import asyncio
import uuid
import demjson
from telepot.namedtuple import InlineQueryResultAudio, InlineKeyboardMarkup, InlineKeyboardButton
from bot import user_steps, sender, get, downloader, is_group, download, config
from message import Message
import telepot
import soundcloud
import os, sys
from requests import get
import json
import telepot
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
bot = telepot.Bot(config['token'])


@asyncio.coroutine
async def run(message, matches, chat_id, step):
        if 'reply_to_message' in message:
            reply = message['reply_to_message']
            if 'photo' in reply:
                await download(reply['photo'][1]['file_id'], 'tmp/ocr{}.jpg'.format(message['from']['id']))
                text = pytesseract.image_to_string(Image.open('tmp/ocr{}.jpg'.format(message['from']['id'])))
                os.remove('tmp/ocr{}.jpg'.format(message['from']['id']))
                return [Message(chat_id).set_text(text)]


plugin = {
    "name": "ocr",
    "desc": "ocr",
    "usage": "ocr",
    "run": run,
    "sudo": False,
    "patterns": [
        "^[/#!](ocr)$"
    ]
}
