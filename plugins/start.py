import asyncio
from telepot.namedtuple import InputTextMessageContent, InlineQueryResultArticle, InlineKeyboardMarkup,\
    InlineKeyboardButton
from message import Message
from bot import is_group, user_steps, key
import redis
import telepot
bot = telepot.Bot('524062252:AAGVHYYvesW-bWoSvfGzgh7Jz2PI4tVdIOc')
r = redis.StrictRedis(host='localhost', port=6379, db=5, decode_responses=True)


@asyncio.coroutine
def run(message, matches, chat_id, step):
    if not is_group(message):
        if message['text'] == '/start':
            text = '''سلام دوست عزیزم 🤓
من سپنتا هستم. خیلی کارا بلدم مثلا دانلود عکس و فیلم از اینستاگرام , دانلود از یوتیوب , جستجوی موسیقی , تغییر کپشن یک فایل , هواشناسی , مدیریت کامل گروه تلگرامی , دانلود استوری اینستاگرام و ....

برای دریافت توضیحات و آموزش استفاده از ربات روی دکمه های زیر کلیک کن 😊
'''

            try:
                del user_steps[message['from']['id']]
            except:
                pass
            return [Message(chat_id).set_text(text, reply_markup=key)]
        if message['text'] == '📥دانلود از اینستاگرام' or message['text'] == '/start instagram':
            text = '''برای دانلود فیلم یا عکس از اینستا لطفا لینک پست را ارسال کنید🤔


        همچنین برای استفاده از حالت اینلاین بعد از نوشتن ایدی ربات لینک را قرار دهید
        مانند تصویر زیر :
        [-](irapi.ir/files/inlineinsta.png)'''
            return [Message(chat_id).set_text(text, parse_mode='Markdown', reply_markup=key)]

        if message['text'] == '📥دانلود از یوتیوب':
            text = '''🎥برای دانلود فیلم از یوتیوب کافیه فقط لینک ویدیو رو برای من ارسال کنی

        مثل :
        https://www.youtube.com/watch?v=tXQ0G7BLUAg

        همچنین میتوانید در حالت اینلاید با استفاده از ربات @vid جستجو کنید و لینک رو اینجا بفرستید'''
            return [Message(chat_id).set_text(text, disable_web_page_preview=True, reply_markup=key)]
        if message['text'] == '🤖ضد لینک و هوش مصنوعی گروه' or message['text'] == '/start antispam':
            bot.sendMessage(chat_id, 'سلام', reply_markup=key)
            text = '''🔖ربات آنتی اسپم و مدیریت گروه سپنتا با قابلیت های فراوان و سرعت فوق العاده

مناسب برای گروه های موزیک متن فروشگاهی و ....

💠قیمت ربات💠
 ماهانه : 10 هزار تومان 
سه ماهه : 20 هزار تومان

برای خرید به بخش پشتیبانی (دکمه پایینی پایینی 😬) مراجعه کنید'''
            return [Message(chat_id).set_text(text, reply_markup=key)]
        if message['text'] == '📋تغییر کپشن':
            text = '''برای تغییر کپشن عکس فیلم یا فایل بر روی آن ریپلای کنید و دستور زیر را وارد کنید

        /cap متن

        مثل تصویر زیر :

        irapi.ir/files/caption.png
        '''
            return [Message(chat_id).set_text(text, reply_markup=key)]
        if message['text'] == '👤پشتیبانی ربات ضد لینک👥' or message['text'] == '/start support':
            if r.hget('contact_user', chat_id):
                r.hset('support_conncet', chat_id, True)
                keysup = {
                    'resize_keyboard': True,
                    'keyboard': [
                                    [
                                        '❌قطع ارتباط'
                                    ]
                            ],
                    'selective': True}
                text = '''💡شما به بخش پشتیبانی متصل شدید

🔖 هر پیامی بفرستید برای ادمین های ربات ارسال خواهد شد.
⚠️ توجه :
+لطفا سوال خود را در یک پیام بفرستید تا جواب بهتری دریافت کنید
+در حین مکالمه ادب را رعایت فرمایید
+شما نمیتوانید پیامی را برای پشتیبانی فوروارد کنید


سلام کن و سوالتو بپرس :)
'''
                return [Message(chat_id).set_text(text, reply_markup=keysup)]
            else:
                r.hset('contact_w8', chat_id, True)
                keysup = {
                    'resize_keyboard': True,
                    'keyboard': [
                        [
                            {'text': 'ارسال شماره همراه📞', 'request_contact': True}
                        ]
                    ],
                    'selective': True}
                text = '''⚠️برای ارتباط با بخش پشتیبانی ما نیازمند  شماره همراه شما باشیم
لطفا برای ارسال شماره همراه بر روی دکمه زیر کلیک کنید'''
                return [Message(chat_id).set_text(text, reply_markup=keysup)]
        if message['text'] == '❌قطع ارتباط':
            r.hdel('support_conncet', chat_id)
            text = '💠 به منوی اصلی خوش آمدید :'
            return [Message(chat_id).set_text(text, reply_markup=key)]



plugin = {
    "name": "start bot",
    "desc": "start",
    "run": run,
    "sudo": False,
    "patterns": [
        "^/start$",
        "^📥دانلود از اینستاگرام$",
        "^📥دانلود از یوتیوب$",
        "^🎧جستجوی موزیک$",
        "^🤖ضد لینک و هوش مصنوعی گروه$",
        "^📋تغییر کپشن$",
        "^⛈هواشناسی$",
        "^👤پشتیبانی ربات ضد لینک👥$",
        "^/sup",
        "^❌قطع ارتباط$",
        "^/start instagram$",
        "^/start support$",
        "^/start antispam$"
    ]
}