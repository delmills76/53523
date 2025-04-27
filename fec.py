import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Конфигурация DeepSeek
DEEPSEEK_API_KEY = os.getenv("sk-d8c1ff6e92014e969365ea7d5a619265")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Конфигурация Telegram
TELEGRAM_TOKEN = os.getenv("7810472277:AAHj2EOu_ZSo79PjshC5n8UWh1fkExewcr4")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот с интеграцией DeepSeek AI. Задайте мне любой вопрос!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    try:
        # Формируем запрос к DeepSeek API
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [
                {"role": "user", "content": user_message}
            ],
            "model": "deepseek-chat",
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers)
        response_data = response.json()
        
        if response.status_code == 200:
            answer = response_data["choices"][0]["message"]["content"]
            await update.message.reply_text(answer)
        else:
            error_msg = response_data.get("error", {}).get("message", "Unknown error")
            await update.message.reply_text(f"Ошибка API: {error_msg}")

    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("Произошла ошибка при обработке запроса")

def main():
    """Запуск бота"""
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запуск бота
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()