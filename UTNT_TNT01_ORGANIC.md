# TNT01: organischere Außenbereiche

Diese erste Fassung ist als Entwicklungsnachweis erhalten. Die aktuelle großflächige Geländeüberarbeitung ist in [UTNT_TNT01_LANDSCAPE.md](UTNT_TNT01_LANDSCAPE.md) beschrieben.

Die Fels- und Graslandschaft in TNT01 erhält zusätzliche echte Kartengeometrie:
22 ausgewählte Felskanten werden in unregelmäßige Teilflächen gegliedert,
zehn niedrige Felsformationen und 17 flache Graswellen ergänzen die Außenflächen.
Die neuen Formen verteilen sich auf die westlichen Außenhöfe, die nördliche
Außenarena und eine ausreichend freie Stelle des östlichen Grasbereichs.
Enge, mit Objekten oder Triggern belegte Flächen werden ausgespart.

Die Überarbeitung ist bewusst maßvoll. Felskonturen ragen höchstens 32 Einheiten
in das ursprüngliche Gelände, die Bodenformen sind maximal 23 Einheiten hoch.
Gras läuft entlang der flachen Ausläufer weiter; die inneren Flächen der
Felsformationen verwenden das vorhandene QROCK3. Es werden keine neuen
Texturen, Dekorations-Actors oder Laufzeit-Thinker hinzugefügt.

## Geometrie und bestehende Kartenfunktionen

| Element | Vorher | Nachher | Hinzugefügt |
| --- | ---: | ---: | ---: |
| Vertices | 17.447 | 18.043 | 596 |
| Linedefs | 19.971 | 21.320 | 1.349 |
| Sidedefs | 34.556 | 37.241 | 2.685 |
| Sektoren | 3.742 | 4.522 | 780 |
| Things | 2.648 | 2.648 | 0 |

Alle ursprünglichen Thing-Eigenschaften und Sektoreigenschaften bleiben erhalten.
SCRIPTS und BEHAVIOR sind byteidentisch zur Ausgangskarte. Linedefs mit Aktionen
oder IDs werden nicht verändert; bestehende Linedef- und Sektorindizes bleiben
erhalten. ZDBSP kann die interne Vertexreihenfolge ändern; deren ursprüngliche
Koordinaten und die unveränderten Linienverbindungen werden räumlich geprüft.
An den aufgeteilten Felskanten werden die Texturversätze fortgeführt.

Neue Böden schließen an ihren Außenkanten exakt an den alten Boden an.
Sie übernehmen Decke, Beleuchtung und Glow-Einstellungen des Elternsektors.
Die maximale geprüfte Steigung beträgt 0,6444 (ca. 32,8 Grad).
Die einzelnen Formen halten mindestens 48 Einheiten Abstand von vorhandenen
Thing-Ursprüngen und meiden den Schutzbereich bestehender Aktionen.

## Prüfung

- Strukturprüfung: keine neuen Linienkreuzungen; 1.300 gemeinsame Bodenkanten
  dicht, größte Abweichung unter 0,000000006 Einheiten.
- Die sechs untersuchten Grasregionen behalten ihre zusammenhängenden
  Laufbereiche bei einem Prüfkreisradius von 32. Die durch neue Felskonturen
  verlorene freie Fläche beträgt je Region höchstens 1,80 Prozent.
- UZDoom 5.0.1: Vulkan/Marine, OpenGL/Scout und Vulkan/Commando bestehen je acht
  Assertions einschließlich Save/Load. Alle 780 Dreiecksflächen werden über
  ihren Schwerpunkt der erwarteten BSP-Region zugeordnet; die tatsächlich
  geladene Höhe stimmt auf besser als 0,000001 Einheiten mit dem Entwurf überein.
- Jede der 27 Formationen wird mit der jeweiligen Spielerklasse in 48
  Kollisionsschritten überquert, vor und nach Save/Load, ohne Noclip.
- Vergleichsansichten im Spiel und aktueller Paketstart ergänzen die Prüfungen.

Dies ist keine vollständige Kampagnen-, Koop- oder Performanceabnahme. Insbesondere
wurde nicht jede mögliche Sprungabkürzung manuell untersucht. Die Kollisionsprobe
prüft das Überqueren der neuen Formen, keinen vollständigen Kampfablauf.
Für die geänderte Karte TNT01 frisch starten; vorhandene Spielstände enthalten
ihren gespeicherten alten Kartenstand.

## Reproduktion

Generator: `tools/build_tnt01_organic.py`, Python 3.12 mit Shapely 2.x und ZDBSP.
Als Eingabe die TNT01-WAD aus dem Parent-Commit dieser Änderung verwenden.
Der Generator prüft den erwarteten Grundaufbau und verweigert eine doppelte
Anwendung auf bereits verfeinerte Karten. Er überschreibt die Eingabe nicht.

```text
python tools/build_tnt01_organic.py --source before.wad --output candidate.wad --zdbsp PATH/TO/zdbsp.exe --report-path build.json
python tools/test_tnt01_organic.py --before before.wad --after candidate.wad --manifest build.json --output structure.json
python tools/test_tnt01_organic_runtime.py --work TEST_DIRECTORY --mapfile candidate.wad --manifest build.json --mod tutnt.pk3 --engine PATH/TO/uzdoom.exe --iwad PATH/TO/DOOM2.WAD --renderer 1 --playerclass Marine
```

Die Normalen der UDMF-Hanggleichungen werden bereits beim Generieren auf Länge 1
gebracht, einschließlich desselben Faktors für den Abstandsterm. Das ist nötig,
weil UZDoom beim Laden nur die drei Normalkomponenten normalisiert.
Die Tests und ihr Add-on werden ausschließlich unter `tools` abgelegt und
nicht in das Spielpaket aufgenommen.

Nachweise: `tools/validation/tnt01-organic-2026-09-09/`.

## Aktives Spielpaket

Das aktive `tutnt.pk3` wurde erfolgreich ersetzt und direkt auf TNT01 geprüft.
Sechs zusätzliche Himmel-/Sektor-/Save-Load-Assertions bestanden; die enthaltene
Karte stimmt bytegenau mit der geprüften WAD überein. Alle 14 ACS-Module sind
aktuell und wurden ohne Bytecodeänderung reproduziert.

- Build: `15865559bae1`; 9038 Einträge, 179996459 Bytes.
- SHA-256: `fee185ebf3d89bb715dcf0b6785c460635c156496550df5760347c32858f1e0a`.
- Die Buildkennung bezeichnet den vor dem abschließenden Commit geprüften Arbeitsstand; das Paket enthält auch bereits vorhandene andere Projektänderungen.
