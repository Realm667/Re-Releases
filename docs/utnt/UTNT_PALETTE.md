# UTNT: globale PLAYPAL für Doom-Grafiken

Die ausdrücklich gewählte Variante 1 ist umgesetzt: 4.713 Grafiken mit der Doom-Palette liegen wieder als echte Doom-Patches beziehungsweise Flats vor. Sie beziehen ihre Farben aus der beim Laden wirksamen `PLAYPAL`. Ein erneuter Export der Grafiken nach einem Palettenwechsel ist damit nicht erforderlich.

## PNG-Blautoene an PLAYPAL angeglichen (11.09.2026)

514 weiterhin eigenstaendige PNGs sind an die **aktuell lokal verwendete** UTNT-PLAYPAL angeglichen: 48 RGBA-, 10 RGB- und 456 PNGs mit eingebetteter Palette. Betroffen sind insbesondere Dark-Imp-Angriffe, blaue Actor-Details, Eis-/Energieprojektile, Plasma-Waffenblitze, blaue Flammen und Funken sowie die passenden Aufnahmesymbole. 199.696 sichtbare blaue Pixel wurden korrigiert.

Klassische Doom-Blaustufen uebernehmen die RGB-Werte der entsprechenden PLAYPAL-Indizes 192–207 und 240–246. Bei eingebetteten Paletten bleibt die Indexzuordnung erhalten; dadurch werden die im Doom-Original RGB-gleichen Indizes 207 und 240 unterschieden, soweit die Palette sie noch identifiziert. Ohne erhaltenen Index verwendet RGB (0, 0, 83) den Hauptverlauf bei Index 207. Freie Verlaeufe ausgewaehlter blauer Effekt- und Actor-Serien verwenden interpolierte Palettenwerte statt einer groben Reduktion auf 16 Farben. Neutrale Rauchgrafiken, absichtlich violette Farbanteile, Normalmaps und Chromakey-Himmel werden nicht pauschal umgefaerbt.

Abmessungen, Farbmodus, Alphakanaele, transparente Pixel, Sprite-Offsets, Farbprofile und alle nichtblauen Pixel bleiben unveraendert. Bei indizierten PNGs aendert sich ausschliesslich die eingebettete PLTE; ihre Bildindizes bleiben byteidentisch. Bei RGB/RGBA aendert sich ausschliesslich der IDAT-Bildinhalt. Die bereits vorgefundenen fehlerhaften grAb-Pruefsummen einzelner Originale bleiben unveraendert; der Pruefer normalisiert sie nur fuer das Einlesen im Arbeitsspeicher.

Die PNGs speichern den abgeglichenen Farbstand weiterhin selbst. Sie reagieren **nicht automatisch** auf spaetere PLAYPAL-Aenderungen. Die lokale PLAYPAL-Datei wurde fuer diese Aufgabe weder veraendert noch mitcommittet. Die verwendeten Blauwerte und alle Original-/Ergebnishashes sind in [png-blue.json](../../tools/fixtures/png-blue.json) festgehalten.

Pruefung: [check_png_blue.py](../../tools/check_png_blue.py) vergleicht alle 514 Dateien mit ihren Original-Git-Blobs, prueft die unveraenderten Daten und optional den exakten Paketinhalt. Das gemeinsame Integrationspaket wurde mit dem regulaeren Buildwerkzeug einschliesslich Lokalisierungs-, Schrift-, ACS- und Engine-Pruefung gebaut. Vulkan und OpenGL laden alle korrigierten Ressourcen; je 530 Assertions bestanden. Ein Vorher-/Nachher-Bildvergleich von acht repraesentativen Ressourcen wurde in beiden Renderern kontrolliert. Der erste OpenGL-Lauf auf TNT01 erreichte alle Ressourcen-Assertions, aber nicht den Abschlussmarker innerhalb von 45 Sekunden; der gezielte Wiederholungslauf auf MAP01 beendete sich regulaer. Dies ist keine vollstaendige Kampagnenpruefung.

```text
python -B tools/check_png_blue.py --pk3 tutnt.pk3
python -B tools/check_png_blue.py --pk3 tutnt.pk3 --require-current-palette
```

Die zweite Variante verlangt zusaetzlich exakt den lokalen PLAYPAL-Blaustand dieses Abgleichs. Der historische `check_palette_assets.py`-Gesamttest ist davon unabhaengig: Sein alter Manifest verweist noch auf `DROPA0.lmp`, das bereits in `14944cc00` entfernt wurde. Dieser vorbestehende Manifestfehler wurde nicht mit der Farbkorrektur vermischt. Lokale Nachweise: `tutnt/.codex/work/truecolor-blue/`, `tutnt/.codex/logs/truecolor-blue-*`; Originale unter `tutnt/.codex/backups/truecolor-blue/`.

