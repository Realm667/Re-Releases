# TNT04B: Originalbefund und Konzept zur Abnahme

Stand: 2026-09-09. Konzept und Mockup wurden abgenommen; die Umsetzung ist
in UTNT_ASH_SKY.md dokumentiert. Die vereinbarte Reihenfolge war:
Original ansehen -> Konzeptabnahme -> Mockup -> Mockupabnahme -> Integration.

## Original

TNT04B (Beyond the Dark Portal) besitzt eine eigene, noch unveraenderte
Skybox-Geometrie. Vergleich mit dem Originalstand
0269888c4c7f65778e343408461bdb47c5c732f9: alle Vertices, Linien, Seiten,
Sektoren und Things stimmen ueberein. Die Skripte enthalten inzwischen
Modernisierungen; die Referenzaufnahmen zeigen die Originalkulisse im aktuellen
Spielstand, keine unveraenderte historische Komplettversion.

Die Engine-Ansichten zeigen eng gestellte, scharfe grauschwarze Felszacken,
eine sehr niedrige, braunschwarze Wolkendecke und zahlreiche orange Feuerkometen
mit deutlich erkennbaren Sprite-Perlen im Schweif. Die Kulisse umschliesst die
dunkle Festungsarchitektur. Die Karte hat bereits Gewitterbeleuchtung und eine
eigene pulsierende Skybox-Beleuchtung. Das sind praegende Bestandteile des Originals.

Default-SkyViewpoint: (-3904,1664), Hoehe 24. Zusaetzliche Viewpoints tragen
TIDs 3,4,5,6,7. Ihre Zuordnung ist bei einer spaeteren Integration separat zu
pruefen und zu erhalten; sie sind kein Auftrag, alle Portalsichten auszutauschen.

Der parallel laufende Task "Entwickle komplexere Skybox Systeme" bearbeitet
zum Zeitpunkt der Abstimmung TNT02s Gewitterhimmel. Dieses Dokument reserviert
die TNT04B-Richtung und den gemeinsamen Kometenstil fuer die weitere Abstimmung.

## Konzept: Schwarze Felsnadeln unter einem Aschesturm

- Eine umlaufende, unregelmaessige Landschaft mit nahen scharfkantigen
  Basaltzacken und zwei bis drei weiter entfernten Gebirgsketten. Zwischenraeume,
  Hoehenunterschiede und sich ueberlagernde Silhouetten erzeugen Tiefe.
- Schwere, tief haengende Wolken in Kohleschwarz, Aschgrau und entsaettigtem
  Braun. Zwei langsam unterschiedlich ziehende Schichten geben dem Himmel
  Bewegung. Der Eindruck bleibt geschlossen, dunkel und bedrohlich.
- Gedampftes rostorangefarbenes Glimmen tief zwischen einzelnen fernen Ketten;
  wenige duenne Rauchfahnen und Dunstbaender verankern die Kulisse in der
  infernalischen Landschaft. Die bestehende Festung bleibt visuell fuehrend.
- Dieselben langsamen Feuerkometen wie in TNT04A, einschliesslich der unten
  festgehaltenen Groessenvariation und seltenen Fragmentgruppen. Bei Integration
  alte sichtbare Skybox-Kometen gezielt ersetzen, damit sich beide Effekte nicht
  addieren. Gameplay-Projektile und andere Karten bleiben erhalten.
- Bestehende Gewitterimpulse mit der neuen Wolkendecke abstimmen. Die normale
  Szenenhelligkeit und das Zusammenspiel mit dunklen Mauern bleiben am Original
  orientiert; Effekte duerfen die Karte nicht dauerhaft aufhellen.

Das spaetere Mockup soll nach Konzeptabnahme eine typische Aussenansicht mit
erhaltener Festungsarchitektur zeigen, dazu eine Rundumsicht der vorgeschlagenen
Fernlandschaft. Erst nach dessen Abnahme folgen Artwork, Skybox-Geometrie,
Materialien, Kamera-Zuordnung und Laufzeittests.

## Fuer TNT04B vorgemerkter Kometenstil

Gemeinsame Quelle: tools/war-comets.glsl. Aktuell nur fuer TNT04A eingebunden.
Sieben langsam fallende Hauptbahnen, unveraenderte Farben und Geschwindigkeiten.
Groesse pro Vorbeiflug konstant zwischen 72 und 134 Prozent des bisherigen
Massstabs. Bei einem von 32 Vorbeifluegen pro Bahn entstehen sanft zwei kleine
Fragmente (52 und 40 Prozent der Hauptkometengroesse), die auseinanderdriften.
Die Ereignisse sind zwischen Bahnen und Bloecken versetzt; im langfristigen
Mittel etwa eine Gruppe je drei Minuten. Sichtbarkeit haengt von Blickrichtung
und Gelaende ab. Dekoration ohne Schaden, Sound oder Gameplay-Zufallsverbrauch.

Der vorgemerkte Stil ist jetzt auch in TNT04B eingebunden, aus derselben Quelle wie TNT04A.
