# -*- coding: utf-8 -*-
"""
Handler pour la commande /fast - Raccourci turbo pour anime-sama.fr
"""
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from ..utils.fast_jump import episode_from_text, ddg_first_site
from ..utils.anime_sama_extractor import extract_anime_sama

HELP_FAST = '''
⚡ **Commande /fast** - Raccourci turbo pour anime-sama.fr

**Usage:** `/fast <mots-clés>`

**Exemples:**
• `/fast ONE PIECE 100 VF` → Trouve l'épisode 100 directement
• `/fast Naruto 500 VOSTFR` → Trouve l'épisode 500
• `/fast Attack on Titan saison 4` → Va à la page de l'anime

**Comment ça marche:**
1. 🦆 Recherche directe sur DuckDuckGo avec `site:anime-sama.fr`
2. 📖 Ouvre directement la page de l'anime trouvée
3. 🎯 Sélectionne automatiquement l'épisode s'il y a un nombre
4. 🎬 Teste les lecteurs et priorise Sibnet
5. ⚡ Résultat en quelques secondes !

**Avantages:**
• Ultra-rapide (pas de crawling)
• Détection automatique d'épisode
• Priorité à Sibnet
• Fonctionne avec VF/VOSTFR
'''

async def handle_fast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler pour /fast"""
    try:
        # Extraire la requête
        if context.args:
            query = " ".join(context.args)
        else:
            await update.message.reply_text(HELP_FAST, parse_mode='Markdown')
            return
        
        # Détecter le numéro d'épisode
        episode_num = episode_from_text(query)
        
        # Message initial
        status_msg = f"⚡ **Recherche turbo:** `{query}`"
        if episode_num:
            status_msg += f"\n🎯 **Épisode détecté:** {episode_num}"
        
        message = await update.message.reply_text(status_msg, parse_mode='Markdown')
        
        # Recherche directe via DuckDuckGo
        await message.edit_text(
            status_msg + f"\n🦆 Recherche sur anime-sama.fr...", 
            parse_mode='Markdown'
        )
        
        direct_url = ddg_first_site("anime-sama.fr", query)
        
        if not direct_url:
            await message.edit_text(
                f"❌ **Aucun résultat trouvé**\n"
                f"Recherche: `{query}`\n"
                f"Essayez avec des mots-clés différents.",
                parse_mode='Markdown'
            )
            return
        
        # Extraction avec anime_sama_extractor
        await message.edit_text(
            status_msg + f"\n✅ Page trouvée, extraction en cours...", 
            parse_mode='Markdown'
        )
        
        try:
            result = await extract_anime_sama(
                "anime-sama.fr",
                query,
                episode=episode_num,
                headless=True,
                direct_url=direct_url,      # Utiliser l'URL directe
                use_ddg_backup=False,       # Pas besoin, déjà fait
            )
        except Exception as e:
            await message.edit_text(
                f"❌ **Erreur d'extraction**\n"
                f"Erreur: `{str(e)}`\n"
                f"Page: {direct_url}",
                parse_mode='Markdown'
            )
            return
        
        # Construire la réponse finale
        if not result.get("matched"):
            await message.edit_text(
                f"⚠️ **Pas de lecteur fiable trouvé**\n"
                f"📖 **Page:** [Lien]({result.get('page_url', direct_url)})\n"
                f"ℹ️ **Raison:** {result.get('why', 'Inconnue')}\n"
                f"🔍 **Recherche:** `{query}`",
                parse_mode='Markdown',
                disable_web_page_preview=False
            )
            return
        
        # Succès !
        lines = [
            f"✅ **{result['titre']}**",
            f"🎯 **Épisode:** {result.get('episode_selected', '(par défaut)')}",
            f"🎬 **Lecteur:** {result.get('lecteur_label', 'Inconnu')}",
            f"🔗 **Lien:** {result.get('final_url', '(aucun)')}",
            f"📖 **Page:** [Voir sur anime-sama.fr]({result.get('page_url', direct_url)})",
            f"ℹ️ {result.get('why', '')}"
        ]
        
        final_text = "\n".join(lines)
        
        await message.edit_text(
            final_text,
            parse_mode='Markdown',
            disable_web_page_preview=False
        )
        
    except Exception as e:
        error_msg = f"❌ **Erreur inattendue**\n`{str(e)}`"
        
        try:
            await message.edit_text(error_msg, parse_mode='Markdown')
        except:
            await update.message.reply_text(error_msg, parse_mode='Markdown')

async def handle_fast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler pour les messages commençant par 'fast '"""
    text = update.message.text
    if not text or not text.lower().startswith('fast '):
        return
    
    # Extraire la requête après "fast "
    query = text[5:].strip()  # Enlever "fast " du début
    
    if not query:
        await update.message.reply_text(HELP_FAST, parse_mode='Markdown')
        return
    
    # Simuler context.args pour réutiliser la même logique
    context.args = query.split()
    await handle_fast_command(update, context)