# UTNT – dynamische Wetterzyklen

Aktueller Stand: freigegebener kräftiger Regenschauer und Schneesturm mit anschließender Beruhigung. Schnee verwendet neutralgraue Grundfarbe `#CCCCCC`, Regen weiterhin `#808080`. Alpha, Beleuchtung und Nebel beeinflussen die tatsächlich sichtbaren Pixel. Jede Flocke und jeder Tropfen bleibt ein einzelnes Teilchen, auch im Skybox-Feld. Der Schnee-Nachlauf übernimmt dieselbe graue Textur; Verwehungen verwenden einen neutralen Shaderfarbwert von 0,8.

## Zeitlicher Verlauf

| Spielzeit im Zyklus | Zustand |
|---|---|
| 0–45 s | Leichtes Wetter |
| 45–105 s | Sanfter Aufbau zur moderaten Stärke |
| 105–165 s | Aufbau zum Schauer beziehungsweise Schneesturm |
| 165–225 s | Intensive Phase mit Böen |
| 225–290 s | Sanfte Beruhigung |
| 290–300 s | Leichtes Wetter vor dem nächsten Zyklus |

Smoothstep-Übergänge vermeiden harte Stufen. Oberhalb der moderaten Intensität verstärkt eine zweite weiche Kurve die freigegebene Spitzenphase. Der Wind verändert sich fortlaufend; ein deterministischer Phasenversatz variiert die Böen zwischen den Zyklen.

`UTNTWeatherHandler` speichert Wettertics und Zyklusnummer pro Karte. Die Uhr stoppt bei Freeze und läuft unabhängig von lokaler Qualität und ausgeschaltetem Wetter weiter. Save/Load stellt sie gemeinsam mit dem Kartenstand wieder her; Koop-Teilnehmer verwenden dieselbe Uhr. Bei einem alten Spielstand ohne Wetteruhr beginnt der neue Zyklus leicht.

## Darstellung und Budgets

Regen erreicht maximal die sechsfache Zielbelegung gegenüber leichtem Wetter. Im Schauer werden seine Striche zusätzlich bis zum Faktor 2,4 gestreckt; Seitenwind und Falltempo nehmen zu. Splashes entstehen an tatsächlichen Bodenaufprällen. Ein reservierter Anteil des Detailbudgets verhindert, dass Spritzer die feinen bodennahen Schleier verdrängen.

Schnee erreicht maximal die 4,8-fache Zielbelegung, kräftigere seitliche Böen, schnelleres Fallen und bis zum Faktor 2,4 gestreckte Flocken. Der transparente Nachlauf wird länger. Wenige bodennahe und schwebende Verwehungen ergänzen die Einzelpartikel. Die ursprünglichen Atlasformen werden als weiche Volumenschleier genutzt; Niederschlagsgruppenbilder werden nicht verwendet. In den bereits verwalteten grauen Nebelsektoren von TNT03A1/TNT03A2 steigt die Dichte von 32 bis höchstens 54 und sinkt beim Abklingen wieder. Wetter aus stellt nur selbst verwaltete Werte zurück.

| Qualität | Niederschlag maximal | Details zusätzlich | Traces/Tic maximal | Nachläufe maximal | Schleier maximal (Teil des Detailbudgets) |
|---|---:|---:|---:|---:|---:|
| Niedrig / reduziert | 2.000 | 80 | 2.200 | 0 | 0 |
| Mittel | 7.000 | 420 | 6.500 | 300 | 32 |
| Hoch | 20.000 | 1.400 | 18.000 | 800 | 96 |

