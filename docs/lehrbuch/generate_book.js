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
          ...placeholderChapter("Kapitel 1: Einf\u00fchrung in die \u00e4sthetische Gesichtsanalyse"),
          ...placeholderSection("1.1 Historischer Kontext"),
          ...placeholderSection("1.2 Standardisierte Fotografie"),
          ...placeholderSection("1.3 KI-gest\u00fctzte Analyse"),
          pb(),
          ...placeholderChapter("Kapitel 2: Anatomische Grundlagen"),
          ...placeholderSection("2.1 Gesichtsknochen und Retaining Ligaments"),
          ...placeholderSection("2.2 Fettkompartimente"),
          ...placeholderSection("2.3 Vaskul\u00e4re Anatomie und Danger Zones"),
          ...placeholderSection("2.4 Mimische Muskulatur"),
          pb(),
          ...placeholderChapter("Kapitel 3: Landmark-basierte Gesichtsvermessung"),
          ...placeholderSection("3.1 Das 478-Punkt-Landmarksystem"),
          ...placeholderSection("3.2 Anatomische Gruppen"),
          ...placeholderSection("3.3 Iris-basierte Kalibrierung"),
          pb(),
          // TEIL II
          h1("Teil II \u2014 Analysemethoden"),
          ...placeholderChapter("Kapitel 4: Symmetrieanalyse"),
          ...placeholderSection("4.1 Median-Sagittallinie und Symmetrieachsen"),
          ...placeholderSection("4.2 Bilaterale Symmetrie: klinische Schwellenwerte"),
          ...placeholderSection("4.3 Dynamische Asymmetrie"),
          pb(),
          ...placeholderChapter("Kapitel 5: Gesichtsproportionen"),
          ...placeholderSection("5.1 Vertikale Drittel"),
          ...placeholderSection("5.2 Horizontale F\u00fcnftel"),
          ...placeholderSection("5.3 Golden Ratio"),
          ...placeholderSection("5.4 Lip Ratio und Cupid\u2019s Bow"),
          pb(),
          ...kapitel6(),
          pb(),
          ...placeholderChapter("Kapitel 7: Volumenanalyse"),
          ...placeholderSection("7.1 Ogee Curve"),
          ...placeholderSection("7.2 Temporal Hollowing"),
          ...placeholderSection("7.3 Tear Trough Assessment"),
          ...placeholderSection("7.4 Pre-Jowl Sulcus"),
          pb(),
          ...placeholderChapter("Kapitel 8: Altersbedingte Ver\u00e4nderungen"),
          ...placeholderSection("8.1 Muskeltonus-Ver\u00e4nderungen"),
          ...placeholderSection("8.2 Gravitationelle Drift"),
          ...placeholderSection("8.3 Periorbitale Alterung"),
          pb(),
          // TEIL III
          h1("Teil III \u2014 Das Zonen-System"),
          ...kapitel9(),
          pb(),
          ...placeholderChapter("Kapitel 10: Multi-View Fusion"),
          pb(),
          // TEIL IV
          h1("Teil IV \u2014 Behandlungsplanung"),
          ...kapitel11(),
          pb(),
          ...placeholderChapter("Kapitel 12: Zone-zu-Produkt-Matching"),
          pb(),
          ...placeholderChapter("Kapitel 13: Klinische Priorisierung"),
          pb(),
          ...kapitel14(),
          pb(),
          // TEIL V
          h1("Teil V \u2014 Ergebniskontrolle"),
          ...placeholderChapter("Kapitel 15: Before/After-Vergleich"),
          pb(),
          ...placeholderChapter("Kapitel 16: Qualit\u00e4tssicherung"),
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
