import os
import signal
import asyncio
from telegram import Bot, Update
from telegram import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from g4f.client import Client

telegram_token = os.getenv('TELEGRAM_TOKEN')
channel_id = '@my_bot_test_666'

def send_message(message):
    bot = Bot(token=telegram_token)
    bot.send_message(chat_id=channel_id, text=message)

signal.signal(signal.SIGTERM, lambda signum, frame: send_message("bot stop"))

send_message("bot start")
client = Client()

# Функция для обработки всех входящих сообщений от пользователя
async def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text

    role_system = "Отвечай на запросы как обычно"
    role_user = user_message

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[ 
            {"role": "system", "content": role_system},
            {"role": "user", "content": role_user}
        ],
    )

    generated_response = completion.choices[0].message.content
    await context.bot.send_message(chat_id=update.message.chat_id, text=generated_response)

# Создаем обновление и настраиваем бота
updater = Updater(token=telegram_token)
dispatcher = updater.dispatcher

# Регистрируем обработчик всех входящих сообщений от пользователя
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Запускаем асинхронный цикл для обработки входящих сообщений
async def main():
    await updater.start_polling()
    await updater.idle()

# Запускаем асинхронный цикл
asyncio.run(main())

send_message("bot stop")