Das sind Obergrenzen; die tatsächliche Menge hängt von Karte, Entfernung und Wetterstärke ab. Mittlere/niedrige Qualität verwendet 35/10 Prozent der hohen Zellzielbelegung. Die zusätzliche Sturm-Dichte des Schnees nimmt in großer Entfernung weich ab; die vorhandene Basisbelegung und der vorausgeladene Bereich mit bis zu 2.048 Einheiten Sichtweite und bis zu 640 Einheiten Spawnpuffer bleiben erhalten. Im Nahbereich gilt die volle freigegebene Stärke. Separate transparente Nachläufe sind auf Weltflocken innerhalb von 450 Einheiten begrenzt; weiter entfernte Flocken und das Skybox-Feld behalten ihre gestreckte Bewegungsform.

Schnee prüft ein gerades Bewegungssegment über zwei Tics statt über einen; die Windglättung ist entsprechend angepasst. Die Renderinterpolation bleibt erhalten. Regen prüft bis zu acht Tics im Voraus. Spritztröpfchen und Verwehungen prüfen ihre Bewegung jeden Tic. Schleier begrenzen ihre Ausdehnung bereits beim Spawn anhand umliegender Wände, Boden und Decke. Ein Notpfad entfernt ein Teilchen bei ausgeschöpftem Tracebudget statt es einzufrieren.

Die vorhandenen Regen-/Wind-Soundbetten folgen der Wetterintensität. Überdachung und Abstand dämpfen sie weiterhin; im Schauer kommt eine stärkere Windkomponente hinzu. Es gibt keine dynamische Schneeakkumulation oder neue Spiegelungen.

## Prüfung und Wiederholung

Aktuelle Nachweise: `tools/validation/weather-cycle-2026-09-08/`. Mit `UTNT_ENGINE` und `UTNT_IWAD`:

```text
python tools/test_weather_cycle.py --mod tutnt.pk3 --case cycle --map TNT02 --renderer 0
python tools/test_weather_cycle.py --mod tutnt.pk3 --case cycle --map TNT03A1 --renderer 1
python tools/test_weather_cycle.py --mod tutnt.pk3 --case geometry --map UTNTWX
python tools/test_weather_cycle.py --mod tutnt.pk3 --case colors --map TNT03A1
python tools/profile_weather_cycle.py --mod tutnt.pk3
```

`--root` erlaubt einen separaten Ort für Testdateien, Logs und Savegames. Die neuen Prüfungen ergänzen die bestehenden Wetter- und Sprinttests. Farbfelder bestätigen RGB-Gleichheit und den erwarteten Alpha-Mischwert: bei Quellalpha 235 ergibt Grundwert 204 auf Schwarz maximal 188. Vollständige Produktionsmessungen stehen in den Ergebnisdateien; kurze lokale Messfenster sind kein allgemeines FPS-Versprechen.

## Historische Stände vor den Wetterzyklen

Die folgenden früheren Abnahmen dokumentieren den jeweiligen damaligen Stand. Ihre Parameter und Budgets wurden durch die Angaben oben ersetzt.

### Einzelpartikel – frühere Fassung

Die zweite Wetterfassung setzt die freigegebenen animierten Mockups um. Jeder Regentropfen und jede Schneeflocke ist ein eigenes bewegtes Teilchen – auch in der Ferne und in der Standard-Skybox. Die früheren Gruppenbilder und die breiten Pulverschnee-Sprites sind entfernt. Die Aufnahmen zur Freigabe liegen neben den neuen Nachweisen unter `tools/validation/weather-v2-2026-09-08/`.

## Darstellung

Regen fällt schnell in schmalen, weich auslaufenden Strichen. Am tatsächlichen Bodentreffer entstehen auf mittlerer/hoher Qualität drei bis fünf einzelne Spritztröpfchen mit jeweils eigener Richtung, Geschwindigkeit und Lebensdauer. Auf niedriger Qualität sind es zwei. Die Tröpfchen steigen kurz auf, werden durch Schwerkraft abgebremst und fallen zurück. Wände, Decken, feste 3D-Böden und Wasser begrenzen auch diese Bewegung.

