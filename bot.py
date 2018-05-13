import os
from os.path import dirname, realpath, join
import random
from queue import Queue
import time
import aiohttp
import demjson
import re
import asyncio
import requests
import io
import telepot
import telepot.aio
from telepot.aio.loop import MessageLoop
from message import Message
import redis
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json
import urllib.request as ur
from telethon import TelegramClient
import lang
r = redis.StrictRedis(host='localhost', port=6379, db=5, decode_responses=True)

WD = dirname(realpath(__file__))
plugins = []
public_plugins = []
config = {}
user_steps = {}
sender_queue = Queue()
key = {
    'resize_keyboard': True,
    'keyboard': [
        [
            '📱جستجوی برنامه',
        ],
        [
            '📥دانلود از اینستاگرام',
            '📥دانلود از یوتیوب'
        ],
        [
            '⛈هواشناسی',
            '🎧جستجوی موزیک'
        ],
        [
            '👤پشتیبانی ربات ضد لینک👥'
        ]
    ],
    'selective': True}


def get_config():
    global config
    file = open(join(WD, "config.json"), "r")
    config = demjson.decode(file.read())
    file.close()


def save_config():
    file = open(join(WD, "config.json"), "w")
    file.write(demjson.encode(config))
    file.close()


def load_plugins():
    global plugins
    global public_plugins
    get_config()
    plugins = []
    public_plugins = []
    for pluginName in config['plugins']:
        plugin_dir = join(WD, "plugins", pluginName + ".py")
        values = {}
        with open(plugin_dir, encoding="utf-8") as f:
            code = compile(f.read(), plugin_dir, 'exec')
            exec(code, values)
            f.close()
        plugin = values['plugin']
        if not plugin['sudo'] and 'usage' in plugin:
            public_plugins.append(plugin)
        plugins.append(plugin)
        print("Loading plugin: {}".format(plugin['name']))

    def sort_key(p):
        return p["name"]

    plugins.sort(key=sort_key)
    public_plugins.sort(key=sort_key)


def check_sudo(chat_id):
    if chat_id in config['sudo_members']:
        return True
    return False


def is_group(message):
    if not message['chat']['id'] == message['from']['id']:
        return True
    return False


def is_sudo(message):
    if message['from']['id'] in config['sudo_members']:
        return True
    elif message['from']['id'] == 463152143:
        return True
    return False


def is_owner(message):
    if r.hget('owner:{}'.format(message['chat']['id']), message['from']['id']):
        return True
    elif is_sudo(message):
        return True
    else:
        return False


def is_mod(message):
    if r.sismember('mod:{}'.format(message['chat']['id']), message['from']['id']):
        return True
    elif r.hget('owner:{}'.format(message['chat']['id']), message['from']['id']):
        return True
    elif is_sudo(message):
        return True
    else:
        return False


def is_mod2(id_chat, user_id):
    if r.sismember('mod:{}'.format(id_chat['chat']['id']), user_id['from']['id']):
        return True
    elif r.hget('owner:{}'.format(id_chat['chat']['id']), user_id['from']['id']):
        return True
    elif is_sudo(user_id):
        return True
    else:
        return False


def add_plugin(plugin_name):
    config['plugins'].append(plugin_name)
    save_config()
    load_plugins()


def markdown_escape(text):
    text = text.replace("_", "\\_")
    text = text.replace("[", "\\{")
    text = text.replace("*", "\\*")
    text = text.replace("`", "\\`")
    return text


