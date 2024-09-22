import asyncio
from telegram import Bot
from g4f.client import Client
import unicodedata
import re

import os
import datetime

def has_glyphs(text):
    for char in text:
        if unicodedata.category(char) == 'Lo':
            return True
    return False

def escape_markdown_v2(text):
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

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
                content = escape_markdown_v2( file.read() )
                
                paragraphs = content.split('\n\n')

                p_lines = paragraphs[0].split('\n')
                p_lines[0] = f"**{p_lines[0]}**"
                p_lines[1] = f"**{p_lines[1]}**"
                p_lines[3] = f"**{p_lines[3]}**"
                p_lines[4] = f"**{p_lines[4]}**"

                paragraphs[0] = '\n'.join(p_lines)
                paragraphs[2] = paragraphs[2].replace("ТОЛЬКО СЕГОДНЯ:", "**ТОЛЬКО СЕГОДНЯ:**")

                largest_paragraph = max(paragraphs, key=len)
                lines = largest_paragraph.splitlines()
                formatted_paragraph = '\n' + '\n\n'.join(lines) + '\n'
                #formatted_content = content.replace(largest_paragraph, formatted_paragraph)
                paragraphs[paragraphs.index(largest_paragraph)] = formatted_paragraph

                final_content = '\n\n'.join(paragraphs)

                return final_content
        else:
            return f"Файл для {current_day} числа не найден в папке месяца {current_month}."
    else:
        return f"Папка для месяца {current_month} не найдена в папке 'book'."
    

