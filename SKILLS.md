# 全局 SKILLS + 经典算子：应对"没有统一标准"的绘图需求

**日期：** 2026-10-18
**背景：** 科研绘图没有统一标准，需求沿坐标轴类型、图例位置、色标、统计标注、多面板组合、目标期刊
等维度不断变化。把每一类需求做成一张"完整图模板"必然僵化；只做底层 drawer 又缺少"如何组装"的
知识。因此采用三层结构：**全局技能底线 + 经典算子 + 命名技能配方**。

---

## 1 分层（从声明到像素到验证）

```
FigureSpec（声明层，figpipe/spec.py）      "这份数据应该画什么、为什么"
     ↓
Skill（配方层，figpipe/skills.py）         "用哪些算子、按什么顺序、验什么"
     ↓
Operator（经典算子层）                     "单用途、正交的经典变换"
     ↓
grammar / drawlib（绘制层）                "意图 → 面板；axes → 像素"
     ↓
composite（几何层）                        "毫米级版面"
     ↓
audit / score / styleprofile（验证层）     "合规、碰撞、统计、风格距离"
```

**关键区分：** `grammar` 的 intent 是"面板的语义角色"；operator 是"经典变换"；skill 是"一次完整
交付的配方"。新需求默认是**新配方**（组合既有算子），而不是新引擎。

---

## 2 全局技能底线（每个配方自动继承）

任何 skill 运行都会执行，不依赖配方是否列出：

1. **Nature 合规**：89/183 mm 栏宽、5–7 pt、嵌入字体（`verify.audit`）；
2. **字形级文字碰撞**（`verify.collisions`，旋转坐标标签不误报）；
3. **参数不静默忽略**：skill 未声明的参数直接 `SkillError`；
4. **可追溯**：返回 `trace`（用了哪些算子）与 `layout`（最终几何）。

---

## 3 经典算子（`figpipe/skills.py`，机器可读清单见 `knowledge/skills_catalog.json`）

| 算子 | 类型 | 作用 |
|---|---|---|
| `layout.plate` | build | 栏宽/高度/共享轴/字母/边距 |
| `encode.trend` | build | 点 + 区间 + 拟合 + 参考线（趋势） |
| `encode.ranked` | build | 排序柱 + 数值直标（构成） |
| `encode.density` | build | 双对数 hexbin + 边缘分布/色标（密度） |
| `encode.matrix` | build | 有正负矩阵 + 色标（矩阵） |
| `encode.box` | build | 分组箱线（分布比较） |
| `encode.bars` | build | 多测度分组柱（并列比较） |
| `encode.scatter` | build | 散点 + 拟合 + r（关系） |
| `style.profile` | build | 参考画像 → rc/配色/宽高比（风格迁移） |
| `verify.audit` | verify | 合规审计 |
| `verify.collisions` | verify | 字形碰撞 |
| `verify.statistics` | verify | 发表统计量对账（可设容差） |

算子只做一件事；需要新的编码方式时**才**新增算子，并在测试中给出正/负控制。

---

## 4 技能配方（当前 7 个）

| 技能 | 契约（必填） | 可选项 | 内部算子 | 验证 |
|---|---|---|---|---|
| `trend_with_uncertainty` | x, y | lo/hi/fit/band/reference/series/title/columns/height_mm/published/computed | encode.trend → layout.plate | 全局 + 统计 |
| `ranked_composition` | label, value | top/percent/xtick_rotation/columns/height_mm | encode.ranked → layout.plate | 全局 |
| `density_relationship` | x, y | marginals/colorbar/gridsize/columns/height_mm | encode.density → layout.plate | 全局 |
| `distribution_comparison` | group, value | columns/height_mm | encode.box → layout.plate | 全局 |
| `grouped_measures` | x, ycols | columns/height_mm | encode.bars → layout.plate | 全局 |
| `matrix_plate` | — | columns/colorbar/height_mm | encode.matrix → layout.plate | 全局 |
| `styled_trend` | x, y, profile | lo/hi/fit/band/reference/columns/height_mm/published/computed | style.profile → encode.trend → layout.plate | 全局 + 统计 |

每个配方带 `version`；机器可读目录由 `figpipe.skills.export_catalogue()` 生成，测试会检查目录与
代码一致（防 stale）。

---

## 5 如何加一个"变化的需求"

以"带误差带、图例在下方、共享 x 轴的三个面板"为例：

```python
from figpipe import skills, composite

# 1) 先判断能否用现有算子组合
#    style.profile / encode.trend / layout.plate / verify.audit 已够用
# 2) 不行才新增 operator，并写正/负控制测试
# 3) 新配方注册：
skills.define(skills.Skill(
    name="three_panel_trend",
    description="three trend panels sharing x, legend below",
    build=(("encode.trend", {}), ("encode.trend", {}), ("encode.trend", {}),
           ("layout.plate", {"columns": 2.0, "sharex": True, "letters": True})),
    required=("x", "y"),
    optional=("fit", "reference", "height_mm"),
    version=1,
))
```

运行时：未知参数直接报错；构建后自动跑全局验证；返回 PDF/PNG、findings、trace。

CLI：

```bash
python scripts/run_skill.py --skill trend_with_uncertainty --data d.csv --x year --y mean
python scripts/run_skill.py --list
```

---

## 6 与同行的差别（为什么这是"青出于蓝"的一层）

| 同行 | 做法 | 我们的差别 |
|---|---|---|
| FigMirror | 以 prompt/skill 文件描述 Drawer/Reviewer 循环 | 我们的 skill 可执行、可测试、参数契约化 |
| NaturePanelForge | 固定 pipeline（面板切分→Qwen→Codex） | 我们把 pipeline 拆成可组合算子，配方可增删 |
| DeTikZify | 模型 + MCTS，输出 TikZ | 我们复用其 MCTS，但算子是显式、可审计的 |

**原则：** 模型可以**提议** skill 或参数，但**验证与晋级**由确定性算子完成；这与项目既有的"模型
不得给自己的发现定标准"一致。
