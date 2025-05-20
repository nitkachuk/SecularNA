import os, asyncio, telebot, g4f, unicodedata, re, threading, queue, time, json, atexit, sys
from datetime import datetime, timedelta
from state import has_latins, escape_system_text
from telebot.apihelper import ApiTelegramException


telegram_token = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(telegram_token)
channel_book = os.getenv('CHANNEL_BOOK')

user_contexts, user_attempts, user_psyhos, user_sent_messages, user_errors, \
user_first_message, user_busy = {}, {}, {}, {}, {}, {}, {}

maxContext = 4000
contextLimit = 1500
psyhoLimit = 500
consoleLimit = 350

globalMessageObject = None
last_message = ""
response = ""

aiAnswersCount = 0


def cleanup_clock_messages():
    for username, message in user_sent_messages.items():
        if message and message.text.strip() in [ '🕑', '🕓', '🕕', '🕗', '🕙' ]:
            try:
                bot.delete_message(message.chat.id, message.message_id)
                user_sent_messages[username] = bot.send_message(
                        message.chat.id,
                            '💥',    # после краша прошлого скрипта
                        parse_mode='HTML'
                    )
            except Exception:
                pass

# Загрузка сохранённых данных при запуске
def load_data():
    global user_contexts, user_psyhos
    try:
        if os.path.exists('data/user_contexts.txt'):
            with open('data/user_contexts.txt', 'r', encoding='utf-8') as f:
                user_contexts = json.load(f)
    except Exception as e:
        print(f"\n\n[load_data] Ошибка загрузки user_contexts: {e}\n\n")

    try:
        if os.path.exists('data/user_psyhos.txt'):
            with open('data/user_psyhos.txt', 'r', encoding='utf-8') as f:
                user_psyhos = json.load(f)
    except Exception as e:
        print(f"\n\n[load_data] Ошибка загрузки user_psyhos: {e}\n\n")

# Вызов при запуске
load_data()


def save_data():
    os.makedirs('data', exist_ok=True)
    with open('data/user_contexts.txt', 'w', encoding='utf-8') as f:
        json.dump(user_contexts, f, ensure_ascii=False, indent=2)
    with open('data/user_psyhos.txt', 'w', encoding='utf-8') as f:
        json.dump(user_psyhos, f, ensure_ascii=False, indent=2)


