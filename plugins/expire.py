import asyncio
from telepot.namedtuple import InputTextMessageContent, InlineQueryResultArticle
from message import Message
from bot import is_owner, is_sudo, is_mod, is_group, config
import telepot
import redis
import os
import re
import time
r = redis.StrictRedis(host='localhost', port=6379, db=5, decode_responses=True)

bot = telepot.Bot(config['token'])

@asyncio.coroutine
def run(message, matches, chat_id, step):
    if matches[0] == 'setexpire':
        if is_sudo(message):
            exp = time.time() + int(matches[1]) * 86400
            r.setex('expire:{}'.format(chat_id), int(exp), 'hemmhm')
            bot.sendMessage(chat_id, 'تاریخ انقضای گروه برای {} روز دیگر تنظیم شد☘️'.format(matches[1]))
    elif matches == 'expire':
        if is_mod(message):
            ex = int(r.ttl('expire:{}'.format(chat_id))) - time.time()
            days = int(ex / 86400)
            bot.sendMessage(chat_id, '📋 روز های باقیمانده از اعتبار گروه : {}'.format(days))



plugin = {
    "name": "expire",
    "desc": "expire",
    "usage": ["/expire"],
    "run": run,
    "sudo": False,
    "patterns": [
        "^[/#!](setexpire) (.*)",
        "^[/#!](expire)$",
    ]
}
