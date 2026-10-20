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


## 31. The cache guard measured half the cache, and pruning broke coverage (2026-10-19)

Two more instrument defects, found by watching the worktree budget rather than the pipeline:

1. `prune_cache()` counted only the task JSON, not the reference images, so it reported 34 MB while
   66 MB sat in the worktree; the worktree reached 147 MB of its 150 MB budget. A guard that
   measures half of what it guards is the same defect as a metric over a growing set.

2. Images are named by TASK ID while the cache is named by OFFSET, so the pruner unlinked
   `<offset>.png` -- which never existed -- and left every reference image orphaned.

3. Worse: pruning the cache made `covered_offsets()` return an EMPTY set (it derived coverage from
   the cache), so the next scheduled run would have restarted the benchmark from offset 0 and
   re-measured everything. Coverage is now defined by the REPORT (`measured_ids()`), with an
   offset->id index written as a side effect of fetching; the chooser self-heals if the cache is
   pruned again.

All three are the same lesson in a new place: **a derived quantity must be derived from the durable
artefact, not from a cache.** The report is the artefact; the cache is an optimisation.


## 32. A style metric cannot see a wrong number (2026-10-19)

Every check in this project until now inspected appearance or geometry: `audit` (width, type size,
fonts), `styleprofile` (palette, sizes, aspect), `score` (NPF dimensions). None of them re-derived a
number from the data. A pipeline optimising style could therefore ship a perfectly formatted figure
printing "r = +0.80" over data whose r is −0.20, and nothing would notice.

`figpipe/semantics.py` closes that gap deterministically:
  * `check_annotations` -- the printed r must match the drawn data's r (tol 0.02, the printed
    precision); a missing r is reported when one is required
  * `check_extent` -- no drawn point may fall outside the visible axes; silently clipping an
    outlier changes the claim ("no point above 0.9" is not "the axis stops at 0.9")
  * `check_marks` -- the number of drawn marks must equal the rows the panel claims
  * `check_labels` -- labels must be the ones the panel says they are

It is now part of the GLOBAL FLOOR, so every skill run is checked; the benchmark records
`semantic_violations`; the report shows the count next to the style distance. Tests use negative
controls (a false r, a clipped outlier, a wrong label) because a check that cannot fail is not a
check.

Scope is stated rather than implied: it verifies the claims OUR drawers make. It is not a semantic
parser for arbitrary figures, and applying the point-count check to heatmaps/fields/bars would
produce false failures -- which is how checks get switched off -- so it is limited to point drawers.


## 33. A real regression the loop caught, and the bug it exposed (2026-10-19)

The scheduled run exited non-zero with three genuine regressions:

    benchmark_success_rate          1.00 -> 0.99
    benchmark_anchor_distance       0.329 -> 0.356
    benchmark_shipped_anchor_distance 0.247 -> 0.269

This time the alarm was CORRECT. Diagnosing it found a bug in the style-transfer layer itself, not
in the new field operator:

**The derived height ignored the canvas width.** `style_from_profile` computed the height from a
hard-coded 183 mm and then the skill drew a 89 mm single-column figure, so the aspect was wrong by
~2x. The style components proved it: every Field 2D task had an `aspect` component of **0.74-0.75**,
while two-column Line tasks had **0.001**. The operator was fine; the style transfer was ruining it.

Fix: `style_from_profile(..., columns=)` derives the height from the width the candidate will
actually be drawn at (183 mm for two columns, 89 mm for one), and `skills.run` passes its own column
count. Result on Field 2D:

    before: styled 0.501  plain 0.441  delta -0.060   (worst chart type)
    after : styled 0.343  plain 0.441  delta +0.098   (a clear gain)

Three lessons, in order of importance:

1. **The regression guard paid for itself.** It caught a defect that no test would have found,
   because every test rendered at a single column width.
2. **A new operator can be blamed for an old bug.** Field 2D got WORSE the moment it switched to
   `field_map`, but the operator was correct -- the style layer had been silently distorting every
   single-column figure, and the old `matrix_plate` path happened to have a matching aspect by luck.
3. **Component-level diagnostics localise a regression in seconds.** `aspect: 0.75` on every task of
   one type, and `0.001` on another, named the defect without reading any code.


## 34. One shared bug was making two chart types look bad (2026-10-19)

After the canvas-width fix (##33), Heatmap was re-measured and flipped as well:

    Heatmap before: styled 0.355  plain 0.334  delta -0.021   (blamed on matrix_plate)
    Heatmap after : styled 0.247  plain 0.333  delta +0.086

The Heatmap rows had been measured BEFORE the fix -- they were stale, and their component
breakdown still showed the signature: `aspect` 0.66-0.95 on nearly every task, versus 0.001 on
two-column figures. One bug in the style layer had been making TWO chart types look like operator
failures.

After re-measuring the stale rows, **no supported chart type is negative**:

    Scatter +0.235  Box/Violin +0.172  Std-band +0.135  Field 2D +0.098  Line +0.088
    Heatmap +0.086  Distribution +0.047  Bar +0.046  Composite +0.023  Polar +0.006

Also fixed while measuring Polar:
  * the mapper chose `panel_row` (95% NaN bookkeeping) as the measured value -> "has non-finite
    values"; a measure must now be >=80% finite and rows are dropped before drawing
  * a dropped connection (WinError 10054) is now retried like a 5xx instead of crashing the scan

METHOD NOTE, now the third time it has paid: **stale rows are a measurement defect too.** Re-running
a fixed operator over a report that still holds pre-fix numbers makes the fix look like a regression.
Before concluding anything about a chart type, check whether its rows were rendered after the last
change to the shared layer.


## 35. Staleness is now a queryable fact (2026-10-19)

Field 2D and Heatmap both looked broken because their rows predated the canvas-width fix. The
lesson from ##34 was "check whether the rows are stale" -- which is a guess until the rows say so.

Every task row now records `code_version`: a 12-char fingerprint over the files that render figures
(drawlib, skills, styleprofile, composite, the harness). The report states how many executed tasks
were measured with an earlier fingerprint, and `--types X --scan` re-measures a whole type after any
change to the shared layer.

Current state after the fix, all measured on the SAME fingerprint:

    125/134 executed, 0 errors, 9 classified unsupported
    Scatter +0.235  Box/Violin +0.172  Std-band +0.135  Field 2D +0.098  Line +0.088
    Heatmap +0.086  Distribution +0.047  Bar +0.046  Composite +0.023  Polar +0.006
    NO chart type is negative any more.

Two milestones reached this round:
  1. every supported chart type now benefits from style transfer (was 2 negative types)
  2. the selection step is measured on 96 tasks: shipped 0.237 vs always-styled 0.264 vs plain
     0.349 -- deciding beats transferring by 0.027 and beats not styling by 0.112.


## 36. "Unknown" is not "stale" (2026-10-19)

The staleness signal fired on 129 of 141 rows and was wrong. Diagnosis: 117 rows were measured
BEFORE the `code_version` field existed, so `t.get("code_version") != CODE_VERSION` was true for
them forever. A row whose fingerprint was never recorded may well have been rendered by the current
code -- we simply cannot prove it.

`freshness()` is now three-valued: fresh / stale / unknown, reported separately. `stale_tasks()`
returns only the rows KNOWN to have been rendered by a different fingerprint.

This is the same error class as collapsing a missing measurement into a passing one -- which this
project already refuses to do for knowledge rules (`ok=None` for UNCHECKED). The rule generalises:
**absence of evidence must be its own value, not the negative of the claim.**

Benchmark pool COMPLETE this round: 141/150 executed, 9 classified unsupported (3D x7,
Network/Tree x2), 0 errors, success rate 1.0.


## 37. The OFFICIAL scorer was reachable all along (2026-10-19)

The project has been saying "the official score needs a VLM, so we report deterministic metrics"
for several rounds. That was WRONG in an important way.

Reading the benchmark's own scorer source (`corpus/e2e/official_scorer/`, fetched from
`figmirror/PlotTwin-Bench`) shows it is `S = 0.35 * S_code + 0.65 * S_vision` and that
`score_code_deviation()` is **fully deterministic** -- AST analysis of a matplotlib script over nine
dimensions (palette, background, aspect, linewidth, grid, spines, tick direction, serif, legend
frame). No model, no API, no GPU. The 35% channel was always runnable; the missing piece was that
figpipe could only RENDER figures and the scorer reads CODE.

What was built:
  * `third_party/plottwin_scorer/` -- the code channel vendored unmodified (CC BY-NC 4.0, local
    evaluation only, NOT in the wheel; NOTICE.md states the licence and why the VLM half is absent)
  * `figpipe/codegen.py` -- emits runnable matplotlib code from a skill's panels, including the
    data as literals so the script actually runs
  * the harness extracts the REFERENCE's own style features with the official extractor and emits
    a candidate that reproduces them, then scores the pair

First measured results on 15 tasks: **mean 92.68 / 100, range 68.86-100.0.**

Three things this taught, and they generalise:

1. **"We cannot run the official scorer" was an assumption, not a measurement.** One HTTP fetch
   and a read of the source disproved it. The claim had been repeated in reports for days.
2. **The honest claim is narrower than it looked, and stronger.** We report the 35% channel by name,
   never the combined score. That is a defensible number produced by THEIR code, not ours.
3. **The score is high because the emitter copies the reference's features by construction.** That
   is legitimate for a style-transfer benchmark -- the reference is the input -- but it must be
   stated plainly: this measures fidelity of style reproduction, not scientific judgement.

Also fixed: the task cache held rows written before `reference_code` was fetched, so the official
channel could only see 2 of 141 tasks. A cache entry missing a required field is now refreshed
instead of silently reused -- the cache version of the staleness lesson.


## 38. A judged field the snapshot never emitted (2026-10-19)

I added `benchmark_official_code_score` to `CAPABILITY_DIRECTION` and reported "the official score
is now a judged capability". It was not: `capability_snapshot()` never returned the field, so
`capability_delta()` saw nothing to judge. The loop would have reported "no change" if the official
score halved.

This is the exact defect the project has fought since its first audit -- **a control that looks
present and does nothing** -- reappearing in the capability system itself, one commit after I wrote
a lesson about measurement defects.

Fix: the snapshot emits the field; a test asserts `set(CAPABILITY_DIRECTION) <= set(snapshot)` so a
judged-but-unmeasured field can never happen again. Second test confirms the official score is
recorded and judged in both directions.

Verified: the next run recorded `benchmark_official_code_score: 92.68` in the capability snapshot.

The general rule, now enforced by test: **every field the system claims to judge must be a field it
actually measures.** Claiming a capability check without wiring it is worse than not claiming it,
because it makes the absence invisible.


## 39. The 100.0 was a tautology, and catching it mattered more than the number (2026-10-19)

After wiring the official scorer I measured a pool-wide **100.0 / 100** and was one sentence away
from reporting it as SOTA. It was not a capability:

  the task record ships `reference_code`, so extracting the style from that code and emitting a
  script with the same style reproduces every scored dimension BY CONSTRUCTION.

Using the reference code is legal -- it is part of the task. But it measures "can the emitter copy
a spec", not "can the pipeline infer a style from a picture", which is the benchmark's actual
premise (`reference image + new data -> figure`).

The honest measurement, style inferred from the reference IMAGE only:

    image-inferred  mean 70.59 / 100  over 149 tasks   <- the number worth reporting
    code-copied     mean 100.00 / 100 over 149 tasks   <- a ceiling, not a capability

Both are now produced by `scripts/score_official.py --source {image,code}` into SEPARATE files, and
the report states the ceiling beside the honest number with the word "ceiling" attached.

Closing the gap found real, recoverable signal: grid lines and spines ARE visible in a raster as
long straight runs of ink, so `StyleProfile.from_image_detailed` detects them deterministically
(interior rules = grid, edge rules = spines). That alone moved the honest score 61.11 -> 71.16 on
the first 20 tasks. Ticks, serif, legend frame and linewidth remain undetermined from pixels, and
the scorer penalises them -- that penalty is real and is reported, not hidden.

Lessons, in order:
1. A number that cannot be wrong is not a measurement. If the answer key is in the input, the score
   is a tautology.
2. The gap between the tautology and the honest number IS the capability being measured.
3. Two modes writing to one output path silently destroyed the honest result once. Output identity
   follows input identity.

Benchmark state: 141/150 executed, no negative chart type, styled anchor 0.305, shipped 0.252,
official code channel (image-inferred) 70.59, official code channel (code-copied ceiling) 100.00.


## 40. Two numbers for one concept, and a correction that looked like a regression (2026-10-19)

The loop failed after the official-scorer work, and both causes were instrument defects:

1. **The capability read a different number than the report.** `cron_run` took the official score from
   the harness's in-run aggregate (93.53 -- it scores only tasks whose cache entry currently carries
   reference_code), while the honest pool-wide pass said 70.59. Two numbers for one concept is how a
   metric stops being trusted. The capability now reads the dedicated pass, and a test asserts they
   match.

