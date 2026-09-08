# Waffenrueckstoss — 08.09.2026

Alle 43 kamerabezogenen Rueckstossaktionen in `tutnt/actors/weapons.txt`
verwenden jetzt 25 % ihrer bisherigen Staerke und `SPF_INTERPOLATE`.
Impulse mit zwei, drei oder fuenf Tics Dauer werden in gleichmaessige
Einzelschritte zerlegt. Das gilt auch fuer das Ladezittern der BFG.
Rueckstellung und Ausschlag bleiben ausgeglichen; Feuerrate, Sprite-Dauer,
Schaden, Munitionsverbrauch und alle anderen Waffenaktionen sind unveraendert.
Faust, Kettensaege und Flammenwerfer besitzen keine solchen Kameraspruenge.

| Waffe | Maximaler Ausschlag vorher | Jetzt | Maximaler Schritt jetzt |
| --- | ---: | ---: | ---: |
| Pistole | 0,6 Grad | 0,15 Grad | 0,075 Grad |
| Schrotflinte | 2 Grad | 0,5 Grad | 0,25 Grad |
| Doppelflinte | 3 Grad | 0,75 Grad | 0,375 Grad |
| Chaingun | 0,7 Grad | 0,175 Grad | 0,175 Grad |
| Minigun | 0,7 Grad | 0,175 Grad | 0,175 Grad |
| Raketenwerfer | 4,8 Grad | 1,2 Grad | 0,4 Grad |
| Plasma | 0,7 Grad | 0,175 Grad | 0,175 Grad |
| BFG | 7 Grad | 1,75 Grad | 0,583333 Grad |
| Pyrokanone | 7,5 Grad | 1,875 Grad | 0,375 Grad |

Die Vorherwerte stammen aus den Waffenstates. Strukturpruefung aller
43 geaenderten Zeilen: exakt ein Viertel des Gesamtimpulses, gleiche
Sprite-Dauer, Interpolation gesetzt und alle anderen Codezeilen identisch.
Alle 14 ACS-Module wurden im Build unveraendert reproduziert.

Laufzeitpruefung: `tools/test_recoil.py --mod <paket.pk3> --engine <uzdoom.exe>
--iwad <DOOM2.WAD>`. Der Test verwendet eine eigene leere Karte, feuert jede
der zwoelf Waffen fuer 70 Tics und misst Spitzenwinkel, groessten Schritt
sowie verbleibenden Versatz nach 100 Tics Erholung. Keine Kampagnen- oder
Koop-Vollabnahme; subjektives Spielgefuehl ist durch Messwerte nicht abgedeckt.

Finaler Lauf mit UZDoom 5.0.1 / Vulkan: alle zwoelf Waffen korrekt ausgewaehlt,
12 Assertions bestanden, keine Laufzeitfehler. Alle gemessenen Spitzen und
Einzelschritte entsprechen der Tabelle; bei jeder Waffe liegt der verbleibende
Versatz unter 0,00001 Grad. Nachweise unter `tools/validation/recoil-2026-09-08/`.

Der erste Testlauf waehlte die Pistole nicht korrekt aus und beendete sich
vor dem letzten asynchronen Messergebnis. Der Runner gibt jetzt jede Waffe
explizit und wartet auf die Messung; die Spielimplementierung benoetigte
keine weitere Korrektur.

Das Standardpaket `tutnt.pk3` war beim Bauen durch einen anderen Prozess
gesperrt. Das separat gebaute `tutnt-recoil.pk3` ist ein vollstaendiges Paket
und enthaelt den aktuellen lokalen Projektstand einschliesslich anderer
uncommittierter Projektarbeiten. Es ersetzt beim Start das normale Paket.
SHA-256: `a0e90ee4f847979aafcac85d618e4a02f516602ee8dadac5c106b03c5e368419`.
