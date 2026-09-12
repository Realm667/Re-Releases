# Flächenstaub und Lava-3D-Floors (11.09.2026)

## Mechanismusstaub

Die bisherige Zellfolge verwendete `cells - 1` als Schrittweite und durchlief damit Nachbarzellen rückwärts. Außerdem entstand unabhängig von der Fläche höchstens eine Wolke pro Emissionsintervall. Diese Kombination verursachte die sichtbare Kette.

Die Emission wird jetzt bei jedem tatsächlichen Bewegungsschritt ausgewertet. Die erwartete Rate beträgt auf hoher Effektqualität 12,6 Wolken pro Sekunde und 65.536 Quadrat-Mapeinheiten. Die tatsächliche Polygonfläche wird aus den orientierten Sektorkanten berechnet; Aussparungen zählen nicht mit. Unabhängige Zufallspositionen werden über die Grenzen des gesamten Sektors verteilt und gegen den tatsächlichen Sektor geprüft. Der lokale Zufallszustand verbraucht keinen Gameplay-Zufall.

Stochastische Rundung verteilt die Geburten zeitlich. Eine viermal größere Fläche erhält im Mittel viermal so viele Wolken. Als Schutz bei extrem großen bewegten Sektoren gilt ein Maximum von vier Geburten pro Tic, auf mittlerer/niedriger Qualität reduziert sich die Rate auf 60/30 Prozent. 64 Versuche pro Position begrenzen die Suche bei stark zerklüfteten Sektoren; erfolglose Versuche werden verworfen. Entfernungsprüfung am nächsten Punkt der Sektorgrenzen statt am Mittelpunkt vermeidet das Abschalten großer Plattformen in Spielernähe.

Neue Wolken entstehen bis zum letzten Bewegungsschritt. Bestehende Wolken behalten ihre Alterskurve, weiches Einblenden, langsames Ausblenden und ihre individuellen Größen, Formen und Bewegungen. Kamerawackeln beim Start, während der Bewegung und beim Anhalten bleibt bestehen.

## Fehlende Wirkung am ersten TNT02-Lavasee

Die große sichtbare Lavaoberfläche liegt im Empfängersektor 46 auf einem 3D-Floor bei Z = -512. Sein eigentlicher Boden liegt bei -700 und verwendet GRAVE02. Die alte Erkennung untersuchte normale Sektorböden und Sidedefs und schloss Kontrollsektoren aus. Dadurch fehlte gerade diese sichtbare Lavafläche in den Hitzequellen.

Der Generator löst nun sichtbare Lava-3D-Floors über `Sector_Set3DFloor`, Sektortags und zusätzliche UDMF-Tags auf die tatsächlichen Empfängerflächen auf. Unsichtbare Kontrollflächen erzeugen keine Quellen. Der neue Tabellentyp 2 verwendet den Empfängersektor im Indexfeld und den Kontrollsektor im Part-Feld; seine Höhe folgt der Deckenebene des Kontrollsektors. Zur Laufzeit muss ein passender sichtbarer 3D-Floor existieren.

Breite Innenbereiche erhalten größere, weich auslaufende Hitzevolumen, deren horizontaler Radius innerhalb der Fläche bleibt. Die Quellenauswahl berücksichtigt ihre Größe und reicht bis 2048 Einheiten. Bei mindestens zwei verfügbaren Plätzen bleibt ein sichtbarer Lavafall berücksichtigt, auch wenn große Bodenvolumen dominieren. Der Pool bleibt auf sechs Actors begrenzt; überlappende Quellen vervielfachen die Verzerrungsstärke nicht. Bernsteinfarbener Haze und Glühen benutzen dieselbe lokale Maske. Die Verdeckungsprüfung bleibt eine Näherung aus Geometriestrahlen, keine pixelgenaue Szenentiefe.

## Verifikation

UZDoom 5.0.1: Der Flächentest bestand unter OpenGL und Vulkan mit 89 bzw. 368 Wolken (wunsichtbare Kontrollflächen.

## Prüfen

Mit dem aktuellen `tutnt.pk3` und zusätzlich `tools/fixtures/environment`:

- `map TNT02`; `netevent envfly`; `netevent envpos 700 -320 -128`; `netevent envview 0 8`: Uferperspektive des ersten großen Lavasees.
- `netevent localheatstats`: nennt aktive normale Böden, Wände und 3D-Floors; `netevent envlakecheck` prüft den See und den Lavafall.
- `UTNT_shaderoverlayswitch false` / `true`: Vergleich der Hitzeeffekte. `UTNT_heatstrength 1`, `UTNT_fxquality 3` und `UTNT_reducedfx false` aktivieren volle Effektqualität.
- `map ENVTEST`; `netevent envfly`; `netevent envpos 1100 800 64`; `netevent envareastart`: gleichzeitig 256 × 256 große Plattform und 512 × 512 große bewegte Decke. Nach neun Sekunden prüft `netevent envareacheck` die Verteilung und das Emissionsende. Vor Wiederholung die Karte neu starten.
- `netevent envdoor`, `netevent envshort`, `netevent envceiling`: bestehende Tür-, Kurzbewegungs- und Deckentests.

Automatisiert: `python -B tools/test_environment_fx.py --case area --renderer 0 --mod <PK3>` sowie `--case motion` und `--case lake`. Die Geometrie- und Shaderverträge prüfen `python -B -m unittest test_local_heat test_environment_contracts` im tools-Verzeichnis. Lokale Laufzeitnachweise liegen unter `tutnt/.codex/validation/environment-area/`.