Schnee reagiert jeden Spieltic auf ein sanft veränderliches Windfeld. Individuelle Phasen und eine geglättete Reaktion erzeugen unterschiedliche Flugbahnen. Die bestehende Interpolation der VisualThinker verbindet die Simulationsschritte. Kleine Flocken bilden die Grunddichte; größere Flocken bleiben selten. Gleichförmig rotierende Gruppen gibt es nicht mehr.

Die Windformeln entsprechen der freigegebenen Vorschau. Die später beauftragte Sprintkorrektur erweitert die Sichtweite auf bis zu 2.048 Einheiten und verteilt Teilchen nach der Belegung einzelner Wetterzellen. Die nachfolgend beauftragte Feinabstimmung verändert Größen, Regenlänge, Deckkraft und Regenfalltempo wie unten beschrieben. Der Spielbetrieb ergänzt separate Budgets und vollständige Kollisionsprüfungen für Spritztröpfchen. Die Vorschau nutzte noch bis zu 5.000 Traces pro Tic; die erste Produktionsfassung war auf 3.200 begrenzt. Die erweiterte Abdeckung darf auf hoher Qualität bis zu 5.000 Traces nutzen.

## Technik und Einstellungen

`tutnt/zscript/UTNT_Weather.zc` enthält den lokalen Controller und die VisualThinker. Bestehende Marker 19021/19022 begrenzen die Wetterflächen; Positionen, TIDs und Kartengeometrie bleiben erhalten. Eine private Zufallsfolge hält die rein visuellen Teilchen aus der Spielzustands-Zufallsfolge heraus. Die vorhandene Standard-Skybox erhält eine eigene Schicht aus Einzelpartikeln, die durch die Sky-Öffnungen verdeckt wird.

`weatherfx` bleibt der gemeinsame Wetterschalter. `UTNT_fxquality`, `UTNT_reducedfx` und `UTNT_lod` steuern die lokale Darstellung. Niedrigere Qualität reduziert Dichte und Detailbudget, ersetzt aber niemals mehrere Teilchen durch eine Gruppengrafik. Die Wetterbudgets sind vom Kampfeffektbudget getrennt.

| Qualität | Niederschlag maximal | Spritzer/Ringe zusätzlich | Traces pro Tic maximal |
| --- | ---: | ---: | ---: |
| Niedrig / reduzierte Effekte | 800 | 40 | 1.100 |
| Mittel | 2.100 | 110 | 2.700 |
| Hoch | 4.200 | 220 | 5.000 |

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

## Sprintabdeckung, grauer Regen und Player-Start – 08.09.2026

Die Standard-Sichtweite wächst von 900 auf 2.048 Karteneinheiten; `UTNT_lod` begrenzt sie weiterhin. Außerhalb liegt ein zusätzlicher Spawnpuffer von bis zu 640 Einheiten. Die Zellauswahl wird alle vier Tics beziehungsweise nach mehr als 64 Einheiten Kamerabewegung aktualisiert. Die Bewegungsgeschwindigkeit bestimmt einen vorausliegenden Bereich für bis zu 24 Tics (maximal 768 Einheiten).

Jede 128×128-Zelle zählt ihre eigenen Teilchen. Die Emission bevorzugt relativ unterbesetzte Zellen und füllt auch das äußere Feld. Dadurch können volle Nahbereichszellen die Versorgung der nächsten Fläche nicht mehr verdrängen. Eine an Entfernung und Qualitätsstufe angepasste Zieldichte schützt den Nahbereich; überzählige Teilchen laufen weich innerhalb von 18 Tics aus. Ein 512 Einheiten breiter Rand blendet die Entfernung aus. Die ersten 20 aktiven Tics nutzen ein begrenztes zusätzliches Füllbudget. Auch die vorausgeladenen Positionen durchlaufen die vorhandenen Dach-/Geometrieprüfungen.

