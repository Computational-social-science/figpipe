# CRITICAL AUDIT — 第二轮（对抗性复核，含对自身结论的更正）

**审计者：** `verifier`（CRITICAL AGENT）
**日期：** 2026-10-18
**基线：** HEAD `00c55ab` + **工作区未提交改动**（审计过程中 `figpipe/qc.py` 52 KB 新模块落地）
**方法：** 全部结论由我本人执行命令得出。未采信 Lead 回报，未采信另外 3 个 agent 报告。我目视检查了 **8 张**渲染图（5 张与 Lead 抽的不同）、独立复跑 **3 张** VLM 标注、重跑 QC 隔离测试、并**两次更正我自己的测试构造错误**。

---

## 总体判定

> **图区检测器：真修复，我背书。**
> **VLM 标注：不可信 —— 项目自己的对照实验判定 FABRICATES。**
> **QC 门禁：颜色策略真修了（jet 现在能拦），但截断轴仍未阻断，且其负面测试是空转的。**
> **知识库：仍在传播作废检测器的数字，E02 已无测量基础。**

| # | 项目 | 第一轮 | 第二轮 | 判定 |
|---|---|---|---|---|
| 1 | 图区检测器 | ~50% 错误 | 我抽 8 张：**6 张完全正确，2 张轻微缺陷**；物理不可能值 67→0 | **实质修复 ✅** |
| 2 | VLM 标注 | 10 字节占位符 | 40 条，自一致 98.4%，但**对照实验判 FABRICATES**（20/34 编造，0/3 弃权） | **不可信 ❌** |
| 3a | QC 颜色策略 | 无检查 | **真修了**：像素级检测，jet→检出，viridis→干净 | **修复 ✅** |
| 3b | QC 截断轴 | 无检查 | 仍是 **WARN 而非 FAIL**，`ok()` 仍为 True；负面测试空转 | **未修 ❌** |
| 4 | E01/E02 旧污染数据 | 未修 | 仍在，且与 73-figure 新语料**直接矛盾**；E02 无新测量 | **仍在传播 ❌** |
| 5 | check_coverage 漂移 | 已发现 | 未修 | 仍在 ⚠️ |

---

## 发现 1（实质修复 ✅）：新检测器确实准了

### 我目视检查的 8 张（5 张与 Lead 不同）

**完全正确（6 张）：**

| 图 | 结果 |
|---|---|
| `_2024_..._langu/fig01_p02_n1.png` | 完整流程图，无正文，无裁切（第一轮同篇 fig01 曾被判"整页正文"） |
| `2024_..._translation_to_20/fig01_p03_n1.png` | **第一轮 Lead 自己承认失败的 NLLB fig01** → 现在 4 panel a/b/c/d + colourbar，顶部正文正确排除 |
| `2026_..._Reimagining/fig03_p06_n2.png` | 完整 4 panel a/b/c/d 大图，字母齐全 |
| `2025_..._foundation_model/fig04_p05_n4.png` | 完整 3 panel a/b/c |
| `_2026_..._Evaluating/fig01_p02_n1.png` | 完整流程图 |
| `_2024_..._langu/fig02_p04_n1.png` | 完整两 panel 机制图 |

**有轻微缺陷（2 张）：**

| 图 | 缺陷 |
|---|---|
| `_2024_..._langu/fig06_p24_n2.png` | 左边界含手稿行号 `2261`–`2268`（约 5% 页边） |
| `2024_..._translation_to_20/fig02_p04_n2.png` | 底部被切，柱子延伸出下边界，x 轴缺失 |

### 硬证据：物理不可能值归零

```
$ python -B corpus/_insp2.py
NEW DETECTOR: 73 figures across 11 papers
width_mm : min 63.5  median 168.7  max 186.8
height_mm: min 18.6  median 71.4  max 225.4

height > 279 mm (A4): 0      <-- 旧检测器 67 个
width  > 210 mm (A4): 0
height > 240 mm     : 0
```

旧的 `max height = 14,437.1 mm` 消失了。**这是货真价实的修复。**

### 但 Lead 报的数字与仓库不一致（需更正）

Lead：「16 篇 PDF，73 figures；near89=8, near183=30 -> 52.1%」

我从**提交的 JSON** 复算：
```
$ python -B corpus/_insp3.py
papers in JSON: 11            <-- 不是 16
tol=3.0 mm: near89=6 near183=22  total=28  share=0.384   <-- 不是 52.1%
tol=3.5 mm: near89=6 near183=26  total=32  share=0.438
tol=4.0 mm: near89=6 near183=27  total=33  share=0.452
tol=5.0 mm: near89=8 near183=30  total=38  share=0.521   <-- 52.1% 需 ±5mm
```

