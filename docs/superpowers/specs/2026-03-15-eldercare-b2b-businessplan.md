# CareSignal — Business Plan
**Produkt:** WiFi-basiertes Sturz- und Präsenzmonitoring für die stationäre und ambulante Pflege
**Technologie:** RuView (WiFi DensePose, MIT-Lizenz — kommerzielle Nutzung erlaubt)
**Strategie:** B2B — Pflegedienste & Pflegeheime (DACH)
**Zeithorizont:** 12 Monate bis investor-ready
**Stand:** März 2026
**Version:** 1.1 (nach kritischem Review überarbeitet)

---

## 1. Executive Summary

CareSignal überwacht ältere Menschen kameralos und wearable-frei durch die Analyse von WiFi-Signalen. Das System erkennt ungewöhnliche Inaktivität und Bewegungsanomalien in Echtzeit — ohne Eingriff in die Privatsphäre.

Zielkunden sind ambulante Pflegedienste und stationäre Pflegeheime in der DACH-Region. Das Geschäftsmodell kombiniert einmalige Hardware-Installation mit monatlichem SaaS-Abo pro überwachter Wohnung/Zimmer.

### Wichtige Klarstellung zur Produktstrategie

| Version | Fähigkeiten | Zeitraum |
|---------|------------|---------|
| **MVP (V1)** | Präsenzerkennung + Inaktivitätsalarm ("Person liegt seit X Minuten still") | Monate 1–6 |
| **V2** | ML-basierte Sturzerkennung (~80% Accuracy nach Modelltraining) | Monate 7–18 |
| **V3 Roadmap** | Vitalzeichen (Atemfrequenz, Herzschlag) via CSI-Hardware | 18+ Monate |

**Kernthese für Investoren:**
Der demografische Wandel schafft einen Pflegenotstand. Pflegedienste müssen mehr Klienten mit weniger Personal versorgen. CareSignal gibt Pflegekräften einen "digitalen Sinn" — sie wissen passiv was passiert, ohne physisch präsent zu sein.

---

## 2. Problem

### Das Pflegeproblem in Zahlen (DACH)
- **5,0 Millionen** Pflegebedürftige in Deutschland (Statistisches Bundesamt, Pflegestatistik 2021: 4,96 Mio., Hochrechnung 2024)
- **Bis zu 500.000** fehlende Pflegekräfte bis 2030 (Bertelsmann Stiftung, "Zukunft der Pflege", 2019, Szenario 2)
- **Sturzkosten:** Ein sturzbedingte Behandlung kostet das Gesundheitssystem durchschnittlich EUR 15.000–30.000 (BARMER Gesundheitsreport 2022; Robert Koch Institut, "Stürze im Alter", 2023)
- **316.000** sturzbedingte Krankenhausfälle bei über 65-Jährigen/Jahr in Deutschland (Destatis, Krankenhausdiagnosestatistik 2022)
- **Nachtpflege:** Zwischen 22:00 und 06:00 Uhr gibt es in den meisten Einrichtungen minimales Personal — die gefährlichste Zeit

### Das Technologieproblem
Bestehende Lösungen haben einen fundamentalen Fehler:

| Lösung | Problem |
|--------|---------|
| Kameras | Privatsphäre — rechtlich & ethisch problematisch im Schlafzimmer |
| Smartwatch/Wearable | Ältere Menschen vergessen sie / lehnen sie ab |
| Bodensensoren (Matten) | Teuer, Stolperfalle, decken nur einen Punkt ab |
| Pflegekraft schaut rein | Nicht skalierbar, würdeverletzend |

**CareSignal löst das:** Keine Kamera. Kein Wearable. Kein Eingriff in die Würde.

---

## 3. Lösung — Was CareSignal kann (realistisch)

### V1 MVP (sofort baubar)
- **Präsenzerkennung** — Ist Person im Zimmer / hat sie das Bett verlassen?
- **Inaktivitätsalarm** — Person war aktiv, ist seit X Minuten ungewöhnlich still → Alert
- **Aktivitätsmuster** — Schlafdauer, Bewegungshäufigkeit, Toilettenfrequenz (Hinweis auf Dehydrierung)
- **Offline-Alarm** — Sensor fällt aus → sofortige Benachrichtigung

### V2 (Monate 7–18, nach Modelltraining)
- **Sturzerkennung** — Person wechselt von vertikal zu horizontal, ungewöhnlich schnell
- Accuracy-Ziel: ≥80% nach Kalibrierung mit gelabelten Daten aus Pilotinstallationen

