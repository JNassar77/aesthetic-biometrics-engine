# Entscheidungs-Memo: Aesthetic Biometrics Engine — Kurs nach Sprint 10

**An:** Jihad Nassar / Praxis Nassar · **Stand:** 2026-06-17
**Methode:** Multi-Agenten-Schwarm (13 Agenten — 6 Research, 3 Richter, 3 Red-Team, 1 Synthese) + Code-Verifikation
**Code-Verifikation:** Die schwerwiegendsten Befunde wurden nach dem Schwarm-Lauf einzeln gegen den Quellcode geprüft (auth.py, profile_engine.py, volume_engine.py, v2_routes.py, pixel_calibration.py) — alle bestätigt.

---

## 1. Quintessenz

**Kurs halten — der technische Kern ist richtig gewählt und darf NICHT pivotiert werden.** MediaPipe-2D + iris-kalibrierte Messung + voll-deterministischer regelbasierter Planer + FastAPI/Supabase/Railway ist für eine Einzelpraxis die korrekte, auditierbare, zukunftssichere Architektur; jeder 3D-/ML-/LLM-Ersatz wäre teures Over-Engineering ohne belegten Genauigkeitsgewinn.

**Aber das System ist heute nicht das, was es vorgibt zu sein:** ein erheblicher Teil der mm-Ausgaben (alle z-/Tiefen-Werte, die Profil-Projektionen) sind physikalisch keine metrischen Messungen, KEINE einzige Ausgabe ist gegen einen Referenzstandard validiert, und der wahre Engpass ist nicht Technik, sondern **Regulatorik (MDR-Scope + DSGVO Art. 9)**, die über die Existenz des Produkts entscheidet. Die Energie gehört in vier billige Härtungen, nicht in einen Umbau.

---

## 2. Empfehlung pro Dimension

