import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Конфигурация Gemini
GEMINI_API_KEY = os.getenv("7810472277:AAHj2EOu_ZSo79PjshC5n8UWh1fkExewcr4")
genai.configure(api_key=GEMINI_API_KEY)
vision_model = genai.GenerativeModel('gemini-pro-vision')
text_model = genai.GenerativeModel('gemini-pro')

# Конфигурация Telegram
TELEGRAM_TOKEN = os.getenv("7810472277:AAHj2EOu_ZSo79PjshC5n8UWh1fkExewcr4")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я могу анализировать изображения и текст через Gemini AI. "
        "Отправь мне фото с описанием или просто текст!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = ""
    images = []
    
    if update.message.photo:
        # Скачиваем фото как байты
        photo_file = await update.message.photo[-1].get_file()
        image_data = await photo_file.download_as_bytearray()
        
        # Определяем MIME-тип из расширения файла
        file_extension = photo_file.file_path.split('.')[-1].lower()
        mime_type = (
            "image/jpeg" if file_extension in ("jpg", "jpeg") else
            "image/png" if file_extension == "png" else
            "image/webp" if file_extension == "webp" else 
            "image/jpeg"  # fallback
        )
        
        images.append({
            "mime_type": mime_type,
            "data": bytes(image_data)
        })
        
        user_message = update.message.caption or "Опиши что на фото?"

    elif update.message.text:
        user_message = update.message.text
    else:
        await update.message.reply_text("Отправьте текст или фото")
        return

    try:
        if images:
            # Собираем мультимодальный запрос
            contents = [user_message] + images
            response = vision_model.generate_content(contents)
        else:
            response = text_model.generate_content(user_message)

        await update.message.reply_text(response.text if response.text else "Не могу обработать запрос")

    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("Ошибка обработки запроса")

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