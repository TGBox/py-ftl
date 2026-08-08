from classes.GameData import GameData
from settings import *


class StateManager:
    """
    Verwaltet alle Zustandswechsel des Spiels.
    """

    def __init__(self, data: GameData):
        self.data = data

    # --------------------------------------------------
    # Eigenschaften
    # --------------------------------------------------

    @property
    def current(self) -> str:
        return self.data.current_state

    @property
    def is_map(self):
        return self.current == STATE_MAP

    @property
    def is_shop(self):
        return self.current == STATE_SHOP

    @property
    def is_event(self):
        return self.current == STATE_EVENT

    @property
    def is_combat(self):
        return self.current == STATE_COMBAT

    @property
    def is_game_over(self):
        return self.current == STATE_GAME_OVER

    @property
    def is_victory(self):
        return self.current == STATE_VICTORY

    # --------------------------------------------------
    # Öffentliche Methoden
    # --------------------------------------------------

    def change_state(self, new_state: str):

        if self.current == new_state:
            return

        old_state = self.current

        self.on_leave(old_state)

        self.data.current_state = new_state

        self.on_enter(new_state)

        print(f"{old_state} -> {new_state}")

    def enter_map(self):
        self.change_state(STATE_MAP)

    def enter_shop(self):
        self.change_state(STATE_SHOP)

    def enter_event(self):
        self.change_state(STATE_EVENT)

    def enter_combat(self):
        self.change_state(STATE_COMBAT)

    def enter_game_over(self):
        self.change_state(STATE_GAME_OVER)

    def enter_victory(self):
        self.change_state(STATE_VICTORY)

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

    def enter_game_over_state(self):
        """
        Spiel verloren.
        """
        self.data.player.projectiles.clear()
        self.data.combat.weapon_targets.clear()

    def enter_victory_state(self):
        """
        Spiel gewonnen.
        """
        self.data.player.projectiles.clear()
        self.data.combat.weapon_targets.clear()

    # --------------------------------------------------
    # Leave-Methoden
    # --------------------------------------------------

    def leave_combat(self):
        pass

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