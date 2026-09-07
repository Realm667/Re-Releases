# UTNT – Einzelpartikel für Regen und Schnee

Die zweite Wetterfassung setzt die freigegebenen animierten Mockups um. Jeder Regentropfen und jede Schneeflocke ist ein eigenes bewegtes Teilchen – auch in der Ferne und in der Standard-Skybox. Die früheren Gruppenbilder und die breiten Pulverschnee-Sprites sind entfernt. Die Aufnahmen zur Freigabe liegen neben den neuen Nachweisen unter `tools/validation/weather-v2-2026-09-08/`.

## Darstellung

Regen fällt schnell in schmalen, weich auslaufenden Strichen. Am tatsächlichen Bodentreffer entstehen auf mittlerer/hoher Qualität drei bis fünf einzelne Spritztröpfchen mit jeweils eigener Richtung, Geschwindigkeit und Lebensdauer. Auf niedriger Qualität sind es zwei. Die Tröpfchen steigen kurz auf, werden durch Schwerkraft abgebremst und fallen zurück. Wände, Decken, feste 3D-Böden und Wasser begrenzen auch diese Bewegung.

Schnee reagiert jeden Spieltic auf ein sanft veränderliches Windfeld. Individuelle Phasen und eine geglättete Reaktion erzeugen unterschiedliche Flugbahnen. Die bestehende Interpolation der VisualThinker verbindet die Simulationsschritte. Kleine Flocken bilden die Grunddichte; größere Flocken bleiben selten. Gleichförmig rotierende Gruppen gibt es nicht mehr.

Windformeln, Nahbereichsgewichtung und maximale Reichweite von 900 Karteneinheiten entsprechen der freigegebenen Vorschau. Die nachfolgend beauftragte Feinabstimmung verändert Größen, Regenlänge, Deckkraft und Regenfalltempo wie unten beschrieben. Der Spielbetrieb ergänzt separate Budgets und vollständige Kollisionsprüfungen für Spritztröpfchen. Die Vorschau nutzte noch bis zu 5.000 Traces pro Tic; die neue hohe Qualitätsstufe ist auf 3.200 begrenzt.

## Technik und Einstellungen

`tutnt/zscript/UTNT_Weather.zc` enthält den lokalen Controller und die VisualThinker. Bestehende Marker 19021/19022 begrenzen die Wetterflächen; Positionen, TIDs und Kartengeometrie bleiben erhalten. Eine private Zufallsfolge hält die rein visuellen Teilchen aus der Spielzustands-Zufallsfolge heraus. Die vorhandene Standard-Skybox erhält eine eigene Schicht aus Einzelpartikeln, die durch die Sky-Öffnungen verdeckt wird.

`weatherfx` bleibt der gemeinsame Wetterschalter. `UTNT_fxquality`, `UTNT_reducedfx` und `UTNT_lod` steuern die lokale Darstellung. Niedrigere Qualität reduziert Dichte und Detailbudget, ersetzt aber niemals mehrere Teilchen durch eine Gruppengrafik. Die Wetterbudgets sind vom Kampfeffektbudget getrennt.

| Qualität | Niederschlag maximal | Spritzer/Ringe zusätzlich | Traces pro Tic maximal |
| --- | ---: | ---: | ---: |
| Niedrig / reduzierte Effekte | 500 | 40 | 760 |
| Mittel | 1.300 | 110 | 1.700 |
| Hoch | 2.600 | 220 | 3.200 |

Emission stoppt an der jeweiligen Obergrenze. Schnee und Spritztröpfchen prüfen ihre Bewegung jeden Tic; Regen prüft bis zu acht Tics als gerades Segment voraus. Falls die Trace-Grenze dennoch erreicht wird, wird das betreffende Teilchen entfernt. Es bleibt nicht sichtbar in der Luft stehen. In den dokumentierten bestandenen Fällen wurde dieser Notpfad nicht benötigt. Umschalten und Freeze gelten auch für den Controller und die neuen Tröpfchen.

