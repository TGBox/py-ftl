import os
import shutil
import unittest
from managers.logger_manager import DebugLogger, log_debug


class TestDebugLogger(unittest.TestCase):

    def setUp(self):
        self.test_dir = "tests_logs_tmp"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def tearDown(self):
        # Close any open file handle before deleting directory
        logger = DebugLogger.get_instance()
        logger.close()
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_logger_disabled_by_default(self):
        logger = DebugLogger(enabled=False, logs_dir=self.test_dir)
        logger.log("INPUT", "Test Klick")
        self.assertFalse(os.path.exists(self.test_dir))

    def test_logger_creates_file_when_enabled(self):
        logger = DebugLogger(enabled=True, logs_dir=self.test_dir)
        logger.log("COMBAT", "Schuss abgefeuert")
        self.assertTrue(os.path.exists(self.test_dir))

        files = os.listdir(self.test_dir)
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].startswith("game_log_"))
        self.assertTrue(files[0].endswith(".txt"))

        log_path = os.path.join(self.test_dir, files[0])
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("PROTOKOLL-LOG GESTARTET", content)
        self.assertIn("[COMBAT] Schuss abgefeuert", content)

    def test_toggle_logger_state(self):
        logger = DebugLogger(enabled=False, logs_dir=self.test_dir)
        logger.set_enabled(True)
        logger.log("SHOP", "Gegenstand gekauft")

        files = os.listdir(self.test_dir)
        self.assertEqual(len(files), 1)
        log_path = os.path.join(self.test_dir, files[0])
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("[SYSTEM] Protokollmodus vom Benutzer AKTIVIERT.", content)
        self.assertIn("[SHOP] Gegenstand gekauft", content)

        logger.set_enabled(False)
        logger.log("MAP", "Darf nicht geloggt werden")

        with open(log_path, "r", encoding="utf-8") as f:
            content_after = f.read()

        self.assertIn("[SYSTEM] Protokollmodus vom Benutzer DEAKTIVIERT.", content_after)
        self.assertNotIn("Darf nicht geloggt werden", content_after)


if __name__ == "__main__":
    unittest.main()
