import asyncio
import uuid

from telepot.namedtuple import InputTextMessageContent, InlineQueryResultArticle

from bot import get
from message import Message


@asyncio.coroutine
async def run(message, matches, chat_id, step):
    exp = matches
    payload = {
        'expr': exp
    }
    req = await get("http://api.mathjs.org/v1/", params=payload)
    if req:
        return [Message(chat_id).set_text(matches + " = " + req)]
    return [Message(chat_id).set_text("Oops,\nSomething went wrong!")]


@asyncio.coroutine
async def inline(message, matches, chat_id, step):
    exp = matches
    payload = {
        'expr': exp
    }
    req = await get("http://api.mathjs.org/v1/", params=payload)
    if req:
        return [InlineQueryResultArticle(
            id=str(uuid.uuid4()), title='Calculator', description=matches + " = " + req,
            input_message_content=InputTextMessageContent(message_text=matches + " = " + req),
            thumb_url="https://lh3.googleusercontent.com/U3jWNUNqn2XqlNhD2ggy6ELAtt0jRps9MKbfERUWcOBO8uC_BmZUqCKV5eD2uarhg14=w300")]
    return [InlineQueryResultArticle(
        id=str(uuid.uuid4()), title='Error occurred!', description="Something Went Wrong!",
        input_message_content=InputTextMessageContent(message_text="*Something Went Wrong!*", parse_mode="Markdown"),
        thumb_url="https://lh3.googleusercontent.com/U3jWNUNqn2XqlNhD2ggy6ELAtt0jRps9MKbfERUWcOBO8uC_BmZUqCKV5eD2uarhg14=w300")]


plugin = {
    "name": "Calculator",
    "desc": "With this plugin you can calculate expressions.",
    "usage": ["/cal \\[`Expression`] _{Inline}_"],
    "inline_patterns": ["^calc (.*)$"],
    "inline_query": inline,
    "run": run,
    "sudo": False,
    "patterns": ["^[!/#]calc (.*)$"]
}