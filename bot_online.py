import os
import signal
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.dispatcher import filters

from g4f.client import Client

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

# Получаем токен из переменной окружения
telegram_token = os.getenv('TELEGRAM_TOKEN')

# Создаем объект бота и диспетчер
bot = Bot(token=telegram_token, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)

# Инициализируем клиент GPT-3
client = Client()

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет! Я помогу тебе узнать твой ID, просто отправь мне любое сообщение")

# Обработчик всех остальных текстовых сообщений
@dp.message_handler(filters.Text & ~filters.Command())
async def echo_message(message: types.Message):
    role_system = "Отвечай на запросы как обычно"
    role_user = message.text

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[ 
            {"role": "system", "content": role_system},
            {"role": "user", "content": role_user}
        ],
    )

    generated_response = completion.choices[0].message.content
    await message.answer(generated_response)

async def main():
    # Стартуем бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(allowed_updates=types.Update.all_updates())

# Запускаем асинхронный цикл
asyncio.run(main())
