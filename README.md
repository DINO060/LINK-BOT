# Configuration et installation du bot

## Installation des dépendances
pip install playwright python-telegram-bot==21.6
playwright install

## Configuration du bot Telegram

1. Créer un bot sur Telegram:
   - Parle à @BotFather sur Telegram
   - Tape /newbot
   - Choisis un nom et un username
   - Récupère ton TOKEN

2. Configure le token:
   
   **Option A - Variable d'environnement (recommandé):**
   ```bash
   set BOT_TOKEN=ton_token_ici
   ```
   
   **Option B - Modifier le code:**
   Dans link_finder_bot.py, ligne 12:
   ```python
   BOT_TOKEN = "ton_token_ici"
   ```

## Utilisation

1. Lance le bot:
   ```bash
   python link_finder_bot.py
   ```

2. Sur Telegram, envoie au bot:
   ```
   find https://youtube.com christ
   ```

3. Le bot te renvoie les 3 meilleurs liens:
   ```
   https://youtube.com/watch?v=abc123
   https://youtube.com/watch?v=def456  
   https://youtube.com/watch?v=ghi789
   ```

## Comment ça marche

Le bot:
1. **Ouvre le site** avec Playwright (navigateur headless)
2. **Cherche automatiquement** le mot-clé (barre de recherche, navigation)
3. **Extrait tous les liens** de la page
4. **Score chaque lien** selon la similarité avec ton mot-clé
5. **Renvoie les 3 meilleurs** (même si pas exactement identiques)

## Exemples d'usage

```
find https://youtube.com christ brown
find https://netflix.com naruto
find https://exemple.com film 2024
```

Le bot tolère les variations:
- Tu cherches "christ" → trouve "Christ Brown", "Christ Fast", etc.
- Matching intelligent avec score de similarité

## Fonctionnalités

✅ **Multi-sites**: Fonctionne sur (presque) tout site web public
✅ **Matching fuzzy**: Trouve des correspondances même approximatives  
✅ **Auto-détection**: Trouve automatiquement les champs de recherche
✅ **URLs absolues**: Convertit les liens relatifs en liens complets
✅ **Seuil de pertinence**: Évite les résultats trop éloignés
✅ **Limite les résultats**: Max 3 liens pour éviter le spam

## Limitations importantes

⚠️ **Respecte les CGU** des sites
⚠️ **Pas de contournement** de protections (captcha, paywall)
⚠️ **Sites avec login**: Préfère les APIs officielles
⚠️ **Rate limiting**: Le bot fait 1 recherche à la fois