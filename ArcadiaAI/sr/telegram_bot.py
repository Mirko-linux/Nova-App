
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters, CommandHandler
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHATBOT_API_URL = "https://arcadiaai.onrender.com/chat"

# Dizionario per la memoria contestuale per ogni utente
user_histories = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # Recupera o crea la cronologia per l'utente
    history = user_histories.get(user_id, [])
    history.append({"role": "user", "message": text})

    # Invia la cronologia al backend
    try:
        response = requests.post(
            CHATBOT_API_URL,
            json={
                "message": text,
                "conversation_history": history
            },
            timeout=30
        )
        data = response.json()
        reply = data.get("reply", "❌ Errore")
    except Exception as e:
        reply = f"❌ Errore: {e}"

    # Aggiungi la risposta del bot alla cronologia
    history.append({"role": "assistant", "message": reply})
    user_histories[user_id] = history[-20:]  # Mantieni solo gli ultimi 20 messaggi

    await update.message.reply_text(reply)

from telegram.constants import ParseMode
from telegraph import Telegraph

telegraph = Telegraph()
telegraph.create_account(short_name="ArcadiaAI")

def publish_to_telegraph(title, content):
    response = telegraph.create_page(
        title=title,
        html_content=content.replace('\n', '<br>'),
        author_name="ArcadiaAI"
    )
    return "https://telegra.ph/{}".format(response["path"])

async def pubblica_telegraph(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args or "|" not in " ".join(context.args):
            await update.message.reply_text("Usa: /pubblica_telegraph Titolo | Testo")
            return

        titolo, testo = " ".join(context.args).split("|", 1)
        url = publish_to_telegraph(titolo.strip(), testo.strip())

        await update.message.reply_text(f"✅ Pubblicato su Telegraph: {url}")

        # Invia il post nel canale da cui è stato eseguito il comando
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"📰 Nuovo post su Telegraph:\n{url}",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Errore: {e}")
    
# === Avvio bot ===
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("pubblica_telegraph", pubblica_telegraph))
    print("🤖 Bot avviato!")
    app.run_polling()

if __name__ == '__main__':
    main()