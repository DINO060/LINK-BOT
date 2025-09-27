# 🎬 Video Link Extractor Bot

Bot Telegram intelligent pour extraire les liens directs de vidéos depuis n'importe quel site web, sans télécharger les fichiers.

## ✨ Fonctionnalités

- 🔍 **Recherche intelligente** : Trouve automatiquement les vidéos sur n'importe quel site
- 🎯 **Multi-extracteurs** : Utilise des extracteurs spécialisés pour les sites majeurs
- 🌐 **Support universel** : Compatible avec 1000+ sites via yt-dlp
- 🤖 **Fallback automatique** : Utilise Playwright si les autres méthodes échouent
- 💾 **Système de cache** : Réponses instantanées pour les recherches répétées
- ⚡ **Rate limiting** : Protection contre les abus
- 📊 **Multi-formats** : Support MP4, M3U8, WebM et plus

## 📁 Structure du Projet

```
video_link_bot/
├── main.py                 # Point d'entrée principal
├── config.py              # Configuration centralisée
├── bot/
│   ├── telegram_bot.py    # Bot Telegram principal
│   └── commands.py        # Gestionnaire de commandes
├── core/
│   ├── orchestrator.py    # Orchestrateur intelligent
│   ├── cache.py          # Système de cache LRU
│   └── rate_limiter.py   # Limiteur de requêtes
├── extractors/
│   ├── base.py           # Classe de base
│   ├── animesama.py      # Extracteur anime-sama
│   ├── ytdlp_handler.py  # Wrapper yt-dlp
│   └── playwright_handler.py  # Navigateur automatisé
└── utils/
    └── helpers.py         # Fonctions utilitaires
```

## 🚀 Installation Rapide

### Prérequis
- Python 3.10+
- Un bot Telegram (créé via @BotFather)
- API credentials Telegram (depuis my.telegram.org)

### Installation pas à pas

1. **Cloner le projet**
```bash
git clone https://github.com/yourusername/video-link-bot.git
cd video-link-bot
```

2. **Créer l'environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Installer les dépendances**
```bash
pip install pyrogram tgcrypto yt-dlp playwright httpx beautifulsoup4 python-dotenv
```

4. **Installer Playwright et Chromium**
```bash
python -m playwright install chromium
```

5. **Configuration**
```bash
# Créer le fichier .env
cat > .env << EOL
BOT_TOKEN=your_bot_token_here
API_ID=your_api_id
API_HASH=your_api_hash
EOL

# Éditer avec vos vraies valeurs
nano .env  # ou vim, notepad, etc.
```

6. **Lancer le bot**
```bash
python main.py
```

## 💬 Commandes Disponibles

### `/find <url> "titre episode" [langue]`
Recherche et extrait les liens directs

**Exemples:**
```
/find https://anime-sama.fr "One Piece 1000" vostfr
/find https://gogoanime.hu "Naruto 220" 
/find https://site.com "video name"
```

### `/status`
Affiche le statut du bot (cache, limites, etc.)

### `/help`
Affiche l'aide complète

### `/clearcache`
Vide le cache (admin seulement)

## ⚙️ Configuration Avancée

### Variables d'environnement (.env)

```env
# Bot Telegram
BOT_TOKEN=your_bot_token
API_ID=12345
API_HASH=your_api_hash

# Limites (optionnel)
REQUESTS_PER_MINUTE=10
REQUESTS_PER_USER=5

# Cache (optionnel)
CACHE_TTL=3600
CACHE_SIZE=1000
```

### Ajouter des extracteurs spécialisés

Créez un nouveau fichier dans `extractors/` :

```python
from extractors.base import BaseExtractor, ExtractResult, VideoLink

class MonExtracteur(BaseExtractor):
    def can_handle(self, domain: str) -> bool:
        return "monsite.com" in domain
    
    async def extract(self, url: str, query: str, lang: str) -> ExtractResult:
        # Votre logique d'extraction
        pass
```

Puis ajoutez-le dans `orchestrator.py` :

```python
from extractors.monextracteur import MonExtracteur

self.extractors['monextracteur'] = MonExtracteur()
```

## 🎯 Flux de Traitement

1. **Réception** : Le bot reçoit `/find <url> "titre"`
2. **Cache** : Vérifie si le résultat est en cache
3. **Routing** : Sélectionne l'extracteur approprié
4. **Extraction** :
   - Essai avec extracteur spécialisé (si disponible)
   - Sinon essai avec yt-dlp
   - En dernier recours, utilise Playwright
5. **Résultat** : Retourne les liens directs trouvés

## 🛠️ Dépannage

### Erreur "No module named 'pyrogram'"
```bash
pip install pyrogram tgcrypto
```

### Erreur Playwright
```bash
python -m playwright install chromium
python -m playwright install-deps  # Linux seulement
```

### Le bot ne trouve pas de liens
- Vérifiez que l'URL est correcte
- Certains sites nécessitent une connexion
- Les sites avec CAPTCHA peuvent bloquer l'extraction

### Rate limit atteint
- Attendez 60 secondes
- Augmentez les limites dans config.py si nécessaire

## 📊 Performances

- **Cache** : Réponses instantanées pour recherches répétées
- **Concurrence** : Gère plusieurs requêtes simultanément
- **Timeout** : 30s pour yt-dlp, 45s pour Playwright
- **Mémoire** : ~100MB en utilisation normale

## 🔒 Sécurité

- Rate limiting par utilisateur et global
- Validation des URLs entrantes
- Timeout sur toutes les opérations
- Logs détaillés pour audit

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créez votre branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 TODO

- [ ] Support pour plus d'extracteurs spécialisés
- [ ] Interface web d'administration
- [ ] Support multi-langues
- [ ] Téléchargement optionnel
- [ ] Conversion de formats
- [ ] API REST

## ⚠️ Avertissement

Ce bot est fourni à des fins éducatives uniquement. Respectez toujours :
- Les conditions d'utilisation des sites
- Les droits d'auteur
- Les lois locales sur le contenu numérique

## 📜 License

MIT License - voir LICENSE pour plus de détails

## 💡 Support

Pour toute question ou problème :
- Ouvrez une issue sur GitHub
- Contactez via Telegram : @yourusername

---

**Fait avec ❤️ pour la communauté**