def g4f_with_timeout(txt, username, timeout=20):
    global globalMessageObject, user_contexts, tempContext, \
        maxContext, response

    try:
        tempContext = user_contexts.get(username, '')
    except Exception as e:
        tempContext = ''

    aiContext = (
        f'{txt}\n·\n🧠  учти скрытую информацию для тебя, информацию о пользователе (не говори что знаешь): \
            \n{user_psyhos[username][:consoleLimit] }.....'
        f'\n·\n📜  мягко учти СТАРУЮ историю перепески если РЕЛЕВАНТНА сообщению пользователя \
            (не говори что знаешь):   \n{tempContext[:consoleLimit] }.....'
    )

    if len(aiContext) > maxContext:
        aiContext = aiContext[:maxContext]
    print(f'\n\n·································································') 
    print(f'\n\n·') 
    print(f'\n\n·································································') 
    
    cleaned_aiContext = aiContext.replace(' (не говори что знаешь)', '').strip()
    print(f"💬  сообщение от [ {globalMessageObject.from_user.username} ]:  \n{cleaned_aiContext}\n\n", flush=True)

    messages = [
        {"role": "system", "content": "ты девочка-альтушка, но интеллигентная, тебя зовут Оракул. ты мой друг. ответь по-русски, "
                                      "не здоровайся каждый раз, продолжай диалог из переписки, но без фанатизма. "
                                      "если есть блоки кода или цитат или списков, то оберни их в pre по примеру <pre>текст</pre>. "
                                      "разнообразь с помощью эмодзи женского характера, но не слишком много, в том числе"
                                      "списки маркируй символом •  и немного символьными эмодзи. "
                                      "В конце каждого ответа добавляй одно ключевое предложение о пользователе, о нем в третьем лице "
                                      "ответь ПО-РУССКИ, кратко, но не слишком "
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
        print(f"[g4f too short ERROR]:  {result}")
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

def has_glyphs(text):
    for char in text:
        if unicodedata.category(char) == 'Lo':
            return True
    return False
    

@bot.message_handler(commands=['f', 'finish'])
def handle_finish(message):
    try:
        bot.delete_message(message.chat.id, "🏁")
        bot.stop_polling()
        sys.exit(0)
    except Exception:
        sys.exit(1)

@bot.message_handler(commands=['c', 'с', 'clear'])
def handle_clear(message):
    global user_busy, user_contexts, user_psyhos
    
    try:
        username = str(message.from_user.id)
        user_contexts[username] = ''
        user_psyhos[username] = ''
        save_data()
        bot.send_message(message.chat.id, "🧹")
        user_busy[username] = False
    except Exception:
        user_busy[username] = False

@bot.message_handler(commands=['psy', 'psyho'])
def handle_psy(message):
    global user_busy, user_psyhos

    try:
        username = str(message.from_user.id)
        user_context = user_contexts.get(username, '')
        user_psyho = f"<pre>{user_psyhos.get(username, '')}</pre>"

        save_data()
        bot.send_message(
            message.chat.id,
            f"<i>📜  Контекст [{len(user_context)}] \n"
            f"🧠  Психоанализ [{len(user_psyho) - 11}]:</i>\n\n{user_psyho}",    # теги
            parse_mode='HTML'
        )
        user_busy[username] = False
    except Exception:
        user_busy[username] = False

@bot.message_handler(func=lambda message: True)


def echo_all(message):
    global aiAnswersCount, user_contexts, user_attempts, \
       user_psyhos, maxContent, response, globalMessageObject, \
       use_first_message
    globalMessageObject = message

    # 🛑 Игнорируем любые сообщения от каналов
    if message.chat.type == 'channel':
        return
    if message.sender_chat is not None:
        return

    username = str(message.from_user.id)
    if username not in user_contexts:
        user_contexts[username] = ''
    aiContext = user_contexts[username]

    if user_busy.get(username, False):
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except Exception as e:
            pass
            
        return
    else:
        user_busy[username] = True

    user_attempts[username] = 0
    if username not in user_psyhos:
        user_psyhos[username] = ''
    
    user_msg = user_sent_messages.get(username)
    if user_msg:
        user_text = user_msg.text.strip()
        if '❌' in user_text or '💥' in user_text:
            delete_last_message(username)

    if username not in user_first_message:
        user_first_message[username] = True
    
        
    user_errors[username] = ''
    last_response = ''

    messageText = message.text
    if len(messageText) > maxContext:
        messageText = messageText[:maxContext]
        

    # команды
    if message.text.strip().lower() in ['пук', 'пукь']:
        try:
            bot.reply_to(message, "Я пукнула 💅🏻")
            user_busy[username] = False
            return
        except Exception as e:
            user_busy[username] = False
            return
            

    last_message = messageText
    clockEmodjis = [ '', '🕑', '🕓', '🕕', '🕗', '🕙' ]

    if user_first_message.get(username, True):
        try:
            temp_msg = bot.send_message(message.chat.id, "⬇️", parse_mode='HTML')    # 🔄
            time.sleep(2)
            bot.delete_message(message.chat.id, temp_msg.message_id)
            user_first_message[username] = False
        except Exception:
            pass
        
    
    while True:
        try:
            user_attempts[username] += 1
            
            if user_errors.get(username, '') != '':
                print( f'•   ', flush=True )
                print( f'•   {(datetime.now() + timedelta(hours=3)).strftime("[ %H:%M:%S ]")}:   {last_message}', flush=True )
                print( f'•   [ error ]:   {user_errors[username]}', flush=True )
                print( f'•   ', flush=True )


            user_sent_messages[username] = bot.send_message(
                message.chat.id,
                clockEmodjis[user_attempts[username]],
                parse_mode='HTML'
            )
            
            if user_attempts[username] > 1:
                user_errors[username] = ''
            

            if user_attempts[username] >= 5:
                time.sleep( 2 )
                delete_last_message(username)

                user_sent_messages[username] = bot.send_message(
                        message.chat.id,
                            '❌',
                        parse_mode='HTML'
                    )

                user_busy[username] = False
                break

            txt = messageText + " по-русски"
            

            response = str( g4f_with_timeout(txt, username) ).strip()

            if response == '':
                time.sleep( 2 )
                delete_last_message(username)
                user_errors[username] = f'таймаут g4f:  {response}'
                continue
                
            if len(response) < 5:
                time.sleep(2)
                delete_last_message(username)
                user_errors[username] = f'слишком короткий ответ:  {response}' 
                continue

            if has_glyphs( response ):
                time.sleep( 2 )
                delete_last_message(username)
                user_errors[username] = 'иероглифы'
                continue

            if has_latins(response) and '<pre>' not in response and '</pre>' not in response:
                time.sleep( 2 )
                delete_last_message(username)
                user_errors[username] = 'латиница'
                continue

            response = escape_system_text( response )
            response = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', response)
            response = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', response)
            response = re.sub(r'```(.*?)```', r'<pre>\1</pre>', response, flags=re.DOTALL)
            response = re.sub(r'\s*(по[\s-]?русски|на[\s-]?русском)', '', response, flags=re.IGNORECASE)
            response = re.sub(r'\s*(по[\s-]?руски|на[\s-]?руском)', '', response, flags=re.IGNORECASE)

            match = re.search(r'######(.*?)######', response)
            if match:
                new_psyho_line = match.group(1).strip()
                user_psyhos[username] = re.sub(r'скрытая информация для тебя:|информация о пользователе:', '', user_psyhos[username]).strip()
                if len(new_psyho_line) > 5 and new_psyho_line not in user_psyhos[username]:
                    user_psyhos[username] = f"{new_psyho_line}\n{user_psyhos[username].strip()}"
                    user_psyhos[username] = user_psyhos[username][:psyhoLimit]    # обрезка psyho 
                response = response.replace(match.group(0), '').strip()
    

            response = re.sub(r'#{2,}', '', response)


            delete_last_message(username)
            bot.reply_to(message, response, parse_mode='HTML')

            aiContext = user_contexts.get(username, '').strip()
            aiContext = f"Пользователь: {messageText}\nОракул: {response}\n" + aiContext
            try:
                user_contexts[username] = aiContext[-maxContext:].strip()    # обрезка контекста 
            except Exception as e:
                pass

            
            try:
                save_data()
            except Exception as e:
                print( f'\n\nошибка сохранения данных в /data/:{e}\n\n' )
                
            aiAnswersCount += 1
            user_busy[username] = False
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

    user_attempts[username] = 0      # сброс счетчика попыток после успешной отправки

atexit.register(cleanup_clock_messages)
bot.polling()
