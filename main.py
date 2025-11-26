import os
import logging
import requests
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ----------------------------------------------------
# 1. CONFIGURACIÓN Y VARIABLES GLOBALES
# ----------------------------------------------------

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# API de Diccionario en ESPAÑOL
DICTIONARY_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/" 

# ----------------------------------------------------
# 2. FUNCIONES AUXILIARES
# ----------------------------------------------------

def escape_markdown_v2(text: str) -> str:
    """Escapa caracteres especiales de MarkdownV2 para evitar errores."""
    return re.sub(r'([_*[\]()~`>#+\-=|{}.!])', r'\\\1', text)

async def fetch_word_data(word: str, update: Update) -> dict | None:
    """Busca los datos de una palabra en la API y maneja errores comunes."""
    url = f"{DICTIONARY_API_URL}{word.lower()}"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            await update.message.reply_text(
                f"Lo siento, la palabra **{word.capitalize()}** no fue encontrada en el diccionario\.", 
                parse_mode="MarkdownV2"
            )
            return None
        else:
            await update.message.reply_text("Error al consultar el diccionario\. Intenta de nuevo\.")
            return None
            
    except requests.exceptions.RequestException:
        await update.message.reply_text("Error de conexión al servidor del diccionario\.")
        return None
    except Exception as e:
        logging.error(f"Error al procesar la respuesta de la API: {e}")
        await update.message.reply_text("Ocurrió un error al procesar la respuesta de la API\.")
        return None

# ----------------------------------------------------
# 3. HANDLERS DE COMANDOS
# ----------------------------------------------------

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        f"¡Hola {user.mention_html()}! Soy tu Bot de consulta\. Usa /ayuda para ver mis comandos\.",
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📚 **Comandos Disponibles**:\n\n"
        "**DICCIONARIO**:\n"
        "`/definir <palabra>` \- Definición principal\.\n"
        " Te ayuda a definir una palabra en inglés\n"
        "Esto ayuda a ampliar tu vocabulario en tu segundo idioma\n\n"
        "`/sinonimos <palabra>` \- Ver sinónimos\.\n"
        "`/antonimos <palabra>` \- Ver antónimos\.\n"
        "Para palabras en inglés \n\n"
        "**EXTRAS**:\n"
        "`/chiste` \- Chiste aleatorio\.\n"
        "`/start` \- Reiniciar\.\n"
        "`/ayuda` \- Esta lista\.",
        parse_mode="MarkdownV2" 
    )

async def joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = "https://icanhazdadjoke.com/"
    headers = {'Accept': 'application/json'}
    
    await update.message.reply_text("Buscando un chiste\.\.\. ⏳", parse_mode="MarkdownV2")
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            chiste = data.get("joke", "Sin chiste disponible.")
            await update.message.reply_text(escape_markdown_v2(chiste), parse_mode="MarkdownV2")
        else:
            await update.message.reply_text(f"Error en API de chistes: {response.status_code}\.")
    except requests.exceptions.RequestException:
        await update.message.reply_text("Error de conexión con el servidor de chistes\.")

async def definir_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Uso: `/definir <palabra>`\.", parse_mode="MarkdownV2")
        return
    word = " ".join(context.args)
    await update.message.reply_text(f"Buscando definición para **{word.capitalize()}**\.\.\. 📖", parse_mode="MarkdownV2")
    
    data = await fetch_word_data(word, update)
    if data is None: return

    try:
        entry = data[0]
        meaning = entry['meanings'][0]
        part_of_speech = escape_markdown_v2(meaning['partOfSpeech'].capitalize())
        definition = escape_markdown_v2(meaning['definitions'][0]['definition'])
        example = escape_markdown_v2(meaning['definitions'][0].get('example', 'Sin ejemplo.').capitalize())

        message = (
            f"**{word.capitalize()}**\n"
            f"\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\n"
            f"🗣️ **Tipo:** {part_of_speech}\n"
            f"📖 **Definición:** {definition}\n"
            f"💡 **Ejemplo:** _{example}_"
        )
        await update.message.reply_text(message, parse_mode="MarkdownV2")
    except Exception:
        await update.message.reply_text(f"No encontré una definición clara para **{word.capitalize()}**\.", parse_mode="MarkdownV2")

async def sinonimos_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Uso: `/sinonimos <palabra>`\.", parse_mode="MarkdownV2")
        return
    word = " ".join(context.args)
    data = await fetch_word_data(word, update)
    if data is None: return
    
    sinonimos = []
    for entry in data:
        for meaning in entry.get('meanings', []):
            sinonimos.extend(meaning.get('synonyms', []))
    
    if sinonimos:
        unique = escape_markdown_v2(", ".join(list(set(sinonimos))))
        await update.message.reply_text(f"**Sinónimos de {word.capitalize()}**:\n{unique}", parse_mode="MarkdownV2")
    else:
        await update.message.reply_text(f"No encontré sinónimos para **{word.capitalize()}**\.", parse_mode="MarkdownV2")

async def antonimos_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Uso: `/antonimos <palabra>`\.", parse_mode="MarkdownV2")
        return
    word = " ".join(context.args)
    data = await fetch_word_data(word, update)
    if data is None: return
    
    antonimos = []
    for entry in data:
        for meaning in entry.get('meanings', []):
            antonimos.extend(meaning.get('antonyms', []))
    
    if antonimos:
        unique = escape_markdown_v2(", ".join(list(set(antonimos))))
        await update.message.reply_text(f"**Antónimos de {word.capitalize()}**:\n{unique}", parse_mode="MarkdownV2")
    else:
        await update.message.reply_text(f"No encontré antónimos para **{word.capitalize()}**\.", parse_mode="MarkdownV2")

async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Dijiste: {update.message.text}")

# ----------------------------------------------------
# 4. ARRANQUE
# ----------------------------------------------------

def main() -> None:
    """Inicia el bot."""
    # Tu token debe ser pasado aquí o estar en las variables de entorno
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8332297959:AAHz8-lTxWgTVAWhTySmYtyfVbJyxxFJjCU")

    application = Application.builder().token(TOKEN).build()
    
    # Registrar los Handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("ayuda", help_command))
    application.add_handler(CommandHandler("chiste", joke_command))
    
    # HANDLERS DE DICCIONARIO
    application.add_handler(CommandHandler("definir", definir_command))
    application.add_handler(CommandHandler("sinonimos", sinonimos_command))
    application.add_handler(CommandHandler("antonimos", antonimos_command))
    
    # Handler de mensajes de texto (si no es comando)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))

    # Inicia el polling
    logging.info("El bot ha iniciado. Esperando mensajes...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()