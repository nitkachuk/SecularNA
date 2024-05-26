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
    attempt_count = 0  # счетчик попыток отправки
    while True:
        try:
            attempt_count += 1  # увеличение счетчика попыток
            if attempt_count > 1:
                sent_message = bot.reply_to(message, f'Секундочку... #{attempt_count}')  # ответ 1
            else:
                sent_message = bot.reply_to(message, 'Секундочку...')  # ответ 1

            if attempt_count > 10:
                bot.delete_message(message.chat.id, sent_message.message_id)  # Удаление сообщения "Секундочку..."
                bot.reply_to(message, "Ошибка нейросети")  # ответ 2
                break

            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    #{"role": "system", "content": ''},
                    {"role": "user", "content": message.text}
                ],
            )

            if has_glyphs(completion.choices[0].message.content):
                bot.delete_message(message.chat.id, sent_message.message_id)  # Удаление сообщения "Секундочку..."
                continue

            bot.delete_message(message.chat.id, sent_message.message_id)  # Удаление сообщения "Секундочку..."
            bot.reply_to(message, completion.choices[0].message.content)  # ответ 2

            break

        except telebot.apihelper.ApiTelegramException as e:
            # Обработка исключения, чтобы скрипт не завершался при ошибке API Telegram
            err = "Произошла ошибка API Telegram"
            print(err, e)
            bot.delete_message(message.chat.id, sent_message.message_id)  # Удаление сообщения "Секундочку..."
            continue

        except Exception as e:
            # Другие исключения
            err = "Произошла неизвестная ошибка"
            print(err, e)
            bot.delete_message(message.chat.id, sent_message.message_id)  # Удаление сообщения "Секундочку..."
            continue 

    attempt_count = 0  # сброс счетчика попыток после успешной отправки

bot.polling()