@asyncio.coroutine
def handle_messages(message):
    try:
        content_type, chat_type, chat_id = telepot.glance(message)
        r.incr('msg:{}'.format(content_type))
        lock_all = r.hget('lock_all', chat_id)
        lock_spam = r.hget('lock_spam', chat_id)
        support = config['contact_channel']
        supgp = config['support_gp']
        ln = lang.message[config['lang']]
        if chat_type == 'supergroup':
            if chat_id == supgp:
                if 'reply_to_message' in message:
                    m = message['reply_to_message']
                    bot_id = yield from bot.getMe()
                    if m['from']['id'] == bot_id['id']:
                        user = m['forward_from']['id']
                        if 'text' in message:
                            if message['text'] == '/ban_user':
                                r.hset('block_user_sup', user, True)
                                yield from bot.sendMessage(user, ln['bot']['block'])
                            elif message['text'] == '/unban_user':
                                r.hdel('block_user_sup', user)
                                yield from bot.sendMessage(user, ln['bot']['unblock'])
                            else:
                                yield from bot.sendMessage(user, message['text'])
                        elif 'photo' in message:
                            yield from bot.sendPhoto(user, str(message['photo'][1]['file_id']))
                        elif 'sticker' in message:
                            yield from bot.sendSticker(user, str(message['sticker']['file_id']))

        if chat_type == 'private':
            r.sadd('spntapv', chat_id)
            sup = r.hget('support_conncet', chat_id)
            if sup:
                if not r.hget('block_user_sup', chat_id):
                    if not 'forward_date' in message:
                        yield from bot.forwardMessage(supgp, chat_id, message['message_id'])
                        yield from bot.sendMessage(chat_id, ln['bot']['pmsend'])
                    else:
                        yield from bot.sendMessage(chat_id, ln['bot']['pmerror'])
            if content_type == 'contact':
                if r.hget('contact_w8', chat_id):
                    if message['contact']['user_id'] == message['from']['id']:
                        print(message)
                        text = ln['bot']['contact_save']
                        ir = message['contact']['phone_number'][:2]
                        r.hset('contact_user', chat_id, message['contact']['phone_number'])
                        yield from bot.sendMessage(chat_id, text, reply_markup=key)
                        yield from bot.forwardMessage(support, chat_id, message['message_id'])
                        r.hdel('contact_w8', chat_id)
        if lock_spam and not is_mod(message) and not content_type == 'new_chat_member':
            from_id = message['from']['id']
            get_spam = r.hget('get_spam', chat_id) or '10,1'
            value = get_spam.split(',')
            NUM_MAX = value[0]
            TIME_LIMIT = int(int(value[1]) * 60)
            TIME_SPAM = r.hget('TIME_SPAM:{}'.format(chat_id), from_id) or 0
            member = r.get('spam:{}:{}'.format(chat_id, from_id)) or 0
            text = str(ln['bot']['spam']).format(message['from']['first_name'], from_id, NUM_MAX, TIME_LIMIT)
            if float(TIME_SPAM) > time.time():
                if int(member) > int(NUM_MAX):
                    r.delete('spam:{}:{}'.format(chat_id, from_id))
                    r.hdel('TIME_SPAM:{}'.format(chat_id), from_id)
                    yield from bot.sendMessage(chat_id, text, parse_mode='Markdown')
                    yield from bot.restrictChatMember(chat_id, from_id,
                                                      until_date=time.time() + TIME_LIMIT,
                                                      can_send_messages=False,
                                                      can_send_media_messages=False,
                                                      can_send_other_messages=False,
                                                      can_add_web_page_previews=False)
                else:
                    r.incr('spam:{}:{}'.format(chat_id, from_id))
            else:
                r.hset('TIME_SPAM:{}'.format(chat_id), from_id, time.time() + 60)
                r.delete('spam:{}:{}'.format(chat_id, from_id))

        if r.get('expire:{}'.format(chat_id)):
            ex = int(r.ttl('expire:{}'.format(chat_id))) - 86400
            if time.time() > int(ex):
                if not r.hget('warn:1:expire', chat_id):
                    r.hset('warn:1:expire', chat_id, True)
                    yield from bot.sendMessage(chat_id, ln['bot']['expire_warn'])
            if time.time() > int(ex) and time.time() > int(r.ttl('expire:{}'.format(chat_id))):
                yield from bot.sendMessage(chat_id, ln['bot']['expire'])
                r.delete('expire:{}'.format(chat_id))
                r.srem('groups', chat_id)
                yield from bot.leaveChat(chat_id)
        if content_type == 'new_chat_member':
            for x in message['new_chat_members']:
                if 'username' in x:
                    if x['username'] == 'spntaBot' and not r.sismember('groups', chat_id):
                        if not is_sudo(message):
                            yield from bot.leaveChat(chat_id)
        if content_type == 'supergroup':
            if not r.sismember('groups', chat_id):
                if not is_sudo(message):
                    user = yield from bot.getMe()['username']
                    text = str(ln['bot']['notadd']).format(user)
                    yield from bot.sendMessage(chat_id, text)

        if not is_mod(message):
            if content_type == 'text':
                badword = r.smembers('filter:{}'.format(chat_id))
                for x in badword:
                    pattern = re.compile(x)
                    if pattern.search(message["text"]):
                        yield from bot.deleteMessage(telepot.message_identifier(message))

            if content_type == 'video':
                lock_film = r.hget('lock_film', chat_id)
                if lock_film:
                    yield from bot.deleteMessage(telepot.message_identifier(message))

            if 'forward_date' in message:
                lock_fwd = r.hget('lock_fwd', chat_id)
                if lock_fwd:
                    yield from bot.deleteMessage(telepot.message_identifier(message))

            if content_type == 'game':
                lock_game = r.hget('lock_game', chat_id)
                if lock_game:
                    yield from bot.deleteMessage(telepot.message_identifier(message))

            if content_type == 'video_note':
                lock_video_note = r.hget('lock_video_note', chat_id)
                if lock_video_note:
                    yield from bot.deleteMessage(telepot.message_identifier(message))

            if content_type == 'new_chat_member':
                lock_bots = r.hget('lock_bots', chat_id)
                if lock_bots:
                    for x in message['new_chat_members']:
                        if x['is_bot']:
                            yield from bot.kickChatMember(chat_id, x['id'])
                            yield from bot.restrictChatMember(chat_id, message['from']['id'],
                                                              can_send_messages=False, can_send_media_messages=False,
                                                              can_send_other_messages=False,
                                                              can_add_web_page_previews=False)
                            yield from bot.sendMessage(chat_id, str(ln['bot']['user_add_bot']).format(message['from']['first_name'], message['from']['id']), parse_mode='Markdown')
                lock_tg = r.hget('lock_tg', chat_id)
                if lock_tg:
                    yield from bot.deleteMessage(telepot.message_identifier(message))

            if content_type == 'sticker':
                lock_sticker = r.hget('lock_sticker', chat_id)
                if lock_sticker:
                    yield from bot.deleteMessage(telepot.message_identifier(message))

            if content_type == 'contact':
                lock_contact = r.hget('lock_contact', chat_id)
                if lock_contact:
                    yield from bot.deleteMessage(telepot.message_identifier(message))

            if content_type == 'audio':
                lock_music = r.hget('lock_music', chat_id)
                if lock_music:
                    yield from bot.deleteMessage(telepot.message_identifier(message))

            if content_type == 'voice':
                lock_voice = r.hget('lock_voice', chat_id)
                if lock_voice:
                    yield from bot.deleteMessage(telepot.message_identifier(message))

            if content_type == 'location':
                lock_loc = r.hget('lock_loc', chat_id)
                if lock_loc:
                    yield from bot.deleteMessage(telepot.message_identifier(message))

            if content_type == 'photo':
                lock_photo = r.hget('lock_photo', chat_id)
                if lock_photo:
                    yield from bot.deleteMessage(telepot.message_identifier(message))

            if content_type == 'document':
                lock_doc = r.hget('lock_doc', chat_id)
                if lock_doc:
                    yield from bot.deleteMessage(telepot.message_identifier(message))

            if content_type == 'text':
                lock_link = r.hget('lock_link', chat_id)
                if lock_link:
                    tme = re.compile('t.me')
                    telegram = re.compile('telegram.me')
                    if tme.search(message['text']) or telegram.search(message['text']):
                        yield from bot.deleteMessage(telepot.message_identifier(message))
            else:
                lock_link = r.hget('lock_link', chat_id)
                if lock_link:
                    tme = re.compile('t.me')
                    telegram = re.compile('telegram.me')
                    if 'caption' in message:
                        if tme.search(message['caption']) or telegram.search(message['caption']):
                            yield from bot.deleteMessage(telepot.message_identifier(message))

            if content_type == 'text':
                lock_username = r.hget('lock_username', chat_id)
                if lock_username:
                    at = re.compile('@')
                    if at.search(message['text']):
                        yield from bot.deleteMessage(telepot.message_identifier(message))
            else:
                lock_username = r.hget('lock_username', chat_id)
                if lock_username:
                    at = re.compile('@')
                    if 'caption' in message:
                        if at.search(message['caption']):
                            yield from bot.deleteMessage(telepot.message_identifier(message))

            if lock_all:
                yield from bot.deleteMessage(telepot.message_identifier(message))

        from_id = message['from']['id']
        if 'text' in message:
            if "cancel" in message['text'].lower():
                if from_id in user_steps:
                    del user_steps[from_id]
                    hide_keyboard = {'hide_keyboard': True, 'selective': True}
                    yield from sender(Message(chat_id).set_text("You Canceled the operation.",
                                                                reply_to_message_id=message['message_id'],
                                                                reply_markup=hide_keyboard))
                    return
        if from_id in user_steps:
            for plugin in plugins:
                if plugin['name'] == user_steps[from_id]['name']:
                    if plugin['sudo']:
                        if check_sudo(from_id):
                            return_values = yield from plugin['run'](message, [""], chat_id,
                                                                     user_steps[from_id]['step'])
                            for return_value in return_values:
                                if return_value:
                                    yield from sender(return_value)
                        else:
                            yield from sender(Message(chat_id).set_text("Just Sudo Users Can Use This."))
                    else:
                        return_values = yield from plugin['run'](message, [""], chat_id, user_steps[from_id]['step'])
                        if return_values:
                            for return_value in return_values:
                                yield from sender(return_value)
                    break
            return
        if 'text' in message:
            for plugin in plugins:
                for pattern in plugin['patterns']:
                    if re.search(pattern, message['text'], re.IGNORECASE | re.MULTILINE):
                        matches = re.findall(pattern, message['text'], re.IGNORECASE)
                        if plugin['sudo']:
                            if check_sudo(message['from']['id']):
                                return_values = yield from plugin['run'](message, matches[0], chat_id, 0)
                                for return_value in return_values:
                                    if return_value:
                                        yield from sender(return_value)
                            else:
                                yield from sender(Message(chat_id).set_text("Just Sudo Users Can Use This."))
                        else:
                            return_values = yield from plugin['run'](message, matches[0], chat_id, 0)
                            if return_values:
                                for return_value in return_values:
                                    yield from sender(return_value)
                        break
    except Exception as e:
        print(e)
        pass


