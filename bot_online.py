import os
import asyncio
import telebot
import g4f
import unicodedata
import re
import threading
import queue

telegram_token = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(telegram_token)

response = ""

def g4f_with_timeout(txt, timeout=10):
    global response
    
    messages = [
                {"role": "system", "content": "ответь по-русски, если есть блоки кода или цитат или списков, то оберни их в pre по примеру <pre>текст</pre>"},
                {"role": "user", "content": txt}
            ]
    
    q = queue.Queue()

    def worker():
        try:
            result = g4f.ChatCompletion.create(
                model=g4f.models.gpt_4,
                messages=messages
            )
            q.put(result)
        except Exception as e:
            q.put(e)

    t = threading.Thread(target=worker)
    t.start()
    t.join(timeout)

    if t.is_alive():
        return ""

    result = q.get()
    if isinstance(result, Exception):
        raise result
    return result

def has_glyphs(text):
    for char in text:
        if unicodedata.category(char) == 'Lo':
            return True
    return False

#@bot.message_handler(func=lambda message: True)
#@bot.message_handler(func=lambda message: message.from_user.username == 'kristina_superstar')

@bot.message_handler(func=lambda message: message.from_user.username in ['kristina_superstar', 'gothicspring', 'Kungfuoko'])

def echo_all(message):
    attempt_count = 0      # счетчик попыток отправки
    err = ''    # Текст ошибок в "Секундочку..."
    global response
    
    while True:
        try:
            attempt_count += 1  # увеличение счетчика попыток
            if attempt_count > 1:
                bot.delete_message(message.chat.id, sent_message.message_id)  # Удаление сообщения "Секундочку..."
                sent_message = bot.reply_to(message, f'Секундочку... #{attempt_count} ({err})')  # ответ 1
                err = ''
            else:
                sent_message = bot.reply_to(message, 'Секундочку...')  # ответ 1

            if attempt_count >= 5:
                bot.reply_to(message, "Превышено количество попыток.")  # ответ 2
                break

            txt = message.text + " по-русски"

            response = g4f_with_timeout( txt )
            if response == "":
                err = 'таймаут g4f'
                continue
            
            response = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', response)


            if has_glyphs( response ):
                err = 'иероглифы'
                continue

            bot.delete_message(message.chat.id, sent_message.message_id)  # Удаление сообщения "Секундочку..."
            
            if "<pre>" in response:
                bot.reply_to(message, response, parse_mode='HTML')
            else:
                bot.reply_to(message, response)

            break

        except telebot.apihelper.ApiTelegramException as e:
            # Обработка исключения, чтобы скрипт не завершался при ошибке API Telegram
            err = "ошибка API Telegram"
            print(err, e)
            continue

        except Exception as e:
            # Другие исключения
            err = str(e)
            print(err, e)
            continue 

    attempt_count = 0  # сброс счетчика попыток после успешной отправки

bot.polling()
