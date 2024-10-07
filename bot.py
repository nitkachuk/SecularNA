import asyncio
from telegram import Bot
from g4f.client import Client
import unicodedata
import re

import os
import datetime

import sys
from replacements import replacements, doReplacements # type: ignore

def has_glyphs(text):
    for char in text:
        if unicodedata.category(char) == 'Lo':
            return True
    return False

def escape_markdown_v2(text):
    escape_chars = [  '[', ']', '(', ')', '~', 'Ⓝ', '>', '#', '+',
                      '-', '=', '|', '{', '}', '.', ',', '!', '\\'  ]
    
    for char in escape_chars:
        pattern = re.escape(char)
        
        if char == '\\':
            replacement = '\\\\'
        else:
            replacement = '\\' + char
        text = re.sub(pattern, replacement, text)

    text = text.replace('\\\\', '\\')
    return text

def escape_system_text(text):
    text = text.replace( '_{"code":200,"status":true,"model":"gpt-3.5-turbo","gpt":"', '')
    text = text.replace( '","original":null}', '')
    return text
    

def get_text():
    # часы запуска скрипта на гитхабе
    send_hour = 17
    send_minute = 0
    
    current_hour = datetime.datetime.now().hour
    current_minute = datetime.datetime.now().minute

    if current_hour > send_hour or (current_hour == send_hour and current_minute >= send_minute):
        today = datetime.date.today() + datetime.timedelta(days=1)
    else:
        today = datetime.date.today()

    current_day = today.day
    current_month = today.month

    folder_path = 'book'

    month_folder_path = os.path.join(folder_path, str(current_month))

    today_file = f"{current_day}.txt"

    if os.path.exists(month_folder_path):
        file_path = os.path.join(month_folder_path, today_file)

        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                paragraphs = content.split('\n\n')

                p_lines = paragraphs[0].split('\n')
                p_lines[0] = f"{p_lines[0]}"        # дата
                p_lines[1] = f"__{p_lines[1]}__"        # заголовок
                p_lines[3] = f"_{p_lines[3]}_"    # цитата
                p_lines[4] = f"*{p_lines[4]}*"      # источник

                paragraphs[0] = '\n'.join(p_lines)
                paragraphs[2] = paragraphs[2].replace("ТОЛЬКО СЕГОДНЯ:", "*ТОЛЬКО СЕГОДНЯ:*")

                largest_paragraph = max(paragraphs, key=len)
                lines = largest_paragraph.splitlines()
                formatted_paragraph = '\n' + '\n\n'.join(lines) + '\n'
                paragraphs[paragraphs.index(largest_paragraph)] = formatted_paragraph

                final_content = '\n\n'.join(paragraphs)

                return escape_markdown_v2( final_content )
        else:
            return f"Файл для {current_day} числа не найден в папке месяца {current_month}."
    else:
        return f"Папка для месяца {current_month} не найдена в папке 'book'."
    

