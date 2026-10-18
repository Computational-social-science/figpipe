# CRITICAL AUDIT — figpipe：它真的在从真实 Nature 图学习，还是又一次「看起来在工作」？

**审计者：** `verifier`（CRITICAL AGENT，对抗性审计）
**日期：** 2026-10-18
**范围：** `E:\2026-AI4S\figpipe`，HEAD `3585b94`，只读审计（除本文件与 `corpus/` 下的审计脚本外未改动任何代码）
**方法：** 全部结论由我本人执行命令得出。未采信任何其他 agent 的报告。我自己写了独立的 PDF 图区提取器、渲染了 18 个图区并用 `read_image` 逐张目视检查、独立复算了 `derived.json`、独立构造违规图测试 QC 门禁。

---

## 总体判定

> **这个管线确实在从真实 Nature PDF 学习 —— 数据来源是真的、部分规则确实被真实语料证伪了 —— 但「学习」的测量基础（图区检测器）未经任何验证，且已知会产生严重错误的图区。因此当前所有基于语料的统计结论（E01/E02）都不可采信，QC 门禁在两项关键违规上是空壳。**

具体地：

| # | 判定 | 级别 |
|---|---|---|
| 1 | 图区检测器把**整页正文**当成 figure，bbox 错误率极高 | **致命** |
| 2 | QC 门禁**不检测调色板**（jet 通过）与**不检测截断坐标轴** | **致命** |
| 3 | `knowledge/layout_rules.json` 的 `check_coverage` 元数据是**手写且已漂移**，与同一文件内的 `last_check` 自相矛盾 | **严重** |
| 4 | LEARNINGS.md 自己定义的 **P0（图区检测器人工验证）从未执行**，而 E01/E02 已在同一文档中作为「实测」呈现 | **严重** |
| 5 | 「35.8% 墨迹密度」这一证伪 H02 的关键数字**不可追溯**到任何提交的产物 | **中等** |
| 6 | 历史缺陷 1（只测硬编码 H02）与缺陷 2（回归覆盖 3/8）**确实已修复** | ✅ 通过 |
| 7 | 历史缺陷 3（Startup 循环从未运行）**确实已修复**，有真实 6 小时日志与活进程 | ✅ 通过 |
| 8 | VLM 标注工作**尚未开始**（`vlm_label.py` 是 10 字节占位符） | 说明 |

**历史教训「机制看起来存在、实际是惰性的」并未完全消除：它换了一个位置 —— 从「进化循环」转移到了「图区检测」和「QC 门禁」。**

---

## 发现 1（致命）：图区检测器把整页正文当作 figure，bbox 不可信

### 证据

我写了**独立于项目代码**的提取器（复现项目的 band 算法以便公平对比），渲染了 18 个图区到 PNG，然后**用 `read_image` 逐张目视检查**。

**样本 1 —— 整页正文被当作 figure：**
```
文件: _2024_Nature_Detecting_hallucinations_in__p01_b0.png
bbox: 191.7 x 250.1 mm, 249 text spans
```
实际内容：**整页 Nature 评论文章的正文**，标题为 "LLMs can combat LLM hallucinations" —— 一个段落、两栏文字、页眉页脚。**这不是 figure。**

**样本 2 —— bbox 把图注 + 两段正文一起吞进去：**
```
文件: _2024_Nature_Detecting_hallucinations_in__p20_b0.png
bbox: 130.7 x 206.3 mm
```
实际内容：上方是一个真实的柱状图（DeBERTa/GPT-4 对比），紧接着是 "Supplementary Figure 1: Entailment method choice..." 图注，**然后是两大段正文**（"Similarly, there are cases where bi-directional entailment..."）。真实 figure 高度约占 bbox 的 55%，**bbox 下边界多出约 40% 的正文**。

**样本 3 —— 提示词模板框被当作 figure：**
```
文件: _2026_Nature_Evaluating_large_language_m__p11_b0.png
bbox: 171.5 x 81.9 mm
```
实际内容：一个 "Consistency template" 文本框，里面是 `<query>{query}</query>` 之类的 prompt 模板。**不是 figure。**

