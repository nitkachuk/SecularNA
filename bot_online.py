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

globalMessageObject = None
sent_message = ""
response = ""

def g4f_with_timeout(txt, timeout=10):
    global response
    
    messages = [
                {"role": "system", "content": "ответь по-русски, если есть блоки кода или цитат или списков, то оберни их в pre по примеру <pre>текст</pre>. разнообразь с помощью эмодзи, но не слишком, в том числе списки"},
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

def delete_last_message():
    try:
        bot.delete_message(globalMessageObject.chat.id, sent_message.message_id)  # Удаление сообщения "Секундочку..."
    except Exception as e:
        pass

def has_glyphs(text):
    for char in text:
        if unicodedata.category(char) == 'Lo':
            return True
    return False

#@bot.message_handler(func=lambda message: True)
#@bot.message_handler(func=lambda message: message.from_user.username == 'kristina_superstar')

@bot.message_handler(func=lambda message: message.from_user.username in ['kristina_superstar', 'gothicspring', 'Kungfuoko'])

def echo_all(message):
    global globalMessageObject  
    global sent_message
    globalMessageObject = message
    
    attempt_count = 0      # счетчик попыток отправки
    err = ''    # Текст ошибок в "Секундочку..."
    global response

    # if sent_message and "секундочку" in sent_message.text.lower():
    #     delete_last_message()
    #     return

    
    while True:
        try:
            attempt_count += 1  # увеличение счетчика попыток
            if attempt_count > 1:
                sent_message = bot.reply_to(message, f'\n\n\n<i>⚙️ Секундочку... #{attempt_count} ({err})</i>', parse_mode='HTML')  # ответ 1
                err = ''
            else:
                sent_message = bot.reply_to(message, '\n\n\n<i>⏳ Секундочку...</i>', parse_mode='HTML')  # ответ 1

            if attempt_count >= 5:
                delete_last_message()
                bot.reply_to(message, "Превышено количество попыток.")  # ответ 2
                break

            txt = message.text + " по-русски"

            response = g4f_with_timeout( txt )
            if response == "":
                delete_last_message()
                err = 'таймаут g4f'
                continue
            
            response = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', response)
            response = re.sub(r'```(.*?)```', r'<pre>\1</pre>', response, flags=re.DOTALL)


            if has_glyphs( response ):
                delete_last_message()
                err = 'иероглифы'
                continue

            delete_last_message()
            
            if any(tag in response for tag in ['<pre>', '<b>']):
                bot.reply_to(message, response, parse_mode='HTML')
            else:
                bot.reply_to(message, response)

            break

        except telebot.apihelper.ApiTelegramException as e:
            # Обработка исключения, чтобы скрипт не завершался при ошибке API Telegram
            err = "ошибка API Telegram"
            print(err, e)
            delete_last_message()
            continue

        except Exception as e:
            # Другие исключения
            err = str(e)
            print(err, e)
            delete_last_message()
            continue 

    attempt_count = 0  # сброс счетчика попыток после успешной отправки

bot.polling()
