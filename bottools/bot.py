from translationtools.language import Translator
from telegram.ext import (
    Updater, CommandHandler, MessageHandler,
    Filters, CallbackQueryHandler, Dispatcher
)
from .constants import *
from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, ParseMode,
    ReplyKeyboardMarkup, ReplyKeyboardRemove
)
from telegram import Bot as TelegramBot
from datetime import (
    datetime, timedelta
)
from queue import Queue
import calendar


class Bot:
    def __init__(self, logger, postgres):
        self._status = {}
        self._logger = logger
        self._postgres = postgres
        self._bot = TelegramBot(token=BOT_TOKEN)
        self._update_queue = Queue()
        self._dispatcher = Dispatcher(self._bot, self._update_queue, use_context=True)
        self._translator = Translator(file=TRANSLATION_FILE)
        self._set_commands()
        self._update_status()
        self._set_job_queue()

# ------------------------------------------------------------------------------------------
#       INIT METHODS
# ------------------------------------------------------------------------------------------

    def _set_commands(self):
        self._dispatcher.add_handler(CommandHandler(START, self._start))
        self._dispatcher.add_handler(CommandHandler(ADD, self._add))
        self._dispatcher.add_handler(CommandHandler(LANGUAGE, self._language))
        self._dispatcher.add_handler(CommandHandler(HELP, self._help))
        self._dispatcher.add_handler(CallbackQueryHandler(self._callback_query))
        self._dispatcher.add_handler(MessageHandler(Filters.all, self._other_messages))

    def _update_status(self):
        command = self._postgres.commands().select_account()
        records = self._postgres.execute(command)
        for record in records:
            self._status[record[0]] = {
                STATUS: NONE,
                LANGUAGE: record[4]
            }

    def _set_job_queue(self):
        pass
        # now = datetime.utcnow()
        # to = now + timedelta(seconds=23 * 60 * 60)
        # to = to.replace(hour=0, minute=0, second=0, microsecond=0)
        # self._updater.job_queue.run_repeating(self._it_is_time_for_birthday,
        #                                       interval=24 * 60 * 60,
        #                                       first=60)
        # to.timestamp() - now.timestamp()

# ------------------------------------------------------------------------------------------
#       PUBLIC METHODS
# ------------------------------------------------------------------------------------------

    def start_pooling(self):
        # self._updater.start_webhook(listen=WEB_HOOK_ADDRESS,
        #                             port=int(os.environ.get(HEROKU_APP_PORT, WEB_HOOK_PORT)),
        #                             url_path=BOT_TOKEN)
        self._bot.setWebhook(HEROKU_APP_URL + BOT_TOKEN)
        # self._updater.start_polling()
        # self._updater.idle()

    def get_dispatcher(self):
        return self._dispatcher

    def get_update_queue(self):
        return self._update_queue

