# FTL-Clone Audio Replacement Documentation & Asset Guide

Dies ist die vollständige Übersicht aller im Spiel enthaltenen prozedural generierten 8-Bit-Sounds, ihrer Klangcharakteristika, Lautstärkeanpassungen und der empfohlenen Dateinamen für echte WAF/OGG Audio-Assets im Verzeichnis `assets/sounds/` und `assets/music/`.

---

## 1. Musik-Track Übersicht (Sektoren-BGM)

Das Spiel unterstützt nun dynamische Musik basierend auf dem aktuellen Sektortyp. Standardmäßig werden hochwertige prozedurale Synth/Orchester-Loops generiert. Falls Custom-Dateien in `assets/music/` existieren, werden diese automatisch vorgezogen.

| Track Name | Sektortyp / Kontext | Beschreibung / Empfohlener Genre-Stil | Dateipfad-Optionen |
| :--- | :--- | :--- | :--- |
| `bgm_menu` | Hauptmenü & Optionen | Ruhiger, atmosphärischer Sci-Fi Synth-Pad Theme | `assets/music/bgm_menu.ogg` (.wav/.mp3) |
| `bgm_civilian` | Zivil-Sektor (Erkundung) | Entspannter, warmer Ambient-Synth mit leichten Arpeggios | `assets/music/bgm_civilian.ogg` |
| `bgm_pirate` | Piraten- / Rebellen-Sektor | Bedrohlicher, treibender Synth-Rhythmus | `assets/music/bgm_pirate.ogg` |
| `bgm_nebula` | Nebel-Sektor | Mystischer, dunkler Ambient-Pad mit tiefem Puls | `assets/music/bgm_nebula.ogg` |
| `bgm_explore` | Allgemeiner Sektor | Neutrales Weltraum-Erkundungsthema | `assets/music/bgm_explore.ogg` |
| `bgm_combat` | Standard Gefecht | Schneller, dynamischer Sci-Fi Combat-Track | `assets/music/bgm_combat.ogg` |
| `bgm_boss` | Miniboss & Endboss | Epischer Bosskampf-Track mit schwerer Percussion | `assets/music/bgm_boss.ogg` |

---

## 2. Soundeffekte (SFX) & 8-Bit Ersetzungsliste

Alle SFX-Lautstärken wurden global auf ein angenehmes Master-Niveau abgesenkt. Wenn echte Sounddateien unter `assets/sounds/<name>.<ext>` abgelegt werden, werden die prozeduralen Generatoren überschrieben.

| SFX Name | Auslöser / Verwendung | Sound-Eigenschaften (Synthese) | Empfohlenes Asset & Beschreibung |
| :--- | :--- | :--- | :--- |
| `laser_fire` | Laserwaffen-Schuss | Sägezahn-Sweep (800Hz -> 150Hz, 120ms) | `assets/sounds/laser_fire.wav` (Knackiger Sci-Fi Blaster) |
| `missile_launch` | Raketenstart | Rausch-Sweep (Weißes Rauschen + 100Hz Sub) | `assets/sounds/missile_launch.wav` (Schwerer Triebwerks-Zisch) |
| `beam_fire` | Strahlfeuer | Kontinuierlicher Sinus-Phaser (440Hz + Mod) | `assets/sounds/beam_fire.wav` (Tiefes Energiestrahl-Brummen) |
| `explosion` | Einschlag / Zerstörung | Rauschen + Sinus-Drop (120Hz -> 30Hz, 600ms) | `assets/sounds/explosion.wav` (Wuchtige Explosion) |
| `shield_hit` | Schild treffer | Gedämpfter Sinus-Plopp (300Hz, 80ms) | `assets/sounds/shield_hit.wav` (Elektrischer Deflektor-Schlag) |
| `alarm` | Schiffsschaden / Warnung | 2-Ton Puls (880Hz / 660Hz) | `assets/sounds/alarm.wav` (Klassische Sci-Fi Gefahrensirene) |
| `jump` | FTL-Sprung | Hochfrequenz Sweep (200Hz -> 1800Hz) | `assets/sounds/jump.wav` (Hyperraum-Verzerrungsgeräusch) |
| `click` | UI Button-Klick | Kurzer Klick-Tick (1200Hz, 15ms) | `assets/sounds/click.wav` (Dezenter Glas/Haptik-Klick) |
| `buy` | Shop-Kauf | 2-Ton Akkord (C5 + G5, 150ms) | `assets/sounds/buy.wav` (Münz- / Kredit-Chime) |
