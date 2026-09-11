# ENDMAP: Quake-Reliquiar

Umsetzung der am 10.09.2026 freigegebenen Variante 01, einschließlich der anschließenden Layout- und Kamerakorrekturen.
Kompakte Bronzetafeln erscheinen links unten vor der laufenden ENDMAP-Kampfszene.
Die bereits adaptierte TNT01-Skybox bleibt erhalten. Es gibt keine großflächige
Abdunklung des Kampfes; lediglich die Rahmenflächen sind dunkel. Die Kinobalken
sind auf acht virtuelle Pixel reduziert, auch die Ultrawide-Ränder bleiben offen.

## Gestaltung und Animation

- Namen: 18,5 statt 37 virtuelle Pixel; Beiträge: 10 statt 20, auf dichten
  Tafeln 9 statt 18. Die Namen verwenden UCRBIG, alle Begleittexte Quake-SMALLFONT.
- Standardrahmen: 328 Pixel breit, dichte Tafeln: zwei Spalten mit je 286 Pixeln.
  Die Höhe beträgt mindestens 74 Pixel und wächst mit dem tatsächlichen Textumbruch.
  Nach dem letzten Textbereich bleiben 16 Pixel Innenabstand, auch bei mehrzeiligen
  Namen und Beiträgen; die Übersetzungen werden vor der Bemessung geladen.
  Ausgangsposition: x=44, y=434 / 516 / 598 im virtuellen 1280 × 720-Bildraum.
  Lange Texte oder explizite Namensumbrüche vergrößern die Rahmenhöhe. Die Reihen
  bleiben getrennt und werden bei Bedarf gemeinsam nach oben versetzt.
- Rahmen mit abgeschrägten Kanten, Bronzeverlauf, Nieten, feiner Innenlinie und
  zurückhaltenden Gebrauchsspuren. Remaster verwendet die freigegebene kühlere
  Metallvariante derselben Rahmen.
- Die Tafeln blenden über 0,65 Sekunden ein. Einzelne Blöcke folgen mit dem
  freigegebenen Versatz, einem quadratisch auslaufenden 18-Pixel-Schub von links
  und einem kurzen Lichtakzent. Ausblendung: 0,5 Sekunden. Bewegung und Deckkraft
  entsprechen den Formeln des freigegebenen Mockups.
- Kapiteltafeln liegen oben mittig (530 × 140), mit 29 Pixel hohem Titel.
  Einblendung 0,55 Sekunden, Ausblendung 0,45 Sekunden. Zu Beginn bleiben zunächst
  1,5 Sekunden ohne Credits; vor dem Remaster-Titel liegt eine kurze Pause.

Die Original-Credits umfassen 24 Tafeln mit unverändert 65 Nennungen und knapp
159 Sekunden Laufzeit (vorher 318). Die acht Beta-Tester stehen zusammen in einem
530 Pixel breiten Rahmen mit zwei Spalten; diese Tafel bleibt zwölf Sekunden.
Alle anderen ursprünglichen Standzeiten sind halbiert. Dezimale Sekunden sind zulässig.
Die vorbereitete Remaster-Standardtafel verwendet 6,5 Sekunden.

## Kameraführung und Übergänge

Die kleine Kapitel-/Rubrikzeile steht ohne Hintergrund und Seitenbalken zentriert
über ihrer Boxengruppe. Lange Überschriften werden in zwei zentrierte Zeilen geteilt.

Eine eigene, gespeicherte Kamera führt pro Einstellung eine weiche seitliche Fahrt
von 24 Einheiten, eine Annäherung von zwölf und einen Höhenwechsel von acht Einheiten
über den gesamten Verlauf aus. Dezente Schwenks, Neigungen und ein FOV-Verlauf von
89 auf 86 ergänzen die Bewegung. Smoothstep beschleunigt und bremst die Fahrt.
Die ursprünglichen Kameras bleiben als unveränderte Ausgangspunkte erhalten.

Jeder Wechsel blendet in 23 Tics (rund 0,66 Sekunden) nach Schwarz. Erst dort wechselt
der Blickpunkt. Danach öffnet sich das Bild in 28 Tics (0,8 Sekunden). Das gilt auch
für manuelles Weiter/Zurück und Überspringen; weitere Eingaben während der Blende
werden ignoriert. Die freigegebene Boxenanimation beginnt nach der Eingangsblende.

Der abschließende FPV-Flug verwendet die vorhandenen Wegpunkte 100–110, eine
Hermite-Kurve mit gemeinsamen Tangenten, 321 Stützproben und einen nach Bogenlänge bestimmten Fortschritt.
Nach einer Sekunde Einblendung dauert die Fahrt 20 Sekunden; anschließend bleibt
fünf Sekunden die Schlusskomposition stehen. Im letzten Teil schwenkt der Blick
weich auf den tatsächlichen OrangeSpark_Up mit TID 7 am Kraterboden. Die beiden
letzten Anflugpunkte werden über die nahe Kraterkante angehoben; der Endpunkt liegt
180 Einheiten südlich und 220 über dem Funken. Die Kartendaten bleiben unverändert.

