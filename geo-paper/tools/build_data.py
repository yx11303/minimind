# Parse manuscript.md -> numbered citations (order of first appearance) + JSON for the docx builder.
import json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sources import SOURCES

src_md, out_json, out_md = sys.argv[1], sys.argv[2], sys.argv[3]
reg = {s["key"]: s for s in SOURCES}
text = open(src_md, encoding="utf-8").read()

CITE = re.compile(r"\[(@[A-Za-z0-9_]+(?:;\s*@[A-Za-z0-9_]+)*)\]")
order = []
for m in CITE.finditer(text):
    for k in re.findall(r"@([A-Za-z0-9_]+)", m.group(1)):
        if k not in reg:
            sys.exit(f"UNKNOWN CITATION KEY: {k}")
        if k not in order:
            order.append(k)
num = {k: i + 1 for i, k in enumerate(order)}
unused = [k for k in reg if k not in num]

def fmt(nums):
    nums = sorted(set(nums)); parts = []; i = 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        parts.append(f"{nums[i]}-{nums[j]}" if j - i >= 2 else ",".join(map(str, nums[i:j + 1])))
        i = j + 1
    return "[" + ",".join(parts) + "]"

def segs(line):
    """Split a paragraph into text / superscript-citation segments."""
    out, pos = [], 0
    for m in CITE.finditer(line):
        if m.start() > pos:
            out.append({"t": line[pos:m.start()]})
        out.append({"t": fmt([num[k] for k in re.findall(r"@([A-Za-z0-9_]+)", m.group(1))]), "sup": True})
        pos = m.end()
    if pos < len(line):
        out.append({"t": line[pos:]})
    return out

meta, blocks, lines, i = {}, [], text.splitlines(), 0
while i < len(lines):
    ln = lines[i].rstrip()
    if not ln:
        i += 1; continue
    m = re.match(r"::(\w+)::\s*(.*)", ln)
    if m and m.group(1) == "table":
        cap = m.group(2); rows = []; i += 1
        while not lines[i].startswith("::endtable::"):
            rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
        blocks.append({"type": "table", "caption": cap, "rows": rows}); i += 1; continue
    if m and m.group(1) == "figure":
        path, cap = [x.strip() for x in m.group(2).split("|", 1)]
        blocks.append({"type": "figure", "path": path, "caption": cap}); i += 1; continue
    if m:
        meta[m.group(1)] = m.group(2); i += 1; continue
    if ln.startswith("### "):
        blocks.append({"type": "h2", "text": ln[4:]})
    elif ln.startswith("## "):
        blocks.append({"type": "h1", "text": ln[3:]})
    else:
        blocks.append({"type": "p", "segs": segs(ln)})
    i += 1

refs = [{"n": num[k], "key": k, "ref": reg[k]["ref"]} for k in order]
json.dump({"meta": meta, "blocks": blocks, "refs": refs}, open(out_json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# Readable markdown with resolved numbers
md = CITE.sub(lambda m: "<sup>" + fmt([num[k] for k in re.findall(r"@([A-Za-z0-9_]+)", m.group(1))]) + "</sup>", text)
md = re.sub(r"^::table:: (.*)$", r"**\1**\n", md, flags=re.M)
md = re.sub(r"^::endtable::$", "", md, flags=re.M)
md = re.sub(r"^\| (维度 .*)$", lambda m: "| " + m.group(1) + "\n" + "|---" * (m.group(1).count("|") + 1) + "|", md, flags=re.M)
md = re.sub(r"^::figure:: (\S+) \| (.*)$", r"![\2](\1)\n\n**\2**", md, flags=re.M)
head = []
for k, lab in [("title", "# "), ("author", ""), ("affil", ""), ("abstract", "**摘要：**"), ("keywords", "**关键词：**"), ("clc", "**中图分类号：**"),
               ("etitle", "## "), ("eauthor", ""), ("eaffil", ""), ("eabstract", "**Abstract:** "), ("ekeywords", "**Key words:** ")]:
    head.append(lab + meta[k])
md = re.sub(r"^::\w+::.*\n", "", md, flags=re.M)
md = "\n\n".join(head) + "\n\n" + md.strip() + "\n\n## 参考文献\n\n" + "\n".join(f"[{r['n']}] {r['ref']}  " for r in refs) + "\n"
open(out_md, "w", encoding="utf-8").write(md)
print(f"cited {len(order)} sources; unused in registry: {unused}")
