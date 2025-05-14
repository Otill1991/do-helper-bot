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
    import signal
    import sys

    def signal_handler(signum, frame):
        print("\nShutting down bot gracefully...")
        bot.stop_polling()
        sys.exit(0)

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        bot.polling(none_stop=True)
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received. Shutting down...")
        bot.stop_polling()
        sys.exit(0)
    except Exception as e:
        print(f"Error occurred: {e}")
        time.sleep(15)
        start_bot()


if __name__ == '__main__':
    parse_config()
    start_bot()
