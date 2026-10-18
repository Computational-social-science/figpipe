# 从真实 Nature 论文中学到的：经验、教训与规则修订

**日期：** 2026-10-18
**语料：** 本地 `D:\2026-AI4S` 下 42 个文件名含 NATURE 的 PDF，实测 38 篇，**420 个图区**，清洗后保留 **369 个**。

---

## 0. 先说教训：我此前做错了什么

### 教训 1：我曾试图从网上抓数据，而本地就有

我写了 Europe PMC 采集器，抓开放获取的 "Nature" 论文。用户指出：**本地就有 1425 个 PDF，其中大量是 Nature**。

**这是方法上的错误，不是效率问题。** 网络抓取引入了不可控的元数据质量，而本地语料是用户已经筛选过的。

### 教训 2："National science review" 是脏数据，不是 Nature

我最初用 `JOURNAL:Nat*` 检索，会把 **National Science Review**（《国家科学评论》，中国科学院主办，与 Nature 无关）一起捞进来。

**这类错误极危险**：它不会报错，只会让统计量悄悄偏移。现在代码里有一条显式的排除表：

```python
DIRTY_PATTERNS = [
    (r"national\s+science\s+review", "National Science Review -- a different journal entirely"),
    (r"natl\s+sci\s+rev",            "abbreviation of the same unrelated journal"),
    (r"nature\s+communications",     "a different journal in the Nature PORTFOLIO, not Nature"),
    (r"npj\s",                       "npj journals are a separate series"),
    (r"scientific\s+reports",        "different journal"),
]
```

**排除必须具名并给出理由**，否则下次还会犯。

### 教训 3：我此前的规则是"我的错误清单"，不是"Nature 的做法"

figpipe 原有 9 条规则全部来自我在本项目的调试经历（198.8mm 的图、8.4pt 的标题、3.15pt 的指数）。**没有一条来自真实发表的论文。**

现在有了对照，立刻暴露问题——见下。

---

## 1. 数据清洗：先排除物理上不可能的

原始 420 个图区里有：

| 排除类型 | 数量 | 理由 |
|---|---:|---|
| 宽度 > 210 mm | 29 | **不可能**——A4 页面只有 210 mm 宽，说明图区合并把整页连成一块 |
| 最小字号 < 2 pt | 22 | **不是正文**——数学上标或伪影字形 |
| 宽度 < 60 mm | 0 | 已在下游过滤 |
| **保留** | **369** | |

**如果不清洗，p90 宽度会报 200 mm、字号会报 0.91 pt——两个都是无意义的数字。** 而它们是"看起来很正常"的输出。

---

## 2. 实测结果：Nature 的实际做法

### 2.1 宽度分布（n = 369）

| 分位 | 宽度 |
|---|---:|
| p10 | 104.4 mm |
| p25 | 139.8 mm |
| **median** | **171.6 mm** |
| p75 | 183.5 mm |
| p90 | 200.0 mm |

**落在规定栏宽 ±3 mm 内的比例：**

| 目标 | 命中数 | 占比 |
|---|---:|---:|
| 89 mm（单栏） | 16 | 4.3 % |
| 183 mm（双栏） | 86 | 23.3 % |
| **任一栏宽** | **102** | **27.6 %** |

**这是一个重要发现：只有 27.6 % 的图区宽度接近 89 或 183 mm。**

### 2.2 最小字号（n = 188）

| 分位 | 字号 |
|---|---:|
| min | 3.0 pt |
| p10 | 4.0 pt |
| **median** | **5.0 pt** |
| p90 | 7.0 pt |
| max | 7.0 pt（注：8pt panel 字母被单独计入） |

**低于 5 pt 的比例：34.0 %**

---

## 3. 这些数字说明了什么（以及不能说明什么）

### 结论 A：Nature 的实际图**远比我以为的宽松**

我的 figpipe 规则要求"宽度必须精确 183.0 mm"，并把任何偏离视为不合规。

**但实测中位数是 171.6 mm，只有 27.6 % 落在规定栏宽附近。**

**可能的解释（尚未区分）：**
1. **我的测量方法有问题** —— "图区"是按绘图对象/图像的连通带自动识别的，可能与真实的 figure 边界不一致。Nature 的图常有多 panel，我的合并算法可能把 panel 间距算进了宽度，或把多个图合并。
2. **Nature 确实允许非标准宽度** —— 官网说的是"printed widths are 89/183 mm"，但 PDF 排版中图可能被缩放。
3. **语料包含非研究论文** —— 42 篇里有 1991/1997/2008 年的短文、评论（`Nature_So what's new.pdf` 等），它们的图版式与研究报告不同。

**我必须先排除解释 1，才能采信解释 2 或 3。** 这是当前最大的不确定性。

