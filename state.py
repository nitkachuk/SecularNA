import unicodedata
import re 

import os
import datetime

import sys
from replacements import doReplacements 

from telegram import Bot
from g4f.client import Client

import random


bot_token = os.getenv('TELEGRAM_TOKEN')
bot = Bot(token=bot_token)
client = Client()

channelBook = '@SecularNA'
channelBill = '@BillSpeaks'

attempts = 0


def has_glyphs( text ):
    for char in text:
        if unicodedata.category(char) == 'Lo':
            return True
    return False

def has_latins( text ):
    latins_count = len(re.findall(r'[a-zA-Z]', text))
    #total_count = len(text)
    
    return latins_count > 10
    

def escape_markdown_v2(text, plus_underline = 0):
    escape_chars = [  '[', ']', '(', ')', '~', 'Ⓝ', '>', '#', '+', '-', 
                      '=', '|', '{', '}', '.', ',', '!', '?', '\\', '""'  ]
    if plus_underline:
        escape_chars += [ '_' ]
    
    for char in escape_chars:
        pattern = re.escape(char)
        
        if char == '\\':
            replacement = '\\\\'
        else:
            replacement = '\\' + char
        text = re.sub(pattern, replacement, text)

    text = text.replace('\\\\', '\\')
    return text


def escape_system_text( text, role_system='' ):
    text = text.replace( '_{"code":200,"status":true,"model":"gpt-3.5-turbo","gpt":"', '')
    text = text.replace( '","original":null}', '')

    text = text.replace(role_system, '')    
    text = text.replace('Assistant:', '')
    text = text.replace('assistant:', '')
    text = text.replace('Конец', '')
    text = text.replace('конец', '')

    text = text.replace('Только сегодня: ', '')
    text = text.replace('ТОЛЬКО СЕГОДНЯ: ', '')
    return text


def escapeUnderline( text ):
    while '_' in text or '__' in text:
        text = text.replace('_', '').replace('__', '')
    return text


def readTheBook( clean = 0 ):
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
                emoji = getEmoji( p_lines[4] )

                if clean != 0:
                    emoji = [''] * len(emoji)
                
                p_lines[0] = f"{emoji[0]} {p_lines[0]}"         # дата
                p_lines[1] = f"__{p_lines[1]}__"                # заголовок
                p_lines[3] = f"_{p_lines[3]}_"                  # цитата
                p_lines[4] = f"{emoji[1]} *{p_lines[4]}*"       # источник

                paragraphs[0] = '\n'.join(p_lines)
                paragraphs[2] = paragraphs[2].replace(f"ТОЛЬКО СЕГОДНЯ:", f"{emoji[0]} *ТОЛЬКО СЕГОДНЯ:*")

                largest_paragraph = max(paragraphs, key=len)
                lines = largest_paragraph.splitlines()
                formatted_paragraph = '\n' + '\n\n'.join(lines) + '\n'
                paragraphs[paragraphs.index(largest_paragraph)] = formatted_paragraph

                final_content = '\n\n'.join(paragraphs)

                return final_content
        else:
            return f"Файл для {current_day} числа не найден в папке месяца {current_month}."
    else:
        return f"Папка для месяца {current_month} не найдена в папке 'book'."


def createMessage( text, title, title2 = '' ):
    title = escape_markdown_v2( title[0] ), title[1]
    
    if title2:
        title2 = f"_{title2}_\n\n"
    title2 = escape_markdown_v2( title2 )
        
    return f"*__{title[0]}__* {title[1]}\n\n{title2}{text}"


async def telegramPost( chat_id, message_to_send, title ):
    global attempts
    getTitle = title[0]+ " " +title[1]
    
    try:
        await bot.send_message(chat_id=chat_id, text=message_to_send, parse_mode='MarkdownV2')
        print( f"{getTitle} ✅ \n", flush=True )
    except Exception as e:
        print( f"{getTitle} ❌", flush=True )
        print( "Ошибка тг:", e, " ⚙️", flush=True )
        print( "Пост:", message_to_send )
        attempts += 1


def aiRequest( role_system, role_user ):
    global attempts
    
    while True:
        if attempts >= 20:
            print("Превышено количество попыток отправки сообщения. Цикл завершен. 💀💀💀", flush=True)
            raise SystemExit    # завершаем всю программу по истечению попыток
                
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ 
                {"role": "system", "content": role_system},
                {"role": "user", "content": role_user}
            ],
        )

        # 1 (очистка от системных настроек в выводе) 
        ai_response = escape_system_text( 
            escapeUnderline( completion.choices[0].message.content ), 
            role_system 
        )

        # 2 (очистка от иероглифов)
        if has_glyphs(ai_response):
            print("has glyphs. try again... ⚙️", flush=True)
            attempts += 1
            continue

        # 3 (очистка от латиницы)
        if has_latins(ai_response):
            print("has latins. try again... ⚙️", flush=True)
            attempts += 1
            continue

        # 4 (проверка на длину сообщения)
        if len( str(ai_response) ) < 250:
            print("too short response. try again... ⚙️", flush=True)
            attempts += 1
            continue

        ai_response = doReplacements( ai_response )
        return escape_markdown_v2( ai_response, 1 )
        

def getEmoji( source = 'базовый' ):
    massiv = [  ]

    # 0
    month = int( datetime.datetime.now().month )
    day = int( datetime.datetime.now().strftime("%-d") )
    
    emojis = [
        '🎄', '☃️',            # зима
        '☘️', '🌱', '🌺',    # весна
        '🌞', '🏖️', '☀️',    # лето
        '🍃', '🍂', '🍁',    # осень
        '❄️'
    ]

    emoji = emojis[ month ]

    if month == 0 and day == 7:
        emoji =  '🎁'
    if month == 1 and day == 14:
        emoji =  '💌'
    if month == 2 and day == 8:
        emoji =  '🌺'
    if month == 9 and day == 30:
        emoji =  '👻'
    if month == 9 and day ==31:
        emoji = '🎃'
    if month == 10 and day == 1:
        emoji =  '💀'
    if month == 11 and day == 31:
        emoji =  '🎅'

    massiv += [ emoji ]


    # 1
    if 'базовый' in source.lower():
        massiv += [ '📘' ]
    else:
        massiv += [ '📄' ]


    # 2
    emoji = [ '📖', '📑', '📌', '➡️', '👇', '✨', '⚪️', 
              '〰️', '•', '📚', '📓', '📕', '📗', '🗂', 
              '📙', '🗞', '📰', '📄', '📃', '📑', '🧾', 
              '📊', '📈', '📉', '🗃', '📂' ]

    massiv += [ random.choice( emoji ) ]

    return massiv
    

def checkNAholiday():
    NAholidays = [
        { 'month': 9, 'day': 10, 'text': '''В этот самый день, только более 70 лет 
        назад 5 октября 1953 года состоялось самое первое собрание Анонимных Наркоманов! ⭐'''   }
    ]
    today = datetime.date.today()
    title = [ 'Сегодня в NA праздник!', '🎉' ]
    
    for NAholiday in NAholidays:
        if NAholidays['month'] == today.month and NAholidays['day] == today.day:
             await telegramPost( channelBook, NAholidays['text'], title )
