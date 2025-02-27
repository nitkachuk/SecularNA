import asyncio
from g4f.client import Client

from replacements import replacements, doReplacements  # type: ignore
from state import attempts, has_glyphs, escape_markdown_v2, escape_system_text, \
    readTheBook, telegramPost, aiRequest, channelBook, channelBill, \
    channelPoets, createMessage, checkNAholiday   # type: ignore
from roulette import getRandomTheme   # type: ignore


async def main():
    global attempts
    
    # уникализация ежедневника (для всех сообществ)
    book = doReplacements( readTheBook( 1 ) )    # книга без разметки
    message_to_send = escape_markdown_v2( doReplacements( readTheBook() ) )

    # постинг в канал "Светский ежедневник"
    title = [ 'пост в канал ежедневника', '📘' ]
    await telegramPost( channelBook, message_to_send, title)

    # # постинг NA праздников
    # title = [ 'Сегодня в NA праздник!', '🎉' ]
    # holiday = checkNAholiday()
    
    # if holiday:
    #     await telegramPost( channelBook, holiday, title )
    
    # высказывание по книге 🗣️
    role_system = """ Выскажись по-русски, по тексту, в духе психологии. 
                      1-2 небольших абзаца. Добавь 3-5 эмодзи в текст. По-русски. """
    title = [ 'Высказывание по книге', '🗣️' ]

    ai_response = aiRequest( role_system, book )
    ai_response = createMessage( ai_response, title )
    
    await telegramPost( channelBill, ai_response, title )

    
    # темы для собраний 📌
    role_system = """ по-русски. Придумай 2 темы для обсуждения, которые косвенно перекликаются 
                      с текстом, но не повторяют его. Раздели эти принципы межстрочными пробелами и 
                      обозначь каждый одним эмодзи. По-русски. """
    title = [ 'Темы для собраний', '📌' ]

    ai_response = aiRequest( role_system, book )
    ai_response = createMessage( ai_response, title )
    
    await telegramPost( channelBill, ai_response, title )

    
    # рулетка тем 🍒
    themeText = getRandomTheme()
    role_system = """ по-русски. Сочини 2-3 предложения, которые кратко выскажутся по тексту
                      в духе психологии. Сделай красивые межстрочные пробелы и добавь 2 
                      эмодзи. По-русски. """
    title = [ 'Рулетка! Случайная тема', '🍒' ]

    ai_response = aiRequest( role_system, themeText, 200 )
    ai_response = createMessage( ai_response, title, f"## {themeText}" )
    
    await telegramPost(  channelBill, ai_response, title )
    

    # шаги и традиции 🧘🏼
    role_system = """ по-русски. Найди один из 12 шагов, который соответствует тексту. Кратко опиши в чем 
                      шаг перекликается с текстом. Найди одну из 12 традиций, которая соответствует 
                      тексту. Кратко опиши в чем шаг перекликается с текстом. Раздели эти шаг и 
                      традицию межстрочными пробелами и обозначь каждый одним эмодзи. По-русски. """
    title = [ 'Шаги и традиции', '🧘🏼' ]

    ai_response = aiRequest( role_system, book )
    ai_response = createMessage( ai_response, title )
    
    await telegramPost( channelBill, ai_response, title )
    

    # принципы программы 🌱
    role_system = """ по-русски. принципы программы: честность, непредубежденность, готовность, спокойствие, 
                      принятие, уверенность, доверие, капитуляция, надежда, верность принятому решению, 
                      мужество, обязательность, упорство, принятие себя, признание, терпение, сострадание, 
                      любовь, прощение, самодисциплина, чистосердечие, бескорыстие, непоколебимость. 
                      Приведи 2 принципа по тексту, над которыми сегодня надо работать, и напиши по 
                      1 предложению описания на каждый. Раздели эти принципы межстрочными пробелами и 
                      обозначь каждый одним эмодзи. по-русски. """
    title = [ 'Принципы программы', '🌱' ]

    ai_response = aiRequest( role_system, book )
    ai_response = createMessage( ai_response, title )
    
    await telegramPost( channelBill, ai_response, title )


    # черты характера 🎭
    role_system = """ по-русски. Приведи 1 негативную черту характера по тексту, над которой сегодня надо работать, 
                      и напиши 1 предложение описания этой негативной черты. Приведи 1 черту позитивную характера, 
                      которая подходит для проработки негативной черты и напиши 1 предложение описания этой 
                      позитивной черты характера. Раздели эти черты межстрочными пробелами и обозначь каждый 
                      одним эмодзи. по-русски. """
    title = [ 'Черты характера', '🎭' ]

    ai_response = aiRequest( role_system, book )
    ai_response = createMessage( ai_response, title )
    
    await telegramPost( channelBill, ai_response, title )
    

    # задание на день 📝
    role_system = """ по-русски. Придумай 3 действия на сегодняшний день, которые я могу сделать, 
                      чтобы следовать тексту. Раздели эти принципы межстрочными пробелами и 
                      обозначь каждый одним эмодзи. строго без медитации. по-русски. """
    title = [ 'Задание на день', '📝' ]

    ai_response = aiRequest( role_system, book )
    ai_response = createMessage( ai_response, title )
    
    await telegramPost( channelBill, ai_response, title )


    # общество тайных поэтов 
    # role_system = """ По-русски. очисти контекст. возьми один случайный жанр поэзии. первой строкой
    #                   укажи жанр поэзии жирным и оступи вниз. дай 2 четверостишья этого 
    #                   жанра поэзии. через межстрочные интервалы с разделителями-эмодзи дай 2 
    #                   предложения про этот жанр поэзии. через межстрочные интервалы с разделителями
    #                   -эмодзи дай 2 поэта-представителей этого жанра поэзии. на каждого поэта две 
    #                   строчки стихов из литературного творчества этого поэта. По-русски. """
    
    # role_system = """ По-русски. очисти контекст. возьми один стих случайного поэта. первой строкой
    #                   укажи название стиха жирным и оступи вниз. дай 2 четверостишья этого 
    #                   стиха. через межстрочные интервалы с разделителями-эмодзи дай 2 информационных
    #                   предложения про этот стих. через межстрочные интервалы с разделителями
    #                   -эмодзи дай пару строчек инфо про этот жанр поэзии. дай пару строчек инфо про
    #                    этого поэта. назови его имя. По-русски. """
    
    # title = [ '\nОбщество тайных поэтов', '🎩' ]

    # ai_response = aiRequest( role_system, book, 200 )
    # ai_response = createMessage( ai_response, title, '', 0 )
    
    # await telegramPost( channelPoets, ai_response, title )

    
    # конечный вывод
    print( "Количество ошибок:", attempts, "из 20", flush=True )
    print( "Вся программа выполнена успешно! ✅ ✅ ✅ ", flush=True )

asyncio.run(main())
