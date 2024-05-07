import os
import signal
import asyncio
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from g4f.client import Client

# Получаем токен из переменной среды TELEGRAM_TOKEN
telegram_token = os.getenv('TELEGRAM_TOKEN')

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