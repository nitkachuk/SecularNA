import unicodedata
import re

import os
import datetime

import sys

def has_glyphs( text ):
    for char in text:
        if unicodedata.category(char) == 'Lo':
            return True
    return False

import re

def escape_markdown_v2(text):
    escape_chars = [  '[', ']', '(', ')', '~', 'Ⓝ', '>', '#', '+', '-', 
                      '=', '|', '{', '}', '.', ',', '!', '?', '\\', '""'  ]
    
    for char in escape_chars:
        pattern = re.escape(char)
        text = re.sub(pattern, f"\\{char}", text)  # Экранирование одной косой чертой
    
    return text

def escape_system_text( text, role_system='' ):
    text = text.replace( '_{"code":200,"status":true,"model":"gpt-3.5-turbo","gpt":"', '')
    text = text.replace( '","original":null}', '')

    text = text.replace(role_system, '')    
    text = text.replace('Assistant:', '')
    text = text.replace('assistant:', '')
    text = text.replace('Конец', '')
    text = text.replace('конец', '')
    return text
    

def readTheBook():
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

                return final_content
        else:
            return f"Файл для {current_day} числа не найден в папке месяца {current_month}."
    else:
        return f"Папка для месяца {current_month} не найдена в папке 'book'."

async def telegramPost( bot, chat_id, message_to_send, title ):
    try:
        await bot.send_message(chat_id=chat_id, text=message_to_send, parse_mode='MarkdownV2')
        print( f"{title} ✅" )
    except Exception as e:
        print( f"{title} ❌" )
        print( "Ошибка тг:", e, " ⚙️ \n" )
