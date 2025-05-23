import unicodedata, re, os, datetime, sys, requests, g4f, random, asyncio
from replacements import doReplacements 


bot_token = os.getenv('TELEGRAM_TOKEN')

channelBook = '@SecularNA'
channelBill = '@BillSpeaks'
channelPoets = '@secret_poets'

attempts = 0


def has_glyphs( text ):
    for char in text:
        if unicodedata.category(char) == 'Lo':
            return True
    return False

# def has_latins(text):
#     text = re.sub(r'<pre>.*?</pre>', '', text, flags=re.DOTALL)

#     latins_count = len(re.findall(r'[a-zA-Z]', text))
#     total_count = len(text)
#     if total_count == 0:
#         return False
#     return latins_count / total_count > 0.5  

def has_latins(text):
    text = re.sub(r'<pre>.*?</pre>', '', text, flags=re.DOTALL)
    letters = re.findall(r'[a-zA-Zа-яА-Я]', text)
    if not letters:
        return False
    latins = re.findall(r'[a-zA-Z]', ''.join(letters))
    return len(latins) / len(letters) > 0.5

def escape_markdown_v2(text, plus_underline = 0):
    escape_chars = [  '[', ']', '(', ')', '~', 'Ⓝ', '>', '#', '+', '-', 
                      '=', '|', '{', '}', '.', ',', '!', '?', '\\', '""', '```'  ]
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

# def escape_system_text(text, role_system=''):
#     system_text = [
#         '_{"code":200,"status":true,"model":"gpt-3.5-turbo","gpt":"',
#         '","original":null}', 'Assistant:', 'assistant:', 'Конец', 'конец',
#         'Только сегодня: ', 'Только Сегодня: ', 'ТОЛЬКО СЕГОДНЯ: ', role_system,
#         'Создай своего интеллектуального друга',  # начало рекламы
#         'HeyReal',
#         'узнай больше',  # ссылка
#         'https://',  # URL
#         'https://pollinations.ai'  # URL
#         'pollinations'
#     ]

#     for pattern in system_text:
#         text = text.replace(pattern, '')

#     # Удаляем всё после рекламного блока, если вдруг осталось
#     text = re.split(r'Создай своего|HeyReal\.ai|узнай больше|https?://', text)[0].strip()

#     return text

def escape_system_text(text, role_system=''):
    # Фразы, при наличии которых строка полностью удаляется
    ad_phrases = ['Создай своего', 'HeyReal', 'узнай больше', 'https://', 'pollinations']

    # Удаляем строки с рекламой
    text = '\n'.join(
        line for line in text.splitlines()
        if not any(p in line for p in ad_phrases)
    )

    # Простой список заменяемых фрагментов
    patterns = [
        '_{"code":200,"status":true,"model":"gpt-3.5-turbo","gpt":"',
        '","original":null}', 'Assistant:', 'assistant:', 'Конец', 'конец',
        'Только сегодня: ', 'Только Сегодня: ', 'ТОЛЬКО СЕГОДНЯ: ', role_system
    ]
    for p in patterns:
        text = text.replace(p, '')

    # Удалить всё после первых признаков рекламы
    text = re.split(r'Создай своего|HeyReal\.ai|узнай больше|https?://', text)[0].strip()

    return text


def escapeAiMarkdown( text ):
    while '_' in text or '__' in text:
        text = text.replace('_', '').replace('__', '')

    while '*' in text or '**' in text:
        text = text.replace('*', '').replace('**', '')
        
    return text


def has_refusal( text ):
  text = text.lower()
    
  pattern = r'\bизвините\b.*\bя не могу\b.*\bвыполнить\b.*\bзапрос\b'
  match = re.search(pattern, text, re.IGNORECASE)
    
  return bool(match)


def has_g4fError( text ):
  text = text.lower()
    
  pattern = r'\bmodel not found\b.*\btoo long input\b'
  match = re.search(pattern, text, re.IGNORECASE)
    
  return bool(match)


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
                
                p_lines[0] = f'{emoji[0]}   {p_lines[0]}'        # дата
                p_lines[1] = f'__{p_lines[1]}__'                 # заголовок
                p_lines[3] = f'_{p_lines[3]}_'                   # цитата
                p_lines[4] = f'{emoji[1]}   *{p_lines[4]}*'      # источник

                # объединить дату и заголовок
                p_lines[0] += "   " +p_lines[1]
                p_lines[1] = ''

                paragraphs[0] = '\n'.join(p_lines)
                paragraphs[2] = paragraphs[2].replace(f"ТОЛЬКО СЕГОДНЯ:", f"{emoji[0]}   *ТОЛЬКО СЕГОДНЯ:*")

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


