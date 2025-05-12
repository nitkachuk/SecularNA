import os
import asyncio
import telebot
import g4f
import unicodedata
import re
import threading
import queue
import time
from datetime import datetime, timedelta
from state import has_latins
#from state import escape_markdown_v2

telegram_token = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(telegram_token)

user_contexts = { }
maxContext = 4000
user_attempts = { }

globalMessageObject = None
last_message = ""
response = ""
sent_message = None 

aiAnswersCount = 0


def g4f_with_timeout(txt, username, timeout=10):
    global user_contexts
    global maxContext
    global response

    try:
        tempContext = user_contexts.get(username, '')
    except Exception as e:
        tempContext = ''

    aiContext = f'{txt}\n\n{tempContext}'
    if len(aiContext) > maxContext:
        aiContext = aiContext[:maxContext]

    messages = [
        {"role": "system", "content": "ты девочка-альтушка, но интеллигентная, тебя зовут Оракул. ответь по-русски, если есть "
                                     "блоки кода или цитат или списков, то оберни их в pre по примеру <pre>текст</pre>. "
                                     "разнообразь с помощью эмодзи женского характера, но не слишком много, в том числе"
                                     " списки маркируй символом •  и немного символьными эмодзи"},
        {"role": "user", "content": aiContext}
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
    global globalMessageObject
    global sent_message
    
    try:
        bot.delete_message(globalMessageObject.chat.id, sent_message.message_id)
    except Exception as e:
        pass
    finally:
        sent_message = None  # обнуляем в любом случае

# def delete_last_message():
#     global globalMessageObject
#     global sent_message
    
#     try:
#         bot.delete_message(globalMessageObject.chat.id, sent_message.message_id)  # Удаление сообщения "Секундочку..."
#     except Exception as e:
#         pass

def has_glyphs(text):
    for char in text:
        if unicodedata.category(char) == 'Lo':
            return True
    return False

#@bot.message_handler(func=lambda message: True)
#@bot.message_handler(func=lambda message: message.from_user.username == 'kristina_superstar')

@bot.message_handler(func=lambda message: message.from_user.username in ['kristina_superstar', 'gothicspring', 'Kungfuoko'])

def echo_all(message):
    global aiAnswersCount
    global user_contexts
    global maxContent
    global sent_message
    global response

    global globalMessageObject
    globalMessageObject = message
    
    if sent_message:
        text = sent_message.text.strip()
        if '❌' in text:
            delete_last_message()

    #attempt_count = 0  
    if username not in user_attempts:
        user_attempts[username] = 0
    err = ''    
    last_response = ''

    messageText = message.text
    if len(messageText) > maxContext:
        messageText = messageText[:maxContext]

    last_message = messageText

    clockEmodjis = [ '', '🕑', '🕓', '🕕', '🕗', '🕙' ]

    username = str(message.from_user.id)
    if username not in user_contexts:
        user_contexts[username] = ''        
    aiContext = user_contexts[username]

    if aiContext.strip() == '':
        try:
            #temp_msg = bot.send_message(message.chat.id, "🧹  <i>История очищена</i>", parse_mode='HTML')
            temp_msg = bot.send_message(message.chat.id, "🧹", parse_mode='HTML')
            time.sleep(2)
            bot.delete_message(message.chat.id, temp_msg.message_id)
        except Exception:
            pass
        
    
    while True:
        try:
            #attempt_count += 1
            user_attempts[username] += 1
            
            if err != '':
                print( f'•   {(datetime.now() + timedelta(hours=3)).strftime("[ %H:%M:%S ]")}:   {last_message}', flush=True )
                print( f'•   [ error ]:   {err}', flush=True )
                print( f'•   ', flush=True )

            if user_attempts[username] > 1:
                #sent_message = bot.reply_to(message, f'\n\n\n<i>⚙️  Секундочку... #{user_attempts[username]} ({err})</i>', parse_mode='HTML')  # ответ 1
                sent_message = bot.send_message(
                        message.chat.id,
                            #f'<i>⚙️  Секундочку...  #{user_attempts[username]} ({err})</i>',
                            clockEmodjis[ user_attempts[username] ],
                        parse_mode='HTML'
                    )
                err = ''
            else:
                #sent_message = bot.reply_to(message, '\n\n\n<i>⏳  Секундочку...</i>', parse_mode='HTML')  # ответ 1
                sent_message = bot.send_message(
                        message.chat.id,
                            #"<i>⏳  Секундочку...</i>",
                            clockEmodjis[ user_attempts[username] ],
                        parse_mode='HTML'
                    )

            if user_attempts[username] >= 5:
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

            txt = messageText + " по-русски"
            

            response = g4f_with_timeout(txt, username)
            if response.strip() == '':
                time.sleep( 2 )
                delete_last_message()
                err = 'таймаут g4f'
                continue

            if has_glyphs( response ):
                delete_last_message()
                err = 'иероглифы'
                continue

            if has_latins(response) and '<pre>' not in response and '</pre>' not in response:
                delete_last_message()
                err = 'латиница'
                continue


            response = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', response)
            response = re.sub(r'```(.*?)```', r'<pre>\1</pre>', response, flags=re.DOTALL)
            #response = re.sub(r'\bпо-?русски\b', '', response)
            # response = re.sub(r'\s*по-?русски', '', response)
            # response = re.sub(r'\s*по ?русски', '', response)
            # response = re.sub(r'\s*на-?русском', '', response)
            # response = re.sub(r'\s*на ?русском', '', response)
            response = re.sub(r'\s*(по[\s-]?русски|на[\s-]?русском)', '', response, flags=re.IGNORECASE)
            response = re.sub(r'\s*(по[\s-]?руски|на[\s-]?руском)', '', response, flags=re.IGNORECASE)


            aiContext = f"{response} \n {aiContext}" 
            if len(aiContext) > maxContext:
                aiContext = aiContext[:maxContext]
            try:
                user_contexts[username] = aiContext
            except Exception as e:
                pass

            
            bot.reply_to(message, response, parse_mode='HTML')
            delete_last_message()
            aiAnswersCount += 1
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

    user_attempts[username] = 0  # сброс счетчика попыток после успешной отправки

bot.polling()
