import logging
import os
from datetime import datetime
from game import Game

if __name__ == "__main__":
    # Ordner "logs" erstellen, falls er nicht existiert
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Generiert einen Namen wie: ftl_debug_11-08-2026_20-54-56.log
    log_name = datetime.now().strftime("logs/ftl_debug_%d-%m-%Y_%H-%M-%S.log")

    # Konfiguriert das Basis-Logging für das gesamte Projekt
    logging.basicConfig(
        filename=log_name,
        level=logging.DEBUG, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filemode='w',
        encoding="utf-8"
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Initialisiere Spiel...")
    game = Game()
    game.run()