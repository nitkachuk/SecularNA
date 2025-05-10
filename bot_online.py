import os
import asyncio
import telebot
import g4f
import unicodedata
import re
import threading
import queue
import time
from state import escape_markdown_v2

telegram_token = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(telegram_token)

user_contexts = { }
maxContext = 4000

globalMessageObject = None
sent_message = ""
response = ""

def g4f_with_timeout(txt, username, timeout=10):
    global user_contexts
    global maxContext
    global response

    messages = [
        {"role": "system", "content": f"контекст: '' {user_contexts.get(username, '')}"},
        {"role": "system", "content": "ты девочка-альтушка, тебя зовут Оракул. ответь по-русски, если есть блоки кода или цитат или "
                                     "списков, то оберни их в pre по примеру <pre>текст</pre>. разнообразь с помощью эмодзи "
                                     "женского характера, но не слишком много, в том числе списки некрупными символьными эмодзи"},
        {"role": "user", "content": txt}
    ]

    #messages.insert(0, {"role": "system", "content": history})
    
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
    global globalMessageObject
    global sent_message
    
    try:
        bot.delete_message(globalMessageObject.chat.id, sent_message.message_id)  # Удаление сообщения "Секундочку..."
    except Exception as e:
        pass

# def delete_last_message():
#     global sent_message
#     try:
#         bot.delete_message(globalMessageObject.chat.id, sent_message.message_id)
#     except Exception as e:
#         pass
#     finally:
#         sent_message = None  # обнуляем в любом случае

def has_glyphs(text):
    for char in text:
        if unicodedata.category(char) == 'Lo':
            return True
    return False

#@bot.message_handler(func=lambda message: True)
#@bot.message_handler(func=lambda message: message.from_user.username == 'kristina_superstar')

@bot.message_handler(func=lambda message: message.from_user.username in ['kristina_superstar', 'gothicspring', 'Kungfuoko'])

def echo_all(message):
    global user_contexts
    global maxContent
    global sent_message
    global response

    global globalMessageObject
    globalMessageObject = message

    attempt_count = 0    
    err = ''    

    clockEmodjis = [ '', '🕑', '🕓', '🕕', '🕗', '🕙' ]

    username = message.from_user.username
    if username not in user_contexts or not user_contexts[username]:
        user_contexts[username] = ''  # Пустой контекст, если его нет

    aiContext = user_contexts[username]
        
    
    while True:
        try:
            if sent_message:
                text = sent_message.text.strip()
                if '❌' in text:
                    delete_last_message()

            attempt_count += 1  # увеличение счетчика попыток
            
            if attempt_count > 1:
                #sent_message = bot.reply_to(message, f'\n\n\n<i>⚙️  Секундочку... #{attempt_count} ({err})</i>', parse_mode='HTML')  # ответ 1
                sent_message = bot.send_message(
                        message.chat.id,
                            f'<i>⚙️  Секундочку...  #{attempt_count} ({err})</i>',
                            #clockEmodjis[ attempt_count ],
                        parse_mode='HTML'
                    )
                err = ''
            else:
                #sent_message = bot.reply_to(message, '\n\n\n<i>⏳  Секундочку...</i>', parse_mode='HTML')  # ответ 1
                sent_message = bot.send_message(
                        message.chat.id,
                            "<i>⏳  Секундочку...</i>",
                            #clockEmodjis[ attempt_count ],
                        parse_mode='HTML'
                    )

            if attempt_count >= 5:
                time.sleep( 2 )
                delete_last_message()
                #bot.reply_to(message, "Превышено количество попыток.")  # ответ 2
                sent_message = bot.send_message(
                        message.chat.id,
                            #"<⏳ Секундочку..._",
                            '❌',
                        parse_mode='HTML'
                    )
                
                break

            txt = message.text + " по-русски"

            response = g4f_with_timeout(txt, username)
            if response == "":
                time.sleep( 2 )
                delete_last_message()
                err = 'таймаут g4f'
                continue

            if has_glyphs( response ):
                delete_last_message()
                err = 'иероглифы'
                continue

            response = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', response)
            response = re.sub(r'```(.*?)```', r'<pre>\1</pre>', response, flags=re.DOTALL)

            aiContext = f"{response} \n {aiContext}" 
            if len(aiContext) > maxContext:
                aiContext = aiContext[:maxContext]
            try:
                user_contexts[username] = aiContext
            except Exception as e:
                pass

            bot.reply_to(message, response, parse_mode='HTML')

            delete_last_message()

            
            # if any(tag in response for tag in ['<pre>', '<b>']):
            #     bot.reply_to(message, response)    # , parse_mode='HTML'
            # else:
            #     bot.reply_to(message, response)

            break

        except telebot.apihelper.ApiTelegramException as e:
            # Обработка исключения, чтобы скрипт не завершался при ошибке API Telegram
            time.sleep( 2 )
            err = f"ошибка api telegram: {e}"
            delete_last_message()
            continue

        except Exception as e:
            # Другие исключения
            time.sleep( 2 )
            err = f"exeption as e: {str(e)}"
            delete_last_message()
            continue 

    attempt_count = 0  # сброс счетчика попыток после успешной отправки

bot.polling()
