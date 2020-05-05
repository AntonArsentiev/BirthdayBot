************************************************************

        PROCFILE

worker: python main.py
web: python main.py

************************************************************

	    GIT

Способ №1

    git clone https://github.com/AntonArsentiev/BirthdayBot.git
    git add .
    git commit -m "first commit"
    git push origin

Способ №2

    git init
    git add .
    git commit -m "first commit"
    git remote add origin https://github.com/AntonArsentiev/BirthdayBot.git
    git push origin master

************************************************************

	    HEROKU
	
1. Посмотреть логи
	heroku logs --tail --app=arsentiev-birthday-bot

2. Запустить бота
	heroku ps:scale web=1 --app=arsentiev-birthday-bot

3. Остановить бота
	heroku ps:scale web=0 --app=arsentiev-birthday-bot

4. Включить техническое обслуживание
    heroku maintenance:on --app=arsentiev-birthday-bot

5. Выключить техническое обслуживание
    heroku maintenance:off --app=arsentiev-birthday-bot

Heroku Error Codes
    https://devcenter.heroku.com/articles/error-codes/

UptimeRobot
    https://uptimerobot.com/
	
************************************************************

        TELEGRAM BOT COMMANDS

add - add your friend's birthday
language - set your locale
help - i will tell what you can do

************************************************************
