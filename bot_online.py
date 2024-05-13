import os
import asyncio
import telebot
from g4f.client import Client
import unicodedata

telegram_token = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(telegram_token)
client = Client()

def has_glyphs(text):
    for char in text:
        if unicodedata.category(char) == 'Lo':
            return True
    return False

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    while True:
        try:
            sent_message = bot.reply_to(message, 'Секундочку...')  # ответ 1

            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": 'ответь на запрос без иероглифов'},
                    {"role": "user", "content": message.text}
                ],
            )

            if has_glyphs(completion.choices[0].message.content):
                continue  # Пропускаем отправку сообщения и повторяем цикл

            bot.delete_message( message.chat.id, sent_message.message_id )  # удаление ответа 1
            bot.reply_to( message, completion.choices[0].message.content )  # ответ 2

            print( completion.choices[0].message )

            break  # выход из цикла while после успешного выполнения

        except telebot.apihelper.ApiTelegramException as e:
            # Обработка исключения, чтобы скрипт не завершался при ошибке API Telegram
            err = "Произошла ошибка API Telegram"
            print(err, e)
            continue  # переход на следующую итерацию цикла while

        except Exception as e:
            # Другие исключения
            err = "Произошла неизвестная ошибка"
            print(err, e)
            continue  # переход на следующую итерацию цикла while

bot.polling()