### V3 Roadmap (18+ Monate, CSI-Hardware erforderlich)
- **Vitalzeichen** — Atemfrequenz und Herzschlag (erfordert ESP32-CSI-Firmware + mehr Rechenleistung)
- *Hinweis: Standardmäßig liefert WiFi nur RSSI-Daten. Vitalzeichen benötigen spezielle CSI-Firmware auf ESP32-S3 — dieser Schritt ist technisch machbar aber nicht trivial*

### Dashboard für Pflegekräfte
- Web-Dashboard: alle Zimmer auf einen Blick (Grün/Rot/Grau)
- Push-Notification auf Smartphone bei Alarm
- Wochenbericht: Trends pro Bewohner

---

## 4. Markt

### Gesamtmarkt (TAM/SAM/SOM)

**TAM — Total Addressable Market (Deutschland)**
- 15.380 stationäre Pflegeeinrichtungen (Destatis, Pflegestatistik 2021) × Ø 72 Plätze × EUR 19/Zimmer/Monat = **~253 Mio EUR/Jahr**
- 14.798 ambulante Pflegedienste (Destatis 2021) × Ø 35 Klienten × EUR 29/Klient/Monat = **~150 Mio EUR/Jahr**
- **Gesamt TAM Deutschland: ~403 Mio EUR/Jahr**

**SAM — Serviceable Market**
Schätzung 10–15% digitalisierungsaffine Einrichtungen (Basis: KHZG-Förderanträge 2022 zeigten ca. 40% der Krankenhäuser, Pflegemarkt schätzungsweise 10–15% durch geringeren Digitalinvestitionsdruck)
- **SAM: ~40–60 Mio EUR/Jahr** *(muss durch eigene Marktbefragung validiert werden)*

**SOM — Realistisch in 12 Monaten**
- Ziel: 10 Pflegedienste × 30 Klienten × EUR 29 = **~8.700 EUR/Monat MRR**
- Das ist der Beweis für Investoren: Product-Market-Fit

### Wachstumstreiber
1. EU-Pflegenotstand — politischer Druck auf Digitalisierung
2. KHZG-Nachfolge und Pflegedigitalisierungsprogramme
3. Krankenkassen-Interesse an Sturzprävention (ein vermiedener Sturz spart EUR 15.000–30.000)

---

## 5. Wettbewerb & Positionierung

### Direkte Konkurrenten

| Unternehmen | Technologie | Preis (ca.) | Schwäche |
|-------------|-------------|-------------|----------|
| **Vayyar (Israel)** | 4D-Radar | ~EUR 40–80/Zimmer/Monat | Teuer, Enterprise-only, kein DACH-Support |
| **Nobi (Belgien)** | Kamera-Lampe | ~EUR 800 HW + Abo | Kamera = Datenschutz-Problem |
| **Sievert Larsen (DK)** | Radar | ~EUR 50/Zimmer/Monat | Teuer, nur Sturz |
| **Essence SmartCare** | Kamera + KI | ~EUR 30/Zimmer/Monat | Kamera |
| **Fall Call Solutions** | Wearable-Button | ~EUR 15/Monat | Muss aktiv gedrückt werden |

### CareSignal Positionierung

**Alleinstellungsmerkmal:**
> "Kein Kamera. Kein Wearable. DSGVO-konform. Günstiger als der Markt."

**TCO-Vergleich (24 Monate, ambulant):**

| Anbieter | HW | Abo × 24 | Total |
|---------|-----|---------|-------|
| CareSignal | EUR 149 | EUR 29 × 24 = 696 | **EUR 845** |
| Vayyar (Hardware-Leasing) | EUR 0 | EUR 60 × 24 = 1.440 | EUR 1.440 |
| Nobi | EUR 800 | EUR 30 × 24 = 720 | EUR 1.520 |

*CareSignal ist ~40% günstiger als günstigster Konkurrent über 24 Monate.*

---

## 6. Geschäftsmodell

### Preisstruktur B2B

**Ambulanter Pflegedienst:**
```
Hardware (einmalig):     EUR 149/Klient   (BOM: ~EUR 95 → Marge: EUR 54)
Installation:            EUR 99 einmalig  (2h Arbeit + Anfahrt — Kostendeckend bei kleinen Distanzen)
SaaS Abo:               EUR 29/Monat/Klient
──────────────────────────────────────────────────────────────────────────
Break-even (Monate):     (149-95 + 99) / 29 = ~7 Monate
LTV bei 24 Monaten:      149 + 99 + (29×24) = EUR 944/Klient
```

