# TNT01: zusätzliche Geländegeometrie zurückgenommen

Stand: **11.09.2026**. Auf Nutzerwunsch sind beide Geländeüberarbeitungen vom 09.09.2026 vollständig aus TNT01 entfernt. Die zusätzlichen Formationen der ersten Fassung sowie sämtliche Geländedreiecke, Böschungen, Slopes, verschobenen Eckpunkte und unterteilten Felskanten der zweiten Fassung sind zurückgenommen.

Die Karte verwendet wieder die Geometrie unmittelbar vor Commit `480556843`: 17.447 Vertices, 19.971 Linedefs, 34.556 Sidedefs und 3.742 Sektoren. Gegenüber der verworfenen Fassung entfallen 4.343 Vertices, 13.062 Linedefs, 25.903 Sidedefs und 8.657 Sektoren. Die ursprünglichen Bodenebenen, Konturen, Höhen, Eigenschaften und BSP-Nodes sind wiederhergestellt. Alle 2.648 Things und ACS-Lumps bleiben unverändert.

Spätere Materialänderungen bleiben auf 75 ursprünglichen Wandseiten erhalten. Die weiteren 13 Materialzuweisungen gehörten zu nun entfernten Linienfragmenten; ihre erhaltenen Ursprungswände tragen weiterhin dasselbe erweiterte Material. Der Sturmhimmel und die zuvor ergänzte Deckenbeleuchtung bleiben erhalten.

Die spätere Laufzeit-Texturausrichtung benötigt zur Originalgeometrie passende Indizes und Schutzprüfungen. Daher wurde ausschließlich `tutnt/areaalign/TNT01.txt` anhand einer nativen Engine-Messung neu erzeugt. Alle 3.831 Materialbindungen werden angenommen; die Materialauswahl, Bilder und Tabellen anderer Karten bleiben bestehen. Die TNT01-Prüfungen für Sektorzahl und Felszuordnungen sind entsprechend angepasst.

Geprüft wurden die exakte Übereinstimmung der Geometrie und Nodes mit dem Ausgangsstand, das vollständige Entfernen beider Erzeugungsmarker, unveränderte Things/ACS sowie Kartenstart, Materialbindungen, Himmel und Speichern/Laden in UZDoom. Lokale Nachweise liegen unter `tutnt/.codex/validation/tnt01-terrain-removal/`, die Sicherung des verworfenen Kartenstands unter `tutnt/.codex/backups/tnt01-terrain-removal/`.

Die früheren Generatoren und historischen Manifeste bleiben als Entwicklungsnachweis verfügbar; sie gehören nicht zum Spielpaket und werden beim regulären Build nicht ausgeführt. Beide Geländevarianten sind nicht mehr Bestandteil des Spiels. Nach dem Paketwechsel TNT01 frisch starten; alte Spielstände enthalten weiterhin ihren gespeicherten Kartenstand.