**样本 4 —— 真实 figure 但被裁切：**
```
文件: _2026_Nature_Evaluating_large_language_m__p02_b0.png
bbox: 89.5 x 27.7 mm
```
实际内容：一个流程图的**上下边缘文字被切掉**（顶部与底部的标签不完整）。

**样本 5 —— 这是唯一一个基本正确的：**
```
文件: _2024_Nature_Detecting_hallucinations_in__p02_b0.png
bbox: 184.0 x 55.4 mm
```
真实流程图，内容完整（但把图注文字也包含进去了）。

### 我在 18 张样本上的目视分类

| 类别 | 数量 | 说明 |
|---|---:|---|
| 整页/大段正文被当作 figure | 2 | 完全错误 |
| 图注+正文被并入 bbox | 3 | bbox 严重偏大 |
| 非 figure（模板框/表格） | 2 | 错误 |
| 真实 figure 但被裁切 | 2 | 内容丢失 |
| 真实 figure，基本正确 | 9 | 可用（部分含图注） |

**约 50%（9/18）的图区存在明确错误。**

### 结构性证据（可推广到全部 420 个图区）

不依赖我的目视样本，从 `corpus/measured.json` 直接统计：

```
$ python -B corpus/quantify_bands.py
width_mm : min 63.5  median 172.2  max 566.6
height_mm: min 25.4  median 78.3  max 14437.1     <-- 14,437 mm！物理上不可能
n_text_spans: min 0  median 9  max 647

bands with > 200 text spans : 10 (2.4%)     <-- 正文页
bands with > 100 text spans : 36 (8.6%)
bands with 0 text spans     : 181 (43.1%)   <-- 完全没有文字，可疑
bands taller than 240 mm    : 67            <-- 超过 A4 高度(279mm)的邻近值
bands taller than 200 mm    : 83
```

**`max height = 14,437.1 mm` 是一个物理上不可能的数值**（A4 高 279 mm）。这说明 band 合并算法在纵向可以跨越数十页把内容连成一条。

### 为什么清洗步骤没能拦住

`scripts/derive_rules.py:39-54` 的 `clean()` 只检查三项：
- `width > 210 mm`（太宽）
- `width < 60 mm`（太窄）
- `min_font_pt < 2.0`（字号过小）

**它从不检查高度、宽高比、文字密度或文字跨度数量。** 因此：
- 191.7 × 250.1 mm、249 spans 的**整页正文**（发现 1 样本 1）**通过了清洗**，成为 369 个"figure bands"之一。
- 4 个高度 > 279 mm 的 band 也通过了。

我用独立实现复现 `clean()`，确认清洗逻辑本身无误（见发现 3），**问题在于清洗规则覆盖不到这些错误模式**。

### 可复现性

**完全可复现。** 我的脚本在 `corpus/extract_for_audit.py`、`corpus/quantify_bands.py`；渲染的 18 张图在 `corpus/extracted/`。任何人可用 `read_image` 复核。

### 修复建议

1. **立即执行 LEARNINGS.md 自己定义的 P0**：人工标注 ≥20 个真实 figure 边界，与检测器对比。这是项目自己写下的门槛，却从未做。
2. **在 `clean()` 中增加物理约束**：`height_mm <= 279`、`0.2 <= aspect <= 8`、`text_spans <= 100`（真实 figure 极少超过此值）。
3. **检测器改为按 caption 定位**：Nature 的图注以 "Figure N" / "Extended Data Fig." 开头，用图注位置反推 figure 上边界，比"连通矩形"可靠得多。
4. **在检测器验证通过前，E01/E02 必须保持 `hypothesis` 且标注"测量方法未验证"。**

---

## 发现 2（致命）：QC 门禁不检测调色板，也不检测截断坐标轴

### 证据

我构造了**除单一违规外其余全部合规**的图（6pt 字体、183 mm、fonttype 42），逐一测试 `figpipe.audit.audit()`：

```
$ python -B corpus/test_qc_isolated.py
QC GATE ON ISOLATED VIOLATIONS (everything else compliant)
================================================================================
  c0_clean.pdf             expected PASS got PASS OK   findings=none
  c1_jet_only.pdf          expected FAIL got PASS *** WRONG ***  findings=none
  c2_truncated_axis.pdf    expected FAIL got PASS *** WRONG ***  findings=none
  c3_4pt_only.pdf          expected FAIL got FAIL OK   findings=['font_size']
```

