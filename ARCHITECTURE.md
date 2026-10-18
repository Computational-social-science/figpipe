# 架构：简洁性、冗余消除、以及逻辑决策的边界

**日期：** 2026-10-18

---

## 1. 结构瘦身（测量，不是印象）

### 做了什么

| 项 | 之前 | 之后 |
|---|---:|---:|
| `scripts/` 脚本数 | 22 | **13** |
| 孤儿脚本（无人调用、无测试） | 12 | **3** |
| `figpipe/` 模块 | 11 | **9** |

### 三类改变

**A. 一次性迁移 → `archive/`（保留证据，移出主路径）**

```
migrate_kb_v2.py     知识库 schema v1→v2        已应用到 v14
void_old_corpus.py   作废 E01/E02、更正 E01 数字  已应用
ingest_corpus.py     折叠语料发现（H02 证伪）      已应用
ingest_captions.py   折叠 C01–C04                已应用
add_checks.py        给规则写 check 块            已应用
close_gaps.py        严重级别与负面测试修复        已应用
```

**为什么归档而不是删除**：它们是知识库当前状态的**来源证明**。删掉后，"为什么 H02 被标为 refuted"就只剩结论没有过程。

**B. 已被证伪的实现 → 删除**

| 脚本 | 删除理由 |
|---|---|
| `learn_from_corpus.py` | 测量的是**旧的启发式检测器**的产物；审计已判定该检测器 ~50% 错误 |
| `derive_rules.py` | 同上，其清洗逻辑基于错误输入 |
| `render_figures.py` | 被 `extract_corpus.py` 的 docling 裁剪取代 |

**C. 旧检测器模块 → `archive/`**

| 模块 | 理由 |
|---|---|
| `figdetect.py` | 自建启发式（图注锚定），已被 docling 取代；无任何代码引用 |
| `bandfilter.py` | 为修正 figdetect 的物理不可能值而写；检测器归档后失去意义 |

**保留的 3 个孤儿**是**可重跑的分析工具**，不是残留：
`validate_extraction.py`、`verify_detector.py`、`analyse_captions.py`——它们能重新产生证据。

---

## 2. 逻辑决策的边界（审计结果）

`scripts/inventory_decisions.py` 枚举了 figpipe 里全部 **10 处判断**：

| ID | 问题 | 确定性 | 准确性已知 | 可用决策模型 |
|---|---|---|---|---|
| J01 | 哪个区域是 figure | 否 | 部分（5/5 目视） | ✅ |
| J02 | 哪个图注属于哪个图 | 否 | 否（196 全配但仅抽查） | ✅ |
| J03 | 开头句是总述还是 panel walk | 否 | 否 | ✅ |
| J04 | 这是什么类型的图 | 否 | 否（38% 未分类） | ✅ |
| J05 | 这个值物理上不可能吗 | **是** | 精确 | ❌ |
| J06 | 截断轴是 FAIL 还是 WARN | **是** | 精确 | ❌ |
| J07 | 这个色图是 rainbow 吗 | **是** | 已测量（jet/viridis 验证） | ❌ |
| J08 | rcParams 合规吗 | **是** | 精确 | ❌ |
| J09 | 这个路径可再生吗 | **是** | 精确 | ❌ |
| J10 | 这条规则该强制还是仅观察 | 否 | 否 | ❌ **禁止** |

### 结论

- **5 个是确定性的**：路由到语言模型只会增加延迟和一个新的错误来源。**继续用代码**。
- **4 个真需要判断**（J01–J04）：这些是决策模型的**唯一候选**。
- **1 个明确禁止**（J10）：**模型不得决定自己的哪些发现算作标准**。H02 的教训正是如此——一个测出来的规律被当成了要求。

---

## 3. 决策算子：共用，不私用

`E:\2026-AI4S\decision-service` 是**独立项目**，不是 figpipe 的子包。

### 为什么必须分开

| 关注点 | 归属 |
|---|---|
| 哪个模型、哪个量化、哪个端口 | **decision-service** |
| 在显存里驻留多久 | **decision-service** |
| "confidence 0.62" 是什么意思 | **decision-service** |
| 某个 pipeline 问什么问题 | 调用方 |