### 结论 B：5 pt 下限在真实论文中**并非普遍遵守**

**34 % 的图区存在 < 5 pt 的文字。**

这与官方规范（"minimum 5 pt"）矛盾。可能原因：
- 我测的是 PDF 中的**渲染字号**，而 Nature 的 5 pt 要求是**最终印刷字号**；PDF 可能以更大版面生成后被缩放
- 部分 < 5 pt 文字是上标、脚注、坐标轴次要刻度
- 语料中的非研究类文章

**这一条不能直接用于推翻规范**，但足以说明"按 PDF 渲染字号判定合规"是有缺陷的度量。

### 结论 C：我原来的 H02（留白比例 3.3–17.4 %）**不成立**

第一次看真实 Nature 图时，墨迹密度是 **35.8 %**，远超我"已验证"的 3.3–17.4 % 带。

**H02 是从我自己的 6 张折线图测出来的，被错误地泛化成"figure 的规律"。** 它必须降级。

---

## 4. 规则修订

| 规则 | 原状态 | 新状态 | 理由 |
|---|---|---|---|
| H02 留白比例 | measured_unenforced | **refuted** | 真实 Nature 图实测 35.8 %，远超 3.3–17.4 % 带；该带只适用于本项目的折线图 |
| L02 精确栏宽 | enforced | **维持 enforced，但限定作用域** | 规范确实要求 89/183；但实测只有 27.6 % 命中，说明"精确"是投稿要求而非观察到的普遍实践 |
| 新增 E01 | — | **hypothesis** | 真实 Nature 图的宽度中位数 171.6 mm，仅 27.6 % 落在规定栏宽 ±3 mm 内（n=369） |
| 新增 E02 | — | **hypothesis** | 34.0 % 的图区含 < 5 pt 文字（n=188），与规范的 5 pt 下限不一致 |

**关键区分：** L02 是"投稿时必须满足的要求"，E01/E02 是"发表后观察到的实践"。**两者可以同时为真且不同。** 把它们混为一谈是此前的核心错误。

---

## 5. 下一步（按能消除的不确定性排序）

### P0：验证测量方法本身

**当前最大风险是我的"图区检测"是错的。**

做法：手工标注 20 个图区的真实边界，与自动检测对比。
- 若吻合率 > 90 % → 结论 A 可信，继续
- 若 < 70 % → 重写检测器，此前所有数字作废

**在此之前，不应把 E01/E02 写成 verified。**

### P1：按论文类型分层

42 篇里有研究论文、评论、新闻、书评。**它们的图版式完全不同**，混在一起统计会掩盖真实分布。

做法：用 DOI/标题分类，只保留 research article 重新统计。

### P2：区分"PDF 渲染字号"与"印刷字号"

Nature 的 PDF 可能是放大生成的。做法：找到页面尺寸与最终印刷尺寸的比例，换算后再比较 5 pt。

### P3：扩充语料

38 篇的 369 个图区，对分位数估计偏少。目标 100 篇以上。

---

## 6. 一句话总结

**真实 Nature 论文的图，与我此前手写的"规范"不一致——不一致的方向是：Nature 比我宽松得多。**

但在我验证"图区检测"是否正确之前，这个结论本身也只是 hypothesis。**先怀疑测量，再相信结论。**

---

# 第二批：组图（2026-10-18 追加）

前六节都是关于"尺寸与字号"的度量。这一批的出发点是项目负责人的一句反问：

> "你在 templates 都是一张完整图片的局部，而非组图，而我们需要的往往是优雅的组图！组图，组图，组图"

这句话指出了能力缺口，而不只是风格问题：**六个模板各画一个 axes，等于六个"色卡"，不是一个"版面"。**

## 7. 组图是怎么做出来的

### 7.1 先分层，再组合

原来的模板函数自己 `fig.add_subplot(111)`，所以**物理上无法被组合**。现在拆成两层：

| 层 | 职责 | 例子 |
|---|---|---|
| DRAWER（`ax_*`） | 只在给定 axes 里画，不建图、不管边距、不写字母 | `ax_grouped_bars(ax, df, ...)` |
| TEMPLATE | 单张画布 + 边距 + 面板字母 | `grouped_bars(df, ...)` |
| COMPOSER | 版面：行列、跨格、间距、共享轴、字母 | `composite.composite(panels)` |

同一个绘制定义只存在一处（`drawlib.DRAWERS`），模板与组图共用它——否则"单图好看、组图变形"会变成两套需要同步维护的代码。

### 7.2 从真实 Nature 组图实测到的版面（`corpus/composite_layouts.json`）

方法不是"找空白列"，因为**右侧面板的 y 轴刻度文字就印在两块面板之间的空白里**，纯粹的空白带根本不存在。实际做法是锚定两个独立信号：

