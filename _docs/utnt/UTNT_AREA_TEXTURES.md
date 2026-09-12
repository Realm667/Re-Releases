# Weitere Originalkorrekturen vom 10.09.2026

Alle erweiterten Bilddateien liegen einheitlich unter tutnt/patches/area-expanded/. Dazu gehören auch QROCK1X8.png, QROCK3X8.png, QROCK4X8.png und QROCK5X8.png. Die Texturaliase, Bilddaten, Skalierung und Map-Zuweisungen bleiben beim Verzeichniswechsel unverändert; die Regenmaterialien verwenden ebenfalls die neuen Bildpfade.

GROUND2 und GROUND3 haben neue, feinere Bodenstrukturen mit an den Originalen abgeglichenen Farbtönen. ADEL_B01 zeigt wieder die Mischung aus braunen und fast schwarzen Ziegeln: Originalkörnung und Originalfugen bleiben erhalten, Steinvarianten werden unregelmäßig verteilt und durch generierte Details ergänzt. Das Ziegelraster bleibt exakt 32 × 16 Pixel. ROCKF2 erhält ein neues Netz kleiner polygonaler Steine; der bisherige 64-Pixel-Verbund wird nicht mehr wiederholt. Die Einzelkonturen ändern sich bewusst, die typische Steingröße bleibt am Original orientiert.

Die vier Erweiterungen sind 512 × 512 Pixel bei 512 × 512 Map-Einheiten. GROUND2/3 und ROCKF2 verwenden periodische Überlappungsschnitte entlang möglichst ähnlicher Pixel statt weich überblendeter Randstreifen. ADEL_B01 erhält seine originalen Fugenpixel auch an den Außenkanten. Die vorhandenen Wandketten-Zuordnungen bleiben erhalten; ADEL_B01 und ROCKF2 behalten die vom Mapper gesetzten UV-Offsets.

OBROWN1 ist deaktiviert und pixelgleich wiederhergestellt. Neue Map-Starts verwenden Originalmaterial und Original-Offsets. Historische Aliasse bleiben als Originalbilder für gespeicherte Spielstände definiert; alte gespeicherte Offsets werden nicht migriert. Damit sind 37 Erweiterungen aktiv und sieben Materialien zurückgesetzt; 88,334 ursprüngliche Flächenzuweisungen bleiben erfasst.

Alle fünf Exporte verwenden die aktuelle PLAYPAL. Die Bildprüfung vergleicht Palette, OBROWN1-Pixel, geschützte ADEL_B01-Fugen und Randdifferenzen; 2×2-Kachelansichten ergänzen die Zahlenprüfung. ROCKF2s Korrelation bei 64 Pixel Verschiebung sinkt von etwa 0,96 auf nahe null. Die regulären ADEL_B01-Fugen bleiben erwartungsgemäß periodisch. Prompts, Originalreferenzen, Rohbilder und reproduzierbarer Export: tools/artwork/area-textures/refinement-2026-09-10 und tools/area-textures/export_refinements.cjs.

Die Paketprüfung bestand in allen 13 Maps: vollständige Annahme der Materialtabellen, Speichern/Laden, dynamische Texturwechsel und Shaderprüfung mit Vulkan/OpenGL. Die gezielte Paketprüfung bestätigt alle sieben geänderten Spielressourcen. Eine neue separate Messung begrenzter Wandblenden war nicht Teil dieses Durchlaufs.

Die folgenden Abschnitte dokumentieren vorherige Revisionen.

# Aktueller Stand vom 10.09.2026

QGRASS, ADEL_V99 und ADEL_M02 verwenden wieder ihre Originalbilder. Ihre Ersetzungs- und Ausrichtungszeilen wurden entfernt. TNT02 war ausdrücklich eine irrtümliche Listenzeile und wurde nicht als Map zurückgesetzt; die materialbezogenen Rücksetzungen gelten auch dort. Zusammen mit ADEL_G04, CITYF19 und GRASS2 bleiben jetzt sechs Materialien im Original. Es sind 38 Erweiterungen mit 88,635 ursprünglichen Wand-/Boden-/Deckenzuweisungen aktiv.

ADEL_B14, ADEL_B15, ADEL_F48, ADEL_B01, QBRICK3, QBRICK6, QWIZ und QCHURCH haben neu generierte Steinoberflächen. Im Gegensatz zur vorherigen Revision werden ihre feinen Originaldetails nicht mehr durch unveränderte Nachbargradienten festgehalten. Ein einzelner Ausschnitt aus dem Steininneren dient als Outpainting-Referenz. Der Export setzt dieses neue Material innerhalb von Masken im nativen Originalraster ein; geschützte Fugenpixel bleiben bytegleich im dekodierten RGB-Bild. Die Masken orientieren sich an den ursprünglichen Mauerwerkslagen und Fugen. Bei den Q-Materialien bleibt zusätzlich die geglättete Formschattierung erhalten. Außenkonturen und Bauteilgrößen bleiben dadurch am Original ausgerichtet, während die Innenflächen neue Poren, Brüche und Abnutzung erhalten. Die bestehenden P-Zuweisungen und UV-Offsets bleiben unverändert.

COMPBLUE hat ein neues, unregelmäßigeres Leiterbahnnetz. Alle zwölf geänderten Bilder sind indizierte PNGs mit der Projekt-PLAYPAL. Die drei Rücksetzungen sind pixelgleich zu den Originalbildern; historische Aliasse bleiben für gespeicherte Spielstände definiert. Für die ursprünglichen Map-Offsets ist ein neuer Map-Start erforderlich.

Die Bildprüfung kontrolliert Palette, geschützte Fugenpixel, die drei Original-Rücksetzungen und COMPBLUEs periodische Außenkanten. Die Korrelation innerhalb der Steinflächen bei Verschiebung um die alte Kachelgröße sank bei allen acht Steinen; regelmäßige Fugen und Formschattierung bleiben absichtlich erhalten. Die Messung ergänzt die visuelle Prüfung, ersetzt sie aber nicht. Prüfdaten und Prompts: `tools/artwork/area-textures/variation-2026-09-10`.

Der Export ist mit `node tools/area-textures/export_interiors.cjs <Original-Arbeitsverzeichnis> <Varianten-Arbeitsverzeichnis>` reproduzierbar; benötigt werden Node, sharp, originals/*.png, materials.json, materials-before.json, groups.json, PLAYPAL.pal und die neun ImageGen-Rohbilder unter raw/. Masken werden beim Export erzeugt. Map-WADs und Skybox-Ressourcen gehören nicht zu dieser Änderung.

Die folgenden Abschnitte dokumentieren die früheren Ausbaustufen; dieser Abschnitt beschreibt die aktuellen Überschreibungen.

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