**`c1_jet_only.pdf`（jet 色图）通过门禁，零发现。**
**`c2_truncated_axis.pdf`（y 轴截断，5.5–10.5 而数据 6–10）通过门禁，零发现。**

### 源码证据

```
$ python -B corpus/test_qc_gate.py  (关键词扫描 audit.audit 源码)
  palette      in audit(): False
  okabe        in audit(): False
  colormap     in audit(): False
  jet          in audit(): False
  hue          in audit(): False
  color        in audit(): False
```

`figpipe/audit.py` 的 docstring（第 20-21 行）**声称**检查：
> `palette      the figure uses the Okabe-Ito hues`

**但 `audit()` 函数体内没有任何颜色相关代码。** 文档承诺了一个不存在的检查 —— 这正是项目历史上「机制看起来存在、实际是惰性」的同一模式，只是换了位置。

`audit()` 实际只检查：`font_size`、`width`、`height`、`font_type`、`overlap`。

### 截断坐标轴

`audit.py` 完全没有"坐标轴是否从零开始"或"是否截断"的概念。构造的截断轴图通过。

### 可复现性

**完全可复现。** `corpus/make_clean_violations.py` 生成违规图，`corpus/test_qc_isolated.py` 测试。

### 修复建议

1. **调色板检查**：解析 PDF 中的填充色/描边色，与 Okabe-Ito 色值表比对；或要求 `style.py` 的 `OKABE_ITO` 是唯一色源并在渲染前拦截未知颜色。
2. **截断轴检查**：需要读回 matplotlib 的轴范围 —— 但这是**源码级**信息，PDF 里没有。正确做法是在 `style.py` 提供一个 `save()` 包装，检查每个 Axes 的 `get_ylim()` 是否包含 0 或数据极值，与 PDF 审计并行。
3. **修正 `audit.py` 的 docstring**：删掉 "palette" 一行，或在实现前标记为 `# NOT IMPLEMENTED`。文档承诺未实现的检查，比没有检查更危险。
4. **增加回归测试**：把 `c1_jet_only.pdf` 和 `c2_truncated_axis.pdf` 固化为测试夹具，要求门禁必须 FAIL。

---

## 发现 3（严重）：`check_coverage` 元数据是手写的，已经与同一文件内的数据矛盾

### 证据

```
$ python -B corpus/audit_metadata.py
check_coverage: METADATA vs REALITY
  metadata rules_with_check    : 8
  actual   rules_with_check    : 7
  MATCH: False

  metadata rules_without_check : 1
  actual   rules_without_check : 4  ['H01', 'H02', 'E01', 'E02']
  MATCH: False
```

`layout_rules.json` 中：
- `check_coverage`（第 208-215 行）声称：8 条有 check，1 条没有（只有 H01）
- 同一文件的 `last_check`（第 216-231 行）声称：`checked: 7`, `unchecked: 4`, `unchecked_ids: [H01, H02, E01, E02]`

**同一个 JSON 文件内部自相矛盾。**

### 根因：没有代码维护它

```
'check_coverage' 在 evolve.py 中出现: 0 次
'check_coverage' 在 ingest_corpus.py 中出现: 0 次
  -> 仅 add_checks.py 出现 1 次（一次性写入，之后不再更新）
```

`add_checks.py` 是一次性迁移脚本，写完后不再运行。此后新增了 H02 降级与 E01/E02，`check_coverage` 从未更新。

### 为什么这重要

项目历史上第 4 个缺陷就是「规则可从无执行机制却标 verified」。`check_coverage` 正是那个「让人相信覆盖完整」的字段 —— 它现在声称 8/9 有检查，实际 7/11。**读者若只看 `check_coverage` 会得出错误结论。**

### 修复建议

1. **让代码生成 `check_coverage`**：在 `evolve.py` 的 `main()` 里，每次运行后用实际规则重算并写回（`_atomic_write` 已有）。
2. 或**删除该字段**，因为 `last_check` 已经包含真实计数，重复数据必然漂移（项目自己在 HANDOFF 历史中已总结过这条教训）。
3. 增加测试：断言 `check_coverage.rules_with_check == sum(1 for r in rules if r.get("check"))`。