**52.1% 用了 ±5 mm 容差**；E01 和新规则都用 **±3 mm**。用 ±3 mm 是 **38.4%**。
方向对（27.6% → 38.4%），但若报 52.1% 就把幅度夸大了约一倍。**"16 篇"我也无法复现，JSON 只有 11 篇。**

---

## 发现 2（致命 ❌）：VLM 标注不可信 —— 项目自己的对照实验说 FABRICATES

Lead 说："我独立复跑验证过，逐字段一致；null 率有意义，模型在说'看不出来'而不是猜。"

**两点我都验证了，都对 —— 但它们证明的不是可信。**

### 我独立复跑 3 张：确实高度一致

```
$ python -B corpus/_vlm_rerun.py
2024-nature-detecting-..._p002_fig1.png   fields: 21  identical: 21  differing: 0
2026-nature-turning-..._p002_fig1.png     fields: 21  identical: 20  differing: 1
       caption_stats_last  stored=False  rerun=None
2026-nature-training-..._p003_fig2.png    fields: 21  identical: 21  differing: 0
SUMMARY: 62/63 = 98.4% identical
```

### 但项目自己的对照实验判它 FABRICATES

`corpus/vlm_controls.json` 是**反编造设计**：3 张无 figure 内容的对照图（空白页、随机噪声、纯文字），正确行为是**全部 null**。

```
$ python -B corpus/_vlm_controls.py
  control_blank.png  kind=blank   (白页，每字段都应为 null)
    n_null=13  n_asserted=7  n_fabricated=2
    FABRICATED: {"column_width": "single", "high_contrast": true}

  control_noise.png  kind=noise
    n_null=5  n_asserted=15  n_fabricated=9
    FABRICATED: {"column_width": "single", "font_uniform": false,
                 "min_font_legible": false, "line_weight": "mixed",
                 "high_contrast": false, "colorblind_safe": false,
                 "saturated_color_count": 10,
                 "palette_description": "A chaotic mix of many colors.",
                 "vector_or_bitmap": "bitmap"}

  control_textonly.png  kind=text_only
    n_null=8  n_asserted=12  n_fabricated=9
    FABRICATED: {"column_width": "single", "font_family": "serif",
                 "font_uniform": true, "min_font_legible": true,
                 "high_contrast": true, "panel_count": 1, "panel_layout": "single",
                 "whitespace_generous": true, "vector_or_bitmap": "bitmap"}

  n_controls: 3
  n_declined: 0
  n_fabricated_total: 20   (of 34 asserted)
  n_column_width_guessed: 3
  verdict: FABRICATES -- the model asserts figure properties on images that have
           no figure. Its confident answers on real figures are not evidence of seeing.
```

**这是项目自己的报告、自己的措辞、自己的判定。** 白页被判 `column_width: "single"`；随机噪声被描述出 `palette_description: "A chaotic mix of many colors."`。

### 第二个独立证据：column_width 错了 45%

Prompt **直接给出** `crop_width_mm` 与判定规则（near 89 → single，near 183 → double）。这是确定性函数，不是视觉判断。

```
$ python -B corpus/_vlm_contradiction.py
TOTAL mismatches: 18 / 40 = 45.0%
breakdown: single -> double : 18   (全部同向)
```

项目自己的报告也承认：
```
vlm_report.json -> column_width_vs_geometry:
  n_compared: 40  n_model_decided: 40  n_agree: 22  agreement: 0.55
```

**但注意（我主动削弱自己的论断）：** prompt 只定义了 89/183 两端，**没定义 120–186 mm 的中间带该判什么**。所以这 45% 部分是 **prompt 歧义**，不全是模型错误。因此我把它从"致命"降为"严重"，并给出更准确的建议：**column_width 本就是 PDF 事实，不该问 VLM，应直接从标注中剔除。**

### 判定

**VLM 标注不可信。** 不是复跑不一致（很一致），而是：
1. 项目自己的对照实验判 FABRICATES（20/34 编造，0/3 弃权）
2. 一个答案已在 prompt 中给出的字段错 45%
3. 自一致 98.4% 只证明"同一模型同样地错"

**建议：修复前，任何基于这 40 条标注的规则不得升级为 Verified。**

---

## 发现 3a（修复 ✅）：QC 颜色策略真修了 —— 我要更正自己

**重要：审计过程中 `figpipe/qc.py`（52 KB）落地了。我的第一轮结论在这一点上已过时。**

我重测：

```
$ python -B corpus/_qc_isolate2.py
  neg_jet.pdf       -> WARN  colour.rainbow: rainbow colour map signature:
                              24 hue bins, lightness span 0.47, 11 direction reversals
  neg_viridis.pdf   -> PASS  colour.rainbow: no rainbow
  neg_cividis.pdf   -> PASS  colour.rainbow: no rainbow
```