**Stationäres Pflegeheim:**
```
Hardware (einmalig):     EUR 99/Zimmer    (BOM: ~EUR 65 bei Volumen, ohne RPi pro Zimmer)
Installation:            EUR 499 (Haus-Pauschale, zentraler Server)
SaaS Abo:               EUR 19/Zimmer/Monat
──────────────────────────────────────────────────────────────────────────
50-Zimmer-Heim:          EUR 4.950 HW + EUR 499 Installation + EUR 950/Monat recurring
```

*Anmerkung: Bei stationären Heimen läuft der Raspberry Pi zentral — ein Gerät für das ganze Haus. Bei ambulanten Klienten benötigt jeder Klient seinen eigenen Pi (höhere Hardware-Kosten).*

### Unit Economics (Ziel-Szenario Monat 12)

```
10 Pflegedienste × 30 Klienten = 300 aktive Klienten

Hardware-Einnahmen:      300 × EUR 149 = EUR 44.700 (einmalig)
Installationen:          300 × EUR 99  = EUR 29.700 (einmalig)
MRR (Monat 12):         300 × EUR 29  = EUR 8.700/Monat
ARR:                    EUR 104.400/Jahr

Kosten Hardware:        300 × EUR 95   = EUR 28.500
Infrastruktur/Hosting:  EUR 100/Monat (Hetzner Cloud)
────────────────────────────────────────────────────
Brutto-Marge Hardware:   ~36% (nach BOM-Korrektheit)
Brutto-Marge SaaS:       ~85% (nach Infrastruktur)
```

---

## 7. Risiken & Schwachstellen

### 7.1 Technische Risiken

| Risiko | W'keit | Impact | Mitigation |
|--------|--------|--------|------------|
| **ESP32 CSI-Firmware** — Standard ESP-IDF gibt kein Raw-CSI aus; braucht custom Firmware-Patch | Hoch | Hoch | RuView hat ESP32-Firmware bereits im Repo; in Pilot validieren bevor skaliert wird |
| **Falsch-Positive Alarme** — Person schläft tief, kein Alarm-Unterschied zu Bewusstlosigkeit | Mittel | Hoch | Adaptive Schwellenwerte pro Person, 2-Stufen-Alarm (Warn → Kritisch) |
| **Falsch-Negative** — Inaktivitätsalarm wird nicht ausgelöst | Mittel | Kritisch | Redundanz: Alarm AUCH bei Sensor-Disconnect; Minimum 3 Sensoren pro Raum |
| **WiFi-Interferenz** | Hoch | Mittel | Site-Survey vor Installation, Mehrkanal-Scanning |
| **Mehrpersonen-Zimmer** | Hoch in Heimen | Mittel | Separate Kalibrierung; MVP erst in Einzelzimmern |
| **Alte WiFi-Infrastruktur** | Mittel | Mittel | Site-Survey-Checkliste: IEEE 802.11n Minimum |
| **Raspberry Pi Ausfall** | Niedrig | Hoch | Watchdog + automatischer Neustart + Offline-Alert bei > 5min kein Heartbeat |
| **Vitalzeichen-Accuracy** | Hoch (V3) | Mittel | Erst in V3, explizit als Forschungsfeature kommunizieren — kein Medizinprodukt |

### 7.2 Regulatorische Risiken (KRITISCH)

| Risiko | Details | Mitigation |
|--------|---------|------------|
| **MDR (Medical Device Regulation)** | Wenn Behörde Vitaldaten als diagnostisch einstuft → CE-Klasse II, >EUR 200.000 Zertifizierung | Von Tag 1: "Sicherheits- und Komfortsystem", KEIN medizinisches Monitoring. Vitaldaten erst in V3 und nur als "Wellness-Indikator" |
| **DSGVO — Ambulant** | Patient-Heimrouter nicht unter Betreiber-Kontrolle; Signalbleed in Mehrfamilienhäuser; Pi = Verarbeitungsgerät in Privatwohnung | Datenverarbeitungskonzept durch IT-Recht-Kanzlei (einmalig ~EUR 800-1.500); Sensor kalibriert NUR auf eine Person; keine Cloud-Übertragung ohne explizite Einwilligung |
| **Bewohner-Einwilligung** | Opt-in für jeden Bewohner rechtlich zwingend | Einwilligungsformular im Onboarding, Widerruf jederzeit möglich |
| **Betriebsrat** | Kann Einführung in großen Einrichtungen blockieren | Früh einbinden; betonen: Bewohner-Sicherheit, keine Personalüberwachung |
| **Heimaufsicht** | Genehmigungspflicht in manchen Bundesländern | Vor Pilotstart: Rückfrage bei zuständiger Heimaufsicht |