Der Blick verengt sich von FOV 88 auf 64, die Kurvenneigung klingt auf null aus.
Der Funke liegt mittig und die Kamera kommt eine Sekunde vor dem ersten durch
ACS 102 ausgelösten Aufflackern zur Ruhe. Dessen viersekündiges Zeitfenster bleibt
im Bild; während der letzten 1,2 Sekunden blendet es wie bisher nach Schwarz.
Anschließend erscheint „THE END“ nach kurzer Ruhe mit einer zweisekündigen Einblendung.
Fokuspunkt, Kurvenproben und Fortschritt werden mitgespeichert. Fehlt der Funkenaktor,
bleiben die ursprünglichen Wegpunkte und Blickrichtungen als Rückfall erhalten.

ACS 55 behält Musik und Umwelt-Cues: D_NOVER beginnt nach der einsekündigen
Eingangsblende. Die alte MovingCamera wird nicht mehr aktiviert; Position und
Blickrichtung bestimmt ausschließlich das gespeicherte Kamera-Rig. Kampfskripte,
Kartengeometrie, Wegpunkte und die TNT01-Skybox bleiben unverändert.

## Ash & Ember (Mockup 03, 11.09.2026)

Der freigegebene Look kombiniert entsättigte Asche-/Steintöne mit warm erhaltenen
Feuer- und Glutfarben. Eine leichte Schattenaufhellung, sanft komprimierte Lichter,
ein kleiner warmer Lichthof, bis zu 14 Prozent Randabdunklung und feines Korn
halten die Szene lesbar. Die Grundsättigung beträgt 52 Prozent; warme Bereiche
behalten bis zu 98 Prozent ihrer Sättigung.

Die Tiefenunschärfe richtet sich während der Credits auf die Kampfmitte und beim
Schlussflug auf den tatsächlichen Funken am Kraterboden. Die maximale Unschärfe
beträgt zwölf Pixel bei 720 Bildzeilen; im Flug wächst sie sanft von sechs auf
14 Pixel. Ein breiter Schärfebereich lässt den Kampf erkennbar. Der Shader benutzt
32 räumliche Abtastungen mit bilinearer Pixelrekonstruktion und farbunabhängigen
Gewichten. Dadurch bleiben helle Originalpixel nicht als scharfe Spitzen in der
Unschärfe stehen. Der Einstieg des Filters unterhalb von 1,35 Pixeln ist weich.
Es wird keine zeitliche Bildhistorie verwendet.

Der Custom-Postprocess dieser Engine stellt keinen nativen Tiefenpuffer bereit.
`UTNTCreditsLook` rekonstruiert deshalb die Geometrietiefe mit einem 16×9-Raster
(maximal 144 Strahlen pro Spieltic bei unveränderter Projektion). Dies ist eine
Näherung: Sprites und transparente Partikel erhalten die Tiefe ihrer Umgebung,
keine individuelle pixelgenaue Tiefenmaske. Kameraschnitte, geänderte Projektion
und das Laden eines Spielstands initialisieren die Messung neu. Kleine laufende
FOV-Änderungen setzen die Glättung nicht zurück; ein Sprung über fünf Grad schon.

Die Korrektur vom 11.09.2026 interpoliert die Unschärfestärke statt der Tiefenwerte.
Nahe und ferne unscharfe Flächen erzeugen dadurch an ihrer Grenze keine künstliche
Schärfeebene. Pro Spieltic folgt die Maske mit Faktor 0,22 und höchstens 0,06
Stärkenänderung; zwischen den Tics wird interpoliert. Drei 8-Bit-Stärken pro Float
halten die Übertragung kompakt, ohne die früheren groben logarithmischen Tiefensprünge.

Der Verlauf wird in Weltkoordinaten definiert: Nach einem scharfen Kern von
mindestens 48 Einheiten beziehungsweise 15 Prozent der Fokusdistanz wächst die
Unschärfe vor dem Fokus über mindestens 320 Einheiten bzw. 110 Prozent der
Fokusdistanz, dahinter über mindestens 768 Einheiten bzw. 250 Prozent. Damit
ist der Übergang besonders im Nahbereich deutlich länger und weniger abrupt.

`credits/ash-ember.gldefs` registriert genau einen Scene-Pass; seine Definition
liegt bewusst außerhalb der automatisch geladenen GLDEFS-Root-Lumps. Der Pass
läuft vor den zweidimensionalen Tafeln, SMALLFONT-Texten und Schwarzblenden.
Diese bleiben scharf und unverfärbt. Bei „THE END“, Verlassen der ENDMAP oder
einer anderen aktiven Kamera wird der Effekt deaktiviert. Es gibt keine neuen
Menütexte oder Spiel-CVars; `creditlookbaseline` existiert nur im Test-Fixture.

## Original Version und Remaster

Alle vorhandenen Nennungen aus `tutnt/credits/original.txt` gehören zu
**Original Version**. Der bisherige Auftakt zeigt diesen Kapiteltitel; während
der einzelnen Tafeln stehen Kapitel und Kategorie als kleine Zeile über den Rahmen.

