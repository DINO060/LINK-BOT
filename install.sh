#!/bin/bash

# Script d'installation pour Video Link Extractor Bot

echo "🎬 Installation du Video Link Extractor Bot"
echo "=========================================="

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

echo "✅ Python 3 détecté"

# Créer l'environnement virtuel
echo "📦 Création de l'environnement virtuel..."
python3 -m venv venv

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances
echo "📚 Installation des dépendances Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Installer Playwright et Chromium
echo "🌐 Installation de Playwright et Chromium..."
python -m playwright install chromium

# Sur Linux, installer les dépendances système
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Installation des dépendances système pour Linux..."
    python -m playwright install-deps
fi

# Créer le fichier .env
echo "⚙️ Configuration..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "📝 Fichier .env créé. Veuillez le modifier avec vos tokens Telegram."
else
    echo "⚠️ Fichier .env existe déjà."
fi

echo ""
echo "🎉 Installation terminée !"
echo ""
echo "📋 Prochaines étapes :"
echo "1. Éditez le fichier .env avec vos tokens Telegram"
echo "2. Lancez le bot avec : python main.py"
echo ""
echo "💡 Pour obtenir vos tokens Telegram :"
echo "   - Créez un bot via @BotFather"
echo "   - Obtenez vos API credentials sur my.telegram.org"
echo ""
echo "📖 Consultez le README.md pour plus d'informations."