# ------------------------------------------------------------------------------------------
#       COMMANDS
# ------------------------------------------------------------------------------------------

    def _start(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE] if self._status.get(account_id, None) else STANDART_LANGUAGE
        translate = self._translator.translate
        if account_id in self._status.keys():
            self._status[account_id][STATUS] = NONE
            context.bot.send_message(
                chat_id=update.effective_message.chat_id,
                text=translate("Я рад снова тебя приветствовать здесь!", language)
            )
        else:
            self._status[account_id] = {LANGUAGE: STANDART_LANGUAGE, STATUS: NONE}
            command = self._postgres.commands().insert_account(
                account_id=account_id,
                first_name=update.effective_user[FIRST_NAME],
                last_name=update.effective_user[LAST_NAME],
                user_name=update.effective_user[USERNAME],
                language_code=STANDART_LANGUAGE
            )
            self._postgres.execute(command)
            context.bot.send_message(
                chat_id=update.effective_message.chat_id,
                text=translate("Я рад тебя приветствовать у меня в гостях. У меня уютно и есть печеньки!", language)
            )
            context.bot.send_message(
                chat_id=update.effective_message.chat_id,
                text=translate("Чтобы вы лучше понимали что я могу, воспользуйтесь командой /help. Если у вас есть желание сменить язык общения, то команда /language поможет вам это сделать!", language)
            )

    def _add(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        self._status[account_id][STATUS] = ADD_CONTACT
        self._status[account_id][BIRTHDAY] = {
            FIO: {
                LAST_NAME: NONE,
                FIRST_NAME: NONE,
                MIDDLE_NAME: NONE
            },
            DATE: {
                YEAR: NONE,
                MONTH: NONE,
                DAY: NONE
            },
            CONGRATULATION: NONE,
            DESIRES: NONE,
            PHONE_NUMBER: NONE,
            TELEGRAM_USER_ID: NONE
        }

        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=translate("Давайте начнем заполнение анкеты вашего друга. Сперва пришлите контакт друга", language)
        )

    def _language(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        self._status[account_id][STATUS] = LANGUAGE
        languages = [(key, value) for key, value in self._translator.languages().items() if key != language]
        keyboard = [
            [
                InlineKeyboardButton(languages[0][1], callback_data=languages[0][0]),
                InlineKeyboardButton(languages[1][1], callback_data=languages[1][0])
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=translate("Сейчас установленный язык русский. На какой Вы желаете изменить?", language),
            reply_markup=reply_markup
        )

    def _help(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        self._status[account_id][STATUS] = NONE
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=translate("BirthdayBot создан для напоминания о днях рождениях твоих друзей! "
                           "Вдруг у вас много работы или дел по дому, то я всегда дам вам знать, "
                           "что особенный день близко!\\n\\n"
                           "Чтобы я смог напомнить вам о дне рождения, вам необходимо заполнить анкету друга! "
                           "Для заполнения анкеты существует команда /add\\n\\n"
                           "При необходимости сменить язык общения - можно отправить команду /language", language)
        )

    def _callback_query(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        query_data = update.callback_query.data
        status = self._status[account_id][STATUS]
        if status == LANGUAGE:
            self._language_in_callback_query(update, context)
        elif status == CREATE:
            context.bot.answer_callback_query(callback_query_id=update.callback_query.id)
            if query_data == ADD_FIO:
                self._add_fio_in_callback_query(update, context)
            elif query_data == ADD_DATE:
                self._add_date_in_callback_query(update,context)
            elif query_data == ADD_CONGRATULATION:
                self._add_congratulation_in_callback_query(update, context)
            elif query_data == ADD_DESIRES:
                self._add_desires_in_callback_query(update, context)
            elif query_data == CREATE:
                self._create_in_callback_query(update, context)
        else:
            self._invalid_in_callback_query(update, context)

    def _other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        status = self._status[account_id][STATUS]

        if status == ADD_CONTACT:
            self._add_contact_in_other_messages(update, context)
        elif status == ADD_DATE_INTERVAL:
            self._add_date_interval_in_other_messages(update, context)
        elif status == ADD_DATE_YEAR:
            self._add_date_year_in_other_messages(update, context)
        elif status == ADD_DATE_MONTH:
            self._add_date_month_in_other_messages(update, context)
        elif status == ADD_DATE_DAY:
            self._add_date_day_in_other_messages(update, context)
        elif status == ADD_FIO_LAST_NAME:
            self._add_fio_last_name_in_other_messages(update, context)
        elif status == ADD_FIO_FIRST_NAME:
            self._add_fio_first_name_in_other_messages(update, context)
        elif status == ADD_FIO_MIDDLE_NAME:
            self._add_fio_middle_name_in_other_messages(update, context)
        elif status == ADD_CONGRATULATION:
            self._add_congratulation_in_other_messages(update, context)
        elif status == ADD_DESIRES:
            self._add_desires_in_other_messages(update, context)
        else:
            self._invalid_in_other_messages(update, context)

# ------------------------------------------------------------------------------------------
#       JOBQUEUE METHODS
# ------------------------------------------------------------------------------------------

    def _it_is_time_for_birthday(self, dispatcher):
        account_command = self._postgres.commands().select_account()
        account_records = self._postgres.execute(account_command)
        translate = self._translator.translate
        for account_record in account_records:
            account_id = account_record[0]
            language = self._status[account_id][LANGUAGE]

            birthday_command = self._postgres.commands().select_birthday_for_account(account_record[0])
            birthday_records = self._postgres.execute(birthday_command)
            for birthday_record in birthday_records:
                datetime_birthday = datetime.strptime(birthday_record[6].strftime("%Y-%m-%d"), "%Y-%m-%d")

                birthday = {
                    FIO: {
                        LAST_NAME: birthday_record[1],
                        FIRST_NAME: birthday_record[2],
                        MIDDLE_NAME: birthday_record[3]
                    },
                    DATE: {
                        YEAR: str(datetime_birthday.year),
                        MONTH: str(datetime_birthday.month),
                        DAY: str(datetime_birthday.day)
                    }
                }
                remind7, remind1 = birthday_record[9], birthday_record[10]
                datetime_birthday = datetime_birthday.replace(year=datetime.utcnow().year)
                if datetime.utcnow().timestamp() > datetime_birthday.timestamp():
                    datetime_birthday = datetime_birthday.replace(year=datetime.utcnow().year + 1)
                if datetime_birthday.timestamp() - datetime.utcnow().timestamp() <= 24 * 60 * 60 and remind1:
                    dispatcher.bot.send_message(
                        chat_id=account_record[0],
                        text=translate("У твоего друга менее чем через сутки день рождения!\\n\\n"
                                       "{fio} исполняется {age}!\\n\\n"
                                       "Не забудь поздравить именинника и постарайся сделать его день рождения незабываемым! "
                                       "Надеюсь, что подарок ты уже приготовил!", language).format(
                            fio=str(" ".join(birthday[FIO].values())).strip(),
                            age=str(datetime.utcnow().year - int(birthday[DATE][YEAR])),
                        )
                    )
                    remind7, remind1 = True, True
                elif datetime_birthday.timestamp() - datetime.utcnow().timestamp() <= 7 * 24 * 60 * 60 and remind7:
                    dispatcher.bot.send_message(
                        chat_id=account_record[0],
                        text=translate(
                            "У твоего друга менее чем через неделю день рождения!\\n\\n"
                            "Приготовь хороший подарок, надеюсь ты знаешь что бы он хотел! "
                            "Не забудь поздравить именинника и постарайся "
                            "сделать его день рождения незабываемым!", language)
                    )
                    remind7, remind1 = False, True
                command = self._postgres.commands().update_remind(remind7, remind1, account_id)
                self._postgres.execute(command)

# ------------------------------------------------------------------------------------------
#       PRIVATE METHODS
# ------------------------------------------------------------------------------------------

    def _send_create_message(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        self._status[account_id][STATUS] = CREATE
        keyboard = [
            [
                InlineKeyboardButton(translate("ФИО", language), callback_data=ADD_FIO),
                InlineKeyboardButton(translate("Дата рождения", language), callback_data=ADD_DATE)
            ],
            [
                InlineKeyboardButton(translate("Поздравление", language), callback_data=ADD_CONGRATULATION),
                InlineKeyboardButton(translate("Пожелания", language), callback_data=ADD_DESIRES)
            ],
            [
                InlineKeyboardButton(translate("Создать", language), callback_data=CREATE)
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        year = self._status[account_id][BIRTHDAY][DATE][YEAR]
        month = self._status[account_id][BIRTHDAY][DATE][MONTH]
        day = self._status[account_id][BIRTHDAY][DATE][DAY]

        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=translate("Давай посмотрим что получилось!", language),
            reply_markup=ReplyKeyboardRemove()
        )
        fio_value = ' '.join(value for value in self._status[account_id][BIRTHDAY][FIO].values() if value)
        congratulation = self._status[account_id][BIRTHDAY][CONGRATULATION]
        congratulation_value = congratulation if congratulation else translate("не задано", language)
        desires = self._status[account_id][BIRTHDAY][DESIRES]
        desires_value = desires if desires else translate("не задано", language)
        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text="{text}:\n\n"
                 "<b>{fio}</b>: {fio_value}\n"
                 "<b>{date}</b>: {date_value}\n"
                 "<b>{congratulation}</b>: {congratulation_value}\n"
                 "<b>{desires}</b>: {desires_value}".format(
                  text=translate("Анкета друга", language),
                  fio=translate("ФИО", language),
                  date=translate("Дата рождения", language),
                  congratulation=translate("Поздравление", language),
                  desires=translate("Пожелания", language),
                  fio_value=fio_value,
                  date_value="{0}-{1}-{2}".format(year, month, day),
                  congratulation_value=congratulation_value,
                  desires_value=desires_value),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

    def _it_is_time_for_birthday_after_create(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        birthday = self._status[account_id][BIRTHDAY]
        datetime_birthday = datetime(
            int(birthday[DATE][YEAR]),
            int(birthday[DATE][MONTH]),
            int(birthday[DATE][DAY]),
            0, 0, 0
        )
        remind7, remind1 = True, True
        datetime_birthday = datetime_birthday.replace(year=datetime.utcnow().year)
        if datetime.utcnow().timestamp() > datetime_birthday.timestamp():
            datetime_birthday = datetime_birthday.replace(year=datetime.utcnow().year + 1)
        if datetime_birthday.timestamp() - datetime.utcnow().timestamp() <= 24 * 60 * 60:
            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=translate("У твоего друга менее чем через сутки день рождения!\\n\\n"
                               "{fio} исполняется {age}!\\n\\n"
                               "Не забудь поздравить именинника и постарайся сделать его день рождения незабываемым! "
                               "Надеюсь, что подарок ты уже приготовил!", language).format(
                         fio=str(" ".join(birthday[FIO].values())).strip(),
                         age=str(datetime.utcnow().year - int(birthday[DATE][YEAR])),
                     )
            )
        elif datetime_birthday.timestamp() - datetime.utcnow().timestamp() <= 7 * 24 * 60 * 60:
            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=translate("У твоего друга менее чем через неделю день рождения!\\n\\n"
                               "Приготовь хороший подарок, надеюсь ты знаешь что бы он хотел! "
                               "Не забудь поздравить именинника и постарайся "
                               "сделать его день рождения незабываемым!", language)
            )
            remind7 = False
        command = self._postgres.commands().update_remind(remind7, remind1, account_id)
        self._postgres.execute(command)

# ------------------------------------------------------------------------------------------
#       CALLBACK QUERY METHODS
# ------------------------------------------------------------------------------------------

    def _language_in_callback_query(self, update, context):
        query_data = update.callback_query.data
        account_id = update.effective_user[ACCOUNT_ID]
        translate = self._translator.translate
        language = query_data
        command = self._postgres.commands().update_language(
            language_code=query_data,
            account_id=account_id
        )
        self._postgres.execute(command)
        self._status[account_id][LANGUAGE] = query_data
        self._status[account_id][STATUS] = NONE
        context.bot.edit_message_text(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            text=translate("Вы изменили язык на русский!", language)
        )

    def _add_fio_in_callback_query(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        self._status[account_id][STATUS] = ADD_FIO_LAST_NAME
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=translate("Введите фамилию друга", language)
        )

    def _add_date_in_callback_query(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        self._status[account_id][STATUS] = ADD_DATE_INTERVAL
        start_year = 1930
        keyboard = [
            [
                "{0} - {1}".format(
                    start_year + (2 * i + j) * 12, start_year + (2 * i + j) * 12 + 11
                ) for j in range(2)
            ] for i in range(4)
        ]
        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=translate("Введите интервал даты рождения", language),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=keyboard,
                resize_keyboard=True
            )
        )

    def _add_congratulation_in_callback_query(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        self._status[account_id][STATUS] = ADD_CONGRATULATION
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=translate("Введите поздравление для друга", language)
        )

    def _add_desires_in_callback_query(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        self._status[account_id][STATUS] = ADD_DESIRES
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            text=translate("Введите желания друга", language)
        )

    def _create_in_callback_query(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        context.bot.answer_callback_query(callback_query_id=update.callback_query.id)
        birthday = self._status[account_id][BIRTHDAY]
        year = birthday[DATE][YEAR]
        month = birthday[DATE][MONTH]
        day = birthday[DATE][DAY]
        command = self._postgres.commands().insert_birthday(
            last_name=birthday[FIO][LAST_NAME],
            first_name=birthday[FIO][FIRST_NAME],
            middle_name=birthday[FIO][MIDDLE_NAME],
            phone_number=birthday[PHONE_NUMBER],
            user_id=birthday[TELEGRAM_USER_ID],
            date="{0}-{1}-{2}".format(year, month, day),
            congratulation=birthday[CONGRATULATION],
            desires=birthday[DESIRES],
            remind7=True,
            remind1=True,
            account_id=account_id
        )
        self._postgres.execute(command)
        context.bot.edit_message_text(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            text=translate("Вы успешно добавили информацию о друге!", language)
        )
        self._it_is_time_for_birthday_after_create(update, context)
        self._status[account_id][STATUS] = NONE
        self._status[account_id][BIRTHDAY] = {}

    def _invalid_in_callback_query(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        context.bot.edit_message_text(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            text=translate("К сожалению, я не поддерживаю данное сообщение!", language)
        )

# ------------------------------------------------------------------------------------------
#       OTHER METHODS
# ------------------------------------------------------------------------------------------

    def _add_contact_in_other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        if update.effective_message[ATTACHMENTS_CONTACT]:
            birthday = self._status[account_id][BIRTHDAY]
            first_name = update.effective_message[CONTACT][FIRST_NAME]
            last_name = update.effective_message[CONTACT][LAST_NAME]
            phone_number = update.effective_message[CONTACT][PHONE_NUMBER]
            user_id = update.effective_message[CONTACT][TELEGRAM_USER_ID]
            birthday[FIO][LAST_NAME] = last_name if last_name and len(last_name) > 0 else NONE
            birthday[FIO][FIRST_NAME] = first_name if first_name and len(first_name) > 0 else NONE
            birthday[PHONE_NUMBER] = phone_number if phone_number and len(phone_number) > 0 else NONE
            birthday[TELEGRAM_USER_ID] = user_id if user_id else NONE
            self._status[account_id][STATUS] = ADD_DATE_INTERVAL
            start_year = 1930
            keyboard = [
                [
                    "{0} - {1}".format(
                        start_year + (2 * i + j) * 12, start_year + (2 * i + j) * 12 + 11
                    ) for j in range(2)
                ] for i in range(4)
            ]
            context.bot.send_message(
                chat_id=update.effective_message.chat_id,
                text=translate("Введите интервал даты рождения", language),
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=keyboard,
                    resize_keyboard=True
                )
            )
        else:
            context.bot.send_message(chat_id=update.effective_message.chat_id,
                                     text="Будьте так любезны, пришлите мне контакт именинника!")

    def _add_date_interval_in_other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        self._status[account_id][STATUS] = ADD_DATE_YEAR
        interval = update.effective_message.text
        begin = int(interval[0:4])
        keyboard = [
            [
                "{0}".format(begin + 3 * i + j) for j in range(3)
            ] for i in range(4)
        ]
        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=translate("Введите год даты рождения", language),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=keyboard,
                resize_keyboard=True
            )
        )

    def _add_date_year_in_other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        self._status[account_id][BIRTHDAY][DATE] = {
            YEAR: NONE,
            MONTH: NONE,
            DAY: NONE
        }
        self._status[account_id][BIRTHDAY][DATE][YEAR] = update.effective_message.text
        self._status[account_id][STATUS] = ADD_DATE_MONTH
        keyboard = [
            [
                translate(MONTH_LIST[3 * i + j], language) for j in range(3)
            ] for i in range(4)
        ]
        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=translate("Введите месяц даты рождения", language),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=keyboard,
                resize_keyboard=True
            )
        )

    def _add_date_month_in_other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        self._status[account_id][STATUS] = ADD_DATE_DAY
        month_arr = [translate(month, language) for month in MONTH_LIST]
        self._status[account_id][BIRTHDAY][DATE][MONTH] = str(month_arr.index(update.effective_message.text) + 1)
        year = int(self._status[account_id][BIRTHDAY][DATE][YEAR])
        month = int(self._status[account_id][BIRTHDAY][DATE][MONTH])
        days = calendar.monthrange(year, month)[1]
        keyboard = [
            [
                str(4 * i + j + 1) for j in range(4) if 4 * i + j + 1 <= days
            ] for i in range(days // 4 + 1)
        ]
        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=translate("Введите день даты рождения", language),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=keyboard,
                resize_keyboard=True
            )
        )

    def _add_date_day_in_other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        self._status[account_id][BIRTHDAY][DATE][DAY] = update.effective_message.text
        self._send_create_message(update, context)

    def _add_fio_last_name_in_other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        if update.effective_message.text:
            self._status[account_id][STATUS] = ADD_FIO_FIRST_NAME
            self._status[account_id][BIRTHDAY][FIO][LAST_NAME] = update.effective_message.text
            context.bot.send_message(
                chat_id=update.effective_message.chat_id,
                text=translate("Введите имя друга", language)
            )
        else:
            context.bot.send_message(
                chat_id=update.effective_message.chat_id,
                text=translate("Будьте так любезны, введите фамилию друга", language)
            )

    def _add_fio_first_name_in_other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        if update.effective_message.text:
            self._status[account_id][STATUS] = ADD_FIO_MIDDLE_NAME
            self._status[account_id][BIRTHDAY][FIO][FIRST_NAME] = update.effective_message.text
            context.bot.send_message(
                chat_id=update.effective_message.chat_id,
                text=translate("Введите отчество друга", language)
            )
        else:
            context.bot.send_message(
                chat_id=update.effective_message.chat_id,
                text=translate("Будьте так любезны, введите имя друга", language)
            )

    def _add_fio_middle_name_in_other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        if update.effective_message.text:
            self._status[account_id][BIRTHDAY][FIO][MIDDLE_NAME] = update.effective_message.text
            self._send_create_message(update, context)
        else:
            context.bot.send_message(
                chat_id=update.effective_message.chat_id,
                text=translate("Будьте так любезны, введите отчество друга", language)
            )

    def _add_congratulation_in_other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        if update.effective_message.text:
            self._status[account_id][BIRTHDAY][CONGRATULATION] = update.effective_message.text
            self._send_create_message(update, context)
        else:
            context.bot.send_message(
                chat_id=update.effective_message.chat_id,
                text=translate("Будьте так любезны, пришлите мне поздравление для именинника!", language)
            )

    def _add_desires_in_other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        if update.effective_message.text:
            self._status[account_id][BIRTHDAY][DESIRES] = update.effective_message.text
            self._send_create_message(update, context)
        else:
            context.bot.send_message(
                chat_id=update.effective_message.chat_id,
                text=translate("Будьте так любезны, пришлите мне пожелания к подарку для именинника!", language)
            )

    def _invalid_in_other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        self._status[account_id][STATUS] = CREATE if self._status[account_id][STATUS] == CREATE else NONE

        if update.effective_message[ATTACHMENTS_AUDIO]:
            self._audio_in_other_messages(update, context)
        elif update.effective_message[ATTACHMENTS_DOCUMENT]:
            self._document_in_other_messages(update, context)
        elif update.effective_message[ATTACHMENTS_PHOTO]:
            self._photo_in_other_messages(update, context)
        elif update.effective_message[ATTACHMENTS_STICKER]:
            self._sticker_in_other_messages(update, context)
        elif update.effective_message[ATTACHMENTS_VIDEO]:
            self._video_in_other_messages(update, context)
        elif update.effective_message[ATTACHMENTS_VOICE]:
            self._voice_in_other_messages(update, context)
        elif update.effective_message[ATTACHMENTS_VIDEO_NOTE]:
            self._video_note_in_other_messages(update, context)
        elif update.effective_message[ATTACHMENTS_CONTACT]:
            self._contact_note_in_other_messages(update, context)
        elif update.effective_message[ATTACHMENTS_LOCATION]:
            self._location_in_other_messages(update, context)
        elif update.effective_message[ATTACHMENTS_VENUE]:
            self._venue_in_other_messages(update, context)
        elif update.effective_message[ATTACHMENTS_GAME]:
            self._game_in_other_messages(update, context)
        elif update.effective_message[ATTACHMENTS_ANIMATION]:
            self._animation_in_other_messages(update, context)
        elif update.effective_message[ATTACHMENTS_INVOICE]:
            self._invoice_in_other_messages(update, context)
        elif update.effective_message[ATTACHMENTS_SUCCESSFUL_PAYMENT]:
            self._successful_payment_in_other_messages(update, context)
        else:
            self._unprocessed_other_messages(update, context)