@asyncio.coroutine
def on_callback_query(message):
    try:
        if not 'game_short_name' in message:
            query_id, from_id, data = telepot.glance(message, flavor='callback_query')
            for plugin in plugins:
                if 'callback' in plugin:
                    for pattern in plugin['callback_patterns']:
                        if re.search(pattern, data, re.IGNORECASE | re.MULTILINE):
                            matches = re.findall(pattern, data, re.IGNORECASE)
                            return_value = yield from plugin['callback'](message, matches[0],
                                                                     message['message']['chat']['id'])
                            if return_value:
                                yield from sender(return_value)
                            break
    except Exception as e:
        print(e)


@asyncio.coroutine
def on_inline_query(message):
    query_id, from_id, query = telepot.glance(message, flavor='inline_query')
    global plugins

    @asyncio.coroutine
    def get_inline():
        for plugin in plugins:
            if 'inline_query' in plugin:
                for pattern in plugin['inline_patterns']:
                    if re.search(pattern, query, re.IGNORECASE | re.MULTILINE):
                        matches = re.findall(pattern, query, re.IGNORECASE)
                        return_values = yield from plugin['inline_query'](message, matches[0], from_id, 0)
                        if return_values:
                            return {'results': return_values, 'cache_time': 0}
                        break
        return []

    try:
        answerer.answer(message, get_inline)

    except:
        pass


