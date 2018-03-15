import asyncio
import uuid
import demjson
from telepot.namedtuple import InlineQueryResultAudio, InlineKeyboardMarkup, InlineKeyboardButton
from bot import user_steps, sender, get, downloader, is_group, key, config
from message import Message
import telepot
import soundcloud
bot = telepot.Bot(config['token'])
import os
# create a client object with your app credentials
client = soundcloud.Client(client_id='') # Your client_id
page_size = 100
# get first 100 tracks


async def search(query):
    tracks = client.get('/tracks', q=query, limit=page_size)
    res = []
    for track in tracks:
        res.append([track.title, track.permalink_url, track.artwork_url or None])
    return res


async def getfile(url):
    response = await get(
        "https://api.soundcloud.com/resolve?url={}&client_id=".format(url)) # Your client_id
    r = demjson.decode(response)
    return r['stream_url'] + "?client_id=" # Your client_id


@asyncio.coroutine
async def run(message, matches, chat_id, step):
    if not is_group(message):
        from_id = message['from']['id']
        if step == 0:
            user_steps[from_id] = {"name": "Soundcloud", "step": 1, "data": {}}
            hide_keyboard = {'hide_keyboard': True, "selective": True}
            return [Message(chat_id).set_text("لطفا اسم موزیک یا نام خواننده را وارد کنید🤔",
                                              reply_to_message_id=message['message_id'],
                                              reply_markup=hide_keyboard)]
        if step == 1:
            await sender(
                Message(chat_id).set_text("اومم یکم صبر کن برم جستجو کنم ببینم چی گیرم میاد 😘😬",
                                          parse_mode="markdown"))
            user_steps[from_id] = {"name": "Soundcloud", "step": 2, "data": {}}
            i = 0
            show_keyboard = {'keyboard': [], "selective": True}
            ttt = message['text'].replace(" ", "+")
            for song in await search(ttt):
                title, link, cover = song[0], song[1], song[2]
                user_steps[from_id]['data'][title] = link
                show_keyboard['keyboard'].append([title])
                i += 1
                if i == 20:
                    break
            if len(show_keyboard['keyboard']) in [0, 1]:
                hide_keyboard = {'hide_keyboard': True, 'selective': True}
                del user_steps[from_id]
                return [Message(chat_id).set_text("چیزی نیافتم 😣",
                                                  reply_to_message_id=message['message_id'], reply_markup=hide_keyboard,
                                                  parse_mode="markdown")]
            return [Message(chat_id).set_text("یکی از اینارو انتخاب کن 🙃👇🏻", reply_to_message_id=message['message_id'],
                                              reply_markup=show_keyboard)]
        elif step == 2:
            try:

                await sender(Message(chat_id).set_text("خب یکم صبر کن تا موزیکو دانلود کنم و برات بفرستم 🤓",
                                                       reply_to_message_id=message['message_id'],
                                                       reply_markup=key, parse_mode="markdown"))
                await downloader(await getfile(user_steps[from_id]['data'][message['text']]),
                                 "tmp/{}.mp3".format(message['text']))
                del user_steps[from_id]
                bot.sendAudio(chat_id, open("tmp/{}.mp3".format(message['text']), 'rb'), title=message['text'],
                                                   performer="@SpntaBot")
                os.remove("tmp/{}.mp3".format(message['text']))
            except Exception as e:
                del user_steps[from_id]
                return [Message(chat_id).set_text("داری اشتباه میزنی 😕", parse_mode="markdown")]


@asyncio.coroutine
async def inline(message, matches, chat_id, step):
    query_id, from_id, query = telepot.glance(message, flavor='inline_query')
    ttt = matches[1].replace(" ", "+")
    musics = []
    i = 0
    for song in await search(ttt):
        title, link, cover = song[0], song[1], song[2]
        key = [
            [
                InlineKeyboardButton(text='🔖ارسال به دیگری', switch_inline_query='music {}'.format(title)),
            ]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=key)
        musics.append(InlineQueryResultAudio(id=str(uuid.uuid4()), title=song[0], audio_url=await getfile(link),
                                             performer='@spntaBot', caption='{}\n@SpntaBot'.format(title),
                                             reply_markup=markup))
        i += 1
        if i == 20:
            break
    bot.answerInlineQuery(query_id, musics)


plugin = {
    "name": "Soundcloud",
    "desc": "Download a Music From Sound Cloud\n\n"
            "*For Start :*\n`/sc michael jackson billie jean`",
    "usage": ["/music \\[`Search`]"],
    "run": run,
    "sudo": False,
    "inline_patterns": ["^(music) (.*)$"],
    "inline_query": inline,
    "patterns": [
        "^🎧جستجوی موزیک$"
    ]
}
