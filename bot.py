import asyncio
from telegram import Bot

import os
import datetime

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

                largest_paragraph = max(paragraphs, key=len)

                lines = largest_paragraph.splitlines()

                formatted_paragraph = '\n' + '\n\n'.join(lines) + '\n'

                formatted_content = content.replace(largest_paragraph, formatted_paragraph)

                return formatted_content
        else:
            return f"Файл для {current_day} числа не найден в папке месяца {current_month}."
    else:
        return f"Папка для месяца {current_month} не найдена в папке 'book'."

async def main():
    # постинг в канал "Светский ежедневник"
    bot_token = '6541742098:AAE-hirxm_Dtl-9kQMAcRjlWGpy_JwQ2rYQ'
    chat_id = '@SecularNA'
    message_to_send = get_text()

    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=message_to_send)
    
    # постинг в канал "Реалисты"
    replacements = [
        {'keyword': 'АН', 'replaceword': 'АА'},

        {'keyword': 'Анонимные Наркоманы', 'replaceword': 'Анонимные Алкоголики'},
        {'keyword': 'Анонимные наркоманы', 'replaceword': 'Анонимные алкоголики'},
        {'keyword': 'анонимные наркоманы', 'replaceword': 'анонимные алкоголики'},
        {'keyword': 'анонимные Наркоманы', 'replaceword': 'анонимные Алкоголики'},

        {'keyword': 'Анонимных Наркоманов', 'replaceword': 'Анонимных Алкоголиков'},
        {'keyword': 'Анонимных наркоманов', 'replaceword': 'Анонимных алкоголиков'},
        {'keyword': 'анонимных наркоманов', 'replaceword': 'анонимных алкоголиков'},
        {'keyword': 'анонимных Наркоманов', 'replaceword': 'анонимных Алкоголиков'},

        {'keyword': 'Анонимным Наркоманам', 'replaceword': 'Анонимным Алкоголикам'},
        {'keyword': 'Анонимным наркоманам', 'replaceword': 'Анонимным алкоголикам'},
        {'keyword': 'анонимным наркоманам', 'replaceword': 'анонимным алкоголикам'},
        {'keyword': 'анонимным Наркоманам', 'replaceword': 'анонимным Алкоголикам'},

        {'keyword': 'Анонимными Наркоманами', 'replaceword': 'Анонимными Алкоголиками'},
        {'keyword': 'Анонимными наркоманами', 'replaceword': 'Анонимными алкоголиками'},
        {'keyword': 'анонимными наркоманами', 'replaceword': 'анонимными алкоголиками'},
        {'keyword': 'анонимными Наркоманами', 'replaceword': 'анонимными Алкоголиками'},

        {'keyword': 'Наркоманов',   'replaceword': 'Алкоголиков'},
        {'keyword': 'Наркоманы',    'replaceword': 'Алкоголики'},
        {'keyword': 'Наркоман',     'replaceword': 'Алкоголик'},
        {'keyword': 'Наркоманам',   'replaceword': 'Алкоголикам'},

        {'keyword': 'наркоманов',   'replaceword': 'алкоголиков'},
        {'keyword': 'наркоманы',    'replaceword': 'алкоголики'},
        {'keyword': 'наркоман',     'replaceword': 'алкоголик'},
        {'keyword': 'наркоманам',   'replaceword': 'алкоголикам'},

        {'keyword': 'Наркотиков',       'replaceword': 'Алкоголя'},
        {'keyword': 'Наркотики',        'replaceword': 'Алкоголь'},
        {'keyword': 'Наркотиками',      'replaceword': 'Алкоголем'},
        {'keyword': 'Наркотикам',       'replaceword': 'Алкоголю'},
        {'keyword': 'Наркотик',         'replaceword': 'Алкоголь'},

        {'keyword': 'наркотиков',       'replaceword': 'алкоголя'},
        {'keyword': 'наркотики',        'replaceword': 'алкоголь'},
        {'keyword': 'наркотиками',      'replaceword': 'алкоголем'},
        {'keyword': 'наркотикам',       'replaceword': 'алкоголю'},
        {'keyword': 'наркотик',         'replaceword': 'алкоголь'},

        {'keyword': 'Наркозависимость',     'replaceword': 'Алкозависимость'},
        {'keyword': 'Наркозависимости',     'replaceword': 'Алкозависимости'},
        {'keyword': 'Наркозависимый',       'replaceword': 'Алкозависимый'},
        {'keyword': 'Наркозависимых',       'replaceword': 'Алкозависимых'},
        {'keyword': 'Наркозависимому',      'replaceword': 'Алкозависимому'},
        {'keyword': 'Наркозависимыми',      'replaceword': 'Алкозависимыми'},
        {'keyword': 'Наркозависимым',       'replaceword': 'Алкозависимым'},
        {'keyword': 'Наркозависим',         'replaceword': 'Алкозависим'},

        {'keyword': 'наркозависимость',     'replaceword': 'алкозависимость'},
        {'keyword': 'наркозависимости',     'replaceword': 'алкозависимости'},
        {'keyword': 'наркозависимый',       'replaceword': 'алкозависимый'},
        {'keyword': 'наркозависимых',       'replaceword': 'алкозависимых'},
        {'keyword': 'наркозависимому',      'replaceword': 'алкозависимому'},
        {'keyword': 'наркозависимыми',      'replaceword': 'алкозависимыми'},
        {'keyword': 'наркозависимым',       'replaceword': 'алкозависимым'},
        {'keyword': 'наркозависим',         'replaceword': 'алкозависим'},

        {'keyword': '', 'replaceword': ''}
    ]
    message_to_send_2 = get_text()

    for replacement in replacements:
        keyword = replacement['keyword']
        replaceword = replacement['replaceword']
        message_to_send_2 = message_to_send_2.replace(keyword, replaceword)

    lines = message_to_send_2.split('\n')
    lines.insert(0, "Атеистический ежедневник АА\n")
    del lines[5]
    message_to_send_2 = '\n'.join(lines)

    bot_token_2 = '6541742098:AAE-hirxm_Dtl-9kQMAcRjlWGpy_JwQ2rYQ'
    chat_id_2 = '-1002137516831'

    bot = Bot(token=bot_token_2)
    await bot.send_message(chat_id=chat_id_2, text=message_to_send_2)

asyncio.run(main())