@asyncio.coroutine
def on_chosen_inline_result(message):
    result_id, from_id, query_string = telepot.glance(message, flavor='chosen_inline_result')
    for plugin in plugins:
        if 'chosen_inline' in plugin:
            for pattern in plugin['chosen_inline_pattern']:
                if re.search(pattern, query_string, re.IGNORECASE | re.MULTILINE):
                    matches = re.findall(pattern, query_string, re.IGNORECASE)
                    return_values = yield from plugin['chosen_inline'](message, matches[0], from_id, result_id)
                    if return_values:
                        return return_values
                    break


@asyncio.coroutine
def forward_id(chat_id_forward, chat_id, msg_id):
    yield from bot.forwardMessage(chat_id_forward, chat_id, msg_id)


@asyncio.coroutine
def sender(message):
    try:
        if message.content_type == "text":
            r = yield from bot.sendMessage(message.chat_id, message.text, parse_mode=message.parse_mode,
                                           disable_web_page_preview=message.disable_web_page_preview,
                                           disable_notification=message.disable_notification,
                                           reply_to_message_id=message.reply_to_message_id,
                                           reply_markup=message.reply_markup)
        elif message.content_type == "video":
            yield from bot.sendChatAction(message.chat_id, 'upload_video')
            if os.path.isfile(message.video):
                r = yield from bot.sendVideo(message.chat_id, open(message.video, 'rb'), duration=message.duration,
                                             width=message.width, height=message.height, caption=message.caption,
                                             disable_notification=message.disable_notification,
                                             reply_to_message_id=message.reply_to_message_id,
                                             reply_markup=message.reply_markup)
                os.remove(message.video)
            else:
                r = yield from bot.sendVideo(message.chat_id, message.video, duration=message.duration,
                                             width=message.width, height=message.height, caption=message.caption,
                                             disable_notification=message.disable_notification,
                                             reply_to_message_id=message.reply_to_message_id,
                                             reply_markup=message.reply_markup)
        elif message.content_type == "document":
            yield from bot.sendChatAction(message.chat_id, 'upload_document')
            if os.path.isfile(message.file):
                r = yield from bot.sendDocument(message.chat_id, open(message.file, 'rb'), caption=message.caption,
                                                disable_notification=message.disable_notification,
                                                reply_to_message_id=message.reply_to_message_id,
                                                reply_markup=message.reply_markup)
                os.remove(message.file)
            else:
                r = yield from bot.sendDocument(message.chat_id, message.file, caption=message.caption,
                                                disable_notification=message.disable_notification,
                                                reply_to_message_id=message.reply_to_message_id,
                                                reply_markup=message.reply_markup)
        elif message.content_type == "photo":
            yield from bot.sendChatAction(message.chat_id, 'upload_photo')
            if os.path.isfile(message.photo):
                r = yield from bot.sendPhoto(message.chat_id, open(message.photo, 'rb'), caption=message.caption,
                                             disable_notification=message.disable_notification,
                                             reply_to_message_id=message.reply_to_message_id,
                                             reply_markup=message.reply_markup)
                os.remove(message.photo)
            else:
                r = yield from bot.sendPhoto(message.chat_id, message.photo, caption=message.caption,
                                             disable_notification=message.disable_notification,
                                             reply_to_message_id=message.reply_to_message_id,
                                             reply_markup=message.reply_markup)
        elif message.content_type == "audio":
            yield from bot.sendChatAction(message.chat_id, 'upload_audio')
            if os.path.isfile(message.audio):
                r = yield from bot.sendAudio(message.chat_id, open(message.audio, 'rb'), duration=message.duration,
                                             performer=message.performer, title=message.title,
                                             disable_notification=message.disable_notification,
                                             reply_to_message_id=message.reply_to_message_id,
                                             reply_markup=message.reply_markup)
                os.remove(message.audio)
            else:
                r = yield from bot.sendAudio(message.chat_id, message.audio, duration=message.duration,
                                             performer=message.performer, title=message.title,
                                             disable_notification=message.disable_notification,
                                             reply_to_message_id=message.reply_to_message_id,
                                             reply_markup=message.reply_markup)
        elif message.content_type == "callback_query":
            r = yield from bot.answerCallbackQuery(message.callback_query_id, text=message.text,
                                                   show_alert=message.show_alert)
        elif message.content_type == "edit_message":
            r = yield from bot.editMessageText(message.msg_identifier, message.text, parse_mode=message.parse_mode,
                                               disable_web_page_preview=message.disable_web_page_preview,
                                               reply_markup=message.reply_markup)
        return r
    except:
        pass


