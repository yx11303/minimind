import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fm.fontManager.addfont("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc")
plt.rcParams["font.family"] = "WenQuanYi Zen Hei"
out = sys.argv[1]

BLUE, ORANGE, RED, GRAY, INK = "#2b5b84", "#b8661f", "#b22222", "#6b6b6b", "#222222"
fig, ax = plt.subplots(figsize=(11.5, 5.6), dpi=300)
ax.set_xlim(0, 14.6); ax.set_ylim(-1.0, 6.3); ax.axis("off")

def box(x, y, w, h, text, ec=INK, fc="white", fs=10.5, lw=1.2, ls="-", weight="normal"):
    ax.add_patch(FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                ec=ec, fc=fc, lw=lw, ls=ls))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=INK, weight=weight, linespacing=1.35)

def arrow(p, q, color=INK, ls="-", lw=1.4, rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=13, color=color, lw=lw, ls=ls,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=2, shrinkB=2))

def label(x, y, text, color=INK, fs=9.5, **kw):
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=color, **kw)

# containers
ax.add_patch(FancyBboxPatch((7.35, 0.35), 2.9, 3.75, boxstyle="round,pad=0.02,rounding_size=0.1",
                            ec=GRAY, fc="#f3f3f3", lw=1.0, ls="--"))
label(8.8, 3.85, "生成式引擎", color=GRAY, fs=10, weight="bold")
ax.add_patch(FancyBboxPatch((11.0, 1.75), 3.3, 4.15, boxstyle="round,pad=0.02,rounding_size=0.1",
                            ec=GRAY, fc="#f3f3f3", lw=1.0, ls="--"))
label(12.65, 5.62, "用户看到的AI回答页面", color=GRAY, fs=10, weight="bold")

# nodes
box(1.0, 3.0, 1.5, 1.0, "广告主", fs=11.5, weight="bold")
box(3.9, 4.75, 2.3, 1.0, "引擎平台\n广告系统", ec=BLUE)
box(3.9, 1.15, 2.0, 1.0, "GEO服务商", ec=ORANGE)
box(6.15, 1.15, 1.9, 1.3, "第三方信源\n资讯·测评\n问答·榜单", ec=ORANGE)
box(8.8, 1.0, 2.2, 0.62, "① 检索召回", fs=10)
box(8.8, 2.0, 2.2, 0.62, "② 上下文分配", fs=10)
box(8.8, 3.0, 2.2, 0.62, "③ 引用生成", fs=10)
box(12.65, 4.6, 2.8, 0.95, "赞助区块\n（标注“赞助”）", ec=BLUE, fc="#e8f0f7")
box(12.65, 2.75, 2.8, 1.2, "回答正文\n（含GEO内容，\n无广告标识）", ec=ORANGE, fc="#fbefe3")
# proposed in-text insertion (mechanism-design research, not deployed): route above the engine box
ax.plot([4.6, 4.6, 11.1], [4.25, 4.33, 4.33], color=BLUE, lw=1.1, ls=(0,(4,3)))
ax.add_patch(FancyArrowPatch((11.1, 4.33), (11.5, 3.38), arrowstyle="-|>", mutation_scale=12, color=BLUE, lw=1.1, ls=(0,(4,3)), shrinkA=0, shrinkB=2))
label(8.1, 4.5, "文内写入（机制设计研究方案，未上线）", color=BLUE, fs=8.8)

# track 1
arrow((1.75, 3.35), (2.75, 4.55), color=BLUE)
label(1.85, 4.25, "广告费", color=BLUE)
arrow((5.05, 4.75), (11.25, 4.75), color=BLUE, lw=1.6)
label(8.15, 5.05, "轨道一：平台广告（收入归平台）", color=BLUE, fs=10, weight="bold")

# track 2
arrow((1.75, 2.65), (2.9, 1.35), color=ORANGE)
label(1.85, 1.75, "服务费", color=ORANGE)
arrow((4.9, 1.15), (5.2, 1.15), color=ORANGE)
arrow((7.1, 1.0), (7.7, 1.0), color=ORANGE, lw=1.6)
arrow((8.8, 1.31), (8.8, 1.69), color=INK)
arrow((8.8, 2.31), (8.8, 2.69), color=INK)
arrow((9.9, 3.0), (11.25, 2.85), color=ORANGE, lw=1.6)
label(10.75, -0.6, "轨道二：第三方GEO内容（收入归服务商与内容渠道）", color=ORANGE, fs=10, weight="bold")

# manipulation
box(3.3, -0.55, 5.4, 0.6, "操纵型GEO：虚构测评·伪造评价·策略性文本·提示注入", ec=RED, fs=9.2, ls="--")
arrow((5.4, -0.25), (5.85, 0.48), color=RED, ls="--")

# governance tags
def tag(x, y, t):
    ax.text(x, y, t, ha="center", va="center", fontsize=8.6, color=GRAY,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=GRAY, lw=0.8))
tag(6.15, 2.25, "治理点A：随检索传递的商业标记")
tag(8.8, 0.02, "治理点B：信源发布行为识别")
tag(12.65, 6.15, "治理点C：多引擎重复抽样监测")

fig.savefig(out, bbox_inches="tight", pad_inches=0.05, facecolor="white")
print("saved", out)