async def main():
    bot_token = os.getenv('TELEGRAM_TOKEN')
    bot = Bot(token=bot_token)


    # уникализация ежедневника (для всех сообществ)
    replacements = [

        {'keyword': 'Сообщество АН',  'replaceword': 'Сообщество'},
        {'keyword': 'Сообщества АН',  'replaceword': 'Сообщества'},
        {'keyword': 'Сообществу АН',  'replaceword': 'Сообществу'},
        {'keyword': 'Сообществом АН', 'replaceword': 'Сообществом'},
        {'keyword': 'Сообществе АН',  'replaceword': 'Сообществе'},

        {'keyword': 'сообщество АН',  'replaceword': 'сообщество'},
        {'keyword': 'сообщества АН',  'replaceword': 'сообщества'},
        {'keyword': 'сообществу АН',  'replaceword': 'сообществу'},
        {'keyword': 'сообществом АН', 'replaceword': 'сообществом'},
        {'keyword': 'сообществе АН',  'replaceword': 'сообществе'},

        {'keyword': 'АН', 'replaceword': 'сообщ.'},

        {'keyword': 'Анонимные Наркоманы', 'replaceword': 'Анонимные'},
        {'keyword': 'Анонимные наркоманы', 'replaceword': 'Анонимные'},
        {'keyword': 'анонимные наркоманы', 'replaceword': 'анонимные'},
        {'keyword': 'анонимные Наркоманы', 'replaceword': 'анонимные'},

        {'keyword': 'Анонимных Наркоманов', 'replaceword': 'Анонимных'},
        {'keyword': 'Анонимных наркоманов', 'replaceword': 'Анонимных'},
        {'keyword': 'анонимных наркоманов', 'replaceword': 'анонимных'},
        {'keyword': 'анонимных Наркоманов', 'replaceword': 'анонимных'},

        {'keyword': 'Анонимным Наркоманам', 'replaceword': 'Анонимным'},
        {'keyword': 'Анонимным наркоманам', 'replaceword': 'Анонимным'},
        {'keyword': 'анонимным наркоманам', 'replaceword': 'анонимным'},
        {'keyword': 'анонимным Наркоманам', 'replaceword': 'анонимным'},

        {'keyword': 'Анонимными Наркоманами', 'replaceword': 'Анонимными'},
        {'keyword': 'Анонимными наркоманами', 'replaceword': 'Анонимными'},
        {'keyword': 'анонимными наркоманами', 'replaceword': 'анонимными'},
        {'keyword': 'анонимными Наркоманами', 'replaceword': 'анонимными'},

        {'keyword': 'Анонимных Наркоманах', 'replaceword': 'Анонимных'},
        {'keyword': 'Анонимных наркоманах', 'replaceword': 'Анонимных'},
        {'keyword': 'анонимных наркоманах', 'replaceword': 'анонимных'},
        {'keyword': 'анонимных Наркоманах', 'replaceword': 'анонимных'},

        {'keyword': 'наша наркомания',     'replaceword': 'наша зависимость'},
        {'keyword': 'нашей наркомании',     'replaceword': 'нашей зависимости'},
        {'keyword': 'нашей наркоманию',     'replaceword': 'нашей зависимостью'},
        {'keyword': 'наркомания',     'replaceword': 'зависимость'},
        {'keyword': 'наркомании',     'replaceword': 'зависимости'},
        {'keyword': 'наркоманией',     'replaceword': 'зависимостью'},

        {'keyword': 'Наркоманов',   'replaceword': 'Зависимых'},
        {'keyword': 'Наркоманы',    'replaceword': 'Зависимые'},
        {'keyword': 'Наркоманам',   'replaceword': 'Зависимым'},
        {'keyword': 'Наркоман',     'replaceword': 'Зависимый'},

        {'keyword': 'наркоманов',   'replaceword': 'зависимых'},
        {'keyword': 'наркоманы',    'replaceword': 'зависимые'},
        {'keyword': 'наркоманам',   'replaceword': 'зависимым'},
        {'keyword': 'наркоман',     'replaceword': 'зависимый'},

        {'keyword': 'Наркотиков',       'replaceword': 'Веществ'},
        {'keyword': 'Наркотики',        'replaceword': 'Вещества'},
        {'keyword': 'Наркотиками',      'replaceword': 'Веществами'},
        {'keyword': 'Наркотикам',       'replaceword': 'Веществам'},
        {'keyword': 'Наркотиках',       'replaceword': 'Веществах'},
        {'keyword': 'Наркотика',        'replaceword': 'Вещества'},
        {'keyword': 'Наркотик',         'replaceword': 'Вещество'},

        {'keyword': 'наркотиков',       'replaceword': 'веществ'},
        {'keyword': 'наркотики',        'replaceword': 'вещества'},
        {'keyword': 'наркотиками',      'replaceword': 'веществами'},
        {'keyword': 'наркотикам',       'replaceword': 'веществам'},
        {'keyword': 'наркотиках',       'replaceword': 'веществах'},
        {'keyword': 'наркотика',       'replaceword': 'вещества'},
        {'keyword': 'наркотик',         'replaceword': 'вещество'},

        {'keyword': 'Наркозависимость',     'replaceword': 'Зависимость'},
        {'keyword': 'Наркозависимости',     'replaceword': 'Зависимости'},
        {'keyword': 'Наркозависимый',       'replaceword': 'Зависимый'},
        {'keyword': 'Наркозависимых',       'replaceword': 'Зависимых'},
        {'keyword': 'Наркозависимому',      'replaceword': 'Зависимому'},
        {'keyword': 'Наркозависимыми',      'replaceword': 'Зависимыми'},
        {'keyword': 'Наркозависимым',       'replaceword': 'Зависимым'},
        {'keyword': 'Наркозависим',         'replaceword': 'Зависим'},

        {'keyword': 'наркозависимость',     'replaceword': 'зависимость'},
        {'keyword': 'наркозависимости',     'replaceword': 'зависимости'},
        {'keyword': 'наркозависимый',       'replaceword': 'зависимый'},
        {'keyword': 'наркозависимых',       'replaceword': 'зависимых'},
        {'keyword': 'наркозависимому',      'replaceword': 'зависимому'},
        {'keyword': 'наркозависимыми',      'replaceword': 'зависимыми'},
        {'keyword': 'наркозависимым',       'replaceword': 'зависимым'},
        {'keyword': 'наркозависим',         'replaceword': 'зависим'},


        {'keyword': 'Сообщество АА', 'replaceword':     'Сообщество'},
        {'keyword': 'Сообщества АА', 'replaceword':     'Сообщества'},
        {'keyword': 'Сообществу АА', 'replaceword':     'Сообществу'},
        {'keyword': 'Сообществом АА', 'replaceword':    'Сообществом'},
        {'keyword': 'Сообществе АА', 'replaceword':     'Сообществе'},

        {'keyword': 'сообщество АА', 'replaceword':     'сообщество'},
        {'keyword': 'сообщества АА', 'replaceword':     'сообщества'},
        {'keyword': 'сообществу АА', 'replaceword':     'сообществу'},
        {'keyword': 'сообществом АА', 'replaceword':    'сообществом'},
        {'keyword': 'сообществе АА', 'replaceword':     'сообществе'},

        {'keyword': 'АА', 'replaceword': 'сообщ.'},

        {'keyword': 'Анонимные Алкоголики', 'replaceword': 'Анонимные'},
        {'keyword': 'Анонимные алкоголики', 'replaceword': 'Анонимные'},
        {'keyword': 'анонимные алкоголики', 'replaceword': 'анонимные'},
        {'keyword': 'анонимные Алкоголики', 'replaceword': 'анонимные'},

        {'keyword': 'Анонимных Алкоголиков', 'replaceword': 'Анонимных'},
        {'keyword': 'Анонимных алкоголиков', 'replaceword': 'Анонимных'},
        {'keyword': 'анонимных алкоголиков', 'replaceword': 'анонимных'},
        {'keyword': 'анонимных Алкоголиков', 'replaceword': 'анонимных'},

        {'keyword': 'Анонимным Алкоголикам', 'replaceword': 'Анонимным'},
        {'keyword': 'Анонимным алкоголикам', 'replaceword': 'Анонимным'},
        {'keyword': 'анонимным алкоголикам', 'replaceword': 'анонимным'},
        {'keyword': 'анонимным Алкоголикам', 'replaceword': 'анонимным'},

        {'keyword': 'Анонимными Алкоголиками', 'replaceword': 'Анонимными'},
        {'keyword': 'Анонимными алкоголиками', 'replaceword': 'Анонимными'},
        {'keyword': 'анонимными алкоголиками', 'replaceword': 'анонимными'},
        {'keyword': 'анонимными Алкоголиками', 'replaceword': 'анонимными'},

        {'keyword': 'Анонимных Алкоголиках', 'replaceword': 'Анонимных'},
        {'keyword': 'Анонимных алкоголиках', 'replaceword': 'Анонимных'},
        {'keyword': 'анонимных алкоголиках', 'replaceword': 'анонимных'},
        {'keyword': 'анонимных Алкоголиках', 'replaceword': 'анонимных'},

        {'keyword': 'наш алкоголизм',     'replaceword': 'наша зависимость'},
        {'keyword': 'нашего алкоголизма',     'replaceword': 'нашей зависимости'},
        {'keyword': 'нашему алкоголизму',     'replaceword': 'нашей зависимости'},
        {'keyword': 'алкоголизм',     'replaceword': 'зависимость'},
        {'keyword': 'алкоголизма',     'replaceword': 'зависимости'},
        {'keyword': 'алкоголизму',     'replaceword': 'зависимости'},

        {'keyword': 'Алкоголиков',   'replaceword': 'Зависимых'},
        {'keyword': 'Алкоголики',    'replaceword': 'Зависимые'},
        {'keyword': 'Алкоголикам',   'replaceword': 'Зависимым'},
        {'keyword': 'Алкоголик',     'replaceword': 'Зависимый'},

        {'keyword': 'алкоголиков',   'replaceword': 'зависимых'},
        {'keyword': 'алкоголики',    'replaceword': 'зависимые'},
        {'keyword': 'алкоголикам',   'replaceword': 'зависимым'},
        {'keyword': 'алкоголик',     'replaceword': 'зависимый'},

        {'keyword': 'Алкоголя',       'replaceword': 'Веществ'},
        {'keyword': 'Алкоголь',       'replaceword': 'Вещество'},
        {'keyword': 'Алкоголем',      'replaceword': 'Веществами'},
        {'keyword': 'Алкоголю',       'replaceword': 'Веществам'},
        {'keyword': 'Алкоголя',        'replaceword': 'Вещества'},
        {'keyword': 'Алкоголь',       'replaceword': 'Вещество'},

        {'keyword': 'алкоголя',       'replaceword': 'веществ'},
        {'keyword': 'алкоголь',       'replaceword': 'вещества'},
        {'keyword': 'алкоголем',      'replaceword': 'веществами'},
        {'keyword': 'алкоголю',       'replaceword': 'веществам'},
        {'keyword': 'алкоголя',        'replaceword': 'вещества'},
        {'keyword': 'алкоголь',       'replaceword': 'вещество'},

        {'keyword': 'Алкозависимость',     'replaceword': 'Зависимость'},
        {'keyword': 'Алкозависимости',     'replaceword': 'Зависимости'},
        {'keyword': 'Алкозависимый',       'replaceword': 'Зависимый'},
        {'keyword': 'Алкозависимых',       'replaceword': 'Зависимых'},
        {'keyword': 'Алкозависимому',      'replaceword': 'Зависимому'},
        {'keyword': 'Алкозависимыми',      'replaceword': 'Зависимыми'},
        {'keyword': 'Алкозависимым',       'replaceword': 'Зависимым'},
        {'keyword': 'Алкозависим',         'replaceword': 'Зависим'},

        {'keyword': 'алкозависимость',     'replaceword': 'зависимость'},
        {'keyword': 'алкозависимости',     'replaceword': 'зависимости'},
        {'keyword': 'алкозависимый',       'replaceword': 'зависимый'},
        {'keyword': 'алкозависимых',       'replaceword': 'зависимых'},
        {'keyword': 'алкозависимому',      'replaceword': 'зависимому'},
        {'keyword': 'алкозависимыми',      'replaceword': 'зависимыми'},
        {'keyword': 'алкозависимым',       'replaceword': 'зависимым'},
        {'keyword': 'алкозависим',         'replaceword': 'зависим'},


        {'keyword': '', 'replaceword': ''}
    ]

    message_to_send = get_text()

    for replacement in replacements:
        keyword = replacement['keyword']
        replaceword = replacement['replaceword']
        message_to_send = message_to_send.replace(keyword, replaceword)

    
    # постинг в канал "Светский ежедневник"
    chat_id = '@SecularNA'
    
    try:
        await bot.send_message(chat_id=chat_id, text=message_to_send)
        print( "Отправил пост в канал ежедневника 📘 ✅" )
    except Exception:
        print( "Не удалось отправить пост в канал ежедневника 📘 ❌" )

    '''
    # постинг в каналы "Реалисты" и "Эволюция"
    chat_id_realists  = '-1002137516831'
    chat_id_evolution = '-1002201877923'
    
    try:
        await bot.send_message(chat_id=chat_id_realists, text=message_to_send)
        print( "Отправил пост в Реалистов ✅" )
    except Exception:
        print( "Не удалось отправить пост в Реалистов ❌" )

    try:
        await bot.send_message(chat_id=chat_id_evolution, text=message_to_send)
        print( "Отправил пост в Эволюцию ✅" )
    except Exception:
        print( "Не удалось отправить пост в Эволюцию ❌" )
    '''

    
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

        ai_response = escape_markdown_v2( completion.choices[0].message.content )
        ai_response = "*__Высказывание по книге__* 🗣️ \n\n" +ai_response

        # удаляем возможное присутствие системных настроек в выводе результата
        ai_response = ai_response.replace(role_system, '')    
        ai_response = ai_response.replace('Assistant:', '')
        ai_response = ai_response.replace('assistant:', '')
        ai_response = ai_response.replace('Конец', '')
        ai_response = ai_response.replace('конец', '')

        if has_glyphs(ai_response):
            print("has glyphs. try again... ⚙️ \n")
            attempts += 1
            continue

        if role_user in ai_response:
            print("role_user in message. try again... ⚙️ \n")
            attempts += 1
            continue

        if len( str(ai_response) ) < 450:
            print("too short response. try again... ⚙️ \n")
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
                          1 предложению описания на каждый. Раздели эти пункты и обозначь каждый одним эмодзи. """
        role_user = message_to_send

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ 
                {"role": "system", "content": role_system},
                {"role": "user", "content": role_user}
            ],
        )

        ai_response = escape_markdown_v2( completion.choices[0].message.content )
        ai_response = "*__Принципы программы__* 🌱 \n\n" +ai_response

        if has_glyphs(ai_response):
            print("has glyphs. try again... ⚙️ \n")
            attempts += 1
            continue

        if len( str(ai_response) ) < 450:
            print("too short response. try again... ⚙️ \n")
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
                          но не повторяют его. Каждый из двух пунктов раздели интервалом. 
                          На каждый пункт добавь один эмодзи. """
        role_user = message_to_send

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ 
                {"role": "system", "content": role_system},
                {"role": "user", "content": role_user}
            ],
        )

        ai_response = escape_markdown_v2( completion.choices[0].message.content )
        ai_response = "*__Темы для собраний__* 📌 \n\n" +ai_response

        if has_glyphs(ai_response):
            print("has glyphs. try again... ⚙️ \n")
            attempts += 1
            continue

        if len( str(ai_response) ) < 450:
            print("too short response. try again... ⚙️ \n")
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
                          чтобы следовать тексту. Каждый из трех пунктов раздели интервалом. 
                          На каждый пункт добавь один эмодзи. """
        role_user = message_to_send

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ 
                {"role": "system", "content": role_system},
                {"role": "user", "content": role_user}
            ],
        )

        ai_response = escape_markdown_v2( completion.choices[0].message.content )
        ai_response = "*__Задание на день__* 📝 \n\n" +ai_response

        if has_glyphs(ai_response):
            print("has glyphs. try again... ⚙️ \n")
            attempts += 1
            continue

        if len( str(ai_response) ) < 450:
            print("too short response. try again... ⚙️ \n")
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
