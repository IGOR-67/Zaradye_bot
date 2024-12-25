import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
from fuzzywuzzy import fuzz
from gtts import gTTS
import os
import glob
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
from telegram.ext import filters     # Импортируем фильтры для обработки сообщений
from config import TOKEN             # Импортируем токен бота из файла config.py

# Загружаем данные о растениях из CSV-файла
CSV_PATH = r"C:\Data_sets\data-60861-2024-08-06.csv"
df_plants = pd.read_csv(CSV_PATH, sep=';', encoding='utf-8', on_bad_lines='skip')
# Убираем строки, где ID равен 'Код'
df_plants = df_plants[df_plants['ID'] != 'Код'].reset_index(drop=True)

# Загружаем модель BERT для обработки вопросов
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModelForQuestionAnswering.from_pretrained("bert-base-uncased")

# Функция для озвучивания текста
def text_to_speech(text):
    tts = gTTS(text=text, lang='ru')  # Создаем объект gTTS для преобразования текста в речь
    audio_path = 'response.mp3'  # Путь для сохранения аудиофайла
    tts.save(audio_path)  # Сохраняем аудиофайл
    return audio_path  # Возвращаем путь к аудиофайлу

# Функция для получения изображений растений по латинскому названию
def get_plant_images(latin_name):
    image_dir = f'C:/Users/Mikl/zaryadye_bot/plant_images/{latin_name}'  # Путь к директории с изображениями
    if os.path.exists(image_dir):  # Проверяем, существует ли директория
        return sorted(glob.glob(f'{image_dir}/Image_*.jpg'))  # Возвращаем отсортированный список изображений
    return []  # Если директория не найдена, возвращаем пустой список

# Функция для получения информации о растениях на основе вопроса
def get_plant_info(question):
    # Обработка запросов о хвойных растениях
    if 'хвойные' in question.lower():
        conifer_plants = df_plants[df_plants['LandscapingZone'].str.contains('Хвойный', na=False)]
        response = "Хвойные растения в парке:\n" + "\n".join(conifer_plants['Name'].tolist())
        return response, True

    # Обработка запросов о смешанных лесах
    if 'смешанный лес' in question.lower():
        mixed_forest = df_plants[df_plants['LandscapingZone'].str.contains('Смешанный', na=False)]
        response = "Растения смешанного леса:\n" + "\n".join(mixed_forest['Name'].tolist())
        return response, True

    # Обработка запросов о всех растениях
    if 'все растения' in question.lower() or 'список растений' in question.lower():
        response = "Растения в парке:\n" + "\n".join(df_plants['Name'].tolist())
        return response, True

    # Нечеткое соответствие для названий растений
    max_ratio = 0
    matched_name = None
    for name in df_plants['Name'].unique():
        ratio = fuzz.partial_ratio(name.lower(), question.lower())  # Вычисляем степень совпадения
        if ratio > max_ratio and ratio > 70:  # Если совпадение выше 70%
            max_ratio = ratio
            matched_name = name  # Сохраняем наиболее подходящее название растения

    if matched_name:  # Если найдено совпадение
        plant = df_plants[df_plants['Name'] == matched_name].iloc[0]  # Получаем данные о растении
        latin_name = plant['LatinName']  # Получаем латинское название
        images = get_plant_images(latin_name)  # Получаем изображения растения

        # Определяем ответ на основе вопроса
        if any(word in question.lower() for word in ['где', 'расположен', 'растет']):
            response = f"{matched_name} расположен в {plant['LocationPlace']}."
        elif any(word in question.lower() for word in ['когда', 'цветет', 'цветение']):
            response = f"{matched_name} цветет в период: {plant['ProsperityPeriod']}."
        elif 'латинск' in question.lower():
            response = f"Латинское название {matched_name}: {plant['LatinName']}."
        else:
            response = f"{matched_name} (латинское название: {latin_name})\n{plant['Description']}"

        return response, images  # Возвращаем ответ и изображения

    return "Растение не найдено.", []  # Если растение не найдено

# Обработчик команды /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Я бот для консультации по растениям парка Зарядье. Задайте мне вопрос.")

# Обработчик текстовых сообщений
def handle_message(update: Update, context: CallbackContext):
    question = update.message.text  # Получаем текст вопроса от пользователя
    response, images = get_plant_info(question)  # Получаем ответ и изображения

    if images:  # Если есть изображения
        update.message.reply_text(response)  # Отправляем текст ответа
        for img in images:  # Отправляем каждое изображение
            with open(img, 'rb') as image_file:
                update.message.reply_photo(photo=image_file)
    else:
        update.message.reply_text(response)  # Если изображений нет, отправляем только текст

    # Озвучивание ответа
    audio_path = text_to_speech(response)  # Преобразуем текст в речь
    with open(audio_path, 'rb') as audio_file:
        update.message.reply_audio(audio_file)  # Отправляем аудиофайл

# Основная функция для запуска бота
def main():
    updater = Updater(TOKEN)  # Создаем объект Updater с токеном
    dp = updater.dispatcher  # Получаем диспетчер для обработки сообщений
    dp.add_handler(CommandHandler("start", start))  # Добавляем обработчик команды /start
    dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # Добавляем обработчик текстовых сообщений
    updater.start_polling()  # Запускаем опрос обновлений
    updater.idle()  # Ожидаем завершения работы

if __name__ == '__main__':
    main()  # Запускаем основную функцию