1. **面板字母**：从 PDF 文本层读出 8 pt 单字符文本，按行列聚类 → 面板数 + 初始边界；
2. **图注**：统计 caption 里点名的字母（`(a)`、`a,`、`a–c`、`Figure 1a`）→ 独立的面板数。

在 73 张真实图上：

| 量 | 结果 |
|---|---|
| 判为组图 | 36 / 73 |
| 内部分界线全部落在空白带（可验证） | 29 / 36 |
| 与图注字母数一致 | 24 |
| 面板间距 gutter（墨迹到墨迹） | 中位 **2.9 mm**（n=61，p25 1.6，p75 5.4） |
| 单个面板宽高比 | 中位 **1.34**（n=90） |
| 面板字母字号 | 中位 **8.0 pt**，46 个字母**全部**是 8.0 |
| 字母相对面板左边界 dx | 中位 **+2.0 mm**（n=46） |

最有用的一条是第二行：它说明"我检测到的分格是真的"，而不是我又在把测量当结论。

### 7.3 测量本身的两次自我纠错（都属"看起来有、其实无效"）

1. **图注交叉校验是 inert 的。** `figures_caption_anchored.json` 里的 `caption_text` 被截断到约 80 字符，里面永远不含 "a, b" → 字母数恒为 0 → 交叉校验**不可能失败**，也不可能通过。这正是本项目反复出现的第 5 类缺陷。修法：从 `caption_features.jsonl` 取全文图注，经 extraction manifest 用 (PDF 文件名, 图号) 关联，65/73 张拿到全文图注，校验才有意义（24 张一致）。
2. **"间距"不能从分界线量。** 分界线只是搜索落点，落在空白带哪一侧带有随机性；量出来的 0–39 mm 大量是伪值。改为**逐格量墨迹包围盒，相邻格墨迹到墨迹的距离**，才对得上"读者看到的缝"。

### 7.4 写组图引擎时被自己抓到 / 被拒绝的缺陷

| 缺陷 | 怎么发现的 |
|---|---|
| `ax_grouped_bars` 用了重构后不存在的变量 `y`，空 ylabel 时 NameError | 新加的 L08 机制检查**第一次运行**就抓到；演示图全部传了 ylabel，所以此前没暴露 |
| 3 个面板自动排成 2×2，右下留一个**空洞** | 组图检查拒绝"行列数乘积 ≠ 面板数"的版面 |
| 三连排量出 `[3.0, 59.5]` mm 的不均间距 | 把"第 1 与第 3 块之间的距离"误当 gutter；改为只计相邻格 |
| 旋转 32° 的模型名在底边被裁掉 | 目视检查；组图边距默认 9 mm 只够水平标签，改为可视情况给 16 mm |
| 热图沿用 `imshow` 默认的 −0.5…1.5 刻度 | 面板默认隐藏无意义刻度，有类别名时才显示类别名 |
| 图例压在最高柱子上 | 加 `headroom` 参数抬 y 上限（Nature 常见做法） |
| 图注/字号层面重复截断的列名（"Acc." 出现两次） | 图例出现两个同名项，改为第二次加序号 |

### 7.5 现在的产能

`scripts/render_composites.py` 用**论文自己的表格**渲染三张完整版面，并全部通过 `audit.audit` 与 `composite.check`：

| 版面 | 面板 | 尺寸 | 说明了什么 |
|---|---|---|---|
| `plate_eval_2x2` | 4（分组建模评估） | 183 × 148 mm | 标准四方格，三种图型混排 |
| `plate_mixed_1plus2` | 3（跨两列的宽面板 + 下方两块） | 183 × 132 mm | 不对称版面 + 面板内嵌色标 |
| `plate_shared_1x3` | 3（共享 y 轴） | 183 × 66 mm | 共享轴只标一次 |

知识库同步升级：**v16**，新增 **L08**（"a plate is not a swatch"），`mechanism_verified` 由 `composite_plate` 检查（真的组一张四面板图，再读回字母/间距/页宽），`empirically_measured` 由 `corpus/composite_layouts.json` 支撑。

## 8. 这一批的教训

1. **"能力"要用产物证明。** 模板能渲染 ≠ 能组图；组图能渲染 ≠ 版面正确。判据必须是"读回成品"的检查（字母数、间距一致性、页宽），不是"模块存在"。
2. **外部独立信号是测量可信的前提。** 面板字母（文本层）与图注字母（另一来源）互为校验；只有孔见一致时才把数字写进先验。
3. **先验必须带出处与 n。** `priors()` 返回 `source`、`measured`、`gutter_n`；读不到实测文件时明确标注 "built-in defaults"，而不是把默认值伪装成测量值。
4. **默认值必须能印出来。** 由实测宽高比推导的高度若超过 170 mm，默认路径会压到上限（而不是抛错），显式指定高度时才严格拒绝。