| Dimension | Urteil | Ein-Satz-Begründung |
|---|---|---|
| **1. Detection (MediaPipe Tasks API)** | **HALTEN** | Einzige CPU-native Wahl mit Iris-Landmarks + Blendshapes + Pose-Matrix zu null Kosten; Alternativen erzwingen GPU + Rewrite von 15+ Engines für RMSE, die die Horizontalmessungen nicht schlägt — einzige Auflage: Modell per SHA256 + Versionspfad pinnen. |
| **2. px→mm Kalibrierung (Iris)** | **HYBRID** | Iris-Skalar für frontale In-plane-Proportionen halten (~3-5 %, klinisch vertretbar), aber Konstante prüfen/dokumentieren, optionalen ArUco-Pfad ergänzen und alle Out-of-plane-/Tiefenwerte als `estimated_only` flaggen. |
| **3. Methodik (statische Ranges)** | **HYBRID** | Deterministischen Kern halten, aber dünne quellenbelegte Lookup-Schicht nach Alter+Geschlecht ergänzen (zuerst Nasolabialwinkel + Lippenverhältnis) — Ethnie nur optional (Art. 9). |
| **4. Behandlungs-Planer (regelbasiert)** | **HALTEN** | Determinismus ist hier ein Sicherheits-Asset („locked algorithm"); LLM im Dosis-/Produktpfad bringt Halluzinationsrisiko in einen Schadenspfad — nur Produktdatenbank als YAML auslagern, LLM höchstens als markierter Text-Layer. |
| **5. Architektur / Stack** | **HYBRID** | Stack-Wahl bleibt; drei lokal behebbare Defekte sind Pflicht: `run_in_threadpool`, Lifespan-Singleton, Error-Tracking — kein Architekturwechsel. |
| **6. Blind-Spots (MDR/DSGVO/Validierung)** | **PIVOT** | Die einzige echte Kursänderung: Regulatorik-Scope + DPIA + klinische Validierung müssen VOR Go-Live geklärt sein — sie entscheiden, ob das Produkt legal betrieben werden darf. |

---

## 3. Red-Team — die drei Angriffe und ihr Überleben

**Angriff 1 — „Accuracy-Illusion" (mm-Werte sind teils fabrizierte Einheiten). Überlebt, verschärft.**
- `volume_engine.py:96/108` schickt MediaPipes **relative** z-Koordinate durch `to_mm()` (horizontale Pixeldichte) → `malar_depth_mm`, `tear_trough.*_depth_mm`, `temporal/jowl _depth_mm` sind Einheiten-Fiktion.
- `profile_engine.py:156`: `chin_proj_px = pogonion[0] - subnasale[0]` — 2D-x-Delta im 90°-Profil, wo Kinn/Nase 20-50 mm vor der Kalibrierebene liegen = doppelter systematischer Fehler, als mm etikettiert.
- `profile_engine.py:193`: `neck_approx = (gnathion[0] - 20, gnathion[1] + 40)` — frei erfundener Landmark mit hartkodierten Pixel-Offsets, speist `cervicomental_angle_deg` / `is_obtuse > 130`.
- `schemas_v2.py:73`: `unit: str = "mm"` als Default — n8n-Agenten erhalten `mm` ohne Signal, dass die Zahl ordinal ist.
- **Fix ist nicht Umbenennen, sondern Quarantäne/Entfernen** dieser Features aus der öffentlichen API, bis validiert — denn ein behandlungsrelevanter Boolean (`is_hollowed`, `is_obtuse`) zieht aus einer bedeutungslosen Größe eine klinische Schlussfolgerung.
- **In-plane-Horizontalmaße bleiben verteidigbar** (Drittel, Fünftel, Symmetrie, Lippe, Alarbreite, E-Linie als Punkt-zu-Linie) — Literatur: ~2,36 % Fehler Alarbreite (PMC12936401).

**Angriff 2 — Regulatorik/Haftung ist das wahre Risiko. Stärkster Befund.**
- Multi-Tenant-Code (`organization_id` durchgängig, per-Org-Auth, `treatment_comparisons`-Tabelle, per-Org-n8n) = **die MDR-Art.-5(5)-Eigenanwendungs-Ausnahme greift faktisch nicht mehr.**
- `auth.py:39`: leeres `API_KEYS` → `"dev-mode"` schaltet Auth komplett ab → Fehl-Deploy = offener, unauthentifizierter Biometrie-Endpunkt.
- Gesichtsbilder = Art.-9-Daten; **DPIA ist Pflicht** und existiert nicht. AI-Act-High-Risk greift erst ~2027/28 (Luft für KI-Auflagen, NICHT für MDR-Klassifizierung + DSGVO).

**Angriff 3 — Completeness-Critic. Wertvollste Korrektur.**
1. „Umbenennen in Stunden" ist die falsche Rahmung — es ist Scope-Reduktion klinischer Behauptungen.
2. **Die billigste Option fehlte:** 2D-Horizontal-Subset ausliefern, Rest aus der API entfernen → Lösch-PR (Tage), schrumpft Sprint-11-Validierungsumfang um ~60 %.
3. **Stiller Kalibrierungs-Fallback = Patientensicherheits-Hard-Stop.** `pixel_calibration.py:188` liefert `confidence=0.45`, `:169` sogar `px_per_mm=1.0, confidence=0.1` — nur Warning-String, **keine harte Ablehnung**; `plan_generator` konsumiert diese Zahlen für Filler-Volumina ohne Gate auf `calibration.confidence`.

---

## 4. Entscheidungs-Matrix (Dimensionen × Owner-Achsen A–F)

Achsen: **A** Klinische Genauigkeit · **B** Determinismus/Audit · **C** Ressourcen-Fit · **D** Ops-Einfachheit · **E** Regulatorik/Sicherheit · **F** Zukunftssicherheit

| Dimension | A | B | C | D | E | F | Empfehlung |
|---|---|---|---|---|---|---|---|
| **1. Detection MediaPipe** | gut (horizontal) / schwach (z) | ✓ | ✓ CPU 3,6 MB | ✓ | SHA-Pin nötig | ✓ | **HALTEN** + Modell pinnen |
| **2. Iris-Kalibrierung** | gut frontal / falsch out-of-plane | ✓ | ✓ | ✓ | mm-Claim begrenzt | ArUco erweiterbar | **HYBRID**: + ArUco + Flag |
| **3. Statische Ranges** | falsch f. diverse Patienten | ✓ | ✓ | ✓ | ⚠ Fairness-Lücke | ✓ | **HYBRID**: Lookup Alter/Geschlecht |
| **4. Regel-Planer** | korrekte Sicherheitslogik | ✓✓ | ✓ | ✓ | ✓✓ MDR-optimal | YAML | **HALTEN** + DB→YAML |
| **5. Architektur/Stack** | neutral | Modell-Pin = Audit | ✓ Railway | ⚠ Blocking/Singleton | ⚠ Observability + DPA | ✓ | **HYBRID**: 3 Fixes |
| **6. Blind-Spots** | unvalidiert (=0 formal) | n.a. | Klärung billig | n.a. | ⚠⚠ MDR + Art. 9 | entscheidet Existenz | **PIVOT**: Compliance-Gate |

**Treiber:** Spalten A (Genauigkeit nur horizontal belegt) und E (einzige Spalte mit zwei ⚠⚠) entscheiden.

---

## 5. Die GRENZE — wann eine andere Wahl richtig wäre

| Entscheidung | Halten gilt, SOLANGE… | Kippt, WENN… |
|---|---|---|
| **MediaPipe behalten** | Inputs standardisierte Fotos, Maße horizontal/in-plane | metrische 3D-Volumenmessung in ml als Kern-Claim + GPU + 3-6 Mon Rewrite-Budget (heute nicht gegeben) |
| **Iris-Skalar** | Praxis nimmt eigene standardisierte Fotos auf | Patienten reichen eigene Selfies ein → ArUco-Marker Pflicht |
| **Statische Ranges → Lookup** | Patientenschaft homogen | diverse Demografie + AI-Act-Fairness-Audit → Lookup zwingend (heute schon empfohlen) |
| **Regelbasierter Planer** | immer | **nie** für Dosis-/Produktpfad |
| **Eigenanwendung-Annahme** | NUR Praxis Nassar, eine `organization_id`, keine Drittbereitstellung | zweite Praxis / SaaS / Fremd-n8n → CE Class IIa Pflicht (57-201k EUR Jahr 1). Code hat diese Grenze bereits überschritten. |

---

## 6. Schlankster Weg — priorisiert

### GATE 0 — VOR jeder weiteren Code-Zeile (Tage–Wochen, billig)
1. **MDR-Scope verbindlich klären** (BfArM-Anfrage / MDR-Fachanwalt): Eigenanwendung vs. Inverkehrbringen. Intended Use schriftlich fixieren.
2. **DPIA für biometrische Art-9-Daten erstellen** (Pflicht). Railway-DPA/SCCs abschließen.
3. **Entscheidung dokumentieren:** Eigenanwendung → Multi-Tenant-Code kastrieren (eine fixe Org). Inverkehrbringen → Tenant-/API-Expansion einfrieren bis CE-Pfad entschieden.

### SPRINT 11 (ergänzt) — Ehrlichkeit + Sicherheit + Validierung
**Stunden-Arbeit zuerst (Integrität):**
4. **Tiefen-/Profil-Features quarantänisieren:** alle aus relativer z abgeleiteten Outputs + Out-of-plane-Profilwerte hinter `estimated_only=true` flaggen ODER aus dem Schema entfernen. `schemas_v2.py:73` darf `unit` nicht auf `"mm"` defaulten.
5. **Kalibrierungs-Hard-Gate:** bei `method != "iris"` oder `confidence < ~0.7` → Analyse ablehnen oder `estimated_only` erzwingen; `plan_generator` verweigert mm-Volumenempfehlungen darunter. `auth.py:39` „dev-mode" in Prod fail-closed.
6. **Iris-Konstante dokumentieren/prüfen + Modell SHA256 + Versionspfad pinnen** (`face_landmarker.task`).

**Dann die eigentliche Validierung:**
7. **Bland-Altman gegen Caliper, n≥20-30**, nur für die 5-8 entscheidungstreibenden Horizontal-Frontalmaße. Tiefen-/Profil-Outputs als ordinale Severity berichten, nicht als mm.
8. **Demografische Lookup-Schicht** (3-5 Tage, deterministisch): Nasolabialwinkel + Lippenverhältnis nach Geschlecht; Quellen je Range (Farkas, 3D Facial Norms DB).

### SPRINT 12 — Ops-Härtung (parallelisierbar, Ein-Personen-wartbar)
9. **`run_in_threadpool(run_pipeline, …)`** in `v2_routes.py:384` (eine Zeile).
10. **Lifespan-Singleton** für `FaceLandmarkerV2` (`orchestrator.py` instanziiert pro Request neu).
11. **Error-Tracking** (Sentry-EU, PII-Scrubbing).
12. **Hygiene:** Python lokal/Docker angleichen (3.12/3.13); `requirements.txt` obere Bounds; `railway.toml` (Region eu-west); `docker-compose`-Healthcheck zeigt noch auf gelöschten `/api/v1/health`.

### KANN WARTEN (kein Over-Engineering jetzt)
- Produktdatenbank → YAML · ArUco-Pfad (erst bei Selfie-Inputs) · LLM-Text-Layer (nie im Entscheidungspfad) · 3D/3DMM/Depth-Pro (frühestens Sprint 15+).

---

## 7. EIN messbarer nächster Schritt

**Schriftliche Intended-Use-Festlegung + MDR-Scope-Anfrage absenden** (BfArM oder MDR-Fachanwalt): „Wird das System ausschließlich praxisintern genutzt oder Dritten bereitgestellt?" — mit dem Code-Befund als Anlage, dass `organization_id`, per-Mandant-Auth und `treatment_comparisons` bereits auf Inverkehrbringen hindeuten. Erledigt, wenn die Anfrage raus ist und der Intended-Use als Dokument im Repo liegt. Diese Aktion bestimmt, ob CE-Class-IIa-Kosten anfallen — und damit, ob jede weitere Sprint-Stunde auf ein legal betreibbares Produkt einzahlt.

---

## Verifizierte Code-Pfade

- `app/analysis/volume_engine.py` (Z. 89-108: `_z_depth_mm`/`_z_diff_mm` — relative z → `to_mm`)
- `app/analysis/profile_engine.py` (Z. 156: `chin_proj` aus 2D-x-Delta; Z. 193: erfundener `neck_approx`)
- `app/utils/pixel_calibration.py` (Z. 24: `IRIS_WIDTH_MM=11.7`; Z. 169/188: stiller Fallback ohne Hard-Reject)
- `app/api/v2_routes.py` (Z. 339 `async def create_assessment` → Z. 384 synchroner `run_pipeline`)
- `app/models/schemas_v2.py` (Z. 73: `unit: str = "mm"` Default)
- `app/pipeline/orchestrator.py` (Z. 208-210: `FaceLandmarkerV2()` pro Request)
- `app/api/auth.py` (Z. 39: `return "dev-mode"` Auth-Bypass bei leerem `API_KEYS`)
