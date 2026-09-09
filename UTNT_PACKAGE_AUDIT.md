# Paketverlust am 09.09.2026

## Ursache und Umfang

Die fehlende QLAVA-Verbesserung wurde nicht aus dem Arbeitsverzeichnis gelöscht.
Das gemeinsame Spielpaket wurde durch ein Paket aus einem anderen Quellumfang
ersetzt. Das lokale `source-focus/build_release.py` exportierte mit `git archive`
ausschließlich Commit `ee303644993885c77188a49907dc8eec1518882e`. Anschließend
prüfte `source-focus/publish_release.py` den Source-Endgegner in TNT04CN und
ersetzte die gemeinsame `tutnt.pk3` atomar durch dieses Paket. Der Build war für
seinen exportierten Quellstand korrekt; vor dem Ersetzen fehlte ein Vergleich
mit den bereits integrierten, noch nicht eingecheckten Änderungen.

Das war ein Fehler im Integrations- und Veröffentlichungsablauf. Ein sauberer
Git-Stand allein belegt nicht, dass ein Paket alle zuvor enthaltenen Arbeiten
enthält. Der gezielte Boss-Test konnte diesen Verlust nicht feststellen.

Belegte Paketfolge (Build-Kennungen aus `UTNTBLD`):

| Paket | Build | Quellstand | SHA-256 |
| --- | --- | --- | --- |
| vorheriges Gesamtpaket, `tutnt-tntle.pk3` | `fc1532bc4bc8` | `d2b3dd236409`, mit lokalen Änderungen | `e78eed96d48be490a18bab6a72c715d7c321df596ea64e5452f97183420a1790` |
| danach installiert, ca. 21:54 Uhr | `83f6cc30babc` | `ee3036449938`, ohne lokale Änderungen | `0bb7f6a50dc881fe61c64b2aa9622c582f38e40cd4d59a71b65c0412d8da0157` |
| geprüftes Korrekturpaket | `53a184edb3a6` | `288ca6f713f8`, mit lokalen Änderungen | `acb1d647bdc793d0ced5e117957fba1c85ebb37c886dfd5be4ae9563caf23d2c` |

Das lokale Release-Buildprotokoll und die Veröffentlichungsbestätigung des
Source-Tasks stimmen mit Build, Commit und Hash des fehlerhaften Pakets überein.

## Weitere bestätigte Rückschritte

Verglichen wurden das vorherige Gesamtpaket, das danach installierte Paket und
die erhaltenen Arbeitsdateien. Bestätigt sind diese Gruppen:

* **Lava:** vier fehlende Ressourcen (`GLDEFS.lava`, zwei Shader und die
  Krustenhöhenkarte), fehlender GLDEFS-Include und wieder aktive alte Warps für
  QLAVA, QLAVA2 und QLAVASB. Damit fehlten Oberfläche und neue Lavafall-Darstellung.
* **34 hochauflösende Grafiken:** Titel, Credits, Zwischen- und Abschlussbilder
  unter `hires/graphics/interms`. Die vollständige Liste steht im Prüfprotokoll.
* **Terror-Flammenpartikel:** Die Erweiterung des Lost-Soul-Effekts auf Terror
  und dessen eigene orange/bernsteinfarbene Partikel fehlten in `TEXTURES.fire`
  und `zscript/UTNT_Fire.zc`.
* **TNT03B:** 13 zusätzliche `HeatEffectGiver`-Objekte und die Entfernung von
  zehn alten mittleren Wandtexturen waren nicht enthalten. Geometriezahlen,
  Sektoren, ACS und Nodes sind zwischen diesen beiden Versionen unverändert.
  Zusätzlich entfielen drei explizite Nullargumente einer Linie, ohne
  funktionale Wirkung.
* **Farbpalette:** Die lokale PLAYPAL-Version wurde durch die Git-Version
  ersetzt: 14 statt 15 Paletten, mit Abweichungen in allen 14 gemeinsamen
  Paletten. Der Vergleich belegt den Versionswechsel, bewertet aber nicht
  pauschal dessen ästhetische Wirkung.

Es wurden 38 entfernte Ressourcen gefunden (34 Grafiken plus vier Lava-Dateien).
Alle 38 sowie die vier geänderten Dateien für Palette, Terror und TNT03B stimmen
im geprüften Korrekturpaket wieder mit dem vorherigen Gesamtpaket überein.
Die Lava-Einbindung wird zusätzlich durch den Paket-Laufzeittest geprüft.
Die neueren eingecheckten Source- und Portalverbesserungen bleiben enthalten;
es wurde ausdrücklich kein altes Gesamtpaket zurückkopiert.

Zeilenende-/Formatänderungen, umsortierte Includes, doppelte Kommentare und
`PLAYPAL.pal.bak` zählen nicht als verlorene Verbesserungen. Nach dem betroffenen
Build neu entstandene Arbeiten, insbesondere an Cursed Peak und Fähigkeitstönen,
sind ebenfalls keine Belege für diesen Paketverlust. Die Prüfung erfasst alle
Ressourcen der genannten Vergleichspakete, aber keinen vollständigen historischen
Nachweis jeder jemals besprochenen Idee oder einen Kampagnen-Durchlauf.

## Wiederherstellung und Absicherung

Die vorhandene freigegebene Lava wird samt Einbindung und Regressionstest mit
der TNTLE-Korrektur eingecheckt. Die übrigen bestätigten lokalen Verbesserungen
werden aus dem gemeinsamen Arbeitsverzeichnis wieder ins Gesamtpaket aufgenommen.
Ihre fremden Änderungen und bereits gestagten Dateien werden nicht in diesen
Commit übernommen. Sie sind damit wieder spielbar, teilweise aber weiterhin
nur lokal beziehungsweise gestagt vorhanden: Ein reiner Commit-Build wäre bis
zu deren regulärem Abschluss weiterhin kein vollständiger Integrationsstand.

Für die gemeinsame `tutnt.pk3` gilt deshalb: aus dem aktuellen gemeinsamen
Arbeitsverzeichnis über `tools/build_utnt.py` bauen und mit Engine-Prüfung
veröffentlichen. Isolierte Commit-/Task-Builds erhalten eigene Dateinamen und
dürfen das Gesamtpaket nicht ohne Ressourcenvergleich ersetzen. Diese Regel
wird zusätzlich in den lokalen Repository-Arbeitsanweisungen festgehalten.
Sie ist eine Arbeitsablaufregel, keine Betriebssystem-Sperre gegen fremde
Kopierskripte.

Die Skybox-Linien haben eine separate Ursache: implizite Mipmap-Auswahl an
diskontinuierlichen Shader-Samplekoordinaten. Details und die ergänzende
Skybox-AO-Konfiguration stehen in `UTNT_TNTLE_SKY_FIXES.md`.
Messwerte, unveränderte Engine-Aufnahmen und die Ressourcenvergleiche liegen
unter `tools/validation/tntle-material-fix-2026-09-09`.
