# TNT03B: vulkanische Caldera

Die flache Kulisse aus transparenten Bergwänden wurde durch eine gestaffelte Basaltlandschaft mit rot glühenden Tälern und einer dunkleren Aschewolkendecke ersetzt. Die helle Öffnung liegt in südlicher Blickrichtung hinter der Festung. Grundlage ist das vom Nutzer freigegebene Mockup.

## Umsetzung

- Der normale SkyViewpoint von TNT03B steht jetzt bei (18000, 18000, 0) in einer isolierten Kulisse. Drei flache, überlappende Felszüge bestehen aus geneigten Sektoren; die detaillierten Fernberge, Taldunst und entfernten Rauchsilhouetten sind im Panorama ausgearbeitet. Diese Kombination wurde nach tatsächlichen Engineaufnahmen gewählt, weil hohe reine Sektorberge zu grob wirkten.
- Ein eigenes 360°-Panorama wird auf sechs nahtlos zusammenhängende Würfelflächen abgebildet. Explizite Interpolation hält die Darstellung auch bei ungefilterten Spieltexturen ruhig. Die hintere Panoramaüberblendung verhindert einen harten Abschluss; die Belichtung nimmt dem hohen Himmel die Dominanz über der Architektur.
- Zwei langsam umlaufende Wolkenlagen bilden einen spiralförmigen Ring um ein ruhiges Sturmauge im Zenit. Die Lagen drehen sich in etwa 14 beziehungsweise 20 Minuten einmal herum. Nur der hohe Himmel oberhalb von 40 Grad wird animiert; ein weich überblendetes Auge verhindert eine sichtbare Polverzerrung. Fernberge und Rauchsilhouetten bleiben fest. Es werden keine physischen Volumenwolken, bewegten Rauch-Actors oder spielerabhängige Skybox-Parallaxe eingesetzt.
- Die zweite Skybox (TID 4) bleibt einschließlich Actorposition erhalten. MAPINFO weist den neuen Himmel nur TNT03B zu. Es gibt keine globalen Texturersetzungen.
- Ergänzt: 448 Vertices, 1.216 Linedefs, 2.368 Sidedefs und 769 Sektoren. Vorhandene Indizes bleiben stabil. ZDBSP hat die Nodes mit `-q -X -g -r` neu aufgebaut.

## Prüfung

- Vergleich mit dem Arbeitsstand vor dieser Änderung: alle ursprünglichen Vertices, Linedefs, Sidedefs, Sektoren, SCRIPTS und BEHAVIOR unverändert. Von 450 Things wurde ausschließlich der normale SkyViewpoint versetzt. Keine neue Verbindung zur Spielgeometrie, keine neuen Linedef-Specials.
- Gemeinsame Kanten der geneigten Flächen schließen mit weniger als 0,000005 Map-Einheiten Höhenabweichung.
- Alle 14 ACS-Module mit ACC erneut geprüft; vorhandener Bytecode ist aktuell und byteidentisch.
- Das gebaute Paket wurde in UZDoom 5.0.1 mit OpenGL und Vulkan bei 1920 × 1080 geprüft: je zwölf Ansichten, freie Sicht auf hinteren Übergang und Würfelkanten sowie Speichern/Laden. Je sechs Assertions bestanden. Geprüfte Bildauswahl und vollständige Laufprotokolle liegen neben diesem Bericht unter `tools/validation/caldera-2026-09-08`.
- Ein separater Test nach Ende der Introeinblendung prüft die Wolkenanimation mit zwei fünf Sekunden auseinanderliegenden Zenithaufnahmen. Mittlere absolute RGB-Differenz im reinen Himmelsausschnitt: 0.2982.
- Die Würfelflächen und Shader wurden aus der gespeicherten Quelle erneut erzeugt und stimmen bytegenau überein. Paketressourcen entsprechen den geprüften Quelldateien; Testkameras werden nicht ins Spielpaket aufgenommen.

Das ist eine Prüfung der geänderten Kulisse, keine erneute vollständige Kampagnen- oder Multiplayerabnahme. Der Bildaufbau folgt dem Mockup; eine pixelidentische Nachbildung der KI-Vorschau wird nicht behauptet. Die Fernkulisse besitzt die tatsächlich generierte Auflösung von 1774 × 887, die Würfelflächen jeweils 768 × 768. Neue Kartengeometrie durch einen frischen Start von TNT03B laden; geprüft wurde Speichern/Laden innerhalb dieses neuen Stands.

## Paket und Wiederholung

Geprüftes lokales `tutnt.pk3`: 144,295,253 Bytes, SHA-256 `e9799ad9f2ca2d6fc4f8180e3f67c1d0504bd7265ee856be36b63fd7011d2834`. Das lokale Paket enthält auch die zur Buildzeit vorhandenen sonstigen Projektänderungen; diese werden nicht durch den Caldera-Commit veröffentlicht.

Strukturvergleich:

```text
python tools/test_caldera_structure.py --baseline-ref cff276776215000b367691ac30d1fcbd0ac1cf06
```

Engineprüfung mit konfigurierten `UTNT_ENGINE` und `UTNT_IWAD`:

```text
python tools/test_caldera_runtime.py --mod tutnt.pk3
```

Assetbau: `python tools/build_caldera_sky.py` (Pillow und NumPy). Die bearbeitbare Map bleibt `tutnt/maps/tnt03b.wad`; der Assetbau verändert ihre Geometrie nicht. Original-Mockup, Herkunft und vollständige verwendete Generierungsprompts stehen unter `tools/artwork/caldera`.

## Cloud motion update - 2026-09-08

TNT01 now animates both cloud projections at exactly four times the original rates.
TNT03B has a slowly rotating polar cloud wall with a calm, softly blended eye.
The low panorama and mountains remain stationary; no map file is part of this update.
Both maps passed OpenGL and Vulkan runtime checks, including save/load.
The annular image comparison measured about 2.1 degrees of TNT03B cloud rotation
over five seconds. Rebuild checks covered all 26 generated sky resources.
Evidence: `tools/validation/sky-motion-2026-09-08`. Repeat with
`python tools/test_sky_motion.py --engine <uzdoom.exe> --iwad <doom2.wad>`.
