# Gezieltes Kampfglühen

Stand: 11.09.2026. Farbige, weiche Leuchthöfe ergänzen Projektile und
Explosionskerne. Die Originalsprites und ihre Animationen bleiben erhalten.
Der Materialshader `shaders/effect-glow.fp` arbeitet nur auf den zusätzlichen
Leuchthöfen; es gibt keinen Helligkeitsfilter über das Bildschirmbild.
Engine-Bloom wird weder vorausgesetzt noch umgestellt.

## Bedienung

Unter **UTNT-Optionen → Kampfrückmeldung**:

| Einstellung | Konsole | Vorgabe / Bereich |
|---|---|---|
| Projektil- und Explosionsglühen | `UTNT_effectglow` | Ein |
| Leuchtstärke | `UTNT_glowstrength` | 0,65 / 0–1 |
| Leuchtgröße | `UTNT_glowsize` | 1 / 0,5–1,75 |

Überarbeitung vom 10.09.2026: Der Grunddurchmesser beträgt jetzt das Doppelte
der ersten Fassung. Bei unveränderten Reglerwerten verdoppelt sich außerdem
die additive Intensität; bei maximaler Leuchtstärke reicht der Alpha-Wert
jetzt bis 1,0 statt 0,5. Quelltransparenz und Entfernung schwächen das Glühen
weiterhin ab. Die Beispiele verwenden Stärke 1 und Größe 1.

Farbkorrektur vom 11.09.2026: Der Materialshader übernimmt die zugeordnete
Projektil-/Explosionsfarbe über `getTexel`, statt weißes RGB zurückzugeben.
Damit bleiben etwa Plasma-Leuchthöfe blau, Baron-Leuchthöfe grün und
Feuer-/Raketen-Leuchthöfe orange, auch bei maximaler Stärke. Die größere
Ausdehnung und erhöhte Maximalhelligkeit bleiben erhalten.

Die Werte gelten lokal pro Spieler. Effektqualität 0, Entfernung 0, Stärke 0
oder der Ausschalter entfernen die Leuchthöfe. Die bestehenden Einstellungen
für Effektqualität, reduzierte Effekte und Entfernung werden berücksichtigt.
Die Profile verwenden dezentes Glühen bei „Originalgefühl“, die normale Stärke
bei „Atmosphärisch“ und schalten es bei „Reduzierte Effekte“ aus. Einzelne
Regler können danach wieder angepasst werden.

## Abdeckung und Darstellung

- Spielerwaffen: Raketenflamme, Plasma, BFG und Flammenwerfer einschließlich
  Bodenflammen; die Raketenexplosion erhält einen gemeinsamen Leuchthof.
- Klassische Gegner: Imp-, Caco-, Baron-, Arachnotron-, Revenant- und
  Mancubus-Projektile sowie ihre im Mod vorhandenen Ableitungen.
- Zusätzliche Gegner: Dark Imp, Catharsi, Imp Warlord, Snake Imp, Cacolantern,
  Belphegor, Hell Guard, Soul Harvester, Hell Warrior, Afrit, Tortured Soul,
  Shadow, Hells Fury, Plasma Elemental, Hectebus, Bruiser, Dragon Familiar,
  TNT Spider sowie Queen-/Source-Projektile.
- Explosionen: New-/MonExplosion-Familien, Raketen- und BFG-Kerne,
  eigenständige Caco-, Baron-, Dark-Seeker- und Red-Skull-Explosionen sowie
  die großen PB-Explosionskerne. Benachbarte PB-Kerne teilen sich einen
  repräsentativen Leuchthof; kleine Begleitfragmente erhalten keinen zweiten.

Die Zuordnung steht zentral in `UTNTEffectGlow.Profile`. Neue, unabhängig
abgeleitete Angriffsklassen werden dort bewusst ergänzt. Rauch, Hülsen,
dekorative Fackeln, Umgebungs-Kometen, Gegenstände, HUD und helle
Wand-/Bodenflächen lösen das System nicht aus. Bestehendes Umgebungslicht
und dynamische Lichter gehören weiterhin zu ihren bisherigen Systemen.

Die Leuchthöfe folgen Spritegröße, Mittelpunkt und Transparenz. Die Raketen-
flugflamme sitzt hinter dem Geschoss; Explosionen verwenden einen kurzen
abklingenden Kern. Sehr nahe Effekte und die letzte Strecke vor der
Entfernungsgrenze werden weich ausgeblendet. Normale Weltgeometrie verdeckt
die als Weltobjekte gerenderten Leuchthöfe.

Beim Verschwinden einer Quelle oder beim Wechsel in einen nicht mehr
leuchtenden Zustand klingt ihr zuletzt sichtbarer Leuchthof über neun
Spielticks (Ziel 0,25 Sekunden, bei 35 Hz etwa 0,257 Sekunden) mit einer weichen Kurve aus. Position,
Größe und Farbe bleiben dabei erhalten. Erneutes Leuchten desselben Actors
übernimmt wieder direkt die aktuelle Darstellung. Einfrieren pausiert auch
den Fadeout; Ausschalter, Stärke 0, Entfernung und Qualitätsbudget greifen
weiterhin unmittelbar. Ausblendende Leuchthöfe zählen zum gleichen Budget.

