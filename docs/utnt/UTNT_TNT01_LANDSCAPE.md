# TNT01: zusammenhängendes Außengelände

Die erste Überarbeitung ergänzte einzelne kleine Formationen. Diese zweite Fassung bearbeitet die großen zusammenhängenden ROCK-/GRASS-Flächen: längere Felskanten werden unterteilt und gekrümmt, Terrassen erhalten geneigte Ränder, und die Grasflächen gehen in gewellte Böden und ansteigende Felsfüße über.

## Umfang

- 785 bestehende lange Linedefs unterteilt, in der Regel in Abschnitte von höchstens 48 Karteneinheiten.
- 160 Felsverläufe mit zusätzlichen unregelmäßigen Konturpunkten; 83 bestehende natürliche Ecken abgerundet.
- Sechs große Grasregionen einschließlich der 780 Dreiecke aus der ersten Fassung als zusammenhängendes Höhenfeld neu modelliert.
- 48 angrenzende Felsterrassen mit abgeschrägten Rändern und sanft gewölbten Oberseiten.
- 8.711 Geländedreiecke insgesamt. 7.877 zusätzliche Sektoren gegenüber der ersten Fassung; TNT01 enthält nun 12.399 Sektoren und 33.033 Linedefs.
- Graswellen und Böschungen reichen von rund 21 Einheiten unter bis 96 Einheiten über die alte Bodenhöhe. Steile Wandfüße sind nicht durchgehend begehbar; sieben flachere Übergänge halten das zusammenhängende Wegnetz offen.

Architektur, auslösende Linien, Türen, Flüssigkeitssektoren und andere nicht ausgewählte Sektoren bleiben erhalten. Alle 2.648 Things, ACS-Lumps und bestehenden Wandmaterialien einschließlich der X8-Varianten bleiben bestehen. Waagerechte Texturversätze werden beim Teilen einer Wand fortgeführt. Die alten Sektornummern bleiben belegt; zusätzliche Dreiecke werden angehängt. ZDBSP baut die erweiterten GL-Nodes neu auf.

## Prüfung

`tools/validation/tnt01-landscape-2026-09-09` enthält Manifest, Strukturbericht, Laufzeitprotokolle und Vergleichsbilder.

Die Strukturprüfung vergleicht Originaleigenschaften und Aktionslinien, prüft neue Linien auf Kreuzungen und kontrolliert die normalisierten Bodenebenen. 10.245 innere Dreieckskanten schließen ohne Lücken; die größte berechnete Höhendifferenz beträgt rund 1,1e-10 Einheiten. Ursprünglich ebene Übergänge erhalten keine neuen Stufen. Die großen begehbaren Komponenten stimmen auf allen drei Außenhöhen weiterhin eindeutig mit den Ausgangsflächen überein. Dabei werden Steigungen über 0,7 ausgeschlossen und die Flächen für einen Spielerradius von 16 verkleinert. Diese geometrische Auswertung berücksichtigt keine Actor-Kollision.

UZDoom 5.0.1 besteht 24 Assertions: Vulkan/Marine, OpenGL/Scout und Vulkan/Commando, jeweils vor und nach Speichern/Laden. Alle 8.711 Dreiecksschwerpunkte haben die erwartete Bodenhöhe; der maximale Laufzeitfehler beträgt rund 1,2e-8 Einheiten. Drei schmale koplanare Teilflächen werden beim BSP-Zugriff einem gleichwertigen Nachbardreieck zugeordnet. Der Test erlaubt das nur bei gleichem ursprünglichem Elternsektor und vollständig identischen Sektoreigenschaften.

Die sieben Geländeübergänge werden mit 506 kleinen Kollisionsschritten pro Prüfung in beiden Richtungen durchlaufen. Spieler-, Wand- und Bodenkollision bleiben aktiv. Ein vorhandener großer Baum steht auf einem dieser Testpfade; deshalb deaktiviert die **separate Test-Erweiterung** die Solid-Eigenschaft vorhandener BigTree-Actors kurz während der Messung und stellt sie unmittelbar wieder her. Die ausgelieferte Karte ändert keine Actors. Der Test ist damit eine Prüfung der veränderten Terrainkollision, keine vollständige Abnahme aller Gegner- und Dekorationskollisionen.

Die Kameravergleiche zeigen Haupttal, Felsfüße, Felsterrassen und erhöhtes Außengelände. Eine vollständige Kampagnen-, Koop-, Sprungshortcut- oder Performanceabnahme ist nicht enthalten. Die höhere Geometriekomplexität ist beabsichtigt.

## Reproduktion

Benötigt werden Python 3.12+, Shapely 2.1.x mit GEOS 3.10+ und ZDBSP. Die Skripte verwenden die vorhandenen Hilfsfunktionen in `tools/build_tnt01_organic.py` und `tools/build_utnt.py`.

Ausgangspunkt ist die erste TNT01-Fassung mit 4.522 Sektoren und 21.320 Linedefs. Der geprüfte Ausgangs-WAD hat SHA256 `52324b6ba45be6954d86092341c68f2614be949e2edd87fe7dc7513869ef8245` und ist beispielsweise in Commit `a03bf7ffd0affe8441f0039050345e780d4b3e7e` enthalten. Den WAD binär aus Git exportieren; die Ausgabe des Generators muss einen anderen Dateipfad bekommen.

```text
python tools/build_tnt01_landscape.py --source before.wad --output candidate.wad --zdbsp <zdbsp.exe> --v1-manifest tools/validation/tnt01-organic-2026-09-09/build.json --report-path build.json --routes tools/validation/tnt01-landscape-2026-09-09/routes.json
python tools/test_tnt01_landscape.py --before before.wad --after candidate.wad --manifest build.json --output structure.json
python tools/test_tnt01_landscape_runtime.py --work <Testordner> --mapfile candidate.wad --manifest build.json --mod <tutnt.pk3> --engine <uzdoom.exe> --iwad <DOOM2.WAD> --renderer 1 --playerclass Marine
```

Der finale WAD hat SHA256 `189513d084c5ba80b72ba9a319ce02bc959f5ddf81a399d0ab29c20caaad2568`. Derselbe Ausgangsstand, dieselben Routen und dieselbe ZDBSP-Version ergeben dieselbe Datei.

Zum Spielen das aktualisierte `tutnt.pk3` laden und TNT01 frisch starten. Ein alter Spielstand enthält weiterhin seine gespeicherte Kartenstruktur.
