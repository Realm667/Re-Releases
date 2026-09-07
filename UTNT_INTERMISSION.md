# UTNT-Intermission: Statistiklayout

`UTNTIntermission` erbt von `DoomStatusScreen` und ersetzt dessen Einzelspieler-Darstellung. `Statscreen_Single` in MAPINFO registriert die Klasse; Koop und Deathmatch behalten ihre bisherigen Statistikbildschirme.

Die großen UTNT-Beschriftungen kollidierten mit der festen Zeitposition des Standardlayouts. `WITIME` und `WIPAR` besitzen außerdem Patch-Offsets von (-40, 20). Das neue Layout zeichnet diese Grafiken anhand ihrer sichtbaren linken oberen Ecke und platziert Kills, Items, Secrets, Zeit, optionale Gesamtzeit und optionale Par-Zeit in getrennten Zeilen. Schrift-/Grafikhöhen und die Breite der vollständigen Werte bestimmen die virtuelle Zeichenfläche. Der Hintergrund und die ursprünglichen Beschriftungsgrafiken bleiben erhalten.

Zahlen verwenden die vollständige UTNT-Textschrift mit proportionaler Breite und rechtsbündiger Ausrichtung. Die alte WINUM-Schrift hat ungleich breite Ziffern und unsichtbare Satzzeichen; die standardmäßigen festen Ziffernzellen waren dafür ungeeignet. Prozentzeichen, Bruchstrich und Zeitdoppelpunkte sind nun sichtbar. Die Gesamtzeitbeschriftung steht in `LANGUAGE.intermission` auf Deutsch und Englisch.

Zähler, Geräusche, Überspringen und Kartenwechsel stammen weiterhin aus der Engine-Basisklasse. `wi_percents` und `wi_showtotaltime` bleiben wirksam; leere Kategorien zeigen 100 % beziehungsweise 0/0. Die ZScript-Klasse setzt den Skalierungsmodus explizit, weil `StatusScreen.SetSize` in UZDoom 5.0.1 den gleichnamigen Parameter statt des Klassenfelds beschreibt.

## Prüfung am 08.09.2026

- Echter Abschluss von TNT01 mit der Produktionsklasse: Intermission fehlerfrei angezeigt und anhand einer Engine-Aufnahme geprüft.
- `python tools/test_intermission.py`: Vulkan mit leeren Kategorien und OpenGL mit bis zu 12.345 Kills, 100 Stunden Kartenzeit, 123 Stunden Gesamtzeit und Par-Zeit. Beide Läufe bestehen je acht Prüfungen zu Zählern, Formatierung, Skalierungsmodus und Weiterwechsel nach TNT02.
- Prozentwerte und absolute Werte, Gesamtzeit an/aus, deutsche Gesamtzeitbeschriftung, 1024×768, 1920×1080 und 2560×1080 aufgenommen. PNG-Abmessungen werden automatisch kontrolliert; Zeilen und Spalten wurden visuell geprüft.
- Die Testunterklasse setzt ausschließlich Teststatistiken und ruft nach den Aufnahmen den regulären `nextStage`-Einstieg auf. Das Test-Add-on wird nicht mit dem Spiel ausgeliefert.

Zum Wiederholen `UTNT_ENGINE` und `UTNT_IWAD` setzen. Ausgewählte unveränderte Engine-Aufnahmen und Ergebnisse liegen unter `tools/validation/intermission-2026-09-08`.