---

# 第三批：真实论文的"图版语法"（2026-10-18 追加，详见 SEED_REPRODUCTION.md）

种子是一篇真实论文（NHB 2026 国家影响力）的 PDF、7 张发表图、分析代码与 1.57 GB 原始数据。
目标不是抄七张图，而是从"每张图都非标准化"里提炼出可复用的语法，并**用统计量证明复现成功**。

## 9. 提炼出了什么

七张图拆到"这张面板在论证里承担什么角色"这一层后，只剩 4 种意图（`figpipe/grammar.py`）：
`trend_with_uncertainty`（5/7 张）、`ranked_composition`、`density_relationship`、`signed_matrix`。

复现判据不是"看起来像"，而是论文图注里的统计量：**15 项 r 全部复现到 ±0.005**（这个数字此前手写成 14，是文档错误；现在由 report.json 自动计数）
（Fig 3 的 6 项、Fig 5 的 4 项、Fig 7 的 4 项；Fig 1b 的 0.78 复现为 0.775，n = 10,046 一致）。

## 10. 这一批最硬的教训

1. **"看起来像"不是复现。** 只有重算的统计量对上，才证明模板携带了同一套编码，而不是像素模仿。
2. **不确定性有两种，语义不同。** `band="data"`（mean ± s.e.m.，带子随点起伏，原 Fig 3c）与
   `band="fit"`（拟合线自身的置信带，带子平滑，原 Fig 5/7）不能互换；混用等于错误陈述不确定性。
   因此两者互斥、缺参数即报错，而不是"有带子就行"。
3. **注释必须与画出的尺度一致。** 双对数图曾把原始值 r（+0.83）标在图上，而论文的 0.78 是对数
   尺度——图画的是对数云，标的就必须是对数相关。
4. **版式允许"没有字母"。** 原论文 Fig 5/7 用标题分面而非 a/b/c；组图检查原先硬性要求字母数等于
   面板数，会把这些合法版面判错。现在 `letters=False` 时不再要求。
5. **缺数据就写"未复现"。** Fig 2（QAP 系数不在数据包）、Fig 4（同类构造，省略）、Fig 6（缺国家→
   区域映射）明确记录在 `templates/seed/report.json`，而不是用近似数据凑一张像的图。

## 11. 复现过程中被检查抓到的缺陷（同一种形状：看着对、其实错）

| 缺陷 | 如何暴露 |
|---|---|
| 共享 x 轴时隐藏了底部面板而不是顶部，导致内层标题与上行 "Year" 重叠 | 目视检查 |
| `xlabel=""` 被当成"用列名"，内层面板仍打印轴标题 | 同一重叠；`""`（抑制）与 `None`（用列名）已分开 |
| 两系列注释画在同一点叠成一团 | 目视；`annotate` 现支持逐系列定位 |
| 双对数 r 用了原始尺度 | 统计核对 |
| marginal 直方图被计为第二个面板 | 自身几何检查 |
| 色标标题画出画布被裁 | 目视 |
| 定时任务把 1.57 GB 数据提交，push 被 GitHub 拒绝 | 推送日志；历史压缩后 `.git` 2049 MB → 191 MB |

## 12. 复现的边界：算术 ≠ 科学，且"优雅"是省略掉的工作量

详见 `REPRODUCTION_GAP_ANALYSIS.md`。三条最该记住的：

1. **复现必须声明层次。** 我们复现的是 L1（变换）+ L2（图），L0（OpenAlex → 词抽取 → 边表）用的
   是作者的成品；上游若有错，我们原样继承。说"复现了"而不说哪一层，是不可证伪的声明。
2. **"数字对上"不等于"复现成功"。** Fig 1b 的发表值 0.78 只有在**对数尺度**下才复现（0.775）；
   原始尺度是 0.83。当时我为了让数字对上换了估计量——这是凑数字，不是复现。现在两个估计量都记录
   在 `report.json.discrepancies`，并标注未解决。
3. **"优雅"不是天赋，是被省略的工作量。** 原图是作者对着渲染图多轮微调的结果（R 脚本里的手工
   坐标与重复 theme 就是证据）；我的复现反复出问题，根因是**组合接口** + **固定放置** + **检查器
   有洞**（复现渲染里 `check_overlap=False`，且 span 级 bbox 对旋转标签误报）。已用 glyph 级碰撞
   硬门槛、空角自动放置、图例外置来工程化地补上机械部分；剩下的迭代预算需要用"可测代理"继续压。




## 13. 同行版图（2026-10-18，详见 `PEER_LANDSCAPE.md`）

读了 FigMirror、NaturePanelForge、DeTi*k*Zify、Math-VR-CodePlot-CoT、ChartCoder 五个仓库后，
最重要的判断是**不要在它们的赛道上正面比**：它们把"像不像"交给 VLM 评审 + 迭代上限，需要大模型；
我们的位置应是"可测量、可搜索、可复现、可审计"。