async def main():
    bot_token = os.getenv('TELEGRAM_TOKEN')
    bot = Bot(token=bot_token)


    # уникализация ежедневника (для всех сообществ)
    message_to_send = doReplacements( get_text() )

    # постинг в канал "Светский ежедневник"
    chat_id = '@SecularNA'
    message_to_send = escape_system_text( escape_markdown_v2( message_to_send ) )
    #print( message_to_send )
    #return
    try:
        await bot.send_message(chat_id=chat_id, text=message_to_send, parse_mode='MarkdownV2')
        print( "Отправил пост в канал ежедневника 📘 ✅" )
    except Exception as e:
        print( "Не удалось отправить пост в канал ежедневника 📘 ❌" )
        print( "Ошибка:", e, " ⚙️ \n" )

    #return
    # постинг в канал "Так говорил Билл"
    chat_id_3 = '@BillSpeaks'
    client = Client()

    attempts = 0
    while True:
        if attempts >= 20:
            print("Превышено количество попыток отправки сообщения. Цикл завершен.")
            break
        
        role_system = """ Выскажись по-русски, по тексту, в духе психологии. 
                          1-2 небольших абзаца. Добавь 3-5 эмодзи в текст. """
        role_user = message_to_send

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ 
                {"role": "system", "content": role_system},
                {"role": "user", "content": role_user}
            ],
        )

        ai_response = escape_system_text( escape_markdown_v2( completion.choices[0].message.content ) )
        ai_response = "*__Высказывание по книге__* 🗣️ \n\n" +ai_response

        # удаляем возможное присутствие системных настроек в выводе результата
        ai_response = ai_response.replace(role_system, '')    
        ai_response = ai_response.replace('Assistant:', '')
        ai_response = ai_response.replace('assistant:', '')
        ai_response = ai_response.replace('Конец', '')
        ai_response = ai_response.replace('конец', '')

        if has_glyphs(ai_response):
            print("has glyphs. try again... ⚙️")
            attempts += 1
            continue

        if role_user in ai_response:
            print("role_user in message. try again... ⚙️")
            attempts += 1
            continue

        if len( str(ai_response) ) < 250:
            print("too short response. try again... ⚙️")
            attempts += 1
            continue

        try:
            await bot.send_message( chat_id=chat_id_3, text=ai_response, parse_mode='MarkdownV2' )
            print( "Отправил пост в канал Билла Уилсона 🗣️ ✅" )
        except Exception as e:
            print( "Не удалось отправить пост в канал Билла Уилсона 🗣️ ❌" )
            print( "Ошибка:", e, " ⚙️ \n" )
            #print( "Ответ от ИИ:", ai_response, " ⚙️ \n" )
            attempts += 1
            continue
            
        break


    # принципы программы на сегодня
    while True:
        if attempts >= 20:
            print("Превышено количество попыток отправки сообщения. Цикл завершен.")
            break
        
        role_system = """ принципы программы: честность, непредубежденность, готовность, спокойствие, 
                          принятие, уверенность, доверие, капитуляция, надежда, верность принятому решению, 
                          мужество, обязательность, упорство, принятие себя, признание, терпение, сострадание, 
                          любовь, прощение, самодисциплина, чистосердечие, бескорыстие, непоколебимость. 
                          Приведи 3 принципа по тексту, над которыми сегодня надо работать, и напиши по 
                          1 предложению описания на каждый. Раздели эти принципы межстрочными отступами и 
                          обозначь каждый одним эмодзи. по-русски. """
        role_user = message_to_send

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ 
                {"role": "system", "content": role_system},
                {"role": "user", "content": role_user}
            ],
        )

        ai_response = escape_system_text( escape_markdown_v2( completion.choices[0].message.content ) )
        ai_response = "*__Принципы программы__* 🌱 \n\n" +ai_response

        if has_glyphs(ai_response):
            print("has glyphs. try again... ⚙️")
            attempts += 1
            continue

        if len( str(ai_response) ) < 250:
            print("too short response. try again... ⚙️")
            attempts += 1
            continue

        try:
            await bot.send_message( chat_id=chat_id_3, text=ai_response, parse_mode='MarkdownV2' )
            print( "Отправил принципы на сегодня 🌱 ✅" )
        except Exception as e:
            print( "Не удалось отправить принципы на сегодня 🌱 ❌" )
            print( "Ошибка:", e, " ⚙️ \n" )
            #print( "Ответ от ИИ:", ai_response, " ⚙️ \n" )
            attempts += 1
            continue
            
        break


    # темы для собрания
    while True:
        if attempts >= 20:
            print("Превышено количество попыток отправки сообщения. Цикл завершен.")
            break
        
        role_system = """ Придумай 2 темы для обсуждения, которые косвенно перекликаются с текстом, 
                          но не повторяют его. Раздели эти принципы межстрочными отступами и 
                          обозначь каждый одним эмодзи. по-русски. """
        role_user = message_to_send

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ 
                {"role": "system", "content": role_system},
                {"role": "user", "content": role_user}
            ],
        )

        ai_response = escape_system_text( escape_markdown_v2( completion.choices[0].message.content ) )
        ai_response = "*__Темы для собраний__* 📌 \n\n" +ai_response

        if has_glyphs(ai_response):
            print("has glyphs. try again... ⚙️")
            attempts += 1
            continue

        if len( str(ai_response) ) < 250:
            print("too short response. try again... ⚙️")
            attempts += 1
            continue

        try:
            await bot.send_message( chat_id=chat_id_3, text=ai_response, parse_mode='MarkdownV2' )
            print( "Отправил темы для собраний 📌 ✅" )
        except Exception as e:
            print( "Не удалось отправить темы для собраний 📌 ❌" )
            print( "Ошибка:", e, " ⚙️ \n" )
            #print( "Ответ от ИИ:", ai_response, " ⚙️ \n" )
            attempts += 1
            continue
            
        break
    

    # задание на день
    while True:
        if attempts >= 20:
            print("Превышено количество попыток отправки сообщения. Цикл завершен.")
            break
        
        role_system = """ Придумай 3 действия на сегодняшний день, которые я могу сделать, 
                          чтобы следовать тексту. Раздели эти принципы межстрочными отступами и 
                          обозначь каждый одним эмодзи. по-русски. """
        role_user = message_to_send

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ 
                {"role": "system", "content": role_system},
                {"role": "user", "content": role_user}
            ],
        )

        ai_response = escape_system_text( escape_markdown_v2( completion.choices[0].message.content ) )
        ai_response = "*__Задание на день__* 📝 \n\n" +ai_response

        if has_glyphs(ai_response):
            print("has glyphs. try again... ⚙️")
            attempts += 1
            continue

        if len( str(ai_response) ) < 250:
            print("too short response. try again... ⚙️")
            attempts += 1
            continue

        try:
            await bot.send_message( chat_id=chat_id_3, text=ai_response, parse_mode='MarkdownV2' )
            print( "Отправил задание на день 📝 ✅" )
        except Exception as e:
            print( "Не удалось отправить задание на день 📝 ❌" )
            print( "Ошибка:", e, " ⚙️ \n" )
            #print( "Ответ от ИИ:", ai_response, " ⚙️ \n" )
            attempts += 1
            continue
            
        break

    
    print( "Количество попыток:", (attempts + 1) )
    print( "success!" )

asyncio.run(main())
