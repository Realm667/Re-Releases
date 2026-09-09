# Korrektur vom 09.09.2026

13 Materialien wurden durch Outpainting eines einzelnen maßstäblichen Originalausschnitts auf transparenter Fläche neu generiert: QFLAT07, BRICK9, GRAVE01, ROCKF6, CITYF11, FLAT10, CITYF20, QFLAT04, ROCKF5, CITYF01, RROCK19, OSNOW und QTWALL11. Eine gekachelte Vorlage wurde verworfen, weil sie starke Wiederholungen weitergab. Die neuen Prompts verlangen eigenständige Strukturen, ursprüngliche Detailgrößen und zusammenpassende Außenkanten. OSNOW besitzt überprüfte periodische Außenkanten; QTWALL11 variiert die Anordnung der Technikmodule.

Die Wiederholungsprüfung misst Bildkorrelationen nach Verschiebungen um 64, 128 und 256 Map-Einheiten und entfernt vorher Zeilen-/Spaltenmittelwerte, um reguläre Mauerwerkslagen nicht mit kopierten Oberflächen gleichzusetzen. Alle 13 Neugenerierungen haben schwächere Korrelationsspitzen als die verworfene Generation. Das ist ein ergänzender Vergleich, kein allgemeiner Beweis visueller Qualität. Die Materialien wurden zusätzlich bei identischem physischem Maßstab und an den Kachelgrenzen betrachtet.

Elf Materialien übernehmen das ursprüngliche Pixelraster: ADEL_B14, ADEL_B15, ADEL_F48, ADEL_B01, ADEL_V99, ROCKF2, QWIZ, QBRICK6, QCHURCH, ADEL_M02 und QBRICK3. Die Originalpixel werden nicht verschoben oder skaliert. Oberflächendetails aus der vorherigen Generierung variieren nur innerhalb des ursprünglichen Farbsatzes und enger Helligkeitsgrenzen. Jeder strikte lokale Helligkeitsverlauf zu den acht Nachbarpixeln bleibt erhalten; die Exportprüfung verlangt null Richtungsänderungen. Damit bleiben die wiederkehrenden Fugen und Bauteilkonturen absichtlich erhalten.

Diese elf Materialien behalten außerdem die vom Mapper gesetzten UV-Offsets, Rotationen und Skalierungen. Die neuen P-Tabelleneinträge ersetzen nur das Material und kompensieren nötigenfalls die Höhenreferenz des Renderers. Dafür verwenden diese Texturen native Pixel-Offsets ohne WorldPanning. Boden- und Decken-Panning wird unverändert übernommen. Es findet für diese Gruppe kein erneutes Auto-Alignment statt.

ADEL_G04, CITYF19 und GRASS2 sind deaktiviert. Neue Map-Starts behalten ihre Originaltexturen und Original-Offsets. Die früheren Aliasnamen bleiben als Originalbilder definiert, damit bereits gespeicherte Spielstände keine fehlenden Texturen erhalten; ihre gespeicherten Offsets werden weiterhin nicht migriert.

Alle 41 aktiven Erweiterungen sind jetzt indizierte PNGs mit der vollständigen Basispalette aus der aktuellen Projekt-PLAYPAL. Die Palette selbst wird nicht überschrieben. Die Export- und Leseprüfung kontrolliert die PLTE-Bytes und jede tatsächlich verwendete Pixelfarbe. Gemeint sind die gespeicherten Albedo-Pixel; Beleuchtung, Flüssigkeitseffekte und Texturfilter der Engine berechnen weiterhin Zwischenfarben.

Der Exporter `tools/area-textures/export_palette.cjs` benötigt Node und `sharp`. Aufruf: `node export_palette.cjs <Original-Arbeitsverzeichnis> <Revisions-Arbeitsverzeichnis>`. Das erste Verzeichnis enthält `materials.json` und `originals/*.png`; das zweite `groups.json`, `PLAYPAL.pal`, die ImageGen-Ausgaben in `raw/` und die vorherigen Erweiterungen in `before/`. Es schreibt `assets/`, `materials.json` und `export-checks.json`. Prompts und Prüfergebnisse liegen in `tools/artwork/area-textures/revision-2026-09-09`.

