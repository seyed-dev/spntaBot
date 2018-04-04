import asyncio
from telepot.namedtuple import InputTextMessageContent, InlineQueryResultArticle
from message import Message
from bot import is_owner, is_sudo, is_mod, is_group, config
import telepot
import redis
import os
import re
import urllib.request as ur
import urllib
bot = telepot.Bot(config['token'])


@asyncio.coroutine
def run(message, matches, chat_id, step):
    if matches[0] == 'voice':
        text = ur.quote(matches[1])
        url = 'http://api.farsireader.com/ArianaCloudService/ReadTextGET?APIKey=demo&Text={}&Speaker=Female1' \
              '&Format=mp3%2F32%2Fm&GainLevel=3&PitchLevel=4&PunctuationLevel=2&SpeechSpeedLevel=5' \
              '&ToneLevel=10'.format(text)
        ur.urlretrieve(url, 'tmp/{}.mp3'.format(message['from']['id']))
        bot.sendVoice(chat_id, open('tmp/{}.mp3'.format(message['from']['id']), 'rb'), caption='@spntaBot')
        os.remove('tmp/{}.mp3'.format(message['from']['id']))


plugin = {
    "name": "voice",
    "desc": "voice",
    "usage": ["/voice"],
    "run": run,
    "sudo": False,
    "patterns": [
        "^[/#!](voice) (.*)",
    ]
}