Die zuvor eingeführte Nebeldichte 32 in TNT03A1/TNT03A2, die ACS-Tag-Nacht-Farben und der lokale Wetteraudiomix bleiben erhalten. Wetter aus stellt die vorherige Nebeldichte wieder her, solange kein anderes System sie übernommen hat. Wasser behält zusätzlich den bisherigen kurzen elliptischen Sprite-Ring; eine neue oberflächenorientierte Ringdarstellung war nicht Bestandteil der freigegebenen Filme. Neue Pfützen, Spiegelungen oder Schneeakkumulation werden nicht berechnet.

## Prüfung

Die aktuelle Fallliste, Assertionszahlen, Bildaufnahmen und Leistungsmessungen liegen unter `tools/validation/weather-v2-2026-09-08/`. Die Nachweise von Version 1 bleiben als historischer Stand im älteren Ordner erhalten.

- UZDoom 5.0.1, OpenGL und Vulkan: Regen TNT02, Schnee TNT03A1 und Außenbereich TNT03A2.
- Save/Load, Wetter aus/an, Qualitätsstufen, reduzierte Effekte und Nebelzustand.
- Hub-Wechsel TNT03A1 → TNT03A2 → TNT03A1 auf beiden Renderern.
- Geometriekarte mit Dach, Wänden, festem 3D-Boden, Schräge, Wasser, Innenraum und Freeze.
- Gezielte Spritztröpfchen gegen Wand, Decke, 3D-Boden und Wasser; ein freies Tröpfchen muss zunächst steigen und anschließend fallen.
- Einzelpartikel-Texturen in allen Entfernungen, unterschiedliche Schneegeschwindigkeiten, getrennte Budgets und kein Erreichen des Notpfads bei der Trace-Grenze.
- Zwei lokale Koop-Prozesse mit unterschiedlichen Qualitätsstufen und übereinstimmendem gemeinsamem Spielzustand.

Der TNT03A2-Startpunkt liegt tief im Innenbereich. Der Außeneffekt-Test wurde auf einen tatsächlichen offenen Wetterbereich gelegt; er verlangt dort sichtbaren Schnee. Das ist eine Änderung der Testposition, keine Verschiebung von Spielstart oder Wettermarkern.

Die kurzen Leistungsmessungen vergleichen Wetter aus/an auf derselben Maschine bei 960×540 unter Vulkan ohne FPS-Limit. Sie sind keine allgemeine FPS-Garantie. Keine vollständige Kampagnenabnahme und keine Zusicherung zur Migration alter Savegames oder zu beliebigen fremden Portal-/Skybox-Konstruktionen. Der Audiomix wurde in dieser Fassung nicht verändert.

## Wiederholung

Mit gesetzten `UTNT_ENGINE` und `UTNT_IWAD`:

```text
python tools/test_weather.py --mod tutnt.pk3
python tools/test_weather.py --case motion
python tools/profile_weather.py
```

`tools/generate_weather_assets.py` erzeugt nur noch Einzelpartikelgrafiken, den vorhandenen Wasserring und die Soundbetten deterministisch. Test-Add-ons werden nicht in das Spielpaket aufgenommen. `tutnt_build.bat` baut das normale PK3.

## Abschlussmessung vom 08.09.2026

21 konsolidierte Laufzeitfälle mit 691 bestandenen Assertions; zusätzlich zwei Prüfungen des gebauten PK3 mit jeweils neun Assertions. Die Texturprüfung findet genau eine sichtbare zusammenhängende Form pro Niederschlagsgrafik. Alle 14 ACS-Module waren beim Bau bytegleich aktuell. Frühere, korrigierte Testversuche sind in den Hinweisen der Ergebnisdatei erläutert.

Gemessen auf Ryzen 9 7950X / GeForce RTX 4080, Vulkan, 960×540, je ein etwa fünfsekündiges Messfenster:

