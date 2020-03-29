# connection_type

CONNECTION_TYPE_DROP = "DROP"
CONNECTION_TYPE_DROP_AND_CREATE = "DROP_AND_CREATE"
CONNECTION_TYPE_CONNECT = "CONNECT"

# connection default settings

HOST = "HOST"
PORT = "PORT"
DATABASE = "DATABASE"
USER = "USER"
PASSWORD = "PASSWORD"

HOST_APP_VALUE = "localhost"
PORT_APP_VALUE = 5432
DATABASE_APP_VALUE = "telegram"
USER_APP_VALUE = "postgres"
PASSWORD_APP_VALUE = "qwe@123"
TYPE_APP_VALUE = CONNECTION_TYPE_DROP_AND_CREATE

# database commands

DROP_ACCOUNT_TABLE = """
    DROP TABLE IF EXISTS "Account" CASCADE;
    DROP SEQUENCE IF EXISTS "Account_id_seq" CASCADE;
"""

DROP_BIRTHDAY_TABLE = """
    DROP TABLE IF EXISTS "Birthday" CASCADE;
    DROP SEQUENCE IF EXISTS "Birthday_id_seq" CASCADE;
"""

DROP_PRESENT_TABLE = """
    DROP TABLE IF EXISTS "Present" CASCADE;
    DROP SEQUENCE IF EXISTS "Present_id_seq" CASCADE;
"""

DROP_FROM_ACCOUNT_TABLE = """
    DROP TABLE IF EXISTS "FromAccount" CASCADE;
    DROP SEQUENCE IF EXISTS "FromAccount_id_seq" CASCADE;
"""

DROP_TO_ACCOUNT_TABLE = """
    DROP TABLE IF EXISTS "ToAccount" CASCADE;
    DROP SEQUENCE IF EXISTS "ToAccount_id_seq" CASCADE;
"""

DROP_ALL = [
    DROP_ACCOUNT_TABLE,
    DROP_BIRTHDAY_TABLE,
    DROP_PRESENT_TABLE,
    DROP_FROM_ACCOUNT_TABLE,
    DROP_TO_ACCOUNT_TABLE
]

CREATE_ACCOUNT_TABLE = """
    CREATE TABLE "Account" (
        account_id bigint NOT NULL,
        first_name character varying(64),
        last_name character varying(64),
        user_name character varying(64),
        language_code character varying(4),
        CONSTRAINT account_account_id_pk PRIMARY KEY (account_id)
    );
    
    ALTER TABLE "Account" OWNER TO {user};
    
    CREATE INDEX account_account_id_idx ON "Account" USING btree (account_id);
"""

CREATE_BIRTHDAY_TABLE = """
    CREATE TABLE "Birthday" (
        id serial NOT NULL,
        first_name character varying(64),
        middle_name character varying(64),
        last_name character varying(64),
        date date,
        congratulation text,
        desires text,
        account_id bigint,
        CONSTRAINT birthday_id_pk PRIMARY KEY (id),
        CONSTRAINT birthday_account_id_fk FOREIGN KEY (account_id)
            REFERENCES "Account" (account_id) ON DELETE CASCADE
    );
    
    ALTER TABLE "Birthday" OWNER TO {user};
    
    CREATE INDEX birthday_id_idx ON "Birthday" USING btree (id);
    
    CREATE INDEX birthday_account_id_idx ON "Birthday" USING btree (account_id);
"""

CREATE_PRESENT_TABLE = """
    CREATE TABLE "Present" (
        id serial NOT NULL,
        name character varying(64),
        description text,
        year character varying(4),
        CONSTRAINT present_id_pk PRIMARY KEY (id)
    );
    
    ALTER TABLE "Present" OWNER TO {user};
    
    CREATE INDEX present_id_idx ON "Present" USING btree (id);
"""

CREATE_FROM_ACCOUNT_TABLE = """
    CREATE TABLE "FromAccount" (
        id serial NOT NULL,
        account_id bigint,
        birthday_id integer,
        present_id integer,
        CONSTRAINT fromaccount_id_pk PRIMARY KEY (id),
        CONSTRAINT fromaccount_account_id_fk FOREIGN KEY (account_id)
            REFERENCES "Account" (account_id) ON DELETE CASCADE,
        CONSTRAINT fromaccount_birthday_id_fk FOREIGN KEY (birthday_id)
            REFERENCES "Birthday" (id) ON DELETE CASCADE,
        CONSTRAINT fromaccount_present_id_fk FOREIGN KEY (present_id)
            REFERENCES "Present" (id) ON DELETE CASCADE
    );
    
    ALTER TABLE "FromAccount" OWNER TO {user};
    
    CREATE INDEX fromaccount_account_id_idx ON "FromAccount" USING btree (account_id);
    
    CREATE INDEX fromaccount_birthday_id_idx ON "FromAccount" USING btree (birthday_id);
    
    CREATE INDEX fromaccount_id_idx ON "FromAccount" USING btree (id);
    
    CREATE INDEX fromaccount_present_id_idx ON "FromAccount" USING btree (present_id); 
"""

