# TNT02: dunkles Gewitter mit unterschiedlichen Entfernungen

Die animierte Wolkendecke und die feine, unbewegte Gebirgskette behalten die Komposition des bestätigten Mockups. Die Korrektur vom 09.09.2026 stellt die dunkle Atmosphäre wieder her: Wolken und Berge sind deutlich abgedunkelt und zu 78 Prozent in Richtung neutraler Grautöne gemischt. Die blaue Färbung ist weitgehend entfernt. Der statische Fallback wird mit derselben Farbkorrektur gebaut.

## Grundlicht und Blitze

Die 551 Außenareale erhalten `#D0D1D4` mit 12 Prozent Entsättigung. Ihre ursprünglichen Map-Helligkeitswerte sind wiederhergestellt; die frühere Mindesthelligkeit 160 entfällt. Der Himmel ist in der geprüften Referenzansicht etwa 63 Prozent dunkler als die erste Umsetzung. Geschlossene Innenraumsektoren, Gameplay-Geometrie, weitere SkyViewpoints und übrige ACS-Scripts bleiben unverändert.

Die Entfernung ist eine inszenierte Eigenschaft jedes Gewitterereignisses. Sie steuert die Blitzspitze, Donnerlautstärke, Tonhöhe und Wartezeit gemeinsam:

| Gewitter | Blitzspitze relativ zum Nahblitz | Donnerpegel | Verzögerung |
| --- | --- | --- | --- |
| Fern | 6–14 % | 12–20 %, tiefer | 3–6 Sekunden |
| Mittel | 25–56 % | 40–60 % | 0,6–1,8 Sekunden |
| Sehr nah | 100 %, kurz fast weiß | 95–100 % | Gleichzeitig mit dem Blitz |

Die Prozentwerte der Blitzspitzen sind Steuerwerte, keine garantierten Bildschirmhelligkeiten. Der Nahblitz erreicht für etwa 86 ms seine Spitze, fällt schnell ab und besitzt einen schwächeren Nachimpuls. Er darf Wolken und Umgebung kurz kräftig überstrahlen. Ein stärkerer, neutraler Belichtungseffekt wird nur unter freiem Himmel angewendet; Dächer und feste 3D-Böden schirmen ihn ab, das HUD bleibt unbeeinflusst. Die vorhandenen Einstellungen für reduzierte Effekte und Shader-Overlays gelten weiterhin.

Ein privater serialisierter Zufallsgenerator wählt wechselnde Richtungen, Abstände von 9–20 Sekunden und leicht variierende Stärken. Fernere Ereignisse dominieren. Zwischen zwei Nahblitzen liegen mindestens drei andere Ereignisse. Im reproduzierbaren Test mit 1000 Ereignissen entstanden 595 ferne, 337 mittlere und 68 nahe Gewitter.

Der Donner läuft über einen eigenen gespeicherten Termin, unabhängig vom kurzen Lichtimpuls. Dadurch funktioniert auch ein später Donner nach dem Abklingen des Blitzes und nach Speichern/Laden. Pro Ereignis wird genau ein atmosphärischer Donnerklang abgespielt; die früheren vielen TID-666-Schallquellen würden den beabsichtigten Pegel je nach Standort verfälschen. Der tatsächliche Lautstärkeeindruck hängt zusätzlich von den Audioeinstellungen ab. Der Gameplay-Zufallsgenerator bleibt unberührt.

## Ressourcen und Prüfung

25 Skyzustände teilen sechs Materialprogramme und sechs statische Würfelflächen. Die Textur-Seitenverhältnisse kodieren acht Blitzstufen an drei Himmelsrichtungen; alle Zustände benutzen dieselbe Animation. Software-Darstellung hat den dunklen statischen Himmel, Sektorblitze und Donner, aber keine animierte Materialwirkung.

`tools/build_thunder_sky.py` erzeugt Shader und Fallbacks, `tools/patch_thunder_map.py` arbeitet auf der ursprünglichen TNT02-Baseline. Die aktuelle Korrektur ändert an der bestehenden Map ausschließlich die 551 Lichtdefinitionen. Nodes und ACS-Bytecode bleiben bytegleich. Texturen/Prompts stehen in `tools/artwork/thunder`.

Die Prüfungen unter OpenGL und Vulkan umfassen Dunkelzustand, bewegte Wolken, drei deutlich abgestufte Blitzspitzen und Abschirmung unter Dächern. Der Vulkan-Test prüft zusätzlich die Ereignisverteilung, gemessene Donnertermine, genau einmalige Wiedergabe-Anforderung und Speichern/Laden während eines ausstehenden Ferndonners. Audio wird in den automatisierten Tests deaktiviert; geprüft werden die tatsächlichen Steuerwerte und Aufruftermine, kein Hörvergleich. Nachweise: `tools/validation/thunder-distance-2026-09-09`. Reproduktion: `tools/test_thunder_distance.py` mit `--engine`, `--iwad`, optional `--profiles` und `--renderer 0` oder `1`.

Das Spiel neu starten und TNT02 frisch laden, damit die geänderten Grundhelligkeiten übernommen werden. Speichern/Laden innerhalb des neuen Mapstands ist geprüft; ein vollständiger Kampagnen- oder Mehrspieler-Durchlauf gehört nicht zu dieser Abnahme.