## Technik und Grenzen

`UTNTEffectGlowHandler` ist ein zustandsloser `StaticEventHandler`, damit auch
Spielstandladen die lokalen Registrierungen wieder aufbaut. Registrierung,
Budgets und `VisualThinker` liegen ausschließlich in der Client-Thinkerliste.
Kein Effekt verändert Schaden, Kollision, Geschwindigkeit, Actor-Zustände oder
den Gameplay-Zufallsstrom. Eine Registrierung funktioniert auch bei zunächst
ausgeschalteten Effekten oder zunächst zu großer Entfernung.

Es gibt höchstens 1.024 registrierte Quellen und je nach Qualität höchstens
48/96/160 Leuchthöfe. Diese eigene Obergrenze verbraucht nicht das Budget der
vorhandenen Kampfpartikel. Bei Überlast entfallen zusätzliche Leuchthöfe;
die Originaleffekte bleiben bestehen. Dies ist eine gezielte Annäherung an
Bloom mit weichen Welt-Sprites, kein separater Emissions-Renderpass der Engine.
Der 64×64-Sprite enthält dieselbe analytische Form als Fallback ohne Shader.
Die größere Ausdehnung erhöht die überzeichnete Pixelfläche je Leuchthof;
die Anzahl der VisualThinker und ihre Qualitätsgrenzen bleiben gleich.

## Prüfung

`tools/test_effect_glow.py` prüft die Klassenabdeckung, unerwünschte
Umgebungsquellen, Ein/Aus und Regler, Qualitäts- und Entfernungsgrenzen,
unveränderte Quellobjekte, Wiederherstellung nach Laden, Explosionen,
Bereinigung und eine Überlast mit 180 Projektilen. `--renderer 0` verwendet
OpenGL, `--renderer 1` Vulkan. Die vorhandene industrielle Testkarte wird
in einem lokalen Addon unter `.codex/work/effect-glow/` wiederverwendet.
Logs und Screenshots liegen unter `.codex/logs/`, Ergebnisberichte unter
`.codex/validation/effect-glow/`. Das Test-Addon wird nicht mit ausgeliefert.

`tools/build_effect_glow.py --check` verifiziert den reproduzierbaren Sprite.
Lokalisierungsprüfungen decken Englisch, Deutsch, Spanisch und Französisch
einschließlich der verwendeten Originalschriften ab.

Prüfung der ersten Fassung vom 10.09.2026: UZDoom 5.0.1 besteht mit dem gemeinsamen
PK3-Build `744279928cd4` jeweils 443 native Assertions unter OpenGL und Vulkan.
Alle 13 zum Glühen gehörenden Laufzeitdateien stimmen bytegenau mit dem
Quellstand überein. Die vier Optionsmenüs wurden visuell geprüft; 14
Lokalisierungstests, Paket-/Schriftprüfung und die Ablageprüfung bestehen.
Dies ist eine gezielte Effektprüfung, kein vollständiger Kampagnen- oder
Mehrspieler-Durchlauf. Der Engine-Prüfer legt seine zusätzliche Fehlerlogdatei
jetzt ebenfalls im jeweiligen Logverzeichnis ab.

Die verstärkte Fassung besteht im isolierten Testpaket unter UZDoom 5.0.1
jeweils 444 native Assertions mit OpenGL und Vulkan, einschließlich einer
Prüfung auf volle additive Helligkeit am Maximum. Neue Ingame-Vergleiche
zeigen Stärke 1 und Größe 1 bei eingefrorener Kamera und Animationsphase;
erneute Aufnahmen desselben Schaltzustands sind pixelgenau identisch.

Die Farbkorrektur besteht ebenfalls jeweils 444 native Assertions unter
OpenGL und Vulkan. Zusätzlich isoliert der Test den Leuchtanteil durch
Subtraktion einer identischen Aufnahme ohne Glühen und prüft die erwarteten
blauen, grünen und orangen Farbkanäle. Der alte weiße Shader fällt durch
diese Farbprüfung; beide Renderer bestehen mit der korrigierten Fassung.

Der kurze Fadeout besteht unter beiden Renderern jeweils 551 native
Assertions plus die Farbprüfung. Die zusätzlichen Tests erfassen mehrere
abnehmende Helligkeitsstufen nach Actor-Zerstörung und nach einem unsichtbaren
Zustand, unveränderte Position/Größe/Farbe, Wiederaufleuchten, Bereinigung,
Einfrieren sowie das sofortige Abschalten verwaister Leuchthöfe. Auch beim
gleichzeitigen Ausklingen vieler Geschosse bleibt das Qualitätsbudget gültig.
