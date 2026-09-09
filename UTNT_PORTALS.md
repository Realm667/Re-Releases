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

## Aktivierungsreparatur und Sog im Nahbereich

Die gesetzten PortalDecoration_128/192 können mit Dormant starten. Der native
SwitchableDecoration-Aktivierungsaufruf wechselt lediglich den Zustand; das
Dormant-Flag blieb bisher gesetzt und sperrte die neue Partikelroutine trotz
Aktivierung durch ACS 176. Die gemeinsame Portal-Basisklasse synchronisiert nun
Zustand, PortalActive und Dormant bei ausdrücklichen Schaltaufrufen.
Die ursprünglichen Editor-Nummern und Kartentrigger bleiben erhalten.

Ein größerer, durch einen Sprite-Shader gezeichneter heißer Glutkern macht die
Partikel auch bei normalen Spielabständen erkennbar. Glut und einzelne Nebelfäden
beschleunigen aus 64–144 Einheiten Entfernung in einen engeren Bereich der
Portalöffnung. Emissionsbudget und Lebensdauer bleiben begrenzt wie zuvor.

Der lokale Szenen-Shader UTNTPortalSuction setzt weich innerhalb von etwa 384
Mapeinheiten vor der Öffnung ein: 384 = aus, 320 = leichter Sog, 192 = halbe und
64 = starke Intensität. Die Stärke steigt beim Annähern stetig an. Gebrochene Glutfäden und eine kurze gerichtete Verzerrung
laufen auf einen Punkt in der sichtbaren Portalöffnung zu. HUD-Texte werden erst
danach gezeichnet. Es gibt keine Änderung an Bewegung oder Spielphysik.

Die Sichtprüfung ignoriert unsichtbare zweiseitige Triggergrenzen, berücksichtigt
aber geschlossene Wandgeometrie. Wegsehen, Rückseite, große seitliche Abstände,
deaktivierte Quellen, FX-Qualität 0, LOD 0, Reduced FX und ausgeschaltete
Shader-Overlays deaktivieren den Szenen-Shader. Die Werte stammen aus der lokalen
Renderkamera; mehrere Portale stapeln die Stärke nicht aufeinander.

Prüfung: tools/test_portal_suction.py --mod tutnt.pk3 --campaign.
Die neuen Testkarten starten beide Spawner ausdrücklich dormant und prüfen
Aktivierung, Partikel, Abstände von 512 bis 24 Einheiten, den stetigen
384-Einheiten-Verlauf, Sichtschutz, Abschalten
und Save/Load. Die Kampagnenprüfung führt den originalen ACS-176-Aufruf mit
einem Spieler als Activator in TNT03B, TNT04A und TNT04B aus.
Belege: tools/validation/portal-suction-2026-09-09/.

## Direkte Annäherung ohne Kartentrigger

Die erste Aktivierungsprüfung führte ACS 176 ausdrücklich aus und übersah den
Zugang per Map-Wechsel und Noclip/Fly. In TNT03B blieb ein direkt angeflogener
Spawner dadurch dormant; weder Partikel noch Nahbereichs-Shader liefen.

An eine erkannte Portal-Wand gebundene Dekorationen verwenden jetzt lokale
Entfernung und Blickseite statt des ursprünglichen Startzustands als Freigabe.
Die regelmäßige Zuordnung zu den gespeicherten Öffnungen gilt auch nach
Save/Load. ACS 176 bestätigt für diese Portal-Klassen nur noch die lokale
Sichtbarkeitsverwaltung. Seine alten Raumgrenzen können die Effekte nicht
dauerhaft ausschalten. Nicht-Portal-Actors behalten die bisherigen ACS-Aufrufe.

Eine ausdrückliche Activate/Deactivate-Anweisung bleibt wirksam. Ein separates
gespeichertes ExplicitOff-Flag unterscheidet sie vom automatischen Dormant-Aufruf
der Engine beim Spawn. Auch ein späterer ACS-Sichtbarkeitshinweis überschreibt
diese manuelle Abschaltung nicht. Qualitäts-, LOD- und Shader-Einstellungen
sowie Budgets bleiben erhalten; es werden keine zusätzlichen Gameplay-Actors
oder Zufallszahlen verwendet.

tools/test_portal_approach.py testet eine direkte Ankunft in TNT03B mit der
normalen Spielerkamera, ohne Aktivierung aufzurufen. Zusätzlich prüft es beide
ACS-Sichtbarkeitshinweise, manuelles Aus/Ein, Qualität 0 und gespeicherte aktive
sowie abgeschaltete Zustände. Belege: tools/validation/portal-approach-2026-09-09/.

Die gemeinsame ACS-Bibliothek wurde angepasst. UZDoom verweigert ältere
Spielstände mit der vorherigen Bibliotheksgröße; für diesen Build die Karte
frisch starten. Save/Load innerhalb der neuen Fassung ist geprüft.

## Vergrößerter Partikel-Sogbereich

Der Ansaugbereich entspricht der größeren räumlichen Ausdehnung aus der grünen
Nutzermarkierung: Startpunkte verteilen sich unabhängig vom Ziel über die
1,6-fache Portalbreite und 96 Prozent der Öffnungshöhe. Vor einem 192er-Portal
beginnen sie 128 bis 320 Mapeinheiten vor der Fläche (vorher 64 bis 144).
Bei 128er-Portalen beträgt die Tiefe 96 bis 240 Einheiten. Automatisch erkannte
Portale nutzen dieselbe Skalierung mit begrenzter Tiefe. Breitere Kurven ziehen
die Partikel zum bisherigen, engeren Zielbereich in der Portalfläche.

Partikelrate, Lebensdauer, Größen und Effektbudgets bleiben unverändert.
Der Nahbereichs-Bildschirmshader setzt weiterhin innerhalb von 128 Einheiten
ein. Die Portaltextur und die Architektur werden nicht vergrößert.
