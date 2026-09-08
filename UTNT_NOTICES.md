# UTNT: schmale Hinweisleiste

Kleinere Spielhinweise und fehlende Tür-/Schalterschlüssel verwenden dieselbe zurückhaltende Leiste: horizontal zentriert bei 40 % der Bildschirmhöhe, dunkler transparenter Hintergrund, feine Bronzekanten und eine kleine Raute. Die vorhandene SmallFont und Objective-Hintergrundtextur verbinden sie mit dem übrigen HUD. Bildschirmmitte, Waffen und Statusleiste bleiben frei.

## Verhalten

- Einblenden in 7 Tics (0,2 s), abhängig von der Textlänge 3–5 s lesen, Ausblenden in 11 Tics (ca. 0,3 s).
- Gleiche aktive oder wartende Hinweise erscheinen nur einmal. Zähler derselben Aufgabe aktualisieren ihren vorhandenen Eintrag. Verschiedene Nachrichten werden nacheinander gezeigt.
- Während der großen Objective-Anzeige mit O, im Menü und in der Konsole wartet die Leiste. Nach Loslassen von O erscheint der verbleibende Hinweis wieder.
- Die Leiste ist lokaler, flüchtiger UI-Zustand. Kartenwechsel und Laden eines Spielstands entfernen alte Hinweise. Gespeicherter Objective-Fortschritt bleibt davon unabhängig.
- Keine zusätzlichen Hinweistöne. Der originale Fehlversuchston verschlossener Türen bleibt erhalten.

## Texte und Integration

`LANGUAGE.notices` enthält englische und deutsche Kurztexte; `TEXTCOLO.notices` definiert Bronze und warmes Grau. 137 aktive Print-/PrintBold-Stellen in zehn Kampagnenkarten sowie der gemeinsame Checkpoint-Hinweis rufen `UTNTWorldHandler.BeginNotice` auf. Der ursprüngliche Empfänger und sämtliche numerischen Zählerausdrücke bleiben erhalten: `PlayerNumber()` entspricht Print, `-2` dem Broadcast von PrintBold. `-1` ist kein Broadcast.

Schlüsselnamen stehen ebenfalls in LANGUAGE, einschließlich des Farbwechsels zurück zum normalen Text: `\c[Red]`, `\c[LightBlue]`, `\c[Yellow]`, anschließend `\c[UTNTNoticeBody]`. LightBlue bleibt auf UTNTs dunklem Hintergrund besser lesbar als die im Mod bereits überschriebene Blue-Translation. Benannte Farben vermeiden Verwechslungen mit Buchstabencodes: `\cR` bezeichnet laut Wiki Dunkelrot.

### Native Schlösser

`WorldLinePreActivated` prüft bekannte Doom-Schlösser mit dem nativen `Actor.CheckKeys(..., quiet=true)`. Erfolgreiche Prüfungen laufen über die unveränderte Engine-Aktion weiter. Bei einem Fehlschlag führt `CheckKeys(..., quiet=false)` den originalen Meldungs-/Soundpfad einmal aus; ein lokales Interface-Event ersetzt dessen `CNTR`-HUDMessage durch die Leiste und verhindert anschließend die gesperrte Aktion. SBARINFO, Inventar, LOCKDEFS und Tür-/Schalterargumente werden nicht geändert. Die originale Konsolenausgabe bleibt erhalten.

Erfasst werden `Line.locknumber`, Door_LockedRaise, Door_Animated, ACS_LockedExecute, ACS_LockedExecuteDoor und Generic_Door. Die IDs 1–6, 100–101, 129–134 und 228–229 verwenden 32 lokalisierte Tür-/Schaltervarianten. Unbekannte Schloss-IDs behalten die Engine-Ausgabe.

Grundlagen: [UZDoom Schlüsselprüfung](https://github.com/UZDoom/UZDoom/blob/trunk/src/gamedata/a_keys.cpp), [native Line-Aktivierung](https://github.com/UZDoom/UZDoom/blob/trunk/src/playsim/p_spec.cpp), [C_MidPrint und CNTR](https://github.com/UZDoom/UZDoom/blob/trunk/src/g_statusbar/hudmessages.cpp), [Wiki: Textfarben](https://zdoom.org/wiki/Print#Colors), [Wiki: LOCKDEFS](https://zdoom.org/wiki/LOCKDEFS).

## Prüfung

`tools/test_minor_notices.py` prüft in UZDoom Zustellung, Empfänger, Warteschlange, Duplikate, Zähler, Einblendung, O sowie Save/Load. `--mode locks` verwendet echte TNT02-Linien mit testweise gesetzten Schlossargumenten und die native `Line.Activate`-Methode: alle sechs Karten-/Schädeltypen, richtige und fehlende Schlüssel, Karte gegen Schädel, alternative Karten-/Schädelschlösser, ACS-Schlösser und `Line.locknumber`. Die Test-Erweiterung wird nicht mit dem Mod ausgeliefert.

`tools/test_minor_notice_contracts.py` vergleicht gegen den unveränderlichen Ausgangscommit: sämtliche Map-Lumps außer SCRIPTS/BEHAVIOR sowie alle ACS-Anweisungen außerhalb der Meldungsadapter müssen identisch sein. Das Manifest dokumentiert jede geänderte Stelle. Alle 14 ACS-Module werden mit ACC kompiliert und das Paket von UZDoom geladen.

Laufzeitnachweise für Englisch/Deutsch und Vulkan/OpenGL liegen unter `tools/validation/minor-notices-2026-09-08`. Diese gezielten Prüfungen ersetzen keinen vollständigen Kampagnen- oder Mehrspieler-Durchlauf.
