import os
import asyncio
import telebot
import g4f
import unicodedata

telegram_token = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(telegram_token)

def has_glyphs(text):
    for char in text:
        if unicodedata.category(char) == 'Lo':
            return True
    return False

#@bot.message_handler(func=lambda message: True)
#@bot.message_handler(func=lambda message: message.from_user.username == 'kristina_superstar')

@bot.message_handler(func=lambda message: message.from_user.username in ['kristina_superstar', 'gothicspring', 'Kungfuoko'])

def echo_all(message):
    attempt_count = 0      # счетчик попыток отправки
    sec_error_text = ''    # Текст ошибок в "Секундочку..."
    
    while True:
        try:
            attempt_count += 1  # увеличение счетчика попыток
            if attempt_count > 1:
                sent_message = bot.reply_to(message, f'Секундочку... #{attempt_count} ({sec_error_text})')  # ответ 1
                sec_error_text = ''
            else:
                sent_message = bot.reply_to(message, 'Секундочку...')  # ответ 1

            if attempt_count >= 10:
                bot.delete_message(message.chat.id, sent_message.message_id)  # Удаление сообщения "Секундочку..."
                bot.reply_to(message, "Ошибка. Превышено количество попыток.)")  # ответ 2
                break

            txt = message.text + " по-русски"
            
            response = g4f.ChatCompletion.create(
                model=g4f.models.gpt_4,
                messages=[ 
                    {"role": "system", "content": "ответь по-русски, если есть блоки кода или цитат или списков, то оберни их в pre по примеру <pre>текст</pre>"},
                    {"role": "user", "content": txt}
                 ],
            )

            response = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', response)


            if has_glyphs( response ):
                bot.delete_message(message.chat.id, sent_message.message_id)  # Удаление сообщения "Секундочку..."
                sec_error_text = 'иероглифы'
                continue

            bot.delete_message(message.chat.id, sent_message.message_id)  # Удаление сообщения "Секундочку..."
            if "<pre>" in response:
                bot.reply_to(message, response, parse_mode='HTML')
            else:
                bot.reply_to(message, response)

            break

        except telebot.apihelper.ApiTelegramException as e:
            # Обработка исключения, чтобы скрипт не завершался при ошибке API Telegram
            err = "Произошла ошибка API Telegram"
            sec_error_text = err
            print(err, e)
            bot.delete_message(message.chat.id, sent_message.message_id)  # Удаление сообщения "Секундочку..."
            continue

        except Exception as e:
            # Другие исключения
            err = "Произошла неизвестная ошибка (Exception as e)"
            sec_error_text = err
            print(err, e)
            bot.delete_message(message.chat.id, sent_message.message_id)  # Удаление сообщения "Секундочку..."
            continue 

    attempt_count = 0  # сброс счетчика попыток после успешной отправки

bot.polling()
