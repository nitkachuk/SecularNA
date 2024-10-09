import asyncio
from g4f.client import Client

from replacements import replacements, doReplacements  # type: ignore
from state import attempts, has_glyphs, escape_markdown_v2, escape_system_text, \
    readTheBook, telegramPost, aiRequest, channelBook, channelBill, \
    createMessage   # type: ignore
from roulette import getRandomTheme   # type: ignore


async def main():
    # уникализация ежедневника (для всех сообществ)
    book = doReplacements( readTheBook() )
    message_to_send = escape_markdown_v2( book )

    # постинг в канал "Светский ежедневник"
    await telegramPost( channelBook, message_to_send, 'Пост в канал ежедневника 📘')
    return    

    
    # высказывание по книге 🗣️
    role_system = """ Выскажись по-русски, по тексту, в духе психологии. 
                      1-2 небольших абзаца. Добавь 3-5 эмодзи в текст. По-русски. """
    title = 'Высказывание по книге 🗣️'

    ai_response = aiRequest( role_system, book )
    ai_response = createMessage( ai_response, title )
    await telegramPost( channelBill, ai_response, title )

    
    # темы для собраний 📌
    role_system = """ Придумай 2 темы для обсуждения, которые косвенно перекликаются с текстом, 
                      но не повторяют его. Раздели эти принципы межстрочными пробелами и 
                      обозначь каждый одним эмодзи. По-русски. """
    title = 'Темы для собраний 📌'

    ai_response = aiRequest( role_system, book )
    ai_response = createMessage( ai_response, title )
    await telegramPost( channelBill, ai_response, title )

    
    # рулетка 🍒
    themeText = getRandomTheme()
    role_system = """ Сочини 2-3 предложения, которые кратко опишут текст. Сделай красивые 
                      межстрочные пробелы и добавь 2 эмодзи. По-русски. """
    title = 'Рулетка! Случайная тема 🍒'

    ai_response = aiRequest( role_system, themeText )
    ai_response = createMessage( ai_response, title, f"##{themeText}" )
    
    await telegramPost(  channelBill, ai_response, title )
    

    # шаги и традиции 🧘🏼
    role_system = """ Найди один из 12 шагов, который соответствует тексту. Кратко опиши в чем 
                      шаг перекликается с текстом. Найди одну из 12 традиций, которая соответствует 
                      тексту. Кратко опиши в чем шаг перекликается с текстом. Раздели эти шаг и 
                      традицию межстрочными пробелами и обозначь каждый одним эмодзи. По-русски. """
    title = 'Шаги и традиции 🧘🏼'

    ai_response = aiRequest( role_system, book )
    ai_response = createMessage( ai_response, title )
    
    await telegramPost( channelBill, ai_response, title )
    

    # принципы программы 🌱
    role_system = """ принципы программы: честность, непредубежденность, готовность, спокойствие, 
                      принятие, уверенность, доверие, капитуляция, надежда, верность принятому решению, 
                      мужество, обязательность, упорство, принятие себя, признание, терпение, сострадание, 
                      любовь, прощение, самодисциплина, чистосердечие, бескорыстие, непоколебимость. 
                      Приведи 2 принципа по тексту, над которыми сегодня надо работать, и напиши по 
                      1 предложению описания на каждый. Раздели эти принципы межстрочными пробелами и 
                      обозначь каждый одним эмодзи. по-русски. """
    title = 'Принципы программы 🌱'

    ai_response = aiRequest( role_system, book )
    ai_response = createMessage( ai_response, title )
    await telegramPost( channelBill, ai_response, title )


    # черты характера 🎭
    role_system = """ Приведи 1 негативную черту характера по тексту, над которой сегодня надо работать, и напиши 
                      1 предложение описания этой негативной черты. Приведи 1 черту позитивную характера, которая 
                      подходит для проработки негативной черты и напиши 1 предложение описания этой позитивной 
                      черты характера. Раздели эти черты межстрочными пробелами и обозначь каждый одним 
                      эмодзи. по-русски. """
    title = 'Черты характера 🎭'

    ai_response = aiRequest( role_system, book )
    ai_response = createMessage( ai_response, title )
    await telegramPost( channelBill, ai_response, title )
    

    # задание на день 📝
    role_system = """ Придумай 3 действия на сегодняшний день, которые я могу сделать, 
                      чтобы следовать тексту. Раздели эти принципы межстрочными пробелами и 
                      обозначь каждый одним эмодзи. по-русски. """
    title = 'Задание на день 📝'

    ai_response = aiRequest( role_system, book )
    ai_response = createMessage( ai_response, title )
    await telegramPost( channelBill, ai_response, title )

    
    # конечный вывод
    print( "\nКоличество ошибок:", attempts, "из 20", flush=True )
    print( "Вся программа выполнена успешно! ✅ ✅ ✅ ", flush=True )

asyncio.run(main())
