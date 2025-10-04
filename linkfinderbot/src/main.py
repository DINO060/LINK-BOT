import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from config.settings import BOT_TOKEN
from bot.handlers.commands import start_command, help_command, link_command
from bot.handlers.messages import handle_other_messages
from bot.handlers.fast import handle_fast_command, handle_fast_message

# Configuration des logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Fonction principale du bot"""
    
    # Vérification du token
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN non configuré dans les variables d'environnement")
        return
    
    # Créer l'application
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Ajouter les handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("link", link_command))
    app.add_handler(CommandHandler("fast", handle_fast_command))  # Nouvelle commande turbo
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_other_messages))
    
    logger.info("🤖 Bot Telegram Link Finder démarré!")
    logger.info("📝 Commandes disponibles: /start, /help, /link, /fast")
    logger.info("📝 Messages: find <site> <mot-clé>, link <site/sibnet> <mot-clé>, fast <mots-clés>")
    
    # Lancer le bot
    app.run_polling()

if __name__ == "__main__":
    main()