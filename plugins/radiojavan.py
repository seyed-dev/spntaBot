import asyncio
import uuid

import requests
import telepot
from bs4 import BeautifulSoup
from telepot.namedtuple import InlineQueryResultPhoto, InlineQueryResultArticle, InputTextMessageContent, \
    InlineQueryResultVideo, InlineKeyboardMarkup, InlineKeyboardButton

from bot import downloader, get, is_group, token
from message import Message
import telepot
bot = telepot.Bot(config['token'])


@asyncio.coroutine
async def run(message, matches, chat_id, step):
        response = await get(message['text'])
        soup = BeautifulSoup(response, "html.parser")
        photo = soup.find("div", {"class": "block_container"}).find('img')['src']
        music = soup.find("a", {"class": "mp3_download_link"})['link']
        title = soup.find('title').get_text()
        if music:
            bot.sendPhoto(chat_id, photo, reply_to_message_id=message['message_id'], caption=title, parse_mode='html')
            bot.sendAudio(chat_id, music, caption='{}\n@spntaBot'.format(title), performer='@spntaBot')
        else:
            return [Message(chat_id).set_text("<b>لینک اشتباهه 😞 !</b>:\n", parse_mode="html",
                                              reply_to_message_id=message['message_id'])]

plugin = {
    "name": "radio javan",
    "desc": "_Just Send_ *radio javan* _Share Link and get the text._",
    "usage": ["radio javan Downloader _{Inline}_"],
    "run": run,
    "sudo": False,
    "patterns": ["^(https?://(radiojavan\.com/.*|www\.radiojavan\.com/.*))$"]
}
