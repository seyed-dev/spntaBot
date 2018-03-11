# coding=utf-8
import asyncio
from telepot.namedtuple import InputTextMessageContent, InlineQueryResultArticle, InlineKeyboardMarkup,\
    InlineKeyboardButton
from message import Message
from bot import is_owner, is_sudo, is_mod, is_group, is_mod2
import telepot
import redis
import os
import re
import time
import urllib.request as ur
import json
r = redis.StrictRedis(host='localhost', port=6379, db=5, decode_responses=True)

bot = telepot.Bot('524062252:AAGVHYYvesW-bWoSvfGzgh7Jz2PI4tVdIOc')



@asyncio.coroutine
def run(message, matches, chat_id, step):
    response = Message(chat_id)
    if is_mod(message):
        ex = int(r.ttl('expire:{}'.format(chat_id))) - time.time()
        days = int(ex / 86400)
        key = [
            [
                InlineKeyboardButton(text='🔐 منوی قفل ها', callback_data='/locks'),
                InlineKeyboardButton(text='📝تنظیمات پیام', callback_data='/pmsetting'),
            ],
            [
                InlineKeyboardButton(text='👥لیست مدیران', callback_data='/admins'),
            ],
            [
                InlineKeyboardButton(text='روز {}'.format(days), callback_data='/expire'),
                InlineKeyboardButton(text='📆شارژ گروه', callback_data='/expire'),
            ],
            [
                InlineKeyboardButton(text='💡ورود به کانال راهنما💡', url='https://t.me/spntaHelp'),
            ]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=key)
        response.set_text("📋به پنل تنظیمات ربات خوش آمدید برای مدیریت گروه از کیبورد زیر استفاده کنید.("
                      "فقط ادمین های ربات در گروه قابلیت کار کردن با این کیبورد را دارند)",
                      parse_mode="Markdown", reply_markup=markup)
        return [response]


def tf(lock):
    if lock:
        return '✔️'
    else:
        return '✖️'


def tf2(lock):
    if lock:
        return '✖️'
    else:
        return '️✔'



