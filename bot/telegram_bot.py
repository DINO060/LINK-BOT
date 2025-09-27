from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
from core.orchestrator import Orchestrator
from bot.commands import CommandHandler
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class VideoLinkBot:
    def __init__(self):
        self.config = Config()
        self.orchestrator = Orchestrator(self.config)
        self.command_handler = CommandHandler(self.config, self.orchestrator)
        
        import time
        session_name = f"video_bot_{int(time.time())}"
        
        self.app = Client(
            session_name,
            api_id=self.config.API_ID,
            api_hash=self.config.API_HASH,
            bot_token=self.config.BOT_TOKEN
        )
        
        self.setup_handlers()
    
    def setup_handlers(self):
        """Configure les gestionnaires de commandes"""
        
        @self.app.on_message(filters.command("find"))
        async def find_command(client, message: Message):
            await self.command_handler.handle_find(client, message)
        
        @self.app.on_message(filters.command("status"))
        async def status_command(client, message: Message):
            await self.command_handler.handle_status(client, message)
        
        @self.app.on_message(filters.command("clearcache"))
        async def clear_cache_command(client, message: Message):
            await self.command_handler.handle_clear_cache(client, message)
        
        @self.app.on_message(filters.command("help"))
        async def help_command(client, message: Message):
            await self.command_handler.handle_help(client, message)
        
        @self.app.on_message(filters.command("start"))
        async def start_command(client, message: Message):
            welcome = """
👋 **Bienvenue sur Video Link Extractor Bot!**

Je peux extraire les liens directs de vidéos depuis n'importe quel site web.

Utilisez `/help` pour voir toutes les commandes disponibles.

Exemple rapide:
`/find https://anime-sama.fr "One Piece 1000" vostfr`
            """
            await message.reply(welcome)
    
    def run(self):
        """Lance le bot"""
        logger.info("Starting Video Link Bot...")
        self.app.run()