已落地的第一步是 `figpipe/styleprofile.py`：**从 PDF 矢量对象直接测风格**（字号分布、字体、面板
字母、配色、线宽、框线），同输入同输出，无 GPU/API；`compare()` 给 0–1 距离并附 6 个可解释分量。
首测种子论文 Fig 7：发表 PDF 区 vs 我们的复现 **距离 0.158**，其中 sizes 0.367、palette 0.124——
"不像"主要来自字号档位与配色，**不是玄学美感**，可以在 5–7 pt 与 Okabe 色带内被搜索优化。

下一步不是多画几张图：把距离写进复现报告、由画像生成模板、用"硬门槛 + 距离 + 统计对账"做确定性
程序空间搜索（替代 VLM 评审循环），并建立**不依赖 VLM 的面板级可验证 benchmark**。

## 14. 从同行整合了什么（2026-10-18 晚）

- **代码级整合**：DeTi*k*Zify 的 MIT MCTS 整包 vendor 到 `third_party/mcts/`（保留许可与出处），
  `figpipe/search.py` 用它做探索策略、用我们的确定性奖励做评价；首跑把风格距离 0.456 → 0.416。
- **方法级整合**：NaturePanelForge（MIT）的 SciFigure2Code 维度表被实现为 `figpipe/score.py` 的
  确定性评分（8 个可测 + 4 个显式 N/A + 无效性声明），不再依赖 VLM 打分。
- **只用思想**：FigMirror（无许可）的 Drawer/Reviewer、preserve list、quality floor；Math-VR /
  ChartCoder（均无许可）的数据引擎与"代码即视觉思考"。未复制任何无许可代码或数据。
- **教训**：整合的门槛是许可与依赖，不是"看起来有用"。ImageSim 类评测器虽好，但要 torch+GPU，
  与"CPU、瘦身、可复现"的定位冲突——所以只借设计，不借依赖。

## 15. 可转化能力的证据（2026-10-18 晚，`style_transfer`）

不是"又多了两个模块"，而是输入→输出的转换：参考 PDF → 实测 profile → 派生合规样式 → 8 个变体渲
染/审计/测量 → 最佳成图 + 报告。种子 Fig 7 上风格距离 **0.122 → 0.093（−24%）**，硬门槛全过、结
果可复现。过程中由于"搜索对字号不敏感"暴露度量缺陷（1 pt 直方图桶），改为 Wasserstein-1 后修
复——**先让自己的度量可证伪，再谈能力提升**。

## 16. 专业报告（2026-10-18）

`reports/figpipe_capability_report.pdf|docx`：7 页能力验证报告（执行摘要 + 能力记分卡 + 同行汲取
矩阵 + 风格迁移前后对比与八变体距离图 + 权威基准 E2E 状态与协议 + 自进化审计 + 路线图 + 附录）。
所有数字由 `scripts/build_capability_report.py` 从仓库产物读取生成（测试数、知识库计数、距离、
探针统计），不手写；数据许可与未覆盖项在附录中声明。

## 17. PIPELINE v3：入口前移（2026-10-18 晚）

用户指出"表现远不尽人意、需重构整体框架、并在权威 benchmark 上 SOTA"。复盘后的结构判断：旧管线
**入口晚了一层**——从"已声明意图"开始，而同行基准从"参考图/面板 + 数据"开始。v3 见
`PIPELINE_V3.md`：L2 声明层（新 `figpipe/spec.py`，规则+理由+显式拒绝）、L3 参考理解（矢量已
有，PNG/参考代码待做）、L7 评测进化（基准 harness 与能力快照待建）。

同时修复：趋势面板遇到 datetime 轴时，matplotlib 会画 `×10^15` 偏差文本（4.2 pt，违反 5–7 pt
带）——改为日期数值 + ConciseDateFormatter 并隐藏 offset。**这是"真画一遍"才会暴露的缺陷，也是
重构必须从入口层开始的原因。**

## 18. 权威基准的首批端到端数字（2026-10-19）

`scripts/bench_plottwin.py` 在 **PlotTwin-Bench**（FigMirror，arXiv 2608.28814，CC BY-NC 4.0）
上跑了 10 个任务（官方参考图 + target_data，本地评测、不再分发数据）：10/10 成功执行，
风格距离（栅格可测的调色板/宽高比/墨迹密度）**0.378 → 0.268**，9 个改善、1 个变差；
best-of-two 0.252。这是**确定性指标**，不是官方 combined 分（后者需要其 VLM scorer）。

