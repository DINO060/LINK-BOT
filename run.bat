@echo off
REM Script de lancement pour Video Link Extractor Bot (Windows)

echo 🎬 Lancement du Video Link Extractor Bot
echo ========================================

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat

REM Vérifier si le fichier .env existe
if not exist .env (
    echo ❌ Fichier .env non trouvé !
    echo 📝 Copiez env.example vers .env et configurez vos tokens.
    pause
    exit /b 1
)

REM Lancer le bot
echo 🚀 Démarrage du bot...
python main.py