若客户端嵌在 figpipe 里，其他项目要问一个 yes/no 就必须 import figpipe 的语料、知识库和瘦身规则。

### 模型选择（有依据）

| 决策 | 选择 | 理由 |
|---|---|---|
| AutoThink vs Instant | **AutoThink** | DecisionPivot **+18.4**；该指标是"只差一个决定性细节"的配对准确率，正是本项目要问的问题形态 |
| Q8_0 vs Q4 | **Q8_0** | README：Q8 基本保持 BF16 性能，Q4_K_M 最多掉 4.3 分；4B 的 Q8 约 4.3 GB，12.9 GB 显存装得下 |
| 4B vs 27B | **4B** | 27B 的 Q4 约 17 GB，超显存；4B AutoThink Decision Index 68.21 |

### 唯一的硬规则：**不得静默降级**

服务不可达时 `decide()` **抛 `DecisionUnavailable`**，绝不返回正则结果。

这不是洁癖。本项目已经四次撞上"控件看起来在、实际不起作用"：
- `.gitignore` 规则对已跟踪文件无效
- 回归检测只覆盖 3/8 规则却报 "3/3 hold"
- QC 声称读调色板却什么都没读
- Startup 的 `.ps1` 被 Windows 静默忽略

**一个在模型离线时悄悄返回正则结果的客户端，就是第五次。**

`tests/test_client.py` 用 7 个测试锁死这条规则。

---

## 4. 下一步的边界条件

1. **先部署，再讨论集成**。没有跑通的算子，任何"引入"都是纸面动作。
2. **J01–J04 必须先在人工标注集上量出基线**，否则无法证明模型比现有正则更好。当前这四个判断的准确性**全部未知**——这是引入模型的前提，不是结果。
3. **J10 永不外包**。

---

## 5. 组图引擎（2026-10-18 追加）

### 5.1 为什么是"新一轮剔除"，而不是加模块

原有六个模板各建一个 axes，互相不可组合——这是**结构问题**，不是缺一个函数。改法是把"画什么"与"摆在哪"分开：

```
figpipe/drawlib.py     DRAWERS: ax_*（只画进给定 axes） + TEMPLATES（单面板包装）
figpipe/composite.py   Panel / composite() / inspect() / check()
```

因此 `figpipe/` 模块数 9 → **11**（新增 `drawlib`、`composite`），但**职责边界更少而不是更多**：绘制定义只有一处，模板与组图共用 `DRAWERS`；不存在"组图专用画法"的第二套实现。

### 5.2 几何放在毫米里算，不用 gridspec 分数

`wspace` 是"平均 axes 宽度的比例"，与直觉差一次减法；用 `wspace` 猜出来的间距，事后无法保证。`composite()` 直接以 mm 计算每个 axes 矩形，再换算成 figure 分数——确定性、可测、与 matplotlib 的布局规则无关。成品由 `inspect()` 读回：页宽、面板盒、间距、字母、越界。

### 5.3 先验来自真实组图，且带出处

`corpus/composite_layouts.json`（`scripts/measure_composites.py` 产出）记录 73 张真实 Nature 图的面板结构：29/36 组图可通过"分界线落在空白带"的检验，gutter 中位 2.9 mm（n=61），面板宽高比 1.34（n=90），46 个面板字母**全部** 8.0 pt。

`composite.priors()` 读该文件，返回 `source` / `measured` / `gutter_n`；文件存在但损坏时**抛错**，不静默回退。

### 5.4 检查必须读成品

`composite.check()` 的判据是：页宽 ∈ {89,183} mm、高度 ≤ 170 mm、每面板恰好一个 8 pt 字母、所有相邻间距一致、无越界。知识库 **L08** 的机器检查 `composite_plate` 会真的组一张四面板图再读回——它第一次运行就抓到 `ax_grouped_bars` 在空 ylabel 下的 `NameError`（重构遗留），而三张演示图全部传了 ylabel，所以此前无人发现。

### 5.5 体积

新增：`composite.py` + `drawlib` 重构 + 测量/渲染脚本 + 12 张校验覆盖图 + 3 张成品 PDF/PNG，tracked 约 +1.3 MB。运行 `scripts/slim.py`：tracked 74.0 MB / worktree 76.6 MB，仍在 80 MB / 150 MB 预算内。