2. **The correction tripped the regression guard.** 93.53 -> 70.59 is not a capability loss: the
   first number was the tautology (copying the reference's own code features) and the second infers
   style from the picture. The guard was right to fire and wrong to fail the run.

   Fix: `KNOWN_CORRECTIONS` records a documented correction WITH its reason, and the verdict reports
   it under `corrections` rather than `regressions`. It is not a mute switch: a field without a
   documented reason still fails, and a test pins both halves.

Also fixed this round, from a REAL budget failure (tracked 80.04 MB > 80 MB limit):
  6 duplicate ingests of the same paper were found by comparing FIGURE SIGNATURES (content.md
  differed only in the source-path header, so hashing it missed them). Removing them recovered
  4.98 MB and brought tracked size to **75.05 MB** -- under budget by real cleanup, not by raising
  the limit.

Final state: 285 passed / 2 skipped, official code channel (image-inferred) 70.59 over 149 tasks,
ceiling (code-copied) 100.00, styled anchor 0.305, shipped 0.252, tracked 75.05 MB.


## 41. The official score is measurable, and three of my "fixes" were wrong (2026-10-19)

Started the round at 70.59 and ended at **75.41** over 149 tasks. The +4.82 came from exactly two
real fixes; three other attempts were wrong and were reverted or corrected. Recording both halves.

WHAT WORKED
1. **Per-dimension diagnostics.** The records stored dimension NAMES but not their scores, so "70"
   said nothing about which choice was wrong. Adding `dimension_scores` produced the ranking:
   tick_direction 0.0, serif 0.0, linewidth 0.43, palette 0.48, aspect 0.85, grid 0.88,
   spines 0.97, legend 1.0. That single change turned a number into a work queue.
2. **Palette extraction was broken, not merely lossy.** `from_image` used PIL adaptive
   quantisation, which reported light blues and greys (#85bbda, #b9d4e5) for a figure whose actual
   ink is #262626, #000000 and #2a7ab9. Nothing could ever match, so the dimension scored 0.47 while
   looking measured. Taking dominant colours from the real pixels and raising the cap from 8 to 24
   (references carry 3-28 colours) moved palette 0.478 -> 0.648 and the mean 70.59 -> 75.41.

WHAT I GOT WRONG (kept in the record on purpose)
1. **Naive "dense row = rule" detection.** A skymap has almost every row dense, so a density
   threshold found 683 "rules" in one image. Replaced with LOCAL CONTRAST (a rule is dense while its
   neighbours are not): the same skymap yields 2, a sparse line figure 0.40/0.36.
2. **Stroke-width estimation.** I converted pixels to points at an assumed 400 dpi. The reference
   renders carry no dpi metadata and vary between roughly 104 and 343 dpi, so estimates of 0.36 pt
   sat against true widths of 0.42-1.38 pt and the dimension got WORSE (0.432 -> 0.244). Reverted:
   linewidth is now reported as undetermined, with the measurement that justifies it.
3. **A too-permissive stroke filter.** The first version reported 688 px on a skymap -- that is a
   filled region, not a line. Only runs under 12 px count as strokes.

Remaining undetermined from a raster: tick_direction (needs a visible spine and clean margin),
serif, background (a raster's page colour is usually just white), linewidth. Their scores are 0 and
they are 3-4 of the activated dimensions, so they cap the achievable number. That ceiling is a
property of the INPUT MODALITY, not of the pipeline, and is now stated as such.

State: official code channel (image-inferred) **75.41** over 149 tasks; ceiling (code-copied)
100.00; benchmark 141/150 executed; styled anchor 0.305; shipped 0.252.


## 42. A frozen task set is not enough: the rows must share one instrument (2026-10-19)

The loop reported the shipped anchor improving 0.252 -> 0.243 and called it a gain. It was not.

The anchor is a frozen set of 20 task ids -- but the ROWS inside it had been measured by different
versions of the measurement code. Only 3 of the 20 had been re-measured after the styleprofile
palette fix, so the mean moved because the INSTRUMENT changed, not the capability. This is the FIFTH
variant of the same defect family:

    raw mean over a growing set          -> false regression
    count over a growing set             -> false gain
    shipped mean over a growing set      -> false regression
    "first N sorted ids" anchor          -> false regression when new ids sort earlier
    frozen ids with MIXED fingerprints   -> false gain

Fix: `_shipped_anchor_single_instrument()` reports the mean over rows measured by the CURRENT
fingerprint, plus `n_same_instrument` / `n_other_instrument` / `comparable`. When the anchor is not
fully re-measured the value is **None**, not a small-sample number that reads as a gain. The judged
capability field is that single-instrument value; the all-rows value is recorded but never judged.
The report shows "—" with a note explaining exactly why.

Rule, now stated as a general invariant: **a judged metric must be a function of a fixed task set
AND a single instrument version.** Freezing the set but not the instrument is the same error one
level down.


## 43. Fixing one metric field left the identical defect one field over (2026-10-19)

Last round I made the SHIPPED anchor single-instrument and left the STYLED anchor untouched. It
carried the same defect, and it surfaced immediately: after restoring the shipped anchor the loop
failed with

    regression: benchmark_anchor_distance 0.305 -> 0.316

15 of the styled anchor's 20 tasks were on an older fingerprint. Same family, sixth instance.

Fix, applied symmetrically this time:
  * `_anchor_single_instrument()` mirrors `_shipped_anchor_single_instrument()`
  * both all-rows values are recorded but NOT judged; both single-instrument values are judged
  * `--ids` re-measures exactly the frozen anchor tasks (a targeted refresh), and
    `ensure_coverage_index()` rebuilds the id -> offset map if it was pruned
  * `refresh_anchor()` in the loop re-measures the anchor automatically when it is non-comparable,
    and is a no-op when it is -- so the loop heals itself instead of reporting "—" forever

Both anchors are now comparable: styled 0.329, shipped 0.293, 20/20 rows on one instrument each.

LESSON: when a defect is found in a metric, audit EVERY sibling metric in the same commit. Fixing
one instance and shipping is how the same bug reaches production twice. The generalised invariant,
now enforced for both anchors: **a judged metric must be a function of a fixed task set AND a single
instrument version.**

Also learned: the targeted refresh needs the id -> offset index, which had been pruned with the data
cache. Coverage is a durable fact; it now has its own few-KB index that the pruner never touches and
a rebuild path if it is lost.


## 44. 75.41 was a number without a referent (2026-10-19)

For two rounds the project reported "official code channel 75.41 / 100" and treated it as progress.
It was not evidence of anything: with no baseline, the number can neither support nor refute a
claim of beating anyone. A score is only a claim when it is stated against a referent.

Three points are now measured on the SAME 149 tasks with the benchmark's own scorer:

    baseline  38.16   matplotlib defaults + figpipe's compliance floor
    pipeline  75.41   style inferred from the reference IMAGE (the benchmark's premise)
    ceiling  100.00   style copied from the reference CODE (a tautology)

**Improvement over baseline: +37.25 points, 97.6% relative.** The remaining 24.59 points to the
ceiling are the dimensions a raster cannot recover (tick_direction, serif, background, linewidth).

Per dimension (baseline -> pipeline):
    palette        0.002 -> 0.648   (+0.646)   <- the dominant gain
    grid           0.000 -> 0.829   (+0.829)   <- the other dominant gain
    figure_aspect  0.480 -> 0.869   (+0.389)
    spines_removed 0.874 -> 0.965   (+0.091)
    linewidth      0.574 -> 0.574   (+0.000)   <- unchanged: undetermined from pixels
    legend_frame   1.000 -> 1.000   (+0.000)
    tick_direction / serif / background         <- 0.0 both: not recoverable from a raster

The `comparison()` helper returns all three points together and a test asserts the ordering
baseline < pipeline < ceiling AND that all three cover the same task count. A single number can no
longer be quoted without its referents.

LESSON: "improved" is a relation, not a property. Every metric in this report now needs a baseline
in the same table, or it is decoration.


## 45. The reusable surface was hidden, and the example found a real bug (2026-10-19)

The project has claimed for many rounds that its capability is "reusable in research scenarios".
It was not demonstrable:

* `figpipe/__init__.py` exported THREE modules (style, layout, audit) while the package contained
  twenty-three. `spec`, `skills`, `select`, `semantics`, `codegen` -- the capabilities the last ten
  rounds were spent building -- were unreachable without knowing internal paths.
* `examples/` was an empty directory. No one could run the pipeline on their own data.

Both are now fixed: fifteen modules are exported with a docstring that names the five entry points
in increasing order of ambition, and `examples/worked_example.py` runs the WHOLE pipeline on an
invented dataset (spec -> recipe -> render -> audit -> semantics -> codegen -> select) and exits
non-zero unless every claim it prints was verified.

THE EXAMPLE IMMEDIATELY EARNED ITS PLACE by finding a real defect:

    spec.infer_spec declared `grouped_bars`
    the example drew a TREND panel            <- the declaration was decorative
    ... after making it follow the spec:
    grouped_measures produced 3 HARD failures (text collisions)
    while `audit` reported 0                  <- audit checks typography, not label duplication

Cause: `encode.bars` drew ONE BAR PER ROW. A long table has many rows per category (40 rows over 2
groups), so it stacked 40 overlapping bar groups and the tick labels collided. A grouped bar
encodes a SUMMARY per level; the aggregation was missing entirely. Now it aggregates (mean by
default), refuses an unknown aggregator, and writes the aggregation into the trace.

Two lessons:
1. **A capability that is not exported and not demonstrated is not reusable, however good it is.**
   "We built X" and "you can use X" are different claims.
2. **An executable example is a test, not documentation.** This one found a drawing bug that
   thirteen rounds of internal tests did not, because it exercised a path (long table ->
   grouped bars) that the benchmark's aggregated data never produced.

Suite: 294 passed, 2 skipped.


## 46. The grouped-bars bug was a CLASS of defect, not an incident (2026-10-19)

The worked example found that `encode.bars` drew one bar per ROW. The obvious response was to fix
that function. The correct response was to ask what else had never been fed real research data --
every internal test used already-aggregated frames, so the path "long table -> any drawer" was
untested for EVERY skill.

`scripts/audit_skills_data.py` runs all 16 skills over 7 realistic data shapes (long format, wide
one-row-per-category, time series, replicates, sparse with missing values, single observation per
level, a genuine 2-D field) -- 19 cases -- and classifies each as ok / refused / BROKEN / CRASHED.
A skill that renders the wrong thing is worse than one that refuses.

IT FOUND TWO MORE REAL DEFECTS:

1. `matrix_plate` on a 48-row field table. The drawer received the long table directly and drew a
   48-row matrix, whose tick labels all collided ("'41' over '42'"). A long table is not a matrix;
   it is now pivoted onto its first two numeric columns, with the pivot written into the trace, and
   an unpivotable table is refused with a pointer to `field_map`.

2. `composite_groups` drawing 20 year-bars on one axis. My first fix looked for DUPLICATE labels --
   but `year` is unique per panel, so nothing was aggregated and 19 collisions remained. The actual
   defect is TOO MANY bars: an axis cannot carry 20 readable tick labels at 6 pt in an 85 mm panel
   whatever the rotation. A category budget (12) now REFUSES with the better encoding named
   (a trend panel), because drawing it hides the problem.

Final state of the audit: 18 ok, 1 refused, 0 BROKEN, 0 CRASHED. The refusal is the correct
outcome for a bar panel asked to show 20 ordered years.

LESSON, and it generalises past this project: **fixing the instance is not fixing the class.** One
example-driven bug should trigger a systematic sweep over the input space, not a single patch. The
sweep is now a test, so the surface cannot silently rot again.

Suite: 295 passed, 2 skipped.


## 47. My own fix caused a regression the loop caught within one cycle (2026-10-19)

Last round's `matrix_plate` fix refused any table over 24 rows that could not be pivoted. It guessed
the pivot keys as "the first two numeric columns", which on one benchmark task were
`panel_row`/`panel_col` -- bookkeeping with ONE distinct value each. The pivot came out 1x1, the
skill refused, and a task that had rendered for weeks became an error.

The scheduled run caught it in the very next cycle: `benchmark_tasks 141 -> 140`, one task in
`error`. Two lessons, both already written down and both violated anyway:

1. **A fix is a change; a change needs the same evidence as the original.** The pivot was never
   run against the tasks that exercise it before being committed.
2. **Refusing is only correct when refusal is better than the old behaviour.** Here it was worse:
   the previous output was imperfect but valid.

Fix: the pivot now SEARCHES for a column pair that actually varies (and a value column distinct from
both), maximising the resulting grid. If no 2-D reading exists it falls through to drawing the frame
as-is up to 40 rows, and only refuses beyond that. Re-measured: 141/150 with 0 errors restored.

ALSO FIXED IN THE SAME CYCLE
  * `refresh_anchor()` checked only the SHIPPED anchor and reported "already comparable" while the
    STYLED anchor was stale -- the identical "fix one, forget the sibling" mistake as last round.
    It now heals both and names which were stale.
  * a test had `import pytest` inside a function, shadowing the module-level name (third time this
    exact bug has appeared in this file). `pytest` is now imported once at module level and the
    local imports are gone.

State after healing: styled anchor 0.351, shipped anchor 0.296, both 20/20 on one instrument;
benchmark 141/150 with 0 errors; official 75.41 vs baseline 38.16 (+37.25). Suite: 296 passed.

The pattern across the last four rounds is consistent and worth naming: **every defect since the
official-scorer work has been in the verification or healing machinery, not in the drawing code.**
The pipeline draws correctly; what keeps breaking is how the project decides whether it does.


## 48. Adversarial sweep of the modules every recent fix touched (2026-10-19)

The data-shape audit covered the SKILL layer. Every fix of the last four rounds landed in
`styleprofile`, `codegen` or `select` -- none of which had been run against inputs that are not the
benchmark's. `scripts/audit_robustness.py` is the systematic version: 26 adversarial cases over
degenerate images (blank, solid, pure noise, 1-pixel dimensions), malformed styles (NaN/inf/zero/
negative aspect, a string where a number belongs), missing files, empty candidate sets and
single-candidate selections. Each case must be HANDLED (with the value checked) or REFUSED with a
specific message -- never silently wrong.

IT FOUND TWO FABRICATED CLAIMS:

1. **A blank and a noise image reported FOUR SPINES.** `np.convolve(mode="same")` divides by the
   full kernel even where it runs off the ends, so the first and last entries of a UNIFORM signal
   come out as high "contrast" (measured 0.444 on a solid black image). The profiler claimed
   structure that does not exist. Fixed by recomputing the edges with the truncated window that
   actually applies there: blank/solid/noise now report 0 rules, 0 spines, no tick direction.

2. **A non-finite `figure_aspect` emitted `figsize=(7.2047, nan)`** -- a script matplotlib cannot
   render, reported as a success. Now refused for NaN, inf, zero, negative and non-numeric values.

AND ONE TEST BUG, which is its own lesson: the "normal figure" fixture drew its grid line at grey
200 while the ink threshold is `< 200`, so the fixture silently tested nothing. A test that cannot
fail is not a test -- the same rule this project applies to knowledge rules, applied to fixtures.

Final state: 26 cases, 16 HANDLED (values checked), 10 REFUSED (specific messages), **0 BROKEN**.
The sweep is now a test, so the surface cannot silently rot.

This is the third layer swept systematically (skills -> benchmark -> robustness). The order was not
planned; it followed the evidence of where the defects actually were.


## 49. The report contradicted the evidence for several rounds (2026-10-19)

The official scorer was integrated, measured, and given a baseline two rounds ago. The report was
still saying:

    "Stated plainly: this is not an SOTA claim ... a formal claim requires ... the official scorer
     (at least its non-VLM subset) ..."
    "Official scorer not integrated: no combined-score SOTA claim is possible."
    "chart types for 110/150 tasks are mapped"

All three were FALSE. The scorer is vendored and measured on 149 tasks; 141/150 tasks execute; and
a claim with a baseline and a ceiling now exists. Nothing noticed, because no test compared the
report's prose against the artefacts.

Fixed:
  * the stale warning became a precise statement: the official code channel scores X against a
    baseline of Y, with the ceiling shown, and no combined-score claim
  * the obsolete "not integrated" risk became the real remaining limit (vision channel out of
    scope)
  * the next-steps card "P1 · Integrate the non-VLM scorer subset — Planned" became
    "DONE · Official non-VLM scorer integrated — Delivered"
  * `CLAIM.md` now holds the claim, its referents and its LIMITS in one place
  * `tests/test_claim.py` pins both halves: the numbers in CLAIM.md must match the measured
    artefacts, the limits must be stated, and the report must not carry the stale phrases again

The general lesson, and it is the same one as the metrics: **a document is a derived artefact and
must be tested against its source, or it becomes a fossil that contradicts the system it
describes.** The report is generated, but its PROSE was hand-written and hand-written prose does
not update itself.

State: 303 passed / 2 skipped; official code channel 75.41 vs baseline 38.16 (+37.25, 97.6%);
ceiling 100.00; benchmark 141/150.


## 50. The snapshot read a half-written state (2026-10-19)

The run exited 1 with `benchmark_anchor_single: null` and `benchmark_shipped_anchor_single: null`
in the capability snapshot, while the report on disk held 0.351 and 0.296. Both anchors were
comparable; the snapshot simply read the report BEFORE the measurement that writes it had finished.

The loop's order was:

    anchor_run = refresh_anchor()     <- may rewrite the report
    bench_run  = benchmark_slice()    <- may rewrite the report
    caps = capability_snapshot()      <- reads the report

...which looks correct until you notice `refresh_anchor()` re-measures the anchor AFTER new rows
land, so the slice must run FIRST. The snapshot is now taken at the moment the record is written,
after every measurement, and re-diffed after the test suite so the test count is current too.

Also: the run reported `303 -> 302 passed` and flagged it a regression. That was a genuine
difference -- one test had turned into a SKIP under the loop's environment. A skip is not a pass,
and a shrinking suite can hide behind "still green", so `test_a_skip_is_not_counted_as_a_pass`
now asserts the collected count stays >= 300.

The 14-minute suite runtime was NOT a defect: a background job of mine was competing for the
machine. Measured clean: 73 s.

Same lesson as the metrics, one layer out: **reading state is a measurement, and a measurement has
an order.** The snapshot must be taken after every write it depends on, or it reports a state that
never existed.


## 51. The lean budget punished a correct concurrent run (2026-10-19)

Re-measuring the whole benchmark pool (150 tasks) downloads ~70 MB of reference images into
`corpus/e2e/images`. The pruner ran only at the END of a pass, so during the pass the worktree grew
to 156 MB and `test_worktree_is_within_budget` failed -- for doing exactly the right thing (caching
inputs) at the wrong time.

Two fixes, and they are different in kind:
1. The benchmark now prunes DURING a pass (every 20 downloaded images), so the cache stays bounded
   at all times rather than only at the end.
2. The lean test EXEMPTS the two input caches (`corpus/e2e/images`, `corpus/e2e/cache`) from the
   worktree budget. They are inputs that their owning script bounds itself; counting them makes a
   correct concurrent run look like a leak.

The distinction matters: fix (1) is about the code's behaviour, fix (2) is about the TEST's
definition. A budget that cannot distinguish "leak" from "input cache in use" is measuring the
wrong thing, which is the same defect family as every metric issue in this project -- one layer
further out, in the test suite itself.

Also written this round: `LOGICAL_AUDIT.md`, which answers the objective's "does the pipeline have
theoretical or logical defects" by TYPE of argument (measurement validity, reference class, input
assumptions, verification completeness, state and timing, scope) rather than by list of bugs. Its
verdict is deliberately not "no defects": the defect rate in the verification layer is higher than
in the drawing layer, and that is where the remaining risk lives. `tests/test_logical_audit.py`
checks that each claimed fix is still present in the code, so the audit cannot become a fossil.


## 52. The benchmark is now measured entirely on ONE instrument (2026-10-19)

Re-measuring all 150 tasks took ~70 minutes (network fetches dominate; the machine was shared).
Result:

    report     141/150 executed, 0 errors
    freshness  141 fresh, 0 stale, 0 unknown      <- the last incomparable metric is gone
    anchors    styled 0.351, shipped 0.296, both 20/20 on one instrument
    official   baseline 38.16 -> pipeline 75.41 (+37.25, 97.6%) | ceiling 100.00
    negative   chart types: none

This closes the last measurement gap named in the previous rounds. Every judged number in the
project now comes from one code fingerprint, one task set, and one scorer.

The remaining ceiling is unchanged and is a property of the INPUT: tick_direction, serif,
background and linewidth score 0 or unchanged because a raster image does not contain them. The
honest statement is that the pipeline recovers everything a picture CAN show (palette 0.648,
grid 0.829, aspect 0.869, spines 0.965, legend 1.0) and nothing a picture cannot.


## 53. The verification layer, swept at last (2026-10-19)

LOGICAL_AUDIT.md names the verification layer as the project's highest-risk area, and until now
`audit` and `composite` had only ever been tested on GOOD figures. A verifier tested only on correct
input has not been tested at all -- the question is whether it can be fooled.

`scripts/audit_verifiers.py` plants each defect the project exists to catch and asks whether it is
caught, in both directions:

  FALSE NEGATIVE (certifies broken output):
    sub-5 pt text ................ CAUGHT (font_size finding)
    wrong width .................. CAUGHT (width finding)
    Type-3 fonts ................. CAUGHT (font_type finding)
    a real glyph collision ....... CAUGHT (1 collision)

  FALSE POSITIVE (teaches users to ignore it):
    a correct figure ............. PASSES (0 hard findings)
    rotated tick labels .......... NOT reported as collisions (0)

  composite refuses invalid geometry, each with a message naming the problem:
    overlapping cells, negative position, half-positioned grid, span collision,
    empty plate, colour bar on a non-mappable drawer -- 6/6 refused
    and a correct plate still passes its own geometry check

Result: 13/13 cases ok. The layer the audit flagged as riskiest holds up under the sweep that the
audit said was missing.

The residual risk is unchanged and is stated: these negative controls were written by the same
author as the checks. A sweep cannot find a blind spot it shares. That is why the earlier
independent `CRITICAL_AUDIT` rounds mattered, and why an external review is still the only real
mitigation for shared blind spots.


## 54. A scheduled failure that cannot be diagnosed (2026-10-19)

The run exited 1 with `tests_ok: false` and `tests_summary: "1 failed, 310 passed"`. That is all it
said. The identity of the failing test was LOST, because `run_tests()` kept only the last line of
pytest's output -- so the only way to find out was to re-run the whole 80-second suite by hand.

That is a diagnosability defect, and it is worse in a scheduled context than an interactive one: an
unattended loop that reports "something failed" without saying what is a loop nobody can repair.
`run_tests()` now captures the FAILED/ERROR lines and records them alongside the summary:

    1 failed in 0.37s | FAILED ...::test_this_must_fail

Proven with a deliberately failing test, and pinned by a test so the capture cannot regress.

THE FAILURE ITSELF was contention, not a defect: I had a full 150-task benchmark running
concurrently with the loop, and the suite's timing-sensitive tests failed once under load. Running
the suite twice in isolation: 312 passed both times. The loop then passed with `ok: true`.

Worth recording as a standing hazard: **this machine runs one measurement at a time.** Two heavy
runs sharing it produce results that are neither reproducible nor trustworthy, and the loop cannot
distinguish that from a real regression. The mitigation is procedural (do not start a pool-wide
re-measure while the loop is due), not code -- stated rather than silently tolerated.


## 55. A procedural rule became an enforced one: one measurement at a time (2026-10-19)

Last round recorded a hazard instead of fixing it: "this machine runs one measurement at a time;
two heavy runs produce untrustworthy results, and the loop cannot distinguish that from a real
regression. The mitigation is procedural." A procedural rule that nothing enforces is not a control
-- that sentence could have been written about any of the eleven defects found before it.

`figpipe/lock.py` now enforces it. The three heavy entry points (`cron_run`, `bench_plottwin`,
`score_official`) acquire the same file lock; a second run is REFUSED with exit code 3 and the
holder named:

    refused: another measurement is running: holder (pid 36172, started ...). Overlapping
    measurements produce numbers that are neither reproducible nor trustworthy

Proven with a genuinely live holder process. The loop tells its own children `--no-lock`, since a
child deadlocking against its parent's lock would be worse than the hazard it prevents.

TWO WINDOWS-SPECIFIC DEFECTS FOUND WHILE BUILDING IT, both in the liveness probe:

1. `os.kill(dead_pid, 0)` raises a bare `OSError` with **WinError 87** on Windows, not
   `ProcessLookupError`. The obvious implementation therefore treats every dead pid as ALIVE, so a
   stale lock blocks the schedule forever. Replaced with `OpenProcess` +
   `GetExitCodeProcess`.
2. On this machine's exFAT volume, the exception path of `os.kill` itself raised
   **KeyboardInterrupt** inside the probe. The new implementation has no signal semantics at all,
   and its failure mode is "assume alive" rather than "crash a scheduled run".

Plus a third, from the same family as the others: `break_stale()` read the lock file TWICE, and the
second open raised the same I/O error. It reads once now, and an unreadable lock file is treated as
"no lock" so a corrupt file cannot wedge the schedule.

Nine tests pin it: refusal, release, refusing to release someone else's lock, dead-pid detection,
stale-lock breaking, corrupt-file tolerance, and that all three entry points actually ask.

Suite: 321 passed, 2 skipped.


## 56. A diagnostic run destroyed 106 benchmark rows (2026-10-19)

While testing the new lock I ran the benchmark harness twice with `--limit 2`. The harness wrote its
report UNCONDITIONALLY, so each small run REPLACED the accumulated pool: 141 tasks became 35, and
the next scheduled run committed the damage. The report is the deliverable and the accumulated
measurement history -- and a two-task diagnostic run silently overwrote 106 rows of it.

This is the same shape as the seed-package deletion earlier: `git add -A` committed the absence of
files nobody meant to delete; here an ordinary write committed the absence of measurements nobody
meant to discard. Both are "a routine operation removed evidence as a side effect".

Fixes:
  * the harness REFUSES to shrink the report unless `--fresh` is passed explicitly:
    "refusing to shrink the benchmark report from 150 to 2 tasks without --fresh"
  * a test runs a 1-task pass against the real report and asserts both the refusal and that the
    file is unchanged
  * the report was restored from git (141/150, freshness 141/0/0)

Note what found it: I looked at the round's summary line and saw `35/35` where the previous round
said `141/150`. Nothing in the loop flagged it, because a smaller report is not an error to any
existing check -- `n_tasks` is a count, and counts are deliberately not judged (see ##26). That is
the trade-off of not judging counts: coverage regressions need a different guard, and this
shrink-refusal is it.

Suite: 322 passed, 2 skipped.


## 57. A peer project reached the same rule independently, and gave it a mechanism (2026-10-19)

Absorbed Harness² (google-research/harness2, Apache 2.0) this round. The full account is in
`PEER_HARNESS2.md`; the part that belongs in the defect log is this.

**The one mechanism figpipe actually lacked was a mutation loop.** Its evolution loop re-verified
rules, measured artefacts and recorded deltas -- but it never PROPOSED a change, PROBED it, and KEPT
it on evidence. It could report that a number moved; it could not choose an edit. Harness²'s
task-level recursion is exactly that loop with no ground truth: propose edits, probe them on the
same task, compose from the behavioural contrast.

**The convergence is the important finding.** Harness² refuses to serve any harness file whose name
or body carries a grader verdict, because such a file "cannot be served as evidence to later tasks".
figpipe learned the same rule the hard way: it once reported an official score of 100.0 that came
entirely from copying the reference figure's own code. Two projects, independent methods, the same
conclusion -- which is the strongest evidence either could have that the rule is real. The
difference is that Harness² had a MECHANISM and figpipe had a lesson. `figpipe/tripwire.py` is now
the mechanism: `assert_no_answer_key()` refuses a path whose name or content carries the target,
with an explicit `allow=(...)` for the one case where reading the answer key IS the measurement.

**Two details from their ledger worth stealing outright** (vendored unmodified at
`third_party/harness2_ledger/`):
  * duplicate labels are checked BEFORE the counts, "because a duplicate can satisfy them" -- a
    repeated label means two stages wrote the same id and one silently overwrote the other, so a
    candidate the ledger counts was never produced. This project has fixed the same family of
    defect four times (mixed instruments, mixed task sets); the ledger's phrasing is sharper.
  * `BudgetError` subclasses `AssertionError`: a budget violation is a programming error, not a
    runtime condition to be tolerated.

WHAT WAS NOT ABSORBED, and the reason is in PEER_HARNESS2.md: their proposer needs an LLM CLI and an
API key, which would make figpipe's mutation loop non-deterministic and therefore unvalidatable by
its own rules. The INTERFACE was adopted; the LLM was not.

Suite: 328 passed, 2 skipped.


## 58. A network failure read as a capability regression (2026-10-19)

After the multi-agent round the scheduled loop exited 1:

    benchmark_success_rate 1.0 -> 0.986    (capability regression)
    benchmark_ok           141 -> 139

Two tasks had returned **HTTP 403 Forbidden** from the dataset host. The pipeline never ran. The
success-rate metric counted them as capability loss -- the same defect family as counting a skipped
test as a pass, or a blank image as four spines: the metric stopped measuring what it claims.

Fix: a fetch failure is excluded from the success-rate denominator and reported separately as
`benchmark_infrastructure_failures`. The exclusion is VISIBLE, because a silent exclusion could be
tuned whenever the number looked bad -- which would be worse than the defect it fixes. That is why
the count is a **DIAGNOSTIC_FIELD** (recorded and diffed, judged in neither direction): fewer fetch
failures is not a better pipeline.

Re-measured the two tasks: both rendered fine, 141/150 with 0 errors. The 403 was transient.

## 59. The mutation loop found that a budget was one row too tight (2026-10-19)

The mutation subagent measured the matrix refusal boundary with budgets forced open:

    41 unpivotable rows -> 0 collisions
    42 rows             -> 41 collisions
    48 rows             -> 96 collisions

So `MAX_MATRIX_ROWS = 40` is **one row too tight**: a 41-row table renders cleanly but is refused.
`matrix-max-rows-41` was the mutation the loop SELECTED (+0.167, no task regressing).

It deliberately did NOT apply the change, and that decision is correct: applying a budget change on
six tasks is exactly the "a fix is a change, a change needs the same evidence" defect recorded at
##47. The decision is routed to a round that can re-measure the pool, not silently taken.

Three defects the subagent had to fix before the loop could be honest, all of the same shape --
a measurement that looks right and cannot fail:
  * a refusal scored 1.0 unconditionally, so an over-TIGHT budget was invisible forever
  * a mean hid a regression: `max_rows=60` nets +0.004 while breaking a 48-row figure
  * its own fixture used 20 SHORT labels that collide ZERO times, so the MAX_BARS refusal it was
    defending looked arbitrary

## 60. Three defects in my own lock, found by the loop exercising it harder (2026-10-19)

The mutation loop holds the measurement lock for ~30 rollouts per probe, far harder than the
scheduled run ever did. That exposed three defects in code I had written two rounds earlier:

1. `__exit__` called `release()`, which raised `MeasurementBusy` and **masked the body's exception**,
   leaving the lock on disk. One failed probe wedged every later probe.
2. **PID REUSE.** A crashed run's entry can name a pid that is now ALIVE (a different process), so
   `release()` refused forever -- a permanent denial of service caused by a crash. Ownership is now
   proven by a **token** we wrote, never inferred from a pid.
3. `_read()` returning `{}` for an unreadable file was treated as "no lock, nothing to do", so the
   file stayed. On this exFAT volume a write is not always visible to an immediate read.

Plus a harness defect: test files contended with each other through the machine-global lock,
producing failures that depended on **test order**. `tests/conftest.py` now points the lock at a
per-session temp dir and asserts the suite is never using the real one.

Suite: 400 passed, 3 skipped.


## 61. A partial anchor is not the anchor (2026-10-19)

The loop reported `benchmark_shipped_anchor_single 0.289 -> 0.296` as a REGRESSION. The numbers were
right and the interpretation was wrong: at the earlier run two anchor tasks had errored on a
transient HTTP 403, so only 18 of 20 rows were present and the mean came out 0.289. The loop read
that as an improvement over 0.296, then read the restoration as a regression. A metric that moves
with network luck, in both directions, on the same frozen set.

This is the SEVENTH variant of the same defect family:
    raw mean over a growing set        -> false regression
    count over a growing set           -> false gain
    shipped mean over a growing set    -> false regression
    "first N sorted ids" anchor        -> false regression when new ids sort earlier
    frozen ids with MIXED fingerprints -> false gain
    both anchors fixed, one at a time  -> the same defect one field over
    frozen ids, one instrument, but INCOMPLETE membership -> false regression AND false gain

The invariant was stated two rounds ago as "a judged metric must be a function of a fixed task set
AND a single instrument version". It needs a third clause: **and complete membership of that set**.
A fetch failure, an unsupported type, or a crashed task silently shrinks the set.

Fix: both anchors now require `len(same) == len(expected)`. A partial mean is still REPORTED (as
`partial_mean`, with `n_expected`), but `mean` is None and `comparable` is False, so it is never
judged. Seven tests pin it: complete -> comparable, partial -> not judged, mixed instrument -> not
judged, for both anchors, plus a live-report consistency check.

Related: the same round's infrastructure-error fix (`##58`) is what made the two 403s visible as
infrastructure rather than capability. Both fixes are needed -- one stops the failure being SCORED,
the other stops the set being SHRUNK.

Suite: 407 passed, 3 skipped.


## 62. The self-evolution loop never evolved, and 61% of its commits said so (2026-10-19)

I audited my own project instead of trusting it, and the audit was unflattering:

    91 scheduled runs
     4 knowledge_changed: true
     1 hypothesis promoted
    60 commits touched knowledge/layout_rules.json
     0 commits changed a RULE (only `last_check.at` moved)
    49 of the last 80 commits read "no knowledge change"

And the decisive one: `figpipe/mutation.py` -- the Propose-Probe-Compose loop I built last round,
which passed 30 tests and which the REPORT listed as a deliverable -- was imported by **nothing**.
AST-level scan: zero imports, zero call sites. `cron_run.py` did not contain the strings `mutation`,
`propose`, `probe`, `compose` or `candidate` even once.

So the honest statement was: **the project had a capability of its TEST SUITE, not of the system.**
"Self-evolution" was a word in a document. The loop could re-verify and record; it could not choose
an edit. That is why 91 runs changed nothing.

Three fixes:
1. `scripts/mutate.py` -- a real entry point that proposes, probes and composes, writing
   `knowledge/mutation_report.json`. It does NOT apply the selection (six tasks is a finding, not a
   change; ##47).
2. `cron_run.py` now calls `mutation_step()` after the benchmark slice and records the result in the
   run. First real run: 5 candidates, `matrix-max-rows-41` SELECTED (+0.167), one tie, three
   rejected with reasons, ledger 36/36.
3. **No-op commits suppressed.** A run that changed nothing no longer commits its own record; the
   record still lands in the worktree and is overwritten next run. A FAILED run still commits,
   because a failure is evidence.

Two bugs found while wiring it, both already-known shapes:
  * the child `mutate.py` tried to take the lock its parent held -- the same deadlock already fixed
    for the benchmark harness. `probe(lock_held=True)` makes ownership explicit instead of relying
    on a flag at the CLI boundary.
  * a test caught my new `contextlib` import because its allow-list was exact. That test was doing
    its job: an import allow-list that silently widens is not a control.

LESSON: **"we built X" and "X runs" are different claims.** The gap between them is not paperwork --
it is the difference between a test suite passing and a system changing. Every artefact in this
project should be asked which of the two it is.

Suite: 411 passed, 3 skipped.


## 63. The mutation loop's selected edit was wrong, and the pool proved it (2026-10-19)

Last round the mutation loop SELECTED `matrix-max-rows-41` (+0.167 on its six-task fixture) and
deliberately did not apply it, routing the decision to a round that could re-measure the pool. This
is that round. **The selection was wrong**, and the reason is instructive.

The fixture contained a clean 41-row matrix, so raising the budget from 40 to 41 "fixed" it. The
REAL pool does not look like that fixture:

    14 matrix_plate tasks
    13 of 14 (93%) already had hard findings at the CURRENT budget of 40
    hard findings: sum 995, median 39, MAX 405

Raising the budget would have made every one of them worse. The fixture had measured the wrong
thing: it asked "does a 41-row table render?" when the real question was "why do 40-row tables
produce hundreds of collisions?"

THE ACTUAL DEFECT, found by reading the findings instead of the score:

    '0.7015383331293864' over '0.7128659440184021'

`ax_tile_diverging` set a tick label for EVERY row and column, and annotated EVERY cell, with no
budget on either. A 40-row matrix drew 40 tick labels plus up to 200 cell annotations on a 90 mm
panel. The budget `MAX_MATRIX_ROWS` was never the lever -- even 40 rows cannot be labelled at 5.5 pt.

Fix: a LABEL BUDGET (12) on each axis and the existing 200-cell annotation cap, so a matrix past
either budget hides ticks and lets the caption carry the meaning -- the rule the heatmap drawer
already applied to numeric indices.

MEASURED RESULT on the real pool:
    hard findings  sum 995 -> 98   (-90%)
    worst task     405 -> 65
    clean tasks    1 of 14 -> 5 of 14

LESSON: **a mutation fixture that does not resemble the production distribution selects the wrong
edit, confidently.** The loop did everything right -- proposed, probed, composed, rejected on
per-task regressions -- and still chose a worse world, because its six tasks were not a sample of
the 150. That is the same defect as a benchmark measured on a convenient subset, one layer in.

Suite: see below.


## 64. The label budget was the real defect; the row budget never was (2026-10-19)

Last round the mutation loop selected `matrix-max-rows-41` (+0.167) and I routed the decision
instead of applying it, because six tasks is not evidence. This round I checked the pool first, and
the selection was WRONG:

    14 matrix_plate tasks in the real benchmark
    13 of 14 (93%) already had hard findings at the CURRENT budget of 40
    hard findings: sum 995, median 39, MAX 405

Raising the budget would have made all of them worse. Reading the actual findings rather than the
score showed why:

    '0.7015383331293864' over '0.7128659440184021'

`ax_tile_diverging` set a tick label for EVERY row and column and annotated EVERY cell, with no
budget on either. A 40-row matrix drew 40 tick labels plus up to 200 cell annotations on a 90 mm
panel. The row budget `MAX_MATRIX_ROWS` was never the lever -- 40 rows cannot be labelled at 5.5 pt
whatever the budget says.

Fix: a LABEL BUDGET (12) on each axis, plus the existing 200-cell annotation cap. Past either, the
ticks are hidden and the caption carries the meaning -- the rule the heatmap drawer already applied
to numeric indices.

MEASURED on the real pool:
    hard findings  sum 995 -> 98   (-90%)
    worst task     405 -> 65
    clean tasks    1 of 14 -> 5 of 14

AND THE CONSEQUENCE FOR THE LOOP: with the real defect fixed, every budget candidate in the default
mutation space became a TIE. The loop now selects nothing, which is the correct answer -- the
budgets were compensating for a defect, not tuning a parameter. `matrix-41-rows` had also declared
`expect="clean"`, which was a STALE SPEC: with the label budget the drawer refuses it for the real
reason (two columns, no 2-D reading). A probe scored against a stale spec "selects" edits that fix
nothing.

Four mutation tests broke because they asserted the OLD selection against the DEFAULT space. The
fix was better test design, not weaker assertions: selection / rejection / inversion logic is now
exercised on SYNTHETIC spaces with a measured, known-improving edit, and the default space is tested
for the property that matters -- every declared expectation matches reality.

LESSON: **a budget is usually compensating for a defect, and raising it hides the defect.** The
question "is the limit wrong?" should always be preceded by "why does the limit exist?".

Suite: 420 passed, 3 skipped.


## 65. The label-budget fix costs 0.008 on the style anchor, and that is the honest trade (2026-10-19)

After the label budget landed, the styled anchor moved 0.351 -> 0.359 (worse, since distance is a
cost). I traced every anchor task rather than accepting the number:

    Chart2Code_level1_direct_contour_18   0.268 -> 0.335   (+0.067)
    Chart2Code_level1_direct_heatmap_3    0.247 -> 0.302   (+0.055)
    Chart2Code_level1_direct_heatmap_7    0.283 -> 0.320   (+0.037)
    17 other tasks                        unchanged
    MEAN                                  0.351 -> 0.359   (+0.008)

Exactly the three matrix tasks moved, and only those. The reason is structural: hiding 40 tick
labels removes ink that the reference figures HAVE, so the rendered figure is now further from the
reference on the dimensions that count ink. Meanwhile the hard findings on matrix tasks fell
995 -> 98 and the official channel stays at ~99.99 per task.

So the project traded 0.008 of style distance for a 90% reduction in collisions. Which is right?

**Style distance is a PROXY; collisions are a DEFECT.** A figure with 405 overlapping labels is not
a figure, whatever its palette distance says. The trade is correct, and the fact that the metric
moved in the "wrong" direction is evidence about the METRIC -- it rewards ink density that a reader
experiences as broken. That is worth recording next to the human-validation result, which already
found the metric concentrates in `aspect`.

This is also why the anchor is judged as a COST and a regression triggers a report: the loop cannot
tell "the metric got worse" from "the metric is measuring the wrong thing". A human has to look, and
this is what looking found.

Suite: 420 passed, 3 skipped.


## 66. The same defect, third instance: a drawer given a long table draws every row (2026-10-19)

After fixing the matrix label budget I asked the obvious follow-up question -- WHERE ELSE? -- instead
of moving on. The answer was immediate: `radial_profile`.

    13 Polar/Radial benchmark tasks
    rows_used: 460 and 784 (the WHOLE long table)
    hard text collisions: 50, 30, 17, 13, 10, 10, 10, 9, 8 ...
    offending labels: 'advantage_profile' over 'benchmark_profile'

`op_encode_polar` passed `ctx.data` straight to the polar drawer, which drew ONE SPOKE PER ROW. The
label budget in the drawer only applied to NUMERIC angles; categorical labels had no cap at all.
Same shape as `encode.bars` (one bar per row) and `ax_tile_diverging` (one tick per row).

Fix, three parts:
  * aggregate to one value per angle (mean by default), recording the reduction in the trace:
    "encode.polar.aggregate(theta by mean: 368 rows -> 8 angles)"
  * a spoke budget (16): past it, REFUSE, because a radar with 40 unreadable spokes is not a radar
  * below three spokes, a NAMED refusal -- two benchmark tasks reduce to exactly 2 angles, and a
    polar profile cannot show 2

MEASURED on the real pool:
    radial hard findings   ~200 -> 4   (max 50 -> 1)
    TOTAL hard findings      301 -> 129  (-57%)

AND A CLASSIFICATION FIX the refusals forced: a `SkillError` that names a STRUCTURAL reason ("this
data has no angular reading") is the pipeline WORKING, so it is now classified `unsupported`, not
`error` -- exactly like 3D and Network/Tree. Classifying a correct refusal as an error would report
a capability failure for a right decision, and would make the success rate FALL whenever the
pipeline got more honest.

LESSON: after fixing an instance, ask "where else is this shape?" The three instances here were
found three different ways -- an example, a sweep, and a score -- and all three were the same bug.
The question is cheap and the answer keeps being yes.


## 67. An absolute cap is the wrong unit for a density problem (2026-10-19)

The first matrix fix capped cell annotations at 200. That looked principled and was wrong: a
40-row x 4-column matrix has 160 cells, passes the cap, and still collides -- 65 hard findings on
one benchmark task. What matters is not how many annotations EXIST but how many land on a given
axis length. Past roughly one label per 4 mm of panel, text overlaps whatever the total is.

So the cap became a DENSITY: annotate only when BOTH dimensions fit the same 12-label axis budget
that governs the ticks. Measured on the real pool:

    matrix hard findings   98 -> 6   (max 65 -> 3)
    TOTAL hard findings   129 -> 37  (from 301 at the start of the round)

The general form: **a budget expressed in the wrong unit is a control that looks present and does
nothing** -- the project's recurring class-A defect, this time in a drawing limit rather than a
metric.

Progression this round, all from asking "where else is this shape?":
    301 -> 129   (radial profile: one spoke per row)
    129 ->  37   (matrix annotations: absolute count -> density)

Suite: 423 passed, 4 skipped.


## 68. When the fix makes the test's scenario unreachable (2026-10-19)

One mutation test broke after the annotation DENSITY fix, and the reason is worth recording: it
constructed a "wins on one task, loses on another" case by raising the matrix row budget, which used
to break a 48-row table (1.0 -> 0.017). After the label budget and the density cap, a matrix renders
cleanly at ANY row count, so NO budget edit can produce a mixed effect. The scenario became
unreachable because the defect it depended on was fixed.

Two wrong responses were available:
  * delete the test -- then the no-regression RULE loses its coverage, and a future drawer
    reintroducing the shape would not be caught
  * keep asserting against the real drawers -- then the test fails forever for a good reason

The right response: test the RULE against a DECLARED probe whose per-task scores are explicit. The
rule is what is under test, not today's drawers. The test now says so in its docstring, including
why the real-drawer version stopped working.

This is the mirror image of the earlier lesson about fixtures (##63): a fixture that does not
resemble production selects the wrong edit; a fixture that CANNOT resemble production because the
defect is gone must still test the rule. Both are about knowing what a test is for.

Suite: 426 passed, 3 skipped.


## 69. A merge that recomputes SOME aggregates is worse than one that recomputes none (2026-10-20)

A scheduled 6-task slice rewrote the benchmark report's aggregates. `n_ok`, `by_type`, the means and
both anchors were recomputed over the MERGED task list -- but `failures`, `unsupported_types` and
`semantic_violations` were left as computed over the SLICE. The visible damage:

    failures            11 entries  ->  []
    unsupported_types    3 types    ->  {}
    semantic_violations  8          ->  0

The report still LOOKED internally consistent: n_ok and n_tasks agreed, the anchors were right, the
per-type table was right. Three fields silently described a different set than the ones beside them.

This is the same family as the mixed-instrument anchors and the mixed-task-set means: **an aggregate
that describes a different set than the one it sits next to**. The difference here is that the
recompute was PARTIAL -- which is harder to notice than none, because a fully unrecomputed report
would be obviously stale, while a partially recomputed one looks coherent.

Fix: every aggregate is now recomputed inside the merge block, and `tests/test_merge_aggregates.py`
asserts the consistency properties directly (failures match the non-ok tasks, unsupported_types
match the unsupported tasks, the counts add up, semantic_violations counts the whole report) plus a
STRUCTURAL check that each field is assigned in the merge block rather than inherited.

LESSON: when a function rebuilds a derived object, enumerate EVERY derived field and assign it.
A partial rebuild is a silent lie about which set the numbers describe.

Suite: see below.


## 70. A structural check found two more instances I had missed (2026-10-20)

After the fourth instance of "a categorical axis given every label" I stopped fixing instances and
wrote the STRUCTURAL check instead: every drawer that calls set_xticklabels/set_yticklabels must
also bound them. It immediately named four drawers, two of which were genuinely unbounded
(`ax_grouped_bars`, `ax_ranked_share`) and two of which were already bounded by a `step` slice the
detector did not recognise.

Both halves of that are the lesson:
  * the check found real defects I had not found by reading
  * the check produced FALSE POSITIVES, and a detector that cries wolf is one people learn to ignore

So the detector now accepts every form of bounding (a named constant, a stride, an explicit
empty-tick branch). Recognising only one spelling would have made the test useless.

AND THE FIX BROKE TWO THINGS, which the data-shape sweep caught within seconds:
`ax.set_xticks([])` followed by `ax.set_xticklabels([...])` is a length mismatch and RAISES
("The number of FixedLocator locations (0) ... does not match the number of labels"). Hiding ticks
must SKIP the labels, not pass an empty locator to a non-empty list. The sweep found it before the
benchmark did.

MEASURED after the round's fixes:
    total hard collisions  37 -> 25
    worst single task       9 ->  3

Everything left is small and idiosyncratic rather than systemic, which is the difference the
structural check made.

Suite: 435 passed, 3 skipped.


## 71. A merge that reorders is a diff generator (2026-10-20)

The scheduled slice kept staging a modified `plottwin_report.json`. Checking whether the content had
changed: **zero tasks differed**, the task SET was identical, and only the ARRAY ORDER differed.

    merged = [t for t in old_tasks if id not in seen] + report["tasks"]

Freshly measured tasks were appended to the END, so a 6-task slice moved six entries and produced a
diff over all 150 rows -- with no content change at all. Every scheduled run therefore staged a
150-row change that meant nothing, in a history whose entire value is that a diff means something.

Fix: sort the merged list by id. A re-measured task now rewrites six lines in place.

This is the third "noise commit" defect, and the mildest:
    * 49 of 80 commits said "no knowledge change"          (fixed: no-op commits suppressed)
    * a 6-task slice erased failures/unsupported_types      (fixed: recompute every aggregate)
    * a 6-task slice rewrote the array order                (fixed: order-stable merge)

The common shape: **a routine operation produced a diff that did not correspond to a change.** A
commit history is a measurement instrument too, and it was reporting motion that was not there.

Suite: 436 passed, 3 skipped.


## 72. The unattended loop had no watchdog, and it had already died (2026-10-20)

I had listed "watchdog" as a next step for six consecutive rounds and never done it. This round I
looked at the evidence instead of the list:

    13 log markers over three days
    one gap of 10.8 hours against a 6-hour schedule
    on 2026-10-20 the loop took exit=3 at 01:54 and then slept until 07:54 doing nothing

exit=3 is the MEASUREMENT LOCK refusing because another run held it. My own manual `cron_run` at
01:52 caused it. The loop treated a transient scheduling accident as a completed cycle and slept six
hours -- one manual run starved the schedule for a quarter of a day.

TWO DEFECTS, both now fixed:
1. **No backoff.** A busy lock now retries after 300 s, up to 6 times, before falling back to the
   full interval. Only a COMPLETED cycle sleeps six hours.
2. **No liveness check.** Nothing verified the loop was alive. `scripts/watchdog.ps1` checks BOTH
   the heartbeat age AND whether a process is running loop.ps1 -- either alone is wrong (a fresh
   file with a dead process, or a live process that is wedged).

THE WATCHDOG DELIBERATELY DOES NOT KILL. A wedged loop may be mid-measurement, and killing it would
abandon a half-written report -- the exact defect class this project spent rounds fixing. It reports
WEDGED and lets a human decide; it only relaunches when the process is GONE.

And a limitation stated rather than hidden: registering a Windows scheduled task needs elevation,
which this unattended account does not have. The watchdog therefore runs as a second Startup
process. A watchdog loop can itself die; two mitigations (it restarts at login with the loop, and it
logs its own start) but a genuinely crash-proof watchdog needs a service or elevation. That is
written in the script, not glossed over.

VERIFIED LIVE: loop pid 43100 + watchdog pid 35912 both running; heartbeat written; the watchdog's
own verdict went from PROBLEM/WEDGED (when the old script had no heartbeat) to
"OK: loop alive, heartbeat 0 min old, 1 process(es)".

Suite: 443 passed, 3 skipped.


## 73. The watchdog I built was a fork bomb, and only a drill found it (2026-10-20)

Round 21 added a watchdog and verified the HEALTHY path. I said the restart path was the one thing
still unproven. This round I drilled it, and the drill found a defect the tests could not.

THE DRILL: kill the loop, watch the watchdog restart it. What actually happened:

    Stop-Process received an ARRAY (Where-Object matched more than one process)
    -> several loops died at once
    -> every watchdog saw a dead loop and restarted it
    -> each restart launched BOTH a loop AND another watchdog
    -> 76 processes in ten seconds

The root cause is one line of missing logic: **the launcher was not idempotent.** It is called from
three places (login, the watchdog, and by hand) and every call started a new pair unconditionally.
Two watchdogs then each restart the loop the other just restarted, and the population grows
exponentially.

Fix: the launcher queries Win32_Process for a live `loop.ps1` / `watchdog_loop.ps1` and starts each
only when absent. Verified by running it three times: exactly 2 processes every time, before and
after.

THE DRILL THEN PASSED on a clean retry: kill the loop -> 0 processes -> run the watchdog -> exit 0 ->
loop back with a new pid.

WHAT THIS TEACHES, and it is uncomfortable: **every guard I add is itself unguarded until it is
exercised in the failure direction.** The watchdog passed 5 unit tests and a live health check and
was still a fork bomb, because none of those ran the path where things are broken. The unit tests I
wrote for its branches used a sandbox pattern precisely to avoid touching the real loop -- and that
isolation is exactly what hid the launcher's behaviour, since the launcher was not in the sandbox.

The project's recurring lesson, one layer out again: a control that is only tested when everything
works is a control that looks present and does nothing.

Suite: 447 passed, 3 skipped.


## 74. "Reusable" was a claim with no entry point (2026-10-20)

The objective's third leg is that the capability be "reusable and verifiable in research
scenarios". The evidence was `examples/worked_example.py`, which runs on INVENTED data -- it proves
the functions exist, not that a stranger can use them. A researcher has a CSV, a journal width, and
often a reference figure. There was no command for that path.

`scripts/make_figure.py` is that command. Writing it took four bugs, and every one was found by
running it ONCE on a real table:

1. the CLI passed an EMPTY parameter dict, so every inferred figure was refused for columns `spec`
   had already resolved in `panel.kwargs`
2. the intent -> skill map used INVENTED names. `infer_spec` actually emits
   `grouped_bars, scatter_fit, boxplot, ranked_composition, density_relationship`; my map contained
   `trend_with_uncertainty`, `distribution`, `signed_matrix`, `comparison_with_error` -- none of
   which it ever emits. The result was a refusal that looked deliberate and was a missing entry.
3. `columns` is an ENUM (1 = 89 mm, 2 = 183 mm) in the layout layer, and I passed a ratio
   (183/89 = 2.056), which is correctly rejected
4. `spec` supplies `xlabel`/`ylabel` that some skills do not declare, and the CLI did not filter --
   but it must not drop them SILENTLY either, so it prints what it omitted

The end state, on a CSV with column names nobody in this repo chose:

    intent: grouped_bars (inferred)
    wrote: research_fig.pdf and its .png preview
    audit: width 183.0 mm, height 91.5 mm, 0 hard finding(s)
    RESULT: compliant

Plus a second shape inferred differently (`ranked_composition` at 89 mm) and a reference-style
transfer (`style.profile` in the trace). Seven end-to-end tests, one of which asserts that the
intent map covers EVERY intent `infer_spec` can emit -- so bug 2 cannot come back.

LESSON: **an API is not a product.** Five documented entry points and a worked example on invented
data still left the actual first step -- "I have a CSV" -- unaddressed. The gap was invisible from
inside because every test already had a DataFrame in hand.


## 75. The declaring layer and the drawing layer spoke different vocabularies (2026-10-20)

Testing the CLI on more real table shapes exposed an architectural break, not a CLI bug:

    spec.infer_spec EMITTED:   grouped_bars, boxplot, scatter_fit,
                               trend_with_uncertainty, density_relationship, ranked_composition
    grammar.INTENTS DECLARED:  comparison_with_error, distribution, signed_matrix,
                               trend_with_uncertainty, density_relationship, ranked_composition

    emitted but NOT declared: grouped_bars, boxplot, scatter_fit
    declared but NEVER emitted: comparison_with_error, distribution, signed_matrix

`grammar.INTENTS` is the DRAWING CONTRACT -- its names are what every drawer, skill and recipe
uses. So `grammar.panel(spec.infer_spec(df).panels[0].intent, df)` raised KeyError on **three of six**
real table shapes. The declaring layer and the drawing layer had silently drifted apart.

I had already worked around this in the CLI with a hand-written map. **A hand-written map was the
symptom, not the fix**: it hid the break from the one place that would have hit it.

Fixed by renaming in `spec` (the declaring layer should speak the drawing contract's language):
    grouped_bars -> comparison_with_error
    boxplot      -> distribution
    scatter_fit  -> density_relationship

AND the deeper fix: there were THREE hard-coded copies of the intent -> recipe map (CLI, worked
example, and my earlier test's expectations). Three copies is three chances to diverge, and they
did. There is now ONE: `spec.INTENT_RECIPES`, with `spec.recipe_for()`, imported by both.

Three new contract tests:
  * every intent spec emits is declared in grammar.INTENTS
  * every emitted intent is accepted by grammar.intent() (the stronger form)
  * the shared map covers every declared intent AND names only real skills
  * there is exactly ONE map (the test looks for a second dict literal)

A related lesson about the tests themselves: my first completeness test drove `infer_spec` over
FIVE hand-picked shapes and asserted the map covered what it saw. That tests the SAMPLE, not the
contract -- and it missed `trend_with_uncertainty`, which a dated time series produces. The test now
enumerates from `grammar.INTENTS`, the registry, which is what "complete" actually means.

Suite: 462 passed, 3 skipped.


## 76. Multi-panel figures were unreachable, and a dict literal hid why (2026-10-20)

A research figure is usually SEVERAL panels. The recipes exist -- `faceted_distribution`,
`composite_groups`, `dual_measure` -- but nothing could reach them:

  * `spec.infer_spec` always declares exactly ONE panel, so the inferred path never yields a facet
  * the CLI had no `--facet`, so the multi-panel capability was unreachable from the command line
  * and when I tried the recipe directly, it FAILED on the commonest faceted table there is

That third failure is the interesting one:

    layout.facets: need two numeric columns for scatter/trend

...raised for a table with ONE numeric column asking for `of="hist"`. The cause is a Python detail
with real consequences:

    call = {"hist": dict(value=...),
            "trend": dict(x=..., y=_second_numeric(ctx)),      # <-- evaluated ALWAYS
            "scatter": dict(x=..., y=_second_numeric(ctx))}[of]

**A dict literal evaluates every value before the key is selected.** So `_second_numeric()` ran for
the trend and scatter branches even when `of` was `"hist"`. The fix is to build only the chosen
branch.

This is the same family as the project's recurring defects -- a control that looks present and does
the wrong thing -- but expressed in the LANGUAGE rather than in a metric: code that appears to select
one option, and in fact executes all of them.

FIXED, and the CLI now has a real multi-panel path:

    python scripts/make_figure.py data.csv --out fig --facet condition --value score

    facet: 4 panels over 'condition' (hist each)
    wrote: facet.pdf and its .png preview
    panels: 4
    audit: width 183.0 mm, height 60.0 mm, 0 hard finding(s)
    RESULT: compliant

Faceting past `--max-panels` REFUSES rather than truncating, because dropping panels changes what
the figure claims. Five new tests cover the multi-panel path, the refusal, the missing-column cases,
and the single-numeric-column regression above.

Suite: 466 passed, 3 skipped.


## 77. The CLI accepted arguments it never used (2026-10-20)

I asked the systematic question -- "does every declared CLI argument actually reach the code that
uses it?" -- and the answer was three times no:

    --reference with --facet   accepted, silently IGNORED, figure came out unstyled
    --quiet                    declared and never read
    (and one more found by the same scan)

The `--reference` case is the worst, because the command REPORTED SUCCESS. A researcher passing
`--facet condition --reference published.pdf` got an unstyled figure and `RESULT: compliant`. That
is this project's class-A defect -- a control that looks present and does nothing -- in the CLI
rather than in a metric.

Cause: `run_facet` was dispatched BEFORE the reference was loaded, and it never accepted style
parameters. The fix loads the reference before the path dispatch and threads `style_kw` into both.

`profile` turned out to be a GLOBAL optional parameter in the skills layer already ("any skill can be
rendered in a measured style"), so the plumbing existed -- the CLI just never connected it.

VERIFIED:
    reference style: ref.pdf (width 89.0 mm)
    facet: 4 panels over 'condition' (hist each)
    operators: layout.facets(condition:4) -> layout.plate -> style.profile(...) -> verify.audit
    RESULT: compliant

`--quiet` was then implemented properly (a `say()` helper; a printing preference should not appear
in function signatures that exist for logic), and a structural test now asserts every declared
argument is read: `test_every_declared_cli_argument_is_actually_read`.

LESSON: after adding a flag, ask "where does this value GO?" An argument that is parsed and dropped
is worse than one that is missing -- the missing one fails loudly, the dropped one lies.

Suite: 472 passed, 3 skipped.


## 78. The skill declaration and the skill signature disagreed (2026-10-20)

Generalising the "declared but unused" check to EVERY script found no unread arguments left -- the
previous round's fix was complete. But turning it on `faceted_distribution` found a different
disagreement between what a skill SAYS and what it DOES:

    of="hist" | "trend" | "scatter"      <- the operator accepts all three
    required = ("value", "by")           <- value is only needed for hist
    optional = (..., "of", "max_panels") <- x and y are MISSING

So a caller asking for a faceted TREND was refused:

    skill 'faceted_distribution' does not understand parameters ['x', 'y']

...for passing exactly the parameters the recipe demands. The declaration said one thing and the
signature another, and the signature won.

Fixed:
  * `x` and `y` added to `optional`
  * `value` moved from `required` to `optional`, because a flat tuple cannot express "value for
    hist, x+y for trend" -- the OPERATOR enforces the real condition and raises with a clear reason
  * `--facet-of` in the CLI now builds the right parameter set per encoder and refuses a trend
    facet without a y

VERIFIED all three from the CLI:

    --facet-of hist     -> 4 panels, 0 hard findings, compliant
    --facet-of trend    -> 4 panels, 0 hard findings, compliant
    --facet-of scatter  -> 4 panels, 0 hard findings, compliant

Also: the argument scanner needed three read forms to be correct (direct `args.x`, guarded
`getattr(args, "x", ...)`, and bulk `vars(args)`), or it reported `--fresh` and ten of
`run_skill.py`'s arguments as unread when they are read fine. A detector with false positives gets
ignored, which is worse than no detector -- so `tests/test_cli_arguments.py` has a NEGATIVE CONTROL
that a synthetic unread argument IS caught, plus tests that each read form is accepted.

Suite: 476 passed, 3 skipped.


## 79. The watchdog accumulated 190 instances, and a mutex did not fix it (2026-10-20)

The scheduled run's watchdog log showed repeated failures while the loop was demonstrably alive:

    [05:49:45] PROBLEM: no powershell process is running loop.ps1
    [05:49:45] RESTARTING: launching ...figpipe-evolve.vbs
    [05:49:50] RESTART FAILED: launcher returned but no loop process appeared
    ... and the same four lines every 30 minutes until 07:20

The loop (pid 66104) had been alive since 04:19. The cause was in the log's own history:

    "watchdog loop started" appears 190 TIMES against ONE live process

The launcher is idempotent -- round 22 fixed that -- but the SCRIPT is not. Anything starting
`watchdog_loop.ps1` directly (a manual run, a stale Startup entry, a restart during the fork-bomb
window) bypasses the launcher's check, so instances accumulated. Each then ran its own watchdog
every 30 minutes, and the interleaved reports looked like a broken guard.

TWO ATTEMPTS, the first WRONG:

  * `New-Object System.Threading.Mutex($true, name, [ref]$createdNew)` -- createdNew is reported
    only for the first creator IN A PROCESS'S LIFETIME and the handle is released when the object
    is collected, so two processes both saw "created" and both ran. Verified: two instances
    survived.
  * an EXCLUSIVE-SHARE FILE HANDLE -- held for the process lifetime, and a second opener fails.
    Verified: "after A: 1 / after B: 1", with the log line
    "another watchdog loop holds the lock; exiting".

That is the same primitive `figpipe/lock.py` already uses for measurements, which should have been
the first guess: this project had already learned that a pid or a mutex name is not ownership.

Suite: 479 passed, 3 skipped.


## 80. The launcher could not tell the loop from its own watchdog (2026-10-20)

Checking whether `loop.ps1` needed the same single-instance guard the watchdog just got, I found
two defects, and the second is the serious one.

**1. `loop.ps1` had no guard.** `loop started` appears 197 times in loop.log, the last cluster one
per SECOND during the fork-bomb window. Fixed with the same primitive that worked for the watchdog:
an exclusive-share file handle (not a mutex).

**2. THE LAUNCHER'S IDEMPOTENCE CHECK WAS A SUBSTRING MATCH.**

    CountMatching("loop.ps1")   ->  matches "...\scripts\watchdog_loop.ps1"

`watchdog_loop.ps1` CONTAINS `loop.ps1`. So once the watchdog was running, the launcher believed a
loop was running too and NEVER started the evolution loop. Observed at 07:47: watchdog alive, loop
dead, and every launcher call a silent no-op.

This is the same defect family the project keeps finding, in its purest form: **a guard whose test
cannot distinguish the thing it guards from a DIFFERENT thing**. It reported success while doing
nothing -- and it did so precisely when the watchdog was healthy, which is the condition under which
nobody would look.

Fixed by anchoring the needle to a path separator: `\loop.ps1` / `/loop.ps1`. `watchdog_loop.ps1`
ends in `_loop.ps1`, so it does not match. A NEGATIVE CONTROL test proves the naive form really does
collide, so the fix is justified rather than superstitious.

VERIFIED: after the fix the launcher started the loop (pid 60108), the loop lock is held, the
watchdog stayed single-instance, and the heartbeat moved to `running`.

LESSON: when a guard asks "is X running?", it must answer about X. A substring, a prefix, or a pid
is not an identity. This project has now learned that three times: pid reuse in the measurement
lock, mutex names in the watchdog loop, and now a filename inside another filename.

Suite: 481 passed, 3 skipped.


## 81. Dead code that looks like the real check (2026-10-20)

Following "a substring is not an identity" outward, I scanned every module for LOCAL VARIABLES THAT
ARE ASSIGNED AND NEVER READ. Fifteen turned up. Most are harmless (`h_mm`, `w_mm`, a leftover
`marker`), but three were the defect family in literal form -- code that looks like a check and does
nothing:

1. `slim.py::tracked_regenerable` computed a `hits` list from
   `str.startswith(pattern.split("*")[0])` and then built the result from a `git ls-files` call
   instead. **`hits` was never used.** Worse, the expression had an operator-precedence bug:
   `A and B or (C and D and E)` binds as `(A and B) or (C and D and E)`, which is not what the
   indentation suggests. Dead code that LOOKS like the real check is worse than none, because a
   reader believes it.

2. `cron_run.py::_main_locked` computed `evolve_failed = p.returncode != 0` and never read it.
   The fact was already carried by `ok_evolve`. Two names for one fact is how one of them silently
   stops being maintained.

3. `skills.py::op_layout_split_panels` used a walrus to bind a throwaway SkillContext to a name that
   was never read again.

All three removed. The scan is the reusable part: **"assigned and never read" is mechanically
findable**, and it is the same question this project keeps asking in different clothes -- is this
control connected to anything?

I also checked the guards that DO use prefix matching (`PROTECTED_PREFIXES` in cron_run.py) and
found them correct: every prefix ends in "/" or is a full filename, so `Seeds2/` and
`reports_old/` do not match. Not every substring check is a bug; the ones that are, are the ones
used as an IDENTITY.

Suite: 482 passed, 3 skipped.


## 82. The mapper detected the uncertainty column and then dropped it (2026-10-20)

The dead-assignment scan turned up a defect with real consequences:

    err = next((c for c in nums if any(k in c.lower() for k in ("ci95_lower", "lower", "err"))), None)
    hi  = next((c for c in nums if any(k in c.lower() for k in ("ci95_upper", "upper"))), None)
    return "composite_groups", {"by": group, "x": label, "y": nums[0]}, df, ...

`err` was DETECTED and then never passed to the recipe. A composite task whose data carries an
uncertainty column was drawn WITHOUT error bars -- the figure silently claimed less than the data
says, which is the opposite of the failure mode this project usually worries about and just as
wrong.

`hi` is genuinely unused (`composite_groups` takes a single symmetric `err`), so it was removed
rather than wired in.

That is the difference the scan makes: it cannot tell a harmless leftover from a dropped input. A
human has to look at each one. What the scan does is make the list short enough to look at.

Also cleaned: 12 other dead stores (`hits` in slim.py, `evolve_failed` in cron_run.py, a walrus in
skills.py, and nine harmless leftovers), and the detector was taught that `global X` means X is read
by other functions so assigning it is not dead.

The remaining dead stores were removed by renaming to `_name`, which is the Python convention for
"deliberately unused" -- a reader now sees the intent instead of wondering.

Suite: 484 passed, 3 skipped.


## 83. Studying a mature peer: what transfers, and what would undo this project (2026-10-20)

Asked to learn from AutoFigure (ResearAI/AutoFigure, **ICLR 2026**, MIT, ~1,930 stars, ~8,000 lines),
I read it instead of admiring it. The honest finding is that three of its central mechanisms are ones
this project has **deliberately ruled out**, and one thing it does is better.

WHAT IT DOES: Generate -> Evaluate -> Refine. An LLM writes SVG or draw.io XML; a **VLM-as-Judge**
scores it 0-10 on eleven named dimensions; the loop repeats until the score clears 9.0 or five
iterations.

WHAT FIGPIPE MUST NOT COPY:
  * **VLM-as-Judge.** This project MEASURED that approach: `vlm_report.json` recorded **20
    fabrications** in VLM descriptions of figures. A judge that invents what it is looking at cannot
    be the ground truth for a pipeline whose value is that its checks can be re-run and disagree.
  * **Text-to-figure from prose.** Different product, different failure modes. A text-to-diagram
    system cannot tell you your error bar is wrong.
  * **LLM-generated code with an LLM quality gate.** figpipe's mutation loop is deterministic and
    offline on purpose; a proposal step that varies run to run cannot be validated by this project's
    own rules.

WHAT TRANSFERS, and is now implemented as `figpipe/quality.py`:

  **A rubric with NAMED dimensions, scored separately.** figpipe's audit reported a flat list of
  findings -- a user told "3 findings" does not know whether to fix the typography or the layout.
  AutoFigure names eleven dimensions and reports each. The STRUCTURE is adopted; the judge is not.

  Six measurable dimensions (typography, geometry, legibility, density, colour, semantics), sorted
  WORST FIRST so the list has an order, and five dimensions listed as UNMEASURED with the reason
  (visual expressiveness, logical flow, information sophistication, audience appropriateness,
  completeness) because no deterministic check can decide them. Faking them with a heuristic would
  be a wrong number nobody can audit.

  One bug found while building it: "findings is empty" was read as "no check ran", so a perfect
  figure and an unverified figure produced identical reports. The TRACE records which steps
  executed, and that is the only honest signal.

THE THING FIGPIPE SHOULD BE EMBARRASSED ABOUT: AutoFigure has a web interface and a Flask API. A
researcher can use it without a terminal. figpipe has a command line and a README that leads with a
shell command. For a tool whose objective is "reusable in research scenarios", that is a barrier
AutoFigure decided was worth removing and figpipe has not.

Full comparison in PEER_AUTOFIGURE.md, including what figpipe does better (deterministic ground
truth, reproducibility, 15 documented defect classes, an audit trail).

Suite: 494 passed, 3 skipped.


## 84. The thing to be embarrassed about, removed (2026-10-20)

Last round I wrote that AutoFigure ships a web interface and a Flask API while figpipe has a command
line, and called it "the one thing figpipe should be embarrassed about". This round I removed it.

`scripts/webapp.py`: a single-process FastAPI app, no new dependency (fastapi/uvicorn were already
installed), serving one page and four endpoints:

    GET  /                  the page
    GET  /api/health        liveness, so a script can wait instead of sleeping
    POST /api/inspect       what WOULD be drawn and why, before drawing it
    POST /api/make          draw it, audit the rendered file, return the quality report
    GET  /api/file/{name}   fetch the PDF or the PNG preview

VERIFIED end to end against a running server, not just in tests:

    health          {"ok":true,...}
    page            200, 4127 bytes, has a form
    inspect         intent=comparison_with_error, rationale + columns
    make            200, compliant, "hard findings: 0", "183.0 mm", named dimensions
    PDF download    200, 30990 bytes, starts %PDF
    traversal       /api/file/..%2F..%2Fetc%2Fpasswd -> 404
    facet           4 panels, compliant

DESIGN DECISIONS, each answering a risk a web surface introduces:

  * **It must not be a second, less honest path.** The page runs the SAME `audit.audit()` and the
    SAME `quality.for_skill_result()` the CLI runs. A page that reports success without verifying is
    the defect this project exists to prevent, with a nicer font.
  * **It must not swallow a refusal.** An ambiguous table returns the reason AND the column list,
    exactly as the CLI does. Showing an error is awkward; hiding it is dishonest.
  * **It must state what it could not measure.** The `unmeasured:` line appears on the page.
  * **Path traversal is checked explicitly.** `GET /api/file/{name}` strips directory components and
    asserts the resolved path is inside the output dir. A web surface is the one place this project
    gains an attack the CLI does not have, so the check is written rather than assumed.
  * **Outputs go to a temp dir, not the repo.** A browser session must not leave artefacts in a git
    working tree -- the lean budget and the "no regenerable path is tracked" rule both depend on it.

9 tests drive the real app through FastAPI's TestClient -- no server process, no network -- and
check the RENDERED file, not the response status.

Suite: 503 passed, 3 skipped.


## 85. A relative improvement is not a pass (2026-10-20)

The mutation loop could only answer one question: **"is this edit better than doing nothing?"**
(`min_margin`, a relative threshold). It could not answer **"is the result good enough to ship?"**

Without an absolute target the loop selects the least-bad available edit even when every candidate
is a tie, and reports motion as progress. On the real default space that is exactly what it does:
four candidates, all ties, selected `(none)` -- which is honest, but only because the verdict says
"tie". An edit that improves the mean and still leaves the figure broken would have been reported as
`selected`, full stop.

AutoFigure (ICLR 2026) calls this `quality_threshold` and stops refining once a figure clears it.
The same idea, added as `MutationSpace.min_score`:

    verdict=selected  reason="improves the fixed task set by +0.450 (>= margin 0.1) with no task
                              regressing, but the result scores 0.950 -- BELOW the target 0.990:
                              this edit helps and is still not good enough to ship"

Three things this had to get right:

1. **The target must not soften the no-regression rule.** A regression is still rejected whatever
   the target says; the target is an additional clause, not a replacement.
2. **A target outside 0..1 is refused at construction.** `min_score=90` (a percentage) would make
   every edit look below target and the loop would never select anything, with no error explaining
   why. The refusal names the mistake.
3. **The message must quote the ACTUAL target.** The first version printed `0.99` as `0.9` because
   the default float format truncates -- a refusal that misquotes its own threshold is a defect.

`None` keeps the old relative-only behaviour, and the reason then does not mention a target it
never applied.

ONE THING BROKE, and it is worth recording: the signature change broke two NEGATIVE CONTROL tests,
because they monkeypatch `_verdict` with a three-argument replacement. Those controls are the
reason the decision rule can be shown to matter -- `tests/test_mutation.py` swaps in an inverted rule
and a marginless rule and asserts the selection tests then FAIL. Updating them was mandatory, not
housekeeping: a negative control that raises instead of proving something is worse than none.

Verified on the real space: `--min-score 0.9` yields four ties and `selected (none)`, with
`min_score` recorded in `knowledge/mutation_report.json` so the record states which standard was
applied.

Suite: 508 passed, 3 skipped.


## 86. The scheduled run deadlocked its own test suite (2026-10-20)

The loop's own 07:52 run reported `tests: FAILED` while I had just measured 508 passing locally. That
discrepancy is the interesting part -- a scheduled run that disagrees with a manual one is either
contention or a real regression, and the record could not tell me which.

The failing test was `test_the_probe_is_deterministic_across_processes`, which spawns a subprocess
that must ACQUIRE the measurement lock and waits **240 s** for it. And `cron_run.main()` does this:

    lock.acquire("cron_run")
    try:
        return _main_locked(argv, dry)     # benchmark slice (~30 min) -> mutation -> evolve
    finally:                                #   -> RUN THE TEST SUITE
        lock.release("cron_run")

**The lock is held across the test suite.** So the suite's own test waited for the lock that the run
was holding while waiting for the test: a self-deadlock with a 240 s fuse. Nothing was broken; the
run simply could not finish its own verification.

A test suite is NOT a measurement. It renders small fixtures and never touches the pool, so holding
the measurement lock over it protects nothing. Fixed by releasing the lock around `run_tests()` and
re-acquiring after, because the publish step follows and must not interleave with another
measurement.

THE RE-ACQUIRE IS GUARDED, and the choice matters: if another measurement has started while the suite
ran, the run does **not** publish. Losing one commit is recoverable; a commit that interleaves with
someone else's measurement is not.

VERIFIED by watching the lock file during a real run:

    lock released during run: True (after ~195s)
    evolve: ok   tests: ok

...where the same run before the fix said `tests: FAILED`.

A note on how this was found: not by reading the code, but by asking why the SCHEDULED run disagreed
with the MANUAL one. An autonomous loop whose failures look like flakiness is worse than no loop,
because it teaches you to ignore it. The fix removes that class of false signal.

Suite: 510 passed, 3 skipped.


## 87. The web page accepted a reference figure and never said whether it worked (2026-10-20)

Auditing "what else is inside the measurement lock" found the two remaining lock sites correct
(`bench_plottwin` wraps only `_run`, which is pure measurement; `evolve.py` re-measures EXISTING
figures and renders nothing, so it needs no lock). The useful finding was somewhere else.

`scripts/webapp.py` accepted a `reference` upload, measured its style profile, passed it to the
skill, and reported `RESULT: compliant`. **It never said whether the style was applied.** A user who
uploads their target journal's figure and reads "compliant" cannot tell whether their argument did
anything at all.

This is the project's recurring defect in the newest surface: a control that looks present and does
nothing -- or does something the user cannot verify. The CLI was already honest here because it
prints the operator trace (`... -> style.profile(ref.pdf) -> verify.audit`), and the trace is where
the answer lives.

Fixed by carrying the same evidence into the response:

    styled: True
    style transferred: yes
    trace: ['encode.box(...)', 'layout.plate', 'style.profile(...)', 'verify.audit', ...]

and by testing BOTH directions, because "styled is always True" would pass a one-sided test:

  * without a reference -> `styled is False` AND no `style.profile` in the trace
  * with a reference    -> `styled is True`  AND `style.profile` in the trace AND the summary line
  * a junk reference    -> refused with a reason, not silently ignored

The general lesson, which this project has now recorded in several forms: **when a surface accepts a
parameter, its output must state whether that parameter took effect.** Otherwise the parameter is
decoration, and the user has no way to tell the difference between a feature and a no-op.

Suite: 512 passed, 3 skipped.


## 88. Is a local VLM necessary? The controls say no, and the fields say "mostly not needed" (2026-10-20)

Asked whether to introduce a localised VLM. The honest answer needed evidence in both directions, so
I read what this repository already had rather than repeating my own summary of it.

FIRST CORRECTION TO MY OWN MEMORY: the corpus labelling was **already local**. `vlm_report.json`
records `models: ["gemma3:12b"]`, 40 figures, 840 field slots, JSON parse rate 1.0, all on this
machine. The question was never cloud-versus-local. It is whether the labels can be trusted.

THE CONTROLS ANSWER THAT. `corpus/vlm_controls.json` fed the model three images containing no figure
at all, and counted how many values it asserted anyway:

    control_blank.png      7 asserted,  2 fabricated   ->  "column_width": "single"
    control_noise.png     15 asserted,  9 fabricated   ->  "high_contrast": true
    control_textonly.png  12 asserted,  9 fabricated

20 fabrications across 3 controls. A model that reports `column_width: single` about a **blank page**
cannot be the ground truth for column width. These are not near-misses on hard cases; they are
confident answers about images with nothing to answer about.

THEN THE USEFUL PART: the ten fields it was asked for are not all unknowable. Six were already
measured deterministically (`audit.width`, `audit.font_type`, `audit.font_size`, `result.panels`,
`colourcheck`, `styleprofile`). This round made **two more** deterministic, so eight of ten now need
no model at all:

    figure_type            figpipe/structure.py
    panel_labels_present   figpipe/structure.py

THE NON-OBVIOUS MEASUREMENT, and the reason both needed care:

> **Panel letters are drawn at a LARGER font size than every axis label and tick.**

Matching on text alone reported the panel letters of a 4-facet histogram as `['v','a']` -- `v` was
the **y-axis label**. Font size separates them exactly (letters 8.0 pt, axis labels 7.0 pt, ticks
6.0 pt). Same class of error in the type classifier: the word `density` is an AXIS LABEL on a
histogram, and the first version called every such figure a `heatmap`. A heatmap's distinguishing
feature is a colour bar that a text-only reader cannot see, so the honest answer for a matrix figure
is `other` -- not a confident wrong guess, which is precisely the VLM's failure mode.

TWO FIELDS REMAIN (`arrow_style`, `panel_layout`). They are visually decidable and not expressible as
a deterministic check, so a local VLM COULD be justified for them -- but only after a control set
specific to each field shows the model answers controls correctly. `structure.compare_to_vlm()` is the
scaffolding for using a model as a **second opinion that is checked**, never as an answer key.

Nothing was wired into the judging path. Doing so would change the official score from
"deterministic, reproducible, 75.41" to "model-dependent, unreproducible", and the controls on this
machine do not justify that trade.

Full reasoning in VLM_DECISION.md.


## 89. BootLoops named every bug this project found, as one standard (2026-10-20)

Asked to introduce BootLoops as the quality-control chain. It is a harness for LLMs doing precision
quantitative science -- 49 packages of integral reduction and ball arithmetic that figpipe has no
use for -- plus **twelve plain-markdown protocols** that say what "done" means.

The `acceptance-gate` skill opens with:

> A result is done when it has survived a check that could have failed, run by a route that could
> not have known the answer. It is never done merely because the computation that produced it
> finished.

> The agent that produced the answer -- human or model -- is the least qualified judge of it,
> because everything that produced the answer also produces reasons to believe it.

And then it lists eleven failure modes. **Seven of them are bugs this project found, one per round,
over thirty rounds:**

    "the gate that cannot fail"       -> the anchor accepting a partial membership (18/20)
    "the unconditional success line"  -> RESULT: compliant printed after a skipped audit
    "certifying at fitted points"     -> the 100.0 score that copied reference_code
    "threshold drift"                 -> KNOWN_CORRECTIONS widened until 93.53 passed
    "adjectives in place of counts"   -> "compliant" with no per-dimension score
    "self-graded confidence"          -> the CLI reporting its own success
    "false independence"              -> styled and shipped anchors sharing a defect

I had each of those as a separate lesson, learned separately. BootLoops states them as ONE standard
with a procedure that produces evidence. That is the value: not new knowledge, but a checklist that
would have caught all seven at once.

IMPLEMENTED as `figpipe/gate.py`, translating numbers to figures:

    reserved points    -> the dimensions are module constants, not chosen per figure
    independent route  -> every check reads the RENDERED PDF back, never the drawing code
    digit count        -> every GateCheck carries `measured` and `required`
    positive control   -> a clean figure must reach CLOSED
    negative control   -> a 150 mm figure must fail, AT column_width
    true verdict       -> CLOSED only if every check passed, computed never assigned

THE BUG THE GATE FOUND IN ITSELF, which is the best argument for the gate: the first version made
`close()` require both controls, but `run_gate()` never set them -- so EVERY gate was OPEN, including
one whose every check passed. A verdict that cannot be reached is as meaningless as one that is
always reached; it is the mirror image of "the unconditional success line".

Fixed by separating two claims that were being conflated: a FIGURE's verdict ("did this figure pass
the gate") from the GATE's trustworthiness ("can this gate fire at all"). Both are needed; neither
substitutes for the other.

Verified: `gate_can_fire: True`, positive -> CLOSED, negative -> OPEN failing at `column_width`.

THE NATURAL NEXT STEP is `planted-truth`: figpipe's controls are figure-level, not data-level. There
is no test that plants a known slope and confirms the pipeline recovers it. That is the gap BootLoops
would close next.

Suite: 543 passed, 3 skipped.


## 90. The controls were figure-level, never data-level (2026-10-20)

BootLoops' `planted-truth` says why that is not enough:

> Real data cannot grade a pipeline. Whatever comes out looks like a finding -- a slope, an evidence
> ratio, a list of anomalies, an empty list of anomalies. The only inputs whose correct output is
> known are the ones you construct.

figpipe had an acceptance gate (a clean figure passes, a wrong one fails). That tests the GATE. It
never planted a known value in the DATA and demanded the drawn figure carry it.

FIRST, THE GAP MEASURED: `verify.semantics` runs on **2 of 16 drawers** (`scatter_fit`,
`trend_band`) and appends `verify.semantics(skip panel 0: <draw>)` for the other fourteen. So a
histogram, a boxplot, an error-bar panel or a ranked-share panel could print a number contradicting
its own input and every check in the project would still pass.

IMPLEMENTED `figpipe/planted.py` with four plants whose answers are exact by construction:

    constant-mean   every observation is 7.25      -> every group mean IS 7.25
    exact-slope     y = 2.5x, no noise             -> the OLS slope IS 2.5
    exact-ratio     groups of 3.0 and 1.0          -> the ratio IS 3.0
    zero-spread     every value is 5.0             -> the IQR IS 0

THEN THE TRAP I WALKED INTO, which is the point of recording this: my first version re-derived the
planted number **from the same frame the drawer saw** and compared it to itself. That is BootLoops'
named failure mode **"certifying at fitted points"** -- agreement at points the derivation already
reproduces measures nothing. All four plants "passed" while never once looking at a figure.

Fixed by reading the value back from the RENDERED PDF:

    constant-mean   4 bars, height spread 0 pt
    exact-slope     fitted line spans 429.1 x 320.2 pt
    exact-ratio     bar height ratio 3.0000
    zero-spread     2 box paths, tallest 0 pt

AND A SECOND BUG IN THE FIX: the bar-height test ran BEFORE the per-plant dispatch, so the LINE and
BOX plants were rejected for having no bars -- a check applied to the wrong object, which is exactly
how a real control gets switched off in practice. Each plant is now judged by the geometry ITS OWN
figure draws.

THE COMPARISON CAN FAIL: `corruption_control()` shifts the expected value and confirms a mismatch is
reported, so a comparison that ignored its inputs could not pass.

`gate.pipeline_controls()` connects the two levels, and they answer different questions that must
not be conflated:

    acceptance gate     is this FIGURE well formed?          (a statement about the file)
    planted truth       is the RIGHT NUMBER in it?           (a statement about the machinery)

A figure can be perfectly formed around a wrong number. Both controls, neither a substitute.

Suite: 552 passed, 3 skipped.


## 91. An empty findings list meant two opposite things (2026-10-20)

`bench_plottwin.py` recorded `semantic_findings` -- the semantic problems found. An empty list
therefore meant EITHER:

    the check RAN and found nothing      -> the task is verified
    the check NEVER RAN for this drawer  -> the task is UNVERIFIED

A pass on an unverified task is a statement about GEOMETRY, not about correctness, and nothing in
the artefact said which was which. This is the same defect as round 29's "findings is empty means
the colour check did not run", which was fixed in `quality.py` and not propagated here.

FIXED: `semantic_state()` classifies each task `checked` / `skipped` / `absent` from the TRACE, and
`report["semantic_coverage"]` counts them.

THEN I GOT THE NUMBER WRONG TWICE, which is the more useful part of this entry.

**First wrong number: 139/139 checked.** My check looked for a `verify.semantics` line without
"skip" and found the operator's bare SUMMARY line -- appended once at the end regardless. So every
task looked verified. Reading the two traces side by side showed the real shapes:

    ALL panels checked  -> only the bare `verify.semantics` summary line
    ANY panel skipped   -> `verify.semantics(skip panel N: <draw>)` lines PLUS the summary

So the rule is: a skip line means at least one panel was NOT verified, whatever else the step did.

**Second wrong number: the whole pool errored.** My first edit called `semantic_state(chosen)`, and
`chosen` does not exist -- the selected result is `(styled if chosen_is_styled else plain)`. All 139
tasks came back `NameError`, which is only visible because the re-measure was RUN rather than
assumed. A static regression test now catches that class (it parses `run_task` and checks every
argument name is bound), with a negative control proving it catches the original mistake.

**THE MEASURED TRUTH, after both corrections:**

    checked  45 / 139   (32%)
    skipped  94 / 139   (68%)
    absent    0 / 139

**68% of the pool's passes rest on geometry alone: their printed numbers were never re-derived from
the data.** That is the honest coverage figure this project did not have before, and it is the
number the next several rounds should move.

THE GENERAL LESSON, learned twice now: **when a collection's emptiness can mean both "looked and
found nothing" and "never looked", the collection cannot be the record.** The trace is the record,
because it says what executed -- and even then it must be read carefully, because a summary line is
not a per-item check.

Suite: 559 passed, 3 skipped.


## 92. A structural test that measured the text, not the code (2026-10-20)

`test_the_merge_recomputes_every_aggregate` slices the merge block out of `bench_plottwin.py` and
asserts every aggregate is reassigned there -- a good structural test, because a 6-task slice once
erased `failures`, `unsupported_types` and `semantic_violations` from a 139-task report.

It sliced a FIXED 4000-character window. This round I added a comment block elsewhere in the file
and `report["by_type"]` moved from offset ~3900 to **4029** -- 29 characters past the edge. The test
then reported a real-looking failure for a code path that was correct.

Fixed by finding the block BY INDENTATION rather than by character count. A test that breaks when
unrelated text changes is measuring the text, not the code.

This is worth recording because it is a near-miss in the opposite direction from the project's usual
defects: not a gate that cannot fail, but a gate that fails for a reason that has nothing to do with
what it claims to check. Both waste a reader's trust.

Also this round: two wrong numbers before the right one.

    139/139 checked   -- my state check matched the operator's bare summary line
    139 errors        -- my edit called semantic_state(chosen); the name does not exist
     45/139 checked   -- the measured truth

68% of the pool's passes rest on geometry alone: their printed numbers were never re-derived. That
is the honest coverage figure, and it is the number the next several rounds should move.

Suite: 559 passed, 3 skipped.


## 93. A current report that could not answer "where are we?" (2026-10-20)

A reader said the report did not look updated and they could not tell how far the project had got.
The file WAS current -- regenerated minutes earlier, and it carried the right numbers. The problem
was that it answered a different question.

The report was an INVENTORY: a list of deliverables, each with a path and a status. An inventory says
what EXISTS. It does not say what is DONE, what is BROKEN, or what the next move is. A reader who
wants orientation has to reconstruct those three things from eight sections of evidence, which is
work they should not have to do to find out whether the project is on track.

FIXED with a status board placed before everything else, built from artefacts so it cannot drift:

    Done                capabilities with a verified number behind them
    Biggest known gap   the largest KNOWN gap, stated as a number
    Unverified rules    rules with no machine check, listed by id
    Next step           the single next move, with its acceptance criterion

The board now reads, at the top of the page:

    Done              139 benchmark tasks execute with 0 errors; 564 tests pass; style anchor 0.355
                      on a single instrument; 45 tasks have their printed numbers re-derived
    Biggest gap       94 of 139 tasks (68%) are drawn by a drawer with NO semantic rule, so their
                      printed numbers were never re-derived
    Unverified rules  8 rules have no machine check and are never counted as passing: H01..C04
    Next step         Write semantic rules for grouped_bars, boxplot, histogram, heatmap.
                      Acceptance: the checked count rises and the pool score does not fall.

THE LESSON IS ABOUT REPORTING, NOT ABOUT THE PROJECT: **a report that requires reconstruction is not
a status report.** Every number was already in the file; what was missing was the sentence that says
what the numbers mean together. The test now asserts the board comes BEFORE the KPIs and the
deliverables, because ordering is the part that makes it a status rather than an appendix.

Suite: 565 passed, 3 skipped.
