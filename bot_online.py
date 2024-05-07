import os
import signal
import asyncio
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from g4f.client import Client

# Получаем токен из переменной среды TELEGRAM_TOKEN
telegram_token = os.getenv('TELEGRAM_TOKEN')
# Указываем ID канала, куда будем постить сообщения
channel_id = '@my_bot_test_666'

# Функция для отправки сообщения в канал
def send_message(message):
    bot = Bot(token=telegram_token)
    bot.send_message(chat_id=channel_id, text=message)

# Функция для отправки сообщения при остановке бота
def stop_bot():
    send_message("bot stop")

# Обработчик события SIGTERM для отправки сообщения перед остановкой
def handle_sigterm(signum, frame):
    stop_bot()
    raise SystemExit

# Регистрируем обработчик события SIGTERM
signal.signal(signal.SIGTERM, handle_sigterm)

# Отправляем сообщение о запуске бота
send_message("bot start")

# Инициализация клиента для GPT-3.5
client = Client()

# Функция для обработки всех входящих сообщений от пользователя
async def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text

    # Запрос на генерацию ответа от GPT-3.5
    role_system = "Отвечай на запросы как обычно"
    role_user = user_message

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[ 
            {"role": "system", "content": role_system},
            {"role": "user", "content": role_user}
        ],
    )

    # Получаем сгенерированный ответ
    generated_response = completion.choices[0].message.content

    # Отправляем сгенерированный ответ пользователю
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

# Перед завершением работы отправляем сообщение в канал
stop_bot()
