def parse_config():
    import json
    from os import environ

    config = json.load(open('config.json', 'r', encoding='utf-8'))
    environ['bot_name'] = config['BOT']['NAME']
    environ['bot_token'] = config['BOT']['TOKEN']
    environ['bot_admins'] = json.dumps(config['BOT']['ADMINS'])


def start_bot():
    from bot import bot
    import time

    while True:
        try:
            bot.polling(none_stop=True)
        except Exception:
            time.sleep(15)
            continue


if __name__ == '__main__':
    parse_config()
    start_bot()
