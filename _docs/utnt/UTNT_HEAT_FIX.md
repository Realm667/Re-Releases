# HeatEffectGiver 32029 — Fehlerkorrektur

## Ursache

`UTNTPresentation.RenderOverlay` übergab `'amount'` als ZScript-Name an die
String-API des Shaders. Namen sind in ZScript nicht case-sensitiv; der Name
ist bereits als `Amount` (Inventar-Eigenschaft) registriert. Die implizite
Umwandlung erzeugt daher `"Amount"`. GLSL-Uniforms sind dagegen case-sensitiv.

Im unveränderten Shaderpfad zeigte UZDoom 5.0.1 mit `listuniforms heatshader`:

```text
amount : 0.000000 0.000000 0.000000
Amount : 51.750000 0.000000 0.000000
```

Der Spieler hatte bereits `Heat=0.75`, aber die tatsächlich gelesene Uniform
blieb null. Deshalb fehlten sowohl Verzerrung als auch Unschärfe. Der Aufruf
verwendet jetzt die exakten Strings `"heatshader"` und `"amount"`.

Zusätzlich nutzte die Entfernungserkennung `FloorZ` und `CeilingZ` des Actors.
Diese Kollisionsgrenzen können an 3D-Böden oder benachbarter Geometrie enden.
Bei einer Quelle unter einer 3D-Plattform (`CeilingZ=32`) und einem Spieler
darüber (`Z=64`, horizontaler Abstand 32) fiel `Heat` fälschlich auf null.
Die ursprüngliche Implementierung füllte ausdrücklich den gesamten Sektor
mit `GetZAt(..., GZF_NO3DFLOOR)`. Dieses Verhalten ist wiederhergestellt;
die Grenzen werden bei jeder Entfernungsprüfung aktuell abgefragt.

## Prüfung

Reproduzierbarer Test: `tools/test_heat.py`. Benötigt Python mit Pillow,
UZDoom 5.0.1 und Doom II; Engine/IWAD über `UTNT_ENGINE` und `UTNT_IWAD`
oder `--engine` / `--iwad` angeben. Beispiel:

```text
python tools/test_heat.py --mod tutnt.pk3 --renderer both
```

Die generierte Testkarte platziert tatsächlich Editor-Nummer 32029 unter
einem soliden 3D-Boden. OpenGL und Vulkan bestehen jeweils 15 Laufzeitprüfungen:
Erzeugung, problematische Höhenkonstellation, Distanzabfall, Rand, Zentrum,
Deaktivierung/Reaktivierung, Skalierung, obere/untere Sektorgrenze,
Wirkung unter dem 3D-Boden, Zerstörung, dynamisches Erzeugen und Save/Load.
Für Prüfpositionen außerhalb der Sektorgrenzen unterdrückt die Testfigur
gezielt die normale Physikkorrektur; der Produktionsactor bleibt unverändert.

Darüber hinaus wird pro Backend die echte Uniform `amount=51.75` überprüft.
Ein Bildvergleich eines statischen Deckenausschnitts bestätigt die sichtbare
Shaderwirkung und deren Abschaltung durch den Effektschalter, Stärke null
und Reduced FX. Die Testbilder enthalten keine erzwungene Shader-Aktivierung.
Alle 14 ACS-Module des isolierten Pakets wurden byteidentisch nachkompiliert.

Nachweise liegen unter `tools/validation/heat-2026-09-08/`. Das getestete
isolierte PK3 enthält den zum Buildzeitpunkt committeten Spielstand plus
diese Korrektur. Parallel bearbeitete Änderungen bleiben außerhalb des
Fix-Commits. Keine vollständige Kampagnen-, Mehrspieler- oder GZDoom-Abnahme.
