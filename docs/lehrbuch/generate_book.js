const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat,
  TableOfContents, HeadingLevel, BorderStyle, WidthType, ShadingType,
  PageNumber, PageBreak
} = require("docx");

// ─── Helpers ───

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };

function h1(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 480, after: 240 }, children: [new TextRun({ text, bold: true })] });
}
function h2(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 360, after: 180 }, children: [new TextRun({ text, bold: true })] });
}
function h3(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 240, after: 120 }, children: [new TextRun({ text, bold: true })] });
}
function p(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 120 },
    alignment: opts.align || AlignmentType.LEFT,
    ...opts.paragraphOpts,
    children: [new TextRun({ text, ...opts })]
  });
}
function pb() { return new Paragraph({ children: [new PageBreak()] }); }
function placeholder() { return p("Inhalt folgt in einer sp\u00e4teren Ausgabe.", { italics: true, color: "888888" }); }

function makeTable(headers, rows, colWidths) {
  const totalWidth = colWidths.reduce((a, b) => a + b, 0);
  const headerRow = new TableRow({
    children: headers.map((h, i) => new TableCell({
      borders, width: { size: colWidths[i], type: WidthType.DXA },
      shading: { fill: "2C3E50", type: ShadingType.CLEAR },
      margins: cellMargins,
      children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, color: "FFFFFF", font: "Arial", size: 20 })] })]
    }))
  });
  const dataRows = rows.map(row => new TableRow({
    children: row.map((cell, i) => new TableCell({
      borders, width: { size: colWidths[i], type: WidthType.DXA },
      margins: cellMargins,
      children: [new Paragraph({ children: [new TextRun({ text: String(cell), font: "Arial", size: 20 })] })]
    }))
  }));
  return new Table({ width: { size: totalWidth, type: WidthType.DXA }, columnWidths: colWidths, rows: [headerRow, ...dataRows] });
}

// ─── Kapitel 9: Die 19 Behandlungszonen (FULL) ───

function kapitel9() {
  const content = [];
  content.push(h1("Kapitel 9: Die 19 Behandlungszonen"));
  content.push(p("Die systematische Gesichtsanalyse erfordert ein standardisiertes Zonensystem, das anatomische Strukturen mit klinischen Behandlungsoptionen verkn\u00fcpft. Inspiriert von de Maios MD-Codes-Konzept (2021) definiert das hier vorgestellte System 19 anatomische Behandlungszonen, die das gesamte Gesicht abdecken. Jede Zone ist durch spezifische Landmarks, Referenzwerte und Behandlungsimplikationen charakterisiert."));
  content.push(p("Der entscheidende Vorteil dieses Ansatzes gegen\u00fcber einer rein messwertbasierten Analyse liegt in der direkten klinischen Anwendbarkeit: Statt abstrakter Zahlen wie \u201eSymmetrie-Score: 87\u201c erh\u00e4lt der Behandler eine zonenspezifische Aussage mit Schweregrad, Befunden und konkreten Behandlungsempfehlungen."));

  // 9.1
  content.push(h2("9.1 Systematik des Zonensystems"));
  content.push(p("Das Zonensystem gliedert das Gesicht in vier Hauptregionen:"));
  content.push(p("\u2022 Upper Face (Oberes Gesichtsdrittel): Temporalregion, Brauen, Glabella, Stirn", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Midface (Mittelgesicht): Jochbogen, Wangenh\u00f6he, Mittelwange, Tr\u00e4nental, Nasolabialfalte", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Lower Face (Unteres Gesichtsdrittel): Lippen, Marionettenfalten, Kinn, Kieferlinie", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Profile (Profilspezifisch): Nasenprofil, Lippenprojektion, Kinn-Hals-Winkel", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Jede Zone besitzt folgende Attribute:"));
  content.push(p("\u2013 Zone-ID: Eindeutiger Bezeichner (z.\u202fB. Ck2 f\u00fcr Zygomatic Eminence)"));
  content.push(p("\u2013 Landmarks: Welche der 478 Gesichtspunkte die Zone definieren"));
  content.push(p("\u2013 Referenzwerte: Idealbereiche f\u00fcr klinische Messungen (in mm, Grad oder Scores)"));
  content.push(p("\u2013 View-Priorit\u00e4t: Welche Kameraposition (frontal, profil, oblique) prim\u00e4r f\u00fcr die Analyse genutzt wird"));
  content.push(p("\u2013 Severity-Gewichte: Welche Faktoren (Messabweichung, Volumendefizit, Asymmetrie, Alterung) den Schweregrad am st\u00e4rksten beeinflussen"));

  // 9.2 Upper Face
  content.push(h2("9.2 Upper Face"));

  // T1
  content.push(h3("Zone T1 \u2014 Temporal (Schl\u00e4fenregion)"));
  content.push(p("Region: Upper Face | Prim\u00e4re Ansicht: Oblique | Sekund\u00e4re Ansichten: \u2014 | Fusion: Nein", { bold: true }));
  content.push(p("Die Temporalregion umfasst die Fossa temporalis \u2014 die laterale Einbuchtung oberhalb des Jochbogens. Eine Eintiefung (Temporal Hollowing) ist ein fr\u00fcher und oft \u00fcbersehener Indikator f\u00fcr altersbedingte Volumenatrophie. Der M. temporalis und das dar\u00fcber liegende Fettgewebe verlieren im Laufe der Jahre an Volumen, was zu einem skelettierten Erscheinungsbild des oberen Gesichtsdrittels f\u00fchrt."));
  content.push(p("Referenzwerte: temporal_depth_mm: -2,0 bis 2,0 mm (Tiefe relativ zur Brauenlinie)"));
  content.push(p("Severity-Gewichte: Volumendefizit 0,6 | Asymmetrie 0,2 | Alterung 0,2"));
  content.push(p("Klinische Relevanz: Eine Eintiefung > 2 mm deutet auf signifikanten Volumenverlust hin. Die Behandlung erfolgt bevorzugt mit Biostimulantien (Sculptra, Radiesse) in der tiefen subkutanen Ebene. Zu beachten ist die A. temporalis superficialis, die in dieser Region verl\u00e4uft."));

  // Bw1
  content.push(h3("Zone Bw1 \u2014 Brow Lateral (Laterale Braue)"));
  content.push(p("Region: Upper Face | Prim\u00e4re Ansicht: Frontal | Sekund\u00e4re: Oblique | Fusion: Ja", { bold: true }));
  content.push(p("Die laterale Brauenposition ist einer der wichtigsten \u00e4sthetischen Parameter des oberen Gesichtsdrittels. Eine Ptosis der lateralen Braue f\u00fchrt zu einem m\u00fcden, gealterten Erscheinungsbild und kann die laterale Sicht einschr\u00e4nken. Die ideale Brauenposition liegt bei Frauen oberhalb des Orbitarands, bei M\u00e4nnern auf H\u00f6he des Orbitarands."));
  content.push(p("Referenzwerte: brow_height_mm: 20\u201325 mm (\u00fcber Orbitalrand) | brow_asymmetry_mm: 0\u20131,5 mm"));
  content.push(p("Severity-Gewichte: Messabweichung 0,4 | Asymmetrie 0,4 | Alterung 0,2"));
  content.push(p("Klinische Relevanz: Asymmetrien > 1,5 mm sind klinisch sichtbar. Eine Brauenanh\u00e4bung kann durch tiefe supraperiostale Filler-Injektion oder durch gezielten Neurotoxin-Einsatz im lateralen Orbicularis oculi erreicht werden."));

  // Bw2
  content.push(h3("Zone Bw2 \u2014 Glabella (Glabellarkomplex)"));
  content.push(p("Region: Upper Face | Prim\u00e4re Ansicht: Frontal | Sekund\u00e4re: \u2014 | Fusion: Nein", { bold: true }));
  content.push(p("Die Glabellaregion umfasst den M. corrugator supercilii und den M. procerus. Hyperaktivit\u00e4t dieser Muskeln f\u00fchrt zu den charakteristischen vertikalen \u201e11-Linien\u201c und horizontalen Glabellafalten. Diese Zone ist die am h\u00e4ufigsten mit Botulinumtoxin behandelte Region weltweit."));
  content.push(p("Referenzwerte: glabellar_depth_mm: 0\u20131,0 mm (Faltentiefe in Ruhe)"));
  content.push(p("Severity-Gewichte: Messabweichung 0,3 | Alterung 0,4 | Muskelaktivit\u00e4t 0,3"));
  content.push(p("Klinische Relevanz: Der Severity-Score wird hier stark durch Muskelaktivit\u00e4t (via Blendshape-Analyse) beeinflusst. Eine hohe Corrugator-Aktivit\u00e4t in Ruhe (Blendshape browDownLeft/Right > 0,2) deutet auf erh\u00f6hten Behandlungsbedarf hin."));

  // Fo1
  content.push(h3("Zone Fo1 \u2014 Forehead (Stirn)"));
  content.push(p("Region: Upper Face | Prim\u00e4re Ansicht: Frontal | Sekund\u00e4re: Profil | Fusion: Nein", { bold: true }));
  content.push(p("Die Stirnzone wird vom M. frontalis dominiert, dessen Kontraktion horizontale Stirnfalten erzeugt. Der Frontalis ist h\u00e4ufig kompensatorisch hyperaktiv, wenn eine Brauenptosis vorliegt \u2014 der Patient hebt unbewusst die Brauen, um das Sichtfeld freizuhalten."));
  content.push(p("Severity-Gewichte: Alterung 0,5 | Muskelaktivit\u00e4t 0,3 | Messabweichung 0,2"));
  content.push(p("Klinische Relevanz: WICHTIG \u2014 Die Stirn darf niemals isoliert mit Neurotoxin behandelt werden, ohne gleichzeitig die Glabella mitzubehandeln. Ohne Corrugator-Relaxation f\u00fchrt eine Frontalis-Schw\u00e4chung zur Brauenptosis. Bei Patienten mit bereits tiefer Brauenposition sind niedrigere Dosen indiziert."));

  // 9.3 Midface
  content.push(h2("9.3 Midface"));

  // Ck1
  content.push(h3("Zone Ck1 \u2014 Zygomatic Arch (Jochbogen)"));
  content.push(p("Region: Midface | Prim\u00e4re Ansicht: Oblique | Sekund\u00e4re: Frontal | Fusion: Ja", { bold: true }));
  content.push(p("Der Jochbogen bildet das kn\u00f6cherne Ger\u00fcst des Mittelgesichts. Die bizygomatische Breite (Abstand zwischen den beiden Jochbogenspitzen) ist ein Schl\u00fcsselparameter f\u00fcr die Gesichtsproportionen. Diese Zone repr\u00e4sentiert die skelettale Basis, auf der alle Weichgewebebehandlungen des Mittelgesichts aufbauen."));
  content.push(p("Referenzwerte: bizygomatic_width_mm: 125\u2013145 mm"));
  content.push(p("Severity-Gewichte: Messabweichung 0,5 | Asymmetrie 0,3 | Volumendefizit 0,2"));
  content.push(p("Klinische Relevanz: Eine Augmentation des Jochbogens schafft die strukturelle Grundlage f\u00fcr weitere Midface-Behandlungen. Behandlung mit hochvernetzten HA-Fillern (G\u2019 > 200 Pa) oder CaHA in supraperiostaler Bolustechnik."));

  // Ck2
  content.push(h3("Zone Ck2 \u2014 Zygomatic Eminence (Wangenh\u00f6he)"));
  content.push(p("Region: Midface | Prim\u00e4re Ansicht: Oblique | Sekund\u00e4re: Frontal | Fusion: Ja", { bold: true }));
  content.push(p("Die Wangenh\u00f6he (Eminentia zygomatica) ist der Schl\u00fcsselpunkt f\u00fcr die Ogee-Kurve \u2014 jene S-f\u00f6rmige Konturlinie, die von der lateralen Stirn \u00fcber die Wangenh\u00f6he in die Wangenvertiefung verl\u00e4uft. Eine Abflachung der Ogee-Kurve ist eines der fr\u00fchesten und auff\u00e4lligsten Zeichen der Mittelgesichtsalterung."));
  content.push(p("Referenzwerte: ogee_curve_score: 70\u2013100 (Flie\u00dfende S-Kurve) | malar_prominence_ratio: 0,75\u20131,0"));
  content.push(p("Severity-Gewichte: Volumendefizit 0,5 | Messabweichung 0,3 | Asymmetrie 0,2"));
  content.push(p("Klinische Relevanz: Diese Zone hat den h\u00f6chsten Einfluss auf das \u00e4sthetische Gesamtergebnis im Mittelgesicht. Die Wiederherstellung des Malar-Volumens verbessert nicht nur den Ogee-Score, sondern reduziert sekundaer auch die Nasolabialfalte und das Tr\u00e4nental."));

  // Ck3
  content.push(h3("Zone Ck3 \u2014 Anteromedial Cheek (Mittelwange)"));
  content.push(p("Region: Midface | Prim\u00e4re Ansicht: Oblique | Sekund\u00e4re: Frontal | Fusion: Ja", { bold: true }));
  content.push(p("Die anteromediale Wange umfasst das Weichgewebe zwischen Jochbogen und Nasolabialfalte. Volumenverlust in dieser Zone vertieft die Nasolabialfalte und f\u00fchrt zu einer Abflachung des Mittelgesichtsprofils. Das SOOF (Suborbicularis Oculi Fat) und das malare Fettpolster sind die relevanten anatomischen Strukturen."));
  content.push(p("Severity-Gewichte: Volumendefizit 0,5 | Alterung 0,3 | Asymmetrie 0,2"));
  content.push(p("Klinische Relevanz: Behandlung mit mittelvernetzten HA-Fillern oder Skin-Boostern (Profhilo) f\u00fcr Hautqualit\u00e4tsverbesserung. H\u00e4ufig ist eine Volumenauff\u00fcllung in Ck2 ausreichend, um sekundaer auch Ck3 zu verbessern."));

  // Tt1
  content.push(h3("Zone Tt1 \u2014 Tear Trough (Tr\u00e4nental)"));
  content.push(p("Region: Midface | Prim\u00e4re Ansicht: Frontal | Sekund\u00e4re: Oblique | Fusion: Ja", { bold: true }));
  content.push(p("Das Tr\u00e4nental (Sulcus palpebromalaris) ist die Vertiefung zwischen Unterlid und Wange. Diese Zone ist anatomisch komplex und geh\u00f6rt zu den anspruchsvollsten Behandlungsarealen in der \u00e4sthetischen Medizin. Die d\u00fcnne Haut, die N\u00e4he zur A. angularis und das Risiko eines Tyndall-Effekts erfordern h\u00f6chste Pr\u00e4zision."));
  content.push(p("Referenzwerte: tear_trough_depth_mm: 0\u20132,0 mm"));
  content.push(p("Severity-Gewichte: Volumendefizit 0,5 | Asymmetrie 0,3 | Alterung 0,2"));
  content.push(p("Klinische Relevanz: HOCHRISIKO-ZONE. Vor einer direkten Behandlung sollte stets gepr\u00fcft werden, ob eine Volumenauff\u00fcllung im Mittelgesicht (Ck2/Ck3) die Tr\u00e4nentaltiefe bereits ausreichend reduziert. Bei direkter Behandlung: stumpfe Kan\u00fcle bevorzugt, maximal 0,1\u20130,2 ml pro Seite pro Sitzung, Kontrolle nach 2 Wochen."));

  // Ns1
  content.push(h3("Zone Ns1 \u2014 Nasolabial Fold (Nasolabialfalte)"));
  content.push(p("Region: Midface | Prim\u00e4re Ansicht: Frontal | Sekund\u00e4re: Oblique | Fusion: Ja", { bold: true }));
  content.push(p("Die Nasolabialfalte ist eine der am h\u00e4ufigsten behandelten Strukturen in der \u00e4sthetischen Medizin. Ihre Tiefe korreliert direkt mit dem Volumenverlust im Mittelgesicht \u2014 sie ist ein Symptom, nicht die prim\u00e4re Pathologie. Ein h\u00e4ufiger Behandlungsfehler ist die isolierte F\u00fcllung der Falte ohne Adressierung des urs\u00e4chlichen Mittelgesichtsvolumendefizits."));
  content.push(p("Referenzwerte: nasolabial_depth_mm: 0\u20133,0 mm | nasolabial_asymmetry_mm: 0\u20131,5 mm"));
  content.push(p("Severity-Gewichte: Volumendefizit 0,4 | Messabweichung 0,3 | Asymmetrie 0,3"));
  content.push(p("Klinische Relevanz: Die klinische Reihenfolge ist entscheidend: Zuerst Midface-Volumen (Ck2) wiederherstellen, dann die Resttiefe der Nasolabialfalte beurteilen. In vielen F\u00e4llen reduziert sich die Faltentiefe allein durch die Mittelgesichtsbehandlung um 30\u201350 %."));

  // 9.4 Lower Face
  content.push(h2("9.4 Lower Face"));

  // Lp1
  content.push(h3("Zone Lp1 \u2014 Upper Lip (Oberlippe)"));
  content.push(p("Region: Lower Face | Prim\u00e4re Ansicht: Frontal | Sekund\u00e4re: Profil | Fusion: Ja", { bold: true }));
  content.push(p("Die Oberlippe umfasst das Vermilion (Lippenrot), den Vermilionrand (Lippensaum) und den Cupid\u2019s Bow. Die Lippenanalyse ber\u00fccksichtigt Volumen, Definition und Symmetrie. Das ideale Verh\u00e4ltnis von Ober- zu Unterlippe betr\u00e4gt etwa 1:1,6 (Golden Lip Ratio)."));
  content.push(p("Referenzwerte: upper_lip_height_mm: 6\u20139 mm | lip_ratio: 0,5\u20130,7 | cupid_bow_asymmetry_pct: 0\u20135 %"));
  content.push(p("Severity-Gewichte: Messabweichung 0,5 | Asymmetrie 0,3 | Volumendefizit 0,2"));
  content.push(p("Klinische Relevanz: Behandlung mit weichen HA-Fillern (G\u2019 < 130 Pa). Technik: Serielle Punktion entlang des Vermilionrands f\u00fcr Definition, Mikrotr\u00f6pfchen im Lippenk\u00f6rper f\u00fcr Volumen. Zu beachten: A. labialis superior."));

  // Lp2
  content.push(h3("Zone Lp2 \u2014 Lower Lip (Unterlippe)"));
  content.push(p("Region: Lower Face | Prim\u00e4re Ansicht: Frontal | Sekund\u00e4re: Profil | Fusion: Ja", { bold: true }));
  content.push(p("Die Unterlippe ist typischerweise voller als die Oberlippe und ben\u00f6tigt seltener eine Augmentation. Bei einer Behandlung ist darauf zu achten, dass das Verh\u00e4ltnis zur Oberlippe (Lip Ratio) erhalten oder auf den Idealwert hin korrigiert wird."));
  content.push(p("Referenzwerte: lower_lip_height_mm: 9\u201314 mm"));
  content.push(p("Severity-Gewichte: Messabweichung 0,5 | Asymmetrie 0,2 | Volumendefizit 0,3"));

  // Lp3
  content.push(h3("Zone Lp3 \u2014 Lip Corners (Mundwinkel)"));
  content.push(p("Region: Lower Face | Prim\u00e4re Ansicht: Frontal | Sekund\u00e4re: \u2014 | Fusion: Nein", { bold: true }));
  content.push(p("Abw\u00e4rtsh\u00e4ngende Mundwinkel (Downturn) sind ein h\u00e4ufiges Zeichen der Alterung und vermitteln einen traurigen oder unzufriedenen Gesichtsausdruck. Die Kommissuren k\u00f6nnen mit minimalen Filler-Mengen oder einem Neurotoxin-Einsatz im M. depressor anguli oris korrigiert werden."));
  content.push(p("Referenzwerte: mouth_corner_angle_deg: -2 bis 5 Grad (negativ = Downturn)"));
  content.push(p("Severity-Gewichte: Messabweichung 0,4 | Asymmetrie 0,3 | Alterung 0,3"));

  // Mn1
  content.push(h3("Zone Mn1 \u2014 Marionette Lines (Marionettenfalten)"));
  content.push(p("Region: Lower Face | Prim\u00e4re Ansicht: Frontal | Sekund\u00e4re: Oblique | Fusion: Ja", { bold: true }));
  content.push(p("Marionettenfalten verlaufen von den Mundwinkeln abw\u00e4rts zum Kinn. Ihre Tiefe korreliert mit Jowling (H\u00e4ngewangen) und Volumenverlust im unteren Gesichtsdrittel. \u00c4hnlich wie bei der Nasolabialfalte ist die isolierte F\u00fcllung der Falte ohne Behandlung der Ursache (Kieferkontur, Pre-Jowl) klinisch suboptimal."));
  content.push(p("Severity-Gewichte: Volumendefizit 0,4 | Alterung 0,4 | Asymmetrie 0,2"));

  // Jw1
  content.push(h3("Zone Jw1 \u2014 Pre-Jowl Sulcus"));
  content.push(p("Region: Lower Face | Prim\u00e4re Ansicht: Frontal | Sekund\u00e4re: Oblique | Fusion: Ja", { bold: true }));
  content.push(p("Der Pre-Jowl-Sulcus ist die Einbuchtung lateral des Kinns, die durch Volumenatrophie und Gewebeabsenkung (Jowling) entsteht. Eine Auff\u00fcllung mit strukturellen Fillern in supraperiostaler Technik stellt die Kieferkontur wieder her."));
  content.push(p("Severity-Gewichte: Volumendefizit 0,5 | Alterung 0,3 | Asymmetrie 0,2"));

  // Ch1
  content.push(h3("Zone Ch1 \u2014 Chin (Kinn)"));
  content.push(p("Region: Lower Face | Prim\u00e4re Ansicht: Profil | Sekund\u00e4re: Frontal | Fusion: Ja", { bold: true }));
  content.push(p("Die Kinnprojektion wird am Pogonion gemessen \u2014 dem am weitesten anterior gelegenen Punkt des Kinns. Die Position wird relativ zur Ricketts-E-Linie und zur Subnasale-Vertikalen beurteilt. Ein retrudiertes Kinn (Retrognathie) verst\u00e4rkt die Jowl-Bildung und verschlechtert den Kinn-Hals-Winkel."));
  content.push(p("Referenzwerte: chin_projection_mm: -4,0 bis 0,0 mm (hinter E-Linie)"));
  content.push(p("Severity-Gewichte: Messabweichung 0,6 | Asymmetrie 0,2 | Volumendefizit 0,2"));
  content.push(p("Klinische Relevanz: Die Kinnaugmentation ist eine der effektivsten strukturellen Behandlungen. Supraperiostale Bolusinjektion mit hochvernetztem HA-Filler (Volux, G\u2019 350 Pa) oder CaHA. Der N. mentalis muss geschont werden."));

  // Jl1
  content.push(h3("Zone Jl1 \u2014 Jawline (Kieferlinie)"));
  content.push(p("Region: Lower Face | Prim\u00e4re Ansicht: Profil | Sekund\u00e4re: Frontal, Oblique | Fusion: Ja", { bold: true }));
  content.push(p("Die Kieferlinie definiert die untere Gesichtskontur. Der Gonialwinkel (Kieferwinkel) liegt idealerweise zwischen 110 und 130 Grad. Eine unscharfe Kieferlinie kann durch Filler-Augmentation entlang des Mandibularrands geschaerft werden."));
  content.push(p("Referenzwerte: gonial_angle_deg: 110\u2013130 Grad"));
  content.push(p("Severity-Gewichte: Messabweichung 0,4 | Asymmetrie 0,3 | Alterung 0,3"));
  content.push(p("Klinische Relevanz: Linear-Threading-Technik entlang des Mandibularrands. Palpation der A. facialis an der Incisura mandibulae vor Injektion obligat."));

  // 9.5 Profile
  content.push(h2("9.5 Profil-spezifische Zonen"));

  // Pf1
  content.push(h3("Zone Pf1 \u2014 Nasal Profile (Nasenprofil)"));
  content.push(p("Region: Profil | Prim\u00e4re Ansicht: Profil | Sekund\u00e4re: \u2014 | Fusion: Nein", { bold: true }));
  content.push(p("Das Nasenprofil umfasst den Nasenr\u00fccken (Dorsum), die Nasenspitze und die Supratip-Region. Der Nasolabialwinkel (90\u2013105\u00b0) und der Nasofrontalwinkel (115\u2013135\u00b0) sind die zentralen Messparameter. H\u00f6cker (Hump) und Satteldeformit\u00e4ten k\u00f6nnen mit Filler non-chirurgisch korrigiert werden."));
  content.push(p("Referenzwerte: nasolabial_angle_deg: 90\u2013105\u00b0 | nasofrontal_angle_deg: 115\u2013135\u00b0"));
  content.push(p("Severity-Gewichte: Messabweichung 0,7 | Asymmetrie 0,1 | Volumendefizit 0,2"));
  content.push(p("Klinische Relevanz: HOCHRISIKO-ZONE. Die A. dorsalis nasi und die A. angularis verlaufen in unmittelbarer N\u00e4he. Gef\u00e4\u00dfverschl\u00fcsse k\u00f6nnen zu Hautnekrose und im schlimmsten Fall zu Erblindung f\u00fchren. Stumpfe Kan\u00fcle und langsame Injektion sind obligat."));

  // Pf2
  content.push(h3("Zone Pf2 \u2014 Lip Projection (Lippenprofil)"));
  content.push(p("Region: Profil | Prim\u00e4re Ansicht: Profil | Sekund\u00e4re: \u2014 | Fusion: Nein", { bold: true }));
  content.push(p("Die Lippenprojektion wird im Profil relativ zur Ricketts-E-Linie und zur Steiner-Linie beurteilt. Idealerweise liegt die Oberlippe 1\u20134 mm und die Unterlippe 0\u20132 mm hinter der E-Linie. Eine zu geringe Lippenprojektion kann durch Filler-Augmentation des Vermilion verbessert werden."));
  content.push(p("Referenzwerte: upper_lip_to_eline_mm: -4 bis -1 mm | lower_lip_to_eline_mm: -2 bis 0 mm"));
  content.push(p("Severity-Gewichte: Messabweichung 0,7 | Volumendefizit 0,3"));

  // Pf3
  content.push(h3("Zone Pf3 \u2014 Chin-Neck Angle (Kinn-Hals-Winkel)"));
  content.push(p("Region: Profil | Prim\u00e4re Ansicht: Profil | Sekund\u00e4re: \u2014 | Fusion: Nein", { bold: true }));
  content.push(p("Der cervicomentale Winkel definiert den \u00dcbergang von Kinn zu Hals. Ein Winkel von 105\u2013120\u00b0 gilt als ideal und vermittelt ein jugendliches, definiertes Profil. Ein stumpfer Winkel (> 130\u00b0) kann auf submentales Fett, Platysma-Laxizit\u00e4t oder Kinnretrusion hindeuten."));
  content.push(p("Referenzwerte: cervicomental_angle_deg: 105\u2013120\u00b0"));
  content.push(p("Severity-Gewichte: Messabweichung 0,5 | Alterung 0,3 | Volumendefizit 0,2"));

  // 9.6 View-Matrix
  content.push(h2("9.6 View-Matrix: Kameraposition und Zonenanalyse"));
  content.push(p("Die folgende Tabelle zeigt, welche Kameraposition f\u00fcr welche Zone prim\u00e4r oder sekund\u00e4r genutzt wird und ob eine Multi-View-Fusion sinnvoll ist."));

  const vmHeaders = ["Zone", "Zone-Name", "Frontal", "Profil", "Oblique", "Fusion"];
  const vmWidths = [800, 2200, 1400, 1400, 1400, 1000];
  const vmRows = [
    ["T1", "Temporal", "\u2014", "\u2014", "Prim\u00e4r", "Nein"],
    ["Bw1", "Brow Lateral", "Prim\u00e4r", "\u2014", "Sekund\u00e4r", "Ja"],
    ["Bw2", "Glabella", "Prim\u00e4r", "\u2014", "\u2014", "Nein"],
    ["Fo1", "Forehead", "Prim\u00e4r", "Sekund\u00e4r", "\u2014", "Nein"],
    ["Ck1", "Zygomatic Arch", "Sekund\u00e4r", "\u2014", "Prim\u00e4r", "Ja"],
    ["Ck2", "Zygomatic Eminence", "Sekund\u00e4r", "\u2014", "Prim\u00e4r", "Ja"],
    ["Ck3", "Anteromedial Cheek", "Sekund\u00e4r", "\u2014", "Prim\u00e4r", "Ja"],
    ["Tt1", "Tear Trough", "Prim\u00e4r", "\u2014", "Sekund\u00e4r", "Ja"],
    ["Ns1", "Nasolabial Fold", "Prim\u00e4r", "\u2014", "Sekund\u00e4r", "Ja"],
    ["Lp1", "Upper Lip", "Prim\u00e4r", "Sekund\u00e4r", "\u2014", "Ja"],
    ["Lp2", "Lower Lip", "Prim\u00e4r", "Sekund\u00e4r", "\u2014", "Ja"],
    ["Lp3", "Lip Corners", "Prim\u00e4r", "\u2014", "\u2014", "Nein"],
    ["Mn1", "Marionette Lines", "Prim\u00e4r", "\u2014", "Sekund\u00e4r", "Ja"],
    ["Jw1", "Pre-Jowl Sulcus", "Prim\u00e4r", "\u2014", "Sekund\u00e4r", "Ja"],
    ["Ch1", "Chin", "Sekund\u00e4r", "Prim\u00e4r", "\u2014", "Ja"],
    ["Jl1", "Jawline", "Sekund\u00e4r", "Prim\u00e4r", "Sekund\u00e4r", "Ja"],
    ["Pf1", "Nasal Profile", "\u2014", "Prim\u00e4r", "\u2014", "Nein"],
    ["Pf2", "Lip Projection", "\u2014", "Prim\u00e4r", "\u2014", "Nein"],
    ["Pf3", "Chin-Neck Angle", "\u2014", "Prim\u00e4r", "\u2014", "Nein"],
  ];
  content.push(makeTable(vmHeaders, vmRows, vmWidths));

  // 9.7 Severity
  content.push(h2("9.7 Severity-Berechnung"));
  content.push(p("Der Schweregrad (Severity) jeder Zone wird auf einer Skala von 0 bis 10 berechnet, wobei 0 keinen Behandlungsbedarf und 10 maximalen Behandlungsbedarf bedeutet. Die Berechnung basiert auf einer gewichteten Kombination von vier Faktoren:"));
  content.push(p("Severity = Messabweichung \u00d7 0,4 + Volumendefizit \u00d7 0,3 + Asymmetrie \u00d7 0,2 + Alterung \u00d7 0,1", { bold: true }));
  content.push(p("Jede Zone besitzt individuell angepasste Gewichte, die die klinische Relevanz der einzelnen Faktoren f\u00fcr diese spezifische Zone widerspiegeln. Beispielsweise hat die Glabella (Bw2) einen h\u00f6heren Alterungs- und Muskelaktivit\u00e4tsanteil, w\u00e4hrend die Wangenh\u00f6he (Ck2) st\u00e4rker vom Volumendefizit abh\u00e4ngt."));
  content.push(p("Klinische Interpretation der Severity-Stufen:", { bold: true }));

  const sevHeaders = ["Severity", "Beurteilung", "Empfehlung"];
  const sevWidths = [1500, 3000, 4860];
  const sevRows = [
    ["0\u20131", "Kein Befund", "Keine Behandlung erforderlich"],
    ["1\u20133", "Leichter Befund", "Behandlung optional, Patient entscheidet"],
    ["3\u20135", "Moderater Befund", "Behandlung empfohlen"],
    ["5\u20137", "Deutlicher Befund", "Behandlung indiziert"],
    ["7\u201310", "Schwerer Befund", "Dringende Behandlung, ggf. Ausschluss Pathologie"],
  ];
  content.push(makeTable(sevHeaders, sevRows, sevWidths));

  content.push(p("Der zusammengesetzte Aesthetic Score (0\u2013100) wird aus den gewichteten Severity-Werten aller Zonen berechnet: 100 bedeutet kein Behandlungsbedarf, 0 bedeutet maximaler Bedarf in allen Zonen. Die Gewichtung ber\u00fccksichtigt die regionale Bedeutung: Midface-Zonen werden mit Faktor 1,3, Lower-Face-Zonen mit 1,1, Upper-Face mit 1,0 und Profil-Zonen mit 0,9 gewichtet."));

  return content;
}

// ─── Kapitel 11: Produkte und Materialien (FULL) ───

