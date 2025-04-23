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

@bot.message_handler(func=lambda message: message.from_user.username in ['kristina_superstar', 'gothicspring', 'Kungfuoko'])
def echo_all(message):
    attempt_count = 0
    sent_message = bot.reply_to(message, 'Секундочку...')  # всегда одно сообщение, одно удаление

    while True:
        attempt_count += 1

        try:
            txt = message.text + " по-русски"

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(g4f.ChatCompletion.create, model=g4f.models.gpt_4, messages=[ 
                    {"role": "system", "content": "ответь по-русски, если в твоем ответе есть код, цитаты или другая подходящая информация то оберни ту часть в теги pre по примеру <pre>текст</pre>"},
                    {"role": "user", "content": txt}
                ])

                try:
                    response = future.result(timeout=1)
                except concurrent.futures.TimeoutError:
                    continue  # пробуем снова

            if attempt_count >= 20:
                bot.delete_message(message.chat.id, sent_message.message_id)
                bot.reply_to(message, "Ошибка нейросети — превышено количество попыток 🕘")
                break

            response = response.replace("**", "<pre>").replace("**", "</pre>")

            if has_glyphs(response):
                continue  # не удаляем сообщение, просто пробуем ещё раз

            bot.delete_message(message.chat.id, sent_message.message_id)  # ✅ удаляем только здесь

            if "<pre>" in response:
                bot.reply_to(message, response, parse_mode='HTML')
            else:
                bot.reply_to(message, response)

            break

        except Exception as e:
            print("Ошибка:", e)
            continue  # сообщение "Секундочку..." остаётся до следующей попытки


    attempt_count = 0  # сброс счетчика попыток после успешной отправки

bot.polling()  # старт бота
