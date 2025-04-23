import os
import asyncio
import telebot
import g4f
import unicodedata
import threading
import speech_recognition as sr
from pydub import AudioSegment

telegram_token = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(telegram_token)


def voice_to_text(message):
    try:
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        ogg_path = 'voice.ogg'
        wav_path = 'voice.wav'

        with open(ogg_path, 'wb') as f:
            f.write(downloaded_file)

        AudioSegment.from_ogg(ogg_path).export(wav_path, format='wav')

        r = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio = r.record(source)
            text = r.recognize_google(audio, language="ru-RU")
            return text

    except sr.UnknownValueError:
        return "Не понял голосовое сообщение."
    except sr.RequestError as e:
        return f"Ошибка сервиса распознавания: {e}"
    except Exception as e:
        return f"Ошибка: {e}"
    finally:
        if os.path.exists(ogg_path): os.remove(ogg_path)
        if os.path.exists(wav_path): os.remove(wav_path)


def has_glyphs(text):
    for char in text:
        if unicodedata.category(char) == 'Lo':
            return True
    return False

@bot.message_handler(
    func=lambda message: message.from_user.username in ['kristina_superstar', 'gothicspring', '@Kungfuoko'],
    content_types=['text', 'voice']  # ← обязательно!
)


def echo_all(message):
    attempt_count = 0  
    
    while True:
        try:
            attempt_count += 1  # увеличение счетчика попыток
            
            if attempt_count > 1:
                sent_message = bot.reply_to(message, f'Секундочку... #{attempt_count}')  # ответ 1
            else:
                sent_message = bot.reply_to(message, 'Секундочку...')  # ответ 1

            if attempt_count >= 10:
                bot.delete_message(message.chat.id, sent_message.message_id)  # Удаление сообщения "Секундочку..."
                bot.reply_to(message, "Превышено количество попыток  ✖️")  # ответ 2
                break

            # голосовое
            if message.content_type == 'voice':
                txt = ''
            if message.content_type == 'text':
                txt = message.text
            
            txt += " по-русски"
            response = g4f.ChatCompletion.create(
                model=g4f.models.gpt_4,
                messages=[ 
                    {"role": "system", "content": "ответь по-русски"},
                    {"role": "user", "content": txt}
                 ],
            )

            txt = voice_to_text( message )

            if has_glyphs( response ):
                bot.delete_message(message.chat.id, sent_message.message_id)  # Удаление сообщения "Секундочку..."
                continue

            bot.delete_message(message.chat.id, sent_message.message_id)  # Удаление сообщения "Секундочку..."
            bot.reply_to(message, response)  # ответ 2

            break

        except telebot.apihelper.ApiTelegramException as e:
            # Обработка исключения, чтобы скрипт не завершался при ошибке API Telegram
            err = "Произошла ошибка API Telegram"
            print(err, e)
            bot.delete_message(message.chat.id, sent_message.message_id)  # Удаление сообщения "Секундочку..."
            continue

        except Exception as e:
            # Другие исключения
            err = "Произошла неизвестная ошибка"
            print(err, e)
            bot.delete_message(message.chat.id, sent_message.message_id)  # Удаление сообщения "Секундочку..."
            continue 

    attempt_count = 0  # сброс счетчика попыток после успешной отправки

bot.polling()
