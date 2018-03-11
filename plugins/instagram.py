import asyncio
import uuid

import requests
import telepot
from bs4 import BeautifulSoup
from telepot.namedtuple import InlineQueryResultPhoto, InlineQueryResultArticle, InputTextMessageContent, \
    InlineQueryResultVideo

from bot import downloader, get, is_group
from message import Message


@asyncio.coroutine
async def run(message, matches, chat_id, step):

        response = await get(message['text'])
        soup = BeautifulSoup(response, "html.parser")
        image = soup.find("meta", {"property": "og:image"})
        video = soup.find("meta", {"property": "og:video"})
        if video:
            width = soup.find("meta", {"property": "og:video:width"})
            height = soup.find("meta", {"property": "og:video:height"})
            return [Message(chat_id).set_video(await downloader(video['content'], "tmp/{}.mp4".format(uuid.uuid4())),
                                               width=width, height=height, reply_to_message_id=message['message_id'],
                                               caption='@spntaBot')]
        elif image:
            return [Message(chat_id).set_photo(await downloader(image['content'], "tmp/{}.jpg".format(uuid.uuid4())),
                                               reply_to_message_id=message['message_id'], caption='@spntaBot')]
        else:
            return [Message(chat_id).set_text("<b>لینک اشتباهه 😞 !</b>:\n", parse_mode="html",
                                              reply_to_message_id=message['message_id'])]


@asyncio.coroutine
async def inline(message, matches, chat_id, step):
    query_id, from_id, query = telepot.glance(message, flavor='inline_query')
    response = requests.get(query)
    soup = BeautifulSoup(response.text, "html.parser")
    image = soup.find("meta", {"property": "og:image"})
    video = soup.find("meta", {"property": "og:video"})
    if video:
        width = soup.find("meta", {"property": "og:video:width"})
        height = soup.find("meta", {"property": "og:video:height"})
        return [InlineQueryResultVideo(
            id=str(uuid.uuid4()), description='Instagram Video', title="Instagram Video", mime_type="video/mp4",
            thumb_url=image['content'], video_url=video['content'], video_width=int(width['content']),
            video_height=int(height['content']))]
    elif image:
        return [InlineQueryResultPhoto(
            id=str(uuid.uuid4()), title="Instagram Photo",
            photo_url=image['content'], photo_width=300, photo_height=300,
            thumb_url=image['content'])]
    else:
        return [InlineQueryResultArticle(
            id=str(uuid.uuid4()), title='Error', description="Not Found",
            input_message_content=InputTextMessageContent(message_text="لینک اشتباهه 😞", parse_mode="Markdown"),
            thumb_url="http://siyanew.com/bots/custom.jpg")]


plugin = {
    "name": "Instagram",
    "desc": "_Just Send_ *Instagram* _Share Link and get the Photo or Video immediately._",
    "usage": ["Instagram Downloader _{Inline}_"],
    "run": run,
    "sudo": False,
    "inline_patterns": ["^(https?://(instagr\.am/p/.*|instagram\.com/p/.*|www\.instagram\.com/p/.*))$"],
    "inline_query": inline,
    "patterns": ["^(https?://(instagr\.am/p/.*|instagram\.com/p/.*|www\.instagram\.com/p/.*))$"]
}