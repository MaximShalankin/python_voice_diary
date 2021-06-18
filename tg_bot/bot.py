import os
import datetime
from subprocess import check_call

import pymongo
import vosk
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from tg_bot.voice_module import recognize_phrase
from database.db_functions import add_value, find_value, find_last_values, del_value
from database.time_processing import get_time_interval, timestamp_to_date, date_to_timestamp


class TGBot:

    def __init__(
            self,
            token: str,
            database: pymongo.collection.Collection,
            voice_model: vosk.Model,
            special_chat_id: int = None
    ):

        self.token = token
        self.database = database
        self.special_chat_id = special_chat_id
        self.bot = telebot.TeleBot(token, threaded=False)
        self.voice_model = voice_model

    def add_handlers(self):

        @self.bot.message_handler(content_types=['voice'])
        def process_voice_message(message):

            path_user_logs = os.path.join('user_logs', str(message.chat.id))
            if not os.path.exists(path_user_logs):
                os.makedirs(path_user_logs)

            file_info = self.bot.get_file(message.voice.file_id)
            downloaded_file = self.bot.download_file(file_info.file_path)

            with open(os.path.join(path_user_logs, 'my_phrase.ogg'), 'wb') as new_file:
                new_file.write(downloaded_file)

            # convert oog to wav
            command = f"ffmpeg -i {path_user_logs}/my_phrase.ogg -vn -ar 16000 -ac 2 -ab 192K -f wav {path_user_logs}/my_phrase_to_translite.wav"
            _ = check_call(command.split())

            user_phrase = recognize_phrase(self.voice_model, f'{path_user_logs}/my_phrase_to_translite.wav')
            add_value(self.database, user_phrase)
            self.bot.reply_to(message,
                              f"Твое сообщение сохранено! Дата: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            os.remove(f'{path_user_logs}/my_phrase.ogg')
            os.remove(f'{path_user_logs}/my_phrase_to_translite.wav')

        @self.bot.message_handler(commands=['menu'])
        def main_menu(message):

            keyboard = InlineKeyboardMarkup()
            button_1 = InlineKeyboardButton(text="получить записи", callback_data='find')
            button_2 = InlineKeyboardButton(text="удалить записи", callback_data='delete')
            button_3 = InlineKeyboardButton(text="ничего", callback_data='pass')
            keyboard.add(button_1, button_2, button_3)

            self.bot.send_message(message.chat.id, "Выбери что хочешь сделать", reply_markup=keyboard)

        @self.bot.message_handler(func=lambda message: True, content_types=['text'])
        def process_text_message(message):
            template_text_message = """
            Привет! Если ты хочешь сохранить сообщение, просто отправь голосовое прямо сюда. Для всех остальных случаев воспользуйся командой /menu.
            """
            self.bot.send_message(message.chat.id, template_text_message)

        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_menu_inline(call):
            if call.data == "back_to_main_menu":
                keyboard = InlineKeyboardMarkup()
                button_1 = InlineKeyboardButton(text="получить записи", callback_data='find')
                button_2 = InlineKeyboardButton(text="удалить записи", callback_data='delete')
                button_3 = InlineKeyboardButton(text="ничего", callback_data='pass')
                keyboard.add(button_1, button_2, button_3)
                self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=keyboard)

            elif call.data == "find":
                find_menu = InlineKeyboardMarkup()
                button_1 = InlineKeyboardButton(text='[find] последние N', callback_data='find_last_n')
                button_2 = InlineKeyboardButton(text='[find] на интервале', callback_data='find_interval')
                button_3 = InlineKeyboardButton(text='назад', callback_data='back_to_main_menu')
                find_menu.add(button_1, button_2, button_3)
                self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                                   reply_markup=find_menu)

            elif call.data == "delete":
                delete_menu = InlineKeyboardMarkup()
                button_1 = InlineKeyboardButton(text='[del] последние N', callback_data='delete_last_n')
                button_2 = InlineKeyboardButton(text='[del] на интервале', callback_data='delete_interval')
                button_3 = InlineKeyboardButton(text='назад', callback_data='back_to_main_menu')
                delete_menu.add(button_1, button_2, button_3)
                self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                                   reply_markup=delete_menu)

            elif call.data == "pass":
                self.bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="Ну и отлично!")

            elif call.data == "delete_last_n":
                msg = self.bot.send_message(call.message.chat.id, 'Введи число записей, которые хочешь удалить')
                self.bot.register_next_step_handler(msg, delete_last_n)

            elif call.data == "find_last_n":
                msg = self.bot.send_message(call.message.chat.id, 'Введи число записей, которые хочешь вывести')
                self.bot.register_next_step_handler(msg, find_last_n)

            elif call.data == "delete_interval":
                msg = self.bot.send_message(call.message.chat.id,
                                            'Удалить последние\n\n1) 10 минут\n2) 1 час\n3) 1 день\n\nвведи число')
                self.bot.register_next_step_handler(msg, delete_interval)

            elif call.data == "find_interval":
                msg = self.bot.send_message(call.message.chat.id,
                                            'Найти последние\n\n1) 10 минут\n2) 1 час\n3) 1 день\n\nвведи число')
                self.bot.register_next_step_handler(msg, find_interval)

        # main handlers
        def delete_last_n(message):
            user_answer = message.text

            if not user_answer.isdigit():
                self.bot.send_message(message.chat.id, 'необходимо ввести число')
                return

            last_values = find_last_values(self.database, int(user_answer))
            last_idx, first_idx = last_values[0]['_id'], last_values[-1]['_id']
            del_value(self.database, first_idx, last_idx)
            self.bot.send_message(message.chat.id, 'удалено!')

        def delete_interval(message):
            user_answer = message.text

            if user_answer == '1':  # 10 минут
                use_interval = get_time_interval(int(datetime.datetime.now().timestamp()), 10)

            elif user_answer == '2':  # 60 минут
                use_interval = get_time_interval(int(datetime.datetime.now().timestamp()), 60)

            elif user_answer == '3':  # 1440 минут
                use_interval = get_time_interval(int(datetime.datetime.now().timestamp()), 1440)

            else:
                self.bot.send_message(message.chat.id, 'введено некорректное значение')
                return

            del_value(self.database, use_interval[0], use_interval[1])
            self.bot.send_message(message.chat.id, 'удалено!')

        def find_last_n(message):
            user_answer = message.text

            if not user_answer.isdigit():
                self.bot.send_message(message.chat.id, 'необходимо ввести число')
                return

            for result in find_last_values(self.database, int(user_answer)):
                self.bot.send_message(message.chat.id, timestamp_to_date(result['_id']) + '\n' + result['text'])

        def find_interval(message):
            user_answer = message.text

            if user_answer == '1':  # 10 минут
                use_interval = get_time_interval(int(datetime.datetime.now().timestamp()), 10)

            elif user_answer == '2':  # 60 минут
                use_interval = get_time_interval(int(datetime.datetime.now().timestamp()), 60)

            elif user_answer == '3':  # 1440 минут
                use_interval = get_time_interval(int(datetime.datetime.now().timestamp()), 1440)

            else:
                self.bot.send_message(message.chat.id, 'введено некорректное значение')
                return

            self.bot.send_message(
                message.chat.id,
                'будут выведены сообщения\nс ' + timestamp_to_date(use_interval[0]) + ' по ' + timestamp_to_date(
                    use_interval[1])
            )

            for result in find_value(self.database, use_interval[0], use_interval[1]):
                self.bot.send_message(message.chat.id, timestamp_to_date(result['_id']) + '\n' + result['text'])

    def run_bot(self, **kwargs):
        self.bot.polling(**kwargs)