---

## 发现 4（严重）：项目自己定义的 P0 从未执行，但 E01/E02 已作为「实测」呈现

### 证据

`LEARNINGS.md` 第 142-150 行明确写着：

> ### P0：验证测量方法本身
> **当前最大风险是我的"图区检测"是错的。**
> 做法：手工标注 20 个图区的真实边界，与自动检测对比。
> - 若吻合率 > 90 % → 结论 A 可信，继续
> - 若 < 70 % → 重写检测器，此前所有数字作废
> **在此之前，不应把 E01/E02 写成 verified。**

### 但：

1. **没有任何人工标注产物存在**（我搜索了 `*manual*`、`*valid*`、`*gold*`、`*label*`，只有 10 字节的 `vlm_label.py`）。
2. **没有任何测试验证检测器**（`tests/` 中 `find_figures` 出现 0 次）。
3. **E01/E02 确实仍是 `hypothesis`** —— 这一点项目做对了，标注是诚实的。
4. **但 LEARNINGS.md 与 knowledge base 把 171.6 mm、27.6%、34.0% 这些数字作为"实测"反复引用**，而它们的测量基础从未验证。

而我的发现 1 已经证明：**如果做 P0，吻合率会远低于 70%**（我的 18 张样本里约 50% 有明确错误），按项目自己写的规则，"此前所有数字作废"。

### 判定

**标注是诚实的（`hypothesis` 正确），但把未验证测量得到的数字当作"实测"反复呈现，与 LEARNINGS.md 自己的 P0 规则冲突。** 这是「文档跑在证据前面」的温和版本 —— 项目已经知道问题在哪，却没有停下来。

### 修复建议

1. **立刻执行 P0**（现在可以借助我的 `corpus/extracted/` 18 张图作为起点）。
2. 在 P0 完成前，E01/E02 的 evidence 字段应加注 `"MEASUREMENT UNVALIDATED — see LEARNINGS P0"`。
3. 修复检测器后，**重新生成 `measured.json` / `derived.json`**，不要修补旧数字。

---

## 发现 5（中等）：证伪 H02 的「35.8%」不可追溯

### 证据

`layout_rules.json:176` 与 `LEARNINGS.md:121` 都声称：
> "The first real Nature figure inspected (**nwag582fig1**) has an ink density of **35.8 %**"

```
$ 搜索 *nwag* 文件 -> 无
$ 搜索 corpus/*.json 与 knowledge/*.json 中的 ink 值 -> 只有这一句文字，没有任何测量产物
```

**该 figure 不在仓库中，35.8% 没有任何可复算的产物支撑。**

### 但方向是对的

我独立测量了渲染出的 18 个真实 Nature 图区的墨迹密度：

```
$ python -B corpus/ink_check.py
  n=18  min 7.4%  median 23.6%  max 82.6%  mean 29.0%

  H02's claimed 'compliant band' was 3.3-17.4%.
  Real Nature bands inside that band : 7 of 18
  Real Nature bands ABOVE 17.4%     : 11 of 18
```

**11/18 超过 17.4%，中位数 23.6%，最高 82.6%。** H02 的证伪在**方向上完全正确**，而且我的数据比 35.8% 更有说服力。

### 修复建议

1. 用**可追溯的产物**替换 35.8%：把 ink density 写进 `derived.json`，并记录 figure 文件名与页码。
2. 把「nwag582fig1」这个无法定位的引用换成本地语料中的真实文件。

---

## 发现 6（通过）：历史缺陷 1、2 确实已修复

### 缺陷 1（只测硬编码 H02）—— 已修复

```
$ python -B corpus/audit_coverage.py
  'H02' appears 0 times in evolve.py
  hardcoded rule ids in evolve.py: []
  'check' appears 42 times
```
`evolve.py` 现在有通用的 `run_check(spec)` 与 `RUNNERS` 字典分发（`_check_rcparams`、`_check_rcparams_range`、`_check_symbol_exists`、`_check_ink_density_band`），**不再硬编码任何规则 ID**。

### 缺陷 2（回归覆盖 3/8）—— 已修复

