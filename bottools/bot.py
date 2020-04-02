from translationtools.language import Translator
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
)
from .constants import *
from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
)
# from datetime import (
#     datetime, timedelta
# )
import os


class Bot:
    def __init__(self, logger, postgres):
        self._status = {}
        self._logger = logger
        self._postgres = postgres
        self._updater = Updater(token=BOT_TOKEN, use_context=True)
        self._translator = Translator(file="translationtools/translation.xml")
        self._set_commands()
        self._update_status()
        self._set_job_queue()

    def _set_commands(self):
        dispatcher = self._updater.dispatcher
        dispatcher.add_handler(CommandHandler(START, self._start))
        dispatcher.add_handler(CommandHandler(ADD, self._add))
        dispatcher.add_handler(CommandHandler(LANGUAGE, self._language))
        dispatcher.add_handler(CommandHandler(HELP, self._help))
        dispatcher.add_handler(CommandHandler(CANCEL, self._cancel))
        dispatcher.add_handler(CallbackQueryHandler(self._callback_query))
        dispatcher.add_handler(MessageHandler(Filters.all, self._other_message))

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
        # to = now + timedelta(seconds=2 * 60)
        # to = to.replace(hour=0, minute=0, second=0, microsecond=0)
        # self._updater.job_queue.run_repeating(self._it_is_time_for_birthday,
        #                                       interval=24 * 60 * 60,
        #                                       first=to.timestamp() - now.timestamp())

        # повторение каждые 2 минуты
        # self._updater.job_queue.run_once(self._it_is_time_for_birthday,
        #                                  when=35 * 60)

    def start_pooling(self):
        """
        при деплое на Heroku раскомментировать 62-65 строки,
        и закомментировать 68 строку
        """
        # port = int(os.environ.get("PORT", WEB_HOOK_PORT)),
        self._updater.start_webhook(listen=WEB_HOOK_ADDRESS,
                                    port=int(WEB_HOOK_PORT),
                                    url_path=BOT_TOKEN)
        self._updater.bot.set_webhook(HEROKU_APP_URL + BOT_TOKEN)

        # self._updater.start_polling()
        self._updater.idle()

    def _it_is_time_for_birthday(self, dispatcher):
        pass
        # dispatcher.bot.send_message(chat_id=513814634,
        #                             text="Я завладел job_queue, бу - га - га")
        # while True:
        #     print(self._status[513814634][STATUS])
        # account_command = self._postgres.commands().select_account()
        # account_records = self._postgres.execute(account_command)
        # for account_record in account_records:
        #     birthday_command = self._postgres.commands().select_birthday_for_account(account_record[0])
        #     birthday_records = self._postgres.execute(birthday_command)
        #     for birthday_record in birthday_records:
        #         datetime_birthday = datetime.strptime(birthday_record[4].strftime("%Y-%m-%d"), "%Y-%m-%d")
        #         datetime_birthday = datetime_birthday.replace(year=datetime.utcnow().year)
        #         if abs(datetime_birthday.timestamp() - datetime.utcnow().timestamp()) <= 7 * 24 * 60 * 60:
        #             # если до др меньше недели
        #             dispatcher.bot.send_message(chat_id=account_record[0],
        #                                         text="У твоего пидрилы, {fio}, скоро др!".format(
        #                                             fio=birthday_record[3]+birthday_record[1]+birthday_record[2]
        #                                         ))

    def _start(self, update, context):
        self._logger.warning("Someone wants to join my bot")
        account_id = update.effective_user[ACCOUNT_ID]
        self._status[account_id] = {LANGUAGE: EN, STATUS: NONE}
        command = self._postgres.commands().insert_account(
            account_id=account_id,
            first_name=update.effective_user[FIRST_NAME],
            last_name=update.effective_user[LAST_NAME],
            user_name=update.effective_user[USERNAME],
            language_code=EN
        )
        self._postgres.execute(command)
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=self._translator.translate(message="Привет, я бот и я рад тебя приветствовать!",
                                                                 language=self._status[account_id][LANGUAGE]
                                                                 )
                                 )

    def _add(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        self._status[account_id][STATUS] = ADD
        self._status[account_id][BIRTHDAY] = {
            FIO: "не задано",
            DATE: "не задано",
            CONGRATULATION: "не задано",
            DESIRES: "не задано"
        }
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        keyboard = [
            [
                InlineKeyboardButton(translate("ФИО", language), callback_data=FIO),
                InlineKeyboardButton(translate("Дата рождения", language), callback_data=DATE)
            ],
            [
                InlineKeyboardButton(translate("Поздравление", language), callback_data=CONGRATULATION),
                InlineKeyboardButton(translate("Пожелания", language), callback_data=DESIRES)
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text="{text}:\n\n"
                 "<b>{fio}</b>: {fio_value}\n"
                 "<b>{date}</b>: {date_value}\n"
                 "<b>{congratulation}</b>: {congratulation_value}\n"
                 "<b>{desires}</b>: {desires_value}".format(
                     text=translate("Создадим дату рождения для друга", language),
                     fio=translate("ФИО", language),
                     date=translate("Дата рождения", language),
                     congratulation=translate("Поздравление", language),
                     desires=translate("Пожелания", language),
                     fio_value=translate(self._status[account_id][BIRTHDAY][FIO], language),
                     date_value=translate(self._status[account_id][BIRTHDAY][DATE], language),
                     congratulation_value=translate(self._status[account_id][BIRTHDAY][CONGRATULATION], language),
                     desires_value=translate(self._status[account_id][BIRTHDAY][DESIRES], language)
                 ),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

    def _language(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        self._status[account_id][STATUS] = LANGUAGE
        language = self._status[account_id][LANGUAGE]
        languages = [(key, value) for key, value in self._translator.languages().items() if key != language]
        keyboard = [
            [
                InlineKeyboardButton(languages[0][1], callback_data=languages[0][0]),
                InlineKeyboardButton(languages[1][1], callback_data=languages[1][0])
            ],
            [
                InlineKeyboardButton(languages[2][1], callback_data=languages[2][0]),
                InlineKeyboardButton(languages[3][1], callback_data=languages[3][0])
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=self._translator.translate(message="Сейчас установленный язык русский. На какой Вы желаете изменить?",
                                            language=self._status[account_id][LANGUAGE]),
            reply_markup=reply_markup
        )

    def _help(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        self._status[account_id][STATUS] = NONE
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=translate("Это меню, которое расскажет что ты можешь.", language))

    def _cancel(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        self._status[account_id][STATUS] = NONE
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=translate("Текущая операция была отменена.", language))

    def _callback_query(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        query_data = update.callback_query.data
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        status = self._status[account_id][STATUS]
        if status == LANGUAGE:
            command = self._postgres.commands().update_language(
                language_code=query_data,
                account_id=account_id
            )
            self._postgres.execute(command)
            self._status[account_id][LANGUAGE] = query_data
            self._status[account_id][STATUS] = NONE
            language = query_data
            context.bot.edit_message_text(
                chat_id=update.callback_query.message.chat_id,
                message_id=update.callback_query.message.message_id,
                text=translate("Вы изменили язык на русский!", language)
            )
        elif ADD in status:
            context.bot.answer_callback_query(callback_query_id=update.callback_query.id)
            if query_data == FIO:
                self._status[account_id][STATUS] = ADD_FIO
                context.bot.send_message(
                    chat_id=update.callback_query.message.chat_id,
                    text=translate("Введите ФИО друга", language)
                )
            elif query_data == DATE:
                self._status[account_id][STATUS] = ADD_DATE
                context.bot.send_message(
                    chat_id=update.callback_query.message.chat_id,
                    text=translate("Введите дату рождения друга", language)
                )
            elif query_data == CONGRATULATION:
                self._status[account_id][STATUS] = ADD_CONGRATULATION
                context.bot.send_message(
                    chat_id=update.callback_query.message.chat_id,
                    text=translate("Введите поздравление для друга", language)
                )
            elif query_data == DESIRES:
                self._status[account_id][STATUS] = ADD_DESIRES
                context.bot.send_message(
                    chat_id=update.callback_query.message.chat_id,
                    text=translate("Введите желания друга", language)
                )
        elif status == CREATE:
            context.bot.answer_callback_query(callback_query_id=update.callback_query.id)
            birthday = self._status[account_id][BIRTHDAY]
            fio = birthday[FIO].split()
            command = self._postgres.commands().insert_birthday(
                last_name=fio[0],
                first_name=fio[1],
                middle_name=fio[2],
                date=birthday[DATE],
                congratulation=birthday[CONGRATULATION],
                desires=birthday[DESIRES],
                account_id=account_id
            )
            self._postgres.execute(command)
            self._status[account_id][STATUS] = NONE
            self._status[account_id][BIRTHDAY] = {}
            context.bot.send_message(chat_id=update.effective_message.chat_id,
                                     text=translate("Вы успешно добавили др друга!", language)
                                     )

    def _other_message(self, update, context):
        account_id = update.effective_user[ACCOUNT_ID]
        language = self._status[account_id][LANGUAGE]
        translate = self._translator.translate
        status = self._status[account_id][STATUS]
        if ADD in status:
            self._status[account_id][BIRTHDAY][status[4:]] = update.effective_message.text
            keyboard = []
            if self._birthday_is_valid(account_id):
                self._status[account_id][STATUS] = CREATE
                keyboard.append(
                    [
                        InlineKeyboardButton(translate("Создать", language), callback_data=CREATE)
                    ]
                )
            else:
                self._status[account_id][STATUS] = ADD
                keyboard.append(
                    [
                        InlineKeyboardButton(translate("ФИО", language), callback_data=FIO),
                        InlineKeyboardButton(translate("Дата рождения", language), callback_data=DATE)
                    ]
                )
                keyboard.append(
                    [
                        InlineKeyboardButton(translate("Поздравление", language), callback_data=CONGRATULATION),
                        InlineKeyboardButton(translate("Пожелания", language), callback_data=DESIRES)
                    ]
                )
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(
                chat_id=update.effective_message.chat_id,
                text="{text}:\n\n"
                     "<b>{fio}</b>: {fio_value}\n"
                     "<b>{date}</b>: {date_value}\n"
                     "<b>{congratulation}</b>: {congratulation_value}\n"
                     "<b>{desires}</b>: {desires_value}".format(
                        text=translate("Создадим дату рождения для друга", language),
                        fio=translate("ФИО", language),
                        date=translate("Дата рождения", language),
                        congratulation=translate("Поздравление", language),
                        desires=translate("Пожелания", language),
                        fio_value=self._status[account_id][BIRTHDAY][FIO],
                        date_value=self._status[account_id][BIRTHDAY][DATE],
                        congratulation_value=self._status[account_id][BIRTHDAY][CONGRATULATION],
                        desires_value=self._status[account_id][BIRTHDAY][DESIRES]
                     ),
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
        else:
            self._status[account_id][STATUS] = NONE
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text=translate("К сожалению, я не поддерживаю данное сообщения.", language))

    def _birthday_is_valid(self, account_id):
        flag = True
        for _, value in self._status[account_id][BIRTHDAY].items():
            flag = flag and (value != "не задано")
        return flag
