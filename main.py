import os
from flask import Flask
from flask import request
from telegram import Update
from bottools.bot import Bot
from bottools.constants import *
from postgrestools import commands
# from argparse import ArgumentParser
from loggingtools.register import Logger
from postgrestools.postgres import Postgres

server = Flask(__name__)


@server.route("/")
def index():
    return HEROKU_APP_URL


@server.route("/" + BOT_TOKEN, methods=[METHOD_POST])
def web_hook():
    update = Update.de_json(request.get_json(force=True), bot.get_bot())
    bot.get_dispatcher().process_update(update)
    bot.get_update_queue().put(update)
    return FLASK_SERVER_OK


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

    logger = Logger(commands.LOGGER_APP_VALUE)

    postgres = Postgres(
        host=commands.HOST_APP_VALUE,
        port=commands.PORT_APP_VALUE,
        database=commands.DATABASE_APP_VALUE,
        user=commands.USER_APP_VALUE,
        password=commands.PASSWORD_APP_VALUE,
        connection_type=commands.CONNECTION_TYPE_DROP_AND_CREATE,
        logger=logger
    )

    if postgres.is_connected():
        bot = Bot(logger=logger, postgres=postgres)
        bot.start_pooling()
    server.run(
        host=FLASK_SERVER_ADDRESS_VALUE,
        port=int(os.environ.get(FLASK_SERVER_PORT, FLASK_SERVER_PORT_VALUE))
    )
