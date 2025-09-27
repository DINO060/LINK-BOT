#!/usr/bin/env python3
"""
Video Link Extractor Bot
Point d'entrée principal
"""

import sys
import asyncio
import logging
from bot.telegram_bot import VideoLinkBot

def main():
    """Fonction principale"""
    try:
        bot = VideoLinkBot()
        bot.run()
    except KeyboardInterrupt:
        print("\nBot arrêté par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Erreur fatale: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