### 7.3 Haftungsrisiko (KRITISCH — war bisher nicht im Plan)

**Szenario:** CareSignal verpasst einen Sturz. Patient liegt 6 Stunden unentdeckt. Pflegedienst hatte Nacht-Rundgänge reduziert weil "das System überwacht". Patient erleidet bleibende Schäden.

**Konsequenz:** Zivilklage gegen Pflegedienst UND möglicherweise gegen CareSignal als Hersteller.

**Mitigation (zwingend vor erstem Kundenvertrag):**
1. AGB mit klarer Haftungsbeschränkung: "CareSignal ist ein ergänzendes Sicherheitssystem, kein Ersatz für Pflegeleistungen"
2. **Betriebshaftpflichtversicherung** für Software/Hardware-Produkte im Pflegebereich: EUR 800–2.000/Jahr
3. Contractual Liability Cap: Haftung max. 6 Monatsbeiträge
4. Vertraglich: Pflegedienst muss dokumentieren dass Rundgänge NICHT reduziert werden

*→ Ohne Punkt 2 und 3 darf kein einziger Vertrag unterzeichnet werden.*

### 7.4 Markt & Sales Risiken

| Risiko | Details | Mitigation |
|--------|---------|------------|
| **Langer Sales-Cycle** | Pflegeheime: 3–12 Monate Entscheidungszeit | Ambulante Dienste zuerst (1–3 Monate); Pilot-Angebot: "30 Tage kostenlos testen" |
| **Abrechnungscodierung fehlt** | Pflegedienste können die Kosten nicht über Pflegekassen abrechnen | Als Eigenleistung verkaufen; ROI-Argument: 1 vermiedener Sturz = EUR 15.000 gespart; Förderanträge vorbereiten |
| **Kein Branchen-Netzwerk** | Keine bestehenden Kontakte in Pflege | LinkedIn-Outreach, AltenpflegeMesse Nürnberg (als Besucher, ~EUR 100 Ticket), lokale Pflegeverbände |
| **Kein Vertrauen als Startup** | "Wir kaufen nicht bei einem 1-Mann-Betrieb" | Pilot-Referenzkunde + Case Study; Betriebshaftpflicht zeigen |
| **Konkurrent reduziert Preise** | Vayyar oder Nobi reagiert | Kundenbindung durch lokalen Support und DSGVO-Vorteil |

### 7.5 Finanzielle Risiken

| Risiko | Details | Mitigation |
|--------|---------|------------|
| **Cashflow** | Hardware vorstrecken (EUR 95/Klient) bevor Zahlung eingeht | 50% Anzahlung bei Bestellung; max. 5 Klienten gleichzeitig ohne Vorfinanzierung |
| **Lieferzeit ESP32** | AliExpress: 4–8 Wochen | Puffer von 20–30 Einheiten halten; Amazon als Backup (teurer aber sofort) |
| **Tatsächliche Betriebskosten** | Plan unterschätzte Kosten | Realistische Kalkulation: EUR 3.500–5.000 bis Monat 9 (Hardware, Legal, Hosting, Versicherung, Messe) |

### 7.6 Operationale Risiken

| Risiko | Details | Mitigation |
|--------|---------|------------|
| **Skalierung alleine** | Ab Kunde 5 nicht mehr alleine managebar | Ab EUR 2.000 MRR: ersten Freelancer für Installation |
| **Support-Aufwand** | Pflegepersonal ruft bei jedem Alarm an | FAQ-Dokument, Video-Tutorial, klares Eskalationsprotokoll |
| **Einzel-Personen-Abhängigkeit** | Nur du kennst den Code | Dokumentation von Tag 1; Claude als "2. Entwickler" |

### 7.7 Gesamtbewertung: Lohnt es sich?

**Ja, aber mit realistischen Augen:**