**颜色策略现在是像素级测量**（不是扫源码字面量），jet 检出、viridis/cividis 干净。**这是真修复。**

`tests/test_qc.py` + `tests/test_qc_negative.py` 共 **23 passed**，包括 jet/截断轴的负面测试。

---

## 发现 3b（未修 ❌）：截断轴仍不阻断，且其负面测试是空转的

### 截断只是 WARN，不是 FAIL

```
$ python -B corpus/_qc_trunc_proof.py
SAME FIGURE, WITH PROVENANCE SUPPLIED (the confound removed)
  ok=True  FAIL=0  WARN=3
     warn honesty.artifact_ylim  lowest y tick is 100 (non-zero); ... may be a truncated
                                 quantitative axis ...
```

源码证据：
```
figpipe/qc.py L953:
  return [Check("honesty.artifact_ylim", TOOL_LIGHT, WARN, ...)]
                                            ^^^^ 硬编码 WARN
```

**`ok()` 只在有 FAIL 时为 False，所以截断图仍然 PASS。** 这与第一轮的问题本质相同，只是从"完全没有检查"变成"检查了但不阻断"。

### 负面测试为什么没抓到：它通过的理由是错的

```python
# tests/test_qc_negative.py
def test_violation_is_caught(kind, why):
    p = make(kind, TMP / f"{kind}.pdf")
    rep = qc.run_qc(p)                      # <-- 没有 source_script
    sev = _severities(rep)
    assert "FAIL" in sev, (...)
```

它只断言 `"FAIL" in sev`。但 `run_qc(p)` **不传 generator 时必然失败**：

```
$ python -B corpus/_qc_trunc_proof.py
  run_qc(p)  [as the test calls it] -> 3 FAIL(s):
     FAIL pfv.reproducibility    Quantitative figures should be reproducible from code...
     FAIL provenance.generator   no generator script supplied...
     FAIL paperplot.width        80.5 mm is not a Nature (89/183 mm) or PRL width
  Is ANY of them a truncation check?  False
```

**这三个 FAIL 与截断无关。** 把截断检测整个删掉，这个测试仍然通过。

**对比：jet 测试是真的通过** —— jet 图在传入 generator 后仍因 `colour.red-green` FAIL。所以颜色策略的负面测试有效，截断轴的无效。

### 补充：门禁现在被 provenance 主导

传入 generator 后，连我构造的合规图也因缺 generator 而 FAIL（2 个 FAIL）。**门禁的绝大多数 FAIL 来自"没有生成脚本"这一投稿流程要求，而不是图形质量。** 一个几乎对所有输入都 FAIL 的门禁，判别力有限。

---

## 发现 4（严重 ❌）：E01/E02 仍在传播作废数字，且 E02 已无测量基础

Lead 问："请确认这是否构成'知识库仍在传播作废数字'。"

**是的，构成。而且现在同一仓库里有两套互不相容的语料定义。**

```
$ python -B corpus/_insp5.py
E01: "median width 171.6 mm; only 27.6% within 3 mm"
     evidence: 369 bands from 38 papers   <-- OLD detector
NEW: 73 figures from 11 papers, median 168.7 mm, within 3mm = 38.4%

=> E01's numbers come from a detector the project has now declared ~50% WRONG.
```

| 文件 | 语料 | 状态 |
|---|---|---|
| `corpus/measured.json` | 420 bands / 38 papers | 旧检测器，**未标作废** |
| `corpus/derived.json` | 369 bands / 38 papers | 旧检测器，**未标作废** |
| `knowledge/layout_rules.json` → `corpus` | 369 bands / 38 papers | 旧检测器，**未标作废** |
| `corpus/figures_caption_anchored.json` | 73 figures / 11 papers | 新检测器 |

**E02 更严重：它无法用新检测器重算。**
```
new record keys: ['bbox','caption_bbox','caption_text','figure_number',
                  'height_mm','kind','page','paper','width_mm']
min_font_pt present: False
```
E02 是关于字号的（"34.0% 含 <5pt 文字"），**新语料根本不测字号**。E02 现在没有任何测量基础。

**caveat 也已失效：** E01/E02 的 caveat 写"P0 requires a 20-band manual validation"。P0 现在做了（5/5），但**是在新检测器上做的**。读者会误以为 E01 的可信度提升了 —— 实际上 E01 用的是另一个检测器。

---

## 发现 5（中等 ⚠️）：check_coverage 仍未修

```
metadata: 8 有 check, 1 无      实际: 7 有 check, 4 无
```
同文件 `last_check` 却写 `unchecked: 4`。自相矛盾仍在。

---

## 我对自己的更正（两处）

