from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import requests

TELEGRAM_TOKEN = "CENSURA"
CHATBOT_API_URL = "CENSURA" 


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    response = requests.post(CHATBOT_API_URL, json={"message": text}).json()
    await update.message.reply_text(response.get("reply", "❌ Errore"))

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Bot avviato!")
    app.run_polling()

if __name__ == '__main__':
    main()