✅ Riesiger, strukturell unversorgter Markt
✅ Technologie existiert bereits (kein R&D von Null)
✅ Wettbewerb ist teuer und datenschutzkritisch
✅ MVP mit vorhandenen Fähigkeiten (Präsenz + Inaktivität) ist sofort baubar
✅ Investor-Ready in 12 Monaten realistisch

⚠️ Kritisches Hindernis #1: Haftpflichtversicherung + AGB nötig vor erstem Vertrag
⚠️ Kritisches Hindernis #2: DSGVO-Konzept für ambulante Pflegeeinstellungen
⚠️ V2 Sturzerkennung (ML-Modell) braucht reale Trainingsdaten — dauert länger als gedacht

---

## 8. MVP — Was wirklich gebaut werden muss

### MVP-Scope (korrekt, nach technischer Analyse)

Das MVP nutzt die **bereits funktionierende** Präsenz- und Bewegungserkennung (RSSI-basiert) aus RuView. Es wird **kein neues ML-Modell** benötigt.

**IN (sofort baubar mit bestehendem Code):**
- Inaktivitätsalarm: "Person war aktiv, seit X Minuten keine Bewegung" → Alert
- Präsenzerkennung: Person hat Raum verlassen / nicht ins Bett gegangen
- Push-Notification via ntfy.sh (kostenlos, DSGVO-konform, kein Account nötig)
- Web-Dashboard: Zimmerstatus (Grün / Alarm / Offline)
- Hardware-Setup-Skript: ein Befehl, alles läuft

**OUT bis V2:**
- ML-basierte Sturzerkennung (braucht gelabelte Daten aus echten Installationen)
- Mehrpersonen-Zimmer (erst nach Einzelzimmer-Validierung)

**OUT bis V3:**
- Vitalzeichen (Herzschlag, Atemfrequenz)
- Mobile Native App
- Multi-Mandanten-System für große Pflegedienste

### Hardware pro Klient (ambulant)
```
3x ESP32-S3 DevKit (Amazon)     ~EUR 45   (3 × EUR 15, sofort lieferbar)
1x Raspberry Pi 4 (2GB)         ~EUR 45
SD-Karte 32GB                   ~EUR 8
Gehäuse + Netzteil + Kabel      ~EUR 12
─────────────────────────────────────────
Gesamt BOM pro Klient:          ~EUR 110
Verkaufspreis:                   EUR 149
Hardware-Marge:                  EUR 39 (~35%)
```

*Bei Volumen (50+ Einheiten): ESP32 von AliExpress ~EUR 8 je → BOM sinkt auf ~EUR 75, Marge steigt auf ~50%*

### Software-Stack (was neu zu bauen ist)

```
Bereits in RuView vorhanden (nicht anfassen):
  ✓ RSSI-Sensing Pipeline
  ✓ Präsenz-/Bewegungserkennung (Classifier)
  ✓ FastAPI Backend + WebSocket
  ✓ Basis-Dashboard

Neu zu bauen (alle in separatem Ordner v1/src/caresignal/):
  □ alert_service.py     — Inaktivitäts-Logik + ntfy.sh Push
  □ dashboard_care.html  — Vereinfachtes Pfleger-Dashboard (1 Seite)
  □ setup.py             — Raspberry Pi Auto-Setup Skript
  □ config_care.yaml     — CareSignal-spezifische Einstellungen
```

*Wichtig: Alle CareSignal-Dateien in eigenem Ordner → RuView-Updates bleiben konfliktfrei*

---

## 9. KI-Agenten für MVP-Entwicklung

### Prinzip
Du bist Product Owner. Claude ist dein Entwicklerteam. Du beschreibst was gebraucht wird, Claude schreibt den Code, du testest.

### Sprint-Plan (2-Wochen-Sprints, realistisch)

**Sprint 1 — Inaktivitätsalarm (Wochen 1–2)**
```
Prompt an Claude:
"In RuView gibt es v1/src/sensing/classifier.py mit MotionLevel.
Baue in v1/src/caresignal/alert_service.py einen Service der:
1. Alle 30 Sekunden den aktuellen MotionLevel abruft
2. Wenn MotionLevel == ABSENT für mehr als 20 Minuten: Alert auslösen
3. Alert = HTTP POST an ntfy.sh/caresignal-[zimmer-id]
Zeig mir den kompletten Code."
```

