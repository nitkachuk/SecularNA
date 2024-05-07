import os
from telegram import Bot

# Получаем токен из переменной окружения
telegram_token = os.getenv('TELEGRAM_TOKEN')

# ID чата или канала, куда будем отправлять сообщения
channel_id = '@my_bot_test_666'

# Функция для отправки сообщения
def send_message(message):
    bot = Bot(token=telegram_token)
    bot.send_message(chat_id=channel_id, text=message)

# Отправляем сообщение "bot start" при запуске
send_message("bot start")

# Действия бота...

# Например, здесь можно добавить обработчики для ответа на сообщения пользователей

# При выключении отправляем сообщение "bot stop"
send_message("bot stop")
