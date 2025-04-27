import os
import io
from PIL import Image
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Конфигурация Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
vision_model = genai.GenerativeModel('gemini-pro-vision')  # Модель для работы с изображениями
text_model = genai.GenerativeModel('gemini-pro')            # Модель для текстовых запросов

# Конфигурация Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я могу анализировать изображения и текст с помощью Gemini AI. "
        "Отправь мне фото с подписью или просто текст!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = ""
    images = []
    
    # Обработка изображений
    if update.message.photo:
        # Берем фото наивысшего качества
        photo_file = await update.message.photo[-1].get_file()
        image_data = await photo_file.download_as_bytearray()
        images.append(Image.open(io.BytesIO(image_data)))
        
        # Получаем подпись к фото или используем стандартный запрос
        user_message = update.message.caption or "Что изображено на фото?"

    # Обработка текста (если нет изображений)
    elif update.message.text:
        user_message = update.message.text
    
    else:
        await update.message.reply_text("Пожалуйста, отправьте текст или изображение")
        return

    try:
        # Формируем запрос
        if images:
            # Для мультимодальных запросов используем vision_model
            response = vision_model.generate_content([user_message, *images])
        else:
            # Для текстовых запросов используем text_model
            response = text_model.generate_content(user_message)
        
        if response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("Не могу обработать этот запрос")

    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("Произошла ошибка при обработке запроса")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(
        (filters.PHOTO | filters.TEXT) & ~filters.COMMAND, 
        handle_message
    ))
    
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()