def createMessage( text, title, title2 = '', ifPostTitles = 1 ):
    if not int( ifPostTitles ):
        return text
    
    title = escape_markdown_v2( title[0] ), title[1]
    
    if title2:
        title2 = f'_{title2}_\n\n'
    title2 = escape_markdown_v2( title2 )
        
    return f'*__{title[0]}__* {title[1]}\n\n{title2}{text}\n\n'


async def telegramPost( chat_id, message_to_send, title ):
    global attempts
    getTitle = title[0]+ " " +title[1]
    
    try:
        requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data={"chat_id": chat_id, "text": message_to_send, "parse_mode": "MarkdownV2"},
        )
        print( f"{getTitle} ✅ \n", flush=True )
    except Exception as e:
        print( f"{getTitle} ❌", flush=True )
        print("Ошибка тг:", type(e).__name__, e, " ⚙️", flush=True)
        print( "Пост:", message_to_send )
        attempts += 1


def aiRequest( role_system, role_user, symbols = 250 ):
    global attempts
    
    while True:
        if attempts >= 20:
            print("\nПревышено количество попыток \nотправки сообщения. Цикл завершен. 💀💀💀", flush=True)
            raise SystemExit    # завершаем всю программу по истечению попыток

        try:
            response = g4f.ChatCompletion.create(
                model=g4f.models.gpt_4,
                messages=[ 
                    {"role": "system", "content": role_system},
                    {"role": "user", "content": role_user}
                 ],
            )
        except Exception as e:
            print( f"{getTitle} ❌", flush=True )
            print("Ошибка g4f:", type(e).__name__, e, " ⚙️", flush=True)
            print( "Запрос:", role_user )
            attempts += 1

        # 1 (очистка от системных настроек в выводе) 
        ai_response = escape_system_text( 
            escapeAiMarkdown( 
                response 
            ), role_system 
        )

        # 2 (очистка от иероглифов)
        if has_glyphs(ai_response):
            print("has glyphs. try again... ⚙️", flush=True)
            print( "''" +ai_response+ "''\n" )
            attempts += 1
            continue

        # 3 (очистка от g4f ошибки)
        if has_g4fError(ai_response):
            print("has 'Model not found or unknown error' try again... ⚙️", flush=True)
            attempts += 1
            continue

        # 4 (очистка от латиницы)
        if has_latins(ai_response):
            print("has latins. try again... ⚙️", flush=True)
            print( "''" +ai_response+ "''\n" )
            attempts += 1
            continue

        # 5 (проверка на длину сообщения)
        if int( len( str(ai_response) ) ) < int( symbols ):
            print("too short response. try again... ⚙️", flush=True)
            print( "''" +ai_response+ "''\n" )
            attempts += 1
            continue

        # 6 (очистка от отказа нейросети)
        if has_refusal(ai_response):
            print("has refusal. try again... ⚙️", flush=True)
            print( "''" +ai_response+ "''\n" )
            attempts += 1
            continue

        ai_response = doReplacements( ai_response )
        return escape_markdown_v2( ai_response, 1 )
        

def getEmoji( source = 'базовый' ):
    massiv = [  ]

    # 0
    month = int( datetime.datetime.now().month )
    day =   int( datetime.datetime.now().day )

    # поправка на 1 день вперед (часовые пояса)
    next_day = datetime.datetime.now() + datetime.timedelta(days=1)
    month = next_day.month
    day = next_day.day
    
    emojis = [ '',
        '☃️', '❄️',            # зима
        '☘️', '🌱', '🌺',    # весна
        '🌞', '🏖️', '☀️',    # лето
        '🌧', '🍂', '🍁',    # осень
        '❄️' ]

    emoji = emojis[ month ]

    if month == 1 and day in range(1,11):
        emoji =  '🎄'
    if month == 1 and day == 7:
        emoji =  '🎁'
    if month == 2 and day == 14:
        emoji =  '💌'
    if month == 3 and day == 8:
        emoji =  '🌺'
    if month == 10 and day == 30:
        emoji =  '👻'
    if month == 10 and day ==31:
        emoji = '🎃'
    if month == 11 and day == 1:
        emoji =  '💀'
    if month == 12 and day == 31:
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
    
    for NAholiday in NAholidays:
        if NAholiday['month'] == today.month and NAholiday['day'] == today.day:
            return NAholiday['text']

    return ''
    
