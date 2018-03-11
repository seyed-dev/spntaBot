import asyncio

import telepot

from bot import markdown_escape
from message import Message

text = {"name": "👤 *{} {}*",
        "group": "👥 *{}*",
        "id": "🆔 \\[{}]",
        "username": "▶️ @{}"}


@asyncio.coroutine
def run(message, matches, chat_id, step):
    content_type, chat_type, chat_id = telepot.glance(message)
    if 'reply_to_message' in message:
        if 'forward_from' in message['reply_to_message']:
            response = ""
            if 'last_name' in message['reply_to_message']['forward_from']:
                response = str(text['name']).format(
                    markdown_escape(message['reply_to_message']['forward_from']['first_name']),
                    markdown_escape(message['reply_to_message']['forward_from']['last_name']))
            else:
                response = str(text['name']).format(
                    markdown_escape(message['reply_to_message']['forward_from']['first_name']), "")
            response += "\n" + text['id'].format(message['reply_to_message']['forward_from']['id'])
            if 'username' in message['reply_to_message']['forward_from']:
                response += "\n" + text['username'].format(
                    markdown_escape(message['reply_to_message']['forward_from']['username']))
            return [Message(chat_id).set_text(response, parse_mode="markdown")]
        else:
            response = ""
            if 'last_name' in message['reply_to_message']['from']:
                response = str(text['name']).format(markdown_escape(message['reply_to_message']['from']['first_name']),
                                                    markdown_escape(message['reply_to_message']['from']['last_name']))
            else:
                response = str(text['name']).format(markdown_escape(message['reply_to_message']['from']['first_name']),
                                                    "")
            response += "\n" + text['id'].format(message['reply_to_message']['from']['id'])
            if 'username' in message['reply_to_message']['from']:
                response += "\n" + text['username'].format(
                    markdown_escape(message['reply_to_message']['from']['username']))
            return [Message(chat_id).set_text(response, parse_mode="markdown")]
    if chat_type == "private":
        response = ""
        if 'last_name' in message['from']:
            response = str(text['name']).format(markdown_escape(message['from']['first_name']),
                                                markdown_escape(message['from']['last_name']))
        else:
            response = str(text['name']).format(markdown_escape(message['from']['first_name']), "")
        response += "\n" + text['id'].format(message['from']['id'])
        if 'username' in message['from']:
            response += "\n" + text['username'].format(markdown_escape(message['from']['username']))
        return [Message(chat_id).set_text(response, parse_mode="markdown")]
    else:
        response = ""
        response += str(text['group']).format(markdown_escape(message['chat']['title']))
        response += "\n" + str(text['id']).format(str(abs(message['chat']['id'])))
        response += "\n➖➖➖➖➖➖➖➖"
        if 'last_name' in message['from']:
            response += "\n" + str(text['name']).format(markdown_escape(message['from']['first_name']),
                                                        markdown_escape(message['from']['last_name']))
        else:
            response += "\n" + str(text['name']).format(markdown_escape(message['from']['first_name']), "")
        response += "\n" + text['id'].format(message['from']['id'])
        if 'username' in message['from']:
            response += "\n" + text['username'].format(markdown_escape(message['from']['username']))
        return [Message(chat_id).set_text(response, parse_mode="markdown")]


plugin = {
    "name": "Who",
    "desc": "Show user id or group id.",
    "usage": ["/who", "/id"],
    "run": run,
    "sudo": False,
    "patterns": ["^[!/#]who$",
                 "^[!/#]id$"]
}