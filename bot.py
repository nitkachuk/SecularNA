import asyncio
from telegram import Bot

import os
import datetime

def get_text():
    # Получаем сегодняшнюю дату
    today = datetime.date.today()
    
    # Добавляем один день к текущей дате, чтобы получить следующий день
    next_day = today + datetime.timedelta(days=1)
    next_day_day = next_day.day
    next_day_month = next_day.month

    # Путь к папке "book"
    folder_path = 'book'

    # Путь к папке следующего месяца
    month_folder_path = os.path.join(folder_path, str(next_day_month))

    # Формируем имя файла следующего дня (например, "1.txt", "2.txt", ..., "31.txt")
    next_day_file = f"{next_day_day}.txt"

    # Проверяем существование папки следующего месяца
    if os.path.exists(month_folder_path):
        # Путь к файлу следующего дня в следующем месяце
        file_path = os.path.join(month_folder_path, next_day_file)

        # Проверяем существование файла следующего дня
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
            return f"Файл для {next_day_day} числа не найден в папке месяца {next_day_month}."
    else:
        return f"Папка для месяца {next_day_month} не найдена в папке 'book'."


async def main():
    bot_token = '6541742098:AAE-hirxm_Dtl-9kQMAcRjlWGpy_JwQ2rYQ'
    chat_id = '@SecularNA'
    message_to_send = get_text()

    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=message_to_send)

asyncio.run(main())
