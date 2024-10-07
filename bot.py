import asyncio
from telegram import Bot
from g4f.client import Client

import os

from replacements import replacements, doReplacements # type: ignore
from state import attempts, has_glyphs, escape_markdown_v2, escape_system_text, \
    readTheBook, telegramPost, aiRequest  # type: ignore


async def main():
    bot_token = os.getenv('TELEGRAM_TOKEN')
    bot = Bot(token=bot_token)
    client = Client()

    channelBook = '@SecularNA'
    channelBill = '@BillSpeaks'

    # уникализация ежедневника (для всех сообществ)
    book = doReplacements( readTheBook() )
    message_to_send = escape_markdown_v2( book )
    

    # постинг в канал "Светский ежедневник"
    await telegramPost( bot, channelBook, message_to_send, 'Пост в канал ежедневника 📘')
    

    # высказывание по книге
    role_system = """ Выскажись по-русски, по тексту, в духе психологии. 
                          1-2 небольших абзаца. Добавь 3-5 эмодзи в текст. """
    title = 'Высказывание по книге 🗣️'

    ai_response = aiRequest( client, role_system, book, title )
    await telegramPost( bot, channelBill, ai_response, title )
    

    # принципы программы
    role_system = """ принципы программы: честность, непредубежденность, готовность, спокойствие, 
                      принятие, уверенность, доверие, капитуляция, надежда, верность принятому решению, 
                      мужество, обязательность, упорство, принятие себя, признание, терпение, сострадание, 
                      любовь, прощение, самодисциплина, чистосердечие, бескорыстие, непоколебимость. 
                      Приведи 3 принципа по тексту, над которыми сегодня надо работать, и напиши по 
                      1 предложению описания на каждый. Раздели эти принципы межстрочными отступами и 
                      обозначь каждый одним эмодзи. по-русски. """
    title = 'Принципы программы 🌱'

    ai_response = aiRequest( client, role_system, book, title )
    await telegramPost( bot, channelBill, ai_response, title )
    

    # темы для собраний
    role_system = """ Придумай 2 темы для обсуждения, которые косвенно перекликаются с текстом, 
                      но не повторяют его. Раздели эти принципы межстрочными отступами и 
                      обозначь каждый одним эмодзи. по-русски. """
    title = 'Темы для собраний 📌'

    ai_response = aiRequest( client, role_system, book, title )
    await telegramPost( bot, channelBill, ai_response, title )
    

    # задание на день 
    role_system = """ Придумай 3 действия на сегодняшний день, которые я могу сделать, 
                      чтобы следовать тексту. Раздели эти принципы межстрочными отступами и 
                      обозначь каждый одним эмодзи. по-русски. """
    title = 'Задание на день 📝'

    ai_response = aiRequest( client, role_system, book, title )
    await telegramPost( bot, channelBill, ai_response, title )
    
    
    # конечный вывод
    print( "Количество ошибок:", attempts, "из 20", flush=True )
    print( "Вся программа выполнена успешно! ✅ ✅ ✅ ", flush=True )

asyncio.run(main())