CREATE_TO_ACCOUNT_TABLE = """
    CREATE TABLE "ToAccount" (
        id serial NOT NULL,
        birthday_id integer,
        account_id bigint,
        present_id integer,
        CONSTRAINT toaccount_id_pk PRIMARY KEY (id),
        CONSTRAINT toaccount_birthday_id_fk FOREIGN KEY (birthday_id)
            REFERENCES "Birthday" (id) ON DELETE CASCADE,
        CONSTRAINT toaccount_account_id_fk FOREIGN KEY (account_id)
            REFERENCES "Account" (account_id) ON DELETE CASCADE,
        CONSTRAINT toaccount_present_id_fk FOREIGN KEY (present_id)
            REFERENCES "Present" (id) ON DELETE CASCADE
    );
    
    ALTER TABLE "ToAccount" OWNER TO {user};
    
    CREATE INDEX toaccount_account_id_idx ON "ToAccount" USING btree (account_id);
    
    CREATE INDEX toaccount_birthday_id_idx ON "ToAccount" USING btree (birthday_id);
    
    CREATE INDEX toaccount_id_idx ON "ToAccount" USING btree (id);
    
    CREATE INDEX toaccount_present_id_idx ON "ToAccount" USING btree (present_id);
"""

CREATE_ALL = [
    CREATE_ACCOUNT_TABLE,
    CREATE_BIRTHDAY_TABLE,
    CREATE_PRESENT_TABLE,
    CREATE_FROM_ACCOUNT_TABLE,
    CREATE_TO_ACCOUNT_TABLE
]

SELECT = "SELECT"

SELECT_ACCOUNT = """
    SELECT * FROM "Account";
"""

INSERT_ACCOUNT = """
    INSERT INTO "Account" (account_id, first_name, last_name, user_name, language_code) 
    VALUES ({account_id}, '{first_name}', '{last_name}', '{user_name}', '{language_code}');
"""

UPDATE_LANGUAGE = """
    UPDATE "Account" SET language_code = '{language_code}' WHERE account_id = {account_id};
"""

INSERT_BIRTHDAY = """
    INSERT INTO "Birthday" (last_name, first_name, middle_name, date, congratulation, desires, account_id) 
    VALUES ('{last_name}', '{first_name}', '{middle_name}', '{date}', '{congratulation}', '{desires}', {account_id});
"""

SELECT_BIRTHDAY_FOR_ACCOUNT = """
    SELECT * FROM "Birthday" WHERE account_id = {account_id};  
"""


class Commands:
    def __init__(self, user="postgres"):
        self._user = user

    def drop_all(self):
        result = ""
        for drop in DROP_ALL:
            result += drop.format(user=self._user)
        return result

    def drop_and_create_all(self):
        result = ""
        for drop in DROP_ALL:
            result += drop.format(user=self._user)
        for create in CREATE_ALL:
            result += create.format(user=self._user)
        return result

    @staticmethod
    def select_account():
        return SELECT_ACCOUNT

    @staticmethod
    def insert_account(account_id, first_name, last_name, user_name, language_code):
        return INSERT_ACCOUNT.format(
            account_id=account_id,
            first_name=first_name,
            last_name=last_name,
            user_name=user_name,
            language_code=language_code
        )

    @staticmethod
    def update_language(language_code, account_id):
        return UPDATE_LANGUAGE.format(
            language_code=language_code,
            account_id=account_id
        )

    @staticmethod
    def insert_birthday(last_name, first_name, middle_name, date, congratulation, desires, account_id):
        return INSERT_BIRTHDAY.format(
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name,
            date=date,
            congratulation=congratulation,
            desires=desires,
            account_id=account_id
        )

    @staticmethod
    def select_birthday_for_account(account_id):
        return SELECT_BIRTHDAY_FOR_ACCOUNT.format(
            account_id=account_id
        )


def main():
    command = INSERT_ACCOUNT.format(
        account_id="12345",
        first_name="anton",
        last_name="arsentiev",
        user_name="antoinearsentiev",
        language_code="en"
    )
    print(command)


if __name__ == "__main__":
    main()
