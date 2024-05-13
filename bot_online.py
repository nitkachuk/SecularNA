import os
import asyncio
import telebot
from g4f.client import Client

telegram_token = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(telegram_token)
client = Client()

sent_message = bot.reply_to(message, 'старт...')  # ответ 1

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    sent_message = bot.reply_to(message, 'Секундочку...')  # ответ 1

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": 'ответь на запрос по-русски'},
                {"role": "user", "content": message.text}
            ],
        )

        if completion.choices:
            bot.delete_message(message.chat.id, sent_message.message_id)  # удаление ответа 1
            bot.reply_to(message, completion.choices[0].message.content)  # ответ 2
        else:
            bot.reply_to(message, "Сбой обращения к нейронной сети: получен пустой ответ")
    except Exception as e:
        bot.delete_message(message.chat.id, sent_message.message_id)  # удаление ответа 1
        bot.reply_to(message, "Сбой обращения к нейронной сети: " + str(e))  # ответ 3

bot.polling()
