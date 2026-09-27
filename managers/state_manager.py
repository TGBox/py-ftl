from typing import TYPE_CHECKING
import logging
from classes.GameData import GameData
from settings import (
    STATE_COMBAT,
    STATE_GAME_OVER,
    STATE_MAIN_MENU,
    STATE_MAP,
    STATE_SHOP,
    STATE_VICTORY,
)
from enums import GameState

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game import Game


class StateManager:
    """Manages all game state transitions and state lifecycle hooks."""

    def __init__(self, data: GameData):
        self.data = data
        self.game: "Game | None" = None
        self.previous_game_state: str | None = None

    @property
    def current(self) -> str:
        return self.data.current_state

    def change_state(self, new_state: str | GameState) -> None:
        state_str = new_state.value if isinstance(new_state, GameState) else str(new_state)
        old_state = self.current

        from managers.logger_manager import log_debug
        log_debug("STATE", f"Zustand wechselt von {old_state} zu {state_str}")

        overlay_states = (GameState.OPTIONS.value, GameState.ACHIEVEMENTS.value)
        is_returning_from_overlay = (old_state in overlay_states) and (state_str not in overlay_states)

        if state_str in overlay_states:
            if old_state not in overlay_states:
                self.previous_game_state = old_state
        else:
            self.on_leave(old_state)

        self.data.current_state = state_str

        if state_str in (GameState.MAIN_MENU.value, GameState.MAP.value, GameState.GAME_OVER.value, GameState.VICTORY.value):
            self.data.show_slot_modal = False
            self.data.show_help_overlay = False
            if hasattr(self.data.player, "show_crew_menu"):
                self.data.player.show_crew_menu = False

        if not is_returning_from_overlay:
            self.on_enter(state_str)

        print(f"{old_state} -> {state_str}")

    def return_from_overlay(self) -> None:
        """Returns from overlay menu (options/achievements) to previous game state."""
        target = self.previous_game_state or GameState.MAP.value
        self.previous_game_state = None
        self.change_state(target)

    def on_leave(self, state: str) -> None:
        if state == STATE_COMBAT:
            self.leave_combat()

    def on_enter(self, state: str) -> None:
        if state == STATE_COMBAT:
            self.enter_combat_state()
        elif state == STATE_SHOP:
            self.enter_shop_state()
        elif state in (STATE_GAME_OVER, STATE_VICTORY):
            self.data.player.projectiles.clear()
            self.data.combat.weapon_targets.clear()
            self.reset_combat_systems()

    def enter_shop_state(self) -> None:
        self.data.world.event_manager.current_event_type = None
        shop_mgr = getattr(self.game, "shop_manager", None) or getattr(self.data, "shop_manager", None)
        if shop_mgr:
            if hasattr(shop_mgr, "refresh_catalog"):
                shop_mgr.refresh_catalog()
            if hasattr(shop_mgr, "generate_next_crew_candidate"):
                shop_mgr.generate_next_crew_candidate()

    def reset_combat_systems(self) -> None:
        self.data.combat.combat_drone_active = False
        self.data.combat.repair_drone_active = False
        self.data.combat.defense_drone_active = False
        self.data.combat.shield_charger_active = False
        self.data.combat.anti_personnel_active = False
        self.data.combat.cloak_active_timer = 0.0
        self.data.combat.cloak_cooldown = 0.0
        self.data.combat.teleport_cooldown = 0.0
        self.data.combat.is_teleport_targeting = False

    def enter_combat_state(self) -> None:
        self.data.combat.msg = ""
        self.data.combat.msg_timer = 0.0
        self.data.combat.combat_won = False
        self.data.combat.ftl_charge_timer = 0.0
        self.data.combat.ftl_ready = False
        self.data.paused = False
        self.data.player.projectiles.clear()
        self.data.combat.weapon_targets.clear()
        if self.game and hasattr(self.game, "particle_manager"):
            self.game.particle_manager.clear()
        if self.game and hasattr(self.game, "combat_manager"):
            self.game.combat_manager.enemy_crew_spawned = False
            self.game.combat_manager.enemy_crew.clear()
        self.reset_combat_systems()

    def leave_combat(self) -> None:
        self.reset_combat_systems()
        if self.game and hasattr(self.game, "combat_manager"):
            self.game.combat_manager.enemy_crew.clear()

    def show_message(self, text: str) -> None:
        self.data.combat.msg = text
        self.data.combat.msg_timer = 1.5