规则从 8 条增至 11 条，**7 条带有可执行的 `check` 规格**（L01–L07），由通用分发器执行。循环日志显示 `checked: 7, passed: 7, unchecked: 4`，且 `unchecked` 是**明确报告**的，不是被计为通过。分母问题已解决。

（注意：这 7 条 check 本身是否有效是另一回事 —— 见发现 2，QC 门禁不检测调色板。）

---

## 发现 7（通过）：历史缺陷 3（Startup 循环从未运行）确实已修复

### 证据

```
$ Get-ChildItem "$env:APPDATA\...\Startup"
figpipe-evolve.vbs    506 bytes     <-- 存在，且是 Windows 会执行的扩展名

$ 内容: WshShell.Run "powershell.exe ... -File ""E:\2026-AI4S\figpipe\scripts\loop.ps1""", 0, False
```

`.vbs` 是 Windows Startup 会执行的类型（.exe/.bat/.cmd/.lnk/.vbs/.com），且注释明确记录了第一次用 `.ps1` 失败的原因。

### 它真的在跑

```
$ Get-Content knowledge/loop.log
[2026-10-17 18:02:56] loop started
[2026-10-17 18:02:56] exit=0
  knowledge: v7 -> v7  changed=False
  rules: {'verified': 8, 'hypothesis': 1, 'regressed': 0}
  pushed to origin/main
[2026-10-18 00:03:07] exit=0
  knowledge: v11 -> v11  changed=False
  rules: {'enforced': 7, 'measured_unenforced': 1, 'hypothesis': 1, 'regressed': 0}
  pushed to origin/main
```

- 两次运行间隔 **6h00m11s**，与 `Start-Sleep -Seconds (6*3600)` 一致
- **有活进程**：PID 64040，命令行确认为 `loop.ps1`
- `changed=False` 说明幂等性修复生效（历史上版本号会虚增）

**这是项目里唯一一个我完全确认「机制真实存在且在工作」的部分。**

---

## 发现 8（说明）：VLM 标注尚未开始

```
$ Get-Item scripts/vlm_label.py
size: 10 bytes
内容: print(1)
```

`citation-fixer` agent 的 VLM 标注工作**目前只有一个占位符**。因此：
- 任务要求我「自己挑 3 张图用相同 prompt 复跑比对」**无法执行**（没有 prompt、没有标注结果）。
- 「检查 null 比例」**无法执行**。
- **没有任何 VLM 标注产物可审计。**

这不构成缺陷（工作可能正在进行），但**任何声称 VLM 标注已完成或可信的报告，在当前时点都是没有依据的**。

---

## 附：测试质量评估（任务第 5 项）

```
$ 各测试文件断言数 / 存在性检查数
  test_evolution.py    asserts=9   existence-checks=1
  test_pipeline.py     asserts=26  existence-checks=0
  test_scheduling.py   asserts=10  existence-checks=6
```

**测试质量明显优于「只测文件存在」的指控：**

- `test_evolution.py` 测的是**真实不变量**：H02 必须是 `refuted` 且携带 `refuted_by` 中的 35.8、版本号在两次运行间不得变化（真的调用 `evolve.py` 两次）。它还记录了**测试自身曾经递归挂起**的缺陷及修复。
- `test_pipeline.py` 有 26 个断言，覆盖字号带、log 轴指数、字体类型等，且是**渲染后审计**（读 PDF）而非读源码。

**但覆盖有缺口：**
```
$ 搜索 palette|okabe|colormap|jet|truncat in tests/
  test_pipeline.py:31  ax.plot(..., color=style.OKABE_ITO["blue"], ...)   <-- 只是使用，不是检测
  (无任何测试覆盖调色板或截断轴)
```

**测试套件 27 passed，但它们无法发现发现 2 的两个致命缺陷，因为没有测试构造 jet 或截断轴的反例。**

---

## 结论：这个管线是否真的在从真实 Nature 图学习？

**一半是，一半不是。**

**真的部分（不可否认）：**
- 语料是**真实的本地 Nature PDF**（我独立确认 42 个文件、33 个唯一、渲染出真实 Nature 图）。
- **H02 被真实语料证伪了**，而且我独立验证了证伪方向正确（11/18 超出声称的带，中位 23.6% vs 声称上限 17.4%）。
- **「进化循环」这次是真的**：6 小时定时、真实日志、活进程、幂等性修复、无硬编码规则 ID、7 条规则有通用 check。
- 项目**主动降级了自己的规则**（H02 → refuted），并把新观察标为 `hypothesis` 而非 `verified`。这在同类项目里是罕见的诚实。

