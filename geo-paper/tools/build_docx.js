// Build the CNKI-style manuscript (.docx) from paper.json.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType,
  AlignmentType, BorderStyle, ShadingType, Footer, PageNumber, VerticalAlign,
} = require("docx");

const [, , jsonPath, figDir, outPath] = process.argv;
const data = JSON.parse(fs.readFileSync(jsonPath, "utf8"));
const M = data.meta;

const SONG = { ascii: "Times New Roman", hAnsi: "Times New Roman", eastAsia: "宋体", cs: "Times New Roman" };
const HEI = { ascii: "Times New Roman", hAnsi: "Times New Roman", eastAsia: "黑体", cs: "Times New Roman" };
const KAI = { ascii: "Times New Roman", hAnsi: "Times New Roman", eastAsia: "楷体", cs: "Times New Roman" };
const pt = (n) => n * 2; // half-points

const run = (text, o = {}) => new TextRun({ text, font: o.font || SONG, size: pt(o.size || 12), bold: !!o.bold, superScript: !!o.sup });
const para = (children, o = {}) => new Paragraph({
  children, alignment: o.align || AlignmentType.JUSTIFIED,
  spacing: { line: o.line || 360, before: o.before || 0, after: o.after || 0 },
  indent: o.indent, keepNext: o.keepNext,
});

const children = [];
// ---- Chinese front matter ----
children.push(para([run(M.title, { font: HEI, size: 18, bold: true })], { align: AlignmentType.CENTER, after: 240, line: 500 }));
children.push(para([run(M.author, { font: KAI, size: 12 })], { align: AlignmentType.CENTER, after: 60 }));
children.push(para([run(`（${M.affil.replace(/^【|】$/g, "")}）`, { size: 10.5 })], { align: AlignmentType.CENTER, after: 240 }));
const labeled = (label, text, font = SONG, labelFont = HEI) =>
  para([run(label, { font: labelFont, size: 10.5, bold: true }), run(text, { font, size: 10.5 })], { line: 300, after: 60 });
children.push(labeled("摘　要：", M.abstract));
children.push(labeled("关键词：", M.keywords));
children.push(para([run("中图分类号：", { font: HEI, size: 10.5, bold: true }), run(M.clc + "　　", { size: 10.5 }),
  run("文献标识码：", { font: HEI, size: 10.5, bold: true }), run("A", { size: 10.5 })], { line: 300, after: 60 }));
children.push(para([run("作者简介：", { font: HEI, size: 10.5, bold: true }),
  run("【姓名（出生年—），性别，籍贯，学历，单位，研究方向】", { size: 10.5 })], { line: 300, after: 300 }));
// ---- English front matter ----
children.push(para([run(M.etitle, { size: 14, bold: true })], { align: AlignmentType.CENTER, after: 120, line: 400 }));
children.push(para([run(M.eauthor, { size: 12 })], { align: AlignmentType.CENTER, after: 60 }));
children.push(para([run(`(${M.eaffil.replace(/^\[|\]$/g, "")})`, { size: 10.5 })], { align: AlignmentType.CENTER, after: 200 }));
children.push(labeled("Abstract: ", M.eabstract, SONG, SONG));
children.push(labeled("Key words: ", M.ekeywords, SONG, SONG));
children.push(para([], { after: 200 }));

// ---- Body ----
const tableBlock = (b) => {
  const [header, ...rows] = b.rows;
  const total = 9000; // DXA, fits A4 text width (11906 - 2*1440 margin)
  // column widths proportional to the longest cell text (sqrt-damped), min 1000 DXA
  const len = (t) => [...t].reduce((n, ch) => n + (ch.charCodeAt(0) > 255 ? 2 : 1), 0);
  const raw = header.map((_, ci) => Math.sqrt(Math.max(...b.rows.map((r) => len(r[ci] || "")))));
  const sum = raw.reduce((a, x) => a + x, 0);
  let widths = raw.map((x) => Math.max(1000, Math.round((total * x) / sum)));
  const diff = total - widths.reduce((a, x) => a + x, 0);
  widths[widths.indexOf(Math.max(...widths))] += diff;
  const thick = { style: BorderStyle.SINGLE, size: 12, color: "000000" };
  const thin = { style: BorderStyle.SINGLE, size: 6, color: "000000" };
  const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  const cell = (t, i, r, isHead, isLast) => new TableCell({
    width: { size: widths[i], type: WidthType.DXA },
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 60, bottom: 60, left: 80, right: 80 },
    shading: { type: ShadingType.CLEAR, fill: "FFFFFF", color: "auto" },
    borders: { top: r === 0 ? thick : none, bottom: isHead ? thin : (isLast ? thick : none), left: none, right: none },
    children: [new Paragraph({ alignment: AlignmentType.CENTER, spacing: { line: 240 },
      children: [run(t, { size: 9, font: isHead ? HEI : SONG, bold: isHead })] })],
  });
  const all = [header, ...rows];
  return [
    para([run(b.caption, { font: HEI, size: 10.5, bold: true })], { align: AlignmentType.CENTER, before: 120, after: 60, keepNext: true }),
    new Table({
      width: { size: total, type: WidthType.DXA }, columnWidths: widths, alignment: AlignmentType.CENTER,
      rows: all.map((r, ri) => new TableRow({ tableHeader: ri === 0, cantSplit: true,
        children: r.map((t, ci) => cell(t, ci, ri, ri === 0, ri === all.length - 1)) })),
    }),
    para([], { after: 120 }),
  ];
};

for (const b of data.blocks) {
  if (b.type === "h1") children.push(para([run(b.text, { font: HEI, size: 14, bold: true })], { align: AlignmentType.LEFT, before: 240, after: 120, keepNext: true }));
  else if (b.type === "h2") children.push(para([run(b.text, { font: HEI, size: 12, bold: true })], { align: AlignmentType.LEFT, before: 120, after: 60, keepNext: true }));
  else if (b.type === "p") children.push(para(b.segs.map((s) => run(s.t, { sup: s.sup })), { indent: { firstLine: 480 } }));
  else if (b.type === "table") children.push(...tableBlock(b));
  else if (b.type === "figure") {
    const img = fs.readFileSync(path.join(figDir, b.path));
    const w = img.readUInt32BE(16), h = img.readUInt32BE(20); // PNG IHDR
    const width = 560;
    children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120 }, keepNext: true,
      children: [new ImageRun({ type: "png", data: img, transformation: { width, height: Math.round(width * h / w) },
        altText: { title: b.caption, description: b.caption, name: b.path } })] }));
    children.push(para([run(b.caption, { font: HEI, size: 10.5, bold: true })], { align: AlignmentType.CENTER, after: 120 }));
  }
}

// ---- References (GB/T 7714-2015, 顺序编码制) ----
children.push(para([run("参考文献", { font: HEI, size: 14, bold: true })], { align: AlignmentType.LEFT, before: 240, after: 120 }));
for (const r of data.refs) {
  children.push(new Paragraph({
    alignment: AlignmentType.LEFT, spacing: { line: 280, after: 40 },
    indent: { left: 480, hanging: 480 },
    children: [run(`[${r.n}]`, { size: 10.5 }), new TextRun({ text: "\t", size: pt(10.5) }), run(r.ref, { size: 10.5 })],
    tabStops: [{ type: "left", position: 480 }],
  }));
}

const doc = new Document({
  creator: "", title: M.title, description: M.etitle,
  styles: { default: { document: { run: { font: SONG, size: pt(12) } } } },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ children: [PageNumber.CURRENT], size: pt(9), font: SONG })] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(outPath, buf); console.log("wrote", outPath, buf.length, "bytes"); });
