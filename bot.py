import asyncio
from telegram import Bot

import os
import datetime

def get_text():
    # Переменные для времени отправки (17:00)
    send_hour = 17
    send_minute = 0
    
    # Получаем текущие часы и минуты
    current_hour = datetime.datetime.now().hour
    current_minute = datetime.datetime.now().minute

    # Проверка текущего времени для определения даты для отправки
    if current_hour > send_hour or (current_hour == send_hour and current_minute >= send_minute):
        # Если текущее время больше или равно 17:00, отправляем текст за следующий день
        today = datetime.date.today() + datetime.timedelta(days=1)
    else:
        # Иначе отправляем текст за сегодняшний день
        today = datetime.date.today()

    current_day = today.day
    current_month = today.month

    # Путь к папке "book"
    folder_path = 'book'

    # Путь к папке текущего месяца
    month_folder_path = os.path.join(folder_path, str(current_month))

    # Формируем имя файла сегодняшнего дня (например, "1.txt", "2.txt", ..., "31.txt")
    today_file = f"{current_day}.txt"

    # Проверяем существование папки месяца
    if os.path.exists(month_folder_path):
        # Путь к файлу сегодняшнего дня в текущем месяце
        file_path = os.path.join(month_folder_path, today_file)

        # Проверяем существование файла сегодняшнего дня
        if os.path.exists(file_path):
            # Открываем файл и считываем его содержимое
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

                # Разделяем содержимое на абзацы
                paragraphs = content.split('\n\n')

                # Находим самый большой абзац
                largest_paragraph = max(paragraphs, key=len)

                # Разделяем содержимое самого большого абзаца на строки
                lines = largest_paragraph.splitlines()

                # Добавляем по две пустые строки до и после самого большого абзаца
                formatted_paragraph = '\n' + '\n\n'.join(lines) + '\n'

                # Заменяем самый большой абзац в тексте на разделенный по строкам
                formatted_content = content.replace(largest_paragraph, formatted_paragraph)

                # Возвращаем обработанный текст
                return formatted_content
        else:
            return f"Файл для {current_day} числа не найден в папке месяца {current_month}."
    else:
        return f"Папка для месяца {current_month} не найдена в папке 'book'."


async def main():
    bot_token = '6541742098:AAE-hirxm_Dtl-9kQMAcRjlWGpy_JwQ2rYQ'
    chat_id = '@SecularNA'
    message_to_send = get_text()

    # Добавляем разметку Markdown для форматирования текста
    formatted_message = f"*{message_to_send.splitlines()[0]}*\n\n_{message_to_send.splitlines()[1]}_\n\n**ТОЛЬКО СЕГОДНЯ:** {message_to_send.split('ТОЛЬКО СЕГОДНЯ:')[1]}"

    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=formatted_message)

asyncio.run(main())

