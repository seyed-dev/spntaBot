import asyncio
from telepot.namedtuple import InputTextMessageContent, InlineQueryResultArticle, InlineKeyboardMarkup,\
    InlineKeyboardButton
from message import Message
from bot import config
import telepot
from bs4 import BeautifulSoup
import requests
import re
import uuid
bot = telepot.Bot(config['token'])

@asyncio.coroutine
def run(message, matches, chat_id, step):
        if matches == 'v3' or matches[0] == 'v3':
            url = 'http://www.varzesh3.com/livescore'
            response = requests.get(url)
            soup = BeautifulSoup(response.content.decode('utf-8'), "html.parser")
            teams = soup.find_all("div", {"id": re.compile('^match-*')})
            text = '⚽️ لیست بازی های امروز :\n'
            i = 1
            for x in teams:
                time_game_start = x.find("div", {"class": "start-time"}).get_text()
                date_game = x.find("div", {"class": "start-date"}).get_text()
                time_game_real = x.find("div", {"class": re.compile("elapsed-time *")}).find('span').get_text()
                team_right = x.find("div", {"class": "teamname right"}).get_text()
                score_right = x.find("div", {"class": re.compile("score right team-*")}).get_text()
                team_left = x.find("div", {"class": "teamname left"}).get_text()
                score_left = x.find("div", {"class": re.compile("score left team-*")}).get_text()
                text += '> {} {} - {} {} 🕓{}\n\n'.format(team_right, score_right, team_left, score_left,
                                                          time_game_real.replace('\n', ''))
                i += 1
                if i > 30:
                    break
            return [Message(chat_id).set_text(text)]


@asyncio.coroutine
async def inline(message, matches, chat_id, step):
    query_id, from_id, query = telepot.glance(message, flavor='inline_query')
    url = 'http://www.varzesh3.com/livescore'
    response = requests.get(url)
    soup = BeautifulSoup(response.content.decode('utf-8'), "html.parser")
    teams = soup.find_all("div", {"id": re.compile('^match-*')})
    i = 1
    games = []
    for x in teams:
        time_game_start = x.find("div", {"class": "start-time"}).get_text()
        date_game = x.find("div", {"class": "start-date"}).get_text()
        time_game_real = x.find("div", {"class": re.compile("elapsed-time *")}).find('span').get_text()
        team_right = x.find("div", {"class": "teamname right"}).get_text()
        score_right = x.find("div", {"class": re.compile("score right team-*")}).get_text()
        team_left = x.find("div", {"class": "teamname left"}).get_text()
        score_left = x.find("div", {"class": re.compile("score left team-*")}).get_text()
        title = '> {} {} - {} {}'.format(team_right, score_right, team_left, score_left)
        text = '''> {} {} - {} {} 

🕗ساعت شروع بازی : {}
🕓زمان سپری شده : {}
📆تاریخ بازی : {}
'''.format(team_right, score_right, team_left, score_left, time_game_start, time_game_real.replace('\n', ''), date_game)
        des = '🕗ساعت شروع بازی : {}'.format(time_game_start)
        i += 1
        if i > 30:
            break
        key = [
            [
                InlineKeyboardButton(text='📋 نمایش لیست بازی ها', switch_inline_query='v3'),
            ]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=key)
        games.append(InlineQueryResultArticle(
            id=str(uuid.uuid4()), title=title,
            description=des,
            input_message_content=InputTextMessageContent(message_text=text),
            reply_markup=markup,
            thumb_url="https://store-images.microsoft.com/image/apps.53391.13510798884212736.df8117c9-93d9-448a-b44a-012e6a8b3089.e0cb56fa-6cdd-43f8-adf9-f2df4402b947?w=180&h=180&q=60"))
        i += 1
        if i == 20:
            break
    bot.answerInlineQuery(query_id, games)


plugin = {
    "name": "varzesh3",
    "desc": "varzesh3",
    "run": run,
    "sudo": False,
    "inline_patterns": [ "^(v3)$", "^(varzesh3) (.*)$"],
    "inline_query": inline,
    "patterns": [
        "^[/#!](v3)",

    ]
}

