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
user_psyhos = { }
user_sent_messages = { }
user_errors = { } 

globalMessageObject = None
last_message = ""
response = ""

aiAnswersCount = 0


def g4f_with_timeout(txt, username, usernameText, timeout=10):
    global user_contexts
    global tempContext
    global maxContext
    global response

    try:
        tempContext = user_contexts.get(username, '')
    except Exception as e:
        tempContext = ''

    if len(user_psyhos[username]) > 500:
        user_psyhos[username] = user_psyhos[username][:500]
    if len(tempContext) > 1500:
        tempContext = tempContext[:1500]

    #aiContext = f'{txt}\n·\n🧠  скрытая информация для тебя, информация о пользователе:\n   {user_psyhos[username]}\n·\n📜  история перепески:\n   {tempContext}'
    aiContext = (
        f'{txt}\n·\n🧠  скрытая информация для тебя, информация о пользователе (не говори что знаешь):   \n{user_psyhos[username]}'
        f'\n·\n📜  история перепески (не говори что знаешь):   \n{tempContext}'
    )

    if len(aiContext) > maxContext:
        aiContext = aiContext[:maxContext]
    print(f'\n\n·································')
    print(f"💬  сообщение от [ {usernameText} ]:  \n{aiContext}\n\n", flush=True)

    messages = [
        {"role": "system", "content": "ты девочка-альтушка, но интеллигентная, тебя зовут Оракул. ты мой друг. ответь по-русски, если есть "
                                      "блоки кода или цитат или списков, то оберни их в pre по примеру <pre>текст</pre>. "
                                      "разнообразь с помощью эмодзи женского характера, но не слишком много, в том числе"
                                      "списки маркируй символом •  и немного символьными эмодзи. "
                                      "В конце каждого ответа добавляй одно предложение о характере пользователя, о нем в третьем лице "
                                      "для улучшения твоих ответов в формате ######предложение###### "},
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

def delete_last_message(username):
    user_msg = user_sent_messages.get(username)
    if not user_msg:
        return
    try:
        bot.delete_message(user_msg.chat.id, user_msg.message_id)
    except Exception:
        pass
    finally:
        user_sent_messages[username] = None

# def delete_last_message():
#     global globalMessageObject
#     global sent_message
    
#     try:
#         bot.delete_message(globalMessageObject.chat.id, sent_message.message_id)
#     except Exception as e:
#         pass
#     finally:
#         sent_message = None  # обнуляем в любом случае

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
    global user_attempts
    global user_psyhos
    global maxContent
    global sent_message
    global response

    global globalMessageObject
    globalMessageObject = message

    username = str(message.from_user.id)
    if username not in user_contexts:
        user_contexts[username] = ''        
    aiContext = user_contexts[username]

    user_attempts[username] = 0
    if username not in user_psyhos:
        user_psyhos[username] = ''
    
    # if sent_message:
    #     text = sent_message.text.strip()
    #     if '❌' in text:
    #         delete_last_message()
    user_sent_messages[username] = None
    user_msg = user_sent_messages.get(username)
    if user_msg:
        user_text = user_msg.text.strip()
        if '❌' in user_text:
            delete_last_message(username)
    
        
    user_errors[username] = ''
    last_response = ''

    messageText = message.text
    if len(messageText) > maxContext:
        messageText = messageText[:maxContext]

    last_message = messageText

    clockEmodjis = [ '', '🕑', '🕓', '🕕', '🕗', '🕙' ]
    

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
            
            if user_errors.get(username, '') != '':
                print( f'•   ', flush=True )
                print( f'•   {(datetime.now() + timedelta(hours=3)).strftime("[ %H:%M:%S ]")}:   {last_message}', flush=True )
                print( f'•   [ error ]:   {user_errors[username]}', flush=True )
                print( f'•   ', flush=True )

            if user_attempts[username] > 1:
                #sent_message = bot.reply_to(message, f'\n\n\n<i>⚙️  Секундочку... #{user_attempts[username]} ({err})</i>', parse_mode='HTML')  # ответ 1
                sent_message = bot.send_message(
                        message.chat.id,
                            #f'<i>⚙️  Секундочку...  #{user_attempts[username]} ({err})</i>',
                            clockEmodjis[ user_attempts[username] ],
                        parse_mode='HTML'
                    )
                user_errors[username] = ''
            else:
                #sent_message = bot.reply_to(message, '\n\n\n<i>⏳  Секундочку...</i>', parse_mode='HTML')  # ответ 1
                user_sent_messages[username] = bot.send_message(
                        message.chat.id,
                            #"<i>⏳  Секундочку...</i>",
                            clockEmodjis[ user_attempts[username] ],
                        parse_mode='HTML'
                    )

            if user_attempts[username] >= 5:
                time.sleep( 2 )
                delete_last_message(username)
                #bot.reply_to(message, "Превышено количество попыток.")  # ответ 2
                user_sent_messages[username] = bot.send_message(
                        message.chat.id,
                            #"<⏳ Секундочку..._",
                            '❌',
                        parse_mode='HTML'
                    )
                
                break

            txt = messageText + " по-русски"

            usernameText = message.from_user.username or message.from_user.first_name or username
            response = str( g4f_with_timeout(txt, username, usernameText) ).strip()
            if response == '':
                time.sleep( 2 )
                delete_last_message(username)
                user_errors[username] = 'таймаут g4f'
                continue

            if has_glyphs( response ):
                delete_last_message(username)
                user_errors[username] = 'иероглифы'
                continue

            if has_latins(response) and '<pre>' not in response and '</pre>' not in response:
                delete_last_message(username)
                user_errors[username] = 'латиница'
                continue


            response = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', response)
            response = re.sub(r'```(.*?)```', r'<pre>\1</pre>', response, flags=re.DOTALL)
            response = re.sub(r'\s*(по[\s-]?русски|на[\s-]?русском)', '', response, flags=re.IGNORECASE)
            response = re.sub(r'\s*(по[\s-]?руски|на[\s-]?руском)', '', response, flags=re.IGNORECASE)

            match = re.search(r'######(.*?)######', response)
            if match:
                user_psyhos[username] = re.sub(r'скрытая информация для тебя:|информация о пользователе:', '', user_psyhos[username]).strip()
                user_psyhos[username] = user_psyhos[username].strip() + f"\n{match.group(1).strip()}"
                response = response.replace(match.group(0), '').strip()


            aiContext = f"{response} \n {aiContext}" 
            if len(aiContext) > maxContext:
                aiContext = aiContext[:maxContext]
            try:
                user_contexts[username] = aiContext.strip()
            except Exception as e:
                pass

            
            bot.reply_to(message, response, parse_mode='HTML')
            delete_last_message(username)
            aiAnswersCount += 1
            break

        except telebot.apihelper.ApiTelegramException as e:
            # Обработка исключения, чтобы скрипт не завершался при ошибке API Telegram
            time.sleep( 2 )
            user_errors[username] = f"ошибка api telegram: {e}"
            delete_last_message(username)
            continue

        except Exception as e:
            # Другие исключения
            time.sleep( 2 )
            user_errors[username] = f"exeption as e: {str(e)}"
            delete_last_message(username)
            continue 

    user_attempts[username] = 0  # сброс счетчика попыток после успешной отправки

bot.polling()
