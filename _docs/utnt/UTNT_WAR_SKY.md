# TNT04A: gemeinsame Caldera und entfernter Kometenhagel

TNT04A verwendet dieselbe aktuelle Caldera wie TNT03B: identisches Panorama,
identische sechs Hintergrundbilder, Belichtung, Wolkenlagen und Rotationsraten.
Die gesamte isolierte Bergkulisse wurde aus TNT03B übernommen; lediglich die
lokalen Vertex-, Sidedef- und Sektorindizes sind an TNT04A angepasst.

Zusätzlich ziehen ausschließlich in TNT04A sieben zeitversetzte Kometenbahnen
über den Himmel. Je nach Blickrichtung und Phase sind mehrere gleichzeitig
sichtbar. Helle gelbweiße Köpfe, orange glühende Schweife und eine kleine
flackernde Auslenkung lassen sie brennen. Die Köpfe sinken mit ungefähr
1,52 bis 2,29 Grad Höhenwinkel pro Sekunde; einzelne Flüge bleiben mehrere
zehn Sekunden sichtbar. Schweife zeigen entgegen der Flugrichtung. Ein- und
Ausblenden vermeiden abrupte Starts und verschwinden vor dem tiefen Horizont.

Die Kometen werden im sphärisch projizierten Sky-Material dargestellt. Sie
überqueren Würfelflächen und den Panoramaabschluss ohne einen separaten
Bildschirmoverlay. Die Berggeometrie verdeckt sie wie den übrigen Himmel.
Sie erzeugen keine Actors, Schäden, Geräusche oder Änderungen am Spielzustand.

## Erhaltene Karte

- Übernommen: 3.456 Vertices, 9.984 Linedefs, 19.776 Sidedefs und 6.529 Sektoren.
- Alle ursprünglichen 3.268 Vertices, 3.956 Linedefs, 7.268 Sidedefs und
  893 Sektoren von TNT04A unverändert.
- Alle 495 Things bleiben erhalten. Nur der normale SkyViewpoint wird nach
  (18000, 18000, Welt-Z 0) versetzt. Keine zusätzliche Skyboxkamera.
- SCRIPTS, BEHAVIOR und übrige Nicht-Geometrie-Lumps unverändert.
- ZDBSP hat ZNODES neu aufgebaut. Keine Verbindung zwischen Kulisse und Spielkarte.
- TNT03B und dessen eigene Sky-Zuweisung werden nicht verändert.

## Bearbeiten und wiederholen

`tools/build_caldera_sky.py` erzeugt nun automatisch auch die TNT04A-Variante,
damit spätere Änderungen am gemeinsamen Himmel beide Karten erreichen.
`tools/build_war_sky.py` kann die Kriegsversion auch separat aus den aktuellen
Caldera-Shadern erzeugen. Die Kometenparameter stehen in `tools/war-comets.glsl`.
Die sechs UWR-Texturen referenzieren dieselben UCH-Bilder; neue Rasterbilder
oder globale Ersetzungen werden nicht angelegt.

`tools/copy_caldera_to_war.py` dokumentiert und prüft die einmalige Übernahme.
Es benötigt eine TNT04A ohne die neue Kulisse, die aktuelle TNT03B und ZDBSP;
vorhandene Kulissen werden nicht versehentlich ein zweites Mal angehängt.

Laufzeitprüfung: `python tools/test_war_sky.py --engine <uzdoom.exe>
--iwad <doom2.wad> --mod <tutnt.pk3> --work <testordner>`.
Optional erlaubt `--resume <spielstand>` einen vorhandenen Spielstand hinter
dem Intro. Dieser muss mit derselben Ressourcenquelle und demselben Test-Add-on
erstellt worden sein. Der Testordner muss existieren.

## Prüfstand und Grenzen

Nachweise unter `tools/validation/war-sky-2026-09-08`: vollständiger
Strukturvergleich, bytegleiche Reproduktion aller 23 generierten Ressourcen,
Engineprotokolle und Bildvergleiche. Alle 14 ACS-Module des isolierten Pakets
wurden unverändert reproduziert; UZDoom 5.0.1 akzeptiert das gebaute PK3.
OpenGL prüft den frischen Kartenstart einschließlich vollständigem Intro,
Vulkan setzt den OpenGL-Spielstand hinter dem Intro fort. Beide prüfen die
Sky-Zuweisung, Skyboxkamera und Speichern/Laden. Der Vergleich über fünf
Sekunden belegt die Bewegung; die sechs Blickrichtungen wurden visuell geprüft.

