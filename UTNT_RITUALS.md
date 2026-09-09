# Bernsteinfarbene Portale und Teleporter

Die freigegebene Fassung übernimmt das warme Bernstein/Orange des Portalmockups
und die gebrochenen Siegelringe des Bosskonzepts. Der schwarze Tiefenspalt und die
asymmetrischen Energiefalten bleiben erhalten. Auf ausdrücklichen Wunsch sind die
Rahmenrunen und fliegenden Zeichen stärker orange als die Portalfläche.

## Grafikquellen und Materialien

- Die vier Runen stammen unverändert aus `QRUNT63`, dem originalen TNT03B-Portal.
  `TEXTURES.teleport` schneidet die vier 32×32-Zeichen direkt aus der vorhandenen
  Grafik. `UTRUNES` ist dieselbe Quelle für die Ringzeichen. Keine neue Symbolschrift.
- `ritual-rune.fp` färbt die Partikelsilhouetten; `ritual-stone.fp` färbt nur die
  roten Leuchtanteile von `QRUNT62/63` und den zugehörigen `QSLIP1–5`-Wänden.
  Originale Steinstruktur, Alpha und Positionen bleiben erhalten.
- `ritual-pad.fp` kombiniert das bestehende Dämonensiegel `SOURA0` mit unterteilten,
  bewegten Ringen und Originalrunen. Eine neue Textur `UTPSEAL` wird auf den ganzen
  Teleporterboden eingepasst, statt auf jeder ursprünglichen 64er-Kachel wiederholt.
- `portal.fp` erhält sein dreischichtiges Faltenmaterial, abgeleitete Normalen und
  blickabhängige Parallaxe. Zwei gegeneinander versetzte Runenringsegmente ergänzen
  die Tiefe. Licht und Nahbereichsfäden verwenden passende Bernstein-/Orangetöne.

## Reichweite und Skripte

Die bestehende Portalzuordnung umfasst 117 mittlere Wandsegmente in ENDMAP01,
TNT03B, TNT04A, TNT04B, TNT04C und TNT04CN, einschließlich schmaler Bogensegmente.
128er und 192er-Dekorationen benutzen dieselben Originalrunen. Die vergrößerte
Einzugsfläche, explizite Aktivierung/Deaktivierung, direkte Annäherung mit Noclip/Fly
und der bei 128 Mapeinheiten beginnende Sichtfeldeffekt bleiben erhalten.

18 rote `TeleportSparkle_R` in TNT01, TNT02, TNT03A2, TNT04A, TNT04B, TNT04C,
TNT04CN und TNTLE emittieren aufsteigende, gekrümmt umlaufende Runen. Ihre Qualität,
Sichtweite und Emissionsbudgets folgen den bestehenden Effektoptionen. Andere
Sparkle-Farbklassen und der anderweitig verwendete Glutsplitter-Atlas bleiben erhalten.
Ankunfts-/Abgangseffekte erhalten ebenfalls passende Farben und eigene Lichtdefinitionen.

`UTNTRitualPads` prüft einmal pro Sekunde die beiden Bodenfamilien QSLIP1–7 und
QSLIPP1–7. Alle Einstiegsframes werden erfasst, auch wenn ein Skript sie später
zuweist. Die Originalskalierung, Verschiebung und Drehung werden im EventHandler
gespeichert. Ersetzt ein Skript den Boden durch ein anderes Material, wird dessen
ursprüngliche Zuordnung wiederhergestellt; explizite UV-Änderungen des Skripts haben
Vorrang. Entfernte Böden werden nicht wieder als Teleporter eingeschaltet.

Die Zuordnung betrifft ausschließlich diese Bodenfamilien und geeignete Sektoren
von 32 bis 512 Einheiten pro Achse. Der separate, per Skript aktivierte GATE2-Teleporter
in TNTLE und eigenständige QRUNE-Schalter gehören nicht zu dieser roten Portalfamilie.

## Prüfung

`tools/test_rituals.py` prüft die acht Teleporterkarten, alle 14 Einstiegsframes,
Skriptwechsel einschließlich UV-Wiederherstellung, Speichern/Laden, Originalglyphen,
Aktivierung/Deaktivierung und deaktivierte Effektqualität. Der detaillierte TNT01-Test
läuft mit OpenGL und Vulkan. Die bestehenden Portaltests prüfen zusätzlich Annäherung,
Nahbereichseffekt, Verdeckung und die 128er/192er-Dekorationen.

Die Darstellung verwendet UZDoom-Hardwarematerialien (OpenGL/Vulkan). Abgeschaltete
optionale Partikel/Posteffekte lassen die Portal-/Bodenmaterialien bestehen; ein
vollständiger Software-Renderer-Look ist nicht Teil dieser Shaderumsetzung.
