import logging
from game import Game

if __name__ == "__main__":
    # Konfiguriert das Basis-Logging für das gesamte Projekt
    logging.basicConfig(
        filename='ftl_debug.log',
        level=logging.DEBUG, # Erfasst ALLES (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filemode='w' # 'w' überschreibt das Log bei jedem Neustart. Nutze 'a' zum Anhängen.
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Initialisiere Spiel...")
    game = Game()
    game.run()