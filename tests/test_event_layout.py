import unittest
import pygame
from utils import wrap_text, calculate_event_layout

class TestEventLayout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.font = pygame.font.SysFont(None, 24)

    def test_wrap_short_text(self):
        text = "Kürzere Nachricht."
        lines = wrap_text(text, self.font, 600)
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], text)

    def test_wrap_long_text(self):
        text = (
            "Ein ziviles Frachtschiff sendet einen dringenden Notruf! "
            "Es wird von einem bewaffneten Piratenjäger bedrängt. "
            "Die Crew ist verzweifelt und bittet dich um sofortige Unterstützung gegen die Angreifer!"
        )
        lines = wrap_text(text, self.font, 600)
        self.assertGreater(len(lines), 1, "Long text should wrap into multiple lines.")
        for line in lines:
            self.assertLessEqual(self.font.size(line)[0], 600, "Wrapped line should not exceed max width.")

    def test_calculate_event_layout_dynamic_box(self):
        long_ev = (
            "Sehr langer Event Text " * 15
        )
        choices: list[dict[str, str | int | bool]] = [
            {"text": "Option 1", "action": "ACTION_1"},
            {"text": "Option 2", "action": "ACTION_2"},
            {"text": "Option 3", "action": "ACTION_3"},
            {"text": "Option 4", "action": "ACTION_4"},
        ]
        layout = calculate_event_layout(long_ev, "", choices, self.font)
        self.assertGreater(len(layout["ev_lines"]), 3)
        self.assertEqual(len(layout["choice_rects"]), 4)
        
        # Verify choice buttons start below the wrapped event text
        ev_text_bottom = 125 + len(layout["ev_lines"]) * 24
        first_choice_y = layout["choice_rects"][0].y
        self.assertGreaterEqual(first_choice_y, ev_text_bottom + 15)

if __name__ == "__main__":
    unittest.main()