**必须记住的教训**：第一次运行时 styled 与 plain 的距离完全相同（delta=0.0）——因为 skill
的默认 height 覆盖了参考宽高比、且 palette 只施加到带 palette 参数的 drawer。**"看起来在
做风格迁移"和"真的改变了像素"是两回事**，修复后才有了上面的 0.11 平均改善。

决策模型接口：`figpipe/decision.py` 已接到共享的 StartLux-Decision 服务（`/v1/systemone`），
无静默回退（不可用即 `DecisionUnavailable`，无选项即 `DecisionRejected`）；服务当前未启动，
基准 harness 的映射回退路径已接好但未被真实调用——启动方式见 decision-service/scripts/serve.ps1。

## 19. Report format and language (2026-10-19)

The owner asked for an HTML report and for scientific work to be in English. `reports/figpipe_report.html`
is now the only report: one self-contained file (CSS inline, images as data URIs, no external CDN),
generated by `scripts/build_report.py` from the reproduction report, the style-transfer report, the
PlotTwin-Bench report, the skills catalogue, the knowledge base and the latest run record. DOCX/PDF
report artefacts and their builder were removed. A test fails if the report stops being English-only,
self-contained, or loses the benchmark evidence.

Report contents: progress overview with per-workstream percentages, research deliverables with
clickable repository paths, the three-figure style-transfer evidence, per-task PlotTwin-Bench results
and an inline SVG chart, the skills/operators catalogue, an honest self-evolution audit, remaining
risks and the next acceptance criteria.

## 20. Benchmark expansion and capability snapshot (2026-10-19)

Expanded PlotTwin-Bench from 10 to 30 tasks: 23/30 executed, deterministic distance 0.376 → 0.288
(Δ +0.088), 9 improved overall but by type the picture is mixed — Box/Violin +0.274, Scatter +0.316,
Std-band +0.107, Line +0.096, Distribution +0.055, **Heatmap −0.006 and Field 2D −0.090**. Six
failures are unsupported chart types whose map failed and the decision service was offline; one Line
task failed with `LinAlgError: SVD did not converge` because raw x values were in the 1e9 range and a
NaN poisoned the fit. Fits are now centred/scaled, drop non-finite pairs, and skip a degenerate fit
instead of killing the panel (regression test added). This is exactly the kind of defect that only a
real benchmark exposes.

The scheduled run now records a **capability snapshot** (`skills`, `operators`, benchmark tasks/ok/
mean distance, statistics reproduced, knowledge version, tests) plus an explicit delta, so "did the
project gain capability since last run?" is answerable from `latest_run.json` instead of inferred
from prose. Two tests pin the snapshot and the delta contract.

## 21. The scheduled loop now measures capability — and its first run failed honestly (2026-10-19)

The scheduled run initially failed for two reasons that are worth keeping in the record: pytest
output was decoded with the Windows locale and raised `UnicodeDecodeError`, and the report contract
test caught a `None` leaking into the capability-delta row. Both are fixed (`encoding="utf-8",
errors="replace"` for subprocess captures; explicit `—` formatting). A later run passed and recorded
the first capability snapshot:

    skills 12 · operators 16 · benchmark 23/30 · tests 228

with an explicit delta (`tests: — → 228` in the transition). This is the first time a scheduled run
answers "did the project gain capability?" from artefacts rather than from prose. The deeper lesson:
**the measurement machinery itself must be treated as a capability** — a capability snapshot that
crashes on a localised error message is not yet a control.


## 22. Benchmark-driven capability: polar + composite operators, capability regression guard (2026-10-19)

PlotTwin-Bench failures became operators, and the operators were validated on the benchmark:

| added | why | benchmark effect |
|---|---|---|
| `polar_profile` drawer + `POLAR_DRAWERS` projection flag | 13 Polar/Radial tasks had no operator; a polar axis is a projection, not a style parameter | Polar 0/1 → 1/1 (d=0.127) |
| `encode.error_bars`, `layout.split_panels` | Composite tasks carry several sub-figures in one long table | Composite 0/3 → 3/3 |
| unsupported-type classification | 3D has no operator and asking a model to choose among our skills would force a wrong answer | 2 tasks now report a REASON instead of a service error |
| bar label thinning above 24 bars | one tick per bar is unreadable and a numeric locator asks for thousands of ticks | removes the 1582/1978-tick warnings |

Aggregate: **28/30 executed, distance 0.361 → 0.287 (Δ +0.074)**, with per-type honesty:
Field 2D −0.090, Polar −0.043 and Heatmap −0.006 still get WORSE under style transfer.

The scheduled loop now also **fails on a capability regression**: `capability_delta()` carries a
verdict with `gains`/`regressions` and a direction table (higher-is-better vs lower-is-better, so a
smaller style distance counts as an improvement). A run that loses a judged capability field exits
non-zero unless the operator passes `--accept-capability-regression`. Recording a delta was not a
control; this is.


