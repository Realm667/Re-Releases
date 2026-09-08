# TNT02: kaltes Gebirgsgewitter

Die freigegebene Gewittervorschau ist als eigener Himmel für TNT02 umgesetzt. Zwei langsam gegeneinander ziehende Wolkenlagen liegen vor einer gestaffelten, im blaugrauen Regendunst versinkenden Bergkulisse. Berge bleiben unbewegt. Die Würfelflächen teilen sich dieselbe Richtungsprojektion; im Zenit blendet die Darstellung in eine planare Projektion über.

## Licht und Gewitter

551 Sektoren mit offenem Himmel erhalten den Lichtfarbton `#B9C9DC` und 16 Prozent Entsättigung. Die Grundhelligkeit beträgt mindestens 160; höhere vorhandene Helligkeitsstufen bleiben erhalten. Geometrie, Spezialfunktionen und geschlossene Innenraumsektoren bleiben unverändert. Beim Blitz steigt nur das Außenlicht kurz an, während geschützte Innenräume ihren bisherigen Zustand behalten. Lava und andere lokale Lichtquellen bleiben eigenständig.

Ein serialisierter ZScript-EventHandler steuert drei wechselnde Blitzrichtungen sowie einen kurzen Hauptimpuls mit schwächerem Nachblitz und Abklingen. Die Pause variiert deterministisch zwischen etwa 8 und 20 Sekunden; kein Gameplay-Zufallsgenerator wird verbraucht. Donner folgt verzögert. Derselbe Puls steuert die lokalen Aufhellungen im Wolkenmaterial und das Sektorlicht. Dunkle, dichte Wolken behalten ihre Kontur.

Ein dezenter Postprocess-Effekt hebt die Belichtung ausschließlich in der lokalen Spielansicht unter freiem Himmel an. Eine Aufwärtsspur berücksichtigt feste 3D-Böden und Dächer; beim Wechsel in Deckung klingt der Effekt in wenigen Tics aus. HUD, tiefe Innenräume und andere Maps erhalten diesen Effekt nicht. Die vorhandenen Einstellungen für reduzierte Effekte und Shader-Overlays werden berücksichtigt.

Der alte ACS-Gewitterablauf in Script 2 ist durch einen leeren Einstieg ersetzt, damit weder der alte Texturwechsel noch die bisherigen Licht-Fades gegen die neue Steuerung arbeiten. Sämtliche anderen ACS-Scripts bleiben erhalten. Der normale SkyViewpoint steht in einer neuen, isolierten Einsektor-Kulisse bei `(28000, -28000, 0)`; die beiden weiteren SkyViewpoints bleiben an ihren bisherigen Positionen.

## Ressourcen und Prüfung

Die 25 Himmelszustände teilen sechs Materialprogramme und sechs statische Würfelflächen. Das Seitenverhältnis der zusammengesetzten Quelltextur kodiert Blitzstärke und -richtung; es bleibt bei gleichmäßiger Texturskalierung erhalten. Dadurch entstehen keine langen Kompilierpausen für jede einzelne Blitzvariante. Die zusätzlichen Randpixel werden nur für den statischen Fallback verwendet; im Shader wird direkt aus den Panoramen abgetastet. Software-Darstellung besitzt den statischen Himmel und das Sektorlicht, ohne die animierte Materialwirkung.

OpenGL und Vulkan wurden jeweils mit 15 Assertions einschließlich Speichern/Laden geprüft. Messwerte und echte Spielaufnahmen: `tools/validation/thunder-2026-09-09`. Bearbeitbare Quelle und Herkunft der Imagegen-Texturen: `tools/artwork/thunder`. Assetbau: `python tools/build_thunder_sky.py` (NumPy/Pillow). Der Map-Patcher benötigt ACC und ZDBSP; der Strukturtest prüft die erhaltene Spielgeometrie und die unveränderten übrigen Scripts.

Für die geänderte Mapgeometrie TNT02 frisch starten. Die Tests decken Speichern/Laden innerhalb dieses neuen Mapstands ab, keinen vollständigen Kampagnen- oder Mehrspieler-Durchlauf.
