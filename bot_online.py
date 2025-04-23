import os
import asyncio
import telebot
import g4f
import unicodedata
from html import escape
import re
import concurrent.futures
import time  # добавлено для использования time.time()

telegram_token = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(telegram_token)

def has_glyphs(text):
    for char in text:
        if unicodedata.category(char) == 'Lo':
            return True
    return False

@bot.message_handler(func=lambda message: message.from_user.username in ['kristina_superstar', 'gothicspring', 'Kungfuoko'])
def echo_all(message):
    attempt_count = 0  # счетчик попыток отправки
    sent_message = None  # Переменная для хранения ID отправленного сообщения

    while attempt_count < 20:  # Ограничиваем количество попыток
        attempt_count += 1

        try:
            # Отправляем сообщение "Секундочку..." только один раз
            if sent_message is None:
                sent_message = bot.reply_to(message, f'Секундочку... #{attempt_count}' if attempt_count > 1 else 'Секундочку...')

            txt = message.text + " по-русски"
            start_time = time.time()

            # обработчик задержки ответа от ИИ
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(g4f.ChatCompletion.create, model=g4f.models.gpt_4, messages=[ 
                    {"role": "system", "content": "ответь по-русски, если в твоем ответе есть код, цитаты или другая подходящая информация то оберни ту часть в теги pre по примеру <pre>текст</pre>"},
                    {"role": "user", "content": txt}
                ])
                
                try:
                    response = future.result(timeout=1)  # ждём ровно 1 секунду
                except concurrent.futures.TimeoutError:
                    continue  # Пробуем снова, если ответ не пришел вовремя

            # Обработка ответа
            response = response.replace("**", "<pre>").replace("**", "</pre>")  # Замена для тегов pre

            if has_glyphs(response):
                continue  # Если в ответе есть глифы, пробуем снова

            # Удаляем сообщение "Секундочку..." перед отправкой окончательного ответа
            if sent_message:
                bot.delete_message(message.chat.id, sent_message.message_id)

            # Отправка ответа пользователю
            if "<pre>" in response:
                bot.reply_to(message, response, parse_mode='HTML')
            else:
                bot.reply_to(message, response)

            break  # Прерываем цикл, если ответ успешно отправлен

        except telebot.apihelper.ApiTelegramException as e:
            # Обработка ошибки API Telegram
            bot.delete_message(message.chat.id, sent_message.message_id)  # Удаляем сообщение "Секундочку..."
            continue  # Пробуем снова

        except Exception as e:
            # Обработка других ошибок
            bot.delete_message(message.chat.id, sent_message.message_id)  # Удаляем сообщение "Секундочку..."
            continue  # Пробуем снова

    else:
        # Если попытки превышают максимальное количество
        bot.reply_to(message, "Ошибка нейросети — превышено количество попыток 🕘")

bot.polling()  # старт бота
