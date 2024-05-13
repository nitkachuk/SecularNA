import os
import asyncio
import telebot
from g4f.client import Client

telegram_token = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(telegram_token)
client = Client()

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    try:
        sent_message = bot.reply_to(message, 'Секундочку...')  # ответ 1

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": 'ответь на запрос без иероглифов'},
                {"role": "user", "content": message.text}
            ],
        )

        bot.delete_message( message.chat.id, sent_message.message_id )  # удаление ответа 1
        bot.reply_to( message, completion.choices[0].message.content )  # ответ 2

        print( completion.choices[0].message )

    except telebot.apihelper.ApiTelegramException as e:
        # Обработка исключения, чтобы скрипт не завершался при ошибке API Telegram
        err = "Произошла ошибка API Telegram"
        print(err, e)

        # try:
        #     bot.reply_to(message, err)
        # except:
        #     pass

        # print( "ответ нейронки: ", sent_message.message_id )

        echo_all(message)

    except Exception as e:
        # Другие исключения
        err = "Произошла неизвестная ошибка"
        print(err, e)
        
        # try:
        #     bot.reply_to(message, err)
        # except:
        #     pass

        echo_all(message)

bot.polling()