## 23. The scheduled run deleted the seed package and called it "no knowledge change" (2026-10-19)

The worst defect of the whole project, found by restoring state rather than by a test:

    commit 8b64e78  run: record scheduled evolution run (no knowledge change)
    ... deleted: the seed paper PDF, seven published figure PNGs, the authors' recipe
    (3.7 MB of INPUT that cannot be regenerated from this repository)

Cause: the publisher runs `git add -A`. The seed files were missing from the worktree at that
moment, so their absence was staged and committed as intent. No test covered "the scheduler must
not delete evidence", and the commit message asserted the opposite of what the commit did.

Fixes:
1. Seeds/ restored from the pre-deletion commit.
2. `cron_run.deletion_problems()` + `PROTECTED_PREFIXES`: a scheduled commit that would delete a
   file under Seeds/, corpus/style/, templates/seed/, templates/transfer/, knowledge/*.json or
   reports/ is REFUSED (everything is unstaged) unless `--allow-deletions` is passed explicitly.
3. A test stages a real deletion of a protected fixture and asserts the guard blocks it, then
   unstages and asserts a clean tree passes.

Lesson for the mission: an unattended loop needs guards against ACTIONS, not only assertions about
results. "It ran and reported success" is not evidence that it did the right thing.


## 24. 60 benchmark tasks measured, and a skill that could not run (2026-10-19)

Window 2 (tasks 31-60) exposed a defect the catalogue hid: `grouped_measures` passed the DRAWER
name `grouped_bars` to `grammar.panel()`, which expects an INTENT. Every grouped-bar task failed
with a KeyError while the skill sat in `knowledge/skills_catalog.json` looking healthy. The fix is
mechanical (build the panel through the composer, like `scatter_relationship` already did); the
lesson is not: **the catalogue advertised a capability that could not execute**, and nothing
checked. `tests/test_skills.py::test_every_registered_skill_can_actually_build` now runs EVERY
registered skill from its declared contract, so the catalogue cannot lie again.

Measured on 60 of the 150 PlotTwin-Bench tasks (deterministic metrics only):

| | value |
|---|---|
| executed | **53 / 60** (7 classified unsupported: 3D x5, Network/Tree x2) |
| mean style distance | **0.380 → 0.300** (Δ +0.080) |
| improved / worse / tie | **39 / 11 / 3** |

Per chart type (Δ): Box/Violin +0.255, Scatter +0.259, Std-band +0.141, Line +0.074, Bar +0.061,
Distribution +0.040, Composite +0.023, **Heatmap −0.039, Polar/Radial −0.043, Field 2D −0.112**.

The honest reading: style transfer is not universally good. For matrix-like targets (Heatmap,
Field 2D) copying a reference's palette/aspect makes our figure WORSE, because the reference's
appearance is driven by its own colormap and aspect, not by a transferable type tier. The next
capability step is not "always transfer" but "decide per task whether to transfer" -- which is
exactly what the best-of-two number (0.261) already hints at.

The scheduled loop now runs a rotating 6-task benchmark slice (`--skip-benchmark` to disable) and
records it in the run record, so capability is measured continuously instead of when someone
remembers.


## 25. The loop reported a capability regression that did not exist (2026-10-19)

The first scheduled run with the benchmark slice in the loop exited non-zero:

    capability regression: benchmark_mean_distance 0.278 -> 0.302

Nothing about the pipeline had changed. The benchmark SET had grown from 30 to 66 tasks, and the
slice happened to include harder windows (Field 2D −0.107, Heatmap negative). The guard worked
exactly as designed and was exactly wrong: it judged a metric whose value depends on the
measurement set rather than on the capability.

Fix: a stable ANCHOR metric -- the mean style distance over the first 20 task ids in sorted order.
It only moves when those tasks' results move, so it is comparable across runs. The raw mean stays
in the report (it is informative) but is deliberately NOT judged. `capability_delta` now carries a
comment saying why, and a test asserts that growing the task set leaves the anchor unchanged while
a genuine worsening moves it.

This is the second time in one day that the MEASUREMENT machinery, not the pipeline, produced the
wrong signal (the first was the size-distance histogram that could not see a 6.0 → 6.5 change).
A self-evolving system must audit its own instruments before it trusts their verdicts.


## 26. Counts are not capabilities (2026-10-19)

Right after fixing the false regression from a growing benchmark SET, the same defect appeared in
the opposite direction: `benchmark_ok` rose 65 → 70 in one run and the verdict recorded it as a
GAIN. Nothing had improved; six more tasks had been measured. A count inflates with coverage, and
coverage is not capability.

Fix: the judged field is now `benchmark_success_rate` (ok / attempted, where attempted excludes
tasks of unsupported chart types). `benchmark_tasks` and `benchmark_ok` remain in the record as
coverage facts but are excluded from the verdict, with a comment saying why. A test asserts the
exclusion and that a genuine rate drop is still caught.

Two measurement lessons in one day, both of the same family: **a metric whose value depends on the
measurement set is not a capability metric**. The raw mean moved with the set; the count moved with
the set; only the rate and the fixed-subset anchor are stable.


## 27. Deciding beats always transferring — but only when both numbers come from one instrument (2026-10-19)

The benchmark's own data said always-transferring cannot be optimal: of 70 measured tasks, transfer
helped 49 and hurt 15. So the pipeline now renders BOTH candidates and ships the one closer to the
reference. That decision is legitimate at inference time: the reference is an INPUT, not an answer
key about the data. `figpipe/select.py` is the general capability (given candidates and a target
style, pick one); the benchmark is one consumer.

Measured over the 28 tasks rendered with the decision in place:

| strategy | mean style distance |
|---|---|
| never style (plain) | 0.352 |
| always style | 0.278 |
| **decide per task** | **0.259** |

picked styled 22 times, plain 6 times.

THE MISTAKE THAT MADE THIS POSSIBLE TO TRUST: the first integration reported a shipped mean of
0.436 — WORSE than always-styled (0.278). A minimum of two numbers cannot exceed either of them, so
the number was impossible by construction. Cause: selection measured PDF profiles while the reported
distances came from cropped PNGs; two different instruments, two different numbers. After selecting
on the same PNGs the metric uses, the result became 0.259, which is consistent. The invariant
"shipped ≤ min(styled, plain)" is now a test.

That is the fourth measurement defect found in two days (1-pt histogram, raw mean over a growing
set, count-as-capability, and now mismatched instruments). The pattern is consistent: **the
instrument, not the pipeline, is usually what is wrong first.**


## 28. The loop was re-measuring tasks it had already measured (2026-10-19)

Run 43 landed on benchmark offset 12, whose six tasks had been measured hours earlier. The slice
offset was computed as `(runs * tasks) % 120`, which cycles rather than advances: the loop looked
busy, ran the benchmark every cycle, and grew nothing.

Fix: `bench_plottwin.covered_offsets()` reads which offsets' task ids are already in the report and
`next_uncovered_offset()` returns the first window that still contains an unmeasured task (wrapping
to 0 only when all 150 are covered). A test asserts the chosen window is not a subset of the
covered set.

This is the fifth self-measurement defect in two days, and the pattern is now unmistakable: **the
instruments and the scheduling of measurement are more likely to be wrong than the pipeline they
measure.** Recording a number every six hours is not the same as learning something every six hours.


## 29. The anchor was stable in name only (2026-10-19)

The "fixed 20-task subset" anchor moved 0.297 -> 0.329 on a run that only added coverage. Cause: it
was defined as "the first 20 task ids in sorted order", which is stable only while no new id sorts
earlier than an existing one. The moment the loop walked into the Chart2Code block, six new ids
entered the anchor set and the metric changed with no capability change -- a false regression, the
second one produced by the same anchor idea.

Fix: the anchor ids are FROZEN in `knowledge/benchmark_anchor.json` on first creation and reused
forever. A test appends a new id that sorts first and asserts the anchor set and its value do not
move. The current anchor (0.329) is therefore the value over those 20 specific tasks, whatever else
gets measured later.

Also restored two tests that a careless edit had dropped (shipped-distance and slice coverage) --
a reminder that deleting tests is a capability regression too, and it was invisible until the count
was checked.

The loop's next run then behaved correctly: it walked to an uncovered window, measured 6 new tasks,
shipped distance improved 0.269 -> 0.257, no regressions, exit 0.


## 30. The same defect, a third time: a mean over a growing set (2026-10-19)

Run 44 exited 1 with:

    capability regression: benchmark_shipped_distance 0.257 -> 0.258

A 0.001 change on a run that only added six tasks. The shipped mean is averaged over the tasks that
carry a selection decision, and that set grows as coverage advances -- so it moves whenever a task is
added. This is the THIRD appearance of one defect family in one day:

    raw mean over a growing set          -> false regression 0.278/30 -> 0.302/66
    count (benchmark_ok) over a growing set -> false GAIN 65 -> 70
    shipped mean over a growing set      -> false regression 0.257 -> 0.258

Each time the fix is identical: judge a metric over a FROZEN task subset. `benchmark_shipped_anchor.json`
now freezes 20 task ids for the shipped metric, exactly as `benchmark_anchor.json` does for the
always-styled metric. The full-set means stay in the record for information and are explicitly NOT
judged, with the reason written beside the direction table.

Rule extracted, and now applied twice: **any judged metric must be a function of a fixed task set.**
If a metric's denominator can grow, it is a measurement, not a capability.
