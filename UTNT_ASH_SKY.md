# TNT04B: freigegebener Aschehimmel

## Umsetzung

Die neue Kulisse folgt dem abgenommenen Mockup: schwarze Basaltzacken,
mehrere in Aschedunst gestaffelte Gebirgsketten, schwere braunschwarze Wolken
und punktuelle Glut in fernen Tälern. Zwei unterschiedliche Panoramaabschnitte
umgeben die Karte. Davor stehen zwei geschlossene räumliche Felszüge mit
256 Winkelschritten und 15 radialen Bändern. Ihr niedriger Vordergrund
lässt die detaillierten Fernketten sichtbar.

Der alte Default-SkyViewpoint wurde von (-3904,1664) nach (18000,18000)
verlegt; der Blick liegt auf Welt-Z 0 über dem Boden bei -640. Die 7169
zusätzlichen Sektoren sind vollständig vom Spielbereich getrennt. Die
vorhandenen fünf zusätzlichen Kameras (TIDs 3 bis 7) bleiben unverändert.
96 alte Skybox-Kometenspawner wurden an ihren bisherigen Positionen mit
unverändertem TID und Thing-Index in inaktive MapSpots umgewandelt.

TNT04A und TNT04B verwenden bytegleich tools/war-comets.glsl: sieben langsam
fallende Hauptbahnen, Größen von 72 bis 134 Prozent, ein fragmentierender
Vorbeiflug je 32 Flüge pro Bahn. Dabei trennen sich zwei kleinere Fragmente
sanft vom Hauptkometen. Keine neuen Gameplay-Akteure, Sounds oder Zufallswerte.
Die Hintergrundgrafiken enthalten keine fest eingezeichneten Kometen.

## Wolken und Gewitter

Die Felslandschaften werden vor separat bewegten Wolken freigestellt. Zwei
langsame Windrichtungen überlagern sich. Eine planare Projektion über Kopf
verhindert eine eingeschnürte Polstelle. Die Kugelrichtung ist über Würfelkanten
hinweg kontinuierlich; die beiden Landschaftshälften gehen weich ineinander über.

UTNTAshSkyHandler liest ausschließlich den Lichtwert des unveränderten
Eingangssektors 0 (Tag 3, Grundlicht 128) und folgt damit dem originalen
ACS-Gewitter. Neun Sky-Zustände verwenden dieselben sechs Shader und dieselbe
Uhr; sie erzeugen dezente Wolkenaufhellung und etwas Licht auf den fernen Felsen.
Die vorhandenen Gewitterzeiten, Geräusche, Raumbeleuchtungen, ACS-Skripte,
Portale, Gegner und Spielabläufe bleiben erhalten. Der Handler arbeitet nur
in TNT04B. Die Shader in TNT04A wurden für diese Integration nicht geändert.

## Quellen und Reproduktion

- tools/artwork/ash: freigegebene Mockups, Imagegen-Prompts und Herkunft.
- tools/build_ash_sky.py: sechs Fallback-Bilder, Materialien und Sky-Zustände.
- tools/ash-material.glsl: Landschaft, Wolken und Gewitterbeleuchtung.
- tools/build_war_sky.py: regeneriert bei vorhandenem Asche-Artwork beide
  Kriegshimmel aus der gemeinsamen Kometenquelle.
- tools/build_ash_terrain.py: baut die isolierte Geometrie aus einer TNT04B
  ohne diese Erweiterung; Eingabekarte wird nicht überschrieben.
- tools/test_ash_structure.py: Vergleich mit der Karte vor der Integration.
- tools/test_ash_sky.py: echte Renderer-, Bewegungs-, Save/Load- und Kartenwechseltests.

Engine und IWAD werden über UTNT_ENGINE / UTNT_IWAD oder CLI-Argumente gesetzt.
Der Standard-TNT04B-Kometenstil benötigt wie TNT04A einen Hardware-Renderer.
Die CPU-Fallback-Flächen stellen die Landschaft auch ohne Materialeffekte dar.

## Prüfung

Strukturvergleich: alle ursprünglichen Vertices, Linien, Seiten und Sektoren
unverändert; alle ACS- und sonstigen Map-Lumps bytegleich. Kameras und Things
bleiben bis auf die ausdrücklich genannten Skybox-Änderungen erhalten.
Die parallel integrierten 18 QROCK3X8-Felsseiten bleiben vollständig erhalten.
Gemeinsame Dreieckskanten der neuen Landschaft stimmen auf weniger als
0.000001 Karteneinheiten überein. Kein neuer Sektor oder Special greift in
die Spielkarte ein.

Laufzeitnachweise liegen in tools/validation/ash-sky-2026-09-09. Geprüft werden
OpenGL und Vulkan, Außenansichten, vier Richtungen, Würfelübergänge, Zenit,
eine zusätzliche Kamerakulisse, natürliche Gewitterphasen, laufende Wolken,
Speichern/Laden und anschließender Wechsel nach TNT04A. Die automatische
Prüfung ergänzt die visuelle Sichtung; sie ist keine vollständige Kampagnen-
oder Netzwerkabnahme. Zum Testen TNT04B frisch starten: ältere Spielstände
enthalten noch die vorherige Kartengeometrie.
