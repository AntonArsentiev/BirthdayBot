import logging
from bottools.bot import Bot
from postgrestools import commands
from argparse import ArgumentParser
from postgrestools.postgres import Postgres


def parse_args():
    parser = ArgumentParser()

    parser.add_argument("--postgres_host", default=commands.HOST_APP_VALUE)
    parser.add_argument("--postgres_port", default=commands.PORT_APP_VALUE)
    parser.add_argument("--postgres_database", default=commands.DATABASE_APP_VALUE)
    parser.add_argument("--postgres_user", default=commands.USER_APP_VALUE)
    parser.add_argument("--postgres_password", default=commands.PASSWORD_APP_VALUE)
    parser.add_argument("--postgres_type", default=commands.CONNECTION_TYPE_DROP_AND_CREATE)

    return parser.parse_args()


def _main():
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
    logger = logging.getLogger(__name__)

    # parse_args_namespace = parse_args()

    postgres = Postgres(host=commands.HOST_APP_VALUE,
                        port=commands.PORT_APP_VALUE,
                        database=commands.DATABASE_APP_VALUE,
                        user=commands.USER_APP_VALUE,
                        password=commands.PASSWORD_APP_VALUE,
                        connection_type=commands.CONNECTION_TYPE_DROP_AND_CREATE,
                        logger=logger)

    # postgres = Postgres(host=parse_args_namespace.postgres_host,
    #                     port=parse_args_namespace.postgres_port,
    #                     database=parse_args_namespace.postgres_database,
    #                     user=parse_args_namespace.postgres_user,
    #                     password=parse_args_namespace.postgres_password,
    #                     connection_type=parse_args_namespace.postgres_type,
    #                     logger=logger)

    if postgres.is_connected():
        logger.warning("postgres connection is established")
        bot = Bot(logger=logger, postgres=postgres)
        bot.start_pooling()
    else:
        logger.warning("postgres connection is not established")


if __name__ == "__main__":
    _main()
