import hashlib
import json
import os
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

from classes.DataModels import SavegameSchema
from classes.GameData import GameData

KEY_SALT = b"FTL_SECRET_SALT_2026_VERSION_1.0"
PASSPHRASE = b"PyGame_FTL_Encryption_Seed"


class SaveManager:

    @staticmethod
    def get_key() -> bytes:
        return PBKDF2(PASSPHRASE, KEY_SALT, dkLen=32, count=1000)

    @classmethod
    def save_game(cls, data: GameData, filepath: str = "savegame.dat") -> bool:
        schema = SavegameSchema(
            schema_version=1,
            current_sector=data.world.star_map.sector,
            player_scrap=data.player.scrap,
            player_fuel=data.player.fuel,
            player_missiles=data.player.missiles,
            ship_name=data.player.ship.name,
            ship_hp=data.player.ship.hp,
        )
        json_str = schema.model_dump_json()

        # SHA-256 Integrity Hash (SRS Kap. 8)
        sha256_hash = hashlib.sha256(json_str.encode("utf-8")).hexdigest()
        payload = json.dumps({"hash": sha256_hash, "data": json_str})

        # AES-256-CFB Encryption (SRS Kap. 8)
        key = cls.get_key()
        cipher = AES.new(key, AES.MODE_CFB)
        iv = cipher.iv
        ciphertext = cipher.encrypt(payload.encode("utf-8"))

        with open(filepath, "wb") as f:
            f.write(iv + ciphertext)

        print(f"Spielstand erfolgreich gespeichert in {filepath}!")
        return True

    @classmethod
    def load_game(cls, data: GameData, filepath: str = "savegame.dat") -> bool:
        if not os.path.exists(filepath):
            print(f"Kein Speicherstand unter {filepath} gefunden!")
            return False

        try:
            with open(filepath, "rb") as f:
                file_bytes = f.read()

            iv = file_bytes[:16]
            ciphertext = file_bytes[16:]
            key = cls.get_key()
            cipher = AES.new(key, AES.MODE_CFB, iv=iv)
            decrypted_text = cipher.decrypt(ciphertext).decode("utf-8")

            payload = json.loads(decrypted_text)
            stored_hash = payload.get("hash")
            json_str = payload.get("data")

            # SHA-256 Verifizierung
            actual_hash = hashlib.sha256(json_str.encode("utf-8")).hexdigest()
            if stored_hash != actual_hash:
                print("KORRUMPIERTER SPEICHERSTAND! Hash-Verifizierung fehlgeschlagen.")
                return False

            schema = SavegameSchema.model_validate_json(json_str)

            data.world.star_map.sector = schema.current_sector
            data.player.scrap = schema.player_scrap
            data.player.fuel = schema.player_fuel
            data.player.missiles = schema.player_missiles
            data.player.ship.hp = schema.ship_hp

            print(f"Spielstand erfolgreich geladen aus {filepath}!")
            return True

        except Exception as e:
            print(f"Fehler beim Laden des Spielstands: {e}")
            return False