function kapitel11() {
  const content = [];
  content.push(h1("Kapitel 11: Produkte und Materialien"));
  content.push(p("Die Auswahl des geeigneten Produkts ist neben der korrekten Injektionstechnik der wichtigste Faktor f\u00fcr ein \u00e4sthetisch ansprechendes und sicheres Behandlungsergebnis. Dieses Kapitel klassifiziert die verf\u00fcgbaren Produkte nach ihren rheologischen Eigenschaften und ordnet sie den anatomischen Behandlungszonen zu."));

  // 11.1
  content.push(h2("11.1 Einf\u00fchrung in die Produktklassen"));
  content.push(p("Die in der \u00e4sthetischen Medizin eingesetzten Produkte lassen sich in sechs Hauptkategorien einteilen:"));
  content.push(p("1. HA Deep (Hoher G\u2019): Hochvernetzte Hyalurons\u00e4ure-Filler f\u00fcr tiefe Volumisierung und strukturelle Unterst\u00fctzung. Typische Anwendung: Mittelgesicht, Kinn, Kieferlinie."));
  content.push(p("2. HA Medium: Mittlere Vernetzung f\u00fcr Konturierung und Faltenbehandlung. Typische Anwendung: Nasolabialfalte, Marionettenfalten."));
  content.push(p("3. HA Soft (Niedriger G\u2019): Weiche, flie\u00dff\u00e4hige Filler f\u00fcr dynamische Areale. Typische Anwendung: Lippen, Tr\u00e4nental, Perioralregion."));
  content.push(p("4. Nicht-HA Volumizer: Calciumhydroxylapatit (CaHA) und Poly-L-Milchs\u00e4ure (PLLA) \u2014 Biostimulantien mit langanhaltender Wirkung."));
  content.push(p("5. Neurotoxine: Botulinumtoxin Typ A zur Relaxation der mimischen Muskulatur."));
  content.push(p("6. Skin Booster: Niedrig vernetzte oder unvernetzte HA f\u00fcr Hauthydratation und -qualit\u00e4t."));

  // 11.2
  content.push(h2("11.2 Hyalurons\u00e4ure-Filler: Rheologie und Klassifikation"));
  content.push(p("Der elastische Modul G\u2019 (G-Prime) ist der zentrale Parameter f\u00fcr die Produktauswahl. Er beschreibt die Steifigkeit eines Filler-Gels und bestimmt seine F\u00e4higkeit, Gewebe anzuheben und seine Form zu behalten:"));
  content.push(p("\u2022 Hoher G\u2019 (> 200 Pa): Steifes Gel, gute Volumenprojektion, widersteht Gewebedruck. Ideal f\u00fcr supraperiostale Injektionen auf Knochen (Jochbogen, Kinn, Kieferlinie).", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Mittlerer G\u2019 (150\u2013200 Pa): Ausgewogenes Profil f\u00fcr Konturierung und m\u00e4\u00dfige Volumengebung. Geeignet f\u00fcr die tiefe subkutane Ebene.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Niedriger G\u2019 (< 150 Pa): Weiches, flexibles Gel, das nat\u00fcrliche Bewegung erh\u00e4lt. Essenziell f\u00fcr Lippen und periorbitale Region.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Ein weiterer wichtiger Parameter ist die Koh\u00e4sivit\u00e4t \u2014 die F\u00e4higkeit des Gels, als einheitliche Masse zusammenzubleiben. Hochkoh\u00e4sive Filler verteilen sich weniger und sind daher f\u00fcr pr\u00e4zise Volumenplatzierung geeignet."));

  // HA Table
  const haHeaders = ["Produkt", "Hersteller", "Kategorie", "G\u2019 (Pa)", "Viskosit\u00e4t", "Dauer (Mon.)", "Hauptindikationen"];
  const haWidths = [1400, 1100, 900, 800, 1000, 900, 2260];
  const haRows = [
    ["Juvederm Voluma", "Allergan", "HA Deep", "274", "Hoch", "12\u201318", "Mittelgesicht, Kinn"],
    ["Juvederm Volux", "Allergan", "HA Deep", "350", "Sehr hoch", "12\u201324", "Jawline, Kinn"],
    ["Juvederm Vollure", "Allergan", "HA Medium", "178", "Mittel", "12\u201318", "Nasolabial, Marionette"],
    ["Restylane Lyft", "Galderma", "HA Medium", "225", "Mittel-hoch", "9\u201312", "Mittelgesicht, Wange"],
    ["Juvederm Volbella", "Allergan", "HA Soft", "98", "Niedrig", "9\u201312", "Lippen, Tr\u00e4nental"],
    ["Restylane Kysse", "Galderma", "HA Soft", "125", "Mittel-niedrig", "9\u201312", "Lippen"],
    ["Teoxane RHA Kiss", "Teoxane", "HA Soft", "110", "Mittel-niedrig", "9\u201312", "Lippen"],
  ];
  content.push(p("Tabelle 11.1: \u00dcbersicht der HA-Filler nach rheologischen Eigenschaften", { bold: true }));
  content.push(makeTable(haHeaders, haRows, haWidths));

  // 11.3
  content.push(h2("11.3 Nicht-HA Volumizer"));

  content.push(h3("Radiesse (Calciumhydroxylapatit)"));
  content.push(p("Hersteller: Merz | Kategorie: Nicht-HA Volumizer | G\u2019: 350 Pa | Dauer: 12\u201318 Monate", { bold: true }));
  content.push(p("Radiesse besteht aus Calciumhydroxylapatit-Mikrosph\u00e4ren (CaHA) in einem Carboxymethylcellulose-Gel. Nach der Injektion wird das Tr\u00e4gergel resorbiert, w\u00e4hrend die CaHA-Partikel als Ger\u00fcst f\u00fcr die Neogenese von Kollagen Typ I und III dienen. Dieser biostimulatorische Effekt f\u00fchrt zu einer progressiven Gewebeverdickung \u00fcber 3\u20136 Monate."));
  content.push(p("Indikationen: Ck1 (Jochbogen), Ck2 (Wangenh\u00f6he), Ch1 (Kinn), Jl1 (Jawline), Jw1 (Pre-Jowl)"));
  content.push(p("Kontraindikation Lippen: Radiesse ist NICHT f\u00fcr die Lippenaugmentation zugelassen. Da CaHA nicht durch Hyaluronidase aufgel\u00f6st werden kann, ist eine Komplikationsbehandlung im Gef\u00e4\u00dfverschlussfall deutlich eingeschr\u00e4nkt.", { bold: true }));
  content.push(p("Technik: Supraperiostale Bolusinjektion oder tiefes Linear Threading. Aspiration vor Injektion obligat."));

  content.push(h3("Sculptra (Poly-L-Milchs\u00e4ure)"));
  content.push(p("Hersteller: Galderma | Kategorie: Nicht-HA Biostimulator | Dauer: 18\u201324 Monate", { bold: true }));
  content.push(p("Sculptra ist ein PLLA-basierter Biostimulator, der \u00fcber einen Zeitraum von 2\u20133 Behandlungssitzungen (im Abstand von 4\u20136 Wochen) eine progressive Volumenwiederherstellung bewirkt. Das Produkt wird vor der Anwendung rekonstituiert und verd\u00fcnnt."));
  content.push(p("Indikationen: T1 (Temporal), Ck2 (Wangenh\u00f6he), Ck3 (Mittelwange) \u2014 besonders bei diffusem Volumenverlust"));
  content.push(p("Technik: F\u00e4cher- oder Linear-Threading-Technik in der tiefen subkutanen Ebene. Massage nach Injektion (5-5-5-Regel: 5 Minuten, 5-mal t\u00e4glich, 5 Tage) zur Vermeidung von Knollenbildung."));

  // 11.4
  content.push(h2("11.4 Neurotoxine"));
  content.push(p("Botulinumtoxin Typ A (BoNT-A) hemmt die Acetylcholin-Freisetzung an der neuromuskul\u00e4ren Endplatte und f\u00fchrt zu einer vor\u00fcbergehenden Relaxation der behandelten Muskulatur. Die drei in Europa zugelassenen Pr\u00e4parate unterscheiden sich in ihrer Formulierung, Diffusionseigenschaft und Dosierung:"));

  content.push(h3("Botox (OnabotulinumtoxinA)"));
  content.push(p("Hersteller: Allergan | Dauer: 3\u20135 Monate"));
  content.push(p("Der Goldstandard unter den Neurotoxinen. Pr\u00e4zise Wirkung mit geringer Diffusion, was eine punktgenaue Applikation erm\u00f6glicht. Dosierung dient als Referenz f\u00fcr Umrechnungen."));

  content.push(h3("Dysport (AbobotulinumtoxinA)"));
  content.push(p("Hersteller: Galderma | Dauer: 3\u20135 Monate | Umrechnung: ca. 2,5:1 zu Botox"));
  content.push(p("H\u00f6herer Diffusionsradius als Botox \u2014 vorteilhaft f\u00fcr fl\u00e4chige Areale (Stirn), nachteilig bei pr\u00e4zisionsabh\u00e4ngigen Indikationen (Lip Flip)."));

  content.push(h3("Xeomin (IncobotulinumtoxinA)"));
  content.push(p("Hersteller: Merz | Dauer: 3\u20135 Monate | Umrechnung: 1:1 zu Botox"));
  content.push(p("Reines Neurotoxin ohne Komplexproteine. Theoretisch geringeres Risiko der Antik\u00f6rperbildung bei Langzeitanwendung. Besonders geeignet f\u00fcr Patienten, die auf herk\u00f6mmliche Pr\u00e4parate nicht mehr ansprechen (sekund\u00e4re Non-Responder)."));

  // Neurotoxin table
  content.push(p("Tabelle 11.2: Neurotoxin-Indikationen nach Zone", { bold: true }));
  const ntHeaders = ["Zone", "Zielmuskel", "Dosis (U)", "Indikation", "Sicherheitshinweise"];
  const ntWidths = [700, 1800, 900, 2200, 3760];
  const ntRows = [
    ["Bw2", "M. corrugator supercilii", "10\u201325", "Glabella-Komplex (\u201e11-Linien\u201c)", "Ptosis-Risiko bei zu tiefer Injektion"],
    ["Bw2", "M. procerus", "5\u201310", "Horizontale Glabellafalten", "Zentr. Injektion auf Proc. nasalis"],
    ["Fo1", "M. frontalis", "10\u201330", "Horizontale Stirnfalten", "IMMER Glabella mitbehandeln; Ptose-Risiko"],
    ["Lp1", "M. orbicularis oris", "2\u20136", "Lip Flip (Eversion Oberlippe)", "Sehr niedrige Dosen; Risiko inkompetenter Lippenschluss"],
  ];
  content.push(makeTable(ntHeaders, ntRows, ntWidths));

  // 11.5
  content.push(h2("11.5 Skin Booster"));

  content.push(h3("Profhilo"));
  content.push(p("Hersteller: IBSA | Konzentration: 32 mg + 32 mg HA | Technik: BAP | Tiefe: Subkutan | Dauer: 4\u20136 Monate", { bold: true }));
  content.push(p("Profhilo ist ein Hyalurons\u00e4ure-Bioremodeler (kein Volumenfiller) mit einer einzigartigen Formulierung aus hoch- und niedrigmolekularer HA. Die Injektion erfolgt an 5 Bio\u00e4sthetischen Punkten (BAP) pro Gesichtsh\u00e4lfte in der subkutanen Ebene. Das Produkt verteilt sich durch seine hohe Flie\u00dff\u00e4higkeit gleichm\u00e4\u00dfig im Gewebe und stimuliert die Produktion von Kollagen, Elastin und Adipozyten."));
  content.push(p("Indikationen: Ck3 (Mittelwange), T1 (Temporal) \u2014 Hautalterung, Elastizit\u00e4tsverlust, Hautqualit\u00e4tsverbesserung"));

  content.push(h3("Juvederm Volite"));
  content.push(p("Hersteller: Allergan | Technik: Mesotherapie/Intradermal | Tiefe: Intradermal | Dauer: 6\u20139 Monate", { bold: true }));
  content.push(p("Volite ist ein mikrodosierter HA-Filler f\u00fcr die intradermale Applikation. Durch multiple kleine Injektionspunkte wird die Hauthydratation, Elastizit\u00e4t und Gl\u00e4tte verbessert. Im Gegensatz zu Profhilo zielt Volite prim\u00e4r auf die Hautqualit\u00e4t, nicht auf Geweberemodeling."));

  // 11.6
  content.push(h2("11.6 Produktauswahl nach Injektionstiefe"));
  content.push(p("Die Injektionstiefe bestimmt ma\u00dfgeblich die Produktwahl. Die folgende Tabelle ordnet die Produktkategorien den anatomischen Injektionsebenen und typischen Behandlungszonen zu:"));

  content.push(p("Tabelle 11.3: Injektionstiefe, Produktkategorie und Zielzonen", { bold: true }));
  const depthHeaders = ["Injektionstiefe", "Produktkategorie", "Typische Zonen"];
  const depthWidths = [2500, 3000, 3860];
  const depthRows = [
    ["Supraperiostal (auf Knochen)", "HA Deep, CaHA", "Ck1, Ck2, Ch1, Jl1, Bw1"],
    ["Tief subkutan", "HA Medium, PLLA", "Ns1, Mn1, Ck3, T1"],
    ["Subkutan", "Skin Booster (Profhilo)", "Ck3, T1"],
    ["Subdermal", "HA Soft", "Lp1, Lp2, Tt1, Pf1, Lp3"],
    ["Intradermal", "Skin Booster (Volite)", "Ck3, T1"],
    ["Intramuskul\u00e4r", "Neurotoxin", "Bw2, Fo1"],
  ];
  content.push(makeTable(depthHeaders, depthRows, depthWidths));

  content.push(p("Entscheidend f\u00fcr die sichere Produktplatzierung ist die genaue Kenntnis der Gewebeschichten und der Gef\u00e4\u00dfanatomie in jeder Zone. Supraperiostale Injektionen sind in den meisten Zonen die sicherste Technik, da die gro\u00dfen Gef\u00e4\u00dfe \u00fcberwiegend in der subkutanen und subdermalen Ebene verlaufen."));

  return content;
}

// ─── Kapitel 6: Profilanalyse (FULL) ───

function kapitel6() {
  const content = [];
  content.push(h1("Kapitel 6: Profilanalyse"));
  content.push(p("Die Profilanalyse (laterale Kephalometrie) ist ein zentraler Baustein der aesthetischen Gesichtsdiagnostik. Sie wird anhand einer standardisierten Profilaufnahme (90\u00b0-Ansicht) durchgefuehrt und liefert Informationen, die aus der Frontalansicht nicht gewonnen werden koennen: die Projektion von Nase, Lippen und Kinn, den Kinn-Hals-Uebergang sowie das Nasenrueckenprofil (Dorsum nasi)."));
  content.push(p("Die hier vorgestellten Analysemethoden basieren auf der profile_engine des Aesthetic Biometrics Engine, die sechs Kernmetriken berechnet: Ricketts-E-Linie, Nasolabialwinkel, Steiner-Linie, Nasofrontalwinkel mit Dorsumanalyse, Cervicomental Angle und Chin Projection. Alle Messungen werden in Millimetern (via Iris-basierte Kalibrierung, vgl. Kapitel 3) oder in Grad angegeben."));
  content.push(p("Die Profilanalyse ergaenzt die Frontal- und Obliqueanalyse und ist insbesondere fuer die Zonen Ch1 (Kinn), Jl1 (Jawline), Pf1 (Nasenprofil), Pf2 (Lippenprofil) und Pf3 (Kinn-Hals-Winkel) des in Kapitel 9 beschriebenen Zonensystems massgeblich."));

  // 6.1 Ricketts E-Line
  content.push(h2("6.1 Ricketts E-Line (Aesthetische Linie)"));
  content.push(p("Die Ricketts-E-Linie (Esthetic Line) ist die bekannteste kephalometrische Referenzlinie fuer die Profilbeurteilung. Sie wurde von Robert M. Ricketts 1968 eingefuehrt und definiert die ideale Lippenposition im Profil."));

  content.push(h3("6.1.1 Definition und Konstruktion"));
  content.push(p("Die E-Linie wird als gerade Verbindung zwischen zwei Referenzpunkten gezogen:"));
  content.push(p("\u2022 Pronasale (Nasenspitze): Der am weitesten anterior projizierte Punkt der Nase", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Pogonion (Kinnspitze): Der am weitesten anterior projizierte Punkt des Weichteilkinns", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Die Position der Ober- und Unterlippe wird als senkrechter Abstand (Perpendikularabstand) zu dieser Linie gemessen. Dabei werden folgende Messpunkte verwendet:"));
  content.push(p("\u2022 Labrale superius: Der am weitesten anterior projizierte Punkt der Oberlippe (Vermiliongrenze)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Labrale inferius: Der am weitesten anterior projizierte Punkt der Unterlippe", { paragraphOpts: { indent: { left: 360 } } }));

  content.push(h3("6.1.2 Berechnung im System"));
  content.push(p("Die Engine berechnet den Perpendikularabstand jedes Lippenpunktes zur E-Linie mittels der point_to_line_distance-Funktion (vgl. Kapitel 3, Geometrie-Utilities). Der Abstand wird ueber die Iris-Kalibrierung in Millimeter umgerechnet. Negative Werte bedeuten, dass die Lippe hinter der E-Linie liegt (ideal), positive Werte bedeuten eine Position vor der Linie (Protrusion)."));
  content.push(p("Mathematische Formulierung:", { bold: true }));
  content.push(p("d = point_to_line_distance(Labrale, Pronasale, Pogonion)"));
  content.push(p("d_mm = Kalibrierung.to_mm(d_px)"));

  content.push(h3("6.1.3 Normwerte und Interpretation"));
  content.push(p("Die Normwerte fuer die Lippenposition relativ zur E-Linie sind:"));

  const elineHeaders = ["Parameter", "Messpunkt", "Idealbereich", "Interpretation bei Abweichung"];
  const elineWidths = [2200, 1800, 1800, 3560];
  const elineRows = [
    ["Oberlippe zur E-Linie", "Labrale superius", "-6,0 bis -1,0 mm", "< -6 mm: Retrudierte Lippe; > -1 mm: Protrusion"],
    ["Unterlippe zur E-Linie", "Labrale inferius", "-4,0 bis 0,0 mm", "< -4 mm: Retrudierte Lippe; > 0 mm: Protrusion"],
  ];
  content.push(p("Tabelle 6.1: Normwerte der Ricketts-E-Linie", { bold: true }));
  content.push(makeTable(elineHeaders, elineRows, elineWidths));

  content.push(p("Die Engine klassifiziert jeden Wert als \u201eideal\u201c (innerhalb des Normbereichs) oder \u201edeviant\u201c (ausserhalb). Die Zuordnung erfolgt durch:"));
  content.push(p("\u2022 upper_lip_ideal: WAHR wenn -6,0 \u2264 d_mm \u2264 -1,0", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 lower_lip_ideal: WAHR wenn -4,0 \u2264 d_mm \u2264 0,0", { paragraphOpts: { indent: { left: 360 } } }));

  content.push(h3("6.1.4 Klinische Relevanz"));
  content.push(p("Die E-Linie ist der wichtigste Indikator fuer die Lippenprofil-Beurteilung in der Zone Pf2 (Lip Projection, vgl. Kapitel 9). Eine Deviation ueber den Normbereich hinaus traegt direkt zum Severity-Score dieser Zone bei, wobei der Messabweichungsfaktor mit dem Gewicht 0,7 einfliesst."));
  content.push(p("Klinische Szenarien:", { bold: true }));
  content.push(p("\u2022 Retrudierte Oberlippe (< -6 mm): Kann auf Oberkieferretrusion oder Volumenverlust hindeuten. Behandlungsoptionen: HA-Filler-Augmentation des Vermilion (Lp1, vgl. Kapitel 11) oder kieferorthopaeische Korrektur.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Protrusion (> -1 mm Oberlippe, > 0 mm Unterlippe): Haeufig ethnisch bedingt (andere Normwerte fuer afrikanische und asiatische Populationen) oder durch bialveolaere Protrusion. Vor einer Behandlung muss die dentoalveolaere Aetiologie abgeklaert werden.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Diskrepanz Ober-/Unterlippe: Wenn nur eine Lippe ausserhalb des Normbereichs liegt, kann ein selektives Filler-Enhancement indiziert sein, um das Verhaeltnis zu harmonisieren.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Wichtig: Die E-Linie ist abhaengig von der Nase- und Kinnprojektion. Eine grosse Nase oder ein prominentes Kinn verschiebt die E-Linie nach anterior und laesst die Lippen retrudierter erscheinen. Daher sollte die E-Linie-Analyse stets im Kontext der Nasen- und Kinnanalyse (Abschnitte 6.4 und 6.6) interpretiert werden.", { bold: true }));

  // 6.2 Nasolabialwinkel
  content.push(h2("6.2 Nasolabialwinkel (Angulus Nasolabialis)"));

  content.push(h3("6.2.1 Definition"));
  content.push(p("Der Nasolabialwinkel (NLA) ist der Winkel zwischen der Nasenunterseite (Columella) und der Oberlippe. Er wird an drei Referenzpunkten gemessen:"));
  content.push(p("\u2022 Subnasale: Der Punkt am Uebergang von Columella zu Oberlippe (Scheitelpunkt des Winkels)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Pronasale: Die Nasenspitze (definiert die Columella-Linie)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Labrale superius: Der Oberlippenpunkt (definiert die Lippenlinie)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Berechnung: angle_between_points(Subnasale, Pronasale, Labrale_superius)"));

  content.push(h3("6.2.2 Normwerte"));
  content.push(p("Der ideale Nasolabialwinkel liegt zwischen 90\u00b0 und 105\u00b0."));

  const nlaHeaders = ["Winkelbereich", "Beurteilung", "Klinische Implikation"];
  const nlaWidths = [1800, 2500, 5060];
  const nlaRows = [
    ["< 90\u00b0", "Akuter NLA", "Ueberprojizierte/ueberrotierte Nasenspitze oder uebermaessige Oberlippenhoehe; haeufig bei postoperativer Ueberkorrektur"],
    ["90\u2013105\u00b0", "Ideal", "Harmonisches Verhaeltnis zwischen Nasenunterseite und Oberlippe"],
    ["> 105\u00b0", "Stumpfer NLA", "Unterrotierte Nasenspitze, retrudierte Oberlippe oder prognather Oberkiefer; haeufig bei Alterung durch Tip-Ptosis"],
  ];
  content.push(p("Tabelle 6.2: Klassifikation des Nasolabialwinkels", { bold: true }));
  content.push(makeTable(nlaHeaders, nlaRows, nlaWidths));

  content.push(h3("6.2.3 Messmethodik im System"));
  content.push(p("Die Engine verwendet die angle_between_points-Funktion, die den Winkel aus den drei Punkten im 2D-Raum berechnet. Die Messung erfolgt im Profilbild (90\u00b0-Ansicht), wobei die Kopfhaltung durch die Head-Pose-Estimation (Yaw, Pitch, Roll) validiert wird. Eine Abweichung der Kopfhaltung von der exakten Profilposition fuehrt zu einer Quality-Warning im Analyseergebnis."));
  content.push(p("Der NLA-Wert fliesst primaer in die Zone Pf1 (Nasenprofil) ein und wird fuer den Severity-Score mit dem Gewicht Messabweichung 0,7 beruecksichtigt (vgl. Kapitel 9, Zone Pf1)."));

  content.push(h3("6.2.4 Klinische Anwendung"));
  content.push(p("Der Nasolabialwinkel ist ein Schluesselparameter fuer die nicht-chirurgische Rhinoplastik (Zone Pf1, vgl. Kapitel 12). Folgende Interventionen koennen den NLA beeinflussen:"));
  content.push(p("\u2022 Filler im Bereich der Columella/Nasenspitze: Kann den NLA verkleinern (Tip Rotation nach oben) oder vergroessern (Tip Deprojection)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Filler im Bereich des Subnasale: Beeinflusst den Uebergangswinkel direkt", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Oberlippenaugmentation (Lp1): Eine Volumenzunahme der Oberlippe kann den NLA sekundaer veraendern", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("ACHTUNG: Zone Pf1 ist eine HOCHRISIKO-ZONE. Die A. dorsalis nasi und die A. angularis verlaufen in unmittelbarer Naehe (vgl. Kapitel 14, Abschnitt 14.1). Injektionen in der Nasenregion erfordern hoechste Vorsicht.", { bold: true }));

  // 6.3 Steiner-Linie
  content.push(h2("6.3 Steiner-Linie (S-Linie)"));

  content.push(h3("6.3.1 Definition und Konstruktion"));
  content.push(p("Die Steiner-Linie (S-Linie) wurde von Cecil C. Steiner als Alternative zur Ricketts-E-Linie eingefuehrt. Sie verbindet:"));
  content.push(p("\u2022 Subnasale: Der Punkt am Uebergang von Columella zu Oberlippe", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Pogonion: Die Kinnspitze (Weichteil)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Im Gegensatz zur E-Linie (die von der Nasenspitze ausgeht) nutzt die Steiner-Linie die Nasenbasis als Referenz. Dadurch ist sie weniger von der Nasengroesse abhaengig und kann als ergaenzende Validierung dienen."));

  content.push(h3("6.3.2 Berechnung und Normwerte"));
  content.push(p("Die Engine berechnet den Perpendikularabstand des Labrale superius (Oberlippenpunkt) zur Steiner-Linie:"));
  content.push(p("d = point_to_line_distance(Labrale_superius, Subnasale, Pogonion)"));
  content.push(p("d_mm = Kalibrierung.to_mm(d_px)"));

  const steinerHeaders = ["Parameter", "Idealposition", "Klinische Bedeutung"];
  const steinerWidths = [2500, 2500, 4360];
  const steinerRows = [
    ["Oberlippe zur S-Linie", "0 mm (auf der Linie) bis leicht davor", "Die Oberlippe sollte die Steiner-Linie beruehren oder minimal vor ihr liegen"],
    ["Positiver Wert", "> 0 mm (vor der Linie)", "Lippenprotrusion; kann auf bialveolaere Protrusion oder Ueberaugmentation hindeuten"],
    ["Negativer Wert", "< 0 mm (hinter der Linie)", "Retrudierte Oberlippe; Filler-Augmentation kann indiziert sein"],
  ];
  content.push(p("Tabelle 6.3: Interpretation der Steiner-Linie", { bold: true }));
  content.push(makeTable(steinerHeaders, steinerRows, steinerWidths));

  content.push(h3("6.3.3 Vergleich E-Linie vs. Steiner-Linie"));
  content.push(p("Die gleichzeitige Analyse beider Linien ergibt ein robusteres Bild der Lippenposition:"));

  const compHeaders = ["Eigenschaft", "Ricketts E-Linie", "Steiner S-Linie"];
  const compWidths = [2200, 3480, 3680];
  const compRows = [
    ["Ankerpunkte", "Pronasale \u2192 Pogonion", "Subnasale \u2192 Pogonion"],
    ["Nasenabhaengigkeit", "Hoch (Nasenspitze als Referenz)", "Gering (Nasenbasis als Referenz)"],
    ["Idealposition Oberlippe", "-6 bis -1 mm (hinter der Linie)", "0 mm (auf der Linie)"],
    ["Beste Anwendung", "Gesamtbeurteilung des Lippenprofils", "Validierung bei grosser/kleiner Nase"],
    ["Im System", "Primaeranalyse (e_line)", "Ergaenzungsanalyse (steiner_upper_lip_mm)"],
  ];
  content.push(p("Tabelle 6.4: Vergleich der Profillinien", { bold: true }));
  content.push(makeTable(compHeaders, compRows, compWidths));

  content.push(p("In der Praxis ist die E-Linie der Primaerparameter fuer die Zone Pf2 (Lip Projection), waehrend die Steiner-Linie als ergaenzende Validierung dient. Diskrepanzen zwischen beiden Linien weisen auf eine prominente Nase (E-Linie zeigt Retrusionseffekt, Steiner-Linie normal) oder ein retrudiertes Kinn (beide Linien abweichend) hin."));

  // 6.4 Nasofrontalwinkel und Dorsumprofil
  content.push(h2("6.4 Nasofrontalwinkel und Dorsumprofil"));

  content.push(h3("6.4.1 Nasofrontalwinkel (Angulus Nasofrontalis)"));
  content.push(p("Der Nasofrontalwinkel wird am Nasion (tiefster Punkt der Nasenwurzel) gemessen und durch drei Referenzpunkte definiert:"));
  content.push(p("\u2022 Nasion (Scheitelpunkt): Tiefster Punkt der Nasenwurzel an der Stirn-Nasen-Grenze", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Glabella: Der am weitesten anterior projizierte Punkt der Stirn zwischen den Brauen", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Rhinion: Der Punkt auf dem knoechernen Nasenruecken (Dorsum nasi)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Berechnung: angle_between_points(Nasion, Glabella, Rhinion)"));

  const nfHeaders = ["Winkelbereich", "Beurteilung", "Klinische Implikation"];
  const nfWidths = [1800, 2500, 5060];
  const nfRows = [
    ["< 115\u00b0", "Spitzer NFW", "Flache Nasenwurzel; kann durch Filler im Nasion-Bereich korrigiert werden"],
    ["115\u2013135\u00b0", "Ideal", "Harmonischer Stirn-Nasen-Uebergang mit gut definierter Nasenwurzel"],
    ["> 135\u00b0", "Stumpfer NFW", "Tiefe Nasenwurzel oder prominente Glabella; Filler-Reduktion in der Glabella oder Augmentation des Nasenrueckens"],
  ];
  content.push(p("Tabelle 6.5: Normwerte des Nasofrontalwinkels", { bold: true }));
  content.push(makeTable(nfHeaders, nfRows, nfWidths));

  content.push(h3("6.4.2 Dorsumprofil und Goode Ratio"));
  content.push(p("Das Dorsumprofil beschreibt die Form des Nasenrueckens in der Profilansicht. Die Engine analysiert zwei Parameter:"));

  content.push(p("A) Dorsumdeviation (Hump/Saddle Detection)", { bold: true }));
  content.push(p("Die Dorsumdeviation wird als Perpendikularabstand des Rhinion (hoechster Punkt des knoechernen Nasenrueckens) von der Linie Nasion\u2192Pronasale gemessen:"));
  content.push(p("dorsum_dev = point_to_line_distance(Rhinion, Nasion, Pronasale)"));
  content.push(p("dorsum_dev_mm = Kalibrierung.to_mm(dorsum_dev_px)"));

  const dorsumHeaders = ["Wert (mm)", "Befund", "Klinische Bedeutung"];
  const dorsumWidths = [1500, 2500, 5360];
  const dorsumRows = [
    ["> 0 mm (positiv)", "Dorsaler Hoecker (Hump)", "Knoechen-/Knorpelprotuberanz; non-chirurgische Korrektur durch Camouflage-Filler oberhalb und unterhalb des Hoeckers moeglich"],
    ["\u2248 0 mm", "Gerade (Straight Dorsum)", "Ideales gerades Profil des Nasenrueckens"],
    ["< 0 mm (negativ)", "Satteldeformitaet (Saddle)", "Einsenkung des Nasenrueckens; Filler-Augmentation auf dem Dorsum oder chirurgische Rekonstruktion"],
  ];
  content.push(p("Tabelle 6.6: Dorsumdeviation und Interpretation", { bold: true }));
  content.push(makeTable(dorsumHeaders, dorsumRows, dorsumWidths));

  content.push(p("B) Goode Ratio (Nasenprojektionsverhaeltnis)", { bold: true }));
  content.push(p("Die Goode Ratio ist das Verhaeltnis von Nasenprojektion (horizontaler Abstand von Subnasale zu Pronasale) zur Nasenlaenge (Strecke Nasion\u2192Pronasale):"));
  content.push(p("Goode Ratio = Nasenprojektion_px / Nasenlaenge_px"));

  const goodeHeaders = ["Verhaeltnis", "Beurteilung", "Klinische Bedeutung"];
  const goodeWidths = [1500, 2500, 5360];
  const goodeRows = [
    ["< 0,55", "Unterprojiziert", "Nasenspitze liegt zu weit posterior; kann durch Tip-Augmentation korrigiert werden"],
    ["0,55\u20130,60", "Ideal", "Harmonisches Verhaeltnis von Nasenprojektion zu Nasenlaenge"],
    ["> 0,60", "Ueberprojiziert", "Nasenspitze liegt zu weit anterior; chirurgische Deprojektion oder kompensatorische Filler-Strategien"],
  ];
  content.push(p("Tabelle 6.7: Goode Ratio und Interpretation", { bold: true }));
  content.push(makeTable(goodeHeaders, goodeRows, goodeWidths));

  content.push(h3("6.4.3 Klinische Anwendung der Nasenprofilanalyse"));
  content.push(p("Die drei Nasenprofilparameter (NLA, NFW, Dorsumprofil) werden gemeinsam in der Zone Pf1 (Nasenprofil, vgl. Kapitel 9) ausgewertet. Der Severity-Score wird primaer durch die Messabweichung (Gewicht 0,7) bestimmt. Fuer die Behandlung mit dermalen Fillern (non-chirurgische Rhinoplastik) ist die genaue Kenntnis der vaskulaeren Anatomie essentiell (vgl. Kapitel 14, Abschnitt 14.1: Zone Pf1, A. dorsalis nasi und A. angularis)."));
  content.push(p("Typische Filler-Strategien nach Befund:", { bold: true }));
  content.push(p("\u2022 Dorsaler Hoecker: Camouflage durch Filler-Injektion cranial (im Nasion-Bereich) und caudal (Supratip-Region) des Hoeckers, um eine gerade Linie zu erzeugen. Produkt: HA Medium (Vollure, vgl. Kapitel 11), Linear-Threading-Technik, subdermal.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Satteldeformitaet: Direkte Augmentation auf dem Dorsum. CAVE: Extrem hohe vaskulaere Risiken in dieser Zone.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Spitzer Nasofrontalwinkel: Filler-Injektion im Nasion-/Radix-Bereich zur Vertiefung des Stirn-Nasen-Uebergangs.", { paragraphOpts: { indent: { left: 360 } } }));

  // 6.5 Cervicomental Angle
  content.push(h2("6.5 Cervicomental Angle (Kinn-Hals-Winkel)"));

  content.push(h3("6.5.1 Definition"));
  content.push(p("Der cervicomentale Winkel (CMA) beschreibt den Uebergang von Kinn zu Hals und ist ein zentraler Indikator fuer das jugendliche Profil. Er wird gebildet durch:"));
  content.push(p("\u2022 Linie 1: Vom Pogonion (Kinnspitze) zum Gnathion (unterster Kinnpunkt)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Linie 2: Vom Gnathion zum Halspunkt (approximiert als Punkt unterhalb und posterior des Gnathion)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Berechnung: angle_between_points(Gnathion, Pogonion, Neck_approximate)"));

  content.push(h3("6.5.2 Normwerte und Klassifikation"));
  const cmaHeaders = ["Winkelbereich", "Beurteilung", "Klinische Bedeutung"];
  const cmaWidths = [1800, 2500, 5060];
  const cmaRows = [
    ["< 105\u00b0", "Akuter CMA", "Sehr definierter Kinn-Hals-Uebergang; in der Regel kein Behandlungsbedarf"],
    ["105\u2013120\u00b0", "Ideal", "Gut definierter Kinn-Hals-Uebergang mit jugendlichem Erscheinungsbild"],
    ["120\u2013130\u00b0", "Leicht stumpf", "Beginnende Unschaerfe; moderate Behandlungsindikation"],
    ["> 130\u00b0", "Stumpf (is_obtuse = WAHR)", "Signifikante Laxizitaet; deutet auf submentales Fett, Platysma-Baender oder Kinnretrusion hin"],
  ];
  content.push(p("Tabelle 6.8: Normwerte des Cervicomental Angle", { bold: true }));
  content.push(makeTable(cmaHeaders, cmaRows, cmaWidths));

  content.push(p("Im System wird ein CMA > 130\u00b0 automatisch als \u201eis_obtuse\u201c markiert. Dieser Schwellenwert ist klinisch relevant, da er auf eine fortgeschrittene Laxizitaet hinweist, die moeglicherweise nicht allein durch Filler korrigierbar ist."));

  content.push(h3("6.5.3 Limitationen der Messung"));
  content.push(p("Die Cervicomental-Analyse unterliegt einer systemischen Limitation: MediaPipe FaceMesh stellt keine Landmarks im Halsbereich zur Verfuegung. Die Engine approximiert den Halspunkt als einen Punkt 40 Pixel inferior und 20 Pixel posterior des Gnathion. Diese Approximation liefert klinisch brauchbare Ergebnisse, aber eine hoehere Praezision waere nur mit spezieller Hals-Landmarkerkennung moeglich."));
  content.push(p("Das Analyseergebnis kann None zurueckgeben, wenn die Landmarks im Profil nicht ausreichend sichtbar sind. In diesem Fall wird eine Quality-Warning im Ergebnis vermerkt."));

  content.push(h3("6.5.4 Klinische Relevanz"));
  content.push(p("Der CMA ist der Primaerparameter fuer die Zone Pf3 (Chin-Neck Angle, vgl. Kapitel 9). Behandlungsoptionen nach Befund:"));
  content.push(p("\u2022 Stumpfer CMA durch Retrognathie: Kinnaugmentation mit HA Deep oder CaHA (Ch1, vgl. Kapitel 11) verschiebt das Pogonion nach anterior und verbessert den CMA sekundaer.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Stumpfer CMA durch submentales Fett: Filler-Behandlung allein unzureichend; Lipolyse (Deoxycholsaeure) oder chirurgische Liposuktion erwaegen.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Stumpfer CMA durch Platysma-Baender: Neurotoxin (Nefertiti-Lift) oder chirurgische Straffung.", { paragraphOpts: { indent: { left: 360 } } }));

  // 6.6 Chin Projection
  content.push(h2("6.6 Chin Projection (Kinnprojektion)"));

  content.push(h3("6.6.1 Messparameter"));
  content.push(p("Die Kinnanalyse umfasst drei Messparameter:"));

  content.push(p("A) Kinnprojektion (chin_projection_mm)", { bold: true }));
  content.push(p("Horizontaler Abstand des Pogonion von der Subnasale-Vertikalen. Berechnung:"));
  content.push(p("chin_proj_px = Pogonion.x - Subnasale.x"));
  content.push(p("chin_proj_mm = Kalibrierung.to_mm(chin_proj_px)"));
  content.push(p("Ein negativer Wert zeigt eine Retrognathie (Kinn hinter der Subnasale-Vertikalen) an, ein positiver Wert eine Prognathie (Kinn vor der Vertikalen)."));

  const chinHeaders = ["Wert (mm)", "Befund", "Klinische Bedeutung"];
  const chinWidths = [1800, 2500, 5060];
  const chinRows = [
    ["< -4 mm", "Ausgepraegt retrudiert", "Deutliche Retrognathie; chirurgische Kinnkorrektur (Genioplastik) oder starke Filler-Augmentation"],
    ["-4 bis 0 mm", "Leicht retrudiert", "Normale bis leichte Retrognathie; Filler-Augmentation (Ch1) haeufig ausreichend"],
    ["0 bis +2 mm", "Ideal", "Pogonion auf Hoehe oder leicht vor der Subnasale-Vertikalen"],
    ["> +4 mm", "Prominent/prognath", "Kinnprominenz; selten behandlungsbeduerftig, ausser bei Wunsch der Harmonisierung"],
  ];
  content.push(p("Tabelle 6.9: Kinnprojektion und Klassifikation", { bold: true }));
  content.push(makeTable(chinHeaders, chinRows, chinWidths));

  content.push(p("B) Mentolabiale Sulcus-Tiefe (mentolabial_depth_mm)", { bold: true }));
  content.push(p("Der Mentolabiale Sulcus ist die Vertiefung zwischen Unterlippe und Kinn. Die Tiefe wird als Perpendikularabstand des Mentolabial-Sulcus-Punktes von der Linie Labrale inferius\u2192Pogonion gemessen:"));
  content.push(p("mento_depth = |point_to_line_distance(Mentolabial, Labrale_inf, Pogonion)|"));
  content.push(p("Eine tiefe Mentolabiale Sulcus (> 4 mm) kann den Eindruck einer Kinnprominenz verstaerken. Sie kann mit HA-Filler aufgefuellt werden, um eine harmonischere Kinn-Lippen-Linie zu erzielen."));

  content.push(p("C) Kinnhoehe (chin_height_mm)", { bold: true }));
  content.push(p("Vertikaler Abstand vom Stomion (Mundspalt) zum Gnathion (unterster Kinnpunkt):"));
  content.push(p("chin_height_px = |Gnathion.y - Stomion.y|"));
  content.push(p("Die Kinnhoehe beeinflusst die Proportionen des unteren Gesichtsdrittels (vgl. Kapitel 5, Vertikale Drittel). Eine kurze Kinnhoehe bei gleichzeitiger Retrognathie verstaerkt den visuellen Effekt der Unterkieferretrudierung."));

  content.push(h3("6.6.2 Zusammenspiel der Profilparameter"));
  content.push(p("Die sechs Profilparameter stehen in engem klinischen Zusammenhang. Die folgende Tabelle zeigt die wichtigsten Interaktionen:"));

  const interHeaders = ["Befund-Kombination", "Interpretation", "Empfohlene Strategie"];
  const interWidths = [2800, 3000, 3560];
  const interRows = [
    ["Retrognathie + stumpfer CMA", "Kinndefizit als Primaerursache", "Kinnaugmentation (Ch1) als erster Schritt; CMA verbessert sich sekundaer"],
    ["Retrudierte Lippen + grosse Nase", "Pseudo-Retrusion durch prominente Nase", "Non-chirurgische Rhinoplastik (Pf1) kann Lippen-E-Linie-Verhaeltnis verbessern"],
    ["Dorsaler Hoecker + spitzer NLA", "Beides weist auf Nasendeformitaet hin", "Kombinierte Camouflage: Hoecker-Korrektur + Tip-Rotation"],
    ["Obtuser CMA + Jowling", "Kombination aus Kinn- und Kieferliniendefizit", "Jawline-Konturierung (Jl1) + Kinnaugmentation (Ch1)"],
    ["Steiner negativ + E-Linie ideal", "Moegliche Kinnretrusion", "Kinnprojektion evaluieren; Filler Ch1 kann Steiner-Linie normalisieren"],
  ];
  content.push(p("Tabelle 6.10: Zusammenspiel der Profilparameter", { bold: true }));
  content.push(makeTable(interHeaders, interRows, interWidths));

  content.push(h3("6.6.3 Klinische Priorisierung der Profilbehandlung"));
  content.push(p("Gemaess dem in Kapitel 13 beschriebenen Priorisierungssystem (STRUCTURAL_PRIORITY) werden Profilbehandlungen wie folgt eingeordnet:"));
  content.push(p("\u2022 Prioritaet 2: Pf3 (Chin-Neck Angle) \u2014 strukturelle Grundlage, fruehe Behandlung", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Prioritaet 3: Pf1 (Nasenprofil) \u2014 unabhaengig, kann parallel zu strukturellen Behandlungen", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Prioritaet 5: Pf2 (Lippenprojektion) \u2014 Verfeinerung nach struktureller Korrektur", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Die Kinnaugmentation (Ch1, Prioritaet 1) sollte vor der CMA-Optimierung erfolgen, da sie den CMA sekundaer verbessert. Die Lippenprofilkorrektur (Pf2) sollte zuletzt adressiert werden, da sich die E-Linie durch Nase- und Kinnveraenderungen verschiebt."));

  content.push(h2("6.7 Zusammenfassung der Profilmetriken"));
  content.push(p("Die folgende Gesamtuebersicht fasst alle Profilmetriken mit ihren Normwerten und klinischen Schwellenwerten zusammen:"));

  const summHeaders = ["Metrik", "Normbereich", "Alarm-Schwelle", "Primaerzone"];
  const summWidths = [2800, 2000, 2000, 2560];
  const summRows = [
    ["Oberlippe zur E-Linie", "-6,0 bis -1,0 mm", "> -1 mm / < -6 mm", "Pf2"],
    ["Unterlippe zur E-Linie", "-4,0 bis 0,0 mm", "> 0 mm / < -4 mm", "Pf2"],
    ["Nasolabialwinkel", "90\u2013105\u00b0", "< 90\u00b0 / > 105\u00b0", "Pf1"],
    ["Nasofrontalwinkel", "115\u2013135\u00b0", "< 115\u00b0 / > 135\u00b0", "Pf1"],
    ["Goode Ratio", "0,55\u20130,60", "< 0,55 / > 0,60", "Pf1"],
    ["Dorsumdeviation", "\u2248 0 mm", "> 0 mm (Hump) / < 0 (Sattel)", "Pf1"],
    ["Cervicomental Angle", "105\u2013120\u00b0", "> 130\u00b0 (obtuse)", "Pf3"],
    ["Kinnprojektion", "-4 bis 0 mm", "< -4 mm (Retrognathie)", "Ch1"],
    ["Steiner-Linie (OL)", "\u2248 0 mm", "Starke Deviation", "Pf2"],
    ["Mentolabiale Sulcus", "Variabel", "> 4 mm (tief)", "Ch1"],
  ];
  content.push(p("Tabelle 6.11: Gesamtuebersicht der Profilmetriken", { bold: true }));
  content.push(makeTable(summHeaders, summRows, summWidths));

  content.push(p("Querverweise:", { bold: true }));
  content.push(p("\u2022 Zonensystem: Kapitel 9 (Zonen Pf1, Pf2, Pf3, Ch1, Jl1)"));
  content.push(p("\u2022 Produktauswahl: Kapitel 11 (HA Deep fuer Ch1, HA Medium fuer Pf1, HA Soft fuer Pf2)"));
  content.push(p("\u2022 Sicherheit: Kapitel 14 (Vaskulaere Risikozonen Pf1, Lp1)"));
  content.push(p("\u2022 Multi-View Fusion: Kapitel 10 (Profilansicht als Primaerquelle fuer Ch1, Jl1, Pf1\u2013Pf3)"));

  return content;
}

// ─── Kapitel 14: Sicherheit und Kontraindikationen (FULL) ───

function kapitel14() {
  const content = [];
  content.push(h1("Kapitel 14: Sicherheit und Kontraindikationen"));
  content.push(p("Die Sicherheit des Patienten hat in der aesthetischen Medizin hoechste Prioritaet. Dieses Kapitel beschreibt das automatisierte Sicherheitssystem (Contraindication Checker) des Aesthetic Biometrics Engine, das als letzte Pruefinstanz vor der Behandlungsplanausgabe geschaltet ist. Das System fuehrt sechs unabhaengige Sicherheitschecks durch und gibt strukturierte Warnungen mit abgestuftem Schweregrad aus."));
  content.push(p("WICHTIG: Das automatisierte Sicherheitssystem ersetzt NICHT die klinische Beurteilung durch den behandelnden Arzt. Es stellt automatisierte Safety-Flags bereit, die vom Behandler geprueft und im klinischen Kontext bewertet werden muessen.", { bold: true }));

  content.push(h3("Schweregrade der Kontraindikationen"));
  content.push(p("Das System verwendet vier Schweregrade, absteigend nach Dringlichkeit:"));

  const sevHeaders = ["Schweregrad", "Code", "Bedeutung", "Handlungsanweisung"];
  const sevWidths = [1800, 1800, 2400, 3360];
  const sevRows = [
    ["CONTRAINDICATED", "Kontraindiziert", "Behandlung dieser Zone nicht durchfuehren", "Absolute Kontraindikation; keine Behandlung"],
    ["REFERRAL", "Ueberweisung", "Moegliche Pathologie; Facharztabklaerung", "Behandlung erst nach Ausschluss der Pathologie"],
    ["CAUTION", "Vorsicht", "Erhoehtes Risiko; erfahrener Injector erforderlich", "Behandlung moeglich, aber mit besonderen Vorsichtsmassnahmen"],
    ["WARNING", "Warnung", "Hinweis auf suboptimale Vorgehensweise", "Behandlungsplan ueberdenken und ggf. anpassen"],
  ];
  content.push(p("Tabelle 14.1: Schweregrade der Kontraindikationen", { bold: true }));
  content.push(makeTable(sevHeaders, sevRows, sevWidths));

  content.push(p("Die Ergebnisse werden nach Schweregrad sortiert ausgegeben: CONTRAINDICATED zuerst, dann REFERRAL, CAUTION und zuletzt WARNING."));

  // 14.1 Vaskulaere Risikozonen
  content.push(h2("14.1 Vaskulaere Risikozonen"));
  content.push(p("Vaskulaere Komplikationen (Gefaessverschluesse) sind die schwerwiegendsten Risiken bei Filler-Injektionen. Ein intraarterielle Injektion oder eine Kompression eines Gefaesses kann zu Hautnekrose, Gewebeverlust und im schlimmsten Fall zu Erblindung (bei retinaler Embolie ueber die A. ophthalmica) fuehren. Das System identifiziert acht Hochrisiko-Zonen mit den zugehoerigen Gefaessen:"));

  const vascHeaders = ["Zone", "Zone-Name", "Gefaehrdete Arterie(n)", "Risikoszenario"];
  const vascWidths = [700, 2000, 2600, 4060];
  const vascRows = [
    ["Tt1", "Tear Trough", "A. angularis, A. infraorbitalis", "Retinale Embolie bei Reflux in A. ophthalmica; Hautnekrose periorbital"],
    ["Ns1", "Nasolabial Fold", "A. facialis", "Nekrose der Nasolabialregion; selten retinale Beteiligung"],
    ["Pf1", "Nasal Profile", "A. dorsalis nasi, A. angularis", "HOECHSTES RISIKO: Retinale Embolie, Nasenspitzennekrose, Erblindung"],
    ["Lp1", "Upper Lip", "A. labialis superior", "Lippennekrose, Ulzeration, Narbenbildung"],
    ["Lp2", "Lower Lip", "A. labialis inferior", "Lippennekrose, Ulzeration, Narbenbildung"],
    ["Jl1", "Jawline", "A. facialis (Incisura mandibulae)", "Nekrose der Wangenregion; Ausbreitung nach cranial moeglich"],
    ["T1", "Temporal", "A. temporalis superficialis", "Temporale Hautnekrose; selten cerebrale Beteiligung"],
    ["Bw1", "Brow Lateral", "A. supraorbitalis", "Brauennekrose; Steckdose-Deformitaet bei Tiefenschaden"],
  ];
  content.push(p("Tabelle 14.2: Vaskulaere Risikozonen und zugehoerige Arterien", { bold: true }));
  content.push(makeTable(vascHeaders, vascRows, vascWidths));

  content.push(h3("14.1.1 Automatische Risikoerkennung"));
  content.push(p("Das System prueft fuer jede Zone, ob sie in der VASCULAR_RISK_ZONES-Datenbank als Hochrisiko-Zone gelistet ist (is_high_risk_zone). Wenn ja und wenn der Severity-Score der Zone den Schwellenwert von 5,0 ueberschreitet (HIGH_RISK_SEVERITY_THRESHOLD = 5,0), wird eine CAUTION-Warnung generiert:"));
  content.push(p("Logik: WENN is_high_risk_zone(zone_id) UND severity \u2265 5,0 DANN erzeuge CAUTION mit Angabe der betroffenen Gefaesse."));
  content.push(p("Der Schwellenwert von 5,0 stellt sicher, dass nur Zonen mit signifikantem Behandlungsbedarf flagged werden \u2014 bei niedrigem Severity waere die Behandlung ohnehin gering."));

  content.push(h3("14.1.2 Empfehlungen fuer Hochrisiko-Zonen"));
  content.push(p("Fuer alle als vaskulaer riskant identifizierten Zonen gibt das System folgende Standardempfehlungen:"));
  content.push(p("\u2022 Stumpfe Kanuele verwenden, wo technisch moeglich (insbesondere Tt1, Pf1, Ns1)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Vor jeder Injektion aspirieren (negative Aspiration schliesst intraarterielle Lage nicht sicher aus, reduziert aber das Risiko)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Hyaluronidase griffbereit halten (siehe Abschnitt 14.2)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Behandlung nur durch erfahrenen Injector mit Kenntnissen der Gefaessanatomie", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Langsame Injektion kleiner Volumina zur Minimierung des Embolierisikos", { paragraphOpts: { indent: { left: 360 } } }));

  content.push(h3("14.1.3 Zonenspezifische Sicherheitshinweise"));
  content.push(p("Zone Pf1 (Nasenprofil) \u2014 Hoechste Risikostufe", { bold: true }));
  content.push(p("Die non-chirurgische Rhinoplastik ist der haeufigste Ausloeser fuer vaskulaere Komplikationen in der aesthetischen Medizin. Die A. dorsalis nasi verlaeuft oberflaeglich auf dem Nasenruecken und kann bereits durch geringe Filler-Mengen komprimiert oder embolisiert werden. Die Produktdatenbank (Kapitel 11) gibt fuer Pf1 explizit folgende Safety Notes aus:"));
  content.push(p("\u2022 \u201eHIGH-RISK ZONE: Dorsal nasal artery \u2014 inject slowly, use blunt cannula\u201c", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 \u201eRisk of skin necrosis and visual impairment with vascular compromise\u201c", { paragraphOpts: { indent: { left: 360 } } }));

  content.push(p("Zone Tt1 (Tear Trough) \u2014 Hohe Risikostufe", { bold: true }));
  content.push(p("Die A. angularis und die A. infraorbitalis verlaufen im Bereich des Traenentals. Die duenne Haut und die Naehe zur Orbita erhoehen das Komplikationsrisiko. Aus der Produktdatenbank:"));
  content.push(p("\u2022 \u201eHIGH-RISK ZONE: Angular artery \u2014 use blunt cannula preferred\u201c", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 \u201eStart conservatively (0.1ml per side), reassess at 2 weeks\u201c", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 \u201eRisk of Tyndall effect with superficial placement\u201c", { paragraphOpts: { indent: { left: 360 } } }));

  // 14.2 Notfallmanagement
  content.push(h2("14.2 Notfallmanagement: Hyaluronidase-Protokoll"));
  content.push(p("Bei Verdacht auf einen Gefaessverschluss durch HA-Filler ist die sofortige Applikation von Hyaluronidase die wichtigste Notfallmassnahme. Die folgenden Protokollschritte sollten in jeder Praxis, die Filler-Injektionen durchfuehrt, als Standard Operating Procedure (SOP) vorliegen:"));

  content.push(h3("14.2.1 Sofortmassnahmen bei Gefaessverschluss"));
  content.push(p("Warnzeichen erkennen:", { bold: true }));
  content.push(p("\u2022 Akute Weissfaerbung (Blanching) der Haut im Injektionsgebiet", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Livide Verfaerbung (reticulaere Livedo) \u2014 netzfoermige blau-violette Zeichnung", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Uebermaessiger Schmerz (disproportional zur Injektionsmenge)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Visusstorungen (Sehverlust, Gesichtsfeldausfall) \u2014 SOFORTIGE Notfallmassnahme!", { paragraphOpts: { indent: { left: 360 } } }));

  content.push(p("Protokoll:", { bold: true }));
  content.push(p("1. Injektion SOFORT stoppen.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("2. Hyaluronidase vorbereiten: 150\u2013300 IE (je nach Schwere) in NaCl 0,9 % aufloesen.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("3. Flaechendeckende Infiltration der gesamten betroffenen Region mit Hyaluronidase (nicht punktuell!).", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("4. Warme Kompressen auf die betroffene Region (Vasodilatation).", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("5. Nitroglycerin-Paste 2 % topisch auf das betroffene Areal (zusaetzliche Vasodilatation).", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("6. Bei Visusstoerungen: Sofortige Einweisung in eine ophthalmologische Notfalleinheit; retrobulbaere Hyaluronidase-Injektion kann erwaegt werden (Evidenzlage begrenzt).", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("7. Dokumentation: Zeitpunkt des Ereignisses, injiziertes Produkt, Menge, Lokalisation, Hyaluronidase-Dosis und klinischer Verlauf.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("8. Nachkontrolle nach 30\u201360 Minuten; bei ausbleibender Besserung erneute Hyaluronidase-Gabe.", { paragraphOpts: { indent: { left: 360 } } }));

  content.push(h3("14.2.2 Limitationen bei Nicht-HA-Fillern"));
  content.push(p("Hyaluronidase loest ausschliesslich Hyalurons\u00e4ure-basierte Filler auf. Bei Komplikationen mit CaHA (Radiesse) oder PLLA (Sculptra) steht kein spezifisches Antidot zur Verfuegung. Dies unterstreicht die Notwendigkeit besonderer Vorsicht bei der Anwendung von Nicht-HA-Fillern in vaskulaeren Risikozonen. Die Produktdatenbank (Kapitel 11) schliesst daher Nicht-HA-Produkte fuer bestimmte Hochrisiko-Zonen (insbesondere Pf1, Tt1) aus."));

  // 14.3 Extreme Asymmetrie
  content.push(h2("14.3 Extreme Asymmetrie als Pathologie-Indikator"));
  content.push(p("Eine Asymmetrie des Gesichts ist bis zu einem gewissen Grad physiologisch. Die bilaterale Symmetrieanalyse (vgl. Kapitel 4) erfasst Abweichungen systematisch. Wenn jedoch eine Zone sowohl einen hohen Severity-Score als auch ausgepragte Asymmetrie-Befunde aufweist, kann dies auf eine zugrunde liegende Pathologie hindeuten."));

  content.push(h3("14.3.1 Schwellenwert und Logik"));
  content.push(p("Der Schwellenwert fuer die Extreme-Asymmetrie-Warnung liegt bei:", { bold: true }));
  content.push(p("EXTREME_ASYMMETRY_THRESHOLD = 8,0 (Severity-Score)", { bold: true }));
  content.push(p("Logik: WENN severity \u2265 8,0 UND findings enthaelt \u201easymmetry\u201c DANN erzeuge REFERRAL-Warnung."));
  content.push(p("Das System prueft nicht nur den Severity-Score, sondern validiert zusaetzlich, ob die Befunde der Zone tatsaechlich Asymmetrie-bezogene Beschreibungen enthalten. Ein hoher Severity-Score allein (z.\u202fB. durch extremen Volumenverlust) loest diese Warnung nicht aus."));

  content.push(h3("14.3.2 Moegliche Pathologien"));
  content.push(p("Bei einer extremen Asymmetrie-Warnung sollten folgende Differentialdiagnosen abgeklaert werden:"));
  content.push(p("\u2022 Fazialisparese (periphere oder zentrale Laesion des N. facialis)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Skelettale Asymmetrie (kondylaere Hyperplasie, Hemimandibularis-Elongation)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Vorangegangenes Trauma (Kieferfrakturen, Jochbeinfrakturen)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Tumore (Parotistumoren, Weichteiltumoren)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Hemifaziale Atrophie (Parry-Romberg-Syndrom)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Iatroge Asymmetrie durch fruehere Behandlungen", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Empfehlung des Systems: \u201eConsider specialist referral before aesthetic treatment. Rule out pathological causes of asymmetry.\u201c", { italics: true }));

  // 14.4 Glabella-Forehead-Abhaengigkeit
  content.push(h2("14.4 Glabella-Forehead-Abhaengigkeit (Ptosis-Risiko)"));
  content.push(p("Eine der haeufigsten Komplikationen der Neurotoxin-Behandlung ist die Brauenptosis (Herabhgaengen der Braue). Sie entsteht, wenn der M. frontalis (Stirnmuskel) durch Botulinumtoxin gelaehmt wird, ohne dass gleichzeitig die Glabella-Muskulatur (M. corrugator supercilii, M. procerus) behandelt wird."));

  content.push(h3("14.4.1 Mechanismus"));
  content.push(p("Der M. frontalis ist der einzige Brauenheber. Die Glabella-Muskeln (Corrugator, Procerus) sind Brauensenker. Im physiologischen Gleichgewicht halten sich Heber und Senker die Waage. Wird nur der Heber (Frontalis) durch Neurotoxin gelaehmt, ueberwiegen die Senker und die Braue sinkt ab \u2014 insbesondere lateral, wo der Frontalis den groessten Hebeeffekt hat."));

  content.push(h3("14.4.2 Schwellenwert und Logik"));
  content.push(p("Das System prueft folgende Bedingung:", { bold: true }));
  content.push(p("WENN Zone Fo1 (Stirn) severity \u2265 3,0 UND Zone Bw2 (Glabella) severity < 1,0 DANN erzeuge WARNING."));
  content.push(p("Der Schwellenwert fo1.severity \u2265 3,0 stellt sicher, dass die Stirn einen moderaten Behandlungsbedarf aufweist (vgl. Kapitel 9, Severity-Interpretation). Der niedrige Schwellenwert fuer Bw2 (< 1,0) bedeutet, dass die Glabella praktisch keinen eigenen Behandlungsbedarf zeigt \u2014 sie wuerde also im Behandlungsplan nicht enthalten sein, was zum Ptosis-Risiko fuehrt."));

  content.push(h3("14.4.3 Empfehlung des Systems"));
  content.push(p("Bei Ausloesung dieser Warnung gibt das System folgende Empfehlung aus:"));
  content.push(p("\u201eAlways include glabella treatment when treating forehead. Consider lower forehead doses if brow position is already low.\u201c", { italics: true }));
  content.push(p("Konkret bedeutet dies:"));
  content.push(p("\u2022 Bei Stirnbehandlung (Fo1) IMMER auch Glabella (Bw2) mitbehandeln", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Neurotoxin-Dosierung nach Zone (vgl. Kapitel 11, Tabelle 11.2):", { paragraphOpts: { indent: { left: 360 } } }));

  const ptosisHeaders = ["Zone", "Muskel", "Dosis (Botox-Aequivalent)", "Sicherheitshinweis"];
  const ptosisWidths = [800, 2200, 2200, 4160];
  const ptosisRows = [
    ["Bw2", "M. corrugator supercilii", "10\u201325 Units", "Ptosis-Risiko bei zu tiefer Injektion"],
    ["Bw2", "M. procerus", "5\u201310 Units", "Zentrale Injektion auf Processus nasalis"],
    ["Fo1", "M. frontalis", "10\u201330 Units", "IMMER Glabella mitbehandeln; niedrigere Dosen bei tiefer Brauenposition"],
  ];
  content.push(p("Tabelle 14.3: Neurotoxin-Dosierung bei kombinierter Stirn-Glabella-Behandlung", { bold: true }));
  content.push(makeTable(ptosisHeaders, ptosisRows, ptosisWidths));

  content.push(p("Die Neurotoxin-Indikationen sind in der Produktdatenbank (NEUROTOXIN_INDICATIONS) hinterlegt und umfassen neben Bw2 und Fo1 auch die Lip-Flip-Indikation (Lp1, M. orbicularis oris, 2\u20136 Units) \u2014 vgl. Kapitel 11 fuer Details."));

  // 14.5 Tear Trough Spezialbehandlung
  content.push(h2("14.5 Tear Trough Spezialbehandlung"));
  content.push(p("Die Zone Tt1 (Tear Trough) ist sowohl technisch als auch anatomisch eine der anspruchsvollsten Behandlungsregionen. Das System fuehrt daher einen dedizierten Sicherheitscheck durch, der ueber den allgemeinen vaskulaeren Risikocheck hinausgeht."));

  content.push(h3("14.5.1 Tyndall-Effekt"));
  content.push(p("Der Tyndall-Effekt ist eine blaugraue Verfaerbung der Haut, die entsteht, wenn HA-Filler zu oberflaechlich platziert wird. Durch die extrem duenne Haut im Traenentalbereich ist das Risiko hier besonders hoch. Die Verfaerbung kann Monate bis Jahre persistieren und erfordert eine Aufloesung mit Hyaluronidase."));
  content.push(p("Das System empfiehlt daher fuer Tt1 ausschliesslich HA Soft (Volbella, G\u2019 98 Pa) in subdermaler Tiefe mit Mikrodroplet- oder Linear-Threading-Technik (vgl. Kapitel 11, Zone Tt1)."));

  content.push(h3("14.5.2 Konservativer Ansatz und Midface-First-Strategie"));
  content.push(p("Schwellenwert:", { bold: true }));
  content.push(p("WENN Tt1 severity \u2265 6,0 DANN erzeuge CAUTION (Code: TEAR_TROUGH_DEEP).", { bold: true }));
  content.push(p("Ein Severity-Score \u2265 6,0 deutet auf eine tiefe Traenentaldeformitaet hin. In diesem Fall gibt das System folgende Empfehlung:"));
  content.push(p("\u201eConsider addressing midface volume (Ck2/Ck3) first \u2014 this often reduces tear trough depth significantly. If direct treatment needed, use blunt cannula and conservative volumes (max 0.1-0.2ml per side per session).\u201c", { italics: true }));

  content.push(p("Die Midface-First-Strategie basiert auf dem anatomischen Zusammenhang: Ein Volumenverlust im Mittelgesicht (Ck2: Wangenhoehe, Ck3: Mittelwange) fuehrt zu einem Absinken des Weichgewebes, das die Traenentaltiefe sekundaer verstaerkt. In vielen Faellen reduziert eine Volumenauffuellung in Ck2/Ck3 die Traenentaltiefe um 30\u201350 %, sodass eine direkte Tt1-Behandlung entweder gar nicht mehr oder nur mit minimalen Volumina noetig ist."));

  content.push(h3("14.5.3 Volumen- und Technikempfehlungen fuer Tt1"));
  content.push(p("Gemaess der Produktdatenbank (ZONE_RECOMMENDATIONS) gilt fuer Zone Tt1:"));
  content.push(p("\u2022 Produkt: Juvederm Volbella (HA Soft, G\u2019 98 Pa)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Technik: Mikrodroplet oder Linear Threading", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Tiefe: Subdermal", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Volumen: 0,1\u20130,3 ml pro Seite (MAXIMAL)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Kontrolle: Wiedervorstellung nach 2 Wochen zur Beurteilung des Ergebnisses", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Die strikte Mengenbegrenzung ist essenziell: Ueberkorrektur im Traenentalbereich fuehrt zu Schwellungen, lymphatischer Obstruktion und einem unnatuerlichen Erscheinungsbild, das schwer zu korrigieren ist."));

  // 14.6 Ueberbehandlungsrisiko
  content.push(h2("14.6 Ueberbehandlungsrisiko (Overtreatment Risk)"));
  content.push(p("Wenn der Behandlungsplan zu viele Zonen gleichzeitig adressiert, steigt das Risiko eines unnatuerlichen Gesamterscheinungsbilds (\u201eOverfilled Look\u201c). Das System ueberwacht die Summe aller Severity-Scores als Globalindikator."));

  content.push(h3("14.6.1 Schwellenwert und Logik"));
  content.push(p("EXCESSIVE_TOTAL_SEVERITY = 60,0", { bold: true }));
  content.push(p("Berechnung: Total Severity = Summe(severity aller Zonen)"));
  content.push(p("WENN Total Severity > 60 DANN erzeuge WARNING (Code: OVERTREATMENT_RISK)."));
  content.push(p("Die Anzahl der behandlungsbeduerftigen Zonen (severity \u2265 1,0) wird zusaetzlich im Warntext angegeben, um dem Behandler einen Ueberblick zu geben."));

  content.push(h3("14.6.2 Empfehlung bei Ueberbehandlungsrisiko"));
  content.push(p("Bei Ausloesung dieser Warnung empfiehlt das System:"));
  content.push(p("\u201ePrioritize structural zones in session 1. Reassess after initial treatment before addressing additional zones. Consider a staged approach over 3-4 sessions.\u201c", { italics: true }));
  content.push(p("Konkret bedeutet dies eine Behandlung in Phasen gemaess dem Priorisierungssystem (STRUCTURAL_PRIORITY, vgl. Kapitel 13):"));

  const phasHeaders = ["Phase", "Prioritaet", "Zonen (Beispiele)", "Zeitpunkt"];
  const phasWidths = [1200, 1800, 3600, 2760];
  const phasRows = [
    ["Phase 1", "Strukturelle Basis (P1)", "Ck1, Ck2, Ch1 (Skelettale Grundlage)", "Sitzung 1"],
    ["Phase 2", "Strukturelle Kontur (P2)", "Jl1, Jw1, Pf3 (Kieferkontur, Kinn-Hals)", "Sitzung 2 (nach 4\u20136 Wochen)"],
    ["Phase 3", "Volumen (P3)", "T1, Ck3, Tt1, Pf1 (Volumendefizite)", "Sitzung 3 (nach 4\u20136 Wochen)"],
    ["Phase 4", "Verfeinerung (P4\u20135)", "Ns1, Mn1, Lp1, Lp2, Fo1, Bw2", "Sitzung 4 (nach 4\u20136 Wochen)"],
  ];
  content.push(p("Tabelle 14.4: Empfohlene Behandlungsphasen bei hoher Gesamt-Severity", { bold: true }));
  content.push(makeTable(phasHeaders, phasRows, phasWidths));

  content.push(p("Vorteile des gestaffelten Ansatzes:", { bold: true }));
  content.push(p("\u2022 Reduziertes Risiko: Weniger Filler-Volumen pro Sitzung bedeutet weniger vaskulaere Komplikationsgefahr", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Sekundaereffekte nutzen: Strukturelle Behandlungen (Ck2, Ch1) verbessern sekundaer auch umliegende Zonen (Ns1, Tt1, CMA)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Natuerliches Ergebnis: Der Patient und die Umgebung gewoehnen sich graduell an die Veraenderungen", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Korrekturmoeglichkeit: Zwischen den Sitzungen kann das Ergebnis evaluiert und der Plan angepasst werden", { paragraphOpts: { indent: { left: 360 } } }));

  // 14.7 Pathologische Severity
  content.push(h2("14.7 Pathologische Severity (Chirurgische Indikation)"));
  content.push(p("Wenn einzelne Zonen extrem hohe Severity-Scores aufweisen, kann dies auf Deformitaeten hindeuten, die ueber den Bereich der aesthetischen Medizin hinausgehen und eine chirurgische Intervention erfordern."));

  content.push(h3("14.7.1 Schwellenwert"));
  content.push(p("PATHOLOGY_SEVERITY_THRESHOLD = 9,0", { bold: true }));
  content.push(p("WENN severity \u2265 9,0 DANN erzeuge CAUTION (Code: HIGH_SEVERITY)."));
  content.push(p("Ein Severity-Score von 9 oder hoeher bedeutet, dass die Messwerte extrem stark von den Normwerten abweichen. In solchen Faellen ist es wahrscheinlich, dass eine rein aesthetische Filler- oder Neurotoxin-Behandlung kein befriedigendes Ergebnis liefern kann."));

  content.push(h3("14.7.2 Empfehlung des Systems"));
  content.push(p("\u201eVerify measurements manually. Consider whether aesthetic treatment alone is appropriate or if surgical/orthodontic intervention is indicated.\u201c", { italics: true }));
  content.push(p("Beispiele fuer chirurgische Indikationen bei hoher Severity:"));

  const surgHeaders = ["Zone", "Severity \u2265 9", "Moegliche chirurgische Indikation"];
  const surgWidths = [800, 3000, 5560];
  const surgRows = [
    ["Ch1", "Extreme Kinnretrusion/-protrusion", "Genioplastik (Gleitostectomie), Kinnimplantat, orthognathe Chirurgie"],
    ["Jl1", "Extreme Kieferasymmetrie/-deformitaet", "Orthognathe Chirurgie, Mandibularresektion"],
    ["Pf1", "Extreme Nasendeformitaet", "Chirurgische Rhinoplastik (funktionell/aesthetisch)"],
    ["Pf3", "Extrem stumpfer CMA", "Submentale Liposuktion, Platysma-Straffung, Facelift"],
    ["Tt1", "Extreme Traenentaldeformitaet", "Blepharoplastik (untere Lidstraffung), Midface-Lift"],
    ["Bw1", "Extreme Brauenptosis", "Brauenanhebung (Browlift), Blepharoplastik"],
    ["Ns1", "Extreme Nasolabialfalte", "Facelift, SMAS-Plication"],
  ];
  content.push(p("Tabelle 14.5: Chirurgische Indikationen bei pathologischer Severity", { bold: true }));
  content.push(makeTable(surgHeaders, surgRows, surgWidths));

  content.push(p("Wichtig: Das System verweist in diesem Fall NICHT auf eine Kontraindikation der aesthetischen Behandlung, sondern empfiehlt lediglich eine manuelle Verifizierung und die Pruefung, ob eine chirurgische Alternative besser geeignet waere. Der Behandler trifft die endgueltige Entscheidung."));

  // 14.8 Zusammenfassung
  content.push(h2("14.8 Zusammenfassung der Sicherheitschecks"));
  content.push(p("Die folgende Tabelle fasst alle sechs automatisierten Sicherheitschecks zusammen:"));

  const checkHeaders = ["Nr.", "Check", "Schwellenwert", "Schweregrad", "Code"];
  const checkWidths = [500, 2600, 2800, 1700, 2760];
  const checkRows = [
    ["1", "Extreme Asymmetrie", "severity \u2265 8,0 + Asymmetrie-Befund", "REFERRAL", "EXTREME_ASYMMETRY"],
    ["2", "Pathologische Severity", "severity \u2265 9,0", "CAUTION", "HIGH_SEVERITY"],
    ["3", "Vaskulaeres Risiko", "Hochrisiko-Zone + severity \u2265 5,0", "CAUTION", "VASCULAR_RISK"],
    ["4", "Tear Trough Spezial", "Tt1 severity \u2265 6,0", "CAUTION", "TEAR_TROUGH_DEEP"],
    ["5", "Ueberbehandlungsrisiko", "Total Severity > 60", "WARNING", "OVERTREATMENT_RISK"],
    ["6", "Stirn ohne Glabella", "Fo1 \u2265 3,0 + Bw2 < 1,0", "WARNING", "FOREHEAD_WITHOUT_GLABELLA"],
  ];
  content.push(p("Tabelle 14.6: Uebersicht der automatisierten Sicherheitschecks", { bold: true }));
  content.push(makeTable(checkHeaders, checkRows, checkWidths));

  content.push(p("Verarbeitungsreihenfolge: Alle sechs Checks werden parallel auf die Zonenergebnisse angewendet. Die resultierenden Kontraindikationen werden anschliessend nach Schweregrad sortiert (CONTRAINDICATED > REFERRAL > CAUTION > WARNING) und dem Behandlungsplan vorangestellt."));

  content.push(p("Querverweise:", { bold: true }));
  content.push(p("\u2022 Zonensystem: Kapitel 9 (Definition aller 19 Zonen mit Referenzwerten und Severity-Gewichten)"));
  content.push(p("\u2022 Produkte: Kapitel 11 (Produktauswahl, vaskulaere Sicherheitshinweise pro Zone)"));
  content.push(p("\u2022 Priorisierung: Kapitel 13 (STRUCTURAL_PRIORITY fuer gestaffelten Behandlungsansatz)"));
  content.push(p("\u2022 Profilanalyse: Kapitel 6 (Normwerte fuer E-Linie, NLA, CMA, die in Severity-Berechnung einfliessen)"));
  content.push(p("\u2022 Symmetrieanalyse: Kapitel 4 (Bilaterale Symmetriemessung als Grundlage fuer Asymmetrie-Check)"));

  content.push(h2("14.9 Klinisches Fallbeispiel: Zusammenspiel der Sicherheitschecks"));
  content.push(p("Szenario: Eine 62-jaehrige Patientin zeigt folgende Zonenanalyse:", { bold: true }));
  content.push(p("\u2022 Ck2 (Wangenhoehe): severity 7,2 \u2014 deutlicher Volumenverlust", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Tt1 (Traenental): severity 6,8 \u2014 tiefe Traenentaldeformitaet", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Ns1 (Nasolabial): severity 5,5 \u2014 maessige Nasolabialfalte", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Fo1 (Stirn): severity 4,2 \u2014 moderater Behandlungsbedarf", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Bw2 (Glabella): severity 0,5 \u2014 kaum Befund", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 12 weitere Zonen mit diversen Severity-Scores, Total Severity = 64,3", { paragraphOpts: { indent: { left: 360 } } }));

  content.push(p("Ausgeloeste Sicherheitschecks:", { bold: true }));
  content.push(p("1. CAUTION (VASCULAR_RISK): Tt1 ist Hochrisiko-Zone + severity 6,8 > 5,0 \u2192 Warnung mit Angabe A. angularis, A. infraorbitalis"));
  content.push(p("2. CAUTION (VASCULAR_RISK): Ns1 ist Hochrisiko-Zone + severity 5,5 > 5,0 \u2192 Warnung mit Angabe A. facialis"));
  content.push(p("3. CAUTION (TEAR_TROUGH_DEEP): Tt1 severity 6,8 \u2265 6,0 \u2192 Midface-First-Empfehlung"));
  content.push(p("4. WARNING (FOREHEAD_WITHOUT_GLABELLA): Fo1 severity 4,2 \u2265 3,0 und Bw2 severity 0,5 < 1,0 \u2192 Ptosis-Warnung"));
  content.push(p("5. WARNING (OVERTREATMENT_RISK): Total Severity 64,3 > 60 \u2192 Empfehlung zur gestaffelten Behandlung"));

  content.push(p("Empfohlene Vorgehensweise:", { bold: true }));
  content.push(p("Sitzung 1: Ck2 (Midface-Volumen) \u2014 verbessert sekundaer Tt1 und Ns1. Bw2 mit niedrig dosiertem Neurotoxin einschliessen, um die Voraussetzung fuer Fo1 zu schaffen."));
  content.push(p("Sitzung 2 (nach 4\u20136 Wochen): Reevaluation. Falls Tt1 verbessert: direkte Tt1-Behandlung moeglicherweise nicht mehr noetig. Fo1 + Bw2 Neurotoxin."));
  content.push(p("Sitzung 3: Restliche Zonen nach Priorisierung."));

  return content;
}

// ─── Kapitel 4: Symmetrieanalyse (FULL) ───

function kapitel4() {
  const content = [];
  content.push(h1("Kapitel 4: Symmetrieanalyse"));
  content.push(p("Die bilaterale Gesichtssymmetrie ist einer der fundamentalsten Parameter der aesthetischen Gesichtsanalyse. Kein menschliches Gesicht ist perfekt symmetrisch \u2014 physiologische Asymmetrien von 2\u20133 % gelten als normal und tragen zur individuellen Attraktivitaet bei. Klinisch relevant werden Asymmetrien erst ab definierten Schwellenwerten, die auf die Wahrnehmungsforschung und klinische Erfahrungswerte zurueckgehen."));
  content.push(p("Die Symmetrieanalyse des Aesthetic Biometrics Engine misst die bilaterale Symmetrie entlang sechs anatomischer Achsen und ergaenzt diese durch eine dynamische Asymmetrieanalyse auf Basis von Blendshape-Koeffizienten. Alle Messungen werden in kalibrierten Millimetern (via Iris-Kalibrierung, vgl. Kapitel 3) durchgefuehrt, um klinisch verwertbare Aussagen zu ermoeglichen."));

  // 4.1
  content.push(h2("4.1 Median-Sagittallinie und Symmetrieachsen"));
  content.push(p("Die Median-Sagittallinie ist die vertikale Referenzlinie, die das Gesicht in eine rechte und linke Haelfte teilt. Sie verlaeuft durch die Midline-Landmarks: Trichion (Haaransatz-Approximation, Landmark 10), Glabella (Landmark 9), Pronasale (Nasenspitze, Landmark 4), Subnasale (Landmark 2), Stomion (Mundspalte, Landmark 13) und Gnathion (Kinnpunkt, Landmark 152)."));
  content.push(p("Gegen diese Referenzlinie werden sechs Symmetrieachsen gemessen, die jeweils bilateral gepaarte Strukturen vergleichen:"));

  const axHeaders = ["Nr.", "Achse", "Linker Landmark", "Rechter Landmark", "Referenz", "Beschreibung"];
  const axWidths = [400, 1600, 1600, 1600, 1400, 2760];
  const axRows = [
    ["1", "brow_height", "282 (Brauenpeak L)", "52 (Brauenpeak R)", "Glabella (9)", "Brauenhoehe relativ zur Glabella"],
    ["2", "eye_width", "263/466 (Augeninnen/aussen L)", "33/246 (Augeninnen/aussen R)", "\u2014", "Lidspaltenbreite (Fissura palpebralis)"],
    ["3", "cheekbone_height", "330 (Jochbein L)", "101 (Jochbein R)", "Pronasale (4)", "Jochbeinhoehe relativ zur Nasenspitze"],
    ["4", "nasolabial_region", "Alar/Mundwinkel L", "Alar/Mundwinkel R", "\u2014", "Alar-Mundwinkel-Distanz (Nasolabialregion)"],
    ["5", "mouth_corner_height", "291 (Mundwinkel L)", "61 (Mundwinkel R)", "Stomion (13)", "Vertikale Mundwinkelposition"],
    ["6", "gonion_height", "Gonion L", "Gonion R", "Gnathion (152)", "Kieferwinkelhoehe relativ zum Kinn"],
  ];
  content.push(p("Tabelle 4.1: Die sechs Symmetrieachsen", { bold: true }));
  content.push(makeTable(axHeaders, axRows, axWidths));

  content.push(p("Fuer jede Achse werden zwei Messtypen verwendet:"));
  content.push(p("\u2022 Hoehenbasierte Messung: Vertikale Distanz eines bilateralen Landmarks zum Midline-Referenzpunkt (Achsen 1, 3, 5, 6). Berechnung: |y_Landmark \u2212 y_Referenz| in Pixel, konvertiert ueber Kalibrierung zu mm.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Distanzbasierte Messung: Euklidische 2D-Distanz zwischen zwei Landmarks einer Seite (Achsen 2, 4). Berechnung: \u221a((x\u2082\u2212x\u2081)\u00b2 + (y\u2082\u2212y\u2081)\u00b2) in Pixel, konvertiert zu mm.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Die Differenz wird sowohl absolut (in mm) als auch relativ (in Prozent des Mittelwerts beider Seiten) angegeben: diff_pct = (diff_mm / avg_mm) \u00d7 100."));

  // 4.2
  content.push(h2("4.2 Bilaterale Symmetrie: klinische Schwellenwerte"));
  content.push(p("Die klinische Signifikanz einer Asymmetrie wird durch zwei unabhaengige Schwellenwerte definiert:"));

  const thHeaders = ["Parameter", "Schwellenwert", "Bedeutung"];
  const thWidths = [3200, 2300, 3860];
  const thRows = [
    ["SIGNIFICANCE_THRESHOLD_MM", "> 2,0 mm", "Absolute Differenz, die vom menschlichen Auge als Asymmetrie wahrgenommen wird"],
    ["SIGNIFICANCE_THRESHOLD_PCT", "> 8,0 %", "Relative Differenz bezogen auf den Mittelwert beider Seiten"],
  ];
  content.push(p("Tabelle 4.2: Schwellenwerte fuer klinische Signifikanz", { bold: true }));
  content.push(makeTable(thHeaders, thRows, thWidths));

  content.push(p("Eine Messung wird als klinisch signifikant markiert (is_clinically_significant = true), wenn EINER der beiden Schwellenwerte ueberschritten wird. Dieses ODER-Kriterium stellt sicher, dass sowohl kleine Gesichter (wo 2 mm relativ viel sind) als auch grosse Gesichter (wo 8 % absolut mehr als 2 mm sein koennen) korrekt erfasst werden."));
  content.push(p("Klinische Einordnung der Asymmetrie:", { bold: true }));
  content.push(p("\u2022 < 3 % Differenz: Physiologische Asymmetrie \u2014 keine Behandlungsindikation", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 3\u20135 % Differenz: Subklinische Asymmetrie \u2014 bei Patientenwunsch behandelbar", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 5\u20138 % Differenz: Moderate Asymmetrie \u2014 behandlungsrelevant", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 > 8 % Differenz: Ausgepraegt \u2014 Abklaerung zugrunde liegender Pathologien empfohlen (vgl. Kapitel 14, Extreme Asymmetrie)", { paragraphOpts: { indent: { left: 360 } } }));

  content.push(h3("4.2.1 Globaler Symmetrie-Index"));
  content.push(p("Der globale Symmetrie-Index fasst alle sechs Achsen zu einem Score von 0 bis 100 zusammen (100 = perfekte Symmetrie). Die Berechnung erfolgt gewichtet, da nicht alle Achsen die gleiche klinische Bedeutung haben:"));

  const wHeaders = ["Achse", "Gewicht", "Begruendung"];
  const wWidths = [2800, 1000, 5560];
  const wRows = [
    ["brow_height", "1,0", "Baseline-Gewicht; moderate visuelle Auswirkung"],
    ["eye_width", "1,2", "Hoeher gewichtet: Augenregion ist zentraler Blickfang"],
    ["cheekbone_height", "1,3", "Hoechste Gewichtung: Mittelgesichtssymmetrie dominiert den Gesamteindruck"],
    ["nasolabial_region", "1,1", "Nasolabial-Asymmetrie faellt auf, besonders beim Laecheln"],
    ["mouth_corner_height", "1,0", "Baseline; Mundwinkel-Downturn separat in Zone Lp3 erfasst"],
    ["gonion_height", "0,8", "Niedrigste Gewichtung: Kieferkontur weniger sichtbar als Mittelgesicht"],
  ];
  content.push(p("Tabelle 4.3: Achsengewichte fuer den globalen Symmetrie-Index", { bold: true }));
  content.push(makeTable(wHeaders, wRows, wWidths));

  content.push(p("Berechnung: Fuer jede Achse wird die prozentuale Abweichung auf einen Maximalwert von 15 % normalisiert (Abweichungen > 15 % erhalten die maximale Bestrafung). Der gewichtete Durchschnitt aller normalisierten Abweichungen wird von 1,0 subtrahiert und mit 100 multipliziert:"));
  content.push(p("Symmetrie-Index = max(0, (1 \u2212 gewichteter_Durchschnitt) \u00d7 100)", { bold: true }));
  content.push(p("Interpretation: Ein Score von 95\u2013100 zeigt exzellente Symmetrie. Werte zwischen 85 und 94 sind im Normalbereich. Unter 85 sollte eine gezielte Analyse der betroffenen Achsen erfolgen. Werte unter 70 deuten auf pathologische Asymmetrien hin (vgl. Kapitel 14.3)."));

  content.push(h3("4.2.2 Pro-Zone Asymmetrie-Scores"));
  content.push(p("Neben dem globalen Index liefert das System zonenspezifische Asymmetrie-Scores. Jede der 19 Behandlungszonen (vgl. Kapitel 9) erhaelt einen eigenen Severity-Beitrag durch die Asymmetrie der zugehoerigen Achse. Beispiele:"));
  content.push(p("\u2022 Zone Bw1 (Laterale Braue): Asymmetrie ueber die brow_height-Achse → Severity-Gewicht 0,4", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Zonen Ck1/Ck2/Ck3 (Wangenregion): Asymmetrie ueber die cheekbone_height-Achse → Severity-Gewicht 0,2\u20130,3", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Zone T1 (Temporal): Asymmetrie der Temporaltiefe links vs. rechts (volume_engine) → Severity-Gewicht 0,2", { paragraphOpts: { indent: { left: 360 } } }));

  // 4.3
  content.push(h2("4.3 Dynamische Asymmetrie"));
  content.push(p("Die statische Symmetrieanalyse erfasst nur die geometrische Position der Landmarks in Ruhe. Die dynamische Asymmetrie nutzt die 52 Blendshape-Koeffizienten (vgl. Kapitel 3) um Unterschiede in der Muskelaktivierung zwischen linker und rechter Gesichtshaelfte zu quantifizieren."));
  content.push(p("WICHTIG: Blendshapes werden NIEMALS ueber Views fusioniert. Die dynamische Asymmetrie wird ausschliesslich auf Basis der Blendshapes einer einzelnen Aufnahme berechnet \u2014 typischerweise der Frontalansicht. Dies verhindert Artefakte durch unterschiedliche Perspektiven.", { bold: true }));
  content.push(p("Das System analysiert acht bilateral gepaarte Blendshapes:"));

  const bsHeaders = ["Blendshape-Paar", "Anatomische Struktur", "Klinische Bedeutung bei Asymmetrie"];
  const bsWidths = [2800, 2800, 3760];
  const bsRows = [
    ["browDownLeft / browDownRight", "M. corrugator supercilii", "Einseitige Glabellafalten, Corrugator-Hyperaktivitaet"],
    ["browOuterUpLeft / browOuterUpRight", "M. frontalis (lateral)", "Einseitige Brauenhebung, kompensatorische Frontalis-Aktivitaet"],
    ["cheekSquintLeft / cheekSquintRight", "M. zygomaticus", "Asymmetrisches Laecheln, unterschiedliche Wangenhebung"],
    ["eyeBlinkLeft / eyeBlinkRight", "M. orbicularis oculi", "Lidschluss-Asymmetrie, moeglicher Hinweis auf Parese"],
    ["eyeSquintLeft / eyeSquintRight", "M. orbicularis oculi (inferior)", "Einseitige Crow\u2019s Feet, periortbitale Aktivitaet"],
    ["mouthSmileLeft / mouthSmileRight", "M. zygomaticus major", "Asymmetrisches Laecheln \u2014 haeufigster dynamischer Befund"],
    ["mouthFrownLeft / mouthFrownRight", "M. depressor anguli oris", "Einseitiger Mundwinkel-Downturn"],
    ["noseSneerLeft / noseSneerRight", "M. levator labii sup. alaeque nasi", "Einseitiges Nasenruempfen, Bunny Lines"],
  ];
  content.push(p("Tabelle 4.4: Blendshape-Paare fuer dynamische Asymmetrie", { bold: true }));
  content.push(makeTable(bsHeaders, bsRows, bsWidths));

  content.push(h3("4.3.1 Schwellenwert und Berechnung"));
  content.push(p("Der Schwellenwert fuer die dynamische Asymmetrie liegt bei einer Differenz von 0,10 (10 % der maximalen Aktivierung). Nur Paare mit einer Differenz > 0,10 werden reportet. Berechnung: diff = |left_value \u2212 right_value|."));
  content.push(p("Ein Blendshape-Koeffizient von 0,0 bedeutet keine Aktivierung, 1,0 maximale Aktivierung. Im Ruhezustand (Neutralexpression) sollten alle Werte nahe 0 liegen. Erhoehte Ruhewerte deuten auf chronische Muskelaktivitaetsmuster hin, die mit Alterung und Faltenbildung korrelieren (vgl. Kapitel 8, Muskeltonus)."));

  content.push(h3("4.3.2 Klinische Relevanz der dynamischen Asymmetrie"));
  content.push(p("Die dynamische Asymmetrie ergaenzt die statische Analyse um zwei wesentliche Dimensionen:"));
  content.push(p("1. Differenzialdiagnose: Eine ausgepraete mouthSmileLeft/Right-Differenz in Ruhe kann auf eine periphere Fazialisparese hinweisen und sollte neurologisch abgeklaert werden (vgl. Kapitel 14.3, Extreme Asymmetrie als Pathologie-Indikator)."));
  content.push(p("2. Behandlungsplanung: Einseitige Muskelueberaktivitaet kann mit gezieltem Neurotoxin behandelt werden. Beispiel: Eine browDownLeft-Aktivierung von 0,35 bei browDownRight von 0,08 deutet auf eine einseitige Corrugator-Hyperaktivitaet hin. Die Neurotoxin-Dosis fuer die Glabella (Zone Bw2) sollte asymmetrisch angepasst werden."));
  content.push(p("Die Ergebnisse der dynamischen Asymmetrieanalyse fliessen in den Severity-Score der jeweiligen Zone ein \u2014 mit einem Gewichtungsfaktor, der sicherstellt, dass dynamische Befunde die statischen nicht ueberlagern, sondern ergaenzen."));

  return content;
}

// ─── Kapitel 5: Gesichtsproportionen (FULL) ───

function kapitel5() {
  const content = [];
  content.push(h1("Kapitel 5: Gesichtsproportionen"));
  content.push(p("Die proportionale Analyse des Gesichts basiert auf dem Konzept idealer Verhaeltnisse, die in der klassischen Aesthetik und modernen Forschung als Grundlage fuer die Beurteilung fazialer Harmonie dienen. Abweichungen von diesen Idealverhaeltnissen koennen \u2014 muessen aber nicht \u2014 einen Behandlungsbedarf begrdnden. Ziel der Proportionsanalyse ist es, dem Behandler eine objektive Grundlage fuer die Planung volumengebender Massnahmen zu liefern."));
  content.push(p("Die proportion_engine des Aesthetic Biometrics Engine berechnet vier Proportionssysteme: vertikale Drittel, horizontale Fuenftel, Golden Ratio und Lip Ratio mit Cupid\u2019s Bow-Analyse. Alle Messungen werden in kalibrierten Millimetern durchgefuehrt und primaer aus der Frontalansicht gewonnen."));

  // 5.1
  content.push(h2("5.1 Vertikale Drittel"));
  content.push(p("Die vertikalen Gesichtsdrittel teilen das Gesicht in drei annaehernd gleich grosse Segmente:"));
  content.push(p("\u2022 Oberes Drittel: Trichion (Haaransatz, Landmark 10) → Glabella (Landmark 9)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Mittleres Drittel: Glabella → Subnasale (Landmark 2)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Unteres Drittel: Subnasale → Menton/Gnathion (Landmark 152)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Idealverhaeltnis: 1:1:1 (jedes Drittel = 33,3 % der Gesamthoehe)", { bold: true }));
  content.push(p("Die Messung erfolgt als vertikale Pixeldistanz (nur y-Komponente) zwischen den Landmarks, konvertiert zu Millimetern ueber die Iris-Kalibrierung. Die Deviation vom Idealverhaeltnis wird als mittlere absolute Abweichung der drei Anteile von 0,333 berechnet:"));
  content.push(p("deviation = (|upper_ratio \u2212 0,333| + |middle_ratio \u2212 0,333| + |lower_ratio \u2212 0,333|) / 3 \u00d7 100", { bold: true }));

  const thHeaders = ["Parameter", "Idealwert", "Klinische Bedeutung bei Abweichung"];
  const thWidths = [2200, 1600, 5560];
  const thRows = [
    ["Oberes Drittel < 30 %", "33,3 %", "Niedrige Stirn; Trichion-Landmark-Limitation bei Haarausfall beachten"],
    ["Oberes Drittel > 36 %", "33,3 %", "Hohe Stirn; Hairline-Eingriffe erwaegen (ausserhalb Filler-Indikation)"],
    ["Mittleres Drittel < 30 %", "33,3 %", "Verkuerzte Mittelgesichtshoehe; selten isoliert behandelbar"],
    ["Unteres Drittel > 36 %", "33,3 %", "Verlaengertes unteres Drittel; Kinn-Reduktion in Betracht ziehen"],
    ["Unteres Drittel < 30 %", "33,3 %", "Verkuerztes unteres Drittel; Kinn-Augmentation (Zone Ch1) erwaegen"],
  ];
  content.push(p("Tabelle 5.1: Vertikale Drittel \u2014 Referenzwerte und klinische Interpretation", { bold: true }));
  content.push(makeTable(thHeaders, thRows, thWidths));

  content.push(p("Hinweis: Das Trichion (Haaransatz) ist fuer MediaPipe nicht direkt detektierbar. Landmark 10 dient als Approximation des hoechsten zuverlaessig erkennbaren Stirnpunkts. Bei Patienten mit Geheimratsecken oder hohem Haaransatz kann das obere Drittel systematisch unterschaetzt werden."));

  // 5.2
  content.push(h2("5.2 Horizontale Fuenftel"));
  content.push(p("Die horizontalen Fuenftel teilen die Gesichtsbreite in fuenf annaehernd gleich breite Segmente. Die Messung erfolgt ueber die x-Koordinaten (horizontale Pixeldistanz) der folgenden Landmarks:"));
  content.push(p("1. Segment: Rechtes Praeauriculare → Rechter Augenaussenwinkel"));
  content.push(p("2. Segment: Rechter Augenaussenwinkel → Rechter Augeninnenwinkel"));
  content.push(p("3. Segment: Rechter Augeninnenwinkel → Linker Augeninnenwinkel (Interkanthaldistanz)"));
  content.push(p("4. Segment: Linker Augeninnenwinkel → Linker Augenaussenwinkel"));
  content.push(p("5. Segment: Linker Augenaussenwinkel → Linkes Praeauriculare"));
  content.push(p("Idealverhaeltnis: 1:1:1:1:1 (jedes Segment = 20 % der Gesamtbreite)", { bold: true }));
  content.push(p("Die Deviation berechnet sich analog zu den Dritteln: deviation = \u03a3|ratio_i \u2212 0,20| / 5 \u00d7 100."));
  content.push(p("Klinisch relevant ist insbesondere das dritte Segment (Interkanthaldistanz). Eine erhoehte Interkanthaldistanz (> 24 % der Gesamtbreite) wird als Hypertelorismus bezeichnet und kann auf ein Syndrom hinweisen. Eine verringerte Distanz (< 16 %) ist als Hypotelorismus bekannt. Beide Befunde liegen ausserhalb der aesthetischen Behandlungsindikation und sollten dokumentiert, aber nicht behandelt werden."));

  // 5.3
  content.push(h2("5.3 Golden Ratio"));
  content.push(p("Das Verhaeltnis von Gesichtshoehe zu Gesichtsbreite wird gegen den Goldenen Schnitt (Phi, \u03c6 = 1,618) verglichen. Die Messung erfolgt:"));
  content.push(p("\u2022 Gesichtshoehe: Trichion (Landmark 10) → Gnathion (Landmark 152), vertikale Pixeldistanz", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Gesichtsbreite: Bizygomatische Breite (Jochbein links, Landmark 330 → Jochbein rechts, Landmark 101), horizontale Pixeldistanz", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Berechnung: ratio = face_height_mm / face_width_mm", { bold: true }));
  content.push(p("Deviation: deviation_pct = |ratio \u2212 1,618| / 1,618 \u00d7 100", { bold: true }));

  const grHeaders = ["Parameter", "Idealwert", "Typischer Bereich", "Deviation bei Behandlungsbedarf"];
  const grWidths = [2200, 1400, 1800, 3960];
  const grRows = [
    ["Gesichtshoehe/Breite", "1,618 (\u03c6)", "1,4\u20131,8", "> 10 % Abweichung von \u03c6"],
    ["Deviation < 5 %", "\u2014", "\u2014", "Exzellente Proportion"],
    ["Deviation 5\u201310 %", "\u2014", "\u2014", "Leichte Abweichung, klinisch meist irrelevant"],
    ["Deviation > 10 %", "\u2014", "\u2014", "Signifikante Abweichung; Ursachenanalyse empfohlen"],
  ];
  content.push(p("Tabelle 5.2: Golden Ratio \u2014 Referenzwerte", { bold: true }));
  content.push(makeTable(grHeaders, grRows, grWidths));

  content.push(p("Klinische Einordnung: Der Goldene Schnitt ist ein aesthetisches Ideal, kein medizinischer Standard. Ethnische und individuelle Variationen sind zu beruecksichtigen. Das System verwendet die Golden Ratio Deviation als einen von mehreren Inputs fuer den globalen Aesthetik-Score, nicht als alleinigen Indikator."));

  // 5.4
  content.push(h2("5.4 Lip Ratio und Cupid\u2019s Bow"));
  content.push(p("Die Lippenanalyse ist fuer die Zonen Lp1 (Oberlippe) und Lp2 (Unterlippe) des Zonensystems (Kapitel 9) massgeblich. Sie umfasst drei Aspekte: Lip Ratio, Cupid\u2019s Bow-Tiefe und Cupid\u2019s Bow-Asymmetrie."));

  content.push(h3("5.4.1 Lip Ratio"));
  content.push(p("Das Lip Ratio beschreibt das Verhaeltnis der Oberlippenhoehe zur Unterlippenhoehe:"));
  content.push(p("\u2022 Oberlippenhoehe: Labrale superius (Landmark am oberen Vermilionrand) → Stomion (Mundspalte, Landmark 13), vertikale Distanz", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Unterlippenhoehe: Stomion → Labrale inferius (Landmark am unteren Vermilionrand), vertikale Distanz", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Idealverhaeltnis: Upper:Lower = 1:1,6 (Lip Ratio = 0,625)", { bold: true }));
  content.push(p("Deviation: deviation_pct = |lip_ratio \u2212 0,625| / 0,625 \u00d7 100"));

  const lipHeaders = ["Parameter", "Idealwert", "Referenzbereich", "Klinische Bedeutung"];
  const lipWidths = [2600, 1200, 1600, 3960];
  const lipRows = [
    ["Oberlippenhoehe (mm)", "6\u20139", "5\u201311", "< 5 mm: Lippenaugmentation erwaegen"],
    ["Unterlippenhoehe (mm)", "9\u201314", "8\u201316", "Selten behandlungsbeduerftig"],
    ["Lip Ratio", "0,625", "0,5\u20130,7", "< 0,5: Oberlippe deutlich zu duenn"],
    ["Lippenbreite (mm)", "45\u201355", "40\u201360", "Mundwinkel-zu-Mundwinkel-Distanz"],
  ];
  content.push(p("Tabelle 5.3: Lip Ratio \u2014 Referenzwerte", { bold: true }));
  content.push(makeTable(lipHeaders, lipRows, lipWidths));

  content.push(h3("5.4.2 Cupid\u2019s Bow-Analyse"));
  content.push(p("Der Cupid\u2019s Bow (Amorbogen) ist die M-foermige Kontur der oberen Vermilionlinie. Die Analyse misst:"));
  content.push(p("\u2022 Bogentiefe (cupid_bow_depth_mm): Vertikaler Abstand zwischen den Philtralsaeulen-Peaks (Landmarks 267 links, 37 rechts) und dem Mittelpunkt der Oberlippe (Landmark 0). Berechnung: avg(mid_y \u2212 left_peak_y, mid_y \u2212 right_peak_y), konvertiert zu mm.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Bogenasymmetrie (cupid_bow_asymmetry_pct): Differenz der Peakhoehen links vs. rechts, normalisiert auf die durchschnittliche Peakhoehe. Berechnung: |left_peak_y \u2212 right_peak_y| / avg_peak_height \u00d7 100.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Interpretation: Eine Cupid\u2019s Bow-Tiefe von 0 mm deutet auf einen flachen, undefineten Lippensaum hin. Asymmetrien > 15 % koennen auf vorangegangene Injektionen, Narben oder kongenitale Variationen hinweisen."));

  return content;
}

// ─── Kapitel 7: Volumenanalyse (FULL) ───

function kapitel7() {
  const content = [];
  content.push(h1("Kapitel 7: Volumenanalyse"));
  content.push(p("Der altersbedingte Volumenverlust ist einer der Hauptmechanismen der Gesichtsalterung. Im Gegensatz zur Symmetrie- und Proportionsanalyse, die primaer zweidimensionale Messungen verwenden, nutzt die Volumenanalyse die z-Koordinaten der 478 3D-Landmarks, um Tiefenverhaeltnisse im Gesicht zu quantifizieren. Damit lassen sich Volumendefizite identifizieren, die in der reinen Frontalansicht nicht sichtbar sind."));
  content.push(p("Die volume_engine des Aesthetic Biometrics Engine analysiert vier klinisch relevante Volumenkomponenten: Ogee Curve (Mittelgesichts-S-Kurve), Temporal Hollowing (Schlaefeneintiefung), Tear Trough (Traenental) und Pre-Jowl Sulcus (Haengewange). Die besten Ergebnisse werden aus der Obliqueansicht (45\u00b0) gewonnen, da hier die Tiefenunterschiede am deutlichsten sichtbar sind."));

  // 7.1
  content.push(h2("7.1 Ogee Curve (Mittelgesichts-S-Kurve)"));
  content.push(p("Die Ogee-Kurve (auch als S-Kurve des Mittelgesichts bezeichnet) ist die fliessende Konturlinie, die von der lateralen Stirn ueber die Wangenhoehe in die Wangenvertiefung verlaeuft. Eine gut definierte Ogee-Kurve ist ein Kennzeichen eines jugendlichen Gesichts. Ihre Abflachung ist eines der fruehesten und klinisch auffaelligsten Zeichen des Mittelgesichtsvolumenverlusts."));

  content.push(h3("7.1.1 Messpunkte und Tiefentransitionen"));
  content.push(p("Die Ogee-Kurve wird ueber vier Tiefenpunkte entlang der malaren Region charakterisiert:"));
  content.push(p("\u2022 Infraorbital (Landmarks 253/23): Punkt unterhalb des Orbitarands \u2014 sollte leicht zurueckliegen", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Malar High (Landmarks 329/100): Hoechster Punkt der Wangenprominenz \u2014 sollte nach vorn projizieren", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Malar Low (Landmarks 425/205): Tieferer Wangenbereich \u2014 Uebergang zur Bukkalregion", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Cheekbone (Landmarks 330/101): Jochbein \u2014 knoecherne Referenz", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Die z-Tiefendifferenz (in mm) zwischen Malar High und Infraorbital repraesentiert die Malarprominenz. Die Differenz zwischen Cheekbone und Malar Low repraesentiert den Bukkal-Uebergang."));

  content.push(h3("7.1.2 Score-Berechnung"));
  content.push(p("Der Ogee-Score (0\u2013100) quantifiziert die Fliessendheit der S-Kurve:"));
  content.push(p("raw_score = |malar_depth| \u00d7 10 + |buccal_transition| \u00d7 8", { bold: true }));
  content.push(p("score = clamp(raw_score, 0, 100)", { bold: true }));

  const ogHeaders = ["Score-Bereich", "Interpretation", "Klinische Empfehlung"];
  const ogWidths = [1600, 3200, 4560];
  const ogRows = [
    ["70\u2013100", "Fliessende S-Kurve; jugendlich", "Kein Behandlungsbedarf"],
    ["50\u201370", "Leichte Abflachung; fruehe Zeichen", "Monitoring oder Biostimulation"],
    ["30\u201350", "Deutliche Abflachung", "HA Deep (Voluma) oder CaHA (Radiesse) in Zone Ck2"],
    ["< 30", "Skelettiertes Erscheinungsbild", "Strukturelle Filler-Augmentation in Ck1 und Ck2"],
  ];
  content.push(p("Tabelle 7.1: Ogee-Score-Interpretation", { bold: true }));
  content.push(makeTable(ogHeaders, ogRows, ogWidths));
  content.push(p("Ein Score < 60 setzt das Flag is_flattened = true, was im Zonensystem (Kapitel 9) den Severity-Score fuer Zone Ck2 direkt beeinflusst."));

  // 7.2
  content.push(h2("7.2 Temporal Hollowing (Schlaefeneintiefung)"));
  content.push(p("Temporal Hollowing bezeichnet die Eintiefung der Fossa temporalis, die durch Volumenverlust des M. temporalis, des temporalen Fettpolsters und der Fascia temporalis entsteht. Es ist einer der fruehesten Alterungsindikatoren und betrifft Zone T1 des Zonensystems."));

  content.push(h3("7.2.1 Messmethode"));
  content.push(p("Die Temporaltiefe wird als z-Differenz (in mm) zwischen dem temporalen Landmark und dem lateralen Brauenlandmark gemessen:"));
  content.push(p("temporal_depth = z(temporal) \u2212 z(brow_outer) \u2014 separat fuer links und rechts", { bold: true }));
  content.push(p("Asymmetrie: asymmetry_mm = |left_depth \u2212 right_depth|"));

  const tempHeaders = ["Parameter", "Schwellenwert", "Interpretation"];
  const tempWidths = [3200, 1800, 4360];
  const tempRows = [
    ["temporal_depth (links oder rechts)", "> 3,0 mm", "Hollowing detektiert (is_hollowed = true)"],
    ["asymmetry_mm", "> 2,0 mm", "Asymmetrische Eintiefung \u2014 Pathologie ausschliessen"],
    ["Idealer Bereich", "-2,0 bis 2,0 mm", "Zone T1 Referenzwerte (Kapitel 9)"],
  ];
  content.push(p("Tabelle 7.2: Temporal Hollowing \u2014 Schwellenwerte", { bold: true }));
  content.push(makeTable(tempHeaders, tempRows, tempWidths));

  content.push(p("Behandlung: Biostimulantien (Sculptra, Radiesse) in der tiefen subkutanen Ebene. Die A. temporalis superficialis verlaeuft in dieser Region und muss geschont werden (vgl. Kapitel 14, Vaskulaere Risikozonen)."));

  // 7.3
  content.push(h2("7.3 Tear Trough Assessment (Traenentalanalyse)"));
  content.push(p("Das Traenental (Sulcus palpebromalaris) ist die Vertiefung zwischen Unterlid und Wange. Es betrifft Zone Tt1, eine der technisch anspruchsvollsten und vaskulaer riskantesten Behandlungszonen (vgl. Kapitel 14.5)."));

  content.push(h3("7.3.1 Tiefenmessung"));
  content.push(p("Die Traenentaltiefe wird als z-Differenz zwischen dem infraorbitalen Landmark und dem Jochbein gemessen:"));
  content.push(p("tear_trough_depth = z(infraorbital) \u2212 z(cheekbone) \u2014 separat links/rechts", { bold: true }));
  content.push(p("Der Severity-Score fuer das Traenental berechnet sich aus der mittleren Tiefe:"));
  content.push(p("severity = min(10, avg_depth \u00d7 2,5)", { bold: true }));

  const ttHeaders = ["Severity-Score", "Tiefe (mm)", "Klinische Einschaetzung", "Empfehlung"];
  const ttWidths = [1400, 1200, 3200, 3560];
  const ttRows = [
    ["0\u20132", "0\u20130,8", "Kein oder minimales Traenental", "Keine Behandlung noetig"],
    ["2\u20134", "0,8\u20131,6", "Leichtes Traenental", "Midface-First-Strategie (Ck2/Ck3) pruefen"],
    ["4\u20136", "1,6\u20132,4", "Moderates Traenental", "Ck2 zuerst, dann Reevaluation"],
    ["6\u20138", "2,4\u20133,2", "Tiefes Traenental", "CAUTION: Konservativ, max 0,1\u20130,2 ml/Seite"],
    ["8\u201310", "> 3,2", "Schwere Deformitaet", "REFERRAL: Facharzt-Abklaerung erwaegen"],
  ];
  content.push(p("Tabelle 7.3: Tear Trough Severity-Einstufung", { bold: true }));
  content.push(makeTable(ttHeaders, ttRows, ttWidths));

  content.push(p("Die Midface-First-Strategie (vgl. Kapitel 14.5) ist bei Zone Tt1 besonders wichtig: In vielen Faellen reduziert eine Volumenauffuellung in den Zonen Ck2 und Ck3 die Traenentaltiefe sekundaer um 30\u201350 %, wodurch eine direkte Behandlung des Traenentals entweder unnoetig wird oder nur mit minimalen Volumina erfolgen muss."));

  // 7.4
  content.push(h2("7.4 Pre-Jowl Sulcus (Haengewange)"));
  content.push(p("Der Pre-Jowl Sulcus ist die Einbuchtung lateral des Kinns, die durch Volumenatrophie und Gewebeabsenkung entsteht. Er betrifft Zone Jw1 und korreliert eng mit der Kieferlinien-Kontinuitaet (Zone Jl1)."));

  content.push(h3("7.4.1 Messmethode"));
  content.push(p("Die Jowl-Tiefe wird als z-Differenz zwischen dem Gonion (Kieferwinkel) und dem Pogonion (Kinnspitze) gemessen:"));
  content.push(p("jowl_depth = z(gonion) \u2212 z(pogonion) \u2014 separat links/rechts", { bold: true }));

  const jwHeaders = ["Parameter", "Schwellenwert", "Interpretation"];
  const jwWidths = [3200, 1800, 4360];
  const jwRows = [
    ["jowl_depth (links oder rechts)", "> 2,0 mm", "Jawline Break detektiert (jawline_break_detected = true)"],
    ["Asymmetrie", "> 1,5 mm", "Einseitige Jowl-Bildung \u2014 ggf. asymmetrische Behandlung"],
    ["Beide Seiten > 2 mm", "\u2014", "Strukturelle Filler-Augmentation in Jw1 + Jl1 empfohlen"],
  ];
  content.push(p("Tabelle 7.4: Pre-Jowl Sulcus \u2014 Schwellenwerte", { bold: true }));
  content.push(makeTable(jwHeaders, jwRows, jwWidths));

  content.push(p("Die Behandlung des Pre-Jowl Sulcus sollte immer im Kontext der gesamten unteren Gesichtskontur betrachtet werden. Haeufig ist eine Kombination aus Kinn-Augmentation (Zone Ch1, supraperiostaler Bolus) und Jawline-Definition (Zone Jl1) effektiver als eine isolierte Jowl-Behandlung. Das Priorisierungssystem (vgl. Kapitel 13) ordnet Ch1 und Jl1 in die strukturelle Prioritaetsstufe P2 ein, waehrend Jw1 als Volumendefizit in P3 klassifiziert ist."));

  return content;
}

// ─── Kapitel 8: Altersbedingte Veraenderungen (FULL) ───

function kapitel8() {
  const content = [];
  content.push(h1("Kapitel 8: Altersbedingte Ver\u00e4nderungen"));
  content.push(p("Die Gesichtsalterung ist ein multifaktorieller Prozess, der knoecherne Resorption, Fettkompartiment-Verschiebung, Muskeltonusveraenderungen und Hauterschlaffung umfasst. Die aging_engine des Aesthetic Biometrics Engine quantifiziert drei Aspekte der Alterung, die aus den 478 Landmark-Koordinaten und den 52 Blendshape-Koeffizienten abgeleitet werden koennen: Muskeltonus-Veraenderungen, gravitationelle Drift und periorbitale Alterung."));
  content.push(p("WICHTIG: Blendshapes sind viewgebunden und werden NICHT ueber verschiedene Aufnahmen fusioniert. Die Aging-Analyse wird typischerweise auf der Frontalansicht durchgefuehrt.", { bold: true }));

  // 8.1
  content.push(h2("8.1 Muskeltonus-Ver\u00e4nderungen"));
  content.push(p("Die mimische Muskulatur veraendert sich im Laufe des Lebens: Bestimmte Muskeln werden hyperaktiv (chronische Kontraktion fuehrt zu Faltenbildung), waehrend andere an Tonus verlieren (Erschlaffung fuehrt zu Ptosis und Konturverlust). Die Blendshape-Analyse ermoeglicht eine nicht-invasive Abschaetzung dieser Veraenderungen."));

  content.push(h3("8.1.1 Blendshape-zu-Muskel-Mapping"));
  content.push(p("Das System gruppiert die 52 Blendshape-Koeffizienten in vier klinisch relevante Muskelgruppen:"));

  const musHeaders = ["Muskelgruppe", "Blendshapes", "Klinische Bedeutung bei erhoehter Ruheaktivierung"];
  const musWidths = [2000, 3800, 3560];
  const musRows = [
    ["Frontalis (Stirnheber)", "browInnerUp, browOuterUpLeft, browOuterUpRight", "Kompensatorische Hyperaktivitaet bei Brauenptosis; horizontale Stirnfalten"],
    ["Corrugator (Brauensenker)", "browDownLeft, browDownRight", "Glabella-\u201e11-Linien\u201c; chronische Muskelspannung"],
    ["Orbicularis (perioral)", "mouthPucker, mouthFunnel, mouthPressLeft, mouthPressRight", "Niedriger Tonus deutet auf periorale Alterung hin"],
    ["Masseter (Kiefer)", "jawOpen, jawForward, jawLeft, jawRight", "Erhoehte Aktivitaet bei Bruxismus/Kieferpressen"],
  ];
  content.push(p("Tabelle 8.1: Blendshape-Gruppen und ihre klinische Interpretation", { bold: true }));
  content.push(makeTable(musHeaders, musRows, musWidths));

  content.push(h3("8.1.2 Severity-Berechnung"));
  content.push(p("Der overall_muscle_age_indicator (0\u201310) berechnet sich aus den gemittelten Blendshape-Werten der vier Gruppen:"));
  content.push(p("severity = frontalis \u00d7 3,0 + corrugator \u00d7 3,0 + (1 \u2212 orbicularis) \u00d7 2,0 + masseter \u00d7 2,0", { bold: true }));
  content.push(p("Hierbei wird die Orbicularis-Aktivierung invertiert: Ein niedriger Orbicularis-Tonus (Wert nahe 0) erhoet den Severity-Score, da dies auf periorale Erschlaffung hindeutet. Frontalis und Corrugator erhalten die hoechste Gewichtung (je 3,0), da ihre Hyperaktivitaet die haeufigste Neurotoxin-Indikation darstellt (vgl. Kapitel 11, Tabelle 11.2)."));

  content.push(p("Interpretation der Muskeltonus-Werte:", { bold: true }));
  content.push(p("\u2022 frontalis_compensation > 0,15: Kompensatorische Brauenhebung \u2014 Vorsicht bei isolierter Frontalis-Behandlung (Ptosis-Risiko, vgl. Kapitel 14.4)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 corrugator_activity > 0,20: Erhoehte Glabella-Spannung in Ruhe \u2014 Neurotoxin-Indikation fuer Zone Bw2", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 orbicularis_tone < 0,05: Periorale Hypotonie \u2014 Lip Flip oder periorale Behandlung in Betracht ziehen", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 masseter_activity > 0,15: Moeglicher Bruxismus \u2014 Masseter-Hypertrophie-Behandlung mit Neurotoxin erwaegen", { paragraphOpts: { indent: { left: 360 } } }));

  // 8.2
  content.push(h2("8.2 Gravitationelle Drift"));
  content.push(p("Mit zunehmendem Alter sinken die Weichgewebe des Gesichts unter dem Einfluss der Schwerkraft nach inferior ab. Dieser als gravitationelle Drift bezeichnete Prozess betrifft alle Gesichtsschichten: Haut, SMAS, Fettkompartimente und Retaining Ligaments. Die Analyse misst die vertikale Verschiebung von Landmarks relativ zu idealen (jugendlichen) Positionen."));

  content.push(h3("8.2.1 Drei Driftindikatoren"));

  const driftHeaders = ["Indikator", "Messung", "Ideale Distanz (Pixel)", "Betroffene Zonen"];
  const driftWidths = [2000, 3000, 1800, 2560];
  const driftRows = [
    ["Brauendeszensus", "Vertikaler Abstand Brauenpeak \u2192 Augenaussenwinkel", "\u2265 40 px", "Bw1, Fo1"],
    ["Malardeszensus", "Vertikale Position Jochbein relativ zu Augenlinie", "\u2264 50 px unter Augenlinie", "Ck2, Ck3, Ns1"],
    ["Jowl-Deszensus", "Vertikaler Abstand Mundwinkel \u2192 Gonion", "\u2265 80 px", "Jw1, Jl1, Mn1"],
  ];
  content.push(p("Tabelle 8.2: Gravitationelle Driftindikatoren", { bold: true }));
  content.push(makeTable(driftHeaders, driftRows, driftWidths));

  content.push(p("Die Berechnung in Millimetern: Fuer jeden Indikator wird die Differenz zwischen der gemessenen und der idealen Distanz berechnet, konvertiert in mm ueber die Kalibrierung. Ein positiver Wert (in mm) repraesentiert den Grad der Absenkung."));
  content.push(p("Der overall_drift_score (0\u201310) ist der Mittelwert der drei Driftindikatoren in mm:"));
  content.push(p("drift_score = min(10, (brow_descent_mm + malar_descent_mm + jowl_descent_mm) / 3)", { bold: true }));

  content.push(h3("8.2.2 Klinische Einordnung"));
  content.push(p("\u2022 Drift-Score < 2,0: Minimale Absenkung; typisch fuer Patienten unter 35 Jahren", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Drift-Score 2,0\u20134,0: Moderate Absenkung; Volumenrestauration kann die Ptosis teilweise korrigieren", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Drift-Score 4,0\u20136,0: Fortgeschrittene Absenkung; kombinierte Behandlung (Filler + Neurotoxin) empfohlen", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Drift-Score > 6,0: Ausgepragte Ptosis; chirurgische Optionen (Facelift) in Betracht ziehen", { paragraphOpts: { indent: { left: 360 } } }));

  // 8.3
  content.push(h2("8.3 Periorbitale Alterung"));
  content.push(p("Die periorbitale Region (Augenumgebung) altert aufgrund der extrem duennen Haut und der oberflaechen Gefaessstruktur besonders frueh und sichtbar. Die Analyse erfasst drei Indikatoren:"));

  content.push(h3("8.3.1 Crow\u2019s Feet Potential"));
  content.push(p("Die Kraehenfuesse (laterale Periorbitalfalten) korrelieren mit der Aktivitaet des M. orbicularis oculi. Der crow_feet_potential-Wert (0\u20131) wird aus den eyeSquint-Blendshapes abgeleitet:"));
  content.push(p("crow_feet_potential = avg(eyeSquintLeft, eyeSquintRight)", { bold: true }));
  content.push(p("Ein Wert > 0,3 in Ruhe deutet auf eine erhoehte Tendenz zur Kraehenfuessbildung hin und ist eine Neurotoxin-Indikation fuer den lateralen Orbicularis oculi."));

  content.push(h3("8.3.2 Unterlidlaxitaet"));
  content.push(p("Die Unterlidlaxitaet wird aus der vertikalen Distanz zwischen dem infraorbitalen Landmark und der Augenmitte geschaetzt:"));
  content.push(p("lid_gap_mm = Kalibrierung(|infraorbital_y \u2212 eye_center_y|)"));
  content.push(p("lid_laxity = min(1,0, lid_gap_mm / 15,0)", { bold: true }));
  content.push(p("Werte > 0,5 deuten auf eine signifikante Unterliderschlaffung hin, die die Traenental-Behandlung (Zone Tt1) erschweren kann. In solchen Faellen ist besondere Vorsicht geboten, da der Filler unter dem erschlafften Lid sichtbar werden kann (Tyndall-Effekt, vgl. Kapitel 14.5)."));

  content.push(h3("8.3.3 Orbitale Einsenkung"));
  content.push(p("Die orbitale Einsenkung (Orbital Hollowing) wird aus der z-Tiefendifferenz zwischen dem infraorbitalen und dem Jochbein-Landmark abgeleitet:"));
  content.push(p("hollowing = min(1,0, Kalibrierung(|z_infraorbital \u2212 z_cheekbone|) / 5,0)", { bold: true }));
  content.push(p("Dieser Indikator erfasst den skelettalen Anteil der periorbitalen Alterung, der durch Volumenverlust des infraorbitalen Fettpolsters und knoecherne Resorption des Orbitarands entsteht."));

  content.push(h3("8.3.4 Composite Aging Severity"));
  content.push(p("Der overall_aging_severity-Score (0\u201310) kombiniert alle drei Alterungskomponenten in einem gewichteten Composite:"));
  content.push(p("severity = muscle_severity \u00d7 0,3 + drift_score \u00d7 0,5 + (crow_feet + lid_laxity) \u00d7 5 \u00d7 0,2", { bold: true }));
  content.push(p("Die Gewichtung priorisiert die gravitationelle Drift (50 %) als dominanten Alterungsindikator, gefolgt von Muskeltonus-Veraenderungen (30 %) und periorbitalen Befunden (20 %)."));

  const ageHeaders = ["Severity-Score", "Geschaetztes biologisches Alter", "Typische Befunde"];
  const ageWidths = [1400, 2600, 5360];
  const ageRows = [
    ["< 1,5", "25\u201330 Jahre", "Minimale Veraenderungen; guter Muskeltonus"],
    ["1,5\u20133,0", "30\u201335 Jahre", "Beginnende Frontalis-Kompensation; leichtes Temporal Hollowing"],
    ["3,0\u20134,5", "35\u201340 Jahre", "Moderate Drift; Nasolabialfalte sichtbar; erste Kraehenfuesse"],
    ["4,5\u20136,0", "40\u201345 Jahre", "Deutliche Midface-Ptosis; Ogee-Abflachung; Jowl-Ansaetze"],
    ["6,0\u20137,5", "45\u201355 Jahre", "Fortgeschrittene Alterung; ausgepraete Jowls; tiefes Traenental"],
    ["> 7,5", "55+ Jahre", "Schwere Gesamtalterung; chirurgische Evaluation erwaegen"],
  ];
  content.push(p("Tabelle 8.3: Biologische Altersschaetzung aus Aging Severity", { bold: true }));
  content.push(makeTable(ageHeaders, ageRows, ageWidths));

  content.push(p("WICHTIG: Die biologische Altersschaetzung ist eine Approximation und kann erheblich vom chronologischen Alter abweichen. Faktoren wie Sonnenschutz, Genetik, Rauchen und vorangegangene Behandlungen beeinflussen das biologische Alter erheblich. Der Score dient als klinische Orientierung, nicht als diagnostisches Instrument.", { bold: true }));

  return content;
}

// ─── Kapitel 3: Landmark-basierte Gesichtsvermessung (FULL) ───

function kapitel3() {
  const content = [];
  content.push(h1("Kapitel 3: Landmark-basierte Gesichtsvermessung"));
  content.push(p("Die objektive Gesichtsanalyse erfordert ein standardisiertes Koordinatensystem, das anatomische Strukturen zuverlaessig und reproduzierbar lokalisiert. Das MediaPipe Face Landmarker System der Google AI Edge Platform bildet die Grundlage des Aesthetic Biometrics Engine. Es erkennt 478 dreidimensionale Landmarks pro Gesicht und liefert zusaetzlich 52 Blendshape-Koeffizienten (Muskelaktivierungsmuster) sowie eine 4\u00d74-Transformationsmatrix fuer die Kopfpositionsbestimmung."));
  content.push(p("Dieses Kapitel beschreibt das Landmark-System, seine anatomischen Gruppierungen und die Methodik der Iris-basierten Pixelkalibrierung, die alle nachfolgenden Messungen in klinisch verwertbare Millimeterwerte ueberfuehrt."));

  // 3.1
  content.push(h2("3.1 Das 478-Punkt-Landmarksystem"));
  content.push(p("MediaPipe Face Landmarker lokalisiert 478 Punkte pro erkanntem Gesicht. Jeder Punkt wird als normalisiertes 3D-Koordinatentripel (x, y, z) im Bereich [0, 1] zurueckgegeben, wobei x und y die Position relativ zur Bildbreite und -hoehe beschreiben und z die relative Tiefe (negativ = naeher zur Kamera) angibt."));
  content.push(p("Die Landmarks gliedern sich in drei Gruppen:"));
  content.push(p("\u2022 Landmarks 0\u2013467: Core Face Mesh \u2014 die klassischen 468 Punkte des Gesichtsnetzes, die Gesichtsoberflaeche, Augen, Brauen, Nase, Mund und Kieferlinie abdecken.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Landmarks 468\u2013472: Linke Iris \u2014 fuenf Punkte (Zentrum, rechts, oben, links, unten), die den linken Irisrand definieren.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Landmarks 473\u2013477: Rechte Iris \u2014 fuenf Punkte analog zur linken Iris.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Die Iris-Landmarks sind besonders wertvoll, da die menschliche Iris einen nahezu konstanten Durchmesser von 11,7 \u00b1 0,5 mm aufweist (Hashemi et al., 2012) und damit als natuerlicher Massstab fuer die Pixelkalibrierung dient."));

  // 3.1.1 Midline
  content.push(h3("3.1.1 Midline-Landmarks"));
  content.push(p("Die Midline-Landmarks liegen auf der Median-Sagittalebene des Gesichts und definieren die vertikale Referenzlinie fuer alle Symmetriemessungen:"));

  const midHeaders = ["Anatomischer Name", "Landmark-Index", "Klinische Bedeutung"];
  const midWidths = [2800, 1800, 4760];
  const midRows = [
    ["Trichion (approx.)", "10", "Hoechster zuverlaessiger Stirnpunkt, Oberkante des oberen Gesichtsdrittels"],
    ["Glabella", "9", "Nasenwurzel/Brauenzentrum, Referenz fuer Brauensymmetrie"],
    ["Nasion", "168", "Nasenbeinansatz, Uebergang Stirn\u2192Nase"],
    ["Rhinion", "5", "Nasenruecken, Referenzpunkt fuer Nasenprofil-Analyse"],
    ["Pronasale", "4", "Nasenspitze, anteriorster Punkt der Nase, E-Line-Referenz"],
    ["Subnasale", "2", "Nasenbasis, Drehpunkt fuer Nasolabialwinkel"],
    ["Labrale superius", "0", "Oberlippenmittelpunkt, obere Vermiliongrenze"],
    ["Stomion", "13", "Mundspalte, Trennlinie Ober-/Unterlippe"],
    ["Labrale inferius", "17", "Unterlippenmittelpunkt"],
    ["Mentolabial-Sulcus", "18", "Lippen-Kinn-Falte"],
    ["Pogonion", "175", "Anteriorster Kinnpunkt, Referenz fuer Profilanalyse"],
    ["Gnathion (Menton)", "152", "Tiefster Kinnpunkt, Unterkante des unteren Gesichtsdrittels"],
  ];
  content.push(p("Tabelle 3.1: Midline-Landmarks", { bold: true }));
  content.push(makeTable(midHeaders, midRows, midWidths));

  // 3.1.2 Bilateral
  content.push(h3("3.1.2 Bilaterale (gepaarte) Landmarks"));
  content.push(p("Bilaterale Landmarks existieren als links-rechts-Paare und bilden die Grundlage der Symmetrieanalyse. Die Konvention folgt dem MediaPipe-Standard: der erste Index ist der LINKE Landmark (aus Sicht des Betrachters rechts im Bild), der zweite der RECHTE."));

  const pairHeaders = ["Struktur", "Links", "Rechts", "Klinische Relevanz"];
  const pairWidths = [2400, 1200, 1200, 4560];
  const pairRows = [
    ["eye_outer", "263", "33", "Lateraler Augenwinkel, Lidspaltenmessung"],
    ["eye_inner", "362", "133", "Medialer Augenwinkel, Interkanthaldistanz"],
    ["brow_outer", "276", "46", "Laterale Braue, Ptosis-Beurteilung"],
    ["brow_inner", "285", "55", "Mediale Braue, Glabella-Komplex"],
    ["brow_peak", "282", "52", "Brauenscheitelpunkt, Brauenform-Analyse"],
    ["mouth_corner", "291", "61", "Mundwinkel, Mundwinkelsymmetrie"],
    ["cheekbone", "330", "101", "Jochbeinprominenz, Mittelgesichtsvolumen"],
    ["alar", "309", "79", "Nasenfluegelbreiteste, Nasenbasismessung"],
    ["gonion", "365", "136", "Kieferwinkel, Jawline-Analyse"],
    ["malar_high", "329", "100", "Obere Wangenhoehe, Ogee-Kurve"],
    ["malar_low", "425", "205", "Untere Wange, Nasolabialfalten-Region"],
    ["infraorbital", "253", "23", "Traenentalregion, Volumendefizit"],
    ["temporal", "251", "21", "Schlaefenregion, Temporal Hollowing"],
  ];
  content.push(p("Tabelle 3.2: Bilaterale Landmarks", { bold: true }));
  content.push(makeTable(pairHeaders, pairRows, pairWidths));

  // 3.2
  content.push(h2("3.2 Anatomische Gruppen und Konturen"));
  content.push(p("Neben einzelnen Punkten definiert das System zusammenhaengende Konturgruppen, die fuer die Analyse von Lippen, Augen und Gesichtsoval verwendet werden:"));
  content.push(p("\u2022 Lip Upper Outer (11 Punkte: 61\u2192185\u219240\u219239\u219237\u21920\u2192267\u2192269\u2192270\u2192409\u2192291): Aeussere Oberlippenkontur von rechtem zu linkem Mundwinkel. Definiert die Vermiliongrenze und den Cupid\u2019s Bow.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Lip Lower Outer (11 Punkte: 291\u2192375\u2192321\u2192405\u2192314\u219217\u219284\u2192181\u219291\u2192146\u219261): Aeussere Unterlippenkontur, definiert das Lip-Ratio (Ober- zu Unterlippenverhaeltnis).", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Lip Upper/Lower Inner (je 11 Punkte): Innere Lippenraender, relevant fuer die Vermilion-Show und die funktionelle Mundoeffnung.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Left/Right Eye Contour (je 17 Punkte): Vollstaendige Lidkontur fuer Fissura palpebralis und perioperative Analyse.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Left/Right Brow (je 10 Punkte): Brauenkontur fuer Formbewertung und Ptosis-Screening.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Face Oval (37 Punkte): Gesichtsrandkontur von Stirn ueber Wangen zum Kinn, definiert die Gesichtsform und Jawline.", { paragraphOpts: { indent: { left: 360 } } }));

  // 3.3
  content.push(h2("3.3 Iris-basierte Kalibrierung"));
  content.push(p("Das zentrale Problem jeder bildbasierten Vermessung ist die Umrechnung von Pixelabstaenden in reale Einheiten. Ohne Kalibrierung sind alle Messungen rein relativ und erlauben keinen Vergleich zwischen Patienten, Aufnahmen oder Zeitpunkten."));
  content.push(p("Der Aesthetic Biometrics Engine loest dieses Problem durch die Nutzung der menschlichen Iris als natuerlichen Massstab:"));

  content.push(h3("3.3.1 Referenzwert und biologische Grundlage"));
  content.push(p("Der horizontale Irisdurchmesser (HVID \u2014 Horizontal Visible Iris Diameter) betraegt beim Erwachsenen 11,7 \u00b1 0,5 mm (Hashemi et al., 2012, n = 3.537). Diese bemerkenswerte Konstanz \u2014 unabhaengig von Ethnie, Geschlecht und Alter (ab 20 Jahre) \u2014 macht die Iris zum idealen internen Kalibrierstandard."));
  content.push(p("Die Kalibrierung erfolgt in drei Schritten:"));
  content.push(p("1. Iris-Breite in Pixeln messen: Der horizontale Abstand zwischen dem linken und rechten Irispunkt wird berechnet. Dies geschieht fuer beide Augen separat, und der Durchschnitt wird gebildet.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("2. Kalibrierungsfaktor berechnen: px_per_mm = iris_width_px / 11,7 mm. Dieser Faktor konvertiert alle Pixelmessungen in Millimeter.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("3. Plausibilitaetspruefung: Der errechnete Faktor wird gegen die Gesichtsbreite (typisch 130\u2013160 mm) validiert. Weicht der Iris-basierte Wert stark ab, sinkt die Confidence.", { paragraphOpts: { indent: { left: 360 } } }));

  content.push(h3("3.3.2 Fallback-Strategie: Face-Width-Schaetzung"));
  content.push(p("In Situationen, in denen die Iris-Kalibrierung nicht zuverlaessig ist \u2014 zum Beispiel bei Brillentraegern, geschlossenen Augen oder Profilaufnahmen, bei denen eine Iris verdeckt ist \u2014 aktiviert das System automatisch einen Fallback:"));
  content.push(p("Der Fallback nutzt die Gesichtsbreite (Bizygomatische Distanz), die typischerweise 130\u2013160 mm betraegt. Diese Schaetzung ist weniger praezise als die Iris-Methode (erwarteter Fehler: 5\u201310 % statt 2\u20133 %), wird aber zuverlaessig erkannt, da die Landmarks fuer den Gesichtsrand selbst bei schwierigen Aufnahmen robust sind."));

  const calHeaders = ["Eigenschaft", "Iris-Kalibrierung", "Face-Width-Fallback"];
  const calWidths = [2600, 3380, 3380];
  const calRows = [
    ["Methode", "iris_width_px / 11,7 mm", "face_width_px / 140,0 mm (geschaetzt)"],
    ["Genauigkeit", "2\u20133 % Fehler", "5\u201310 % Fehler"],
    ["Confidence", "0,85\u20130,95", "0,40\u20130,55"],
    ["Voraussetzung", "Beide Iris-Landmarks sichtbar", "Face-Oval-Landmarks vorhanden"],
    ["Aktivierung", "Standard (bevorzugt)", "Automatisch bei Iris-Confidence < Schwelle"],
  ];
  content.push(p("Tabelle 3.3: Vergleich der Kalibrierungsmethoden", { bold: true }));
  content.push(makeTable(calHeaders, calRows, calWidths));

  content.push(h3("3.3.3 Confidence-Modell"));
  content.push(p("Die Kalibrierungs-Confidence wird durch mehrere Faktoren bestimmt:"));
  content.push(p("\u2022 Iris-Symmetrie: Stimmen die Durchmesser beider Iris ueberein? Eine starke Abweichung (z. B. durch Verdeckung) reduziert die Confidence.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Iris-Groesse in Pixeln: Zu kleine Iris (< 15 px Durchmesser) fuehren zum automatischen Fallback, da die Messungenauigkeit zu gross wird.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Cross-Validation: Der Iris-basierte Kalibrierungsfaktor wird gegen die Gesichtsbreite geprueft. Stimmen beide ueberein (innerhalb 15 %), steigt die Confidence.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("KLINISCHER HINWEIS: Die Genauigkeit der Kalibrierung ist der limitierende Faktor fuer alle nachfolgenden Millimeter-Messungen. Eine Iris-basierte Kalibrierung mit Confidence > 0,85 ermoeglicht klinisch verwertbare Aussagen. Messungen mit Face-Width-Fallback (Confidence 0,40\u20130,55) sollten als Schaetzungen interpretiert und mit Vorsicht klinisch verwendet werden.", { bold: true }));

  return content;
}

// ─── Kapitel 10: Multi-View Fusion (FULL) ───

function kapitel10() {
  const content = [];
  content.push(h1("Kapitel 10: Multi-View Fusion"));
  content.push(p("Die aesthetische Gesichtsanalyse aus einer einzelnen Aufnahme liefert stets nur eine partielle Sicht. Frontale Fotos erfassen die bilaterale Symmetrie, nicht aber die sagittale Projektion. Profilaufnahmen zeigen die Nasen- und Kinnprojektion, nicht aber die Mittelgesichtsbreite. Erst die systematische Kombination mehrerer Ansichten \u2014 frontal (0\u00b0), oblique (45\u00b0) und profil (90\u00b0) \u2014 ergibt ein vollstaendiges klinisches Bild."));
  content.push(p("Dieses Kapitel beschreibt den Multi-View-Fusion-Algorithmus des Aesthetic Biometrics Engine, der Messungen aus bis zu drei Ansichten confidence-gewichtet zusammenfuehrt, Widersprueche zwischen Views erkennt und eine konsolidierte Zonenanalyse produziert."));

  // 10.1
  content.push(h2("10.1 Designprinzipien der Fusion"));
  content.push(p("Drei Grundregeln bestimmen die Architektur der Multi-View Fusion:"));
  content.push(p("Regel 1 \u2014 Nur Landmark-Geometrie wird fusioniert: Blendshape-Koeffizienten (Muskelaktivierungen) werden NIEMALS ueber Views fusioniert. Der Grund: Zwischen den Aufnahmen aendert sich die Mimik des Patienten. Eine Blendshape-basierte Messung (z. B. Muskeltonus) ist nur innerhalb derselben Aufnahme gueltig.", { bold: true }));
  content.push(p("Regel 2 \u2014 Primaere View dominiert: Jede Zone hat eine primaere Ansicht, die klinisch am aussagekraeftigsten ist (z. B. frontal fuer Symmetrie, profil fuer E-Line). Sekundaere Views bestaetigen oder korrigieren, ueberstimmen aber nie die primaere Messung.", { bold: true }));
  content.push(p("Regel 3 \u2014 Widersprueche werden explizit gemeldet: Wenn zwei Views fuer dieselbe Metrik stark abweichende Werte liefern, wird dies nicht stillschweigend gemittelt, sondern als Contradiction markiert und die Confidence reduziert.", { bold: true }));

  // 10.2
  content.push(h2("10.2 Confidence-gewichtete Fusion"));
  content.push(p("Die Fusion einer Metrik folgt einer gewichteten Mittelung:"));
  content.push(p("Formel: fused_value = (\u03A3 value_i \u00d7 weight_i) / (\u03A3 weight_i)"));
  content.push(p("Die Gewichte sind:"));

  const wHeaders = ["View-Typ", "Basis-Gewicht", "Beschreibung"];
  const wWidths = [2400, 2400, 4560];
  const wRows = [
    ["Primary", "1,0", "Volle Gewichtung \u2014 klinisch massgebliche Ansicht fuer diese Zone"],
    ["Secondary", "0,7", "Reduzierte Gewichtung \u2014 Best\u00e4tigung der Prim\u00e4rmessung"],
  ];
  content.push(p("Tabelle 10.1: View-Gewichte", { bold: true }));
  content.push(makeTable(wHeaders, wRows, wWidths));

  content.push(p("Das effektive Gewicht eines sekundaeren Views wird zusaetzlich mit der Kalibrierungs-Confidence des jeweiligen Bildes multipliziert: effective_weight = 0,7 \u00d7 calibration_confidence."));
  content.push(p("Die Gesamt-Confidence einer fusionierten Messung steigt mit der Anzahl bestaetiegender Views: confidence = min(1,0; 0,8 + n_secondary \u00d7 0,1). Eine Messung aus nur einem View hat Confidence 0,8; bei Bestaetigung durch einen zweiten View steigt sie auf 0,9."));

  // 10.3
  content.push(h2("10.3 Widerspruchserkennung"));
  content.push(p("Ein Widerspruch (Contradiction) wird erkannt, wenn zwei Views fuer dieselbe Metrik Werte liefern, die ueber einem metrik-abhaengigen Schwellenwert auseinanderliegen:"));

  const cHeaders = ["Einheit", "Schwellenwert", "Beispiel"];
  const cWidths = [1600, 2400, 5360];
  const cRows = [
    ["mm", "> 3,0 mm", "Nasenbreite frontal 35 mm vs. oblique 39 mm \u2192 Contradiction"],
    ["Grad (\u00b0)", "> 10,0\u00b0", "Nasolabialwinkel profil 95\u00b0 vs. oblique 108\u00b0 \u2192 Contradiction"],
    ["Ratio", "> 0,15", "Lip Ratio frontal 1,6 vs. oblique 1,9 \u2192 Contradiction"],
    ["Score (0\u2013100)", "> 15 Punkte", "Symmetrie-Score frontal 88 vs. oblique 70 \u2192 Contradiction"],
  ];
  content.push(p("Tabelle 10.2: Widerspruchsschwellen nach Metrik-Einheit", { bold: true }));
  content.push(makeTable(cHeaders, cRows, cWidths));

  content.push(p("Wird ein Widerspruch erkannt, geschieht Folgendes:"));
  content.push(p("\u2022 Die Contradiction wird mit Zone, Metrik, beiden Werten und prozentualem Unterschied protokolliert.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Die Fusion-Confidence der betroffenen Messung wird um 40 % reduziert (Faktor 0,6).", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Die betroffene Metrik erhaelt das Flag contradiction = true.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Klinische Interpretation: Widersprueche entstehen haeufig durch suboptimale Bildqualitaet in einem der Views, durch leichte Kopfdrehungen zwischen Aufnahmen oder durch tatsaechlich asymmetrische 3D-Strukturen (z. B. einseitige Schwellung). In jedem Fall signalisieren sie dem Behandler, dass die Messung mit Vorsicht zu interpretieren ist."));

  // 10.4
  content.push(h2("10.4 Fusion-Zuordnung der Zonen"));
  content.push(p("Nicht alle 19 Zonen erfordern Multi-View Fusion. Profilspezifische Zonen (NP1, LP1, CH2) werden ausschliesslich aus der Profilansicht analysiert, da eine frontale Messung des Nasenprofils oder der Lippenprojektion klinisch nicht sinnvoll ist."));

  const fHeaders = ["Zone-ID", "Zone", "Primaere View", "Sekundaere Views", "Fusion"];
  const fWidths = [1000, 2400, 1600, 2200, 1160];
  const fRows = [
    ["T1", "Temporal", "oblique", "\u2014", "Nein"],
    ["Bw1", "Brow Lateral", "frontal", "oblique", "Ja"],
    ["Bw2", "Glabella", "frontal", "\u2014", "Nein"],
    ["Ck1", "Zygomatic Arch", "oblique", "frontal", "Ja"],
    ["Ck2", "Zygomatic Eminence", "frontal", "oblique", "Ja"],
    ["Ck3", "Mid-Cheek", "oblique", "frontal", "Ja"],
    ["It1", "Tear Trough", "frontal", "oblique", "Ja"],
    ["NLF", "Nasolabialfalte", "oblique", "frontal", "Ja"],
    ["Lp1", "Upper Lip", "frontal", "\u2014", "Nein"],
    ["Lp2", "Lower Lip", "frontal", "\u2014", "Nein"],
    ["ML1", "Marionette", "frontal", "oblique", "Ja"],
    ["Jw1", "Pre-jowl Sulcus", "frontal", "oblique", "Ja"],
    ["Jw2", "Jawline", "frontal", "oblique", "Ja"],
    ["Ch1", "Pogonion (Kinn)", "frontal", "profil", "Ja"],
    ["NP1", "Nasal Profile", "profil", "\u2014", "Nein"],
    ["LP1", "Lip Projection", "profil", "\u2014", "Nein"],
    ["CH2", "Chin-Neck Angle", "profil", "\u2014", "Nein"],
    ["Fw1", "Forehead", "frontal", "\u2014", "Nein"],
    ["Pc1", "Perioral", "frontal", "\u2014", "Nein"],
  ];
  content.push(p("Tabelle 10.3: Fusion-Konfiguration aller 19 Zonen", { bold: true }));
  content.push(makeTable(fHeaders, fRows, fWidths));

  content.push(p("KLINISCHER HINWEIS: Die Fusion funktioniert auch bei partiellen Daten. Wenn nur ein frontales und ein Profilbild vorliegen (ohne Oblique), werden die oblique-abhaengigen Zonen (T1, Ck1, Ck3, NLF) nur aus dem verfuegbaren Material analysiert, mit entsprechend reduzierter Confidence. Dies ermoeglicht flexible klinische Workflows, in denen nicht immer alle drei Standardaufnahmen verfuegbar sind.", { bold: true }));

  return content;
}

// ─── Kapitel 12: Zone-zu-Produkt-Matching (FULL) ───

function kapitel12() {
  const content = [];
  content.push(h1("Kapitel 12: Zone-zu-Produkt-Matching"));
  content.push(p("Die Ueberfuehrung einer zonenbasierten Diagnose in konkrete Produktempfehlungen erfordert ein strukturiertes Regelwerk, das rheologische Produkteigenschaften mit anatomischen Anforderungen abgleicht. Der Aesthetic Biometrics Engine verfuegt ueber eine integrierte Produktdatenbank mit 14 Produkten aus 6 Kategorien, die systematisch den 19 Behandlungszonen zugeordnet werden."));
  content.push(p("Dieses Kapitel beschreibt die Produktkategorien, ihre rheologischen Eigenschaften, die Zuordnungslogik und die zonenspezifischen Empfehlungen."));

  // 12.1
  content.push(h2("12.1 Produktkategorien und Rheologie"));
  content.push(p("Die sechs Produktkategorien spiegeln die klinische Klassifikation aesthetischer Injektabilia wider:"));

  const catHeaders = ["Kategorie", "Beschreibung", "G\u2019 (Pa)", "Typische Anwendung"];
  const catWidths = [2200, 3200, 1200, 2760];
  const catRows = [
    ["HA Deep", "Hochviskoese Hyaluronsaeure", "400\u2013600", "Tiefe Volumenaugmentation, Knochenersatz"],
    ["HA Medium", "Mittlere Viskositaet", "150\u2013300", "Konturierung, Stuetzstruktur"],
    ["HA Soft", "Weiche Hyaluronsaeure", "50\u2013100", "Lippen, feine Linien, Tr\u00e4nental"],
    ["Non-HA Volumizer", "CaHA, PLLA Biostimulatoren", "\u2014", "Kollagenstimulation, tiefe Volumenrestauration"],
    ["Neurotoxin", "Botulinumtoxin Typ A", "\u2014", "Muskelrelaxation, dynamische Falten"],
    ["Skin Booster", "Hydratation, Hautqualitaet", "\u2014", "Hauttextur, Feuchtigkeit, Elastizitaet"],
  ];
  content.push(p("Tabelle 12.1: Produktkategorien", { bold: true }));
  content.push(makeTable(catHeaders, catRows, catWidths));

  content.push(p("Der elastische Modul G\u2019 (gesprochen \u201eG-Prime\u201c) ist der zentrale rheologische Parameter: Er beschreibt die Festigkeit eines Gels unter Belastung. Je hoeher G\u2019, desto steifer das Produkt und desto staerker die Lift-Kapazitaet. Regionen wie das Jochbein (Ck1/Ck2) erfordern hohe G\u2019-Werte, waehrend Lippen (Lp1/Lp2) weiche Produkte benoetigen."));

  // 12.2
  content.push(h2("12.2 Injektionstechniken und Injektionsebenen"));
  content.push(p("Jede Zonenempfehlung umfasst neben dem Produkt auch die empfohlene Injektionstechnik und -tiefe:"));

  const techHeaders = ["Technik", "Beschreibung", "Typische Zonen"];
  const techWidths = [2400, 3800, 3160];
  const techRows = [
    ["Bolus", "Einzeldepot in der Tiefe, punktuelles Volumen", "Ck1, Ck2, Ch1 (supraperiostal)"],
    ["Linear Threading", "Lineare Deposition beim Zurueckziehen", "NLF, ML1, Jawline"],
    ["Serial Puncture", "Mehrere kleine Depots in Reihe", "Lippen, Perioral"],
    ["Fan", "Faecherfoermige Verteilung von einem Einstichpunkt", "Temporal, Mid-Cheek"],
    ["Microdroplet", "Superfizielle Mikro-Injektionen", "Tear Trough, Skin Booster"],
    ["BAP (Bio-Aesthetic Points)", "Standardisierte Injektionspunkte nach de Maio", "Ck2, Jw1, Jw2"],
  ];
  content.push(p("Tabelle 12.2: Injektionstechniken", { bold: true }));
  content.push(makeTable(techHeaders, techRows, techWidths));

  const depthHeaders = ["Ebene", "Tiefe", "Typische Produkte"];
  const depthWidths = [2800, 3200, 3360];
  const depthRows = [
    ["Supraperiostal", "Auf dem Knochen", "HA Deep, CaHA (Volify, Radiesse)"],
    ["Tief subkutan", "Tiefes Fettgewebe", "HA Deep/Medium, Sculptra"],
    ["Subkutan", "Oberfl\u00e4chliches Fettgewebe", "HA Medium (Voluma, Volift)"],
    ["Subdermal", "Unter der Dermis", "HA Soft (Volbella, Volite)"],
    ["Intradermal", "In der Dermis", "Skin Booster (Profhilo, Volite)"],
    ["Intramuskul\u00e4r", "Im Muskel", "Neurotoxin (Botox, Dysport)"],
  ];
  content.push(p("Tabelle 12.3: Injektionsebenen", { bold: true }));
  content.push(makeTable(depthHeaders, depthRows, depthWidths));

  // 12.3
  content.push(h2("12.3 Zonenspezifisches Produkt-Matching"));
  content.push(p("Die Zuordnungslogik folgt dem Prinzip: anatomische Anforderung \u2192 rheologische Eignung \u2192 Produktempfehlung. Fuer jede Zone werden passende Produkte, Techniken, Injektionsebene und Volumenbereiche spezifiziert."));
  content.push(p("Beispielhafte Zuordnungen:", { bold: true }));

  const matchHeaders = ["Zone", "Kategorie", "Produkte", "Technik", "Volumen/Seite"];
  const matchWidths = [1200, 1400, 2800, 2000, 1960];
  const matchRows = [
    ["T1 Temporal", "Non-HA", "Radiesse, Sculptra", "Fan", "0,5\u20131,5 ml"],
    ["Ck2 Zygoma", "HA Deep", "Volux, Voluma", "Bolus/BAP", "0,5\u20131,5 ml"],
    ["It1 Tear Trough", "HA Soft", "Volbella, Belotero Soft", "Microdroplet", "0,2\u20130,5 ml"],
    ["Lp1 Upper Lip", "HA Soft", "Volbella, Juvederm Smile", "Serial Puncture", "0,3\u20130,8 ml"],
    ["Jw2 Jawline", "HA Deep", "Volux", "Linear/BAP", "0,5\u20132,0 ml"],
    ["Ch1 Kinn", "HA Deep", "Volux, Voluma", "Bolus", "0,5\u20131,5 ml"],
  ];
  content.push(p("Tabelle 12.4: Beispielhafte Zone-zu-Produkt-Zuordnungen", { bold: true }));
  content.push(makeTable(matchHeaders, matchRows, matchWidths));

  content.push(p("Das System empfiehlt Volumenranges (Minimum bis Maximum pro Seite), die auf publizierten Konsensus-Empfehlungen und klinischer Erfahrung basieren. Die Angabe als Range statt als fester Wert respektiert die individuelle klinische Entscheidung des Behandlers."));

  // 12.4
  content.push(h2("12.4 Vaskul\u00e4res Risikoprofil"));
  content.push(p("Bestimmte Zonen sind als vaskul\u00e4re High-Risk-Zonen klassifiziert, in denen die Gefahr einer intravasal\u00e4ren Injektion erh\u00f6ht ist. Das System kennzeichnet diese Zonen automatisch mit Sicherheitshinweisen:"));
  content.push(p("\u2022 Tear Trough (It1): A./V. angularis, Infraorbitalarterie. Hoechstes Blindheitsrisiko.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Nasal Profile (NP1): A. dorsalis nasi, laterale Nasalarterie. Risiko der Nasenspitzennekrose.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Glabella (Bw2): A. supratrochlearis, Endast der A. ophthalmica. Blindheitsrisiko bei retrograder Embolisation.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("KLINISCHER HINWEIS: Die Produkt-Matching-Engine ersetzt nicht das klinische Urteil des Behandlers. Sie bietet eine evidenzbasierte Orientierung, die der Behandler auf Basis seiner Erfahrung, der individuellen Patientenanatomie und der Patientenwuensche anpassen muss.", { bold: true }));

  return content;
}

// ─── Kapitel 13: Klinische Priorisierung (FULL) ───

function kapitel13() {
  const content = [];
  content.push(h1("Kapitel 13: Klinische Priorisierung"));
  content.push(p("Nach der zonenbasierten Analyse und dem Produkt-Matching steht der Behandler vor der Frage: Welche Zone wird zuerst behandelt? Und kann alles in einer Sitzung erfolgen? Die klinische Priorisierung des Treatment Plan Generators folgt einem strukturierten Algorithmus, der Schweregrad, anatomische Hierarchie und Sicherheitsgrenzen kombiniert."));

  // 13.1
  content.push(h2("13.1 Severity-basierte Klassifikation"));
  content.push(p("Jede Zone erhaelt durch die Zonenanalyse einen Severity-Score (0\u201310). Dieser Score wird in drei Behandlungskategorien unterteilt:"));

  const sevHeaders = ["Kategorie", "Severity-Range", "Bedeutung", "Anzeigefarbe"];
  const sevWidths = [2400, 1800, 3800, 1360];
  const sevRows = [
    ["Primary Concern", "\u2265 3,0", "Klinisch relevante Abweichung, Behandlung empfohlen", "Rot"],
    ["Secondary Concern", "1,0 \u2013 2,9", "Subklinisch, bei Patientenwunsch behandelbar", "Gelb"],
    ["Keine Behandlung", "< 1,0", "Innerhalb der Norm, keine Indikation", "Gruen"],
  ];
  content.push(p("Tabelle 13.1: Severity-Klassifikation", { bold: true }));
  content.push(makeTable(sevHeaders, sevRows, sevWidths));

  content.push(p("Nur Zonen mit Severity \u2265 1,0 werden in den Behandlungsplan aufgenommen. Die Unterscheidung zwischen Primary und Secondary bestimmt die Reihenfolge und Dringlichkeit."));

  // 13.2
  content.push(h2("13.2 Strukturelle Hierarchie"));
  content.push(p("Die klinische Logik der aesthetischen Medizin folgt dem Prinzip: Fundament vor Detail. Strukturelle Zonen (Knochen-nahe Volumisierung) werden vor Detail-Zonen (oberflaechliche Korrekturen) behandelt, da die strukturelle Grundlage die Ergebnisse der Detailkorrekturen beeinflusst."));
  content.push(p("Beispiel: Eine Lippenaugmentation (Lp1) ohne vorherige Mittelgesichtsrestauration (Ck2/Ck3) kann ein unharmonisches Ergebnis produzieren, da das Lippenergebnis auf einem eingesunkenen Mittelgesicht \u201esitzt\u201c."));
  content.push(p("Die strukturelle Prioritaet wird durch eine 5-stufige Hierarchie kodiert:"));

  const prioHeaders = ["Priorit\u00e4t", "Typ", "Zonen (Beispiele)", "Behandlungslogik"];
  const prioWidths = [1200, 1800, 3000, 3360];
  const prioRows = [
    ["1 (h\u00f6chste)", "Strukturell", "Ck1, Ck2, Ch1, Jw2", "Knochen-nahe Volumisierung als Fundament"],
    ["2", "Semi-strukturell", "Ck3, Jw1, ML1", "Tiefes Fettgewebe-Support"],
    ["3", "Medium", "NLF, T1, Bw1, Fw1", "Regionale Korrekturen"],
    ["4", "Detail", "Lp1, Lp2, It1, Pc1", "Oberflaechliche Verfeinerung"],
    ["5 (niedrigste)", "Toxin-only", "Bw2, Fw1 (dynamisch)", "Neurotoxin, kein Volumenbedarf"],
  ];
  content.push(p("Tabelle 13.2: Strukturelle Priorit\u00e4tshierarchie", { bold: true }));
  content.push(makeTable(prioHeaders, prioRows, prioWidths));

  // 13.3
  content.push(h2("13.3 Composite Priority Score"));
  content.push(p("Die tatsaechliche Behandlungsreihenfolge ergibt sich aus einem kombinierten Score:"));
  content.push(p("priority_score = severity \u00d7 2,0 + structural_weight"));
  content.push(p("wobei structural_weight = 6 \u2212 structural_priority (also Prioritaet 1 \u2192 Gewicht 5, Prioritaet 5 \u2192 Gewicht 1)."));
  content.push(p("Dieses Modell stellt sicher, dass:"));
  content.push(p("\u2022 Bei gleichem Schweregrad die strukturellere Zone zuerst behandelt wird.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Ein hoher Schweregrad (z. B. 8/10) in einer Detail-Zone immer noch vor einem niedrigen Schweregrad (z. B. 3/10) in einer strukturellen Zone kommt.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Die Severity den dominanten Faktor darstellt (Faktor 2,0), waehrend die strukturelle Ordnung als Tie-Breaker wirkt."));

  // 13.4
  content.push(h2("13.4 Sitzungsplanung"));
  content.push(p("Der Treatment Plan Generator verteilt die priorisierten Concerns auf ein oder mehrere Behandlungssitzungen. Dabei gelten zwei Sicherheitsgrenzen:"));

  const limHeaders = ["Parameter", "Grenzwert", "Begr\u00fcndung"];
  const limWidths = [3200, 2200, 3960];
  const limRows = [
    ["Max. Filler-Volumen/Sitzung", "6,0 ml", "Konservatives Sicherheitslimit, reduziert Schwellungsrisiko"],
    ["Max. Zonen/Sitzung", "6 Zonen", "Praktisches Limit f\u00fcr Behandlungsdauer und Patientenkomfort"],
    ["Sitzungsintervall", "4 Wochen", "Standardintervall f\u00fcr Nachbehandlung und Gewebeerholung"],
  ];
  content.push(p("Tabelle 13.3: Sitzungslimits", { bold: true }));
  content.push(makeTable(limHeaders, limRows, limWidths));

  content.push(p("Die Zuordnung erfolgt sequentiell: Die nach Priority Score sortierten Concerns werden der Reihe nach auf Sessions verteilt. Sobald eine Session das Volumenlimit oder das Zonenlimit erreicht, wird eine neue Session eroeffnet."));
  content.push(p("Session 1 Focus: Structural foundation \u2014 strukturelle und semi-strukturelle Zonen mit hoechster Prioritaet."));
  content.push(p("Session 2+ Focus: Refinement \u2014 Detail-Zonen und sekundaere Concerns."));
  content.push(p("Neurotoxin-Behandlungen koennen parallel zu Filler-Behandlungen in derselben Sitzung erfolgen und zaehlen nicht gegen das Volumenlimit."));

  // 13.5
  content.push(h2("13.5 Kontraindikationspruefung"));
  content.push(p("Vor der finalen Planausgabe durchlaeuft jeder Behandlungsvorschlag eine automatisierte Kontraindikationspruefung (vgl. Kapitel 14). Drei Prueftypen sind implementiert:"));
  content.push(p("\u2022 Extreme Asymmetrie: Asymmetrien > 15 % koennen auf Pathologien (Fazialisparese, Kieferfehlstellung) hinweisen und erfordern fachaerztliche Abklaerung vor kosmetischer Behandlung.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Vaskul\u00e4res Risiko: High-Risk-Zonen (It1, NP1, Bw2) erhalten automatisch Sicherheitshinweise zu Gef\u00e4ssanatomie und Aspirationspflicht.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 \u00dcberbehandlung: Das System warnt, wenn viele Zonen gleichzeitig hohe Severity-Werte zeigen (\u2265 5 Zonen mit Severity \u2265 5), da dies auf systemische Faktoren (starkes Altern, Gewichtsverlust) hindeuten kann.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("KLINISCHER HINWEIS: Der Behandlungsplan ist eine evidenzbasierte Empfehlung, kein Behandlungsprotokoll. Die finale Entscheidung ueber Produkt, Volumen, Technik und Zeitplan obliegt dem Behandler auf Basis seiner klinischen Expertise und der individuellen Patientenanamnese.", { bold: true }));

  return content;
}

// ─── Kapitel 1: Einfuehrung in die aesthetische Gesichtsanalyse (FULL) ───

function kapitel1() {
  const content = [];
  content.push(h1("Kapitel 1: Einfuehrung in die aesthetische Gesichtsanalyse"));
  content.push(p("Die aesthetische Gesichtsanalyse hat sich in den vergangenen Jahrzehnten von einer rein subjektiven, erfahrungsbasierten Beurteilung zu einer zunehmend standardisierten, messwertgestuetzten Disziplin entwickelt. Diese Transformation wurde durch drei parallele Entwicklungen angetrieben: die Etablierung standardisierter Fotografieprotokolle, die mathematische Formalisierung aesthetischer Ideale und die juengste Integration kuenstlicher Intelligenz in die klinische Diagnostik."));
  content.push(p("Das vorliegende Werk beschreibt den Aesthetic Biometrics Engine — ein KI-gestuetztes System, das aus standardisierten Fotografien (frontal, oblique, profil) biometrische Gesichtsmessungen extrahiert, 19 anatomische Behandlungszonen analysiert und evidenzbasierte Behandlungsempfehlungen generiert. Es richtet sich an aesthetisch taetige Aerzte, die ihre klinische Entscheidungsfindung durch objektive Daten unterstuetzen moechten."));

  // 1.1 Historischer Kontext
  content.push(h2("1.1 Historischer Kontext"));
  content.push(p("Die systematische Vermessung des menschlichen Gesichts hat eine lange Tradition. Bereits in der Renaissance definierte Leonardo da Vinci Proportionsregeln fuer das ideale Gesicht, basierend auf der Aufteilung in horizontale Drittel und vertikale Fuenftel. Diese Konzepte wurden im 20. Jahrhundert durch die Kephalometrie weiterentwickelt."));
  content.push(p("Wegweisende Arbeiten in der aesthetischen Gesichtsvermessung:", { bold: true }));
  content.push(p("\u2022 Ricketts (1968/1982): Einfuehrung der Aesthetic E-Line und des Divine Proportion Konzepts (Goldener Schnitt, Phi = 1,618). Diese Arbeiten legten den Grundstein fuer die mathematische Beschreibung aesthetischer Harmonie.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Farkas (1994): Umfassende anthropometrische Normwerte fuer ueber 100 Gesichtsmessungen an verschiedenen ethnischen Populationen. Erstmals wurden populationsspezifische Referenzwerte fuer die klinische Praxis verfuegbar.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 De Maio (2021): Einfuehrung der MD Codes\u2122 \u2014 ein zonenbasiertes Behandlungsschema, das anatomische Regionen mit spezifischen Injektionstechniken und Produktempfehlungen verknuepft. Dieses Konzept inspirierte das 19-Zonen-System des vorliegenden Systems.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Der entscheidende Paradigmenwechsel der letzten Jahre liegt in der Automatisierung der Gesichtsvermessung. Waehrend klassische Kephalometrie manuelle Punktmarkierung auf Roentgenbildern erforderte, ermoeglichen moderne Computer-Vision-Systeme die automatische Erkennung von bis zu 478 Gesichtspunkten (Landmarks) aus einfachen Fotografien \u2014 in Echtzeit und mit einer Genauigkeit, die manuelle Messungen in vielen Parametern uebertrifft."));

  // 1.2 Standardisierte Fotografie
  content.push(h2("1.2 Standardisierte Fotografie"));
  content.push(p("Die Grundlage jeder biometrischen Gesichtsanalyse ist die standardisierte Fotodokumentation. Ohne reproduzierbare Aufnahmebedingungen sind Messungen nicht vergleichbar \u2014 weder zwischen verschiedenen Patienten noch im Vorher-Nachher-Vergleich desselben Patienten. Das System arbeitet mit drei standardisierten Aufnahmewinkel:"));

  content.push(h3("1.2.1 Die drei Standardansichten"));
  const viewHeaders = ["Ansicht", "Winkel", "Primaere Analysebereiche", "Klinischer Fokus"];
  const viewWidths = [1500, 1200, 3300, 3360];
  const viewRows = [
    ["Frontal", "0\u00b0", "Symmetrie, Proportionen (Drittel/Fuenftel), Lippen, Nasolabialfalte", "Symmetrieabweichungen, Brauenposition, Lippenverhaeltnis"],
    ["Oblique", "45\u00b0", "Ogee-Kurve, Volumen (Temporal, Wange, Jowl), Traenental", "Mittelgesichtsvolumen, Konturdefizite, Altersveraenderungen"],
    ["Profil", "90\u00b0", "E-Linie, NLA, Kinnprojektion, Nasenruecken, Kinn-Hals-Winkel", "Lippenposition, Nasenform, Kinnharmonie"],
  ];
  content.push(p("Tabelle 1.1: Die drei Standardansichten der aesthetischen Fotodokumentation", { bold: true }));
  content.push(makeTable(viewHeaders, viewRows, viewWidths));

  content.push(h3("1.2.2 Aufnahmeprotokoll"));
  content.push(p("Fuer reproduzierbare Ergebnisse muessen folgende Bedingungen eingehalten werden:"));
  content.push(p("\u2022 Beleuchtung: Gleichmaessige, diffuse Ausleuchtung ohne harte Schatten. Idealerweise Ringblitz oder zwei symmetrisch positionierte Softboxen.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Hintergrund: Einfarbig, neutral (blau oder grau empfohlen), ohne ablenkende Elemente.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Kopfhaltung: Natuerliche Kopfposition (Natural Head Position, NHP). Der Patient blickt geradeaus auf einen Fixpunkt in Augenhoehe. Die Frankfurter Horizontale (Tragion\u2013Infraorbitale) sollte horizontal verlaufen.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Gesichtsausdruck: Neutral, entspannt. Kein Laecheln, keine Stirnrunzeln, Lippen leicht geschlossen.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Aufloesung: Mindestens 640\u00d7480 Pixel; empfohlen 1024\u00d71024 oder hoeher.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Das System prueft diese Kriterien automatisch ueber die Quality Gate (vgl. Kapitel 16): Aufloesung, Helligkeit, Kontrast und Schaerfe werden gemessen, die Kopfhaltung wird ueber Head-Pose-Estimation validiert, und der Gesichtsausdruck wird ueber Blendshape-Analyse auf Neutralitaet geprueft."));

  content.push(h3("1.2.3 Bildvorverarbeitung"));
  content.push(p("Vor der Analyse durchlaeuft jedes Bild eine automatisierte Vorverarbeitungskette (Image Preprocessor):"));
  content.push(p("1. EXIF-Orientierung korrigieren: Smartphone-Kameras speichern die Orientierung haeufig als Metadatum statt die Pixel zu rotieren. Das System liest das EXIF-Tag und rotiert das Bild entsprechend."));
  content.push(p("2. Gesichtszentrierter Zuschnitt: Ein quadratischer Bildausschnitt wird um das erkannte Gesicht herum erzeugt. Dies eliminiert Verzeichnungen am Bildrand, die bei Smartphone-Weitwinkellinsen auftreten (Barrel Distortion)."));
  content.push(p("3. Standardgroesse: Das Bild wird auf 1024\u00d71024 Pixel skaliert \u2014 die optimale Groesse fuer die Landmark-Erkennung."));
  content.push(p("Diese Vorverarbeitung stellt sicher, dass die nachfolgende Analyse unabhaengig von Kameratyp, Bildgroesse und Aufnahmeformat konsistente Ergebnisse liefert."));

  // 1.3 KI-gestuetzte Analyse
  content.push(h2("1.3 KI-gestuetzte Analyse"));
  content.push(p("Der Aesthetic Biometrics Engine nutzt maschinelles Lernen fuer die Gesichtserkennung und kombiniert dies mit regelbasierter medizinischer Logik fuer die klinische Interpretation. Dieser hybride Ansatz vereint die Staerken beider Paradigmen:"));

  content.push(h3("1.3.1 Maschinelles Lernen: Landmark-Erkennung"));
  content.push(p("Die Erkennung der 478 Gesichtspunkte (Landmarks) erfolgt ueber ein vortrainiertes neuronales Netz (MediaPipe Face Landmarker). Dieses Modell wurde auf Millionen von Gesichtern trainiert und erkennt anatomische Strukturen mit subpixel-genauer Praezision. Zusaetzlich liefert es:"));
  content.push(p("\u2022 52 Blendshapes: Numerische Koeffizienten (0,0\u20131,0) fuer einzelne Gesichtsmuskelgruppen (z.\u202fB. browDownLeft, mouthSmileRight). Diese ermoeglichen die Analyse des Muskeltonus in Ruhe \u2014 ein Indikator fuer Neurotoxin-Bedarf.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Transformation Matrix: Eine 4\u00d74-Matrix, aus der die Kopfhaltung (Yaw, Pitch, Roll) abgeleitet wird. Dies validiert, ob das Bild der angegebenen Ansicht entspricht.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 3D-Koordinaten: Jeder Landmark hat neben x/y auch eine z-Koordinate (Tiefe), was volumetrische Analysen wie die Ogee-Kurve ermoelicht.", { paragraphOpts: { indent: { left: 360 } } }));

  content.push(h3("1.3.2 Regelbasierte Medizinlogik"));
  content.push(p("Die klinische Interpretation der erkannten Landmarks erfolgt durch sechs spezialisierte Analyse-Engines:"));

  const engineHeaders = ["Engine", "Kapitel", "Analyseschwerpunkt"];
  const engineWidths = [2500, 1200, 5660];
  const engineRows = [
    ["Symmetrie-Engine", "Kap. 4", "Bilaterale Symmetrie auf 6 Achsen, pro-Zone Asymmetrie-Score, dynamische Asymmetrie"],
    ["Proportionen-Engine", "Kap. 5", "Gesichtsdrittel, Fuenftel, Goldener Schnitt, Lippenverhaeltnis"],
    ["Profil-Engine", "Kap. 6", "E-Linie, Nasolabialwinkel, Kinnprojektion, Nasenrueckenprofil"],
    ["Volumen-Engine", "Kap. 7", "Ogee-Kurve, Temporal Hollowing, Traenental, Pre-Jowl Sulcus"],
    ["Aging-Engine", "Kap. 8", "Muskeltonus-Profil, gravitationelle Drift, periobitale Alterung"],
    ["Zone Analyzer", "Kap. 9\u201310", "Orchestrierung aller Engines \u2192 19-Zonen-Report mit Severity"],
  ];
  content.push(p("Tabelle 1.2: Die sechs Analyse-Engines", { bold: true }));
  content.push(makeTable(engineHeaders, engineRows, engineWidths));

  content.push(h3("1.3.3 Vom Messwert zum Behandlungsplan"));
  content.push(p("Der wesentliche Unterschied dieses Systems zu reinen Vermessungswerkzeugen liegt in der klinischen Handlungsanleitung. Der Analysepfad verlaeuft in vier Stufen:"));
  content.push(p("1. Erkennung: 478 Landmarks + 52 Blendshapes + Head Pose aus 3 Bildern extrahieren."));
  content.push(p("2. Analyse: Sechs Engines berechnen medizinische Messwerte (mm, Grad, Scores)."));
  content.push(p("3. Zonenbewertung: Messwerte werden den 19 Behandlungszonen zugeordnet, Severity-Scores berechnet und nach klinischer Dringlichkeit sortiert."));
  content.push(p("4. Behandlungsplan: Fuer jede behandlungsbeduerftige Zone werden Produkte, Techniken, Volumina und Sicherheitshinweise empfohlen."));
  content.push(p("Dieses Kapitel gibt einen Ueberblick ueber den Gesamtansatz. Die folgenden Kapitel vertiefen jeden Aspekt: von der anatomischen Grundlage (Kapitel 2) ueber die Kalibrierung und Vermessung (Kapitel 3) bis hin zur Behandlungsplanung (Kapitel 11\u201314) und Ergebniskontrolle (Kapitel 15\u201316)."));

  return content;
}

// ─── Kapitel 2: Anatomische Grundlagen (FULL) ───

function kapitel2() {
  const content = [];
  content.push(h1("Kapitel 2: Anatomische Grundlagen"));
  content.push(p("Die sichere und effektive Anwendung von Fillern und Neurotoxinen setzt ein tiefgreifendes Verstaendnis der Gesichtsanatomie voraus. Dieses Kapitel beschreibt die vier anatomischen Schichten, die fuer die aesthetische Gesichtsanalyse und -behandlung relevant sind: das knoecherne Geruest mit den Retaining Ligaments, die Fettkompartimente, die vaskulaere Anatomie und die mimische Muskulatur. Das Verstaendnis dieser Strukturen ist entscheidend fuer die Interpretation der Analyseergebnisse und die sichere Umsetzung der Behandlungsempfehlungen."));

  // 2.1 Gesichtsknochen und Retaining Ligaments
  content.push(h2("2.1 Gesichtsknochen und Retaining Ligaments"));
  content.push(p("Das knoecherne Geruest bestimmt die dreidimensionale Grundform des Gesichts. Die relevanten Strukturen fuer die biometrische Analyse umfassen:"));

  content.push(h3("2.1.1 Knoecherne Referenzpunkte"));
  const boneHeaders = ["Struktur", "Landmark-Region", "Klinische Bedeutung"];
  const boneWidths = [2200, 2500, 4660];
  const boneRows = [
    ["Os frontale (Stirnbein)", "Glabella, Supraorbitalrand", "Definiert Stirnkontur und Brauenposition; Basis fuer Zone Fo1, Bw1, Bw2"],
    ["Os zygomaticum (Jochbein)", "Zygomatic Arch, Eminentia", "Breitester Punkt des Mittelgesichts; Basis fuer Zonen Ck1, Ck2; bestimmt Ogee-Kurve"],
    ["Maxilla (Oberkiefer)", "Subnasale, Piriformis", "Traegt die Nasenbasis und beeinflusst den Nasolabialwinkel; Basis fuer Zonen Ns1, Pf1"],
    ["Mandibula (Unterkiefer)", "Pogonion, Gonion, Mentale", "Definiert Kinn und Jawline; Basis fuer Zonen Ch1, Jl1; bestimmt Profillinie"],
    ["Os nasale (Nasenbein)", "Nasion, Rhinion", "Nasenprofil und Nasofrontalwinkel; Basis fuer Zone Pf1"],
  ];
  content.push(p("Tabelle 2.1: Knoecherne Referenzpunkte und ihre klinische Zuordnung", { bold: true }));
  content.push(makeTable(boneHeaders, boneRows, boneWidths));

  content.push(h3("2.1.2 Retaining Ligaments"));
  content.push(p("Die Retaining Ligaments sind bindegewebige Verbindungen zwischen Periost und Dermis, die das Weichgewebe am Skelett fixieren. Mit zunehmender Laxitaet dieser Ligamente kommt es zur altersbedingten Gewebeptose \u2014 einem der Hauptindikatoren, die das System ueber den Gravitational-Drift-Score (vgl. Kapitel 8) erkennt."));
  content.push(p("Klinisch relevante Retaining Ligaments:", { bold: true }));
  content.push(p("\u2022 Orbicularis Retaining Ligament (ORL): Fixiert das Unterlid am Orbitarand. Laxitaet fuehrt zur Traenentalvertiefung (Zone Tt1) und Lower-Lid-Laxity.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Zygomatic Ligament: Verbindet den Jochbogen mit der Haut ueber dem Malar Fat Pad. Laxitaet verursacht die Abflachung der Wangenhoehe (Ck2) und vertieft die Nasolabialfalte (Ns1).", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Masseteric Ligament: Fixiert die Weichteile ueber dem M. masseter. Laxitaet traegt zur Jowl-Bildung bei (Zone Jw1).", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Mandibular Ligament: Am anterioren Unterkieferrand. Laxitaet fuehrt zur Marionettenfaltenvertiefung (Zone Mn1).", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Das System erkennt die Folgen dieser Ligament-Laxitaet indirekt ueber Landmark-Positionen und Volumendefizit-Scores. Eine direkte Darstellung der Ligamente ist auf Fotografien nicht moeglich \u2014 ihre Funktion wird ueber die resultierenden Weichgewebeveraenderungen erschlossen."));

  // 2.2 Fettkompartimente
  content.push(h2("2.2 Fettkompartimente"));
  content.push(p("Die Gesichtsfettkompartimente bilden die Grundlage fuer das Verstaendnis von Volumenverlust und Konturveraenderungen. Sie sind in tiefe (supraperiostale) und oberflaechliche (subkutane) Kompartimente gegliedert, die unabhaengig voneinander an Volumen verlieren."));

  content.push(h3("2.2.1 Tiefe Fettkompartimente"));
  content.push(p("\u2022 Deep Medial Cheek Fat (DMCF): Liegt direkt auf dem Oberkiefer, medial des Jochbeins. Volumenverlust fuehrt zur Vertiefung der Nasolabialfalte und des Traenentals. Betrifft primaer die Zonen Ck3, Ns1 und Tt1.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Sub-Orbicularis Oculi Fat (SOOF): Unterhalb des M. orbicularis oculi, ueber dem Jochbein. Volumenverlust fuehrt zur Abflachung der Wangenhoehe (Ck2) und verstaerkt das Traenental.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Buccal Fat Pad (Bichat-Fettkoerper): Zwischen Wangenmuskulatur und Masseter. Sein Volumen beeinflusst die Wangenbreite und den Buccal Corridor.", { paragraphOpts: { indent: { left: 360 } } }));

  content.push(h3("2.2.2 Oberflaechliche Fettkompartimente"));
  content.push(p("\u2022 Malar Fat Pad: Das oberflaechliche Wangenfettpolster. Seine kaudale Migration (Gravitational Drift) ist einer der sichtbarsten Alterungseffekte und fuehrt zur Nasolabialfaltenvertiefung. Die Volumen-Engine (Kapitel 7) erkennt diesen Effekt ueber die Ogee-Kurve und den Malar-Prominence-Ratio.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Temporal Fat Pad: Oberflaechliches und tiefes temporales Fett. Atrophie fuehrt zum Temporal Hollowing (Zone T1), einem fruehen Alterungszeichen.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Periorbital Fat: Komplex geschichtetes Fett um die Augenhohle. Pseudohernie oder Atrophie fuehrt zu Traenensaecken respektive Traenental (Zone Tt1).", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Das System quantifiziert Volumenverlust indirekt ueber Konturanalyse (Ogee-Kurve, Temporal-Depth, Tear-Trough-Depth) und ordnet die Ergebnisse den entsprechenden Zonen zu. Die Volumenscore-Berechnung (Kapitel 7) nutzt die z-Koordinaten der 3D-Landmarks, um Tiefenunterschiede zu erkennen, die auf Volumendefizite hindeuten."));

  // 2.3 Vaskulaere Anatomie und Danger Zones
  content.push(h2("2.3 Vaskulaere Anatomie und Danger Zones"));
  content.push(p("Die Kenntnis der Gesichtsgefaesse ist fuer die sichere Injektion von Fillern essentiell. Vaskulaere Komplikationen (Embolie, Kompression) gehoeren zu den schwerwiegendsten Risiken in der aesthetischen Medizin. Das System kennzeichnet Hochrisikozonen automatisch mit vaskulaeren Warnhinweisen (vgl. Kapitel 14)."));

  content.push(h3("2.3.1 Arterielle Versorgung"));
  content.push(p("Die Gesichtsdurchblutung erfolgt primaer ueber zwei Hauptgefaesse:"));
  content.push(p("\u2022 A. facialis: Verlaeuft ueber den Unterkieferrand, lateral der Nasolabialfalte nach cranial. Sie gibt die A. labialis superior und inferior ab (Versorgung der Lippen, Zone Lp1) und setzt sich als A. angularis fort (mediale Kanthusregion, Zone Tt1).", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 A. temporalis superficialis: Verlaeuft vor dem Ohr nach cranial in die Temporalregion (Zone T1). Sie gibt den R. zygomaticoorbicularis ab, der die laterale Periorbitalregion versorgt.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Zusaetzlich relevante Gefaesse:", { bold: true }));
  content.push(p("\u2022 A. dorsalis nasi: Verlaeuft auf dem Nasenruecken und ist die haeufigste Ursache vaskulaerer Komplikationen bei non-chirurgischer Rhinoplastik (Zone Pf1).", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 A. supratrochlearis/A. supraorbitalis: Versorgen die Glabellaregion (Zone Bw2) und die Stirn (Zone Fo1).", { paragraphOpts: { indent: { left: 360 } } }));

  content.push(h3("2.3.2 Vaskulaere Risikozonen im System"));
  content.push(p("Die Produktdatenbank (Kapitel 11) klassifiziert 8 der 19 Behandlungszonen als vaskulaere Risikozonen. Fuer diese Zonen werden automatisch Sicherheitshinweise generiert:"));
  const vascHeaders = ["Zone", "Name", "Gefaehrdetes Gefaess", "Risikoniveau"];
  const vascWidths = [800, 2500, 3200, 2860];
  const vascRows = [
    ["Tt1", "Traenental", "A. angularis, A. infraorbitalis", "Hoch"],
    ["Pf1", "Nasenprofil", "A. dorsalis nasi, A. angularis", "Sehr hoch"],
    ["Lp1", "Oberlippe", "A. labialis superior", "Hoch"],
    ["Bw2", "Glabella", "A. supratrochlearis", "Hoch"],
    ["Ns1", "Nasolabialfalte", "A. facialis", "Mittel"],
    ["Bw1", "Laterale Braue", "R. zygomaticoorbicularis", "Mittel"],
    ["T1", "Temporal", "A. temporalis superficialis", "Mittel"],
    ["Fo1", "Stirn", "A. supraorbitalis", "Mittel"],
  ];
  content.push(p("Tabelle 2.2: Vaskulaere Risikozonen des Systems", { bold: true }));
  content.push(makeTable(vascHeaders, vascRows, vascWidths));
  content.push(p("Die detaillierte Beschreibung der vaskulaeren Sicherheitsmechanismen findet sich in Kapitel 14 (Sicherheit und Kontraindikationen)."));

  // 2.4 Mimische Muskulatur
  content.push(h2("2.4 Mimische Muskulatur"));
  content.push(p("Die mimische Muskulatur (Gesichtsausdruck-Muskulatur) ist fuer zwei Aspekte der Analyse relevant: (1) die Neurotoxin-Indikation bei Hyperaktivitaet und (2) die Blendshape-basierte Muskeltonusanalyse in Ruhe (vgl. Kapitel 8). Im Gegensatz zur Kaumuskulatur inseriert die mimische Muskulatur direkt in der Haut, was ihre Auswirkungen auf die Gesichtsoberflaeche erklaert."));

  content.push(h3("2.4.1 Oberes Gesichtsdrittel"));
  content.push(p("\u2022 M. frontalis: Stirnheber, erzeugt horizontale Stirnfalten. Einziger Brauenheber. Der Blendshape browInnerUp korreliert mit seiner Aktivitaet. WICHTIG: Isolierte Neurotoxin-Behandlung ohne gleichzeitige Glabellabehandlung kann zur Brauenptosis fuehren (vgl. Zone Fo1, Kapitel 14.4).", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 M. corrugator supercilii: Brauenrunzler, erzeugt vertikale Glabellafalten ('11-Linien'). Die Blendshapes browDownLeft/Right messen seine Aktivitaet. Haeufigste Neurotoxin-Indikation (Zone Bw2).", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 M. procerus: Zieht die Glabella nach kaudal, erzeugt horizontale Nasenwurzelfalten. Wird gemeinsam mit dem Corrugator behandelt.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 M. orbicularis oculi: Ringmuskel um das Auge, verantwortlich fuer Kraehenfuesse und Squint-Muster. Die Blendshapes eyeSquintLeft/Right messen seinen Tonus.", { paragraphOpts: { indent: { left: 360 } } }));

  content.push(h3("2.4.2 Mittleres und unteres Gesichtsdrittel"));
  content.push(p("\u2022 M. zygomaticus major/minor: Heben den Mundwinkel nach lateral-cranial (Laecheln). Die Blendshapes mouthSmileLeft/Right korrelieren mit ihrer Aktivitaet. Asymmetrische Aktivierung in Ruhe kann auf eine periphere Fazialisparese hindeuten (vgl. Kapitel 14.3).", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 M. levator labii superioris: Hebt die Oberlippe. Beteiligt an der Nasolabialfaltentiefe.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 M. orbicularis oris: Ringmuskel der Lippen. Lip-Flip-Indikation bei Hyperaktivitaet (2\u20136 Units Neurotoxin, Zone Lp1). Der Blendshape mouthPucker misst seinen Tonus.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 M. depressor anguli oris (DAO): Zieht den Mundwinkel nach kaudal, verursacht den mueden, traurigen Ausdruck. Beteiligt an der Marionettenfaltenbildung (Zone Mn1).", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 M. mentalis: Hebt das Kinnpolster ('Kinngruebelchen-Muskel'). Hyperaktivitaet erzeugt eine unruhige Kinnoberflaeche (Peau d'orange).", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 M. platysma: Breiter Halsmuskel, der im Alter Banding und den Turkey-Neck-Effekt verursacht. Beeinflusst den Cervicomental Angle (Zone Pf3).", { paragraphOpts: { indent: { left: 360 } } }));

  content.push(h3("2.4.3 Integration in das Analysesystem"));
  content.push(p("Das System nutzt die Blendshape-Koeffizienten als indirekten Indikator fuer den Muskeltonus in Ruhe. Die Aging-Engine (Kapitel 8) berechnet einen Muskeltonus-Score pro Zone, der die Summe der aktivitaetsgewichteten Blendshape-Koeffizienten darstellt. Ein erhoehter Tonus in Ruhe (z.\u202fB. browDownLeft > 0,2 ohne bewusstes Stirnrunzeln) deutet auf eine Neurotoxin-Indikation hin."));
  content.push(p("WICHTIG: Blendshape-Werte sind immer nur pro Aufnahme gueltig und werden NIEMALS ueber verschiedene Ansichten (frontal, oblique, profil) fusioniert. Nur die geometrischen Landmark-Positionen werden im Multi-View-Fusion-Prozess (Kapitel 10) zusammengefuehrt.", { bold: true }));

  return content;
}

// ─── Kapitel 15: Before/After-Vergleich (FULL) ───

function kapitel15() {
  const content = [];
  content.push(h1("Kapitel 15: Before/After-Vergleich"));
  content.push(p("Die objektive Messung von Behandlungsergebnissen ist eine der wichtigsten Funktionen des Aesthetic Biometrics Engine. Waehrend Vorher-Nachher-Fotos in der aesthetischen Medizin allgegenwaertig sind, fehlt haeufig eine systematische, quantitative Auswertung. Die Comparison Engine schliesst diese Luecke, indem sie zwei Zone-Reports (pre-treatment und post-treatment) systematisch vergleicht und den Behandlungserfolg in messbaren Kennzahlen ausdrueckt."));
  content.push(p("Dieses Kapitel beschreibt die Methodik des Before/After-Vergleichs: die Delta-Berechnung pro Zone, den Improvement Score, die Status-Klassifikation und die Heatmap-Visualisierung. Die Engine ist als reine Berechnungslogik implementiert \u2014 ohne Datenbankabhaengigkeit \u2014 und kann sowohl fuer einzelne Behandlungen als auch fuer longitudinale Behandlungsverlaeufe eingesetzt werden."));

  // 15.1 Grundprinzip
  content.push(h2("15.1 Grundprinzip des Vergleichs"));
  content.push(p("Der Vergleich basiert auf der einfachen Idee, zwei vollstaendige Gesichtsanalysen (Zone-Reports) desselben Patienten nebeneinanderzustellen und die Differenzen systematisch auszuwerten. Jeder Zone-Report enthaelt pro Zone:"));
  content.push(p("\u2022 Severity-Score (0\u201310): Wie stark ist die Zone behandlungsbeduerftig?", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Einzelmessungen: Konkrete biometrische Messwerte (in mm, Grad oder Scores)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Aesthetic Score (0\u2013100): Gesamtaesthetischer Score ueber alle 19 Zonen", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Der Vergleich erzeugt fuer jede Zone ein ZoneDelta-Objekt, das die Veraenderung zwischen Pre und Post beschreibt. Aus diesen Deltas werden der Gesamtverbesserungswert und die Heatmap-Visualisierung abgeleitet."));
  content.push(p("API-Endpunkt: POST /api/v2/compare erwartet zwei Assessment-IDs (pre_assessment_id, post_assessment_id), laedt die zugehoerigen Zone-Reports aus Supabase und fuehrt den Vergleich durch. Das Ergebnis wird als ComparisonResponse zurueckgegeben und optional in der Tabelle treatment_comparisons persistiert.", { bold: true }));

  // 15.2 Delta-Berechnung
  content.push(h2("15.2 Delta-Berechnung pro Zone"));
  content.push(p("Fuer jede der 19 Zonen wird ein ZoneDelta berechnet, das folgende Felder enthaelt:"));
  const deltaHeaders = ["Feld", "Berechnung", "Interpretation"];
  const deltaWidths = [2800, 3000, 3560];
  const deltaRows = [
    ["severity_delta", "post_severity \u2212 pre_severity", "Negativ = Verbesserung, Positiv = Verschlechterung"],
    ["severity_improvement_pct", "(\u2212severity_delta / pre_severity) \u00d7 100", "Prozentuale Verbesserung relativ zum Ausgangswert"],
    ["measurement_deltas", "Pro Messwert: post_value \u2212 pre_value", "Detaillierte Veraenderung jedes einzelnen Messwerts"],
    ["status", "Klassifikation (siehe 15.3)", "improved / worsened / unchanged / resolved / new"],
  ];
  content.push(p("Tabelle 15.1: Felder des ZoneDelta-Objekts", { bold: true }));
  content.push(makeTable(deltaHeaders, deltaRows, deltaWidths));

  content.push(h3("15.2.1 Measurement-Level Deltas"));
  content.push(p("Zusaetzlich zum Severity-Delta werden die einzelnen Messwerte innerhalb jeder Zone verglichen. Fuer jeden Messwert, der in beiden Assessments vorhanden ist, wird berechnet:"));
  content.push(p("\u2022 delta: Absolute Differenz (post_value \u2212 pre_value)", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 delta_pct: Prozentuale Veraenderung relativ zum Pre-Wert", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 improved: Boolean \u2014 ob sich der Wert dem Idealbereich angenaehert hat", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Die Verbesserungsbeurteilung nutzt die Idealwertbereiche aus den Zonen-Definitionen (vgl. Kapitel 9). Wenn Idealwerte vorhanden sind, wird geprueft, ob der Post-Wert naeher am Idealmittelpunkt liegt als der Pre-Wert. Fuer Metriken ohne Idealbereich gelten typspezifische Heuristiken: Asymmetrie- und Deviations-Metriken verbessern sich bei Abnahme, Traenentaltiefe bei Reduktion."));
  content.push(p("Aenderungsschwelle: Eine minimale Aenderung von 5% (MEASUREMENT_CHANGE_THRESHOLD = 0,05) ist erforderlich, um als tatsaechliche Veraenderung gewertet zu werden. Dies verhindert, dass Messrauschen als Behandlungserfolg interpretiert wird.", { bold: true }));

  // 15.3 Status-Klassifikation
  content.push(h2("15.3 Status-Klassifikation"));
  content.push(p("Jede Zone erhaelt einen von fuenf Status-Codes, die den Behandlungsverlauf kategorisieren:"));
  const statusHeaders = ["Status", "Bedingung", "Klinische Bedeutung"];
  const statusWidths = [1500, 4000, 3860];
  const statusRows = [
    ["resolved", "Post-Severity < 1,0 UND Pre-Severity \u2265 1,0", "Zone vollstaendig behandelt \u2014 kein weiterer Handlungsbedarf"],
    ["improved", "Severity-Delta < \u22120,5", "Deutliche Verbesserung, moeglicherweise weitere Sitzung noetig"],
    ["unchanged", "Severity-Delta zwischen \u22120,5 und +0,5", "Keine signifikante Veraenderung \u2014 Behandlungsansatz ueberpruefen"],
    ["worsened", "Severity-Delta > +0,5", "Verschlechterung \u2014 moegliche Komplikation oder Progression abklaeren"],
    ["new", "Zone nur im Post-Assessment vorhanden", "Neues Problem entstanden \u2014 kann durch Behandlung anderer Zonen bedingt sein"],
  ];
  content.push(p("Tabelle 15.2: Status-Klassifikation der Zonenveraenderung", { bold: true }));
  content.push(makeTable(statusHeaders, statusRows, statusWidths));
  content.push(p("Die Schwellenwerte (SEVERITY_CHANGE_THRESHOLD = 0,5 und RESOLVED_THRESHOLD = 1,0) wurden konservativ gewaehlt, um Messrauschen von tatsaechlichen Veraenderungen zu unterscheiden. Ein Severity-Delta von \u00b10,5 kann allein durch normale Variabilitaet in der Bildaufnahme entstehen."));
  content.push(p("Die Sortierung der Zone-Deltas im Ergebnis erfolgt nach absolutem Severity-Delta (groesste Veraenderung zuerst), was dem Kliniker sofort zeigt, in welchen Zonen die deutlichsten Veraenderungen stattgefunden haben."));

  // 15.4 Improvement Score
  content.push(h2("15.4 Improvement Score"));
  content.push(p("Der Improvement Score (0\u2013100) ist die zentrale KPI des Before/After-Vergleichs. Er fasst die Veraenderungen aller behandelten Zonen in einen einzigen Wert zusammen und ermoeglicht den schnellen Ueberblick ueber den Gesamtbehandlungserfolg."));

  content.push(h3("15.4.1 Berechnungsmethodik"));
  content.push(p("Der Score wird als gewichtetes Mittel der Verbesserungsquoten aller behandelten Zonen berechnet:"));
  content.push(p("1. Fuer jede Zone mit Pre-Severity \u2265 1,0 (behandlungsbeduerftig) wird die Verbesserungsquote berechnet: improvement_ratio = \u2212severity_delta / pre_severity (Wert zwischen \u22121,0 und +1,0)"));
  content.push(p("2. Die Gewichtung erfolgt nach Regionen (REGION_WEIGHTS): Midface 1,2 | Lower Face 1,0 | Upper Face 0,8 | Profile 1,0. Diese Gewichtung spiegelt die klinische Bedeutung wider."));
  content.push(p("3. Das gewichtete Mittel wird auf die Skala 0\u2013100 skaliert, wobei 50 = keine Veraenderung."));

  content.push(h3("15.4.2 Interpretation"));
  const scoreHeaders = ["Score-Bereich", "Bewertung", "Klinische Implikation"];
  const scoreWidths = [1800, 2500, 5060];
  const scoreRows = [
    ["75\u2013100", "Exzellentes Ergebnis", "Behandlungsziele weitgehend oder vollstaendig erreicht"],
    ["60\u201374", "Gute Verbesserung", "Deutliche Verbesserung, evtl. eine weitere Sitzung geplant"],
    ["50\u201359", "Moderate Verbesserung", "Messbare Veraenderung, aber Behandlungsziele nicht vollstaendig erreicht"],
    ["40\u201349", "Minimale Veraenderung", "Kaum Verbesserung \u2014 Behandlungsstrategie ueberdenken"],
    ["< 40", "Bedenken", "Moeglicherweise Verschlechterung in einigen Zonen \u2014 Ursachenanalyse empfohlen"],
  ];
  content.push(p("Tabelle 15.3: Interpretation des Improvement Scores", { bold: true }));
  content.push(makeTable(scoreHeaders, scoreRows, scoreWidths));
  content.push(p("Der Baseline-Wert von 50 (keine Veraenderung) wurde bewusst gewaehlt, um sowohl Verbesserungen (> 50) als auch Verschlechterungen (< 50) abzubilden. Ein Score von exakt 50,0 bedeutet, dass die gewichteten Verbesserungen und Verschlechterungen sich gegenseitig aufheben."));

  // 15.5 Aesthetic Score Delta
  content.push(h2("15.5 Aesthetic Score Delta"));
  content.push(p("Zusaetzlich zum zonenspezifischen Improvement Score wird der Gesamt-Aesthetic-Score (0\u2013100, vgl. Kapitel 9) fuer Pre und Post verglichen. Das Delta (post \u2212 pre) gibt die Veraenderung des aesthetischen Gesamteindrucks an."));
  content.push(p("Zusammenhaeng: Der Aesthetic Score ist der uebergreifende Qualitaetsindikator, waehrend der Improvement Score die Behandlungswirksamkeit misst. Beide korrelieren, koennen aber divergieren: Eine erfolgreiche Behandlung einer einzelnen schweren Zone (hoher Improvement Score) kann den Aesthetic Score nur gering anheben, wenn die anderen Zonen unbeeinflusst bleiben."));

  // 15.6 Heatmap-Visualisierung
  content.push(h2("15.6 Heatmap-Visualisierung"));
  content.push(p("Fuer die Darstellung im Frontend generiert die Engine Heatmap-Daten pro Zone. Jeder HeatmapEntry enthaelt:"));
  content.push(p("\u2022 pre_intensity / post_intensity (0\u20131): Normalisierte Severity (0 = kein Problem, 1 = schwer). Berechnung: min(1,0; severity / 10,0).", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 delta_intensity (\u22121 bis +1): Veraenderung. Negativ = Verbesserung, Positiv = Verschlechterung.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 color_code: Vorgeschlagene Farbe fuer die Frontend-Darstellung:", { paragraphOpts: { indent: { left: 360 } } }));
  const heatHeaders = ["Status", "Farbe", "Hex-Code"];
  const heatWidths = [2500, 3000, 3860];
  const heatRows = [
    ["resolved", "Gruen (stark)", "#22c55e"],
    ["improved", "Gruen (hell)", "#4ade80"],
    ["unchanged", "Grau", "#9ca3af"],
    ["worsened", "Rot", "#ef4444"],
    ["new", "Orange", "#f97316"],
  ];
  content.push(p("Tabelle 15.4: Heatmap-Farbzuordnung", { bold: true }));
  content.push(makeTable(heatHeaders, heatRows, heatWidths));
  content.push(p("Die Heatmap-Daten koennen im Frontend als zonenspezifische Overlay-Grafik auf dem Gesichtsbild dargestellt werden, wobei jede Zone entsprechend ihres delta_intensity eingefaerbt wird. Dies ermoeglicht dem Behandler und dem Patienten einen intuitiven visuellen Vergleich."));

  // 15.7 Summary-Textgenerierung
  content.push(h2("15.7 Summary-Textgenerierung"));
  content.push(p("Die Engine erzeugt automatisch eine Zusammenfassung im natuerlichsprachlichen Format, die drei Informationen kombiniert:"));
  content.push(p("1. Aesthetic Score Veraenderung: z.\u202fB. 'Aesthetic score: 72,5 \u2192 84,3 (+11,8)'"));
  content.push(p("2. Zonenstatus-Verteilung: z.\u202fB. 'Zones: 5 improved, 2 resolved, 10 unchanged, 1 worsened'"));
  content.push(p("3. Gesamtbewertung: z.\u202fB. 'Overall: Good improvement'"));
  content.push(p("Diese Summary eignet sich fuer die Patientenkommunikation und die Dokumentation im Behandlungsverlauf."));

  // 15.8 Klinische Anwendung
  content.push(h2("15.8 Klinische Anwendung"));
  content.push(p("Der Before/After-Vergleich unterstuetzt den Kliniker in drei Szenarien:"));
  content.push(p("\u2022 Nachkontrolle: Nach einer Behandlung wird ein neues Assessment erstellt und mit dem Pre-Assessment verglichen. Der Kliniker sieht sofort, welche Zonen sich verbessert haben und wo Nachbesserungsbedarf besteht.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Longitudinale Dokumentation: Ueber die Patient-History-API (GET /api/v2/patients/{id}/history) koennen alle Assessments eines Patienten abgerufen und paarweise verglichen werden, um den Behandlungsverlauf ueber mehrere Sitzungen zu verfolgen.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 Qualitaetssicherung: Die aggregierten Improvement Scores ueber alle Patienten hinweg koennen als Qualitaetsmetrik fuer die Praxis dienen (vgl. Kapitel 16).", { paragraphOpts: { indent: { left: 360 } } }));

  return content;
}

// ─── Kapitel 16: Qualitaetssicherung (FULL) ───

function kapitel16() {
  const content = [];
  content.push(h1("Kapitel 16: Qualitaetssicherung"));
  content.push(p("Die Qualitaet der Analyseergebnisse steht und faellt mit der Qualitaet der Eingangsdaten. Ein noch so ausgefeiltes Analysesystem liefert unbrauchbare Ergebnisse, wenn die Bilder unscharf, falsch belichtet oder aus dem falschen Winkel aufgenommen sind. Das Qualitaetssicherungssystem des Aesthetic Biometrics Engine implementiert daher eine mehrstufige Validierungskette, die jedes Bild vor der Analyse auf Eignung prueft."));
  content.push(p("Dieses Kapitel beschreibt die drei Saeulen der Qualitaetssicherung: Bildqualitaetspruefung (Image Quality Gate), Kopfhaltungsvalidierung (Pose Validation) und Gesichtsausdruck-Check (Expression Validation). Zusaetzlich wird die Kalibrierungs-Confidence als Mass fuer die Zuverlaessigkeit der absoluten Messungen erlaeutert."));

  // 16.1 Architektur der Quality Gate
  content.push(h2("16.1 Architektur der Quality Gate"));
  content.push(p("Die Quality Gate ist als Pipeline organisiert, die sequentiell vier Pruefkategorien durchlaeuft. Jede Pruefung erzeugt QualityWarning-Objekte mit einem Schweregrad (low, medium, high, critical). Warnungen sind grundsaetzlich nicht-blockierend \u2014 die Analyse wird durchgefuehrt und die Warnungen werden im Response mitgeliefert. Nur bei kritischen Befunden (critical) wird das Bild abgelehnt."));

  const gateHeaders = ["Pruefung", "Modul", "Schweregrade", "Blockierend?"];
  const gateWidths = [2500, 2800, 2000, 2060];
  const gateRows = [
    ["Bildqualitaet", "check_image_quality()", "medium, high", "Nein \u2014 Warnungen"],
    ["Gesichtserkennung", "run_quality_gate()", "high", "Ja \u2014 Abbruch wenn kein Gesicht"],
    ["Kopfhaltung (hard)", "check_hard_pose_rejection()", "critical", "Ja \u2014 Bild wird abgelehnt"],
    ["Kopfhaltung (soft)", "check_head_pose()", "medium, high", "Nein \u2014 Warnungen"],
    ["Gesichtsausdruck", "check_neutral_expression()", "medium", "Nein \u2014 Warnungen"],
  ];
  content.push(p("Tabelle 16.1: Pruefkategorien der Quality Gate", { bold: true }));
  content.push(makeTable(gateHeaders, gateRows, gateWidths));
  content.push(p("Designprinzip: Das System bevorzugt Warnungen gegenueber Ablehnungen. Ein suboptimales Bild mit Warnungen ist fuer den Kliniker wertvoller als gar kein Ergebnis. Nur wenn die Landmark-Erkennung so unzuverlaessig waere, dass klinische Messungen sinnlos werden, erfolgt eine harte Ablehnung.", { bold: true }));

  // 16.2 Bildqualitaetspruefung
  content.push(h2("16.2 Bildqualitaetspruefung"));
  content.push(p("Die Bildqualitaetspruefung analysiert vier physikalische Bildeigenschaften, die die Zuverlaessigkeit der Landmark-Erkennung direkt beeinflussen:"));

  content.push(h3("16.2.1 Aufloesung"));
  content.push(p("Mindestanforderung: 640\u00d7480 Pixel. Unterhalb dieser Aufloesung sind feine anatomische Strukturen (Vermiliongrenze, Traenentaltiefe, Iris-Durchmesser) nicht zuverlaessig erkennbar. Bei Unterschreitung wird der Warning-Code LOW_RESOLUTION mit Severity 'medium' erzeugt."));
  content.push(p("Empfehlung: 1024\u00d71024 Pixel oder hoeher. Das System skaliert Bilder intern auf 1024\u00d71024 nach dem Gesichtszuschnitt (Image Preprocessor). Hoehere Eingangsaufloesungen verbessern die Zuschnittsqualitaet, da mehr Bildinformation fuer den Crop zur Verfuegung steht."));

  content.push(h3("16.2.2 Belichtung"));
  content.push(p("Die mittlere Helligkeit des Graustufenbilds wird als Indikator fuer die Belichtung verwendet:"));
  const expHeaders = ["Bereich", "Warning-Code", "Severity", "Empfehlung"];
  const expWidths = [2000, 2200, 1200, 3960];
  const expRows = [
    ["< 50 / 255", "UNDEREXPOSED", "high", "Bild zu dunkel \u2014 Beleuchtung erhoehen, Blitz verwenden"],
    ["50\u2013220 / 255", "\u2014 (OK)", "\u2014", "Akzeptabler Belichtungsbereich"],
    ["> 220 / 255", "OVEREXPOSED", "high", "Bild ueberbelichtet \u2014 Beleuchtung reduzieren, Blitz vermeiden"],
  ];
  content.push(p("Tabelle 16.2: Belichtungsbereiche und Warnungen", { bold: true }));
  content.push(makeTable(expHeaders, expRows, expWidths));

  content.push(h3("16.2.3 Kontrast"));
  content.push(p("Der Kontrast wird ueber die Standardabweichung der Helligkeit im Graustufenbild gemessen. Ein Wert unter 30 erzeugt den Warning-Code LOW_CONTRAST mit Severity 'medium'. Niedriger Kontrast erschwert die Erkennung feiner Konturen (Nasolabialfalte, Traenental) und fuehrt zu ungenaeueren Landmark-Positionen."));
  content.push(p("Empfehlung: Gleichmaessige, diffuse Beleuchtung (Ringblitz oder symmetrische Softboxen) erzeugt guten Kontrast ohne harte Schatten. Direkte Sonne oder punktfoermige Lichtquellen erzeugen starke Schatten, die zu falsch-positiven Volumendefiziten fuehren koennen."));

  content.push(h3("16.2.4 Schaerfe"));
  content.push(p("Die Bildschaerfe wird ueber die Varianz des Laplace-Operators (Laplacian Variance) gemessen \u2014 ein gaengiges Mass fuer lokale Kantenschaerfe. Ein Wert unter 50 erzeugt den Warning-Code BLURRY mit Severity 'high'."));
  content.push(p("Unscharfe Bilder fuehren zu ungenauerer Landmark-Platzierung, insbesondere bei feinen Strukturen wie der Vermiliongrenze (Lippenkontur) und der Iris (Kalibrierungsreferenz). Die Iris-basierte Kalibrierung (vgl. Kapitel 3) ist besonders empfindlich gegenueber Unschaerfe, da der Iris-Durchmesser als Massstab dient."));

  // 16.3 Kopfhaltungsvalidierung
  content.push(h2("16.3 Kopfhaltungsvalidierung (Pose Validation)"));
  content.push(p("Die Kopfhaltung wird ueber die Head-Pose-Estimation (Yaw, Pitch, Roll aus der Transformationsmatrix, vgl. Kapitel 3) gemessen und gegen ansichtsspezifische Toleranzen geprueft. Das System unterscheidet zwischen weichen Warnungen (Soft Limits) und harten Ablehnungen (Hard Limits)."));

  content.push(h3("16.3.1 Soft Limits (Warnungen)"));
  content.push(p("Soft Limits erzeugen Warnungen, die auf eine suboptimale aber verwertbare Kopfhaltung hinweisen:"));
  const softHeaders = ["Ansicht", "Max Yaw", "Max Pitch", "Max Roll"];
  const softWidths = [2000, 2500, 2500, 2360];
  const softRows = [
    ["Frontal", "\u00b112\u00b0", "\u00b110\u00b0", "\u00b18\u00b0"],
    ["Oblique", "25\u00b0\u201360\u00b0 (abs)", "\u00b110\u00b0", "\u00b18\u00b0"],
    ["Profil", "> 70\u00b0 (abs)", "\u00b110\u00b0", "\u00b18\u00b0"],
  ];
  content.push(p("Tabelle 16.3: Soft Limits fuer die Kopfhaltung", { bold: true }));
  content.push(makeTable(softHeaders, softRows, softWidths));

  content.push(h3("16.3.2 Hard Limits (Ablehnung)"));
  content.push(p("Hard Limits fuehren zur Ablehnung des Bildes (Severity 'critical'), da die Landmarks bei extremer Kopfhaltung zu unzuverlaessig fuer klinische Messungen werden:"));
  const hardHeaders = ["Ansicht", "Max Yaw", "Max Pitch", "Max Roll"];
  const hardWidths = [2000, 2500, 2500, 2360];
  const hardRows = [
    ["Frontal", "\u00b125\u00b0", "\u00b120\u00b0", "\u00b115\u00b0"],
    ["Oblique", "15\u00b0\u201375\u00b0 (abs)", "\u00b120\u00b0", "\u00b115\u00b0"],
    ["Profil", "> 55\u00b0 (abs)", "\u00b120\u00b0", "\u00b115\u00b0"],
  ];
  content.push(p("Tabelle 16.4: Hard Limits (Bildablehnung)", { bold: true }));
  content.push(makeTable(hardHeaders, hardRows, hardWidths));
  content.push(p("Bei einer harten Ablehnung wird die Analyse abgebrochen und dem Nutzer eine Fehlermeldung mit dem konkreten Abweichungswert und der empfohlenen Korrektur angezeigt (z.\u202fB. 'Head rotation 28,3\u00b0 exceeds maximum 25\u00b0 for frontal view. Image rejected.'). Die Analyse wird fuer die anderen Ansichten fortgesetzt, sofern diese akzeptiert werden (Partial-Failure-Handling)."));

  content.push(h3("16.3.3 Ansichtsspezifische Warning-Codes"));
  const codeHeaders = ["Warning-Code", "Bedingung", "Typische Ursache"];
  const codeWidths = [2500, 3500, 3360];
  const codeRows = [
    ["HEAD_NOT_FRONTAL", "Yaw > 12\u00b0 bei Frontalansicht", "Patient hat den Kopf leicht gedreht"],
    ["HEAD_NOT_OBLIQUE", "Yaw < 25\u00b0 oder > 60\u00b0 bei Oblique", "Zu wenig oder zu viel Drehung fuer 45\u00b0"],
    ["HEAD_NOT_PROFILE", "Yaw < 70\u00b0 bei Profilansicht", "Kopf nicht genug zur Seite gedreht"],
    ["HEAD_TILTED", "Roll > 8\u00b0", "Kopf zur Seite geneigt"],
    ["HEAD_PITCH", "Pitch > 10\u00b0", "Kopf nach oben oder unten geneigt"],
    ["POSE_REJECTED", "Ueberschreitung Hard Limit", "Extreme Fehlhaltung \u2014 Bild unbrauchbar"],
  ];
  content.push(p("Tabelle 16.5: Warning-Codes der Kopfhaltungsvalidierung", { bold: true }));
  content.push(makeTable(codeHeaders, codeRows, codeWidths));

  // 16.4 Gesichtsausdruck-Validierung
  content.push(h2("16.4 Gesichtsausdruck-Validierung (Expression Check)"));
  content.push(p("Die biometrische Analyse erfordert einen neutralen, entspannten Gesichtsausdruck. Aktive Gesichtsausdruecke veraendern die Landmark-Positionen und fuehren zu fehlerhaften Messwerten. Ein Laecheln verschiebt beispielsweise die Mundwinkel nach lateral-cranial und simuliert eine geringere Nasolabialfaltentiefe."));
  content.push(p("Die Pruefung erfolgt ueber die Blendshape-Koeffizienten (52 Werte von 0,0 bis 1,0), die die Aktivierung einzelner Gesichtsmuskelgruppen quantifizieren. Fuer 9 klinisch relevante Blendshapes sind Schwellenwerte definiert:"));
  const exprHeaders = ["Blendshape", "Schwellenwert", "Gemessene Muskelbewegung"];
  const exprWidths = [2500, 1800, 5060];
  const exprRows = [
    ["mouthSmileLeft / Right", "> 0,15", "Laecheln \u2014 verfaelscht Nasolabialfalte, Mundwinkelposition"],
    ["browDownLeft / Right", "> 0,20", "Stirnrunzeln \u2014 verfaelscht Brauenposition, Glabellabeurteilung"],
    ["jawOpen", "> 0,10", "Mund offen \u2014 verfaelscht Lippenverhaeltnis, Kinnposition"],
    ["mouthPucker", "> 0,15", "Lippen gespitzt \u2014 verfaelscht Lippenvolumenmessung"],
    ["mouthFunnel", "> 0,15", "Lippen gerundet \u2014 verfaelscht Vermiliongrenze"],
    ["eyeSquintLeft / Right", "> 0,25", "Augen zusammengekniffen \u2014 verfaelscht periobitale Analyse"],
  ];
  content.push(p("Tabelle 16.6: Blendshape-Schwellenwerte fuer Neutral-Expression-Check", { bold: true }));
  content.push(makeTable(exprHeaders, exprRows, exprWidths));
  content.push(p("Bei Ueberschreitung eines oder mehrerer Schwellenwerte wird der Warning-Code NON_NEUTRAL_EXPRESSION erzeugt. Die Warnung nennt die bis zu drei staerksten Abweichungen (z.\u202fB. 'Active facial expression detected: mouthSmileLeft: 0,34, mouthSmileRight: 0,28, jawOpen: 0,15')."));

  content.push(h3("16.4.1 Expression Deviation Score"));
  content.push(p("Zusaetzlich zur binaeren Warnung berechnet die Funktion compute_expression_deviation() einen kontinuierlichen Abweichungswert (0,0 = neutral, 1,0 = extreme Expression). Dieser Score wird von der Zone-Analyse genutzt, um Blendshape-basierte Befunde (Muskeltonus, dynamische Asymmetrie) bei nicht-neutralem Ausdruck automatisch herabzugewichten."));
  content.push(p("Die Berechnung erfolgt ueber den normalisierten Ueberschuss: Fuer jeden Blendshape oberhalb seines Schwellenwerts wird (value \u2212 threshold) / (1,0 \u2212 threshold) berechnet und das arithmetische Mittel aller Ueberschuesse gebildet."));
  content.push(p("WICHTIG: Expression-Blendshapes werden NIEMALS ueber verschiedene Ansichten gemittelt oder fusioniert. Jede Ansicht hat ihren eigenen Expression-Check, da der Gesichtsausdruck sich zwischen den Aufnahmen aendern kann.", { bold: true }));

  // 16.5 Kalibrierungs-Confidence
  content.push(h2("16.5 Kalibrierungs-Confidence"));
  content.push(p("Die Umrechnung von Pixeln in Millimeter erfolgt ueber die Iris-basierte Kalibrierung (vgl. Kapitel 3). Die Zuverlaessigkeit dieser Kalibrierung wird als Confidence-Wert (0,0\u20131,0) angegeben:"));
  content.push(p("\u2022 > 0,9 (Iris-basiert, beide Augen sichtbar): Hoechste Genauigkeit (< 3% Fehler). Iris-Durchmesser 11,7 mm als Referenz.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 0,7\u20130,9 (Iris-basiert, ein Auge sichtbar): Gute Genauigkeit (3\u20135% Fehler). Haeufig bei Oblique-Aufnahmen.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 0,5\u20130,7 (Face-Width-Fallback): Moderate Genauigkeit (5\u201310% Fehler). Wird verwendet, wenn Iris nicht zuverlaessig erkennbar (Unschaerfe, Brille, Profil).", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("\u2022 < 0,5: Niedrige Confidence. Absolute mm-Werte sollten mit Vorsicht interpretiert werden; relative Verhaeltnisse (Proportionen, Symmetrie-Scores) bleiben zuverlaessig.", { paragraphOpts: { indent: { left: 360 } } }));
  content.push(p("Bei niedriger Kalibrierungs-Confidence wird eine QualityWarning im Analyseergebnis mitgeliefert. Der Kliniker sollte in solchen Faellen die absoluten mm-Werte kritisch hinterfragen und sich primaer auf relative Scores (Symmetrie, Proportionen, Severity) stuetzen, die kalibrierungsunabhaengig sind."));

  // 16.6 Zusammenspiel im Pipeline-Orchestrator
  content.push(h2("16.6 Zusammenspiel im Pipeline-Orchestrator"));
  content.push(p("Der Pipeline-Orchestrator (vgl. Kapitel 1) integriert die Quality Gate in den Analysepfad wie folgt:"));
  content.push(p("1. Bild empfangen und vorverarbeiten (Image Preprocessor: EXIF, Crop, Resize)"));
  content.push(p("2. Bildqualitaet pruefen (check_image_quality) \u2192 Warnungen sammeln"));
  content.push(p("3. Gesichtserkennung durchfuehren (Face Landmarker)"));
  content.push(p("4. Falls kein Gesicht erkannt: Warnung NO_FACE_DETECTED, Bild ueberspringen (HTTP 422 wenn kein Bild akzeptiert)"));
  content.push(p("5. Hard-Pose-Rejection pruefen \u2192 Bei Ablehnung: Bild ueberspringen, naechste Ansicht versuchen"));
  content.push(p("6. Soft-Pose-Warnungen und Expression-Check \u2192 Warnungen sammeln"));
  content.push(p("7. Analyse mit allen akzeptierten Ansichten durchfuehren (Partial-Failure: mindestens eine Ansicht muss akzeptiert werden)"));
  content.push(p("8. Alle Warnungen im Response-Objekt mitliefern"));
  content.push(p("Dieses Partial-Failure-Handling stellt sicher, dass der Kliniker auch bei suboptimaler Fotodokumentation verwertbare Ergebnisse erhaelt \u2014 mit klaren Hinweisen auf die Einschraenkungen. Wurden beispielsweise nur Frontal- und Oblique-Bild akzeptiert (Profil abgelehnt), fehlen die Profilzonen (Pf1\u2013Pf3, Ch1, Jl1) im Report, aber alle frontal und oblique messbaren Zonen werden vollstaendig analysiert."));

  // 16.7 Empfehlungen fuer die Praxis
  content.push(h2("16.7 Empfehlungen fuer die Praxis"));
  content.push(p("Basierend auf den implementierten Qualitaetspruefungen gelten folgende Empfehlungen fuer die klinische Fotodokumentation:"));
  content.push(p("1. Beleuchtung: Ringblitz oder zwei symmetrische Softboxen auf 45\u00b0. Keine direkte Sonne, kein harter Blitz."));
  content.push(p("2. Hintergrund: Einfarbig neutral, kein Muster, keine anderen Personen."));
  content.push(p("3. Aufloesung: Smartphone-Kamera in hoechster Aufloesung (mindestens 1024\u00d71024 empfohlen)."));
  content.push(p("4. Entfernung: 0,5\u20131,0 Meter zum Patienten \u2014 nah genug fuer Detail, weit genug fuer minimale Verzeichnung."));
  content.push(p("5. Kopfhaltung: Patient blickt geradeaus auf Fixpunkt in Augenhoehe (Frontal), dreht den Kopf 45\u00b0 (Oblique) bzw. 90\u00b0 (Profil) zur Kamera."));
  content.push(p("6. Ausdruck: Neutral, entspannt, Lippen leicht geschlossen. Kein Laecheln, keine Stirnrunzeln."));
  content.push(p("7. Wiederholung: Bei Warnungen (insbesondere BLURRY, UNDEREXPOSED, HEAD_NOT_*) die entsprechende Aufnahme wiederholen."));
  content.push(p("Die konsistente Einhaltung dieser Standards verbessert nicht nur die Analysequalitaet, sondern ermoeglicht auch zuverlaessigere Before/After-Vergleiche (Kapitel 15), da Variabilitaet in den Aufnahmebedingungen minimiert wird."));

  return content;
}

// ─── Placeholder chapters ───

function placeholderChapter(title) {
  return [h1(title), placeholder()];
}
function placeholderSection(title) {
  return [h2(title), placeholder()];
}

// ─── Build Document ───

async function main() {
  const doc = new Document({
    styles: {
      default: {
        document: { run: { font: "Arial", size: 24 } }
      },
      paragraphStyles: [
        { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 36, bold: true, font: "Arial", color: "2C3E50" },
          paragraph: { spacing: { before: 480, after: 240 }, outlineLevel: 0 } },
        { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 30, bold: true, font: "Arial", color: "34495E" },
          paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 1 } },
        { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 26, bold: true, font: "Arial", color: "5D6D7E" },
          paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 2 } },
      ]
    },
    sections: [
      // Title page
      {
        properties: {
          page: {
            size: { width: 11906, height: 16838 },
            margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
          }
        },
        children: [
          new Paragraph({ spacing: { before: 4000 } }),
          new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
            children: [new TextRun({ text: "\u00c4sthetische Gesichtsanalyse", size: 56, bold: true, font: "Arial", color: "2C3E50" })] }),
          new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 },
            children: [new TextRun({ text: "und Behandlungsplanung", size: 56, bold: true, font: "Arial", color: "2C3E50" })] }),
          new Paragraph({ spacing: { before: 400 } }),
          new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 },
            children: [new TextRun({ text: "Ein systematischer Ansatz f\u00fcr die \u00e4sthetische Medizin", size: 28, italics: true, font: "Arial", color: "5D6D7E" })] }),
          new Paragraph({ spacing: { before: 2000 } }),
          new Paragraph({ alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: "2026", size: 28, font: "Arial", color: "5D6D7E" })] }),
          pb(),
        ]
      },
      // TOC
      {
        properties: {
          page: {
            size: { width: 11906, height: 16838 },
            margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
          }
        },
        headers: {
          default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
            children: [new TextRun({ text: "\u00c4sthetische Gesichtsanalyse und Behandlungsplanung", size: 18, italics: true, color: "999999" })] })] })
        },
        footers: {
          default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
            children: [new TextRun({ children: [PageNumber.CURRENT], size: 20 })] })] })
        },
        children: [
          h1("Inhaltsverzeichnis"),
          new TableOfContents("Inhaltsverzeichnis", { hyperlink: true, headingStyleRange: "1-3" }),
          pb(),
          // TEIL I
          h1("Teil I \u2014 Grundlagen"),
          ...kapitel1(),
          pb(),
          ...kapitel2(),
          pb(),
          ...kapitel3(),
          pb(),
          // TEIL II
          h1("Teil II \u2014 Analysemethoden"),
          ...kapitel4(),
          pb(),
          ...kapitel5(),
          pb(),
          ...kapitel6(),
          pb(),
          ...kapitel7(),
          pb(),
          ...kapitel8(),
          pb(),
          // TEIL III
          h1("Teil III \u2014 Das Zonen-System"),
          ...kapitel9(),
          pb(),
          ...kapitel10(),
          pb(),
          // TEIL IV
          h1("Teil IV \u2014 Behandlungsplanung"),
          ...kapitel11(),
          pb(),
          ...kapitel12(),
          pb(),
          ...kapitel13(),
          pb(),
          ...kapitel14(),
          pb(),
          // TEIL V
          h1("Teil V \u2014 Ergebniskontrolle"),
          ...kapitel15(),
          pb(),
          ...kapitel16(),
          pb(),
          // ANHANG
          h1("Anhang"),
          ...placeholderChapter("Anhang A: Vollst\u00e4ndige Zone-Referenztabelle"),
          ...placeholderChapter("Anhang B: Produkt-\u00dcbersichtstabelle"),
          ...placeholderChapter("Anhang C: Vaskul\u00e4re Danger-Zone Karte"),
          ...placeholderChapter("Anhang D: Glossar"),
          pb(),
          h1("Literaturverzeichnis"),
          p("De Maio M. MD Codes\u2122: A Methodological Approach to Facial Aesthetic Treatment with Injectable Hyaluronic Acid Fillers. Aesthetic Plast Surg. 2021;45:1\u201318."),
          p("Hashemi H, Khabazkhoob M, Emamian MH, Shariati M, Fotouhi A. Distribution of iris diameter measured with the Orbscan II. Cornea. 2012;31(12):1442\u20131447."),
          p("Ricketts RM. The biologic significance of the divine proportion and Fibonacci series. Am J Orthod. 1982;81(5):351\u2013370."),
          p("Sundaram H, Voigts B, Beer K, Meland M. Comparison of the Rheological Properties of Viscosity and Elasticity in Two Categories of Soft Tissue Fillers: Calcium Hydroxylapatite and Hyaluronic Acid. Dermatol Surg. 2010;36:1859\u20131865."),
          p("Sundaram H, Liew S, Signorini M, et al. Global Aesthetics Consensus: Hyaluronic Acid Fillers and Botulinum Toxin Type A \u2014 Recommendations for Combined Treatment and Optimizing Outcomes in Diverse Populations. Plast Reconstr Surg. 2016;137(5):1410\u20131423."),
          p("Cotofana S, Lachman N. Arteries of the Face and Their Relevance for Minimally Invasive Facial Procedures: An Anatomical Review. Plast Reconstr Surg. 2019;143(1):240\u2013252."),
        ]
      }
    ]
  });

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync("C:/Users/User/ClaudePlayground/AESTHETIC BIOMETRICS ENGINE/docs/lehrbuch/Aesthetic_Facial_Analysis.docx", buffer);
  console.log("Document created successfully!");
}

main().catch(console.error);
