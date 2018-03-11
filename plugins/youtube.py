import asyncio
import uuid
from telepot.namedtuple import InlineQueryResultAudio, InlineKeyboardMarkup, InlineKeyboardButton
import pafy
from bot import user_steps, sender, downloader, is_group, key
from message import Message


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'K', 'M', 'G', 'T', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


@asyncio.coroutine
async def run(message, matches, chat_id, step):
    from_id = message['from']['id']
    if not is_group(message):
        if step == 0:
            video = pafy.new(matches)
            allstreams = video.allstreams
            user_steps[from_id] = {"name": "Youtube", "step": 0, "data": []}
            user_steps[from_id]['video'] = video
            show_keyboard = {'keyboard': [], 'selective': True}
            counter = 1
            for s in allstreams:
                if s.mediatype == "normal":
                    show_keyboard['keyboard'].append(
                        [str(counter) + ". " + s.quality + " | " + s.extension + " | " + str(
                            sizeof_fmt(s.get_filesize()))])
                    user_steps[from_id]['data'].append(s)
                    counter += 1
                if s.mediatype == "audio":
                    show_keyboard['keyboard'].append([str(
                        counter) + ". (Audio " + s.bitrate + " ) | " + s.extension + " | " + str(
                        sizeof_fmt(s.get_filesize()))])
                    user_steps[from_id]['data'].append(s)
                    counter += 1
            user_steps[from_id]['step'] += 1
            return [Message(chat_id).set_text("ـاین لینک رو در چه فرمتی میخواید دریافت کنید؟ـ", parse_mode="Markdown",
                                              reply_to_message_id=message['message_id'], reply_markup=show_keyboard)]
        elif step == 1:
            try:
                video = user_steps[from_id]['video']
                best = user_steps[from_id]['data'][int(message['text'].split(".")[0]) - 1]
                hide_keyboard = {'hide_keyboard': True, 'selective': True}
                await sender(
                    Message(chat_id).set_text('''ـلطفا صبر کنیدـ
        بزودی براتون فرمت دلخواه رو میفرستم 😊''', parse_mode="markdown",
                                              reply_to_message_id=message['message_id'], reply_markup=key))
                if best.get_filesize() < 49000000:
                    if best.mediatype == "normal":
                        del user_steps[from_id]
                        filepath = "tmp/{}.{}".format(uuid.uuid4(), best.extension)
                        await downloader(best.url, filepath)

                        return [Message(chat_id).set_document(filepath, reply_markup=key)]
                    if best.mediatype == "audio":
                        filepath = "tmp/{}.{}".format(uuid.uuid4(), best.extension)
                        await downloader(best.url, filepath)
                        del user_steps[from_id]
                        return [Message(chat_id).set_audio(filepath, performer="@spntaBot", title=video.title,
                                                           reply_markup=key)]
                result = "_برای دانلود روی لینک زیر کلیک کنید_\n[{}]({})".format(video.title, best.url)
                del user_steps[from_id]

                return [Message(chat_id).set_text(result, disable_web_page_preview=True,
                                                  reply_to_message_id=message['message_id'], parse_mode="Markdown",
                                                  reply_markup=key)]
            except Exception as e:
                print(e)
                del user_steps[from_id]
                hide_keyboard = {'hide_keyboard': True, 'selective': True}
                return [
                    Message(chat_id).set_text("هومم یک مشکلی پیش اومده نمیتونم دانلودش کنم🤔", parse_mode="markdown",
                                              reply_to_message_id=message['message_id'], reply_markup=key)]

    else:
        if step == 0:
            video = pafy.new(matches)
            allstreams = video.allstreams
            user_steps[ from_id ] = {"name": "Youtube", "step": 0, "data": [ ]}
            user_steps[ from_id ][ 'video' ] = video
            show_keyboard = {'keyboard': [ ], 'selective': True}
            counter = 1
            for s in allstreams:
                if s.mediatype == "normal":
                    show_keyboard[ 'keyboard' ].append(
                        [ str(counter) + ". " + s.quality + " | " + s.extension + " | " + str(
                            sizeof_fmt(s.get_filesize())) ])
                    user_steps[ from_id ][ 'data' ].append(s)
                    counter += 1
                if s.mediatype == "audio":
                    show_keyboard[ 'keyboard' ].append([ str(
                        counter) + ". (Audio " + s.bitrate + " ) | " + s.extension + " | " + str(
                        sizeof_fmt(s.get_filesize())) ])
                    user_steps[ from_id ][ 'data' ].append(s)
                    counter += 1
            user_steps[ from_id ][ 'step' ] += 1
            return [ Message(chat_id).set_text("این لینک رو در چه فرمتی میخواید دریافت کنید؟", parse_mode="Markdown",
                                               reply_to_message_id=message[ 'message_id' ],
                                               reply_markup=show_keyboard) ]
        elif step == 1:
            try:
                video = user_steps[ from_id ][ 'video' ]
                best = user_steps[ from_id ][ 'data' ][ int(message[ 'text' ].split(".")[ 0 ]) - 1 ]
                hide_keyboard = {'hide_keyboard': True, 'selective': True}
                await sender(
                    Message(chat_id).set_text('''لطفا صبر کنید
        بزودی براتون فرمت دلخواه رو میفرستم 😊''', parse_mode="markdown",
                                              reply_to_message_id=message[ 'message_id' ], reply_markup=hide_keyboard))
                if best.get_filesize() < 49000000:
                    if best.mediatype == "normal":
                        del user_steps[ from_id ]
                        filepath = "tmp/{}.{}".format(uuid.uuid4(), best.extension)
                        await downloader(best.url, filepath)

                        return [ Message(chat_id).set_document(filepath, reply_markup=hide_keyboard) ]
                    if best.mediatype == "audio":
                        filepath = "tmp/{}.{}".format(uuid.uuid4(), best.extension)
                        await downloader(best.url, filepath)
                        del user_steps[ from_id ]
                        return [ Message(chat_id).set_audio(filepath, performer="@spntaBot", title=video.title,
                                                            reply_markup=hide_keyboard) ]
                result = "_برای دانلود روی لینک زیر کلیک کنید_\n[{}]({})".format(video.title, best.url)
                del user_steps[ from_id ]

                return [ Message(chat_id).set_text(result, disable_web_page_preview=True,
                                                   reply_to_message_id=message[ 'message_id' ], parse_mode="Markdown",
                                                   reply_markup=hide_keyboard) ]
            except Exception as e:
                print(e)
                del user_steps[ from_id ]
                hide_keyboard = {'hide_keyboard': True, 'selective': True}
                return [
                    Message(chat_id).set_text("هومم یک مشکلی پیش اومده نمیتونم دانلودش کنم🤔", parse_mode="markdown",
                                              reply_to_message_id=message[ 'message_id' ], reply_markup=hide_keyboard) ]


plugin = {
    "name": "Youtube",
    "desc": "_Just Send me a_ *Youtube* _Link and get the Download Link immediately._",
    "usage": ["Youtube Link Retriever"],
    "run": run,
    "sudo": False,
    "patterns": [
        "^(?:https?:\/\/)?(?:www\.)?(?:m\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_]+)\&?$"]
}