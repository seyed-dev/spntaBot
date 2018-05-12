import asyncio
import json

from bot import get, user_steps, is_group, key, config
from message import Message

icons = {'01d': '🌞',
         '01n': '🌚',
         '02d': '⛅️',
         '02n': '⛅️',
         '03d': '☁️',
         '03n': '☁️',
         '04d': '☁️',
         '04n': '☁️',
         '09d': '🌧',
         '09n': '🌧',
         '10d': '🌦',
         '10n': '🌦',
         '11d': '🌩',
         '11n': '🌩',
         '13d': '🌨',
         '13n': '🌨',
         '50d': '🌫',
         '50n': '🌫',
         }

import sys
sys.path.append('../')
import lang
ln = lang.message[config['lang']]

@asyncio.coroutine
async def run(message, matches, chat_id, step):
    from_id = message['from']['id']
    if not is_group(message):
        if step == 0:
            hide_keyboard = {'hide_keyboard': True, 'selective': True}
            user_steps[from_id] = {"name": "weather", "step": 1, "data": []}
            text = ln['weather']['city']
            return [Message(chat_id).set_text(text, reply_markup=hide_keyboard)]
        elif step == 1:
            del user_steps[from_id]
            payload = {
                'q': message['text'],
                'units': "metric",
                'appid': '973e8a21e358ee9d30b47528b43a8746'  # Your Open Weather Api Code
            }
            req = await get("http://api.openweathermap.org/data/2.5/weather", params=payload)
            try:
                data = json.loads(req)
                cityName = "{}, {}".format(data["name"], data["sys"]["country"])
                tempInC = round(data["main"]["temp"], 2)
                tempInF = round((1.8 * tempInC) + 32, 2)
                icon = data["weather"][0]["icon"]
                desc = data["weather"][0]["description"]
                res = "<b>{}</b>\n<pre>🌡{}C ({}F)</pre>\n<pre>{} {}</pre>".format(cityName, tempInC, tempInF,
                                                                                   icons[icon],
                                                                                   desc)
                return [Message(chat_id).set_text(res, parse_mode="html",reply_markup=key)]
            except:
                return [Message(chat_id).set_text(ln['weather']['error'], parse_mode="Markdown",reply_markup=key)]

plugin = {
    "name": "weather",
    "desc": "Show The Weather of a city\n\n"
            "*For Example :*\n`/weather London`",
    "usage": ["/weather \\[`City`]"],
    "run": run,
    "sudo": False,
    "patterns": ["^⛈هواشناسی$"]
}