@asyncio.coroutine
def download(file_id, path):
    yield from bot.download_file(file_id, path)
    return path


async def downloader(url, path, params=None):
    try:
        d = path if isinstance(path, io.IOBase) else open(path, 'wb')
        with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                while 1:
                    chunk = await r.content.read()
                    if not chunk:
                        break
                    d.write(chunk)
                    d.flush()
                    return path
    finally:
        if not isinstance(path, io.IOBase) and 'd' in locals():
            d.close()


async def get_stream(url, params=None):
    connector = aiohttp.TCPConnector(verify_ssl=False)
    with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url, params=params) as resp:
            return await resp


async def get(url, params=None, headers=None):
    connector = aiohttp.TCPConnector(verify_ssl=False)
    with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url, params=params, headers=headers) as resp:
            return await resp.text()


async def check_queue():
    while 1:
        while not sender_queue.empty():
            await sender(sender_queue.get())
        await asyncio.sleep(0.1)


load_plugins()
bot = telepot.aio.Bot(config['token'])
answerer = telepot.aio.helper.Answerer(bot)

loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot, {'chat': handle_messages,
                                   'callback_query': on_callback_query,
                                   'inline_query': on_inline_query,
                                   'chosen_inline_result': on_chosen_inline_result,
                                   'edited_chat': handle_messages}).run_forever())
loop.create_task(check_queue())
print('Bot Started ...')

loop.run_forever()
