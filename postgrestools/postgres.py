from os import environ
from psycopg2 import (
    connect, Error
)
from postgrestools.commands import Commands
from postgrestools.commands import (
    CONNECTION_TYPE_DROP,
    CONNECTION_TYPE_DROP_AND_CREATE,
    HOST, PORT, DATABASE, USER, PASSWORD,
    SELECT
)


class Postgres:
    def __init__(self,
                 host="localhost",
                 port=5432,
                 database="telegram",
                 user="postgres",
                 password="postgres",
                 connection_type="connect",
                 logger=None):
        self._host = environ.get(HOST, host)
        self._port = environ.get(PORT, port)
        self._database = environ.get(DATABASE, database)
        self._user = environ.get(USER, user)
        self._password = environ.get(PASSWORD, password)
        self._logger = logger
        self._connection = None
        self._cursor = None
        self._commands = Commands(user=self._user)
        self._establish_connection(connection_type)

    def _establish_connection(self, connection_type):
        try:
            self._connection = connect(host=self._host,
                                       port=self._port,
                                       database=self._database,
                                       user=self._user,
                                       password=self._password)
            self._connection.set_session(autocommit=True)
            self._cursor = self._connection.cursor()
            if connection_type == CONNECTION_TYPE_DROP:
                self.execute(self.commands().drop_all())
            elif connection_type == CONNECTION_TYPE_DROP_AND_CREATE:
                self.execute(self.commands().drop_and_create_all())
        except Error as error:
            self._logger.warning(error.pgerror)

    def _terminated_connection(self):
        if self._connection:
            try:
                self._cursor.close()
                self._connection.close()
            except Error as error:
                self._logger.warning(error.pgerror)

    def is_connected(self):
        if self._connection:
            self._logger.info(place="Postgres.is_connected()", message="postgres connection is established")
        else:
            self._logger.critical(place="Postgres.is_connected()", message="postgres connection is not established")
        return True if self._connection else False

    def execute(self, command):
        try:
            self._cursor.execute(command)
            if SELECT in command:
                return self._cursor.fetchall()
        except Error as error:
            self._logger.warning(error.pgerror)

    def commands(self):
        return self._commands


if __name__ == "__main__":
    from loggingtools.register import Logger
    logger = Logger("debug")
    postgres = Postgres(password="qwe@123", logger=logger)
    if postgres.is_connected():
        command = 'SELECT * FROM "Present"'
        result = postgres.execute(command)
        print(result)
    else:
        print("postgres - connection is not established")
