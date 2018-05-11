import asyncio
from telepot.namedtuple import InputTextMessageContent, InlineQueryResultArticle
import sys
sys.path.append('../')
from message import Message
from bot import is_owner, is_sudo, is_mod, is_group, config
import telepot
import redis
import os
import re
import time
from datetime import datetime
import pytz
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
    if matches == 'setowner':
        if 'reply_to_message' in message:
            if is_sudo(message):
                r.hset('owner', chat_id, message['reply_to_message']['from']['id'])
                r.hset('owner:{}'.format(chat_id), message['reply_to_message']['from']['id'], True)
                text = str(ln['ingroup']['setowner']).format(message['reply_to_message']['from']['first_name'],
                        message['reply_to_message']['from']['id'])
                bot.sendMessage(chat_id, text, parse_mode='Markdown')
    if matches == 'admin':
        if 'reply_to_message' in message:
            if is_owner(message):
                r.sadd('mod:{}'.format(chat_id), message['reply_to_message']['from']['id'])
                text = str(ln['ingroup']['setowner']).format(message['reply_to_message']['from']['first_name'],
                        message['reply_to_message']['from']['id'])
                bot.sendMessage(chat_id, text, parse_mode='Markdown')
    if matches == 'user':
        if 'reply_to_message' in message:
            if is_owner(message):
                r.srem('mod:{}'.format(chat_id), message['reply_to_message']['from']['id'])
                text= str(ln['ingroup']['user']).format(message['reply_to_message']['from']['first_name'],
                          message['reply_to_message']['from']['id'])
                bot.sendMessage(chat_id, text, parse_mode='Markdown')
    if matches[0] == 'title' and matches[1]:
        if is_mod(message):
            try:
                set = bot.setChatTitle(chat_id, matches[1])
                bot.sendMessage(chat_id, ln['ingroup']['title'], reply_to_message_id=message['message_id'])
            except:
                pass
    if matches == 'pin':
        if is_mod(message):
            if 'reply_to_message' in message:
                bot.pinChatMessage(chat_id, message['reply_to_message']['message_id'])
                bot.sendMessage(chat_id, ln['ingroup']['pin'], reply_to_message_id=message['reply_to_message']['message_id'])
    if matches == 'unpin':
        if is_mod(message):
            bot.unpinChatMessage(chat_id)
            bot.sendMessage(chat_id, ln['ingroup']['unpin'])
    if matches == 'ban':
        if is_mod(message):
            if 'reply_to_message' in message:
                user = message['reply_to_message']
                if not is_mod(user):
                    bot.kickChatMember(chat_id, user['from']['id'])
                    bot.sendMessage(chat_id, str(ln['ingroup']['ban']).format(user['from']['first_name'],
                                                                              user['from']['id']), parse_mode='Markdown')
                else:
                    bot.sendMessage(chat_id, ln['ingroup']['banError'])
    if matches[0] == 'ban':
        if is_mod(message):
            user = str(matches[1])
            bot.kickChatMember(chat_id, user)
            bot.sendMessage(chat_id, 'کاربر {} از گروه اخراج شد❌'.format(user))
            bot.sendMessage(r.hget('owner', chat_id), '''کاربر [{}](tg://user?id={}) از گروه {} اخراج شد❌
اخراج کننده :  [{}](tg://user?id={})
'''.format(user, user, message['chat']['title'], message['from']['id'], message['from']['id']), parse_mode='Markdown')
    if matches == 'avatar':
        if is_mod(message):
            try:
                bot.download_file(message['reply_to_message']['photo'][1]['file_id'], '{}.jpg'.format(chat_id))
                bot.setChatPhoto(chat_id, open('{}.jpg'.format(chat_id), 'rb'))
                os.remove('{}.jpg'.format(chat_id))
            except Exception as e:
                bot.sendMessage(chat_id, '#Error:\n{}'.format(e),
                                reply_to_message_id=message['reply_to_message']['message_id'])
    if matches == 'admins':
        if is_mod(message):
            owner = r.hget('owner', chat_id)
            if owner:
                oner = '[{}](tg://user?id={})'.format(owner, owner)
            else:
                oner = ln['ingroup']['admins']['0']
            mods = r.smembers('mod:{}'.format(chat_id))
            if mods:
                mod = '👥'
                sc = r.scard('mod:{}'.format(chat_id))
                scnum = int(sc)
                i = 1
                for x in mods:
                    if scnum == i:
                        mod += '\n└ > [{}](tg://user?id={})'.format(x, x)
                    else:
                        mod += '\n├> [{}](tg://user?id={})'.format(x, x)
                        i = i + 1
            else:
                mod = ln['ingroup']['admins']['0']

            text = str(ln['ingroup']['admins'][1]).format(oner, mod)
            bot.sendMessage(chat_id, text, parse_mode='Markdown')
    if matches[0] == 'filter':
        if is_mod(message):
            text = message['text'].replace(matches[0], '').replace('/ ', '').replace('# ', '').replace('! ', '')
            lines = re.findall('[^\n]+', text)
            fil = ''
            for x in lines:
                r.sadd('filter:{}'.format(chat_id), x)
                fil += '\n>{}'.format(x)
            bot.sendMessage(chat_id, str(ln['ingroup']['filter']).format(fil))
    if matches[0] == 'unfilter':
        if is_mod(message):
            text = message['text'].replace(matches[0], '').replace('/ ', '').replace('# ', '').replace('! ', '')
            lines = re.findall('[^\n]+', text)
            fil = ''
            for x in lines:
                r.srem('filter:{}'.format(chat_id), x)
                fil += '\n>{}'.format(x)
            bot.sendMessage(chat_id, str(ln['ingroup']['unfilter']).format(fil))
    if matches == 'filters':
        if is_mod(message):
            filters = r.smembers('filter:{}'.format(chat_id))
            text = ''
            for x in filters:
                text += '\n>{}'.format(x)
            bot.sendMessage(chat_id, str(ln['ingroup']['filters']).format(text))
    if matches[0] == 'mute':
        if is_mod(message):
            if 'reply_to_message' in message:
                user = message['reply_to_message']
                if not is_mod(user):
                    name = message['reply_to_message']['from']['first_name']

                    bot.restrictChatMember(chat_id, user['from']['id'],
                                           until_date=time.time() + int(matches[1]) * 86400,
                                           can_send_messages=False, can_send_media_messages=False,
                                           can_send_other_messages=False, can_add_web_page_previews=False
                                           )
                    bot.sendMessage(chat_id, str(ln['ingroup']['mute']).format(name, user['from']['id'], matches[1]),
                                    parse_mode='Markdown')

                else:
                    bot.sendMessage(chat_id, 'ادمینه 🤧')
    if matches == 'unmute':
        if is_mod(message):
            if 'reply_to_message' in message:
                user = message['reply_to_message']
                bot.restrictChatMember(chat_id, user['from']['id'],
                                       can_send_messages=True, can_send_media_messages=True,
                                       can_send_other_messages=True, can_add_web_page_previews=True)
                bot.sendMessage(chat_id, ln['ingroup']['unmute'])
    if matches[0] == 'unmute':
        if is_mod(message):
            if 'reply_to_message' in message:
                bot.restrictChatMember(chat_id, matches[1],
                                       can_send_messages=True, can_send_media_messages=True,
                                       can_send_other_messages=True, can_add_web_page_previews=True)
                bot.sendMessage(chat_id, ln['ingroup']['unmute'])
    if matches[0] == 'mute' and matches[1] == 'all':
        if is_mod(message):
            if r.hget('lock_all', chat_id):
                bot.sendMessage(chat_id, ln['ingroup']['muteAll']['0'])
            else:
                r.hset('lock_all', chat_id, True)
                bot.sendMessage(chat_id,  ln['ingroup']['muteAll']['1'])
    if matches[0] == 'unmute' and matches[1] == 'all':
        if is_mod(message):
            if r.hget('lock_all', chat_id):
                r.hdel('lock_all', chat_id)
                bot.sendMessage(chat_id, ln['ingroup']['unmuteAll']['0'])
            else:
                bot.sendMessage(chat_id, ln['ingroup']['unmuteAll']['1'])
    if matches == 'newlink':
        if is_mod(message):
            link = bot.exportChatInviteLink(chat_id)
            r.hset('group_link', chat_id, link)
            text = '''{}
{}'''.format(message['chat']['title'], link)
            bot.sendMessage(chat_id, text)
    if matches == 'newlink':
        if is_mod(message):
            link = r.hget('group_link', chat_id) or 'link not Found\ncreate new link with /newlink'
            text = '''{}
{}'''.format(message['chat']['title'], link)
            bot.sendMessage(chat_id, text)

    if matches == 'admins_set':
        if is_owner(message):
            admins = bot.getChatAdministrators(chat_id)
            bot.sendMessage(chat_id, ln['ingroup']['admins_set'])
            i = 1
            for x in admins:
                if x['status'] == 'administrator':
                    r.sadd('mod:{}'.format(chat_id), x['user']['id'])
                    text = str(ln['ingroup']['setowner']).format(x['user']['first_name'], x['user']['id'])
                    bot.sendMessage(chat_id, text, parse_mode='Markdown')
                    i = i + 1

    if matches[0] == 'setlang':
        if is_mod(message):
            r.hset('lang_gp', chat_id, matches[1])
            return [Message(chat_id).set_text(str(ln['ingroup']['setlang']).format(matches[1]))]

plugin = {
    "name": "ingroup",
    "desc": "ingroup",
    "usage": ["/ingroup"],
    "run": run,
    "sudo": False,
    "patterns": [
        "^[/#!](setowner)",
        "^[/#!](admin)$",
        "^[/#!](user)$",
        "^[/#!](title) (.*)$",
        "^[/#!](pin)$",
        "^[/#!](unpin)$",
        "^[/#!](ban)$",
        "^[/#!](ban) (.*)$",
        "^[/#!](avatar)$",
        "^[/#!](admins)$",
        "^[/#!](filter) (.*)",
        "^[/#!](unfilter) (.*)",
        "^[/#!](filters)$",
        "^[/#!](mute) (.*)$",
        "^[/#!](unmute)$",
        "^[/#!](unmute) (.*)$",
        "^[/#!](mute all)$",
        "^[/#!](unmute all)$",
        "^robot$",
        "^[/#!](link)$",
        "^[/#!](creator)$",
        "^[/#!](time)$",
        "^[/#!](admins_set)$",
        "^[/#!](setlang) (.*)$",
        "^[/#!](newlink)$"
    ]
}

