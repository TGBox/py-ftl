# Py-FTL — Faster Than Light Clone (Pygame-CE)

Ein in Python und **Pygame-CE** umgesetzter 2D Space-Roguelike-Simulator inspiriert von *Faster Than Light (FTL)*. Steuere dein Raumschiff, verwalte Energie und Crew, rüste Waffen an physischen Hardpoints auf und bewältige geskriptete Zufallsbegegnungen auf dem Weg durch 5 gefährliche Sektoren zum Sieg über das rebellische Flaggschiff!

---

## 🌟 Hauptfeatures

### 🚀 Schiffssysteme & Druckausgleich
- **Reaktor & Energieverteilung**: Weise Reaktorleistung dynamisch Schild-, Waffen-, Antriebs- und Medbay-Räumen zu.
- **Türen & Druckausgleich**:
  - Öffne äußere **Luftschleusen** (Airlocks), um Sauerstoff ins Vakuum des Weltalls abzusaugen.
  - Geöffnete Innentüren sorgen für einen realen Sauerstoff-Druckausgleich zwischen angrenzenden Räumen.
- **Crew-Management**: Befehle Crew-Mitgliedern (Menschen, Engis, Mantis) mit individuellen Spezies-Eigenschaften, Räume zu reparieren oder sich in der Medbay zu heilen.

### ⚔️ Taktische Raumkämpfe & Waffen-Fusion
- **Feste Waffenslots & Hardpoints**: Geschosse feuern direkt von den physischen Waffenslot-Koordinaten (`H1`, `H2`, `H3`...) der Schiffshülle ab.
- **Slot-Einschränkungen**: Manche Hardpoints beschränken sich auf bestimmte Waffentypen (z. B. nur `LASER`/`BEAM` oder `MISSILE`).
- **Waffen-Fusion (Stufen MK I bis MK V)**: Fusioniere identische Waffentypen im Shop auf bis zu Stufe 5 für erhöhten Schaden (+25%) und verkürzte Ladezeiten (-15%).
- **Autofire & Visuelle Zielschusslinien**: Farblich unterschiedliche Zielschusslinien und Abzeichen (`W1`, `W2`...) für maximale Übersicht.

### 🗺️ Sternenkarte & Skriptbare Random Events
- **5 Sektoren & Mini-Boss-Kämpfe**: Zufallsgenerierte Sternenkarte mit besuchten Knoten-Farben, Sektorfortschritt und der herannahenden Rebellenflotte.
- **Skriptbare Random Events (`data/events.json`)**:
  - Narrative Begegnungen mit 2 bis 5 Antwortmöglichkeiten.
  - Spezies-Abfragen für Blaue Spezialoptionen (Engi/Mantis).
  - Leicht erweiterbare JSON-Struktur für neue Begegnungen und Ergebnisse.

### 🔒 Spielstand & Schiffsfreischaltung
- **AES-256 Verschlüsselter Spielstand**: Sichere Speicherung (`S` / `L`) des kompletten Spielstands mit SHA-256 Integritätsprüfung.
- **Fortschrittliches Schiffs-Freischaltsystem**:
  - 5 spielbare Schiffstypen: `Kestrel` ➔ `Kreuzer` ➔ `Tarnschiff` ➔ `Zoltan-Fregatte` ➔ `Federations-Kreuzer`.
  - Bei jedem Sieg über das Flaggschiff (oder einen Sektor-Boss) wird das nächste Schiff dauerhaft in `unlocks.json` freigeschaltet.

---

## 🎮 Steuerung & Tastaturkürzel

| Taste / Aktion | Funktion |
| :--- | :--- |
| **`Leertaste`** | **Taktische Pause**: Stoppt die Zeit, das Spiel bleibt voll interaktiv (Crew befehligen, Waffen zielen, Türen schalten). |
| **`ESC`** | **Pause-Menü Modal**: Öffnet / Schließt das Hauptpause-Menü (Weiter, Speichern, Laden, Optionen, Hauptmenü). |
| **`S`** | **Schnellspeichern**: Speichert den aktuellen Spielstand verschlüsselt in `savegame.dat`. |
| **`L`** | **Schnellladen**: Lädt den gespeicherten Spielstand. |
| **Linksklick** | Zielen / Auswählen von Crew, Räumen, Türen, Shop-Items und Event-Optionen. |
| **Rechtsklick** | Reaktor-Energie aus einem Raum abziehen / Crew abwählen / Waffenziel aufheben. |

---

## 📦 Installation & Start

### Voraussetzungen
- **Python 3.10+**
- Virtual Environment (empfohlen)

### 1. Repository klonen & Umgebung einrichten
```bash
git clone https://github.com/TGBox/py-ftl.git
cd py-ftl

# Virtual Environment erstellen und aktivieren
python -m venv .venv
# Unter Windows PowerShell:
.\.venv\Scripts\activate
# Unter Linux / macOS:
source .venv/bin/activate
```

### 2. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
# Oder via uv:
uv pip install -r requirements.txt
```

### 3. Spiel starten
```bash
python main.py
```

---

## 🏗️ Projektstruktur

```text
py-ftl/
├── main.py                # Haupteinstiegspunkt & Asyncio Loop
├── game.py                # Haupt-Spielloop & Manager-Initialisierung
├── settings.py            # Globale Konstanten, Farben & Auflösungen
├── data/
│   └── events.json        # Skriptbares JSON-Format für Zufallsbegegnungen
├── unlocks.json           # Dauerhafte Schiffs-Freischaltungen
├── classes/
│   ├── Crew.py            # Crew-Mitglieder & Erstickungs-/Heillogik
│   ├── DataModels.py      # Pydantic Schemas für Serialisierung
│   ├── Door.py            # Türen & Sauerstoff-Druckausgleich
│   ├── EventManager.py    # Event-Parser für events.json
│   ├── GameData.py        # Zentraler Spielzustand
│   ├── Projectile.py      # Geschosse & Flugbahn-Logik
│   ├── Reactor.py         # Reaktor & Energieverteilung
│   ├── Room.py            # Räume, Hülle & Sauerstoffzustand
│   ├── ShieldSystem.py    # Schilde & Aufladezeit
│   ├── ShipModel.py       # Schiff-Blueprints & Hardpoint-Positionen
│   ├── StarMap.py         # Sternenkarte & Sektor-Generierung
│   └── Weapon.py          # Waffen & Level-Fusion (MK I bis MK V)
└── managers/
    ├── combat_manager.py  # Kampfschleife & Schadensberechnung
    ├── input_manager.py   # Tastatur- & Mauseingabeverarbeitung
    ├── map_manager.py     # Karten-Navigation & Sektorsprünge
    ├── render_manager.py  # Graphisches Rendering (Pygame-CE)
    ├── save_manager.py    # AES-256 Speichern & Laden
    ├── shop_manager.py    # Händler-Katalog, Kauf & Verkauf
    ├── sound_manager.py   # Soundeffekte & Audio-Engine
    ├── state_manager.py   # Zustandsübergänge
    └── weapon_manager.py  # Zielerfassung & Waffen-Update
```

---

## 📄 Lizenz & Mitwirkende

Entwickelt als moderne Python-Umsetzung von FTL mit Pygame-CE. Freigegeben unter der MIT-Lizenz.