**Sprint 2 — Dashboard (Wochen 3–4)**
```
Prompt an Claude:
"Baue v1/src/caresignal/dashboard_care.html — eine einzelne HTML-Seite:
- Zeigt alle konfigurierten Zimmer als Karten
- Jede Karte: Zimmername, Status (Grün=OK, Rot=Alarm, Grau=Offline)
- Letzter Alert-Zeitpunkt
- Verbindet sich mit der RuView REST API auf localhost:8000
- Kein Framework, reines HTML+JavaScript"
```

**Sprint 3 — Setup-Automatisierung (Wochen 5–6)**
```
Prompt an Claude:
"Schreibe v1/src/caresignal/setup.py:
- Läuft auf Raspberry Pi
- Prüft ob alle 3 ESP32-Sensoren erreichbar sind
- Startet RuView API Server
- Startet CareSignal Alert Service
- Richtet Autostart ein (systemd service)
- Gibt am Ende: READY oder FEHLER + Anleitung aus"
```

**Sprint 4 — Härtung & Dokumentation (Wochen 7–8)**
```
- Offline-Alarm wenn Sensor > 5min nicht antwortet
- Alarm-Protokoll (lokale SQLite-Datei, kein Cloud-Zwang)
- Setup-Anleitung für Pflegedienst (1 Seite PDF, Claude schreibt es)
```

### Parallele Sales-Aktivität (ab Woche 2)
*Wichtig: Nicht erst fertig entwickeln, dann verkaufen — parallel laufen lassen*

```
Woche 2: LinkedIn-Profil aufbauen, erste 10 Pflegedienst-GFs anschreiben
Woche 4: Demo mit Mock-Dashboard zeigen (schon funktionsfähig)
Woche 6: Ersten Pilot-Partner für kostenlose Testinstallation gewinnen
Woche 8: Pilot live, erste echte Daten sammeln
```

---

## 10. Update-Strategie

### RuView-Updates sauber einspielen

```bash
# 1. Änderungen prüfen bevor Update
cd D:\CodeENV\ruview
git fetch origin
git log HEAD..origin/main --oneline    # Was kommt neu?
git diff HEAD..origin/main -- v1/src/  # Konkrete Code-Änderungen

# 2. Claude fragen was betroffen ist
# "Hier ist das Diff: [paste]. Was ändert sich für meinen
# CareSignal-Code in v1/src/caresignal/?"

# 3. Update einspielen
git pull origin main
pip install -e .

# 4. Verification
cd v1
python data/proof/verify.py   # Muss VERDICT: PASS ausgeben

# 5. CareSignal-Tests
python -m pytest tests/caresignal/ -x -q
```

### Warum das funktioniert (Architektur-Entscheidung)
Alle CareSignal-Ergänzungen liegen in `v1/src/caresignal/` — einem Ordner der in RuView nicht existiert. RuView-Updates ändern nie diesen Ordner. Conflicts sind strukturell unmöglich solange du nie RuView-Kerndateien veränderst.

### Versionsstrategie

```
RuView (Upstream):    Du folgst — regelmäßige git pull
CareSignal:           Du entwickelst — semantic versioning (1.0.0, 1.1.0, ...)
Kundensysteme:        Jeder Raspberry Pi bekommt Updates via:
                      ssh pi@[ip] "cd ruview && git pull && sudo systemctl restart caresignal"
```

Für später (ab 10+ Kunden): Automatisches Remote-Update-System via Ansible oder einfaches Shell-Script.

---

## 11. 12-Monats-Roadmap

### Phase 1: Prototyp (Monate 1–3) — EUR 500 Budget
**Ziel:** Funktionierender MVP, erster Pilot-Partner zugesagt

| Woche | Technisch | Business |
|-------|-----------|---------|
| 1–2 | Inaktivitätsalarm (Sprint 1) | Hardware bestellen, LinkedIn aufbauen |
| 3–4 | Dashboard (Sprint 2) | 10 Pflegedienst-GFs anschreiben |
| 5–6 | Setup-Skript (Sprint 3) | Demo-Gespräche führen |
| 7–8 | Härtung (Sprint 4) | Pilot-Partner schriftlich zusagen |
| 9–12 | Pilot installieren, echte Daten | DSGVO-Konzept + AGB erstellen (EUR 800) |

**Kosten Phase 1:** EUR 110 Hardware + EUR 800 Legal = EUR 910

### Phase 2: Pilot (Monate 4–6) — EUR 800 Budget
**Ziel:** 1–3 zahlende Kunden, echte Nutzungsdaten

