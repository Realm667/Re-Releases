# ENDMAP: komponierte Credits

Die freigegebenen Mockups sind als native, zeitgesteuerte Credit-Tafeln umgesetzt.
Die lebende ENDMAP, ihre Kampfszene und die bereits adaptierte TNT01-Skybox bleiben
als Hintergrund erhalten. Dezente Schwenks, optischer Zoom, schwarze Blenden und
seitliche Abdunklung führen durch die Credits. Die großen Namen verwenden eine
private, aufgehellte Variante der vorhandenen DBIGFONT. Alle Begleittexte,
Rubriken und Bedienhinweise verwenden die vorhandene Quake-SMALLFONT.

Die sechs Freigabebilder waren Layoutbeispiele. Die vollständigen Original-Credits
umfassen 25 Tafeln mit 65 Nennungen und 318 Sekunden Laufzeit vor dem Finale.
Texte stehen in `tutnt/credits/original.txt`; die alte Scroller-Grafik wird nicht
mehr abgespielt. Originale Kameras, Kampfskripte und Schlussfahrt bleiben erhalten.

## Remaster ergänzen: zwischen 05 und 06

`tutnt/credits/remaster.txt` wird nach dem persönlichen Dank an Graf Zahl
("DANKE CHRIS!", Freigabebild 05) und vor der Schlussfahrt mit "THE END"
(Freigabebild 06) geladen. Der vorbereitete Block ist ohne Namen unsichtbar.
Einfach echte Einträge unter der vorhandenen P-Zeile ergänzen:

```text
P|standard|1|13|Remaster
N|NAME|Beitrag zum Remaster
N|WEITERER NAME|Weiterer Beitrag
```

`P|Layout|Kamera|Sekunden|Rubrik` beginnt einen Abschnitt. `N|Name|Beitrag`
fügt eine Nennung hinzu. Kameras: 1 bis 5; Dauer: 8 bis 60 Sekunden pro Tafel.
`standard` verteilt automatisch auf drei Namen pro Tafel, `dense` auf sechs.
Weitere P-Zeilen erlauben eigene Kategorien. `~` im Namen erzwingt einen Umbruch.
Datei als UTF-8 speichern. Die bestehende Quake-Schrift ist für ASCII ausgelegt;
für Umlaute gegebenenfalls ae/oe/ue verwenden und neue Texte im Spiel prüfen.
Danach das PK3 neu bauen und ENDMAP neu betreten; ein gespeicherter Spielstand
behält seine gespeicherten Credit-Texte. Für reine Textänderungen ist keine neue
ACS-Logik erforderlich. Im ausgelieferten Remaster-Block stehen keine Testnamen.

## Bedienung und Technik

Enter, Leertaste, Rechts oder Gamepad-A: nächste Tafel. Links: vorherige Tafel.
Ende: Credits überspringen und die vorhandene Schlussfahrt starten. Im Koop
steuert der Host; Fortschritt und Finale sind synchronisiert. Tastenwiederholung
wird abgefangen, Menü und Konsole behalten ihre Eingaben. Karten, Fortschritt,
Kameras und Finale-Zustand werden mit Spielständen gespeichert.

`UTNTCreditsHandler` lädt die Karten und steuert die vorhandenen Kameras.
`UTNTCreditsUI` zeichnet in einem an 720 Pixel Höhe orientierten virtuellen
Bildraum; für 4:3 werden Ränder und Spalten angepasst. Texte werden zur Laufzeit
umgebrochen. Die ENDMAP enthält nur neue SCRIPTS/BEHAVIOR-Lumps; Geometrie und
der bereits freigegebene Skybox-Umbau bleiben unverändert. ACS 55 startet einmal
die bisherige Schlussfahrt, ACS 51/52/102 behalten ihren ursprünglichen Inhalt.
Die Musiksequenz D_ENDG / D_NOVER bleibt erhalten. Zufällige zusätzliche
Bomben-Ambients des alten Scrollers entfallen; Kampfgeräusche bleiben bestehen.

`tools/build_credit_assets.py` erzeugt die private Titelschrift und zwei winzige
Verlaufstexturen reproduzierbar aus DBIGFONT und festen Parametern (Pillow).
SMALLFONT wird direkt aus den bestehenden STCFN-Grafiken verwendet.

## Prüfungen

Reproduzierbarer Engine-Test, Beispiel:

```text
python tools/test_credits.py --engine PATH/uzdoom.exe --iwad PATH/DOOM2.WAD --out PATH/results --mode visual --renderer 1
```

Zusätzlich `--classic` für 4:3, `--renderer 0` für OpenGL, und die Modi
`regression` (Weiter, Debounce, Speichern/Laden, Überspringen, Schlussbild),
`finale` (natürliches Ende) und `remaster` (vier temporäre Einträge, automatische
Folgeseite, richtige Position). `--mod` kann ein bestimmtes PK3 auswählen.
Der Remaster-Test schreibt ausschließlich einen separaten Testzusatz im
Ausgabeordner. Das Endbild und repräsentative Ansichten sind unter
`tools/validation/credits-2026-09-09` dokumentiert.

Die Prüfung umfasst alle Tafeln und den vollständigen Ablauf der Schlussfahrt;
ein ununterbrochener fünfminütiger Durchlauf und subjektives Abhören der Musik
sind damit nicht behauptet. Bestehende Spielstände aus der alten Scroller-Version
sind nicht als Migration getestet; ENDMAP für diese Version neu betreten.

Zwei echte Koop-Clients sind mit `tools/test_credits_coop.py` geprüft; das Werkzeug
akzeptiert ebenfalls `--engine`, `--iwad`, `--mod` und `--out`. Der finale
Paket-Build und die erfolgreichen Prüfergebnisse stehen im Validierungsordner.
