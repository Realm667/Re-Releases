# Erweiterte Flächentexturen

44 ausgewählte Materialfamilien erhalten größere Texturflächen und fortlaufende Wandkoordinaten. 40 PNGs wurden mit dem eingebauten ImageGen-Werkzeug aus den Projekttexturen generativ erweitert. QROCK1/3/4/5 verwenden die bereits freigegebenen Erweiterungen. Die Originalmaterialien bleiben verfügbar.

## Verhalten

`UTNT_AreaTextures` ersetzt beim neuen Map-Start die ausgewählten Wand-, Boden- und Deckenzuweisungen anhand überprüfter Tabellen in `tutnt/areaalign`. Die WAD-Dateien, Skyboxen, Geometrie, Dinge, Specials und ACS-Programme werden nicht umgeschrieben. Die aktuelle Auswahl umfasst 98.491 ursprüngliche Zuweisungen in elf Maps; TITLEMAP und INTERMAP enthalten keine dieser Texturen. Vier zusätzliche sichtbare 3D-Wandzuordnungen und drei dynamische Sektor-Zuordnungen werden ebenfalls berücksichtigt.

Zusammenhängende Wandketten teilen fortlaufende U-Koordinaten und eine gemeinsame Höhenreferenz über Upper/Middle/Lower hinweg. Geschlossene Ringe, deren Umfang nicht zum Wiederholungsmaß passt, behalten eine ausdrücklich dokumentierte Übergangsstelle an ihrer stärksten Ecke. Verzweigungen beginnen eigene Ketten. Das ist keine Zusage einer mathematisch nahtlosen Abwicklung beliebiger geschlossener Geometrie.

Für Ebenen werden vollständige alte Wiederholungen aus den Panning-Offsets entfernt. Individuelle Rotation und Skalierung bleiben erhalten; unterschiedlich projizierte Nachbarflächen werden nicht zwanghaft vereinheitlicht. Die 3D-Floor-Steuersektoren verwenden dieselben neuen Materialien. Begrenzte zweiseitige Middle-Texturen erhalten horizontal erweiterte Ausschnitte mit ihrer ursprünglichen physischen Höhe.

Das physische Wiederholungsmaß liegt materialabhängig zwischen 320 und 1.024 Map-Einheiten. Es wurde im Vergleich mit den ursprünglichen Motivgrößen eingestellt und ist von der PNG-Auflösung getrennt. Acht Materialien überblenden zusätzlich nur einen schmalen periodischen Bildrand im Hardware-Renderer; das Innere wird unverändert abgetastet. Es gibt keine flächige Helligkeits- oder Farbmodulation. Die Software-Darstellung verwendet die generierten PNGs ohne diese zusätzliche Randüberblendung.

SLIME05B behält das vorhandene Flüssigkeitsmaterial, dessen Bewegung, Normal- und Höhenkarten sowie die bestehende Terrain-Zuordnung `UTNT_Lava`. Nur das Wiederholungsmaß seiner Farbabtastung wird angepasst. Die konkreten `ChangeFloor`-Aufrufe in TNT04B (TEKWALL4, Tag 31) und TNTLE (QROCK3, Tag 61) werden in drei Sektoren weiterverfolgt. Es findet kein permanenter Scan aller Flächen statt.

Die Änderungen werden ab einem neuen Map-Start aktiv. Danach gespeicherte Spielstände behalten die Materialzuweisungen und Offsets. Frühere Spielstände werden nicht nachträglich umgeschrieben.

## Schutz paralleler Änderungen

Die Tabellen prüfen Map-Größe, Wandendpunkte, Sektoren, ursprüngliche Texturen, Offsets und Skalierungen. Polyobjekte dürfen sich als starre Objekte gegenüber ihrer Editorposition verschieben. Unpassende Tabellen werden protokolliert statt blind angewendet. Drei optionale Einträge unterstützen die älteren TNT03B-Wandblenden; die inzwischen für die Skybox entfernten Blenden werden dadurch nicht wiederhergestellt.

## Erneute Erzeugung nach Map-Änderungen

Python mit Standardbibliothek genügt für den Tabellenbau. ACC, UZDoom und DOOM2.WAD werden explizit angegeben oder über `UTNT_ACC`, `UTNT_ENGINE`, `UTNT_IWAD` gesetzt.

```text
python tools/area-textures/rebuild.py --output <Arbeitsverzeichnis> --engine <uzdoom.exe> --iwad <DOOM2.WAD> --acc <acc.exe>
```

Das Werkzeug erzeugt einen unveränderlichen Test-Snapshot, misst die geladenen Maps in der Engine und schreibt neue Tabellen in `<Arbeitsverzeichnis>/addon/areaalign`. Erst `--apply` übernimmt diese Tabellen ins Projekt, nach erneutem Abgleich der Map-Hashes. Bildgeneration gehört nicht zum Tabellenbau; Materialien und Prompts liegen unter `tools/artwork/area-textures`.

## Prüfung

```text
python tools/area-textures/verify.py --root . --mod <tutnt.pk3> --engine <uzdoom.exe> --iwad <DOOM2.WAD> --output <Prüfverzeichnis>
```

Die Prüfung lädt alle 13 Maps, verlangt vollständige Annahme der Tabellen, testet Speichern/Laden und die dynamischen Texturwechsel und prüft auf Shaderfehler unter Vulkan und OpenGL. Statische Mappingwerte werden nach dem Laden verglichen; zuvor tatsächlich als laufend erkannte Scrollwerte werden gesondert gezählt. Optional vergleicht `--reference-geometry <Logverzeichnis>` die nativen Grenzen begrenzter Wandblenden mit dem ursprünglichen Stand.

Die separate lokale Übersicht enthält die 44 Materialien gruppiert nach Namen, Map-Zuordnungen und 43 per Raytrace geprüfte Vorher/Nachher-Aufnahmen. Für RROCK01 treffen die vorhandenen Audit-Kameras überdeckende Geometrie; dort wird die Materialvorschau ausdrücklich als solche gezeigt. Die Zuordnung selbst wurde über die native Sektorausgabe geprüft.

Technische Referenz für WorldPanning, Offset-Einheiten und die gerundeten Darstellungsgrößen: [GZDoom FTexCoordInfo](https://github.com/ZDoom/gzdoom/blob/master/src/common/textures/gametexture.cpp). Die Umsetzung und Prüfungen liefen mit UZDoom 5.0.1.