`textures/definitions/TEXTURES.weather` definiert drei neutralgraue Varianten für Regenstrich, Spritztröpfchen und Wasserring: RGB 128/128/128 (`#808080`). Die Komposition ersetzt nur RGB, bewahrt die einzelnen Formen samt Alpha und lässt die Schneequellen unverändert. Die zuvor beauftragten 70 % relativer Deckkraft und langsameren/längeren Regentropfen gelten weiterhin.

In TNT03A1 wurde ausschließlich der zusätzliche normale Player-1-Start Thing 1141 bei (832, −5376) entfernt. Der normale Start bei (−1440, 2112), seine Koop-Partner sowie die alternative Einstiegsgruppe mit `arg0=1` bei (3360, −4992) bleiben erhalten. Alle anderen TEXTMAP-Bytes und alle übrigen WAD-Lumps wurden bei dieser Änderung erhalten; insbesondere wurden parallele Änderungen an Ausgangslinien und Kartenskripten nicht zurückgesetzt.

Neue Nachweise: `tools/validation/weather-coverage-2026-09-08/`. Reproduzierbar mit `tools/test_weather_sprint.py --mod tutnt.pk3`, `tools/test_weather_mapstart.py --mod tutnt.pk3` und den bestehenden Wettertests. Der Sprinttest fährt mit 32 Einheiten pro Tic insgesamt 9.600 Einheiten hin und zurück und verlangt an jedem Messpunkt bereits gereifte Teilchen vor der Kamera und im Bereich 1.000–1.600 Einheiten voraus. Kein allgemeines Versprechen für beliebig hohe Mod-Geschwindigkeiten oder Teleports über die Pufferweite hinweg.

Abnahme dieser Fassung: 11 bestandene Laufzeitfälle mit 339 Assertions, neutralgraue gerenderte Farbmuster auf beiden Renderern und Startpunktprüfungen im Test- und regulären Paket. In jedem der vier Sprintläufe waren alle 35 Messpunkte ohne Versorgungslücke (Regen mindestens 12 gereifte Teilchen nah / 5 außen; Schnee mindestens 171 nah / 56 außen).

Kurze Vulkan-Messfenster auf derselben Maschine (Millisekunden pro Frame):

| Karte | Median Wetter aus | Median Wetter an | p95 Wetter an |
| --- | ---: | ---: | ---: |
| TNT02 | 2.038 | 2.035 | 3.066 |
| TNT03A1 | 1.343 | 3.267 | 5.750 |

Die nahezu gleichen Regen-Mediane liegen innerhalb der Schwankung dieser kurzen Messung; daraus folgt kein Leistungsgewinn. Die früheren Abnahmen bleiben historisch dokumentiert.

## Abschluss der Wetterzyklen – 08.09.2026

12 konsolidierte Laufzeitfälle mit 438 bestandenen Assertions, zusätzlich 2 Läufe des regulären PK3 mit 32 Assertions. Die höchste Schneestufe bleibt deutlich aufwendiger als leichter Schneefall. Separate Nachläufe nur für lesbare nahe Weltflocken und geringere zusätzliche Dichte fern liegender Flocken reduzieren die Last, während die Basisbelegung des äußeren Felds bestehen bleibt.

Vulkan, 960×540, Ryzen9 7950X/RTX4080, kurze feste Perspektiven; Millisekunden pro Frame:

| Karte | Median aus | Median leicht | Median Sturm | p95 Sturm |
|---|---:|---:|---:|---:|
| TNT02 | 2.336 | 3.148 | 6.066 | 11.119 |
| TNT03A1 | 1.481 | 3.976 | 16.806 | 19.85 |

Diese Messungen sind keine allgemeine FPS-Garantie. Sie stammen aus dem isolierten Wetterpaket; das reguläre Paket enthält zusätzlich parallele Projektänderungen. Eine ergänzende Endpunktprüfung in jedem Niederschlags-Tic verhindert auch schnelle seitliche Eintritte in feste 3D-Böden. Die neue Farbfassung ersetzt ausschließlich RGB; die bisherige Einzelpartikelform und Transparenz bleiben erhalten.