@asyncio.coroutine
def callback(message, matches, chat_id):
    locks = {'lock_link': 'قفل لینک📎',
             'lock_username': 'قفل یوزرنیم[@]🔗',
             'lock_photo': 'قفل عکس🖼',
             'lock_doc': 'قفل گیف🌠',
             'lock_film': 'قفل فیلم🎥',
             'lock_music': 'قفل موزیک🎼',
             'lock_voice': 'قفل ویس🗣',
             'lock_game': 'قفل بازی🏓',
             'lock_doc': 'قفل فایل📁',
             'lock_contact': 'قفل مخاطب🔢',
             'lock_sticker': 'قفل استیکر🎭',
             'lock_bots': 'قفل ورود ربات🤖',
             'lock_fwd': 'قفل فوروارد 🔂',
             'lock_spam': 'قفل اسپم 👿',
             'lock_tg': 'قفل پیام ورود و خروج 🚶',
             'lock_loc': 'قفل لوکیشن(مکان)🗺',
             'lock_all': 'قفل گروه🔕',
             'lock_video_note': 'قفل ویدیو مسیج🤳'
             }
    query_id, from_id, data = telepot.glance(message, flavor='callback_query')
    if is_mod2(message['message'], message):
        if data == "/admins":
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

            key = [
                [
                    InlineKeyboardButton(text='🏛 منوی اصلی', callback_data='/back'),
                ]
            ]
            markup = InlineKeyboardMarkup(inline_keyboard=key)
            msgid = (chat_id, message[ 'message' ][ 'message_id' ])
            return Message(chat_id).edit_message(msgid, text, parse_mode="Markdown", reply_markup=markup)
        if data == '/back':
            text = "📋به پنل تنظیمات ربات خوش آمدید برای مدیریت گروه از کیبورد زیر استفاده کنید." \
                   "(فقط ادمین های ربات در گروه قابلیت کار کردن با این کیبورد را دارند)"
            ex = int(r.ttl('expire:{}'.format(chat_id))) - time.time()
            days = int(ex / 86400)
            key = [
                [
                    InlineKeyboardButton(text='🔐 منوی قفل ها', callback_data='/locks'),
                    InlineKeyboardButton(text='📝تنظیمات پیام', callback_data='/pmsetting'),
                ],
                [
                    InlineKeyboardButton(text='👥لیست مدیران', callback_data='/admins'),
                ],
                [
                    InlineKeyboardButton(text='روز {}'.format(days), callback_data='/expire'),
                    InlineKeyboardButton(text='📆شارژ گروه', callback_data='/expire'),
                ],
                [
                    InlineKeyboardButton(text='💡ورود به کانال راهنما💡', url='https://t.me/spntaHelp'),
                ]
            ]
            markup = InlineKeyboardMarkup(inline_keyboard=key)
            msgid = (chat_id, message[ 'message' ][ 'message_id' ])
            return Message(chat_id).edit_message(msgid, text, parse_mode="Markdown", reply_markup=markup)
        if data == '/pmsetting':
            get_spam = r.hget('get_spam', chat_id) or '10,1'
            value = get_spam.split(',')
            NUM_MAX = value[0]
            TIME_LIMIT = value[1]
            key = [
                [
                    InlineKeyboardButton(text='🔽 تعداد مجاز پیام در دقیقه 🔽', callback_data='hem')
                ],
                [
                    InlineKeyboardButton(text='➖', callback_data='spam_num_down'),
                    InlineKeyboardButton(text='{}'.format(NUM_MAX), callback_data='hem'),
                    InlineKeyboardButton(text='➕', callback_data='spam_num_up'),
                ],
                [
                    InlineKeyboardButton(text='               ', callback_data='hem')
                ],
                [
                    InlineKeyboardButton(text='🔽 تایم محدودیت کاربر(به دقیقه)🔽', callback_data='hem')
                ],
                [
                    InlineKeyboardButton(text='➖', callback_data='spam_time_down'),
                    InlineKeyboardButton(text='{}'.format(TIME_LIMIT), callback_data='hem'),
                    InlineKeyboardButton(text='➕', callback_data='spam_time_up'),
                ],
                [
                    InlineKeyboardButton(text='🏛 منوی اصلی', callback_data='/back'),
                ]

            ]
            text = 'منوی تنظیمات ارسال پیام🗯'
            markup = InlineKeyboardMarkup(inline_keyboard=key)
            msgid = (chat_id, message[ 'message' ][ 'message_id' ])
            return Message(chat_id).edit_message(msgid, text, parse_mode="Markdown", reply_markup=markup)
        spam = re.compile('spam_')
        if spam.search(data):
            pat = data.replace('spam_', '')
            if pat == 'time_down':
                getwww = r.hget('get_spam', chat_id) or '10,1'
                vvv = getwww.split(',')
                mmm = vvv[1]
                sss = vvv[0]
                num = int(mmm) - 1
                r.hset('get_spam', chat_id, '{},{}'.format(sss, num))
                get_spam = r.hget('get_spam', chat_id) or '10,1'
                value = get_spam.split(',')
                NUM_MAX = value[0]
                TIME_LIMIT = value[1]
                key = [
                    [
                        InlineKeyboardButton(text='🔽 تعداد مجاز پیام در دقیقه 🔽', callback_data='hem')
                    ],
                    [
                        InlineKeyboardButton(text='➖', callback_data='spam_num_down'),
                        InlineKeyboardButton(text='{}'.format(NUM_MAX), callback_data='hem'),
                        InlineKeyboardButton(text='➕', callback_data='spam_num_up'),
                    ],
                    [
                        InlineKeyboardButton(text='               ', callback_data='hem')
                    ],
                    [
                        InlineKeyboardButton(text='🔽 تایم محدودیت کاربر(به دقیقه)🔽', callback_data='hem')
                    ],
                    [
                        InlineKeyboardButton(text='➖', callback_data='spam_time_down'),
                        InlineKeyboardButton(text='{}'.format(num), callback_data='hem'),
                        InlineKeyboardButton(text='➕', callback_data='spam_time_up'),
                    ],
                    [
                        InlineKeyboardButton(text='🏛 منوی اصلی', callback_data='/back'),
                    ]

                ]
                text = '''منوی تنظیمات ارسال پیام🗯
(فقط ادمین های ربات در گروه قابلیت کار کردن با این کیبورد را دارند)

اخرین تغییرات :
👤 [{}](tg://user?id={})
├ `Pm setting`
└ `{} => {}`'''.format(message['from']['first_name'], message['from']['id'], pat, num)
                markup = InlineKeyboardMarkup(inline_keyboard=key)
                msgid = (chat_id, message['message']['message_id'])
                return Message(chat_id).edit_message(msgid, text, parse_mode="Markdown", reply_markup=markup)
            if pat == 'time_up':
                getwww = r.hget('get_spam', chat_id) or '10,1'
                vvv = getwww.split(',')
                mmm = vvv[1]
                sss = vvv[0]
                num = int(mmm) + 1
                r.hset('get_spam', chat_id, '{},{}'.format(sss, num))
                get_spam = r.hget('get_spam', chat_id) or '10,1'
                value = get_spam.split(',')
                NUM_MAX = value[0]
                TIME_LIMIT = value[1]
                key = [
                    [
                        InlineKeyboardButton(text='🔽 تعداد مجاز پیام در دقیقه 🔽', callback_data='hem')
                    ],
                    [
                        InlineKeyboardButton(text='➖', callback_data='spam_num_down'),
                        InlineKeyboardButton(text='{}'.format(NUM_MAX), callback_data='hem'),
                        InlineKeyboardButton(text='➕', callback_data='spam_num_up'),
                    ],
                    [
                        InlineKeyboardButton(text='               ', callback_data='hem')
                    ],
                    [
                        InlineKeyboardButton(text='🔽 تایم محدودیت کاربر(به دقیقه)🔽', callback_data='hem')
                    ],
                    [
                        InlineKeyboardButton(text='➖', callback_data='spam_time_down'),
                        InlineKeyboardButton(text='{}'.format(num), callback_data='hem'),
                        InlineKeyboardButton(text='➕', callback_data='spam_time_up'),
                    ],
                    [
                        InlineKeyboardButton(text='🏛 منوی اصلی', callback_data='/back'),
                    ]

                ]
                text = '''منوی تنظیمات ارسال پیام🗯
(فقط ادمین های ربات در گروه قابلیت کار کردن با این کیبورد را دارند)

اخرین تغییرات :
👤 [{}](tg://user?id={})
├ `Pm setting`
└ `{} => {}`'''.format(message['from']['first_name'], message['from']['id'], pat, num)
                markup = InlineKeyboardMarkup(inline_keyboard=key)
                msgid = (chat_id, message['message']['message_id'])
                return Message(chat_id).edit_message(msgid, text, parse_mode="Markdown", reply_markup=markup)
            if pat == 'num_down':
                getwww = r.hget('get_spam', chat_id) or '10,1'
                vvv = getwww.split(',')
                mmm = vvv[0]
                sss = vvv[1]
                num = int(mmm) - 1
                r.hset('get_spam', chat_id, '{},{}'.format(num, sss))
                get_spam = r.hget('get_spam', chat_id) or '10,1'
                value = get_spam.split(',')
                NUM_MAX = value[0]
                TIME_LIMIT = value[1]
                key = [
                    [
                        InlineKeyboardButton(text='🔽 تعداد مجاز پیام در دقیقه 🔽', callback_data='hem')
                    ],
                    [
                        InlineKeyboardButton(text='➖', callback_data='spam_num_down'),
                        InlineKeyboardButton(text='{}'.format(num), callback_data='hem'),
                        InlineKeyboardButton(text='➕', callback_data='spam_num_up'),
                    ],
                    [
                        InlineKeyboardButton(text='               ', callback_data='hem')
                    ],
                    [
                        InlineKeyboardButton(text='🔽 تایم محدودیت کاربر(به دقیقه)🔽', callback_data='hem')
                    ],
                    [
                        InlineKeyboardButton(text='➖', callback_data='spam_time_down'),
                        InlineKeyboardButton(text='{}'.format(TIME_LIMIT), callback_data='hem'),
                        InlineKeyboardButton(text='➕', callback_data='spam_time_up'),
                    ],
                    [
                        InlineKeyboardButton(text='🏛 منوی اصلی', callback_data='/back'),
                    ]

                ]
                text = '''منوی تنظیمات ارسال پیام🗯
(فقط ادمین های ربات در گروه قابلیت کار کردن با این کیبورد را دارند)

اخرین تغییرات :
👤 [{}](tg://user?id={})
├ `Pm setting`
└ `{} => {}`'''.format(message['from']['first_name'], message['from']['id'], pat, num)
                markup = InlineKeyboardMarkup(inline_keyboard=key)
                msgid = (chat_id, message['message']['message_id'])
                return Message(chat_id).edit_message(msgid, text, parse_mode="Markdown", reply_markup=markup)
            if pat == 'num_up':
                getwww = r.hget('get_spam', chat_id) or '10,1'
                vvv = getwww.split(',')
                mmm = vvv[0]
                sss = vvv[1]
                num = int(mmm) + 1
                r.hset('get_spam', chat_id, '{},{}'.format(num, sss))
                get_spam = r.hget('get_spam', chat_id) or '10,1'
                value = get_spam.split(',')
                NUM_MAX = value[0]
                TIME_LIMIT = value[1]
                key = [
                    [
                        InlineKeyboardButton(text='🔽 تعداد مجاز پیام در دقیقه 🔽', callback_data='hem')
                    ],
                    [
                        InlineKeyboardButton(text='➖', callback_data='spam_num_down'),
                        InlineKeyboardButton(text='{}'.format(num), callback_data='hem'),
                        InlineKeyboardButton(text='➕', callback_data='spam_num_up'),
                    ],
                    [
                        InlineKeyboardButton(text='               ', callback_data='hem')
                    ],
                    [
                        InlineKeyboardButton(text='🔽 تایم محدودیت کاربر(به دقیقه)🔽', callback_data='hem')
                    ],
                    [
                        InlineKeyboardButton(text='➖', callback_data='spam_time_down'),
                        InlineKeyboardButton(text='{}'.format(TIME_LIMIT), callback_data='hem'),
                        InlineKeyboardButton(text='➕', callback_data='spam_time_up'),
                    ],
                    [
                        InlineKeyboardButton(text='🏛 منوی اصلی', callback_data='/back'),
                    ]

                ]
                text = '''منوی تنظیمات ارسال پیام🗯
(فقط ادمین های ربات در گروه قابلیت کار کردن با این کیبورد را دارند)

اخرین تغییرات :
👤 [{}](tg://user?id={})
├ `Pm setting`
└ `{} => {}`'''.format(message['from']['first_name'], message['from']['id'], pat, num)
                markup = InlineKeyboardMarkup(inline_keyboard=key)
                msgid = (chat_id, message['message']['message_id'])
                return Message(chat_id).edit_message(msgid, text, parse_mode="Markdown", reply_markup=markup)

        if data == '/locks':
            key = []
            for lock in locks:
                key.append(
                    [
                        InlineKeyboardButton(text=r.hget(lock, chat_id) and '«✔️»' or '«✖️»', callback_data='/'+lock),
                        InlineKeyboardButton(text=locks[lock], callback_data='/'+lock)
                    ]
                )
            key.append(
                [
                    InlineKeyboardButton(text='🏛 منوی اصلی', callback_data='/back'),
                ]
            )
            markey = InlineKeyboardMarkup(inline_keyboard=key)


            text = 'برای تغییر حالت قفل بر روی آن کلیک کنید👌'
            msgid = (chat_id, message[ 'message' ][ 'message_id' ])
            return Message(chat_id).edit_message(msgid, text, parse_mode="Markdown", reply_markup=markey)

        if matches[0] == 'lock_':
            l = matches[0]+matches[1]
            text = '''📋به پنل تنظیمات ربات خوش آمدید برای مدیریت گروه از کیبورد زیر استفاده کنید.
(فقط ادمین های ربات در گروه قابلیت کار کردن با این کیبورد را دارند)

اخرین تغییرات :
👤 [{}](tg://user?id={})
 ├ `settings changed`
 └ `{} =>'''.format(message['from']['first_name'], message['from']['id'], l)
            key = []
            for lock in locks:
                if lock == l:
                    if r.hget(lock, chat_id):
                        r.hdel(lock, chat_id)
                        text += ' OFF`'
                        status = '«✖️»'
                        bot.answerCallbackQuery(query_id, 'غیر فعال شد✖️')
                    else:
                        r.hset(lock, chat_id, True)
                        text += ' ON`'
                        status = '«✔️»'
                        bot.answerCallbackQuery(query_id, 'فعال شد ✔️')
                else:
                    status = r.hget(lock, chat_id) and '«✔️»' or '«✖️»'
                key.append(
                    [
                        InlineKeyboardButton(text=status, callback_data='/'+lock),
                        InlineKeyboardButton(text=locks[lock], callback_data='/'+lock)
                    ]
                )
            key.append(
                [
                    InlineKeyboardButton(text='🏛 منوی اصلی', callback_data='/back'),
                ]
            )
            markey = InlineKeyboardMarkup(inline_keyboard=key)
            msgid = (chat_id, message['message']['message_id'])
            return Message(chat_id).edit_message(msgid, text, parse_mode="Markdown", reply_markup=markey)


plugin = {
    "name": "Panel",
    "desc": "Show This Message!",
    "usage": ["/panel"],
    "run": run,
    "sudo": False,
    "callback": callback,
    "callback_patterns": [
        "^[!/#]admins$",
        "^[!/#]back$",
        "^[/#!]locks$",
        "^[/#!]pmsetting$",
        "^spam_(.*)",
        "^/(lock_)(.*)$"
    ],
    "patterns": [
        "^[!/#]panel",
    ]
}