### 5.6 下一步的边界

1. **组图复现尚未闭环**：当前三张版面用真实表格数据，但**不是某一篇论文原图的逐面板复现**。`Seeds/0001`（NHB 七面板论文 + R 复现脚本）是下一个目标，原始数据已移出仓库（见 `Seeds/README.md`）。
2. **面板字母偏移的 dy 未采用实测值**：实测以"格边界"为参照，而 composer 以 axes 顶边为参照，两者差一个 gutter，直接套用会把字母压进面板。dx 可用，dy 保持常量并在代码里写明原因。
3. **共享轴 + 跨格目前互斥**：跨格时列内 axes 未必同尺度，宁可拒绝也不猜。

---

## 6. 图版语法层（2026-10-18 追加，详见 `SEED_REPRODUCTION.md`）

### 6.1 为什么还要再加一层

`drawlib` 回答"用哪些像素"（`bar_with_errors(df, x, y, err, ...)`），`composite` 回答"摆在哪"。
但"这个面板在论证中承担什么角色"没有位置存放，于是每篇论文的图仍是一堆绘图参数。种子论文的七张
图提供了证据：它们看似各不相同，拆到**面板意图**这一层后只有 4 种，其中一种覆盖 5/7 张。

### 6.2 结构

```
figpipe/grammar.py      INTENTS: intent -> drawer + 数据契约 + 实测惯例
figpipe/drawlib.py      idiom drawers: trend_band / ranked_share / hexbin_corr / tile_diverging
scripts/reproduce_seed.py   用真实原始数据重算面板，并与论文统计量比对
corpus/seed/derived/    派生面板数据（小，可版本化）+ manifest（输入哈希/时间戳）
corpus/seed/cache/      639 MB 边表的分块聚合缓存（可再生，不进版本库）
templates/seed/         4 张复现版面 + report.json（统计比对与审计）
```

模块数 11 → 12（`grammar`）。与 `drawlib` 的分工是：**grammar 不画任何东西**，它只把语义意图翻
译成 drawer + 契约；所有像素仍只由 `drawlib` 一处产生。

### 6.3 复现作为验收

`templates/seed/report.json` 记录 15 项发表统计量与本仓库重算值的差（全部 ≤ 0.005）。复现未成功
的 Fig 2/4/6 连同原因一并记录——**缺数据时写"未复现"，不用近似数据凑图**。

### 6.4 对既有模块的修改（都是被复现逼出来的）

| 修改 | 原因 |
|---|---|
| `composite(letters=False)` 合法 | 原论文 Fig 5/7 用标题分面而非 a/b/c |
| 逐面板 `letter_dx_pt` / `letter_dy_pt` | 带边缘直方图的面板，字母需上移越过直方图 |
| `_figpipe_marginal` 轴不计入面板 | 边缘分布属于一个面板，不是第二个面板 |
| 色标标题可选 | 平移出画布会被裁掉；原图 1b 没有色标标题 |
| `trend_band` 区分 `band="data"` / `band="fit"` | 原论文两种误差带语义不同（mean±s.e.m. vs 拟合置信带） |
| `""` 与 `None` 在轴标题上分开 | `xlabel=""` 应抑制标签，而不是回退到列名 |

### 6.5 体积与预算

新增约 1 MB（4 张版面、派生数据、文档；639 MB 缓存不进库）。`scripts/slim.py` 度量仍在
tracked ≤ 80 MB、worktree ≤ 150 MB 的预算内。

### 6.6 下一步边界

1. **Fig 4 已具备条件**：`corpus/seed/derived` 里已有相对影响力中心性，只差一行组装；留作验证
   "模板可复用"的最短路径。
2. **Fig 6 需要国家→区域映射**（原 R 用 `raster::ccodes` + 自定义 UNREGION1 表），该映射不在数据
   包内。宁可标注为缺口，也不凭空构造区域。
3. **`trend_band` 的 loess 带是近似**：tricube 局部线性 + 全局残差方差替代 loess 的逐点方差，已
   在代码与文档中写明，不得表述为与 ggplot2 loess 等价。
