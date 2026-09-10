# ENDMAP: Quake-Reliquiar

Umsetzung der am 10.09.2026 freigegebenen Variante 01 und ihrer Animation.
Kompakte Bronzetafeln erscheinen links unten vor der laufenden ENDMAP-Kampfszene.
Die bereits adaptierte TNT01-Skybox bleibt erhalten. Es gibt keine großflächige
Abdunklung des Kampfes; lediglich die Rahmenflächen sind dunkel. Die Kinobalken
sind auf acht virtuelle Pixel reduziert, auch die Ultrawide-Ränder bleiben offen.

## Gestaltung und Animation

- Namen: 18,5 statt 37 virtuelle Pixel; Beiträge: 10 statt 20, auf dichten
  Tafeln 9 statt 18. Die Namen verwenden UCRBIG, alle Begleittexte Quake-SMALLFONT.
- Standardrahmen: 328 × 74; dichte Tafeln: zwei Spalten mit je 286 × 74.
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
  2,5 Sekunden ohne Credits; vor dem Remaster-Titel liegt eine kurze Pause.

Die Freigabevorschau war beschleunigt. Die Original-Credits behalten ihre 25 Tafeln,
65 Nennungen und 318 Sekunden Laufzeit vor der bestehenden Schlussfahrt.
Schlussfahrt und „THE END“ bleiben erhalten; auch das Schlussbild verwendet jetzt
die halbierten Textgrößen. Die Musiksequenz D_ENDG / D_NOVER bleibt unverändert.

## Original Version und Remaster

Alle vorhandenen Nennungen aus `tutnt/credits/original.txt` gehören zu
**Original Version**. Der bisherige Auftakt zeigt diesen Kapiteltitel; während
der einzelnen Tafeln stehen Kapitel und Kategorie als kleine Zeile über den Rahmen.

`tutnt/credits/remaster.txt` folgt nach dem persönlichen Dank an Graf Zahl
(„DANKE CHRIS!“, Freigabebild 05) und vor Schlussfahrt / „THE END“ (Bild 06).
Der Remaster-Abschnitt samt Kapitelauftakt bleibt unsichtbar, solange keine
Nennungen eingetragen sind. Einträge unter der vorbereiteten P-Zeile ergänzen:

```text
P|standard|1|13|Remaster
N|NAME|Beitrag zum Remaster
N|WEITERER NAME|Weiterer Beitrag
```

Sobald mindestens eine echte Nennung vorhanden ist, entsteht automatisch genau
ein viersekündiger Remaster-Auftakt. Drei Namen passen auf eine Standardtafel,
sechs auf eine dichte Tafel; zusätzliche Einträge erzeugen automatisch Folgeseiten.
Eigene Kategorien sind mit weiteren `P|Layout|Kamera|Sekunden|Rubrik`-Zeilen möglich.
Kamera 1 bis 5, Dauer 8 bis 60 Sekunden pro Credit-Tafel. `~` im Namen bleibt ein
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
Rahmen und Texte. Diese Änderung verändert keine ENDMAP-Geometrie oder ACS-Skripte.
`tools/build_credit_assets.py` erzeugt die nativen Rahmen in doppelter Auflösung
und die private Titelschrift reproduzierbar (Pillow). Die alten Verlaufstexturen
bleiben als unbenutzte Bestandsressourcen erhalten.

## Prüfungen

```text
python tools/test_credits.py --engine PATH/uzdoom.exe --iwad PATH/DOOM2.WAD --out PATH/results --mode visual --renderer 1
```

`--classic` wählt das schmale Bildformat, `--renderer 0` OpenGL. Weitere Modi:
`regression` für Speichern/Laden und Finale, `animation` für einen Spielstand
mitten in der Einblendung, `remaster` für Kapitel, automatische Folgeseiten und
Kapitel-Spielstand, `finale` für das natürliche Ende. `--mod` kann ein bestimmtes
PK3 wählen. Der Remaster-Test verändert nur eine separate Testdatei im Ausgabeordner.
Zwei echte Koop-Clients prüft `tools/test_credits_coop.py` mit denselben Pfadoptionen.

Ergebnisse und repräsentative Spielansichten stehen unter
`tools/validation/credits-reliquiar-2026-09-10`. Automatisierte Tests laufen ohne
Ton; sie behaupten kein subjektives Abhören und keinen vollständigen Kampagnenlauf.
Bei einem Versionswechsel ENDMAP neu betreten, um die neue Kapitelstruktur zu laden.
