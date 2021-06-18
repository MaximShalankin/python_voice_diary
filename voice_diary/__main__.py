import json

from tg_bot.bot import TGBot
from database import DIARY_DB
from tg_bot import VOICE_MODEL

with open('voice_diary/credentials.json', 'r') as file:
    credentials = json.load(file)


def main():
    my_diary_bot = TGBot(credentials['api_key'], DIARY_DB, VOICE_MODEL, credentials['special_chat_id'])
    my_diary_bot.add_handlers()
    my_diary_bot.run_bot(**{'none_stop': True})


if __name__ == '__main__':
    main()