# Erweiterte FlÃ¤chentexturen

44 ausgewÃ¤hlte Materialfamilien erhalten grÃ¶ÃŸere TexturflÃ¤chen und fortlaufende Wandkoordinaten. 40 PNGs wurden mit dem eingebauten ImageGen-Werkzeug aus den Projekttexturen generativ erweitert. QROCK1/3/4/5 verwenden die bereits freigegebenen Erweiterungen. Die Originalmaterialien bleiben verfÃ¼gbar.

## Verhalten

`UTNT_AreaTextures` ersetzt beim neuen Map-Start die ausgewÃ¤hlten Wand-, Boden- und Deckenzuweisungen anhand Ã¼berprÃ¼fter Tabellen in `tutnt/areaalign`. Die WAD-Dateien, Skyboxen, Geometrie, Dinge, Specials und ACS-Programme werden nicht umgeschrieben. Die aktuelle Auswahl umfasst 94.190 ursprÃ¼ngliche Zuweisungen in elf Maps; TITLEMAP und INTERMAP enthalten keine dieser Texturen. Vier zusÃ¤tzliche sichtbare 3D-Wandzuordnungen und drei dynamische Sektor-Zuordnungen werden ebenfalls berÃ¼cksichtigt.

ZusammenhÃ¤ngende Wandketten teilen fortlaufende U-Koordinaten und eine gemeinsame HÃ¶henreferenz Ã¼ber Upper/Middle/Lower hinweg. Geschlossene Ringe, deren Umfang nicht zum WiederholungsmaÃŸ passt, behalten eine ausdrÃ¼cklich dokumentierte Ãœbergangsstelle an ihrer stÃ¤rksten Ecke. Verzweigungen beginnen eigene Ketten. Das ist keine Zusage einer mathematisch nahtlosen Abwicklung beliebiger geschlossener Geometrie.

FÃ¼r Ebenen werden vollstÃ¤ndige alte Wiederholungen aus den Panning-Offsets entfernt. Individuelle Rotation und Skalierung bleiben erhalten; unterschiedlich projizierte NachbarflÃ¤chen werden nicht zwanghaft vereinheitlicht. Die 3D-Floor-Steuersektoren verwenden dieselben neuen Materialien. Begrenzte zweiseitige Middle-Texturen erhalten horizontal erweiterte Ausschnitte mit ihrer ursprÃ¼nglichen physischen HÃ¶he.

Das physische WiederholungsmaÃŸ liegt materialabhÃ¤ngig zwischen 320 und 1.024 Map-Einheiten. Es wurde im Vergleich mit den ursprÃ¼nglichen MotivgrÃ¶ÃŸen eingestellt und ist von der PNG-AuflÃ¶sung getrennt. Acht Materialien Ã¼berblenden zusÃ¤tzlich nur einen schmalen periodischen Bildrand im Hardware-Renderer; das Innere wird unverÃ¤ndert abgetastet. Es gibt keine flÃ¤chige Helligkeits- oder Farbmodulation. Die Software-Darstellung verwendet die generierten PNGs ohne diese zusÃ¤tzliche RandÃ¼berblendung.

SLIME05B behÃ¤lt das vorhandene FlÃ¼ssigkeitsmaterial, dessen Bewegung, Normal- und HÃ¶henkarten sowie die bestehende Terrain-Zuordnung `UTNT_Lava`. Nur das WiederholungsmaÃŸ seiner Farbabtastung wird angepasst. Die konkreten `ChangeFloor`-Aufrufe in TNT04B (TEKWALL4, Tag 31) und TNTLE (QROCK3, Tag 61) werden in drei Sektoren weiterverfolgt. Es findet kein permanenter Scan aller FlÃ¤chen statt.

