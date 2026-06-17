# Konzept: Echte metrische 3D-Tiefe

**Stand:** 2026-06-17 · **Status:** Konzept (kein Code) · **Bezug:** docs/STRATEGY_REVIEW_2026-06.md (Befund „Accuracy-Illusion")

> Ziel dieses Dokuments: Den Weg skizzieren, wie die aktuell als `estimated` markierten Tiefen-/Projektionswerte (`malar_depth`, `tear_trough_depth`, `chin_projection`, …) durch **echte metrische Messungen** ersetzt werden. Machbarkeit, erwartbare Genauigkeit, Aufwand — als Entscheidungsgrundlage, noch keine Implementierung.

---

## 1. Das Problem (warum die heutigen Tiefen `estimated` sind)

Eine einzelne 2D-Kamera kann keine Tiefe messen. Der aktuelle Code behilft sich mit MediaPipes z-Koordinate — die ist aber **relativ** (kein metrischer Nullpunkt, grob geschätzt) und wird durch die **horizontale** Pixeldichte geteilt. Ergebnis: eine Zahl, die wie mm aussieht, aber keine ist. Die Profil-Projektionen (`chin_projection`) sind reine 2D-x-Deltas mit doppeltem perspektivischem Fehler.

**Was wir haben** (und was die Lösung trägt):
- **478 Landmarks pro Ansicht mit identischer Semantik** → Punkt-Korrespondenzen über die 3 Ansichten sind *geschenkt* (der schwierigste Teil klassischer Photogrammetrie entfällt).
- **Head-Pose-Matrix pro Ansicht** (`detection/head_pose.py`) → relative Kamera-Orientierung ist bekannt.
- **Iris-Durchmesser 11,7 mm** → metrischer Maßstab ist bekannt (derselbe Anker wie heute, aber für echte 3D-Triangulation statt 2D-Skalierung).

---

## 2. Drei Wege zu echter Tiefe (aufsteigend nach Genauigkeit und Aufwand)

### Weg A — Landmark-Triangulation aus den 3 Fotos *(empfohlener erster Schritt)*

Reine Mehransichten-Geometrie, passt exakt zum aktuellen Input (frontal/oblique/profil) und Stack (NumPy/SciPy/OpenCV, CPU, kein Deep Learning).

**Pipeline (neue Stufe vor den Analyse-Engines):**
1. Pro Ansicht: 478 2D-Landmarks + Head-Pose (Orientierung) + Iris-Skalar.
2. Kamera-Modell je Ansicht aufstellen: Orientierung aus Head-Pose, Brennweite aus EXIF (Fallback: Standard-Annahme), Position relativ.
3. Für jeden Landmark, der in ≥ 2 Ansichten sichtbar ist: Sichtstrahlen schneiden (Triangulation) → 3D-Punkt.
4. Iris-Distanz (11,7 mm) als bekannte Strecke → metrische Skalierung der gesamten Punktwolke.
5. Optional: Bündelausgleich (bundle adjustment) — Posen + Punkte gemeinsam optimieren, um Restfehler zu minimieren.
6. Ergebnis: **metrische 3D-Punktwolke der 478 Landmarks in mm.** Die Engines lesen Tiefen/Projektionen daraus statt aus relativem z.

**Eigenschaften:**
- ✅ **Deterministisch + auditierbar** (reine Geometrie) — entscheidend fürs Medizinprodukt (jede Zahl rückführbar, kein Black-Box-Modell).
- ✅ Kein GPU, keine neuen schweren Abhängigkeiten, bleibt im CPU-/Railway-Profil.
- ✅ Nutzt vorhandene Daten; kein neues Input-Format.
- ⚠️ Genauigkeit hängt **stark vom Aufnahme-Protokoll** ab (siehe §3).

### Weg B — Tiefensensor-Aufnahme *(höchste Genauigkeit, ändert das Input-Format)*

Statt zu *rekonstruieren*, die Tiefe direkt **messen**: iPhone Pro TrueDepth, dedizierter 3D-Gesichtsscanner oder strukturiertes Licht. Der Sensor liefert metrische 3D-Daten direkt — das Triangulations-Genauigkeitsproblem entfällt komplett.

- ✅ Höchste, robusteste Genauigkeit (sub-mm möglich), unabhängig von Mimik-Konsistenz.
- ✅ Verarbeitung simpel (Tiefe ist schon da, MediaPipe-Landmarks darauf projizieren).
- ⚠️ Braucht Hardware in der Praxis; ändert die API (Tiefenbild/Mesh statt Foto). Für *Patienten-Uploads* (Agent-as-a-Service) ungeeignet, für *Praxis-interne* Aufnahme ideal.

### Weg C — Metrisches 3DMM (MICA / Pixel3DMM) *(Deep Learning, später / optional)*

Ein neuronales Netz fittet ein metrisches Gesichtsmodell (FLAME) an ein Bild ([MICA, ECCV 2022](https://github.com/Zielon/MICA); [Pixel3DMM, 2025](https://simongiebenhain.github.io/pixel3dmm/)). Rekonstruiert die ganze Oberfläche, nicht nur Landmarks.

- ✅ Robust (Modell-Prior regularisiert), state-of-the-art metrische Form.
- ❌ **Black-Box** → schwer zu validieren/auditieren für ein Medizinprodukt (widerspricht Owner-Achse „Determinismus").
- ❌ Braucht GPU + ML-Stack → sprengt das Einzelpraxis-/Railway-Profil.
- Benchmark-„mm" sind oft mit optimalem Scale-Alignment berechnet (geschönt) — echte metrische Genauigkeit ist geringer als die Papers suggerieren.

---

## 3. Erwartbare Genauigkeit — ehrlich

Die mm-Genauigkeit von **Weg A** wird von vier Fehlerquellen bestimmt:

| Fehlerquelle | Wirkung | Gegenmittel |
|---|---|---|
| **Nicht-synchrone Aufnahmen** (3 Fotos zu verschiedenen Zeitpunkten) | Mimik/Kopfbewegung zwischen Aufnahmen → Korrespondenz-Punkte liegen nicht auf derselben Anatomie | Striktes Protokoll: gleiche Sitzung, neutrale Mimik (wird schon validiert), Kopf still. **Größte Schwäche.** |
| **Unbekannte Brennweite** | systematischer Tiefen-Skalierungsfehler | EXIF nutzen; pro Kamera einmal kalibrieren |
| **Perspektivische Verzerrung** (variabler Aufnahme-Abstand) | Nahaufnahmen verzerren Proportionen (Nase wirkt größer); die Iris-Skala korrigiert das **nicht** | perspektivisches Kameramodell + Distanz-Schätzung → siehe §3b |
| **Head-Pose-Ungenauigkeit** | Triangulationsrauschen | Bündelausgleich; mehr als 3 Ansichten |
| **Landmark-Lokalisierungsrauschen** | ±1–2 px pro Punkt | Mittelung; Subpixel-Verfeinerung |

**Realistische Erwartung:**
- Standardisierte Aufnahme (Stativ, eine Sitzung, neutrale Mimik, bekannte Brennweite): **~1–2 mm** für gut in ≥ 2 Ansichten sichtbare Punkte — klinisch brauchbar.
- Hand-gehaltene, nicht-synchrone Patienten-Selfies: **3–5 mm+**, teils nicht klinisch brauchbar.

➡️ **Kernaussage:** Echtes 3D per Triangulation steht und fällt mit einem **standardisierten Aufnahme-Protokoll.** Das ist gleichzeitig die billigste Qualitäts-Maßnahme und deckt sich mit dem Strategie-Review (standardisierte Fotos sind Voraussetzung für jede mm-Aussage).

---

## 3b. Perspektivische Korrektur — warum echtes 3D auch variable Abstände rettet

Die Iris-Kalibrierung löst den **Maßstab**: Ein Selfie aus 30 cm und ein Foto aus 2 m liefern beide korrekte mm, weil die Iris (11,7 mm) den Abstand herausrechnet. Sie löst aber **nicht** die **perspektivische Verzerrung**: Bei kurzer Aufnahme-Distanz ragen nahe Strukturen (Nase) optisch stärker heraus als entfernte (Ohren) — die Proportionen kippen. Aus einem einzelnen 2D-Bild ist das nicht herausrechenbar; deshalb empfehlen wir heute einen Mindestabstand.

**Echtes 3D korrigiert das automatisch** — und macht damit die letzte große aufnahmebedingte Fehlerquelle (neben der Pose, die wir bereits messen) beherrschbar:

1. Statt der orthografischen Näherung ein **perspektivisches Kameramodell** (Lochkamera) verwenden.
2. Die **Aufnahme-Distanz mitschätzen** — sie folgt aus der Iris-Pixelgröße und der Brennweite: Iris = 11,7 mm bekannt ⇒ bei bekannter Brennweite ergibt die Iris-Pixelgröße direkt die Kamera-Distanz. EXIF liefert die Brennweite; fehlt sie, wird sie im Bündelausgleich mitoptimiert.
3. **Bündelausgleich (bundle adjustment)** optimiert Kamerapose + Distanz + Brennweite gemeinsam mit der 3D-Struktur, bis alle Ansichten konsistent sind.

**Effekt:** Die mm-Werte werden robust gegen den Aufnahme-Abstand — egal ob jemand das Handy selbst hält oder aus 2 m fotografiert wird. Das ist der Schritt, der „funktioniert mit beliebigen Fotos" und „klinische mm-Genauigkeit" am nächsten zusammenbringt.

> **Reihenfolge:** Phase 1/2 nutzt zunächst die orthografische Näherung (einfach, deterministisch, sofort gegen synthetische Daten verifizierbar). Die perspektivische Korrektur ist die gezielte Genauigkeits-Stufe **danach** (Phase 2+): Sie ersetzt die Näherung durch das volle Kameramodell, sobald die Triangulation an echten Aufnahmen steht. Beides bleibt reine Geometrie — deterministisch und auditierbar.

---

## 4. Integration in die bestehende Pipeline

Die Rekonstruktion ist eine **neue Stufe**, die *vor* den Analyse-Engines läuft — der Rest bleibt:

```
preprocess → detect (478 + pose) → calibrate (iris)
   → [NEU] reconstruct_3d  →  metrische 3D-Punktwolke (478 pts)
   → engines (volume/profile lesen ECHTE Tiefe statt relativer z)
   → fusion → zone_analyzer → plan
```

- Neues Modul `analysis/multiview_reconstruction.py` (Triangulation + metrische Skalierung).
- `volume_engine` / `profile_engine`: Tiefen-/Projektionsmaße aus der 3D-Punktwolke statt `_z_depth_mm` / 2D-x-Delta.
- Sobald eine Messung aus echter 3D kommt, wird sie aus `EXPERIMENTAL_MEASUREMENTS` entfernt → `estimated=false`. **Genau hier wird aus „ehrlich gekennzeichnet" → „echte Messung".**
- `multi_view_fusion` (heute Messwert-Fusion) wird für diese Maße überflüssig bzw. zur Konsistenzprüfung.

---

## 5. Aufwand (Weg A) — grobe Phasen

| Phase | Inhalt | Größenordnung |
|---|---|---|
| 0 | **Aufnahme-Protokoll** definieren + Testdatensatz mit Caliper-Ground-Truth (n≥20) | klein, aber Voraussetzung |
| 1 | Kamera-Modell + Triangulations-Prototyp (2 Ansichten, statische Landmarks) | mittel |
| 2 | Metrische Skalierung (Iris) + Bündelausgleich + Genauigkeits-Messung vs. Caliper (orthografische Baseline) | mittel |
| 2b | **Perspektivische Korrektur** (§3b): volles Lochkameramodell + Distanz-/Brennweiten-Schätzung — robust gegen variablen Aufnahme-Abstand | mittel |
| 3 | Engines auf 3D umstellen; Felder von `estimated` befreien, sobald validiert | mittel |
| 4 | Robustheit (fehlende Ansichten, schlechte Pose) + Quality-Gate „3D unzuverlässig" | klein–mittel |

Bewusst phasenweise: Nach Phase 2 steht eine **Zahl** (erreichte mm-Genauigkeit), die über Weitergehen oder Wechsel zu Weg B (Tiefensensor) entscheidet — bevor großer Engine-Umbau passiert.

---

## 6. Empfehlung

1. **Weg A (Landmark-Triangulation)** als ersten Schritt — passt zu Stack, Determinismus-Anforderung und vorhandenen Daten; deterministisch und auditierbar.
2. **Voraussetzung zuerst:** standardisiertes Aufnahme-Protokoll + Caliper-Ground-Truth. Ohne das ist jede 3D-Zahl wieder nur eine schönere Schätzung.
3. **Weg B (Tiefensensor)** ernsthaft erwägen, falls die Praxis ohnehin standardisiert aufnimmt — er umgeht das Genauigkeitsproblem komplett und ist der direkteste Weg zu „das Beste am Markt".
4. **Weg C (3DMM)** vorerst nicht — Black-Box + GPU widersprechen dem Medizinprodukt-/Einzelpraxis-Profil.

**Reihenfolge gegenüber Gate 0:** Dieses Feature ist das Premium-Ziel, aber die Regulatorik-Klärung (MDR-Scope + DPIA) bleibt laut Strategie-Review der vorgelagerte Engpass — echtes 3D macht das Produkt *besser*, beantwortet aber nicht, ob es *betrieben werden darf*.

---

## Quellen
- [MICA — Towards Metrical Reconstruction of Human Faces (ECCV 2022)](https://github.com/Zielon/MICA)
- [Pixel3DMM — Single-Image 3D Face Reconstruction (2025)](https://simongiebenhain.github.io/pixel3dmm/)
- [FLAME-Universe (Modelle/Code-Sammlung)](https://github.com/TimoBolkart/FLAME-Universe)
- [Multi-view Consensus CNN for 3D Facial Landmark Placement](https://arxiv.org/pdf/1910.06007)
