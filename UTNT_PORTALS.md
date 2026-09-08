# Höllenschlund-Portale

Die Portalwände zeigen einen asymmetrischen schwarzen Spalt zwischen zerrissenen
blutroten Rauchfalten und einzelnen glühenden Adern. Gegenläufige Verformungen
bewegen die Schichten unabhängig voneinander. Ein flackernder Energiesaum hält
die Öffnung im Rahmen. `PortalDecoration_128` und `_192` ziehen Glut und
Rauchfäden auf beschleunigten, gekrümmten Bahnen zur Öffnung. Bis zu zwei lokale
rote Lichter beleuchten den Rahmen; ein leises Dröhnen begleitet den Effekt.

## Material und Zuordnung

- Drei Tiefenschichten mit blickabhängiger Parallaxe. Die Tiefe entsteht im
  Wandshader; es handelt sich um kein geometrisches Sichtportal.
- Eine eigens gestaltete Höllenstruktur liefert die unregelmäßigen Falten.
  Eine nahtlose Strömungsdaten-Textur steuert ihre Verformung. Der Shader leitet
  die Oberflächennormale aus denselben Falten ab, sodass das Relief der sichtbaren
  Struktur folgt. Die alte separate Normalmap wird nicht mehr benötigt.
- Beim Kartenladen ersetzt `UTNTPortalMaterials` ausschließlich mittlere
  Wandtexturen `QTELEPT`/`QTELEPOR` an Öffnungen ab 48 × 48 Einheiten durch
  `UPORTAL` und passt die Texturskalierung an die jeweilige Wand an.
  Benachbarte kollineare Segmente, einschließlich der vier Einheiten schmalen
  Verbindungsstreifen, erhalten gemeinsame UV-Koordinaten über die gesamte
  Öffnung. Boden-/Deckentexturen und obere/untere Wandtexturen bleiben
  erhalten. Keine Karten-WADs, Geometrie, Specials, TIDs oder ACS geändert.
- Das bisherige 256 × 256 Basisbild bleibt als statische Editor-/Software-
  Darstellung erhalten. Die neue Darstellung benötigt den Hardware-Renderer.
- DECORATE-Namen, Editor-Nummern 31000/31001 und Active/Inactive-Zustände bleiben
  kompatibel. Das alte ACS-Skript 777 bleibt für externe Aufrufer vorhanden.

## Kampagnenweite Abdeckung

117 Wandflächen in ENDMAP01, TNT03B, TNT04A, TNT04B, TNT04C und TNT04CN
verwenden die neue Darstellung. Das umfasst die segmentierten Spitzbogenportale
und kleinere bisher undekorierte Portalöffnungen. Obertexturen mit QTELEPOR sind
in den vorliegenden Karten verdeckte Belegungen ohne sichtbare obere Wandfläche;
sie werden ebenso wie die andersartigen Boden-Teleporter unverändert belassen.

Fehlt ein gesetzter PortalDecoration-Actor, ergänzt das System rein lokale
Effektquellen. Gegenüberliegende Seiten emittieren nur zur lokalen Kamera hin.
Gesetzte Dekorationen und deren ACS-Schalter haben Vorrang. Gespeicherte
Öffnungsgeometrie stellt lokale Quellen nach Save/Load wieder her; zusätzliche
Gameplay-Actors, TIDs oder Zufallszahlen werden nicht angelegt.

`tools/audit_portals.py --out audit.json` inventarisiert alle 14 Karten.
`tools/test_portal_coverage.py --mod tutnt.pk3` prüft die Abdeckung sowie
automatische Effekte und Save/Load. Belege: `tools/validation/portal-all-2026-09-09/`.

## Begrenzung und Lebenszyklus

Emitter, Partikel, Licht und Audio sind lokal. Maximal 32 Emitter und maximal
29 kurzlebige Partikel pro Emitter; zusätzlich gilt das gemeinsame Ambient-
Budget. Keine Projektile, Ziel-Actors oder Spielzufallszahlen für den Effekt.
Qualität 0 bzw. LOD 0 deaktiviert die Dekoration; reduzierte Effekte verringern
Partikelzahl und Lichtpuls. Die Portalfläche bleibt sichtbar.
Deaktivierung, Entfernung und Reichweitenwechsel räumen lokale Objekte auf.
Aktive Effekte werden nach Save/Load neu aufgebaut.

## Prüfung

Die erste Fassung wurde mit beiden Größen, unabhängiger Aktivierung,
Deaktivierung, FX aus, Reduced FX und Save/Load in OpenGL und Vulkan geprüft.
Zwei lokale Koop-Peers mit unterschiedlicher Effektqualität bestanden ebenfalls.
Diese Actor-Logik bleibt in der visuellen Überarbeitung unverändert.
Die damaligen Belege liegen unter `tools/validation/portal-2026-09-08/`.

Aktuelle Material- und Spielbildprüfungen stehen getrennt unter
`tools/validation/portal-2026-09-09/`; dort beschreibt `RESULTS.md` die tatsächlich
ausgeführten Prüfungen der neuen Fassung. UZDoom 5.0.1, OpenGL und Vulkan.
Die Bildherkunft ist in `tools/artwork/portal/ARTWORK.md` dokumentiert.

Wiederholbar mit `tools/test_portal.py --mod tutnt-portals-v2.pk3 --campaign`
bei gesetztem `UTNT_ENGINE` und `UTNT_IWAD`. Keine vollständige Kampagnen- oder
WAN-Abnahme, keine allgemeine FPS-Garantie. Das freigegebene KI-Mockup ist das
Gestaltungsziel; die Belegbilder stammen aus dem tatsächlichen Spiel.
