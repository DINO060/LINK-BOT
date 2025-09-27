#!/bin/bash

# Script de lancement pour Video Link Extractor Bot

echo "🎬 Lancement du Video Link Extractor Bot"
echo "========================================"

# Activer l'environnement virtuel
source venv/bin/activate

# Vérifier si le fichier .env existe
if [ ! -f .env ]; then
    echo "❌ Fichier .env non trouvé !"
    echo "📝 Copiez env.example vers .env et configurez vos tokens."
    exit 1
fi

# Lancer le bot
echo "🚀 Démarrage du bot..."
python main.py
