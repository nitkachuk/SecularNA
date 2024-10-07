import asyncio
from telegram import Bot
from g4f.client import Client

from replacements import replacements, doReplacements # type: ignore
from secondary import has_glyphs, escape_markdown_v2, escape_system_text, read_the_book  # type: ignore


async def main():
    bot_token = os.getenv('TELEGRAM_TOKEN')
    bot = Bot(token=bot_token)

    # уникализация ежедневника (для всех сообществ)
    book = doReplacements( read_the_book() )
    message_to_send = escape_markdown_v2( book )
    
    # постинг в канал "Светский ежедневник"
    telegramPost( '@SecularNA', message_to_send, 'канал ежедневника 📘 ✅' )

    # try:
    #     await bot.send_message(chat_id=chat_id, text=message_to_send, parse_mode='MarkdownV2')
    #     print( "Отправил пост в канал ежедневника 📘 ✅" )
    # except Exception as e:
    #     print( "Не удалось отправить пост в канал ежедневника 📘 ❌" )
    #     print( "Ошибка:", e, " ⚙️ \n" )

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
        role_user = book

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ 
                {"role": "system", "content": role_system},
                {"role": "user", "content": role_user}
            ],
        )

        ai_response = escape_system_text( escape_markdown_v2( 
            doReplacements(completion.choices[0].message.content) ), role_system  )
        ai_response = "*__Высказывание по книге__* 🗣️ \n\n" +ai_response

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
        role_user = book

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ 
                {"role": "system", "content": role_system},
                {"role": "user", "content": role_user}
            ],
        )

        ai_response = escape_system_text( escape_markdown_v2( 
            doReplacements(completion.choices[0].message.content) ) )
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
        role_user = book

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ 
                {"role": "system", "content": role_system},
                {"role": "user", "content": role_user}
            ],
        )

        ai_response = escape_system_text( escape_markdown_v2( 
            doReplacements(completion.choices[0].message.content) ) )
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
        role_user = book

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ 
                {"role": "system", "content": role_system},
                {"role": "user", "content": role_user}
            ],
        )

        ai_response = escape_system_text( escape_markdown_v2( 
            doReplacements(completion.choices[0].message.content) ) )
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