## Plasmagun: Laufzeitfarbe #3B7CD3 (12.09.2026)

Die eigentlichen Plasmagun-Kugeln verwenden X029-Sprites mit einer zusätzlichen Actor-Translation. Die alte Translation `[0.6,0.6,2.0]` übersteuerte Blau und färbte auch Schweif, Trefferrauch und Funken erneut ein. Das war unabhängig von den zuvor korrigierten PNGs und verursachte den verbliebenen violettblauen Eindruck.

`UTNTPlasmaBall`, `PBTrail`, `PlasmaSmoke` und `BlasterPuffParticle` verwenden nun denselben Helligkeitsverlauf von Schwarz nach **#3B7CD3 / RGB (59,124,211)**. Die frühere Übersteuerung entfällt. Fluglicht, alle fünf Trefferlichtstufen, der kurze Schuss-Blend und der zusätzliche Plasma-Halo verwenden ebenfalls diese Zielfarbe. Additive Überlagerung und Beleuchtung können helle Kerne weiterhin heller als den Basisfarbwert darstellen.

Der Halo bekommt seine Plasmafarbe gezielt anhand des Quell-Actors. Die bereits abgenommenen gemeinsamen Blautöne von Dark-Imp-Projektilen und QueenElectro bleiben erhalten. Grafikdateien, PLAYPAL, Geschwindigkeit, Schaden, Skalierung, Zustandsdauer und Effektanzahl werden durch diese Korrektur nicht verändert. Gegner und Marines, die denselben PlasmaBall verschießen, erhalten dieselbe Projektilfarbe.

[tools/test_plasma_color.py](../../tools/test_plasma_color.py) prüft die gemeinsamen Translationen und die tatsächlichen Halo-Farben zur Laufzeit, einschließlich unveränderter anderer blauer Projektiltypen. Er nimmt Flug, Einschlag und echtes Plasmagewehrfeuer in UZDoom auf. Lokale Vorher-/Nachher-Aufnahmen und Laufzeitberichte liegen unter `tutnt/.codex/validation/plasma-blue/`. Vulkan und OpenGL bestanden jeweils sieben Laufzeit-Assertions; Flug, Einschlag und echtes Waffenfeuer wurden visuell geprüft. Das gemeinsame Paket wurde mit ACS-, Lokalisierungs-, Schrift- und Engine-Prüfung gebaut; die drei geänderten Laufzeitdateien sind byteidentisch im PK3 enthalten.

```text
python -B tools/test_plasma_color.py --renderer 1
python -B tools/test_plasma_color.py --renderer 0
```

## Umfang der Doom-Format-Umstellung vom 07.09.2026

| Bereich | Grafiken |
| --- | ---: |
| Flats | 328 |
| HUD und Schriftgrafiken | 162 |
| Patches | 820 |
| Sprites | 2.489 |
| Texturen | 914 |
| Gesamt | 4.713 |

4.708 LMP-Dateien wurden byteidentisch aus `01557144c` wiederhergestellt. Die zugehörigen PNG-Kopien wurden entfernt. Bei 94 Bildern hatte der damalige PNG-Export unterschiedliche Indizes mit identischen Doom-RGB-Farben zusammengeführt. Die Original-LMPs stellen diese Indizes wieder her, sodass eine geänderte Palette auch diese Unterscheidungen korrekt abbildet.

Fünf Dateien mussten tatsächlich umcodiert werden: `flats/A-DAN5.lmp` enthielt selbst im Original PNG-Daten und wurde zu einem echten 64 × 64-Doom-Flat. Die vier bereits ursprünglich als PNG vorliegenden Patches `BERGE1`, `BERGE2`, `SBERG1` und `SBERG2` wurden zu Doom-Tall-Patches mit 1.024 × 512 Pixeln. Ihre sichtbaren Indizes, Transparenz und Offsets wurden durch vollständiges Decodieren der erzeugten Daten gegengeprüft. Es erfolgte keine neue Farbquantisierung.

Die fünf Bossrahmen `M_HPB1` bis `M_HPB5` verwenden wieder die Original-LMPs. Die Gesichter, Abmessungen und korrigierte Balkenposition bleiben erhalten; ihre Farben folgen nun ebenfalls `PLAYPAL`. Der Boss-HUD-Code musste dafür nicht geändert werden.