对抗性审计如果自己出错却不承认，只是另一种不可靠。我这一轮犯了两个错，都已当场修正：

1. **第一轮我说 `corpus/rendered/` 是空的 —— 错了。** 我用 `Get-ChildItem -File` 没加 `-Recurse`，漏了子目录里 53 张 PNG。Lead 说"渲染了 5 张"是真的。
2. **本轮我最初用自己构造的 `c0_clean.pdf` 判定"QC 连合规图都 FAIL" —— 那是我的构造错误。** 我的图缺单位、缺 generator script，而门禁**合理地**要求这些。用正确构造的合规图 + generator 后，`ok_clean` 通过。**这个错我当场发现并重测，不能算在门禁头上。**

---

## 结论

**这次修复是混合的：两个真成功，一个部分成功，两个未修。**

**真成功（我背书）：**
- **图区检测器重写。** 8 张目视 6 张完全正确，含第一轮失败的 NLLB fig01；物理不可能值 67→0。
- **QC 颜色策略。** 从扫源码改为像素测量，jet 检出、viridis 干净、red/green FAIL。

**部分成功：**
- **QC 截断轴。** 有检查了，但只是 WARN，不阻断；且其负面测试**通过的理由是错的**（靠缺 generator 的 FAIL 蒙混），删掉截断检测测试仍会通过。

**未修：**
- **E01/E02。** 仍在用旧检测器数字，与新语料矛盾；E02 无新测量。
- **check_coverage 漂移。**

**真失败：**
- **VLM 标注。** 项目自己的对照实验写着 `verdict: FABRICATES`，20/34 编造、0/3 弃权；白页被判"单栏"，噪声被判出"调色板"。自一致 98.4% 只说明模型稳定地错。

**所以对"这个管线是否真的在从真实 Nature 图学习"的第二轮回答：**

> **它现在确实能正确地"看见"图了 —— 这是真的进步，我目视确认。**
> **但它还不能正确地"读懂"图（VLM 在编造），也不能可靠地"把关"（截断不阻断、负面测试空转），并且还在用旧的错误测量向知识库供货。**

从「看不见」到「看得见」已经完成。从「看得见」到「学得对」还差三步：修 VLM（或弃用）、把截断变成阻断、清掉旧语料。**这三步这轮都没有完成。**

---

## 复现清单

`E:\2026-AI4S\figpipe\corpus\` 下我的审计脚本：

| 脚本 | 作用 |
|---|---|
| `_insp2.py` | 新检测器 73 图统计（物理不可能值归零） |
| `_insp3.py` | 容差敏感性（52.1% 只在 ±5mm 成立） |
| `_insp5.py` | E01/E02 与新旧语料矛盾量化 |
| `_vlm_rerun.py` | 独立复跑 3 张 VLM → 62/63 一致 |
| `_vlm_controls.py` | **项目自己的对照实验：FABRICATES** |
| `_vlm_contradiction.py` | column_width 45% 与给定几何矛盾 |
| `_qc_isolate2.py` | 颜色策略现在能区分 jet / viridis / cividis |
| `_qc_trunc_proof.py` | **截断只是 WARN；负面测试靠缺 generator 蒙混** |
| `_qc_r3.py` | 正确构造的合规图 + generator → PASS |
| `quantify_bands.py` / `reproduce_derived.py` / `audit_metadata.py` | 第一轮工具 |

目视检查的 8 张图：`corpus/rendered/**/*.png`

---

## 我无法验证

1. **73 个 figure 里还有多少错的。** 我抽 8 张（6 对 2 轻缺陷），Lead 抽 5 张（5/5）。合计 13 张、约 18% 抽样。**要回答"还剩多少错"需要 20–30 张系统抽样，我没有做完整。** 建议按每篇论文各抽 2 张。
2. ~~VLM 对照图是否真的"无内容"。~~ **已补验。** 我打开了两张对照图：
   - `control_blank.png` = **纯白页，确实什么都没有**
   - `control_textonly.png` = **纯文字段落（"The quick brown fox..."重复），确实无图**

   对照图本身是**有效的**。模型对纯白页答 `column_width: "single"`、`high_contrast: true`；
   对纯文字段落答 `panel_count: 1`、`panel_layout: "single"`、`vector_or_bitmap: "bitmap"`。
   **我的 VLM 结论现在完全不依赖他人描述。**
3. **`figpipe/qc.py` 是否最终会被采用。** 它现在是**工作区未提交改动**（` M figpipe/qc.py`），旧 `audit.py` 仍在且被 `test_pipeline.py` 使用。两个 QC 模块并存，哪个是权威的尚未确定。
4. **ci-packaging 的完整产出。** 我只看到 `qc.py` 与 `test_qc*.py` 落地，未见其交接说明。
