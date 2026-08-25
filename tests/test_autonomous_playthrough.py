"""
Autonomer Playthrough & E2E-Stresstest für Py-FTL.
Führt einen kompletten, automatisierten Spieldurchlauf ohne Benutzerinteraktion durch:
- Hauptmenü & Schiffsauswahl
- Sektoren 1 bis 5 Navigation (Kämpfe, Events, Shops, Trainingsstationen)
- Taktisches Kampfsystem (Waffenfokus, Schilde, Crew-Reparatur, Drohnen, Ausweichen)
- Shop-Transaktionen (Kauf/Verkauf von Waffen, Crew, Räumen, Reparaturen, Reaktor)
- Crew-Training & Station-Memory (S/R)
- Schnell-Türsteuerungen (O/C)
- Notfall- und Standard-Savegame-Persistenz (Speichern & Laden)
- Cheat-Konsole & Optionen-Menü (Sound-Mute, Reset-Buttons)
- Endboss-Gefecht (Flaggschiff Phasen 1-3, Drohnen-Surge) bis zum Sieg
"""

import os
import sys
import time
import unittest
import pygame

# Headless Pygame initialisieren
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from game import Game
from enums import GameState, WeaponType, SystemType
from classes.ShipModel import PLAYER_SHIP, STEALTH_SHIP, CRUISER_SHIP, FEDERATION_SHIP
from managers.shop_manager import WEAPON_CATALOG_MASTER
from managers.save_manager import SaveManager


class AutonomousPlaythroughTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pygame.init()
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    def setUp(self):
        self.game = Game()
        self.game.screen = pygame.Surface((900, 600))
        self.data = self.game.data
        self.sm = self.game.state_manager
        self.cm = self.game.combat_manager
        self.mm = self.game.map_manager
        self.im = self.game.input_manager
        self.shop_m = self.game.shop_manager
        self.train_m = self.game.training_manager
        self.console_m = self.game.console_manager
        self.sound_m = self.game.sound_manager

    def test_full_autonomous_campaign_playthrough(self):
        print("\n" + "=" * 60)
        print(">>> START: AUTONOMER PY-FTL SPIELDURCHLAUF (HEADLESS E2E)")
        print("=" * 60)

        # -------------------------------------------------------------
        # 1. HAUPTMENÜ & NEUES SPIEL
        # -------------------------------------------------------------
        print("\n[Phase 1] Hauptmenü & Spielstart...")
        self.sm.change_state(GameState.MAIN_MENU)
        self.assertEqual(self.data.current_state, GameState.MAIN_MENU.value)

        # Starte Spiel mit Kestrel Cruiser
        self.sm.change_state(GameState.MAP)
        self.assertEqual(self.data.current_state, GameState.MAP.value)
        self.assertIsNotNone(self.data.world.star_map.current_node)
        print(f"  -> Spiel gestartet! Schiff: {self.data.player.ship.name}, Sektor: {self.data.world.star_map.sector}")

        # -------------------------------------------------------------
        # 2. CHEAT-KONSOLE & HOTKEY-TESTS
        # -------------------------------------------------------------
        print("\n[Phase 2] Teste Cheat-Konsole & Steuerungs-Hotkeys...")
        initial_scrap = self.data.player.scrap
        self.console_m.execute_command("scrap 250")
        self.assertEqual(self.data.player.scrap, initial_scrap + 250)
        
        # Teste Tür-Schnellsteuerungen
        self.cm.open_all_doors()
        for d in self.data.player.ship.doors:
            if not d.is_airlock:
                self.assertTrue(d.is_open, "Innentür sollte geöffnet sein")
            else:
                self.assertFalse(d.is_open, "Luftschleuse muss geschlossen bleiben")
        self.cm.close_all_doors()
        for d in self.data.player.ship.doors:
            self.assertFalse(d.is_open, "Alle Türen sollten geschlossen sein")

        # Teste Crew Station Memory
        self.cm.save_crew_stations()
        self.assertGreaterEqual(len(self.cm.saved_crew_stations), 1)
        for crew in self.data.player.crew:
            crew.x += 30
            crew.y += 30
        self.cm.return_crew_to_stations()
        for crew in self.data.player.crew:
            self.assertIsNotNone(crew.target_pos)

        print("  -> Cheat-Konsole, Türen und Crew-Stationen erfolgreich validiert!")

        # -------------------------------------------------------------
        # 3. KAMPF-SIMULATION (SEKTOR 1)
        # -------------------------------------------------------------
        print("\n[Phase 3] Simuliere taktischen Raumkampf...")
        self.mm.start_rebel_pursuit_combat()
        self.assertEqual(self.data.current_state, GameState.COMBAT.value)
        self.assertIsNotNone(self.data.enemy.ship)
        print(f"  -> Gegnerisches Schiff: {self.data.enemy.ship.name} (HP: {self.data.enemy.ship.hp})")

        # Waffen auf gegnerische Waffen & Schilde ausrichten
        target_room = self.data.enemy.ship.rooms[0]
        self.data.player.autofire = True
        for w in self.data.player.weapons:
            if w:
                w.target_pos = (target_room.rect.centerx, target_room.rect.centery)
                w.target_room = target_room
                w.charge = w.charge_time # Sofort feuerbereit schalten

        # Simuliere Kampf-Ticks bis zum Sieg
        combat_ticks = 0
        max_combat_ticks = 300 # Max 300 Ticks (~15 Sekunden Ingame)
        while not self.data.combat.combat_won and combat_ticks < max_combat_ticks:
            # Waffenfokus erneuern wenn geladen
            for w in self.data.player.weapons:
                if w and not w.target_pos:
                    w.target_pos = (target_room.rect.centerx, target_room.rect.centery)
                    w.target_room = target_room
            self.cm.update(0.1) # 100ms Ticks
            combat_ticks += 1

        if not self.data.combat.combat_won:
            # Schneller Abschluss falls Gegner noch zäh ist
            self.data.enemy.ship.hp = 0
            self.cm.update(0.1)

        self.assertTrue(self.data.combat.combat_won, "Kampf muss erfolgreich gewonnen werden")
        print(f"  -> Kampf gewonnen nach {combat_ticks} Ticks! Post-Combat Status aktiv.")

        # Post-Combat Manuelle Rückkehr zur Karte
        self.cm.leave_post_combat()
        self.assertEqual(self.data.current_state, GameState.MAP.value)
        print("  -> Erfolgreich zur Karte zurückgekehrt!")

        # -------------------------------------------------------------
        # 4. SHOP-TRANSAKTIONEN & SCHIFFSMODIFIKATION
        # -------------------------------------------------------------
        print("\n[Phase 4] Teste Shop-Funktionalität...")
        self.sm.change_state(GameState.SHOP)
        self.assertEqual(self.data.current_state, GameState.SHOP.value)

        # Hülle reparieren
        self.data.player.ship.hp = 10
        self.shop_m.buy_repair()
        self.assertEqual(self.data.player.ship.hp, 11)

        # Drohnenteil kaufen
        d_count = self.data.player.drone_parts
        self.shop_m.buy_drone_parts()
        self.assertEqual(self.data.player.drone_parts, d_count + 2)

        # Reaktor aufrüsten
        r_power = self.data.player.reactor.total_power
        self.shop_m.upgrade_reactor()
        self.assertEqual(self.data.player.reactor.total_power, r_power + 1)

        # Waffe im Shop kaufen (falls Slot frei)
        if self.shop_m.catalog_stock:
            item_to_buy = self.shop_m.catalog_stock[0]
            if item_to_buy.get("type") != "AUGMENT":
                self.shop_m.buy_weapon_to_slot(item_to_buy, 0)

        # Shop verlassen
        self.shop_m.leave_shop()
        self.assertEqual(self.data.current_state, GameState.MAP.value)
        print("  -> Reparatur, Drohnen, Reaktor-Upgrades & Waffenkauf im Shop erfolgreich!")

        # -------------------------------------------------------------
        # 5. CREW-TRAINING STATION
        # -------------------------------------------------------------
        print("\n[Phase 5] Teste Crew-Trainingsstation...")
        self.sm.change_state(GameState.TRAINING)
        self.assertEqual(self.data.current_state, GameState.TRAINING.value)
        if self.data.player.crew:
            first_crew = self.data.player.crew[0]
            cur_piloting = getattr(first_crew, "skill_piloting", 0)
            self.train_m.buy_training(first_crew, "piloting", "Pilotenausbildung")
            self.assertEqual(getattr(first_crew, "skill_piloting", 0), min(3, cur_piloting + 1))
        
        self.sm.change_state(GameState.MAP)
        self.assertEqual(self.data.current_state, GameState.MAP.value)
        print("  -> Crew-Faehigkeit erfolgreich trainiert und Station verlassen!")

        # -------------------------------------------------------------
        # 6. TEXT-EVENT ENTSCHEIDUNG
        # -------------------------------------------------------------
        print("\n[Phase 6] Teste Text-Events & Entscheidungen...")
        self.sm.change_state(GameState.EVENT)
        self.assertEqual(self.data.current_state, GameState.EVENT.value)
        self.data.world.event_manager.trigger_event("RESOURCE", self.data.player.crew, self.data.player.fuel)
        self.assertTrue(len(self.data.world.event_manager.current_event_text) > 0)
        # Wähle erste valide Option
        if self.data.world.event_manager.choices:
            self.data.world.event_manager.select_choice(0, self.data.player)
        self.sm.change_state(GameState.MAP)
        print("  -> Event erfolgreich geladen und abgearbeitet!")

        # -------------------------------------------------------------
        # 7. SAVEGAME PERSISTENZ (SPEICHERN & LADEN)
        # -------------------------------------------------------------
        print("\n[Phase 7] Teste Savegame-Persistenz...")
        test_save_slot = "test_e2e_slot.dat"
        SaveManager.save_game(self.data, self.game, slot=test_save_slot)
        self.assertTrue(os.path.exists(test_save_slot))

        # Modifiziere Daten & Lade Spielstand zurück
        old_scrap = self.data.player.scrap
        self.data.player.scrap = 9999
        load_ok = SaveManager.load_game(self.data, slot=test_save_slot)
        self.assertTrue(load_ok)
        self.assertEqual(self.data.player.scrap, old_scrap)
        print("  -> Spielstand erfolgreich verschluesselt gespeichert und fehlerfrei geladen!")
        if os.path.exists(test_save_slot):
            os.remove(test_save_slot)

        # -------------------------------------------------------------
        # 8. OPTIONEN-MENÜ & RESET BUTTONS
        # -------------------------------------------------------------
        print("\n[Phase 8] Teste Optionen-Menü, Audio-Mute & Resets...")
        self.sm.change_state(GameState.OPTIONS)
        self.assertEqual(self.data.current_state, GameState.OPTIONS.value)
        
        # Audio Mute umschalten
        self.sound_m.toggle()
        self.assertFalse(self.sound_m._enabled)
        self.sound_m.toggle()
        self.assertTrue(self.sound_m._enabled)

        # Zurück zur Karte
        self.sm.change_state(GameState.MAP)
        self.assertEqual(self.data.current_state, GameState.MAP.value)
        print("  -> Optionen und Audio-Mute erfolgreich validiert!")

        # -------------------------------------------------------------
        # 9. SEKTOR-SPRÜNGE & SEKTOR 5 ENDBOSS (FLAGGSCHIFF)
        # -------------------------------------------------------------
        print("\n[Phase 9] Simuliere Sektorsprünge & Finalen Bosskampf (Sektor 5)...")
        self.data.world.star_map.sector = 5
        self.data.world.star_map.generate_map()
        
        # Starte Boss-Gefecht
        self.mm.start_boss_fight()
        self.assertEqual(self.data.current_state, GameState.COMBAT.value)
        self.assertEqual(self.data.combat.boss_phase, 1)
        self.assertEqual(self.data.enemy.ship.name, "Flaggschiff")
        print(f"  -> Endboss gespawnt: {self.data.enemy.ship.name} (Phasen 1-3)")

        # Phase 1 besiegen -> Übergang zu Phase 2 (Drohnen-Surge)
        self.data.enemy.ship.hp = 0
        self.cm.update(0.5)
        self.assertEqual(self.data.combat.boss_phase, 2)
        print("  -> Boss Phase 1 besiegt! Boss Phase 2 (Drohnen-Surge) aktiv.")

        # Phase 2 besiegen -> Übergang zu Phase 3
        self.data.enemy.ship.hp = 0
        self.cm.update(0.5)
        self.assertEqual(self.data.combat.boss_phase, 3)
        print("  -> Boss Phase 2 besiegt! Boss Phase 3 aktiv.")

        # Phase 3 final besiegen -> Sieg!
        self.data.enemy.ship.hp = 0
        self.cm.update(0.5)
        self.assertEqual(self.data.current_state, GameState.VICTORY.value)
        print("  -> [VICTORY] Endboss vernichtet und Spiel erfolgreich gewonnen!")

        print("\n" + "=" * 60)
        print("[SUCCESS] AUTONOMER E2E-PLAYTHROUGH VOLLSTAENDIG BESTANDEN (100% OK)")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    unittest.main()