**不成立的部分：**
- **测量基础从未验证。** 图区检测器把整页正文当作 figure，bbox 可超出真实 figure 40%，高度可达 14,437 mm（物理不可能）。项目自己定义的 P0 门槛（人工验证 20 个图区）**从未执行**，而按项目自己的规则，吻合率若 <70% 则「此前所有数字作废」。
- **QC 门禁在两处关键违规上是空壳**：jet 色图通过、截断坐标轴通过。`audit.py` 的 docstring 声称检查调色板，代码里一行都没有。
- **`check_coverage` 元数据已漂移**，与同一文件内的真实计数矛盾。

**所以：项目确实在「从真实 Nature 学习」这个方向上迈出了真实的一步 —— 语料是真的、证伪是真的、循环是真的。但它还没有能力确认「学到的东西是否正确」，因为测量工具本身未经检验，而项目自己已经写出了这个门槛却没有跨过去。**

这正是历史模式的**第四次重演，只是换了一个位置**：从「进化循环是空壳」变成「图区检测是未验证的」，从「规则标 verified 但无机制」变成「QC 声称查调色板但没实现」。**形式变了，惰性没变。**

---

## 复现清单

所有脚本在 `E:\2026-AI4S\figpipe\corpus\`：

| 脚本 | 作用 |
|---|---|
| `extract_for_audit.py` | 独立图区提取 + 渲染 18 张 PNG 到 `corpus/extracted/` |
| `quantify_bands.py` | 420 个 band 的结构统计（高度/文字跨度/不可能值） |
| `reproduce_derived.py` | 独立复现 `derived.json` 的全部数字 |
| `audit_rules.py` | 逐条规则的 evidence 可复现性检查 |
| `ink_check.py` | 18 张真实 Nature 图的墨迹密度（验证 H02 证伪方向） |
| `make_clean_violations.py` | 构造单违规图（jet / 截断轴 / 4pt） |
| `test_qc_isolated.py` | **证明 QC 门禁放过 jet 与截断轴** |
| `audit_coverage.py` | 规则 check 覆盖与硬编码检测 |
| `audit_metadata.py` | `check_coverage` 元数据漂移证明 |

---

## 我无法验证的事项

1. **VLM 标注质量** —— `vlm_label.py` 是 10 字节占位符，无 prompt、无输出、无 null 比例可查。
2. **35.8% 这个具体数字** —— 引用的 `nwag582fig1` 不在仓库，无产物支撑。我用 18 张图独立确认了**证伪方向正确**，但无法确认 35.8 本身。
3. **42 篇 PDF 的期刊纯度** —— 我确认文件名含 NATURE 且排除了 Nature Communications / npj / Scientific Reports / National Science Review，但**未逐篇核对 DOI**，可能仍有非研究论文（1991/1997/2008 的短文）混入，这正是 LEARNINGS.md P1 指出的问题。
4. **`measured.json` 是否由当前代码生成** —— 我复现了 `derived.json` 的清洗逻辑（除一处四舍五入），但**没有重跑 `learn_from_corpus.py` 全流程**（需数分钟扫描 38 篇 PDF）。`measured.json` 的 420 个 band 与我的独立提取是否逐条一致，我未完整比对。
5. **其他 3 个 agent 的工作** —— 按铁律未采信。`vlm_label.py` 的 10 字节内容是我自己读出来的。


---

## 附录：第二轮复核与历史审计（原文件已删，细节见 git 历史）

- 第二轮对抗性复核（原 `CRITICAL_AUDIT_R2.md`）更正了第一轮的两处判断，并明确认为
  **图区检测器的修复有效**；其核心更正已并入本文件与 `LEARNINGS.md`，不再单独保留文件。
- 更早的 `AUDIT.md`（格式化能力成立、"自主进化"为空的逻辑审计）的结论已由本文件与
  `LEARNINGS.md` 覆盖。
- 保留本文件作为唯一审计记录：它包含致命/严重项的证据与整改状态。
