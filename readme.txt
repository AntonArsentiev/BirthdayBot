************************************************************

    PROCFILE

worker: python main.py
web: python main.py

************************************************************

	GIT

1. git clone https://github.com/AntonArsentiev/BirthdayBot.git
2. git add .
3. git commit -m "first commit"
4. git push origin

git remote add origin https://github.com/AntonArsentiev/BirthdayBot.git
git push origin master

************************************************************

	HEROKU
	
1. сделать deploy через github
2. посмотреть логи 
	heroku logs --tail --app=arsentiev-birthday-bot
3. запуск бота
	heroku ps:scale worker=1 --app=arsentiev-birthday-bot 
4. остановка бота
	heroku ps:scale worker=0 --app=arsentiev-birthday-bot 
	
************************************************************

Команды:

add - adding your friend's birthday
language - setting your locale
help - menu that tell what you can
cancel - cancel the current operation













       if update.callback_query.data in ['first_name', 'last_name', 'data']:
            context.bot.edit_message_text(
                chat_id=update.callback_query.message.chat_id,
                message_id=update.callback_query.message.message_id,
                text="Введите - {0}".format(update.callback_query.data)
            )
        elif update.callback_query.data == 'arrive_to_adding':
            keyboard = [
                [
                    InlineKeyboardButton('Имя', callback_data='first_name'),
                    InlineKeyboardButton('Фамилия', callback_data='last_name')
                ],
                [
                    InlineKeyboardButton('Дата', callback_data='data')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.edit_message_text(
                chat_id=update.callback_query.message.chat_id,
                message_id=update.callback_query.message.message_id,
                text="Мы вернулись к добавлению",
                reply_markup=reply_markup
            )
        else:
            context.bot.send_message(
                chat_id=update.effective_message.chat_id,
                text="Что-то пошло не так!"
            )
			
			
			
			
			# chat_id = update.callback_query.message.chat_id,
            # message_id = update.callback_query.message.message_id,
			
			
			
			
			
			            [
                InlineKeyboardButton(translate("Фамилия", language), callback_data="last_name"),
                InlineKeyboardButton("Имя", callback_data="first_name"),
                InlineKeyboardButton("Отчество", callback_data="last_name")
            ],
            [
                InlineKeyboardButton("Дата", callback_data="date"),
                InlineKeyboardButton("Поздравление", callback_data="congratulation"),
                InlineKeyboardButton("Пожелания", callback_data="desires")
            ]






# if self._status in ['first_name', 'last_name', 'data']:
        #     context.bot.delete_message(chat_id=update.effective_message.chat_id,
        #                                message_id=update.effective_message.message_id)
        #     keyboard = [
        #         [
        #             InlineKeyboardButton('Вернуться к настройкам', callback_data='arrive_to_adding'),
        #             InlineKeyboardButton('Завершить', callback_data='exit')
        #         ]
        #     ]
        #     reply_markup = InlineKeyboardMarkup(keyboard)
        #     context.bot.send_message(
        #         chat_id=update.effective_message.chat_id,
        #         text="Успешно введено - {0}".format(self._status),
        #         reply_markup=reply_markup
        #     )
        # else:
        # self._status = ''