import os
from flask import Flask
from flask import request
from bottools.bot import Bot
from bottools.constants import *
from postgrestools import commands
# from argparse import ArgumentParser
from loggingtools.register import Logger
from postgrestools.postgres import Postgres
from telegram import (
    Update
)
# from telegram.ext import (
#     CommandHandler, Dispatcher
# )
# from queue import Queue

server = Flask(__name__)

logger = Logger(commands.LOGGER_APP_VALUE)

postgres = Postgres(host=commands.HOST_APP_VALUE,
                    port=commands.PORT_APP_VALUE,
                    database=commands.DATABASE_APP_VALUE,
                    user=commands.USER_APP_VALUE,
                    password=commands.PASSWORD_APP_VALUE,
                    connection_type=commands.CONNECTION_TYPE_DROP_AND_CREATE,
                    logger=logger)

# if postgres.is_connected():
bot = Bot(logger=logger, postgres=postgres)
bot.start_pooling()

# bot = Bot(token=BOT_TOKEN)
# bot.setWebhook(HEROKU_APP_URL + BOT_TOKEN)
# update_queue = Queue()
# dp = Dispatcher(bot, update_queue, use_context=True)
#
#
# def start(update, context):
#     context.bot.send_message(
#         chat_id=update.effective_chat.id,
#         text="_команда старт_"
#     )


# start_handler = CommandHandler('start', start)
# dp.add_handler(start_handler)

# def parse_args():
#     parser = ArgumentParser()
#
#     parser.add_argument("--postgres_host", default=commands.HOST_APP_VALUE)
#     parser.add_argument("--postgres_port", default=commands.PORT_APP_VALUE)
#     parser.add_argument("--postgres_database", default=commands.DATABASE_APP_VALUE)
#     parser.add_argument("--postgres_user", default=commands.USER_APP_VALUE)
#     parser.add_argument("--postgres_password", default=commands.PASSWORD_APP_VALUE)
#     parser.add_argument("--postgres_type", default=commands.CONNECTION_TYPE_DROP_AND_CREATE)
#     parser.add_argument("--logger_level", default=commands.LOGGER_APP_VALUE)
#
#     return parser.parse_args()


@server.route('/')
def index():
    logger.info("index", "something was received")
    return HEROKU_APP_URL


@server.route('/' + BOT_TOKEN, methods=["POST"])
def web_hook():
    if request.method == "POST":
        logger.info("web_hook", "something was received")
        update = Update.de_json(request.get_json(force=True), bot.get_bot())
        bot.get_dispatcher().process_update(update)
        bot.get_update_queue().put(update)
        return "OK"


if __name__ == "__main__":
    # parse_args_namespace = parse_args()

    # logger = Logger(parse_args_namespace.logger_level)
    #
    # postgres = Postgres(host=parse_args_namespace.postgres_host,
    #                     port=parse_args_namespace.postgres_port,
    #                     database=parse_args_namespace.postgres_database,
    #                     user=parse_args_namespace.postgres_user,
    #                     password=parse_args_namespace.postgres_password,
    #                     connection_type=parse_args_namespace.postgres_type,
    #                     logger=logger)

    # logger = Logger(commands.LOGGER_APP_VALUE)
    #
    # postgres = Postgres(host=commands.HOST_APP_VALUE,
    #                     port=commands.PORT_APP_VALUE,
    #                     database=commands.DATABASE_APP_VALUE,
    #                     user=commands.USER_APP_VALUE,
    #                     password=commands.PASSWORD_APP_VALUE,
    #                     connection_type=commands.CONNECTION_TYPE_DROP_AND_CREATE,
    #                     logger=logger)
    #
    # if postgres.is_connected():
    #     bot = Bot(logger=logger, postgres=postgres)
    #     bot.start_pooling()
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
