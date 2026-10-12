import csv, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sources import SOURCES
out = sys.argv[1]
os.makedirs(os.path.join(out, "sources"), exist_ok=True)
with open(os.path.join(out, "sources.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["no", "key", "type", "tier", "reference_gbt7714", "url", "verification"])
    for i, s in enumerate(SOURCES, 1):
        w.writerow([i, s["key"], s["type"], s["tier"], s["ref"], s["url"], s["check"]])
        with open(os.path.join(out, "sources", f"{i:02d}_{s['key']}.md"), "w", encoding="utf-8") as g:
            g.write(f"# {s['key']}\n\n- 类型：{s['type']}（{s['tier']}）\n- 著录（GB/T 7714-2015）：{s['ref']}\n- 链接：{s['url']}\n- 核验方式：{s['check']}\n- 核验日期：2026-10-12\n\n## 本文使用的事实\n\n{s['facts']}\n")
print(len(SOURCES), "sources")