- Pilot läuft live, wöchentliches Feedback-Gespräch
- Alert-Genauigkeit messen und dokumentieren
- Preismodell validieren
- Case Study schreiben: "X Alarme in Y Wochen"
- Betriebshaftpflicht abschließen (EUR 800–1.000/Jahr)

**Kosten Phase 2:** EUR 330 Hardware (3 weitere Klienten) + EUR 900 Versicherung = EUR 1.230

### Phase 3: Sales (Monate 7–9) — EUR 1.500 Budget
**Ziel:** 5–8 zahlende Kunden, EUR 3.000+ MRR

- AltenpflegeMesse Nürnberg besuchen (EUR 100 Ticket + Reise)
- ML-Sturzerkennung V2 beginnen (Trainingsdaten aus Pilot)
- Onboarding standardisieren
- UG gründen (bei erstem Vertrag — EUR 300 Notar)

**Kosten Phase 3:** EUR 1.500 total

### Phase 4: Investor-Ready (Monate 10–12)
**Ziel:** 8.700 EUR MRR, Seed-Pitch vorbereiten

- 10 Kunden, 300 Klienten live
- Metriken: Churn, NPS, Alert-Accuracy, Reaktionszeit
- Pitch-Deck mit echten Zahlen
- EXIST oder High-Tech Gründerfonds kontaktieren

**Gesamtbudget 12 Monate: EUR 3.500–5.000** (keine Gehälter, nur Sachkosten)

---

## 12. Fördermöglichkeiten

| Programm | Was | Betrag | Voraussetzung |
|----------|-----|--------|---------------|
| **EXIST Gründerstipendium** | Bis 12 Monate Lebensunterhalt + EUR 30.000 Sachkosten | EUR 2.500–3.000/Monat | Hochschulabsolvent, max. 5 Jahre nach Abschluss |
| **Digital Jetzt (BMWK)** | Digitalisierungsinvestition | bis EUR 50.000 | Bestehendes Unternehmen |
| **KfW StartGeld** | Gründerkredit | bis EUR 125.000 | Nach UG-Gründung |
| **High-Tech Gründerfonds** | Seed-Investment | EUR 600.000 | MVP + erste Kunden vorhanden |
| **Digitalisierungsprämie BW/BY** | Je nach Bundesland | EUR 5.000–15.000 | Variert |

---

## 13. Investor-Pitch — die 3 Kernaussagen (Monat 12)

1. **Traktion:** "Wir überwachen aktiv 300 Bewohner in 10 Einrichtungen. MRR: EUR 8.700. Kein einziger Kunde hat gekündigt."

2. **Problem-Beweis:** "In 6 Pilotmonaten haben wir 47 kritische Inaktivitäts-Alarme ausgelöst. 8 davon nachts. Durchschnittliche Reaktionszeit der Pflegekraft: unter 6 Minuten. Vorher: unentdeckt bis zum Morgen."

3. **Markt:** "15.000+ Pflegeheime in Deutschland. 0,07% penetriert. EUR 400 Mio/Jahr TAM. Wir brauchen 2% für EUR 8 Mio ARR."

---

## 14. Die nächsten 3 Schritte (diese Woche)

**Schritt 1 — Hardware bestellen (heute)**
Amazon: "ESP32-S3 DevKit" (3 Stück × EUR 15) + "Raspberry Pi 4 2GB Starter Kit" (~EUR 75)
Lieferzeit: 1–3 Tage

**Schritt 2 — Rechtliches vorbereiten (diese Woche)**
IT-Recht Kanzlei (it-recht-kanzlei.de) — AGB-Template für Software/Hardware im B2B-Bereich: EUR 100–300 für Basis-Paket

**Schritt 3 — Ersten Kontakt aufnehmen (diese Woche)**
Google: "Pflegedienst [deine Stadt] Geschäftsführer"
LinkedIn-Suche: "Pflegedienstleitung" + deine Stadt
Nachricht (kurz):
> "Ich entwickle ein System das Pflegekräfte per Smartphone alarmiert wenn ein Bewohner ungewöhnlich lange still liegt — ohne Kamera, ohne Wearable. Darf ich Ihnen in 15 Minuten eine Demo zeigen? Pilotteilnehmer testen kostenlos."

---

*Dieses Dokument wird fortlaufend aktualisiert. Version 1.1 — nach kritischem Review überarbeitet.*
