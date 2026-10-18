# 种子复现：一篇真实 Nature 论文的图版 → 可复用的绘图语法

**日期：** 2026-10-18
**种子：** `Seeds/0001/`（NHB 2026, *The growing concentration of national influence in global
science and its impact on future research*）+ `E:\2026-AI4S\dataverse_cache\0001\`（原始 1.57 GB
数据；见 `Seeds/README.md` 为何移出仓库）

---

## 1. 为什么"非标准化"的图也可以提炼出共性

七张发表图初看各不相同：排序柱、双对数密度、带误差带的时序、四宫格、红绿弧形关系图、
区域矩阵。逐张抄代码只能得到七个一次性的产物。**把它们拆到"这张面板在论证里承担什么角色"这一
层，重复就出现了：**

| 面板意图（intent） | 覆盖的图 | 它要编码的东西 |
|---|---|---|
| `trend_with_uncertainty` | Fig 2、3c、4、5、7（7 张里 5 张） | 一个量随时间变化，且**不确定性必须可见**：点、误差带、拟合线、参考线、角落的 r |
| `ranked_composition` | Fig 1a | 每个实体占多少份额，**排序**，数值直接印在柱上 |
| `density_relationship` | Fig 1b | 上万个点、两个量、跨数量级：用**密度**而不是散点，并声明相关 |
| `signed_matrix` | Fig 6b | 有正负的矩阵，缺失格要明显区别于 0 |
| `comparison_with_error` | —（旧模板） | 少量实体 + 不确定性的比较 |
| `distribution` | —（旧模板） | 分布形态 |

这就是本项目的"抽象层次高于某一项具体工作"：新论文的图不再写成几十行 matplotlib 调用，而是
**声明它由哪些意图的面板组成**，由 `figpipe.grammar` 把意图映射到绘制器、契约和版式。

---

## 2. 复现判据：不是"看起来像"，而是**统计量对得上**

原论文在图注里给出了每张图的统计量（r、n）。复现脚本从**原始数据**重算，逐项比较：

| 图 | 指标 | 论文值 | 本仓库重算 | 差 |
|---|---|---|---|---|
| Fig 1b | 项数-引用数相关系数（log-log） | 0.78（n = 10,046） | **0.775**（n = 10,046） | −0.005 |
| Fig 3a | Gini 与年份 r（归因） | 0.88 | **0.876** | −0.004 |
| Fig 3b | Gini 与年份 r（话语） | 0.86 | **0.857** | −0.003 |
| Fig 3c | 核心国家中心性 r（归因） | 0.98 | **0.982** | +0.002 |
| Fig 3c | 边缘国家中心性 r（归因） | 0.87 | **0.868** | −0.002 |
| Fig 3c | 核心国家中心性 r（话语） | 0.99 | **0.985** | −0.005 |
| Fig 3c | 边缘国家中心性 r（话语） | 0.86 | **0.855** | −0.005 |
| Fig 5 | Core→Core | 0.88 | **0.884** | +0.004 |
| Fig 5 | Core→Periphery | 0.47 | **0.471** | +0.001 |
| Fig 5 | Periphery→Core | −0.43 | **−0.431** | −0.001 |
| Fig 5 | Periphery→Periphery | 0.43 | **0.431** | +0.001 |
| Fig 7 | Core→Core | 0.96 | **0.958** | −0.002 |
| Fig 7 | Core→Periphery | 0.66 | **0.659** | −0.001 |
| Fig 7 | Periphery→Core | −0.62 | **−0.624** | −0.004 |
| Fig 7 | Periphery→Periphery | −0.69 | **−0.686** | +0.004 |

14 项统计量全部在 ±0.005 以内。**这不是"风格相似"，而是同一批数字算出来了。**

产物：

```
templates/seed/fig1_term_papers_and_density.pdf|png      183 × 96 mm，2 面板
templates/seed/fig3_centrality_and_gini.pdf|png          183 × 168 mm，4 面板
templates/seed/fig5_relative_influence.pdf|png           183 × 168 mm，4 面板（标题分面）
templates/seed/fig7_national_signature_mimicry.pdf|png   183 × 168 mm，4 面板（标题分面）
templates/seed/report.json                               每个面板的审计 + 复现差值
corpus/seed/derived/*.csv                                从原始数据算出的面板数据（小文件）
```

四张成品都通过 `audit.audit`（字号/栏宽/嵌入字体）与 `composite.check`（字母、间距、越界）。

---

## 3. 复现过程中被检查抓到的缺陷（这才是"学习"的部分）

| 缺陷 | 怎么暴露的 |
|---|---|
| 共享 x 轴时**隐藏了底部**而不是顶部面板的刻度与轴标题，导致内层面板标题与上行 "Year" 文字重叠 | 复现图目视检查；根本原因是"哪一行是外层"写反了 |
| `xlabel=""` 被抽屉当成"用列名"，于是本该无标签的内层面板仍打印 "Year" | 同一处重叠；修法是把 `""`（抑制）与 `None`（用列名）分开 |
| 两个系列的相关性注释画在同一点，文字叠在一起 | Fig 3c 目视检查；`annotate` 现在接受 `(text, x, y)` 给每个系列单独定位 |
| 双对数图注释的 r 用的是**原始值**相关（+0.83），而论文值 0.78 是**对数尺度**相关 | 统计核对；注释必须与画出的尺度一致，已改为按绘制尺度计算 |
| 边缘直方图被 `composite.inspect` 当成第 2 个面板，导致"2 面板但 1 个字母" | 自身几何检查；marginal 轴标记 `_figpipe_marginal` 后不计入面板 |
| 色标标题画在画布外被裁掉 | 目视检查；色标标题改为可选，图 1b 不设标题（与原图一致） |
| 学习阶段一次定时任务把 1.57 GB 数据 `git add` 进历史，push 被 GitHub 拒绝（pre-receive hook） | 推送日志；历史被压成不含大文件的等价提交，`.git` 从 2049 MB 降到 191 MB |

---

## 4. 提炼出的"可迁移知识"

1. **先看语义，再看坐标。** 同一篇论文 5/7 张图是同一个"时序 + 不确定性 + 参考线 + r"句式。把
   这种句式命名（intent）之后，模板才可被检索和复用。
2. **不确定性有两种，不能混。**
   - `band="data"`：区间来自数据（如 mean ± s.e.m.），带子随每年的点起伏（原 Fig 3c）；
   - `band="fit"`：区间是拟合线自身的置信带，带子平滑地环绕曲线（原 Fig 5、7）。
   混用会错误陈述不确定性，因此两者互斥且缺参数即报错。
3. **拟合方法按论证需要选择。** 中心性面板用线性 `lm`；Gini 面板用三次 `poly3`；二元组面板用
   局部回归 `loess`。这三种都来自原论文 R 代码，不是自选。
4. **版式可以复用测量值。** 复现图的栏宽/高度/间距由 `composite` 的实测先验决定（见
   `corpus/composite_layouts.json`），标题分面版（无 a/b/c 字母）也被允许——
   `letters=False` 时不再要求每面板一个字母。
5. **不要为了复现而编造。** Fig 2（QAP 系数）、Fig 4（同类构造，省略）、Fig 6（弧形图 + 区域矩
   阵，缺少国家→区域映射）没有复现，原因写在 `templates/seed/report.json` 的
   `not_reproduced` 里，而不是用近似数据凑一张像的图。

---

## 5. 复用方式

```python
from figpipe import grammar

panels = [
    grammar.panel("trend_with_uncertainty", df,
                  x="year", y="mean", lo="lo", hi="hi",   # 数据区间
                  band="data", fit="lm", reference=0,
                  xlabel="Year", ylabel="z-score"),
    grammar.panel("ranked_composition", shares, label="country", value="share",
                  top=20, percent=True),
]
fig = grammar.plate(panels, columns=2.0, sharex=True, sharey=True, letters=False)
```

运行复现（先派生数据，再出图）：

```
python scripts/reproduce_seed.py --stage derive    # 读原始 CSV，约 2 分钟
python scripts/reproduce_seed.py --stage render    # 出图 + 审计 + 统计对比
```

派生步骤把 639 MB 的归因影响边表分块聚合，结果缓存于 `corpus/seed/cache/`（可再生、不进版本
库）；面板数据（小）在 `corpus/seed/derived/`，附带 `manifest.json`（输入文件的大小/哈希/
时间戳），以便证明"这些数字来自那份数据"。

---

## 6. 与既有知识库的关系

- 格式规则（栏宽、字号、字体、面板字母）仍是 `figpipe.style` + `audit` + 知识库 L01–L08 的职责；
- 本文件记录的是**编码语法**（用什么图表达什么论证），两者不混为一谈；
- 种子论文的版面特征（栏宽 183 mm、四宫格、标题分面、误差带 α = 0.25、r 注在角落）作为**惯例**
  写进 `figpipe.grammar.SEED_CONVENTIONS`，每条都注明出处（发表图或 R 代码）。
