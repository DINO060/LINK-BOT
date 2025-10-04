from telegram import Update
from telegram.ext import ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande /start du bot"""
    help_text = """
🤖 **Bot de recherche de liens précis**

**Usage:**
`find <site-ou-URL> <mot-clé>`

**Exemples:**
• `find anime-sama.fr One Piece 1000`
• `find https://youtube.com chris brown`
• `find netflix.com stranger things`

**Fonctionnalités:**
✅ Recherche intelligente avec matching fuzzy
✅ Filtrage précis (mots entiers requis)
✅ Déduplication automatique
✅ Top 3 des meilleurs résultats
✅ Score de pertinence affiché

Le bot crawle le site donné et trouve les pages les plus pertinentes pour ton mot-clé.
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande /help du bot"""
    help_text = """
📖 **Aide détaillée**

**🔍 Recherche générale:** `find <site> <mot-clé>`
• Crawler intelligent avec scoring fuzzy
• Top 3 des meilleurs résultats
• Exemples: `find anime-sama.fr 86 EIGHTY SIX`

**🎯 Liens média directs:** `link <site/sibnet> <mot-clé> [--episode N]`
• Priorité Sibnet (plus rapide et direct)
• Fallback sites spécialisés si nécessaire
• Exemples: 
  - `link sibnet ONE PIECE`
  - `link anime-sama.fr ONE PIECE --episode 1089`

**⚡ Raccourci turbo:** `/fast <mots-clés>`
• Ultra-rapide pour anime-sama.fr
• Détection automatique d'épisode
• Priorité Sibnet
• Exemples:
  - `/fast ONE PIECE 1000 VF`
  - `/fast Attack on Titan saison 4`
  - `fast Naruto 500 VOSTFR` (sans /)

**✨ Avantages:**
• 🚀 `/fast` = Le plus rapide (recherche directe)
• 🎯 `link` = Liens normalisés avec fallback
• 🔍 `find` = Recherche complète et précise

**Tips:**
• Pour Sibnet: utilise `link sibnet <titre>`
• Pour sites spécialisés: `link <site> <titre>`
• Score affiché = pertinence (100 = parfait)
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def link_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande /link du bot"""
    help_text = """
🎯 **Commande /link - Liens média intelligents**

**Usage:** `link <site-ou-'sibnet'> <mot-clé> [--episode N]`

**Stratégie intelligente:**
1. 🚀 **Sibnet prioritaire** - Recherche directe la plus rapide
2. 🔄 **Fallback site** - Si Sibnet n'a rien, utilise le site spécifié
3. 🔗 **Normalisation** - Convertit automatiquement les embeds

**Exemples:**
• `link sibnet ONE PIECE` 
  → Cherche directement sur video.sibnet.ru
• `link anime-sama.fr ONE PIECE --episode 1089`
  → Cherche sur Sibnet, sinon sur anime-sama
• `link https://video.sibnet.ru/shell.php?videoid=123456 _`
  → Normalise en https://video.sibnet.ru/video123456

**Avantages vs find:**
✅ Plus rapide pour les médias
✅ Liens de partage directs  
✅ Support épisodes spécifiques
✅ Détection automatique Sibnet
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')