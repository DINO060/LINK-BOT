import urllib.parse
from telegram import Update
from telegram.ext import ContextTypes
from ..utils.precise_playwright_adapter import precise_site_search
from ..utils.media_link_resolver import resolve_media_link

async def handle_find_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Traite les commandes de recherche 'find'"""
    text = update.message.text.strip()
    
    # Parse: "find URL mot-clé"
    parts = text.split(maxsplit=2)
    
    if len(parts) < 3:
        help_msg = """
❌ **Format incorrect**

**Usage:** `find <site-ou-URL> <mot-clé>`

**Exemples:**
• `find anime-sama.fr One Piece`
• `find https://youtube.com drake`
        """
        await update.message.reply_text(help_msg, parse_mode='Markdown')
        return
    
    _, site_url, keyword = parts
    
    # Validation URL
    if not site_url.startswith(("http://", "https://")) and "." not in site_url:
        await update.message.reply_text("❌ URL invalide. Utilise un format comme `site.com` ou `https://site.com`")
        return
    
    # Message de chargement
    loading_msg = await update.message.reply_text(f"🔍 Recherche en cours sur **{site_url}** pour « **{keyword}** »...", parse_mode='Markdown')
    
    try:
        # Lancer la recherche
        results = await precise_site_search(site_url, keyword, top_k=3)
        
        # Supprimer le message de chargement
        await loading_msg.delete()
        
        if not results:
            await update.message.reply_text(f"❌ Aucun résultat suffisamment précis trouvé pour « **{keyword}** » sur {site_url}", parse_mode='Markdown')
            return
        
        # Formater les résultats
        response_lines = [f"🎯 **Résultats pour « {keyword} » sur {site_url}:**\n"]
        
        for i, result in enumerate(results, 1):
            title = result['title'][:80] + "..." if len(result['title']) > 80 else result['title']
            score = result['score']
            url = result['url']
            
            # Emojis selon le score
            if score >= 95:
                emoji = "🏆"
            elif score >= 90:
                emoji = "🥇"
            elif score >= 85:
                emoji = "🥈"
            else:
                emoji = "🥉"
            
            response_lines.append(f"{emoji} **{title}** `({score})`\n{url}\n")
        
        response_lines.append("_Score = pertinence (100 = parfait)_")
        
        await update.message.reply_text(
            "\n".join(response_lines), 
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
        
    except Exception as e:
        await loading_msg.delete()
        error_msg = f"❌ **Erreur lors de la recherche:**\n`{str(e)}`"
        await update.message.reply_text(error_msg, parse_mode='Markdown')

def _parse_episode_flag(parts):
    """Parse les flags --episode N dans une liste de mots"""
    episode = None
    rest = []
    it = iter(parts)
    for tok in it:
        if tok == "--episode":
            try:
                episode = int(next(it))
            except (StopIteration, ValueError):
                pass
        else:
            rest.append(tok)
    return " ".join(rest).strip(), episode

async def handle_link_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Traite les commandes 'link' - version intelligente avec Sibnet prioritaire"""
    text = update.message.text.strip()
    
    # Parse: "link site/sibnet mot-clé [--episode N]"
    parts = text.split()
    
    if len(parts) < 3:
        help_msg = """
❌ **Format incorrect**

**Usage:** `link <site-ou-'sibnet'> <mot-clé> [--episode N]`

**Exemples:**
• `link sibnet ONE PIECE` (recherche directe Sibnet)
• `link anime-sama.fr ONE PIECE --episode 1089`
• `link https://video.sibnet.ru/shell.php?videoid=123456 _` (normalise)
        """
        await update.message.reply_text(help_msg, parse_mode='Markdown')
        return
    
    _, site_or_alias, *tail = parts
    tail_text = " ".join(tail) if tail else ""
    query, episode = _parse_episode_flag(tail_text.split())
    
    # Alias 'sibnet' -> URL Sibnet
    if site_or_alias.lower() == "sibnet":
        site = "https://video.sibnet.ru/"
        display_name = "Sibnet"
    else:
        site = site_or_alias
        display_name = site_or_alias
    
    if not query:
        await update.message.reply_text("❌ Mot-clé manquant", parse_mode='Markdown')
        return
    
    # Message de chargement
    episode_text = f" (épisode {episode})" if episode else ""
    loading_msg = await update.message.reply_text(
        f"🔎 Recherche sur **{display_name}** → « **{query}** »{episode_text}...", 
        parse_mode='Markdown'
    )
    
    try:
        # Résolution intelligente
        res = await resolve_media_link(site, query, episode=episode)
        
        # Supprimer le message de chargement
        await loading_msg.delete()
        
        if not res["link"]:
            await update.message.reply_text("⚠️ Aucun lien fiable trouvé.", parse_mode='Markdown')
            return
        
        # Formater la réponse selon la source
        if res["source"] == "sibnet-direct":
            icon = "🔗"
            source_text = "Lien Sibnet normalisé"
        elif res["source"] == "sibnet-search":
            icon = "🎯"
            source_text = "Trouvé sur Sibnet"
        elif res["source"] == "site-search":
            icon = "🏆"
            score = res.get("score", 0)
            source_text = f"Trouvé sur le site (score: {score})"
        else:
            icon = "❓"
            source_text = "Source inconnue"
        
        response_lines = [
            f"{icon} **{source_text}**",
            f"📝 **Titre:** {res.get('title', 'N/A')}",
            f"� **Lien:** {res['link']}",
        ]
        
        if res.get("page") and res["page"] != res["link"]:
            response_lines.append(f"📄 **Page:** {res['page']}")
        
        await update.message.reply_text(
            "\n".join(response_lines),
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
        
    except Exception as e:
        await loading_msg.delete()
        error_msg = f"❌ **Erreur lors de la résolution:**\n`{str(e)}`"
        await update.message.reply_text(error_msg, parse_mode='Markdown')

async def handle_other_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Traite les messages qui ne sont pas des commandes"""
    text = update.message.text.strip().lower()
    
    if text.startswith("find "):
        await handle_find_command(update, context)
    elif text.startswith("link "):
        await handle_link_command(update, context)
    elif text.startswith("fast "):
        # Importer et utiliser le handler fast
        from .fast import handle_fast_message
        await handle_fast_message(update, context)
    else:
        help_msg = """
💡 **Commandes disponibles:**

🔍 `find <site> <mot-clé>` - Recherche précise sur un site
🎯 `link <site/sibnet> <mot-clé> [--episode N]` - Lien média intelligent
⚡ `fast <mots-clés>` - Raccourci turbo anime-sama.fr

**Exemples:**
• `link sibnet ONE PIECE`
• `find anime-sama.fr naruto`
• `link anime-sama.fr ONE PIECE --episode 1089`
• `fast ONE PIECE 1000 VF` ⚡

Ou utilise `/help` pour plus d'infos.
        """
        await update.message.reply_text(help_msg, parse_mode='Markdown')