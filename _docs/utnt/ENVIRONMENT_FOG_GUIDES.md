# Lava im Nebel und Mechanismusreaktionen

Stand: 11.09.2026. Umsetzung in den Lava-Materialshadern und `UTNT_Environment.zc`, ohne Änderung der Map-Geometrie.

## Lava und FADE

Die Engine wendet farbigen Sektornebel nach der Materialbeleuchtung an. Fullbright beziehungsweise Brightmaps allein verhindern deshalb nicht, dass die Lava in dunklen FADE-Räumen stark abgedunkelt wird.

Die Shader für Lavaflächen, Lavafälle und generierte Überlaufkanten gleichen jetzt ausschließlich den selbstleuchtenden Materialanteil vor dieser Nebelstufe aus. Die zusätzliche Glut durchdringt den Nebel stärker; Kruste, Raumbeleuchtung und Nebelfarbe bleiben erhalten. Ohne farbigen Nebel ist der zusätzliche Beitrag null. Die Verstärkung ist begrenzt, sodass sehr dichter Nebel die Lava weiterhin verdecken kann. Die bestehende Ausblendung am Lava-Horizont bleibt bestehen.

Nach visueller Rückmeldung wurde der Exponent der Emissionsdurchlässigkeit von 0,40 auf 0,28 reduziert: Die glühenden Anteile sind dadurch nochmals heller. Dies ist die abschließende Fassung. Es wird weder der gesamte Bildschirm noch der ganze Sektor aufgehellt.

## Staub und Bewegung

Native vertikale Türen werden anhand ihres aktiven Door-Movers erkannt. Ihr Staub entsteht zufällig entlang geschlossener seitlicher Sektorgrenzen, nicht auf den offenen Durchgangsflächen. Die Auswahl gewichtet die Länge der Führungen. Bereits erzeugter Staub bleibt dort zurück und übernimmt keine Türbewegung; seine eigene sanfte Drift bleibt erhalten.

Bei bewegten Böden und Decken bleiben die unabhängigen Zufallspositionen über der gesamten Fläche und die flächenabhängige Erzeugungsrate bis zum Bewegungsende erhalten. Partikel übernehmen jetzt nur 22 Prozent der Flächenbewegung. Wird ein Partikel von einer festen Fläche eingeholt, blendet es aus. Lebensdauer, Größenvariation und stetige Transparenzkurve bleiben erhalten.

Kamerawackeln verwendet nur noch eine Entfernungsabschwächung statt der bisherigen doppelten Dämpfung. Es bleibt bei 384–512 Mapeinheiten spürbar und klingt bis 768 Einheiten aus; Start und Stopp sind stärker als die laufende Bewegung. Es gibt keinen Schaden oder Spielerstoß. Globale Bebenintensität sowie UTNT-Effektoptionen bleiben wirksam.

## Prüfung und Debugging

Die Regressionen in `tools/test_environment_fx.py` ergänzen folgende Fälle:

```text
python -B tools/test_environment_fx.py --case fog --renderer 0 --mod tutnt.pk3
python -B tools/test_environment_fx.py --case fog --renderer 1 --mod tutnt.pk3
python -B tools/test_environment_fx.py --case guides --renderer 1 --mod tutnt.pk3
python -B tools/test_environment_fx.py --case area --renderer 0 --mod tutnt.pk3
```

`fog` öffnet TNT02 bei (3480, -5330, -239), Blickwinkel 90, Pitch 24: die Stelle des dunklen Lava-Screenshots. Die aktualisierte Glut wurde unter OpenGL und Vulkan gerendert und visuell geprüft.

Mit geladener Environment-Test-Fixture sind zusätzlich `netevent envguides`, `netevent envdoor`, `netevent envceiling`, `netevent envceilingup` und `netevent envfog 80` verfügbar. Diese Diagnosebefehle gehören zur Test-Fixture, nicht zum normalen Spielpaket.

Nachweise: Türtest mit 15 Staubgeburten, keiner außerhalb der Führungen und drei beobachteten zurückbleibenden Partikeln. Bewegungsübernahme mit 246 Boden- und 252 Deckenmessungen ohne Abweichung. Im RenderEvent gemessene seitliche Kamerabewegung während gleichmäßiger Bewegung: 0 ohne Mechanismus, 0,338 bei 512 Einheiten, 0,501 bei 384 und 0,825 bei 32 Einheiten. Die Werte hängen vom Zufallsverlauf und den globalen Kameraoptionen ab; die Regression prüft Sichtbarkeit und steigende Stärke bei Annäherung. Der Bewegungstest besteht mit 18 Laufzeitprüfungen, der Flächentest mit 14. Zusätzlich bestehen 19 Struktur- und Vertragsprüfungen für Umgebung, lokale Hitze und Lavaüberläufe.

Türführungen werden aus vorhandenen geschlossenen Grenzen abgeleitet; außergewöhnliche geskriptete Deckenbewegungen ohne nativen Door-Mover bleiben Deckenmechanismen. Nebelkorrektur benötigt die Hardware-Materialshader. Lokale Nachweise liegen unter `tutnt/.codex/validation/environment-fog-guides/`.