| Karte | Median Wetter aus | Median Wetter an | Mehrkosten Median | p95 Wetter an |
| --- | ---: | ---: | ---: | ---: |
| TNT02 – Regen | 2,188 ms | 2,414 ms | 0,226 ms | 3,685 ms |
| TNT03A1 – Schnee | 1,271 ms | 2,861 ms | 1,590 ms | 4,633 ms |

Die freigegebene Bewegung benötigt besonders beim Schnee mehr Rechenzeit als die frühere Gruppendarstellung. Die Qualitätsstufen begrenzen deshalb Teilchenzahl und Kollisionsprüfungen separat. Build-Daten und Paketprüfungen stehen in `weather-v2-build.json`, `weather-v2-live-build.json` und `weather-v2-package-results.json` im Nachweisordner. Das Gesamtpaket enthält zusätzlich den zum Bauzeitpunkt vorhandenen Stand anderer Projektarbeiten; diese gehören nicht zum Wettercommit.

## Feinabstimmung nach Nutzerprüfung – 08.09.2026

- Regenstriche sind pro Tropfen zufällig 30–50 % länger. Derselbe Faktor gilt auch für die entfernungsabhängige Begrenzung, damit die Verlängerung im Nahbereich sichtbar bleibt.
- Ein gemeinsamer Faktor 0,70 reduziert die bisherige Deckkraft von Regen, einzelnen Bodenspritzern und Wasserringen um 30 %. Vorhandene weiche Ein-/Ausblendungen bleiben wirksam. Die vorherigen effektiven Alpha-Werte waren bereits variabel, daher wird nicht pauschal Alpha 0,70 erzwungen.
- Jeder Regentropfen bewegt sich um zufällig 10–15 % langsamer. Das gilt für seine vertikale und horizontale Geschwindigkeit und auch für den Regen in der Skybox.
- Jede Schneeflocke ist um zufällig 10–20 % größer, einschließlich ihrer Größenbegrenzung nahe der Kamera und der Skybox-Schicht.
- Der dezente Schnee-Nachlauf folgt dem bereits auf Kollision geprüften letzten Bewegungssegment. Ein einzelnes, eng überlappendes Abbild derselben Flocke hat 14 % ihrer Deckkraft und höchstens 30 % ihres Durchmessers Versatz. Es benötigt weder Gruppentexturen noch zusätzliche Kollisionsabfragen. Maximal 520 Nachläufe auf hoher beziehungsweise 260 auf mittlerer Qualität, nur innerhalb von 450 Einheiten; niedrige Qualität/reduzierte Effekte lassen den Nachlauf aus. Elternteil und Nachlauf werden gemeinsam entfernt.

Neue Nachweise: `tools/validation/weather-tuning-2026-09-08/`. Die vorherige Abschlussmessung beschreibt weiterhin den Stand vor dieser Feinabstimmung. Die neuen Prüfungen verwenden ein festes PK3, damit gleichzeitig bearbeitete Kartenskripte während Save/Load nicht wechseln können.

Abnahme der Feinabstimmung: 10 bestandene Laufzeitfälle mit 552 Assertions auf OpenGL/Vulkan (inklusive Save/Load, Freeze, Geometrie und Qualitätswechsel), Bildprüfung beider Effekte sowie vier kurze Leistungsmessungen. Wettercode und Texturen im erneuerten regulären PK3 sind bytegleich zum getesteten Snapshot.

| Karte | Median Wetter aus | Median Wetter an | p95 Wetter an |
| --- | ---: | ---: | ---: |
| TNT02 | 2.026 ms | 2.554 ms | 3.885 ms |
| TNT03A1 | 1.313 ms | 3.149 ms | 5.072 ms |

Diese kurzen Messfenster gelten für dieselbe Maschine und Auflösung wie oben. Gleichzeitig fortgeschrittene andere Projekteffekte verhindern einen isolierten Vergleich mit der früheren Gesamtbildzeit.
