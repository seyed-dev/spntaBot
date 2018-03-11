import asyncio
import uuid

import requests
import telepot
from bs4 import BeautifulSoup
from telepot.namedtuple import InlineQueryResultPhoto, InlineQueryResultArticle, InputTextMessageContent, \
    InlineQueryResultVideo, InlineKeyboardMarkup, InlineKeyboardButton

from bot import downloader, get, is_group
from message import Message
import telepot
bot = telepot.Bot('524062252:AAGVHYYvesW-bWoSvfGzgh7Jz2PI4tVdIOc')


@asyncio.coroutine
async def run(message, matches, chat_id, step):
        link = '{}?lang=fa'.format(message['text'])
        response = await get(link)
        soup = BeautifulSoup(response, "html.parser")
        text = soup.find("p", {"class": "TweetTextSize TweetTextSize--jumbo js-tweet-text tweet-text tweet-text-rtl"})
        name = soup.find("strong", {"class": "fullname show-popup-with-id u-textTruncate fullname-rtl"})
        date = soup.find("span", {"class": "metadata"})
        photo = soup.find("div", {"class": "AdaptiveMedia-photoContainer js-adaptive-photo "})
        like = soup.find("a", {"class": "request-favorited-popup"})
        ret = soup.find("a", {"class": "request-retweeted-popup"})
        if text:
            mtext = '{}\n\n«{}»\n{} - {}\n{}'.format(text.get_text(), name.get_text(),
                                                     like['data-activity-popup-title'].replace('پسندیدن', '❤️'),
                                                     ret['data-activity-popup-title'].replace('بازتوییت', '🔁'),
                                                     date.get_text())
            if photo:
                msg = bot.sendPhoto(chat_id, photo['data-image-url'], reply_to_message_id=message['message_id'])
                bot.sendMessage(chat_id, mtext, reply_to_message_id=msg['message_id'], parse_mode='html')
            else:
                return [Message(chat_id).set_text(mtext, parse_mode="html", reply_to_message_id=message['message_id'])]
        else:
            return [Message(chat_id).set_text("<b>لینک اشتباهه 😞 !</b>:\n", parse_mode="html",
                                              reply_to_message_id=message['message_id'])]


@asyncio.coroutine
async def inline(message, matches, chat_id, step):
    query_id, from_id, query = telepot.glance(message, flavor='inline_query')
    link = '{}?lang=fa'.format(query)
    response = await get(link)
    soup = BeautifulSoup(response, "html.parser")
    text = soup.find("p", {"class": "TweetTextSize TweetTextSize--jumbo js-tweet-text tweet-text tweet-text-rtl"})
    name = soup.find("strong", {"class": "fullname show-popup-with-id u-textTruncate fullname-rtl"})
    date = soup.find("span", {"class": "metadata"})
    photo = soup.find("div", {"class": "AdaptiveMedia-photoContainer js-adaptive-photo "})
    like = soup.find("a", {"class": "request-favorited-popup"})
    ret = soup.find("a", {"class": "request-retweeted-popup"})
    if text:
        mtext = '{}\n\n«{}»\n{}'.format(text.get_text(), name.get_text(),
                                                 date.get_text())
        des = '{} {}'.format(like['data-activity-popup-title'].replace('پسندیدن', '❤️'),
                             ret['data-activity-popup-title'].replace('بازتوییت', '🔁'),)
        show_keyboard = [
            [
                InlineKeyboardButton(text=like['data-activity-popup-title'].replace('پسندیدن', '❤️'), url=link),
                InlineKeyboardButton(text=ret['data-activity-popup-title'].replace('بازتوییت', '🔁'), url=link),
            ]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=show_keyboard)
        return [InlineQueryResultArticle(
            id=str(uuid.uuid4()), title=name.get_text(), description=des,
            input_message_content=InputTextMessageContent(message_text=mtext, parse_mode="html"),
            reply_markup=markup,
            thumb_url="https://www.saydaily.com/.image/c_limit%2Ccs_srgb%2Cw_410/MTM0ODg3OTkwOTMyNTc1NTA2/"
                      "screen-shot-2015-12-03-at-22820-pmpng.png")]


plugin = {
    "name": "twitter",
    "desc": "_Just Send_ *twitter* _Share Link and get the text._",
    "usage": ["twitter Downloader _{Inline}_"],
    "run": run,
    "sudo": False,
    "inline_patterns": ["^(https?://(t\.co/.*|twitter\.com/.*|www\.twitter\.com/.*))$"],
    "inline_query": inline,
    "patterns": ["^(https?://(t\.co/.*|twitter\.com/.*|www\.twitter\.com/.*))$"]
}