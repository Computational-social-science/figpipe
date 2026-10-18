# 同行版图与"青出于蓝"路线（2026-10-18）

**对象：** VILA-Lab/FigMirror、littlepeachs/NaturePanelForge、potamides/detikzify、
HKU-MMLab/Math-VR-CodePlot-CoT、thunlp/ChartCoder。
**方法：** 五个仓库以只读方式浅克隆到 `E:\2026-AI4S\peer-repos\`（不进入 figpipe 版本库，许可
各自保留），逐仓阅读 README、方法与配置，并与其公开产物比对。**结论：** 它们的强项是"从栅格
图重建/迁移风格"与"大规模 benchmark"；figpipe 的强项是"可验证的复现与版面规格"。青出于蓝不
是去比它们的视觉分，而是把它们的短板变成我们的主线：**确定性、可审计、数据与统计可核验**。本文
记录差距、已落地的第一步与下一步路线。

---

## 1. 五个项目各是什么

| 项目 | 任务 | 方法核心 | 评测/数据 | 许可 |
|---|---|---|---|---|
| **FigMirror** (VILA-Lab) | 参考图 + 数据 → 同风格的 matplotlib 脚本与 PDF | Drawer/Reviewer 双 agent 循环；**Grounded Measurement**（VLM 给坐标，再裁线段读像素颜色）；preserve list 防漂移；Aesthetic Lib；Quality Floor（文字重叠、标签裁切、字体可读、轴出画布、退回默认样式）；硬迭代上限 | PlotTwin-Bench：399 参考、150 评测（50 手选 + 100 增广）；combined 72.7 / 76.4（GPT-5.5 条件下）；内部 hybrid style scorer | 仓库无 LICENSE 文件（**只学思想，不复制代码**） |
| **NaturePanelForge** | 开放获取 Nature 系论文 → 面板级 → 可执行绘图代码 | Codex 面板切分 + 审查；Qwen 质量/类型打分；Codex 复现+精修循环 | **8,385 个数据/统计面板**，5 领域（生物 836、环境 3,831、地理 2,688、材料 441、物理 589）；SciFigure2Code 零样本评测（11 模型；P0 执行/视觉/图型/布局/数据模式，P1 风格/配色/字体/科学标注/面板语境，P2 像素/代码相似/运行时） | MIT |
| **DeTi*k*Zify** | 草图/既有图 → 语义保持的 Ti*k*Z 程序 | 8B 多模态模型（v2.5，RLSF 自反馈强化学习）；**MCTS 推理**用 ImageSim 作奖励；TikZero 零样本文本条件 | ImageSim、CLIPScore、CrystalBLEU、KID、DreamSim、TeX 编辑距离 | Apache-2.0 |
| **Math-VR-CodePlot-CoT** | 数学视觉推理 | 代码驱动 CoT：模型产出文本推理 + 绘图代码，**渲染成"视觉思考"再喂回模型**；MatplotCode 图→代码 | Math-VR 178K 样本；5,000 题双语 bench；AC（答案正确）、PS（过程分）；相对基座最高 +21% | 仓库无 LICENSE 文件 |
| **ChartCoder** | 图表 → 代码（MLLM） | Chart2Code-160K 自指示数据引擎；LLaVA 系模型 | ChartMimic/Plot2Code/ChartX；ChartMimic 低层 72.5（code_pass），并公开修正过数据集代码 bug | 仓库无 LICENSE 文件 |

**共同范式：** 输入是**栅格图**，输出是**代码**，判据是**另一个模型/视觉相似度**；都需要大模型、
GPU/API、以及"评审模型 + 迭代上限"来兜底不确定性。

---

## 2. 它们真正强在哪（必须承认的差距）

1. **规模**：NaturePanelForge 8,385 面板、FigMirror 399 参考、ChartCoder 160K 图码对、Math-VR
   178K。我们的实测语料是 73 张 caption 锚定图 + 4 张复现版面；**差两到三个数量级**。
2. **风格迁移的入口**：FigMirror 面向"给一张参考图，按它的风格画我的数据"，这正是研究者最常用
   的入口；我们目前只有"从语料测量出的先验 + 手工选择模板"。
3. **程序空间搜索**：DeTi*k*Zify 用 MCTS + ImageSim 奖励做推理时搜索；我们是一次成型 + 少量修补。
4. **评测协议与榜单**：它们有公开 benchmark、基线、分数；我们的检查器是内部的，尚无对外协议。
5. **面板切分**：NaturePanelForge 有 Codex 面板切分 + 人工/模型审查；我们的 caption 锚定测量
   只覆盖有图注的图。

## 3. 我们已经领先的地方（青出于蓝的支点）

| 维度 | 同行 | figpipe |
|---|---|---|
| 风格测量的可重复性 | VLM 看图给坐标/颜色，需 judge 与 preserve list | **从 PDF 矢量对象直接测**：字号分布、字体、面板字母、配色、线宽、框线，同输入同输出（`figpipe/styleprofile.py`，无 GPU/API） |
| 数据真实性 | 输入是"数据表"，不校验图与数据关系；无统计复现 | **从原文数据重算并对照发表统计量**：种子复现 15/15 项 r 误差 ≤0.005 |
| 版面合规 | 没有 Nature 投稿规范检查 | 字号 5–7 pt、栏宽 89/183 mm、字体 Type 42、面板字母 8 pt、glyph 级碰撞、几何一致，全部机器检查 |
| 版面几何 | 按图猜边距/间距 | 来自 73 张真实图的测量先验（panel gap 2.9 mm、aspect 1.34、字母 8.0 pt） |
| 知识演化 | 静态仓库 | CRON 六小时自检 + 规则回归 + 知识库版本化 + 瘦身预算 |

**判断：** 在"把任意截图变成好看代码"这条赛道上，它们已经领先且需要大模型，我们不该正面拼分。
在"**让图形生产可验证、可复现、可负担**"这条赛道上，它们几乎没有布局：这正是 figpipe 应该拿下
的位置。

---

## 4. 已落地的第一步：PDF 原生风格画像（对 FigMirror 的正面回应）

`figpipe/styleprofile.py` + `scripts/profile_figure.py`：

- 输入一个 PDF（页 + bbox 或图注定位），输出**实测**：字号分布、字体、面板字母（要求 bold 8 pt，
  避免把轴标签 "y" 误认成字母）、配色（映射到 Okabe-Ito 并给 RGB 距离）、线宽、框线、页面形状。
- 两个画像可比较：`distance` 0–1，附 6 个分量（sizes/palette/letters/lines/rules/aspect），**每个
  分量都能解释**，可直接驱动模板参数。
- 测试：已知样张的字号/字母/蓝色填充/隐藏右边框必须被精确测出；自己和自己比必须为 0；只改字号时
  只有 sizes 分量变化；同样宽度不同高度必须体现在 aspect 上。

**首次实测（种子论文 Fig 7）**：

| 量 | 发表 PDF 区（184.3×153.5 mm） | figpipe 复现（183×168 mm） |
|---|---|---|
| 字号中位 | 6.44 pt（5.5–6.5，3 种） | 6.0/7.0（2 种） |
| 面板字母 | 无（标题分面） | 无（一致） |
| 主色 | 黑、浅灰、靛蓝、绿、红 | 黑/深灰、蓝、白/灰 |
| 框线 | 区域级长线 0 条 | 0 条 |
| **风格距离** | — | **0.158**（sizes 0.367 为主） |

这给出了一个可执行的结论：**复现的统计与内容已经对上（15/15），剩下的"不像"主要来自字号分布
与配色（0.367 + 0.124），不是"玄学美感"**——而这两项都是模板参数，可在规范带内被搜索优化。

---

## 5. 下一步建议（按可交付与验收标准）

### P0（本周，CPU，无外部模型）

1. **把风格距离接入复现报告**：四张版面 vs 发表 PDF 区各算一次，写入
   `templates/seed/report.json`；验收：四张距离 ≤ 0.20（当前 Fig 7 = 0.158）。
2. **模板从画像生成**：实现 `styleprofile.to_template(profile)`（在 5–7 pt 带内选字号档位、按
   Okabe 名称分配系列色、线宽取中位、决定是否网格），先做一次"固定数据、只改风格参数"的实验；
   验收：同一数据下距离相对基线下降 ≥30%，同时硬门槛（字号/栏宽/碰撞/字母）不退化。
3. **多面板框线语义**：当前框线检测只对"区域级长线"有效，2×2 多面板图的每格轴线检测不到；改为
   按面板盒内检测或在报告中标注 N/A。验收：Fig 7 四格图的边框判断不再为空。

### P1（2–4 周）

4. **确定性程序空间搜索替代 VLM 评审循环**：把模板的可变点（注释角、图例内外、刻度定位、字号
   档位、调色板槽位、面板间距微调）参数化，用"硬约束 + 风格距离 +（若有数据）统计对账"做打分，
   beam/MCTS 搜索候选；保留完整搜索轨迹（每次候选的分数与改动），**可复现**。验收：在 4 张种
   子版面上给出"无同分异构"的收敛轨迹，平均距离低于 P0 结果。
5. **建立面板级可验证 benchmark（FigPipe-Repro）**：从 caption 锚定语料（73 张，矢量 PDF）中
   选 20–30 个"有图注 + 有数据表/统计量"的面板，记录：目标 PDF、数据、发表统计量、风格画像、
   复现产物与偏差。验收：协议文档 + JSON schema + 一条命令跑出分数；不依赖任何 VLM。
6. **许可合规地做外部对比**：NaturePanelForge（MIT）的 `clean_tiny100` 可用于评测；FigMirror /
   ChartCoder / Math-VR 仓库无 LICENSE，**只引用方法与数字，不复制数据/代码**；PlotTwin-Bench
   使用前先确认其数据集许可。

### P2（1–2 个月）

7. **栅格参考的降级路径**：若参考只有截图，明确只测"可测且可信"的量（页面形状、主色、粗略线
   宽），并在画像里标 `raster_uncertain=true`；绝不把模型猜测当 ground truth（本项目已实测 VLM
   会编造图属性）。
8. **风格漂移纳入 CRON**：每周重算语料风格中位（字号/线宽/配色）与四张复现版面距离，偏离阈值即
   告警；同时保持瘦身预算（tracked ≤ 80 MB）。
9. **对外一篇方法短文**：对比"VLM 评审循环"与"确定性测量 + 精确搜索"，报告同预算下的距离、
   可复现性与成本；把 `styleprofile` 的 JSON 作为可审计产物公开。

---

## 6. 一句话

**同行把"像"交给模型去猜；figpipe 把"像"变成可测量、可搜索、可复现的目标，并且不止于像——图必须
承载原文的数据与统计。** 先拿下 PNG 到 PDF 原生风格这一层（已开始），再用确定性搜索把距离压下去，
最后以"统计可核验的复现 benchmark"立住差异；这是"青出于蓝"最现实也最难的路径。

---

## 附录：网页获取（web_fetch）故障与修复（2026-10-18）

**现象：** 抓取 `raw.githubusercontent.com` 的 README 全部失败，报
`DeepSeek API error (HTTP 404)`；而 `https://example.com`、GitHub HTML 页面均正常（200）。

**诊断：**
- 直接用本机 HTTP 请求 `raw.githubusercontent.com` 返回 200（14 KB），说明网络与目标站正常；
- 失败发生在 harness 的 fetch 提供者链路：`~/.dsh/profiles/desktop/cordis.patch.yml` 里
  `web.fetchProvider: deepseek-fetch-api`，该 API 对 `raw.githubusercontent.com` 返回 404；
- 该 harness 自带另一提供者 `http`（`@deepseek-ai/dsh-web-fetch-http`，本地 HTTP 抓取），
  是发行版默认组合里的 fetch 提供者（默认 `search: deepseek-official, fetch: http`）。

**修复：** 将配置改为 `fetchProvider: http`（search 仍为 `deepseek-search-api`），备份原文件为
`cordis.patch.yml.bak-20261018-230132`；修改后立即验证：raw README 返回 200 与全文。

**教训（与本项目"控件看起来在、实际不起作用"同构）：** 工具"存在"不等于"可用"；一个只在普通
HTML 上成功的抓取器，会在 raw 文本源上静默失败。遇到同类问题先做**分端点探测**（本地直连 vs
工具链路、不同 host），再改配置。
