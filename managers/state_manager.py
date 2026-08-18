from typing import TYPE_CHECKING
import logging
from classes.GameData import GameData
from settings import *

from enums import GameState

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game import Game
    
class StateManager:
    """
    Verwaltet alle Zustandswechsel des Spiels.
    """

    def __init__(self, data: GameData):
        self.data = data
        self.game: "Game | None" = None   # Set by Game after construction

    # --------------------------------------------------
    # Eigenschaften
    # --------------------------------------------------

    @property
    def current(self) -> str:
        return self.data.current_state

    @property
    def is_main_menu(self) -> bool:
        return self.current == GameState.MAIN_MENU.value

    @property
    def is_options(self) -> bool:
        return self.current == GameState.OPTIONS.value

    @property
    def is_achievements(self) -> bool:
        return self.current == GameState.ACHIEVEMENTS.value

    @property
    def is_map(self) -> bool:
        return self.current == GameState.MAP.value

    @property
    def is_shop(self) -> bool:
        return self.current == GameState.SHOP.value

    @property
    def is_event(self) -> bool:
        return self.current == GameState.EVENT.value

    @property
    def is_combat(self) -> bool:
        return self.current == GameState.COMBAT.value

    @property
    def is_training(self) -> bool:
        return self.current == GameState.TRAINING.value

    @property
    def is_game_over(self) -> bool:
        return self.current == GameState.GAME_OVER.value

    @property
    def is_victory(self) -> bool:
        return self.current == GameState.VICTORY.value

    # --------------------------------------------------
    # Öffentliche Methoden
    # --------------------------------------------------

    def change_state(self, new_state: str | GameState):
        state_str = new_state.value if isinstance(new_state, GameState) else str(new_state)
        
        logger.debug(f"State wechselt von {self.current} zu {state_str}")

        if self.current == state_str:
            return

        old_state = self.current

        self.on_leave(old_state)

        self.data.current_state = state_str

        # Modal-Zustände zurücksetzen, falls in Hauptzustand gewechselt wird
        if state_str in (GameState.MAIN_MENU.value, GameState.MAP.value, GameState.GAME_OVER.value, GameState.VICTORY.value):
            self.data.show_slot_modal = False
            self.data.show_help_overlay = False
            if hasattr(self.data.player, "show_crew_menu"):
                self.data.player.show_crew_menu = False

        self.on_enter(state_str)

        print(f"{old_state} -> {state_str}")

    def enter_main_menu(self):
        self.change_state(GameState.MAIN_MENU)

    def enter_options(self):
        self.change_state(GameState.OPTIONS)

    def enter_achievements(self):
        self.change_state(GameState.ACHIEVEMENTS)

    def enter_map(self):
        self.change_state(GameState.MAP)

    def enter_shop(self):
        self.change_state(GameState.SHOP)

    def enter_event(self):
        self.change_state(GameState.EVENT)

    def enter_combat(self):
        self.change_state(GameState.COMBAT)

    def enter_training(self):
        self.change_state(GameState.TRAINING)

    def enter_game_over(self):
        self.change_state(GameState.GAME_OVER)

    def enter_victory(self):
        self.change_state(GameState.VICTORY)

    # --------------------------------------------------
    # Hooks
    # --------------------------------------------------

    def on_leave(self, state: str):

        if state == STATE_COMBAT:
            self.leave_combat()

        elif state == STATE_EVENT:
            self.leave_event()

        elif state == STATE_SHOP:
            self.leave_shop()

    def on_enter(self, state: str):

        if state == STATE_MAP:
            self.enter_map_state()

        elif state == STATE_COMBAT:
            self.enter_combat_state()

        elif state == STATE_EVENT:
            self.enter_event_state()

        elif state == STATE_SHOP:
            self.enter_shop_state()

        elif state == STATE_GAME_OVER:
            self.enter_game_over_state()

        elif state == STATE_VICTORY:
            self.enter_victory_state()

    # --------------------------------------------------
    # Enter-Methoden
    # --------------------------------------------------

    def enter_map_state(self):
        """
        Wird jedes Mal aufgerufen,
        wenn die Sternenkarte betreten wird.
        """
        pass

    def enter_shop_state(self):
        """
        Initialisierung des Shops.
        """
        self.data.world.event_manager.current_event_type = None

    def enter_event_state(self):
        """
        Initialisierung eines Zufallsevents.
        """
        pass

    def reset_combat_systems(self):
        """Reset active drones, cloaking timers, and cooldowns between battles (TODO 41)."""
        self.data.combat.combat_drone_active = False
        self.data.combat.repair_drone_active = False
        self.data.combat.defense_drone_active = False
        self.data.combat.shield_charger_active = False
        self.data.combat.anti_personnel_active = False
        self.data.combat.cloak_active_timer = 0.0
        self.data.combat.cloak_cooldown = 0.0
        self.data.combat.teleport_cooldown = 0.0
        self.data.combat.is_teleport_targeting = False

    def enter_combat_state(self):
        """
        Initialisierung eines Kampfes.
        """
        self.data.combat.msg = ""
        self.data.combat.msg_timer = 0.0
        self.data.combat.combat_won = False
        self.data.combat.ftl_charge_timer = 0.0
        self.data.combat.ftl_ready = False
        self.data.paused = False
        self.reset_combat_systems()

    def enter_game_over_state(self):
        """
        Spiel verloren.
        """
        self.data.player.projectiles.clear()
        self.data.combat.weapon_targets.clear()
        self.reset_combat_systems()

    def enter_victory_state(self):
        """
        Spiel gewonnen.
        """
        self.data.player.projectiles.clear()
        self.data.combat.weapon_targets.clear()
        self.reset_combat_systems()

    # --------------------------------------------------
    # Leave-Methoden
    # --------------------------------------------------

    def leave_combat(self):
        self.reset_combat_systems()

    def leave_event(self):
        pass

    def leave_shop(self):
        pass
    
    
    # --------------------------------------------------
    # HILFSMETHODEN
    # --------------------------------------------------

    def show_message(self, text: str):

        self.data.combat.msg = text

        self.data.combat.msg_timer = 1.5