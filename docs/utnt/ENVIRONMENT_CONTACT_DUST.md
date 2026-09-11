# Mechanismusstaub an Reibungskanten

Stand: 12.09.2026. Diese Anpassung ersetzt die flächige Erzeugung aus `ENVIRONMENT_AREA_FIX.md` und die reine 22-Prozent-Mitnahme aus `ENVIRONMENT_FOG_GUIDES.md`. Die dort dokumentierte Lavaaufhellung bleibt unverändert.

## Aktuelles Verhalten

Staub entsteht während der Bewegung an Kontaktkanten zwischen bewegtem Boden oder bewegter Decke und einer angrenzenden festen Wand. Die Ermittlung nutzt vorhandene Sektorgrenzen und die Höhe der Nachbaröffnung. Selbstreferenzierende Linien und freie Durchgangsflächen erzeugen keinen Reibungsstaub. Bei nativen Türen bleiben ausschließlich die seitlichen geschlossenen Führungen aktiv. Map-Geometrie und Gameplay bleiben unverändert.

Die Positionen werden unabhängig zufällig entlang dieser Kanten ausgewählt, gewichtet nach ihrer Länge. Die erwartete Menge beträgt bei hoher Effektqualität 0,36 Partikel pro Tic und 1024 Einheiten Kontaktlänge, mit maximal vier pro Tic. Damit bestimmt die tatsächlich reibende Kante die Menge statt der gesamten Sektorfläche. Die Zufallsfolge bleibt von der Spielsimulation getrennt.

Partikel werden bereits bei ihrer Geburt mit Abstand auf der freien Seite der Fläche platziert. Abziehende Flächen nehmen sie weiterhin nur leicht mit; eine entgegenkommende Fläche drückt die sichtbare Wolke vor sich her, statt ihren Mittelpunkt zu überholen und sie abzuschneiden. Beide Interpolationspositionen werden zusammen verschoben. Bei einer vollständig schließenden Öffnung klingt die Transparenz schrittweise aus. Die normale Lebensdauer und Größen-/Bewegungsvariation bleiben erhalten.

## Kamerawackeln und Noclip

Die Ursache des gemeldeten fehlenden Wackelns war aktives `noclip`, vom Nutzer bestätigt. UZDoom unterdrückt in diesem Zustand auch native Earthquake-Effekte (`DEarthquake::StaticGetQuakeIntensities`). Der frühere Test setzte lediglich das Actor-Flag `bNoClip`, nicht den Spieler-Cheat `CF_NOCLIP`; dieser Unterschied wird jetzt ausdrücklich getestet. Der Mod verändert den Cheat oder die globale Bebenpräferenz nicht.

Auf Wunsch sind alle Intensitäten gegenüber der Fassung vom 11.09. um 20 Prozent reduziert: Start/Stopp 0,92, laufende Bewegung 0,336; Rollanteile 0,096 beziehungsweise 0,036. Reichweite und Entfernungsabschwächung bleiben erhalten.

`netevent environmentstats` zeigt zusätzlich `MECHANISM_QUAKE` mit Noclip-Zustand, globaler Bebenintensität und den relevanten Effektoptionen. Zum visuellen Test muss `noclip` ausgeschaltet sein. Ein absichtlich auf null gesetztes `r_quakeintensity` bleibt wirksam.

## Regressionen

```text
python -B tools/test_environment_fx.py --case area --renderer 0 --mod tutnt.pk3
python -B tools/test_environment_fx.py --case guides --renderer 1 --mod tutnt.pk3
python -B tools/test_environment_fx.py --case motion --renderer 1 --mod tutnt.pk3
```

Der historische Fallname `area` prüft jetzt Kontaktkanten statt flächiger Geburt: keine Partikel im Inneren, zur Kontaktlänge passende Häufigkeit, Streuung entlang der Kanten über die gesamte Bewegung und Erzeugungsende beim Stopp. Zusätzlich werden der Abstand zur fahrenden Decke beziehungsweise zum Boden und die kontinuierliche Transparenz bestehender Wolken erfasst. `guides` prüft zurückbleibenden Türstaub und misst die tatsächliche gerenderte Kamera mit aktivem und inaktivem Noclip sowie bei 512, 384 und 32 Einheiten Entfernung. `motion` prüft kurze Bewegungen, Ausblenden, Türen und Decken sowie den unveränderten lokalen Hitzeeffekt.

Lokale Laufzeitnachweise: `tutnt/.codex/validation/mechanism-contact/`. Die Kontaktprüfung nutzt den Mittelpunkt einer vorhandenen Kante; ungewöhnliche geneigte Übergänge sind entsprechend angenähert. Ein vollständig geschlossener Sektor kann keine sichtbare Rauchwolke im Inneren erhalten.

## Wandabstand und Auslöseschwellen (12.09.2026)

Der bisherige Abstand von 2–5 Einheiten reichte für die Rauchgrafik nicht aus. Die Wolke erhält jetzt nach innen einen Abstand entsprechend dem umschließenden Radius ihrer skalierten 96-Pixel-Grafik plus vier Einheiten Luft. Das ergibt bei der Geburt ungefähr 24–45 Einheiten Abstand des Mittelpunkts zur Wand. Die Prüfung berücksichtigt angrenzende Wandsegmente und Ecken; sie wird nach Drift und Wachstum erneut ausgeführt. Wenn eine enge Führung kein weiteres Wachstum zulässt, behält die Wolke ihre vorherige Größe und sichere Position und blendet über ihre normale Lebensdauer aus. Zu große neue Wolken werden ausgelassen.

Es gibt keine feste Mindestfläche und keinen Flächenschwellwert für Sektorverbünde. Bewegung wird ab mehr als 0,01 Einheiten Höhenänderung pro Tic erkannt. Erforderlich sind ein erfasster Mechanismus, Reibungskanten, aktivierte Effekte und eine Kamera innerhalb von 1200 Einheiten. Die freie Höhe muss mindestens 40 Einheiten betragen; größere Varianten benötigen durch ihre vertikalen Abstände ungefähr bis zu 66 Einheiten. Zwischen zwei gegenüberliegenden Wänden braucht eine neue Wolke je nach Variante ungefähr 48–90 Einheiten freie Breite. Dies sind Platzprüfungen für einzelne Wolken, keine Mindestfläche eines Sektors.

Bei hoher Qualität beträgt die erwartete Erzeugungsrate vor Platzprüfungen 12,6 Wolken pro Sekunde und 1024 Einheiten Reibungskante: 128 Einheiten ergeben etwa 1,6/s, 256 etwa 3,2/s, 512 etwa 6,3/s. Mittlere/niedrige Qualität verwendet 60/30 Prozent; kurze Bewegungen können durch die Zufallsverteilung ohne Wolke bleiben. Obergrenze: vier Erzeugungsversuche pro Tic und einzeln beobachtetem Sektor.

Gleich getaggte, angrenzende Sektoren werden weiterhin einzeln beobachtet, nicht ausdrücklich zu einem zusammenhängenden Verbund zusammengefasst. Bündige offene Innengrenzen erzeugen keine Reibung; die äußeren Kontaktlängen tragen jeweils zur Gesamtrate bei. Daher ist die Summe unterhalb der Einzelbudgets weitgehend proportional zur gemeinsamen Außenkontaktlänge, aber kein gemeinsames Gruppenlimit implementiert.

Die Regression prüft den Wandabstand bei Geburt und Wachstum, beide Wände einer Ecke und die Ablehnung einer zu großen Wolke in einer engen Führung. Nachweise: `tutnt/.codex/validation/smoke-wall-clearance/`.
