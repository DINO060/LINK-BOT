@echo off
REM Script d'installation pour Video Link Extractor Bot (Windows)

echo 🎬 Installation du Video Link Extractor Bot
echo ==========================================

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

REM Installer les dépendances
echo 📚 Installation des dépendances Python...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Installer Playwright et Chromium
echo 🌐 Installation de Playwright et Chromium...
python -m playwright install chromium

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
echo 📋 Prochaines étapes :
echo 1. Éditez le fichier .env avec vos tokens Telegram
echo 2. Lancez le bot avec : python main.py
echo.
echo 💡 Pour obtenir vos tokens Telegram :
echo    - Créez un bot via @BotFather
echo    - Obtenez vos API credentials sur my.telegram.org
echo.
echo 📖 Consultez le README.md pour plus d'informations.
pause
