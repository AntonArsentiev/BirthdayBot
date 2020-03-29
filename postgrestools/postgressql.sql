/*
************************************************************

	Работа с таблицей Account
	
************************************************************	
*/

-- Создание таблицы

DROP TABLE IF EXISTS "Account";

CREATE TABLE "Account" (
	account_id bigint NOT NULL,
	first_name character varying(64),
	last_name character varying(64),
	user_name character varying(64),
	language_code character varying(4),
	CONSTRAINT account_account_id_pk PRIMARY KEY (account_id)
);

ALTER TABLE "Account" OWNER TO postgres;

CREATE INDEX account_account_id_idx ON "Account" USING btree (account_id);

-- Добавление записей в таблицу

INSERT INTO "Account" (account_id, first_name, last_name, user_name, language_code) 
VALUES (12345, 'Антон', 'Арсентьев', 'antonarsentiev', 'en');

-- Выборка записей из таблицы

SELECT language_code FROM "Account" WHERE account_id = 12345;

-- Изменение записей таблицы
  
UPDATE "Account" SET language_code = 'ru' WHERE account_id = 12345;

/*
************************************************************

	Работа с таблицей Birthday
	
************************************************************	
*/

-- Создание таблицы

DROP TABLE IF EXISTS "Birthday";

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

ALTER TABLE "Birthday" OWNER TO postgres;

CREATE INDEX birthday_id_idx ON "Birthday" USING btree (id);

CREATE INDEX birthday_account_id_idx ON "Birthday" USING btree (account_id);
  
-- Добавление записей в таблицу

INSERT INTO "Birthday" (first_name, middle_name, last_name, date, congratulation, desires, account_id) 
VALUES ('Антон', 'Алексеевич', 'Арсентьев', '1994-02-18', 'Передаю мои поздравления!', 'Список пожеланий здесь обеспечен!', 12345);

-- Выборка записей из таблицы
  
SELECT * FROM "Birthday" WHERE account_id = 12345;  
  
SELECT * FROM "Account" LEFT JOIN "Birthday" ON "Account"."account_id" = "Birthday"."account_id"

-- Изменение записей таблицы
  
UPDATE "Birthday" SET congratulation = 'Update поздравления!' WHERE id = 1;

UPDATE "Birthday" SET congratulation = 'Update!!!!!!!!', date = '2222-11-11' WHERE id = 1;
  
/*
************************************************************

	Работа с таблицей Present
	
************************************************************	
*/
  
-- Создание таблицы

DROP TABLE IF EXISTS "Present";  
  
CREATE TABLE "Present" (
	id serial NOT NULL,
	name character varying(64),
	description text,
	year character varying(4),
	CONSTRAINT present_id_pk PRIMARY KEY (id)
);

ALTER TABLE "Present" OWNER TO postgres;

CREATE INDEX present_id_idx ON "Present" USING btree (id);  
  
-- Добавление записей в таблицу 
  
INSERT INTO "Present" (name, description, year) 
VALUES ('Подарок 1', 'Описание подарка 1', '2019'); 
  
-- Выборка записей из таблицы
  
SELECT * FROM "Present";    
  
-- Изменение записей таблицы  
  
UPDATE "Present" SET description = 'Update описание подарка!' WHERE id = 1;  
  
/*
************************************************************

	Работа с таблицей FromAccount
	
************************************************************	
*/  

-- Создание таблицы
  
DROP TABLE IF EXISTS "FromAccount";   
  
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

ALTER TABLE "FromAccount" OWNER TO postgres;

CREATE INDEX fromaccount_account_id_idx ON "FromAccount" USING btree (account_id);

CREATE INDEX fromaccount_birthday_id_idx ON "FromAccount" USING btree (birthday_id);

CREATE INDEX fromaccount_id_idx ON "FromAccount" USING btree (id);

CREATE INDEX fromaccount_present_id_idx ON "FromAccount" USING btree (present_id); 
  
-- Добавление записей в таблицу  
  
INSERT INTO "FromAccount" (account_id, birthday_id, present_id) 
VALUES (12345, 1, 2); 
  
-- Выборка записей из таблицы  

SELECT "In2"."user_name", "In2"."first_name", "In2"."last_name", "P"."name", "P"."description", "P"."year"
FROM (SELECT "In1"."user_name", "B"."first_name", "B"."last_name", "In1"."present_id"
FROM (SELECT "A"."account_id", "A"."user_name", "FA"."birthday_id", "FA"."present_id"
FROM "Account" "A"
LEFT JOIN "FromAccount" "FA"
ON "A"."account_id" = "FA"."account_id"
WHERE "A"."user_name" = 'antonarsentiev') "In1"
LEFT JOIN "Birthday" "B"
ON "In1"."birthday_id" = "B"."id") "In2"
LEFT JOIN "Present" "P"
ON "In2"."present_id" = "P"."id"
 
-- Изменение записей таблицы  

/*
************************************************************

	Работа с таблицей ToAccount
	
************************************************************	
*/  

-- Создание таблицы
  
DROP TABLE IF EXISTS "ToAccount";   
  
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

ALTER TABLE "ToAccount" OWNER TO postgres;

CREATE INDEX toaccount_account_id_idx ON "ToAccount" USING btree (account_id);

CREATE INDEX toaccount_birthday_id_idx ON "ToAccount" USING btree (birthday_id);

CREATE INDEX toaccount_id_idx ON "ToAccount" USING btree (id);

CREATE INDEX toaccount_present_id_idx ON "ToAccount" USING btree (present_id); 
  
-- Добавление записей в таблицу  
  
INSERT INTO "ToAccount" (birthday_id, account_id, present_id) 
VALUES (1, 12345, 2); 
  
-- Выборка записей из таблицы  

SELECT "In2"."user_name", "In2"."first_name", "In2"."last_name", "P"."name", "P"."description", "P"."year"
FROM (SELECT "In1"."user_name", "B"."first_name", "B"."last_name", "In1"."present_id"
FROM (SELECT "A"."account_id", "A"."user_name", "TA"."birthday_id", "TA"."present_id"
FROM "Account" "A"
LEFT JOIN "ToAccount" "TA"
ON "A"."account_id" = "TA"."account_id"
WHERE "A"."user_name" = 'antonarsentiev') "In1"
LEFT JOIN "Birthday" "B"
ON "In1"."birthday_id" = "B"."id") "In2"
LEFT JOIN "Present" "P"
ON "In2"."present_id" = "P"."id"

-- Изменение записей таблицы  

/*
************************************************************

	!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	
************************************************************	