# ------------------------------------------------------------------------------------------
#       ATTACHMENT METHODS
# ------------------------------------------------------------------------------------------

    def _audio_in_other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=translate("У вас определенно хороший музыкальный вкус!", language)
        )

    def _document_in_other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=translate("Я обязательно прочту ваш документ и напишу рецензию!", language)
        )

    def _photo_in_other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=translate("Как вы смеете мне присылать такие фото!", language)
        )

    def _sticker_in_other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=translate("У меня есть набор стикеров поинтереснее!", language)
        )

    def _video_in_other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=translate("Это видео я отправлю в Роскомнадзор, там с вами разберутся!", language)
        )

    def _voice_in_other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=translate("Какой милый голосок! Прочитай мне сказку!", language)
        )

    def _video_note_in_other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=translate("Если я буду присылать такие видео как проснусь, то я буду выглядеть намного лучше!", language)
        )

    def _contact_note_in_other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=translate("ФСБ проверит твой контакт, я уже передал!", language)
        )

    def _location_in_other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=translate("Если там собираются красивые девушки, то я уже выезжаю!", language)
        )

    def _venue_in_other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=translate("Там определенно продаются самые вкусные пончики в мире!", language)
        )

    def _game_in_other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=translate("Я в такие игры не играю! Я еще маленький!", language)
        )

    def _animation_in_other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=translate("Рассмашил так рассмешил! Мне понравилось!", language)
        )

    def _invoice_in_other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=translate("Я такого не заказывал! Хочу оформить возврат!", language)
        )

    def _successful_payment_in_other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=translate("Если вы отдаете мне это бесплатно, то я готов принять подарок!", language)
        )

    def _unprocessed_other_messages(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=translate("К сожалению, я не поддерживаю данное сообщение!", language)
        )

# ------------------------------------------------------------------------------------------
