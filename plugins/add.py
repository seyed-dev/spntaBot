import asyncio
from telepot.namedtuple import InputTextMessageContent, InlineQueryResultArticle
from message import Message
from bot import is_owner, is_sudo, is_mod, is_group
import telepot
import redis
import os
import re
import time
import json
r = redis.StrictRedis(host='localhost', port=6379, db=5, decode_responses=True)

bot = telepot.Bot('524062252:AAGVHYYvesW-bWoSvfGzgh7Jz2PI4tVdIOc')


@asyncio.coroutine
def run(message, matches, chat_id, step):
    if matches == 'add':
        if r.sismember('groups', chat_id):
            bot.sendMessage(chat_id, 'گروه از قبل به لیست گروه های ربات اضافه شده بود🔖')
        else:
            r.sadd('groups', chat_id)
            bot.sendMessage(chat_id, 'گروه به لیست گروه های ربات اضافه شد🔖')
            bot.sendMessage(284244758, 'Group added\n{}\n{}'.format(chat_id, message['from']['first_name']))
    elif matches == 'rem':
        if r.sismember('groups', chat_id):
            r.srem('groups', chat_id)
            bot.sendMessage(chat_id, 'با موفقیت حذف شد💢')
        else:
            bot.sendMessage(chat_id, 'این گروه در لیست گروه های ربات موجود نبوده🌀ـ🌀')
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
    elif matches[0] == 'sendTab' and matches[1]:
        gp = r.smembers('groups')
        i = 0
        for x in gp:
            try:
                send = bot.sendMessage(x, matches[1], parse_mode='Markdown')
                if send:
                    i = i + 1
            except:
                pass
        bot.sendMessage(chat_id, 'به {} گروه ارسال شد'.format(i))
    elif matches == 'fbc':
        if 'reply_to_message' in message:
            m = message['reply_to_message']
            gp = r.smembers('groups')
            i = 0
            for x in gp:
                try:
                    send = bot.forwardMessage(x, m['chat']['id'], m['message_id'])
                    if send:
                        i = i + 1
                except:
                    pass
            bot.sendMessage(chat_id, 'به {} گروه ارسال شد'.format(i))

    elif matches == 'leave_free':
        free = r.smembers('groups_free')
        for x in free:
            try:
                bot.leaveChat(x)
            except:
                pass
            r.srem('groups_free', x)
        bot.sendMessage(chat_id, 'Bot Left From All Free Groups')


plugin = {
    "name": "پنل ادمین",
    "desc": "دستوراتی مخصوص ادمین های ربات",
    "usage": ["/add"],
    "run": run,
    "sudo": True,
    "patterns": [
        "^[/#!](add)",
        "^[/#!](rem)$",
        "^[/#!](leave)$",
        "^[/#!](stats)$",
        "^[/#!](sendTab) (.*)$",
        "^[/#!](fbc)$",
        "^[/#!](leave_free)$"
    ]
}