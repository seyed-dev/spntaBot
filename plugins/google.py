import asyncio
from telepot.namedtuple import InlineQueryResultAudio, InlineKeyboardMarkup, InlineKeyboardButton,\
    InlineQueryResultArticle, InputTextMessageContent
import uuid
from message import Message
import telepot
import re
import requests
from bot import config
from bs4 import BeautifulSoup

bot = telepot.Bot(config['token'])

@asyncio.coroutine
def run(message, matches, chat_id, step):
    if matches[0] == 'google':
        mtext = matches[1].replace(' ', '+')
        link = 'https://www.google.com/search?q={}'.format(mtext)
        response = requests.get(link)
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.findAll("h3", {"class": "r"})
        text = '\n💠 نتایج جستجو برای : {}\n'.format(matches[1])
        for i in title:
            text += '[{}](https://google.com{})\n\n'.format(i.get_text(), i.find('a', href=True)[ 'href' ])
        bot.sendMessage(chat_id, text, parse_mode='Markdown', disable_web_page_preview=True)
    elif matches[0] == 'lmgtfy':
        mtext = matches[ 1 ].replace(' ', '+')
        link = 'http://lmgtfy.com/?q={}'.format(mtext)
        text = 'کلیک کنید 😉👇🏻\n\n[{}]({})'.format(matches[1], link)
        bot.sendMessage(chat_id, text, parse_mode='Markdown', disable_web_page_preview=True)
    elif matches[0] == 'spell':
        mtext = matches[ 1 ].replace(' ', '+')
        link = 'https://www.google.com/search?q={}'.format(mtext)
        response = requests.get(link)
        soup = BeautifulSoup(response.text, "html.parser")
        try:
            text = soup.find("a", {"class": "spell"}).get_text()
            m = bot.sendMessage(chat_id, 'آیا منظور شما عبارت زیر هستش ؟👇🏻', reply_to_message_id=message['message_id'])
            bot.sendMessage(chat_id, text)
        except:
            bot.sendMessage(chat_id, 'منظورتو نفهمیدم 🤧')
    elif matches == 'spell':
        if 'reply_to_message' in message:
            m = message['reply_to_message']
            mtext = m['text'].replace(' ', '+')
            link = 'https://www.google.com/search?q={}'.format(mtext)
            response = requests.get(link)
            soup = BeautifulSoup(response.text, "html.parser")
            try:
                text = soup.find("a", {"class": "spell"}).get_text()
                m = bot.sendMessage(chat_id, 'آیا منظور شما عبارت زیر هستش ؟👇🏻',
                                    reply_to_message_id=message[ 'message_id' ])
                bot.sendMessage(chat_id, text)
            except:
                bot.sendMessage(chat_id, 'منظورتو نفهمیدم 🤧')

@asyncio.coroutine
async def inline(message, matches, chat_id, step):
    query_id, from_id, query = telepot.glance(message, flavor='inline_query')
    mtext = matches[ 1 ].replace(' ', '+')
    link = 'https://www.google.com/search?q={}'.format(mtext)
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.findAll("h3", {"class": "r"})
    des = {}
    num = 1
    gg = []
    for x in soup.findAll("span", {"class": "st"}):
        des.update({'{}'.format(num): x.get_text()})
        num += 1
    nums = 1
    def desc(number):
        try:
            return des['{}'.format(number)]
        except:
            return 'توضیحات ندارد'
    for i in title:
        text = '{}\n\n{}'.format(i.get_text(), desc(nums))
        key = [
            [
                InlineKeyboardButton(text=' 🔖 ورود به سایت', url='https://google.com{}'.format(i.find('a', href=True)[ 'href' ])),
            ]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=key)
        gg.append(InlineQueryResultArticle(
            id=str(uuid.uuid4()), title='{}'.format(text),
            description='{}'.format(desc(nums)),
            input_message_content=InputTextMessageContent(message_text=text),
            reply_markup=markup,
            thumb_url="https://www.apkmirror.com/wp-content/uploads/2017/12/5a26211455d5a.png"))
        nums += 1
    bot.answerInlineQuery(query_id, gg)


plugin = {
    "name": "google",
    "desc": "google",
    "usage": ["/google text"],
    "run": run,
    "sudo": False,
    "inline_patterns": [ "^(google) (.*)$" ],
    "inline_query": inline,
    "patterns": [
        "^[/#!](google) (.*)",
        "^[/#!](lmgtfy) (.*)",
        "^[/#!](spell) (.*)",
        "^[/#!](spell)$"
    ]
}
