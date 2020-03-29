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
        # self._port = environ.get(PORT, port)
        self._port = port
        self._database = environ.get(DATABASE, database)
        self._user = environ.get(USER, user)
        self._password = environ.get(PASSWORD, password)
        self._logger = logger
        self._connection = None
        self._cursor = None

        self._logger.warning("host = {host}, "
                             "port = {port}, "
                             "database = {database}, "
                             "user = {user}, "
                             "password = {password}".format(
                                host=self._host,
                                port=self._port,
                                database=self._database,
                                user=self._user,
                                password=self._password
                             ))

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
            if self._logger:
                self._logger.warning(error.pgerror)
            else:
                print(error)

    def _terminated_connection(self):
        if self._connection:
            try:
                self._cursor.close()
                self._connection.close()
            except Error as error:
                if self._logger:
                    self._logger.warning(error.pgerror)
                else:
                    print(error)

    def is_connected(self):
        return True if self._connection else False

    def execute(self, command):
        try:
            self._cursor.execute(command)
            if SELECT in command:
                return self._cursor.fetchall()
        except Error as error:
            if self._logger:
                self._logger.warning(error.pgerror)
            else:
                print(error)

    def commands(self):
        return self._commands


def main():
    connection = connect(host="127.0.0.1",
                         port=5432,
                         database="telegram",
                         user="postgres",
                         password="postgres")
    connection.set_session(autocommit=True)
    cursor = connection.cursor()
    cursor.execute("UPDATE \"Account\" SET language_code = 'ru' WHERE account_id = 513814634;")
    # cursor.execute("SELECT * FROM \"Account\";")
    import psycopg2.errors
    try:
        records = cursor.fetchall()
        for record in records:
            print(record)
    except psycopg2.Error:
        print(123)


if __name__ == "__main__":
    main()
