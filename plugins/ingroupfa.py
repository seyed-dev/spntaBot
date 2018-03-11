import asyncio
from telepot.namedtuple import InputTextMessageContent, InlineQueryResultArticle
from message import Message
from bot import is_owner, is_sudo, is_mod, is_group
import telepot
import redis
import os
import re
import time
from datetime import datetime
import pytz
r = redis.StrictRedis(host='localhost', port=6379, db=5, decode_responses=True)

bot = telepot.Bot('524062252:AAGVHYYvesW-bWoSvfGzgh7Jz2PI4tVdIOc')


@asyncio.coroutine
def run(message, matches, chat_id, step):
    if matches == 'setowner':
        if 'reply_to_message' in message:
            if is_sudo(message):
                r.hset('owner', chat_id, message['reply_to_message']['from']['id'])
                r.hset('owner:{}'.format(chat_id), message['reply_to_message']['from']['id'], True)
                text= 'کاربر [{}](tg://user?id={}) ادمین اصلی ربات در گروه شد👤'.\
                    format(message['reply_to_message']['from']['first_name'],
                     message['reply_to_message']['from']['id'])
                bot.sendMessage(chat_id, text, parse_mode='Markdown')
    if matches == 'ادمین':
        if 'reply_to_message' in message:
            if is_owner(message):
                r.sadd('mod:{}'.format(chat_id), message['reply_to_message']['from']['id'])
                text= 'کاربر [{}](tg://user?id={}) ادمین ربات در گروه شد👤'.\
                    format(message['reply_to_message']['from']['first_name'],
                     message['reply_to_message']['from']['id'])
                bot.sendMessage(chat_id, text, parse_mode='Markdown')
    if matches == 'کاربر':
        if 'reply_to_message' in message:
            if is_owner(message):
                r.srem('mod:{}'.format(chat_id), message['reply_to_message']['from']['id'])
                text= 'کاربر [{}](tg://user?id={}) از این به بعد یک کاربر معمولی میباشد👌'.\
                    format(message['reply_to_message']['from']['first_name'],
                     message['reply_to_message']['from']['id'])
                bot.sendMessage(chat_id, text, parse_mode='Markdown')
    if matches[0] == 'عنوان' and matches[1]:
        if is_mod(message):
            try:
                set = bot.setChatTitle(chat_id, matches[1])
                bot.sendMessage(chat_id, 'نام گروه با موفقیت تغییر یافت✅', reply_to_message_id=message['message_id'])
            except:
                bot.sendMessage(chat_id, 'ربات ادمین نیست 🤔')
    if matches == 'پین':
        if is_mod(message):
            if 'reply_to_message' in message:
                bot.pinChatMessage(chat_id, message['reply_to_message']['message_id'])
                bot.sendMessage(chat_id, 'سنجاق شد📌', reply_to_message_id=message['reply_to_message']['message_id'])
    if matches == 'حذف پین':
        if is_mod(message):
            bot.unpinChatMessage(chat_id)
            bot.sendMessage(chat_id, 'سنجاق گروه برداشته شد📌')
    if matches == 'اخراج':
        if is_mod(message):
            if 'reply_to_message' in message:
                user = message['reply_to_message']
                if not is_mod(user):
                    bot.kickChatMember(chat_id, user['from']['id'])
                    bot.sendMessage(chat_id, 'کاربر [{}](tg://user?id={}) از گروه اخراج شد❌'.
                                    format(user['from']['first_name'], user['from']['id']), parse_mode='Markdown')
                    bot.sendMessage(r.hget('owner', chat_id), '''کاربر [{}](tg://user?id={}) از گروه {} اخراج شد❌
اخراج کننده :  [{}](tg://user?id={})
'''.format(user['from']['first_name'], user['from']['id'], message['chat']['title'],
           message['from']['first_name'], message['from']['id']), parse_mode='Markdown')
                else:
                    bot.sendMessage(chat_id, 'شما نمیتوانید ادمین را اخراج کنید🙄')
    if matches[0] == 'اخراج':
        if is_mod(message):
            user = str(matches[1])
            bot.kickChatMember(chat_id, user)
            bot.sendMessage(chat_id, 'کاربر {} از گروه اخراج شد❌'.format(user))
            bot.sendMessage(r.hget('owner', chat_id), '''کاربر [{}](tg://user?id={}) از گروه {} اخراج شد❌
اخراج کننده :  [{}](tg://user?id={})
'''.format(user, user, message['chat']['title'], message['from']['id'], message['from']['id']), parse_mode='Markdown')
    if matches == 'آواتار':
        if is_mod(message):
            try:
                bot.download_file(message['reply_to_message']['photo'][1]['file_id'], '{}.jpg'.format(chat_id))
                bot.setChatPhoto(chat_id, open('{}.jpg'.format(chat_id), 'rb'))
                os.remove('{}.jpg'.format(chat_id))
            except Exception as e:
                bot.sendMessage(chat_id, '#Error:\n{}'.format(e),
                                reply_to_message_id=message['reply_to_message']['message_id'])
    if matches == 'لیست ادمین':
        if is_mod(message):
            owner = r.hget('owner', chat_id)
            if owner:
                oner = '[{}](tg://user?id={})'.format(owner, owner)
            else:
                oner = 'وجود ندارد❌'
            mods = r.smembers('mod:{}'.format(chat_id))
            if mods:
                mod = ''
                for x in mods:
                    mod += '\n>[{}](tg://user?id={})'.format(x, x)
            else:
                mod = 'وجود ندارد❌'

            text = '''👤 ادمین اصلی : {}

👥 سایر ادمین ها :
{}'''.format(oner, mod)
            bot.sendMessage(chat_id, text, parse_mode='Markdown')
    if matches[0] == 'فیلتر':
        if is_mod(message):
            text = message['text'].replace(matches[0], '').replace('/ ', '').replace('# ', '').replace('! ', '')
            lines = re.findall('[^\n]+', text)
            fil = ''
            for x in lines:
                r.sadd('filter:{}'.format(chat_id), x)
                fil += '\n>{}'.format(x)
            bot.sendMessage(chat_id, '''☠️کلمات زیر به لیست فیلتر افزوده شدند :
{}'''.format(fil))
    if matches[0] == 'حذف':
        if is_mod(message):
            text = message['text'].replace(matches[0], '').replace('/ ', '').replace('# ', '').replace('! ', '')
            lines = re.findall('[^\n]+', text)
            fil = ''
            for x in lines:
                r.srem('filter:{}'.format(chat_id), x)
                fil += '\n>{}'.format(x)
            bot.sendMessage(chat_id, '''☠️کلمات زیر از لیست فیلتر حذف شدند :
{}'''.format(fil))
    if matches == 'لیست فیلتر':
        if is_mod(message):
            filters = r.smembers('filter:{}'.format(chat_id))
            text = ''
            for x in filters:
                text += '\n>{}'.format(x)
            bot.sendMessage(chat_id, '''🤐لیست کلمات فیلتر شده :
{}'''.format(text))
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
                    bot.sendMessage(chat_id, 'کاربر [{}](tg://user?id={})'
                                             ' به مدت {} روز نمیتواند در گروه پیامی ارسال کند😕'
                                    .format(name, user['from']['id'], matches[1]), parse_mode='Markdown')

                else:
                    bot.sendMessage(chat_id, 'ادمینه 🤧')
    if matches == 'unmute':
        if is_mod(message):
            if 'reply_to_message' in message:
                user = message['reply_to_message']
                bot.restrictChatMember(chat_id, user['from']['id'],
                                       can_send_messages=True, can_send_media_messages=True,
                                       can_send_other_messages=True, can_add_web_page_previews=True)
                bot.sendMessage(chat_id, 'آزاد شد :)')
    if matches[0] == 'unmute':
        if is_mod(message):
            if 'reply_to_message' in message:
                bot.restrictChatMember(chat_id, matches[1],
                                       can_send_messages=True, can_send_media_messages=True,
                                       can_send_other_messages=True, can_add_web_page_previews=True)
                bot.sendMessage(chat_id, 'آزاد شد :)')
    if matches[0] == 'قفل' and matches[1] == 'گروه':
        if is_mod(message):
            if r.hget('lock_all', chat_id):
                bot.sendMessage(chat_id, 'قفل گروه از قبل فعال بوده است✔️')
            else:
                r.hset('lock_all', chat_id, True)
                bot.sendMessage(chat_id,  'گروه قفل شد✔️')
                bot.sendDocument(chat_id, open('tmp/mute.gif', 'rb'), caption='''#گروه_تعطیل_است
#چیزی_ارسال_نکنید_چون
#توسط_ربات_حذف_خواهد_شد
@spntaBot''')
    if matches[0] == 'بازکردن' and matches[1] == 'گروه':
        if is_mod(message):
            if r.hget('lock_all', chat_id):
                r.hdel('lock_all', chat_id)
                bot.sendMessage(chat_id, 'قفل گروه باز شد✅')
            else:
                bot.sendMessage(chat_id, 'گروه قفل نبوده ک 🙄')
    if matches == 'ربات':
        txt = '[{} هستم 🐣](tg://user?id={})'.format(message['from']['first_name'], message['from']['id'])
        bot.sendMessage(chat_id, txt, parse_mode='Markdown')
    if matches == 'link':
        link = bot.exportChatInviteLink(chat_id)
        text = '''{}
{}'''.format(message['chat']['title'], link)
        bot.sendMessage(chat_id, text)
    if matches == 'سازنده':
        if is_sudo(message):
            admins = bot.getChatAdministrators(chat_id)
            for x in admins:
                if x['status'] == 'creator':
                    print(x)
                    r.hset('owner', chat_id, x['user']['id'])
                    r.hset('owner:{}'.format(chat_id), x['user']['id'], True)
                    text = 'کاربر [{}](tg://user?id={}) ادمین اصلی گروه است'. \
                        format(x['user']['first_name'], x['user']['id'])
                    bot.sendMessage(chat_id, text, parse_mode='Markdown')
    if matches == 'ساعت':
        now = datetime.now(pytz.timezone("Asia/Tehran")).strftime("%H:%M:%S")
        bot.sendMessage(chat_id, now)



plugin = {
    "name": "ingroup",
    "desc": "ingroup",
    "usage": ["/ingroup"],
    "run": run,
    "sudo": False,
    "patterns": [
        "^(setowner)",
        "^#(ادمین)$",
        "^#(کاربر)$",
        "^#(عنوان) (.*)$",
        "^(پین)$",
        "^(حذف پین)$",
        "^#(اخراج)$",
        "^#(اخراج) (.*)$",
        "^(آواتار)$",
        "^(لیست ادمین)$",
        "^#(فیلتر) (.*)",
        "^#(حذف) (.*)",
        "^#(لیست فیلتر)$",
        "^(mute) (.*)$",
        "^(unmute)$",
        "^(unmute) (.*)$",
        "^(قفل) (گروه)$",
        "^(بازکردن) (گروه)$",
        "^ربات$",
        "^(لینک)$",
        "^#(سازنده)$",
        "^(ساعت)$",
    ]
}