Die Ã„nderungen werden ab einem neuen Map-Start aktiv. Danach gespeicherte SpielstÃ¤nde behalten die Materialzuweisungen und Offsets. FrÃ¼here SpielstÃ¤nde werden nicht nachtrÃ¤glich umgeschrieben.

## Schutz paralleler Ã„nderungen

Die Tabellen prÃ¼fen Map-GrÃ¶ÃŸe, Wandendpunkte, Sektoren, ursprÃ¼ngliche Texturen, Offsets und Skalierungen. Polyobjekte dÃ¼rfen sich als starre Objekte gegenÃ¼ber ihrer Editorposition verschieben. Unpassende Tabellen werden protokolliert statt blind angewendet. Drei optionale EintrÃ¤ge unterstÃ¼tzen die Ã¤lteren TNT03B-Wandblenden; die inzwischen fÃ¼r die Skybox entfernten Blenden werden dadurch nicht wiederhergestellt.

## Erneute Erzeugung nach Map-Ã„nderungen

Python mit Standardbibliothek genÃ¼gt fÃ¼r den Tabellenbau. ACC, UZDoom und DOOM2.WAD werden explizit angegeben oder Ã¼ber `UTNT_ACC`, `UTNT_ENGINE`, `UTNT_IWAD` gesetzt.

```text
python tools/area-textures/rebuild.py --output <Arbeitsverzeichnis> --engine <uzdoom.exe> --iwad <DOOM2.WAD> --acc <acc.exe>
```

Das Werkzeug erzeugt einen unverÃ¤nderlichen Test-Snapshot, misst die geladenen Maps in der Engine und schreibt neue Tabellen in `<Arbeitsverzeichnis>/addon/areaalign`. Erst `--apply` Ã¼bernimmt diese Tabellen ins Projekt, nach erneutem Abgleich der Map-Hashes. Bildgeneration gehÃ¶rt nicht zum Tabellenbau; Materialien und Prompts liegen unter `tools/artwork/area-textures`.

## PrÃ¼fung

```text
python tools/area-textures/verify.py --root . --mod <tutnt.pk3> --engine <uzdoom.exe> --iwad <DOOM2.WAD> --output <PrÃ¼fverzeichnis>
```

Die PrÃ¼fung lÃ¤dt alle 13 Maps, verlangt vollstÃ¤ndige Annahme der Tabellen, testet Speichern/Laden und die dynamischen Texturwechsel und prÃ¼ft auf Shaderfehler unter Vulkan und OpenGL. Statische Mappingwerte werden nach dem Laden verglichen; zuvor tatsÃ¤chlich als laufend erkannte Scrollwerte werden gesondert gezÃ¤hlt. Optional vergleicht `--reference-geometry <Logverzeichnis>` die nativen Grenzen begrenzter Wandblenden mit dem ursprÃ¼nglichen Stand.

Die separate lokale Ãœbersicht enthÃ¤lt die 44 Materialien gruppiert nach Namen, Map-Zuordnungen und 43 per Raytrace geprÃ¼fte Vorher/Nachher-Aufnahmen. FÃ¼r RROCK01 treffen die vorhandenen Audit-Kameras Ã¼berdeckende Geometrie; dort wird die Materialvorschau ausdrÃ¼cklich als solche gezeigt. Die Zuordnung selbst wurde Ã¼ber die native Sektorausgabe geprÃ¼ft.

Technische Referenz fÃ¼r WorldPanning, Offset-Einheiten und die gerundeten DarstellungsgrÃ¶ÃŸen: [GZDoom FTexCoordInfo](https://github.com/ZDoom/gzdoom/blob/master/src/common/textures/gametexture.cpp). Die Umsetzung und PrÃ¼fungen liefen mit UZDoom 5.0.1.