Der isolierte Teststand besteht aus Commit
`ccf15f4acf3b8c9aca362c52af0b4474a6a5e4d7` plus dieser Skyboxänderung.
Der erste Gesamtbuild wurde durch parallel bearbeitete Portal-/UI-Skripte
unterbrochen. Nach deren Korrektur akzeptiert UZDoom den lokalen Arbeitsstand
und das inzwischen parallel erstellte regulaere `tutnt.pk3` direkt. Alle
Skyboxressourcen und die neue TNT04A im Hauptpaket wurden bytegenau mit den
geprueften Quellen verglichen. Der eigene Austauschversuch traf auf eine
Dateisperre; ein weiteres Ersetzen des bereits aktuellen Pakets war unnoetig.
Fremde lokale Aenderungen werden nicht mit diesem Commit veroeffentlicht.

TNT04A frisch starten, damit die neue Kartengeometrie geladen wird.
Geprüft wurde Speichern/Laden innerhalb des neuen Stands, keine Migration
alter Spielstände oder vollständige Kampagnen-/Netzwerkabnahme.

## TNT04A-Intro ueberspringen - 2026-09-09

Ein neuer Druck auf die belegte Benutzen-Taste beendet das Intro. Der Hinweis
steht unten im Bild. Eine beim Karteneintritt gehaltene Taste wird ignoriert;
der Skip wird nach einer kurzen Eingangsfrist von 15 Tics angenommen.
Im Koop beendet ein Mitspieler das gemeinsame Intro fuer alle.

Normaler Abschluss und Skip verwenden denselben einmaligen Abschluss:
Intro-Bilder und Sperren werden entfernt, Spieler und HUD freigegeben,
Schlacht, Musik, anschliessende Sprachausgabe und Missionshinweise gestartet.
Beim Skip wird ausstehende Intro-Erzaehlung verworfen und durch die originale
Nach-Intro-Zeile ersetzt. Der gemeinsame Kartenhinweis wartet jetzt auf den
tatsaechlichen Abschluss statt immer 1860 Tics zu warten.

Alle Geometrie- und Node-Lumps sind bytegleich. Frueher Skip, gehaltene Taste,
Laden eines laufenden Intros, Save/Load nach Skip, normaler Ablauf und
Gast-Skip mit zwei echten Koop-Peers bestehen 186 Assertions in UZDoom 5.0.1.
Nachweise: `tools/validation/intro-skip-2026-09-09`. Wiederholung mit
`tools/test_tnt04a_intro.py` und `tools/test_tnt04a_intro_coop.py`; Engine
und IWAD ueber `UTNT_ENGINE` / `UTNT_IWAD` oder die jeweiligen CLI-Argumente.
Fuer die neue Skriptfassung TNT04A frisch starten.

## Kometenvariation - 2026-09-09

Die Hauptbahnen behalten ihre Geschwindigkeit, Frequenz und Feuerfarben.
Pro Vorbeiflug variiert der Massstab dezent zwischen 0.72 und 1.34, waehrend
des sichtbaren Flugs bleibt er konstant. Ein deterministisch versetzter
Vorbeiflug je 32 Fluege pro Bahn zerfaellt sanft in eine kleine Dreiergruppe:
Hauptkomet plus zwei kleinere, langsam auseinanderdriftende Fragmente.
Langfristig ergibt sich etwa eine solche Gruppe alle drei Minuten ueber den
gesamten Himmel; nicht jede davon liegt im sichtbaren Bildausschnitt.

Die Fragmente erhalten denselben Flammenstil in kleinerem Massstab; sie
blenden weich ein und erzeugen keinen hellen Explosionsblitz. Panorama,
Terrain, Wolkenbewegung, Karten, Intro und Gameplay bleiben unveraendert.
Die Skybox-Geometrie und die sechs gemeinsam genutzten Caldera-Basisshader
wurden gegen den Ausgangszustand per SHA-256 geprueft.

Der Stil ist auch fuer TNT04B vorgemerkt. Dessen Originalbefund und noch
abzunehmender Entwurf stehen in tutnt/.codex/notes/TNT04B_SKY_CONCEPT.md. TNT04B wird erst nach
Konzept- und anschliessender Mockupabnahme integriert.

Pruefung: tools/test_war_comet_variation.py rendert normale Groessen,
fruehe/spaete Fragmentierung mit festem Testzeitpunkt und echte laufende
Bewegung in UZDoom 5.0.1. Die festen Zeiten werden ausschliesslich in einem
Test-Addon eingesetzt; das Spiel nutzt weiter den normalen Shader-Timer.
OpenGL-/Vulkan-Aufnahmen und Laufzeitlogs liegen unter
tools/validation/comet-variation-2026-09-09. Die Aufnahmen erfordern eine
visuelle Beurteilung, die automatischen Assertions pruefen Kamera und
Skybox-Zuordnung. Keine vollstaendige Kampagnenabnahme fuer diese Dekoration.
