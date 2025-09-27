@echo off
REM Script d'installation pour Python 3.13 (Windows)

echo 🎬 Installation du Video Link Extractor Bot (Python 3.13)
echo ========================================================

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé. Veuillez l'installer d'abord.
    pause
    exit /b 1
)

echo ✅ Python détecté

REM Créer l'environnement virtuel
echo 📦 Création de l'environnement virtuel...
python -m venv venv

REM Activer l'environnement virtuel
echo 🔧 Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Installer pip et wheel
echo 🔧 Mise à jour de pip...
python -m pip install --upgrade pip setuptools wheel

REM Installer les dépendances de base d'abord
echo 📚 Installation des dépendances de base...
pip install requests aiohttp httpx beautifulsoup4 python-dotenv

REM Installer pyrogram et tgcrypto
echo 📚 Installation de Pyrogram...
pip install pyrogram tgcrypto

REM Installer yt-dlp
echo 📚 Installation de yt-dlp...
pip install yt-dlp

REM Essayer d'installer Playwright (peut échouer sur Python 3.13)
echo 🌐 Tentative d'installation de Playwright...
pip install playwright || echo ⚠️ Playwright installation échouée - sera installé plus tard

REM Installer Chromium pour Playwright si possible
echo 🌐 Installation de Chromium...
python -m playwright install chromium || echo ⚠️ Chromium installation échouée

REM Créer le fichier .env
echo ⚙️ Configuration...
if not exist .env (
    copy env.example .env
    echo 📝 Fichier .env créé. Veuillez le modifier avec vos tokens Telegram.
) else (
    echo ⚠️ Fichier .env existe déjà.
)

echo.
echo 🎉 Installation terminée !
echo.
echo ⚠️ Note importante pour Python 3.13 :
echo    - Certains packages peuvent ne pas être compatibles
echo    - Playwright peut nécessiter une installation manuelle
echo    - Consultez le README pour les alternatives
echo.
echo 📋 Prochaines étapes :
echo 1. Éditez le fichier .env avec vos tokens Telegram
echo 2. Testez le bot avec : python main.py
echo.
pause
