import asyncio
from telepot.namedtuple import InputTextMessageContent, InlineQueryResultArticle
from message import Message
from bot import is_owner, is_sudo, is_mod, is_group, config
import telepot
import redis
import os
import re
import time
import json
import sys
sys.path.append('../')
import lang
r = redis.StrictRedis(host='localhost', port=6379, db=5, decode_responses=True)

bot = telepot.Bot(config['token'])


@asyncio.coroutine
def run(message, matches, chat_id, step):
    ln = lang
    if r.hget('lang_gp', chat_id) == 'en':
        ln = ln.en
    else:
        ln = ln.fa
    if matches == 'add':
        if r.sismember('groups', chat_id):
            bot.sendMessage(chat_id, ln['admin']['add']["0"])
        else:
            r.hset('lang_gp', chat_id, 'fa')
            r.sadd('groups', chat_id)
            bot.sendMessage(chat_id, ln['admin']['add']["1"])
    elif matches == 'rem':
        if r.sismember('groups', chat_id):
            r.srem('groups', chat_id)
            bot.sendMessage(chat_id, ln['admin']['rem']['0'])
        else:
            bot.sendMessage(chat_id, ln['admin']['rem']['1'])
    elif matches == 'leave':
        bot.leaveChat(chat_id)
    elif matches == 'stats':
        mmd = ['photo', 'video', 'voice', 'video_note', 'contact', 'sticker',
               'audio', 'text', 'location', 'document', 'new_chat_member']
        text = 'Stats Bot:'
        i = 0
        for x in mmd:
            get = r.get('msg:{}'.format(x))
            text += '\n>{} : {}'.format(x, get)
            i = i + int(get)
        text += '\n>All Message : {}'.format(i)
        text += '\n>pv members: {}'.format(r.scard('spntapv'))
        text += '\n>Groups: {}'.format(r.scard('groups'))
        text += '\n>Free Groups: {}'.format(r.scard('groups_free') or 0)
        bot.sendMessage(chat_id, text)
    elif matches == 'fbc':
        if 'reply_to_message' in message:
            m = message['reply_to_message']
            gp = r.smembers('groups')
            i = 0
            for x in gp:
                try:
                    send = bot.forwardMessage(x, m['chat']['id'], m['message_id'])
                    if send:
                        i += 1
                except:
                    pass
            bot.sendMessage(chat_id, 'به {} گروه ارسال شد'.format(i))


plugin = {
    "name": "admin",
    "desc": "admin",
    "run": run,
    "sudo": True,
    "patterns": [
        "^[/#!](add)",
        "^[/#!](rem)$",
        "^[/#!](leave)$",
        "^[/#!](stats)$",
        "^[/#!](sendTab) (.*)$",
        "^[/#!](fbc)$",
    ]
}