`tutnt/credits/remaster.txt` folgt nach dem persönlichen Dank an Graf Zahl
(„DANKE CHRIS!“, Freigabebild 05) und vor Schlussfahrt / „THE END“ (Bild 06).
Der Remaster-Abschnitt samt Kapitelauftakt bleibt unsichtbar, solange keine
Nennungen eingetragen sind. Einträge unter der vorbereiteten P-Zeile ergänzen:

```text
P|standard|1|6.5|Remaster
N|NAME|Beitrag zum Remaster
N|WEITERER NAME|Weiterer Beitrag
```

Sobald mindestens eine echte Nennung vorhanden ist, entsteht automatisch genau
ein viersekündiger Remaster-Auftakt. Drei Namen passen auf eine Standardtafel,
sechs auf eine dichte Tafel; zusätzliche Einträge erzeugen automatisch Folgeseiten.
Eigene Kategorien sind mit weiteren `P|Layout|Kamera|Sekunden|Rubrik`-Zeilen möglich.
Kamera 1 bis 5, Dauer 4 bis 60 Sekunden pro Credit-Tafel. `~` im Namen bleibt ein
expliziter Zeilenumbruch. Die Datei als UTF-8 speichern; für fehlende Glyphen der
Originalschrift ggf. ae/oe/ue verwenden. Neue Texte vor Freigabe im Spiel ansehen.

Danach das PK3 neu bauen und ENDMAP neu betreten. Gespeicherte Spielstände behalten
ihre bereits geladenen Texte. Der ausgelieferte Remaster-Block enthält keine
Testnamen. Reine Textänderungen erfordern keine Änderung der ACS-Logik.

## Bedienung, Spielstände und Koop

Enter, Leertaste, Rechts oder Gamepad-A: nächste Tafel. Links: vorherige Tafel.
Ende: vorhandene Schlussfahrt starten. Im Koop steuert der Host; Kapitel,
Kartenfortschritt und Finale sind synchronisiert. Menü und Konsole behalten ihre
Eingaben. Kapitelzuordnung, Fortschritt und Animationszeit werden gespeichert.
Neue Koop-Spieler und respawnte Spieler bekommen weiterhin die aktive Kamera.

`UTNTCreditsHandler` verwaltet Daten und Ablauf; `UTNTCreditsUI` zeichnet die
Rahmen und Texte. Die ENDMAP-Geometrie bleibt unverändert; ACS 55 übergibt Kameraführung und Blenden an das Rig.
`tools/build_credit_assets.py` erzeugt die nativen Rahmen in doppelter Auflösung
und die private Titelschrift reproduzierbar (Pillow). Die alten Verlaufstexturen
bleiben als unbenutzte Bestandsressourcen erhalten.

## Prüfungen

```text
python tools/test_credits.py --engine PATH/uzdoom.exe --iwad PATH/DOOM2.WAD --out PATH/results --mode visual --renderer 1
```

`--language en|de|es|fr` wählt die Textfassung. `--classic` wählt das schmale Bildformat, `--renderer 0` OpenGL. Weitere Modi:
`regression` für Speichern/Laden und Finale, `animation` für einen Spielstand
mitten in der Einblendung, `remaster` für Kapitel, automatische Folgeseiten und
Kapitel-Spielstand, `finale` für das natürliche Ende, `cinematic` für Blenden-/Flug-Spielstände und kontinuierliche Kamerabewegung,
`spark` für die natürliche Effektsequenz, freie Sicht, zentrierten Schlussblick und
Speichern/Laden während der ruhenden Schlusskomposition. `--mod` kann ein bestimmtes
PK3 wählen. `look` prüft alle fünf Kameraperspektiven, die einmalige
Shader-Registrierung, räumliche Tiefenwerte, gespeicherten Funkenfokus sowie das
Sequenzende. Native Bewegungsprüfungen kontrollieren den fortlaufenden Verlauf
über 30 Kameratics ohne Zoom-Reset und begrenzen abrupte Maskenänderungen; feste
Entfernungsproben sichern den verbreiterten räumlichen Verlauf. Ein pausierter A/B-Pixelvergleich bestätigt die unveränderten
Schriftbereiche und den sichtbaren Effekt auf die Welt. Der Remaster-Test verändert nur eine separate Testdatei im Ausgabeordner.
Zwei echte Koop-Clients prüft `tools/test_credits_coop.py` mit denselben Pfadoptionen.

Ergebnisse und repräsentative Spielansichten stehen unter
`tutnt/.codex/validation/credits-polish`; die Kraterkorrektur unter
`tutnt/.codex/validation/credits-spark`, die Postprocess-Prüfungen unter
`tutnt/.codex/validation/credits-ash-ember`, die Stabilitätskorrektur unter
`tutnt/.codex/validation/credits-dof-stability`. Automatisierte Tests laufen ohne
Ton; sie behaupten kein subjektives Abhören und keinen vollständigen Kampagnenlauf.
Bei einem Versionswechsel ENDMAP neu betreten, um die neue Kapitelstruktur zu laden.
