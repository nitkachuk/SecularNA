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
    
    while True:    
        attempt_count += 1

        try:
            last_message = bot.get_chat_history(message.chat.id, limit=1)[0]  # Получаем последнее сообщение
            if last_message.text.lower() == "секундочку...":
                bot.delete_message(message.chat.id, last_message.message_id)  # Удаляем, если оно "секундочку..."
        except Exception:
            pass  # Ошибки игнорируются, просто продолжаем выполнение
        
        try:
            if attempt_count > 1:
                sent_message = bot.reply_to(message, f'Секундочку... #{attempt_count}')  # ответ 1
            else:
                sent_message = bot.reply_to(message, 'Секундочку...')  # ответ 1

            # if attempt_count >= 10:
            #     bot.delete_message(message.chat.id, sent_message.message_id)  # Удаление сообщения "Секундочку..."
            #     bot.reply_to(message, "Ошибка нейросети")  # ответ 2
            #     break

            txt = message.text + " по-русски"
            start_time = time.time()

            # обработчик задержки ответа от ИИ
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(g4f.ChatCompletion.create, model=g4f.models.gpt_4, messages=[ 
                    {"role": "system", "content": "ответь по-русски, если в твоем ответе есть код, цитаты или другая подходящая информация то оберни ту часть в теги pre по примеру <pre>текст</pre>"},
                    {"role": "user", "content": txt}
                ])
                
                try:
                    try:
                        response = future.result(timeout=1)  # ждём ровно 5 секунд
                    except concurrent.futures.TimeoutError:
                        #bot.delete_message(message.chat.id, sent_message.message_id)
                        continue  # считаем как неудачную попытку и пробуем заново
                except concurrent.futures.TimeoutError:
                    #bot.delete_message(message.chat.id, sent_message.message_id)
                    #bot.reply_to(message, f"Секундочку... #{attempt_count}")
                    continue  # Продолжаем цикл с новой попыткой

            # обработка ответа
            if attempt_count >= 20:
                response = "Ошибка нейросети — превышено количество попыток 🕘"
                break

            response = response.replace("**", "<pre>").replace("**", "</pre>")  # Замена для тегов pre

            if has_glyphs(response):
                bot.delete_message(message.chat.id, sent_message.message_id)  # Удаление сообщения "Секундочку..."
                continue

            bot.delete_message(message.chat.id, sent_message.message_id)  # Удаление сообщения "Секундочку..."
            if "<pre>" in response:
                bot.reply_to(message, response, parse_mode='HTML')  # ответ с кодом в цитате
            else:
                bot.reply_to(message, response)  # обычный ответ

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
            continue  # Продолжаем цикл с новой попыткой

    attempt_count = 0  # сброс счетчика попыток после успешной отправки

bot.polling()  # старт бота
