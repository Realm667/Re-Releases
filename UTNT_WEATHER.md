# UTNT – Regen und Schnee

Das freigegebene Wetterkonzept ist in ZScript umgesetzt. Regen verwendet kurze, feine, windgerichtete Striche und sparsame Bodenspritzer. Schnee verwendet kleine unregelmäßige Flocken, gemeinsamen Böenwind, individuelle Taumelbewegung, entfernte Flockengruppen und bodennahen Pulverschnee. Die bestehenden Kartentexturen, Geometrie, Spawner-Positionen und TIDs bleiben erhalten.

## Aufbau

- `tutnt/zscript/UTNT_Weather.zc`: ein lokaler Controller, private Zufallsfolge, begrenzte `VisualThinker`, getrennte Welt- und Skybox-Schicht. Keine Niederschlags-Projektile und keine Netzereignisse für Wetterteilchen. Spawner 19021/19022 sind jetzt inaktive Flächenmarker mit den ursprünglichen Klassennamen.
- Marker werden zu 128-Einheiten-Zellen zusammengefasst; nahes Wetter hat Vorrang. Die tatsächlichen Teilchenpositionen bleiben in der Welt verankert. Die entfernte Schicht liegt innerhalb der vorhandenen Standard-Skybox und wird von Architektur/Sky-Öffnungen verdeckt.
- Vor einem Spawn wird der freie Raum einschließlich fester 3D-Böden und Flüssigkeiten geprüft. Aufwärts-Traces prüfen den Himmel. Bewegungssegmente werden vorab gegen Wände, Böden, Decken und Wasser geprüft; bei ausgeschöpftem Prüfbudget hält ein Teilchen an, statt ungeprüft weiterzufliegen. Regen prüft höchstens acht, Schnee höchstens sechzehn Tics im Voraus. Breite Nebel-/Pulverschnee-Sprites werden nur auf freien Außenflächen erzeugt.
- Regen reagiert mit kleinen Spritzern auf Böden und mit kurzen elliptischen Ringen auf Wasser. Diese Effekte sind sparsame Sprite-Annäherungen; es gibt keine neu berechneten Pfützen, Spiegelungen oder Schneeakkumulation.
- Der Nahbereich von TNT03A1/TNT03A2 erhält explizite Nebeldichte 32. Die vorhandenen ACS-Tag-Nacht-Farben bleiben maßgeblich. Ausgeschaltetes Wetter stellt die vorherige Dichte wieder her, sofern kein anderes System inzwischen eine andere Dichte gesetzt hat.
- Vier prozedural erzeugte Audioressourcen bilden überlappende Regen-/Windbetten, gedämpften Regen und einzelne Tropfen. Der lokale Mix berücksichtigt die Nähe zu Wetterflächen und Überdachungen. Musik und vorhandene Ambiente-Actors werden nicht verändert.

## Einstellungen und Budgets

`weatherfx` bleibt die gemeinsame Wetteroption. `UTNT_fxquality`, `UTNT_reducedfx` und `UTNT_lod` steuern die lokale Teilchendarstellung. Die Nebeldichte hängt für alle Koop-Spieler am gemeinsamen Wetterschalter. Lokale Qualitätsunterschiede ändern keinen Spielzustand und beanspruchen nicht das Budget der Kampfeffekte.

| Qualität | Aktive Wetterobjekte, maximal | Geometrie-Traces pro Tic, maximal |
| --- | ---: | ---: |
| Niedrig / reduzierte Effekte | 320 | 64 |
| Mittel | 1024 | 144 |
| Hoch | 2048 | 240 |

Ferne Flockengruppen enthalten mehrere kleine Flocken in einer Grafik. Die Tabelle zählt VisualThinker, nicht jede einzelne gezeichnete Flocke. Beim Ausschalten werden vorhandene Teilchen entfernt. Der Controller wird nach Save/Load neu aufgebaut; Windphase und vorhandener Karten-/Nebelzustand bleiben an den Levelzustand gebunden.

## Prüfung

