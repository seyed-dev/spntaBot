class Message:
    def __init__(self, chat_id=""):
        self.chat_id = chat_id

    def set_text(self, text, parse_mode=None, disable_web_page_preview=None, disable_notification=None,
                 reply_to_message_id=None, reply_markup=None):
        self.text = text
        self.content_type = "text"
        self.parse_mode = parse_mode
        self.disable_web_page_preview = disable_web_page_preview
        self.disable_notification = disable_notification
        self.reply_to_message_id = reply_to_message_id
        self.reply_markup = reply_markup
        return self

    def set_video(self, video, duration=None, width=None, height=None, caption=None, disable_notification=None,
                  reply_to_message_id=None, reply_markup=None):
        self.content_type = "video"
        self.video = video
        self.duration = duration
        self.width = width
        self.height = height
        self.caption = caption
        self.disable_notification = disable_notification
        self.reply_to_message_id = reply_to_message_id
        self.reply_markup = reply_markup
        return self

    def set_document(self, file, caption=None, disable_notification=None, reply_to_message_id=None, reply_markup=None):
        self.content_type = "document"
        self.file = file
        self.caption = caption
        self.disable_notification = disable_notification
        self.reply_to_message_id = reply_to_message_id
        self.reply_markup = reply_markup
        return self

    def set_photo(self, photo, caption=None, disable_notification=None, reply_to_message_id=None, reply_markup=None):
        self.content_type = "photo"
        self.photo = photo
        self.caption = caption
        self.disable_notification = disable_notification
        self.reply_to_message_id = reply_to_message_id
        self.reply_markup = reply_markup
        return self

    def set_audio(self, audio, duration=None, performer=None, title=None, disable_notification=None,
                  reply_to_message_id=None, reply_markup=None):
        self.content_type = "audio"
        self.audio = audio
        self.duration = duration
        self.title = title
        self.performer = performer
        self.disable_notification = disable_notification
        self.reply_to_message_id = reply_to_message_id
        self.reply_markup = reply_markup
        return self

    def callback_query(self, callback_query_id, text=None, show_alert=None):
        self.content_type = "callback_query"
        self.callback_query_id = callback_query_id
        self.text = text
        self.show_alert = show_alert
        return self

    def edit_message(self, msg_identifier, text, parse_mode=None, disable_web_page_preview=None, reply_markup=None):
        self.content_type = "edit_message"
        self.msg_identifier = msg_identifier
        self.text = text
        self.parse_mode = parse_mode
        self.disable_web_page_preview = disable_web_page_preview
        self.reply_markup = reply_markup
        return self