Grafiken mit eigenen Paletten, Truecolor-Grafiken, Model-Skins und Materialkarten wurden nicht pauschal umgewandelt. Neun historische SM-Texturen besaßen bereits zusätzliche Truecolor-PNGs gleichen Basisnamens. Diese vorhandenen Ersatzgrafiken bleiben bestehen; die beim letzten Export zusätzlich erzeugten ` (1).png`-Kopien wurden durch die ursprünglichen LMPs ersetzt. Vollständige PNG-Dateipfade in Spieldefinitionen wurden überprüft: keine Referenz auf eine der entfernten PNG-Dateien bleibt übrig.

Die bestehende lokale Änderung an `PLAYPAL.pal` sowie parallel bearbeitete Statusleisten-, Menü-, Sprach- und ACS-Dateien gehören nicht zu diesem Commit und wurden nicht zurückgesetzt.

## Abnahme am 07.09.2026

- Alle 4.713 Dateien: Hash, echtes Dateiformat, Abmessungen, Offsets, Post-Grenzen sowie exakte Paketdaten geprüft. Die vor der Umstellung gelesenen PNGs wurden mit den Originalbildern hinsichtlich sichtbarer Farben, Masken und Offsets verglichen; keine Abweichung blieb offen.
- Separates Paket aus `dedaaaccc` plus ausschließlich den Grafikänderungen gebaut und mit UZDoom 5.0.1 validiert. Alle 14 ACS-Module dieses isolierten Pakets sind byteidentisch.
- OpenGL und Vulkan mit Projektpalette und einer absichtlich invertierten Testpalette: 52 Ressourcen-Assertions und 26 Bildvergleiche bestanden. Alle zwölf geprüften Doom-Ressourcen reagieren auf den Palettenwechsel; das Kontroll-PNG bleibt pixelgleich. Ein OpenGL-Lauf blieb nach fertigem Screenshot und Abschlussmarker beim Beenden hängen; der gezielte Wiederholungslauf beendete sich regulär.
- Alle 13 Karten starten im isolierten Paket unter Vulkan ohne Laufzeitfehler. Dies ist eine Ladeprüfung, keine neue vollständige Kampagnenabnahme.
- Boss-HUD-Test mit LMP-Rahmen bestanden: 30 Assertions, einschließlich Save/Load, Schadensnachlauf und Todesfrist. Aufnahme bei 1.920 × 1.080 sowie die weiteren Testauflösungen geprüft.
- Das während der parallelen HUD-Arbeit aktualisierte reguläre `tutnt.pk3` wurde separat als konsistenter Snapshot geprüft: UZDoom-Kompilierung bestanden, alle 4.713 Zielgrafiken mit den korrekten Bytes enthalten.

![Doom-Ressourcen mit Projektpalette und unabhängiges Kontroll-PNG](https://raw.githubusercontent.com/Realm667/Re-Releases/e571d62969b2473133bfc00f9ba09bb622d23b17/tools/validation/palette-restore-2026-09-07/palette-candidate-project-1.png)

[Vergleich mit absichtlich invertierter PLAYPAL](https://github.com/Realm667/Re-Releases/blob/e571d62969b2473133bfc00f9ba09bb622d23b17/tools/validation/palette-restore-2026-09-07/palette-candidate-swapped-1.png)

## Reproduzieren

```text
python tools/check_palette_assets.py --pk3 tutnt.pk3
python tools/test_palette.py --mod tutnt.pk3
python tools/test_boss_hud.py --mod tutnt.pk3
```

Die Renderer-Tests benötigen `UTNT_ENGINE` und `UTNT_IWAD`; der Bildvergleich verwendet Pillow ausschließlich zum Lesen der Engine-Aufnahmen. Testpaletten und Sicherungen liegen unter dem ignorierten `logs/palette-restore`. Die Quelldatei `PLAYPAL.pal` wird vom Test nicht verändert. Die Test-Add-ons unter `tools` gelangen nicht ins Spielpaket.

Nachweise und der vollständige Dateimanifest liegen unter `tools/validation/palette-restore-2026-09-07`. `sha256.json` beschreibt die unveränderten Nachweisdateien.

Isoliertes Paket: 8779 Einträge, 82057203 Bytes, SHA-256 `be2623f0c7ed858746077e2d79bc435be853d7fddcde1e817dcf7a5e9ae9c6a7`. Geprüfter lokaler Paket-Snapshot einschließlich paralleler Änderungen: 8818 Einträge, 83585588 Bytes, SHA-256 `6dcaa6127e938b1e408c72d7337f309505c46827ba1061321ef6eb6fb7c6459b`. Diese Paketunterschiede sind beabsichtigt; der Grafikmanifest wurde gegen beide geprüft.
