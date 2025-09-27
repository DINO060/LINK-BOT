from pyrogram import filters
from pyrogram.types import Message
from config import Config
from core.orchestrator import Orchestrator
from utils.helpers import parse_search_command, format_size
import logging

logger = logging.getLogger(__name__)

class CommandHandler:
    def __init__(self, config: Config, orchestrator: Orchestrator):
        self.config = config
        self.orchestrator = orchestrator
    
    async def handle_find(self, client, message: Message):
        """Commande /find <url> "titre" [lang]"""
        try:
            # Parse de la commande
            url, query, lang = parse_search_command(message.text)
            
            if not url or not query:
                await message.reply(
                    "❌ Format invalide\n"
                    "Utilisez: `/find <url> \"titre episode\" [lang]`\n"
                    "Exemple: `/find https://anime-sama.fr \"One Piece 1000\" vostfr`"
                )
                return
            
            # Message de traitement
            status_msg = await message.reply("🔍 Recherche en cours...")
            
            # Traitement de la requête
            result = await self.orchestrator.process_request(
                user_id=message.from_user.id,
                site_url=url,
                query=query,
                lang=lang
            )
            
            # Formatage de la réponse
            if result.success:
                response = f"✅ **Trouvé** (via {result.source})\n"
                response += f"📺 **{result.title or query}**\n\n"
                
                for i, link in enumerate(result.links[:5], 1):
                    response += f"**Lien {i}:**\n"
                    response += f"• Format: {link.format}\n"
                    if link.quality:
                        response += f"• Qualité: {link.quality}\n"
                    if link.size:
                        response += f"• Taille: {format_size(link.size)}\n"
                    response += f"• URL: `{link.url}`\n\n"
                
                await status_msg.edit(response)
                
            else:
                error_msg = f"❌ **Échec de l'extraction**\n"
                if result.error:
                    error_msg += f"Erreur: {result.error}"
                else:
                    error_msg += "Aucun lien trouvé. Vérifiez l'URL et le titre."
                
                await status_msg.edit(error_msg)
                
        except Exception as e:
            logger.error(f"Error in handle_find: {e}")
            await message.reply(f"❌ Erreur: {str(e)}")
    
    async def handle_status(self, client, message: Message):
        """Commande /status - Affiche le statut du bot"""
        cache_size = len(self.orchestrator.cache.cache)
        
        response = "📊 **Statut du Bot**\n\n"
        response += f"• Cache: {cache_size}/{self.config.CACHE_SIZE} entrées\n"
        response += f"• Limite globale: {self.config.REQUESTS_PER_MINUTE} req/min\n"
        response += f"• Limite par user: {self.config.REQUESTS_PER_USER} req/min\n"
        response += f"• Extracteurs actifs: {len(self.orchestrator.extractors)}\n"
        
        await message.reply(response)
    
    async def handle_clear_cache(self, client, message: Message):
        """Commande /clearcache - Vide le cache (admin uniquement)"""
        if message.from_user.id not in self.config.ADMIN_IDS:
            await message.reply("❌ Cette commande est réservée aux administrateurs.")
            return
        
        self.orchestrator.cache.clear()
        await message.reply("✅ Cache vidé avec succès.")
    
    async def handle_help(self, client, message: Message):
        """Commande /help - Affiche l'aide"""
        help_text = """
**🤖 Bot Extracteur de Liens Vidéo**

**Commandes disponibles:**

• `/find <url> "titre episode" [lang]` - Recherche et extrait les liens
  Exemple: `/find https://anime-sama.fr "One Piece 1000" vostfr`

• `/status` - Affiche le statut du bot
• `/help` - Affiche cette aide

**Sites supportés:**
• anime-sama.fr (extracteur dédié)
• 9anime, Gogoanime, KissAnime (via extracteurs)
• 1000+ autres sites (via yt-dlp)
• Tout autre site (via navigateur automatisé)

**Formats retournés:**
• MP4 - Fichiers vidéo directs
• M3U8 - Flux HLS
• WebM - Format vidéo alternatif

Le bot recherche automatiquement la meilleure source disponible.
        """
        await message.reply(help_text)