Nachweise liegen unter `tools/validation/weather-2026-09-07/`, die konsolidierte Fallliste und genaue Assertionszahl in `results.json`.

- UZDoom 5.0.1: Kompilierung sowie OpenGL-/Vulkan-Aufnahmen der Originalkarten TNT02 und TNT03A1; TNT03A2 ebenfalls gestartet.
- Save/Load, Wetter aus/an, Qualitätsstufen einschließlich vollständig ausgeschalteter lokaler Effekte, reduzierte Effekte und Nebelzustand.
- Hub-Wechsel TNT03A1 → TNT03A2 → TNT03A1 auf beiden Renderern.
- Isolierte Geometriekarte: Dach, Unter-/Oberseite eines festen 3D-Bodens, Spawn innerhalb eines festen 3D-Volumens, Schräge, Wand, Wasser, geschützter Innenraum und Freeze ohne weitere Teilchenerzeugung.
- Zwei echte lokale Koop-Prozesse mit Qualität 0 und 3: unabhängige Darstellung, übereinstimmender gemeinsamer Spielzustand.
- Audio mit aktivem Soundsystem decodiert. Subjektive Audiomischung wurde nicht durch einen Hörtest abgenommen.

Ein anfänglicher Vulkan-Aufnahmestart blieb ohne VM-Fehlermeldung stehen. Die anschließenden vollständigen Bildprüfungen bestanden auf beiden Renderern; die Testkonfiguration setzt Hintergrundaktivität ausdrücklich.

Vier kurze Einzelmessungen bei 960×540, Vulkan, ohne FPS-Limit, Ryzen 9 7950X / RTX 4080: Median mit Wetter aus/an in TNT02 1,810/2,252 ms, in TNT03A1 1,360/2,093 ms. Dies misst den zusätzlichen Aufwand gegenüber ausgeschaltetem Wetter im aktuellen Spielstand, keinen Vergleich mit dem alten Wettersystem und keine allgemeine FPS-Garantie. Rohdaten: `profile-results.json` und zugehörige Logs.

Keine vollständige Kampagnenabnahme, keine Zusicherung zur Migration alter Savegames oder zu beliebigen fremden Portal-/Skybox-Konstruktionen. Die Tests beziehen sich auf die beschriebenen Karten und Geometriefälle. Bewegte Geometrie wird abschnittsweise erneut geprüft; das System ist keine vollständige Flüssigkeitssimulation.

## Wiederholung

Mit konfigurierten `UTNT_ENGINE` und `UTNT_IWAD`:

```text
python tools/test_weather.py --mod tutnt.pk3
python tools/profile_weather.py
```

Die Testkarte kann über `tools/make_weather_fixture.py` reproduziert werden. `tools/generate_weather_assets.py` erzeugt alle Wettergrafiken und Soundbetten deterministisch (Pillow/NumPy); die Laufzeit benötigt diese Bibliotheken nicht. Das normale `tutnt_build.bat` erzeugt das PK3 einschließlich der neuen Ressourcen. Test-Add-ons werden nicht mit ausgeliefert.

## Finales Build

Das fertige lokale `tutnt.pk3` wurde erneut mit TNT02 und TNT03A1 unter Vulkan geprüft. Alle 14 ACS-Kompilate blieben beim Build bytegleich. Paket: 8.838 Dateien, 85.569.860 Bytes; SHA-256 `e38df499033f6333a062d0a44b9988a57cc527504d9396cec1084905d2e6b2ff`.

Zusätzlich wurde ein aus dem Git-HEAD erzeugter Stand mit ausschließlich den Wetteränderungen kompiliert und auf TNT03A1 gestartet (fünf Assertions bestanden). Der Commit enthält nur die Wetterimplementierung und ihre Prüfmittel. Das lokale PK3 enthält außerdem den bereits vorhandenen Arbeitsstand anderer Aufgaben; dessen Dateien werden nicht in den Wettercommit aufgenommen. Die isolierten Prüfprotokolle liegen neben den übrigen Nachweisen.
