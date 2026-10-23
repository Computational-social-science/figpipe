# Adopting VisionHOPE: what was attempted, what the code says, and what blocks it

Asked directly: **"立即VLM引入 https://github.com/PSRben/VisionHOPE，放弃原来本地的VLM"**.

This records what happened, because the request rests on a premise the repository does not support.

## First: VisionHOPE is not a VLM

The README states what it is, in its own words:

> PyTorch implementation of **VisionHOPE**, a visual backbone based on self-referential nested
> learning (SRNL). This repository provides **ImageNet classification, COCO detection and instance
> segmentation, and ADE20K semantic segmentation**.

`models/factory.py::create_model` returns a `HierarchicalVisionHOPE` with
`num_classes=1000, input_size=(3,224,224)` and a `head` classifier. Its output is **1000 ImageNet
logits**. There is no tokenizer, no language head, no prompt interface, and no way to ask it
"how many panels are in this image".

So it cannot replace `gemma3:12b` for the job the local VLM was being screened for. Swapping one for
the other would not be an upgrade; it would be a category error. **This is not a reason not to use
VisionHOPE -- it is a reason to be clear about what for.**

## What was actually done, in order

1. **Cloned it.** `E:\2026-AI4S\VisionHOPE`, 121 files, MIT.
2. **Checked the hardware.** RTX 4070, **12.0 GB VRAM**, compute capability 8.9, 46 SMs. CUDA 12.9
   toolkit present, `nvcc` at `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.9\bin\nvcc.exe`.
3. **Checked the Python.** The repo requires `>=3.10,<3.12`; the project interpreter is 3.14. Python
   **3.11.9** is installed at `C:\Users\Administrator\AppData\Local\Programs\Python\Python311`.
4. **Built an isolated environment.** `E:\2026-AI4S\.venv-visionhope` on 3.11.9.
5. **Installed torch.** `torch 2.14.1+cu126`, `cuda.is_available() == True`, device reported as
   `NVIDIA GeForce RTX 4070`.
6. **Installed the package.** `pip install --no-deps -e .` succeeded; `timm==0.6.13`, `numpy<2`,
   `ninja 1.13.2` installed.
7. **Imported it.** `from visionhope.models import SRNL, VisionHOPEOperator, VisionHOPEBlock` — OK.
8. **Ran it.** `SRNL(dim=64, head_dim=16).cuda()` forward **failed**.

## The blocker, exactly

    File "models/srnl_core/chunk.py", line 126, in load_cuda
        _srnl_cuda_fp32 = load_inline(
    RuntimeError: Ninja is required to load C++ extensions

`ninja` was then installed, and the next requirement is a **C++ compiler**:

    VS 18 Community  ->  only Auxiliary, Redist.  No Tools\MSVC.
    VS 2022          ->  directory exists, empty of C++ tools.
    vcvars64.bat     ->  not present anywhere under Program Files.
    cl.exe           ->  not present anywhere under Program Files.

VisionHOPE's SRNL kernel is `torch.utils.cpp_extension.load_inline` — **it compiles CUDA at first
use**, and there is no pure-Python path (`chunk.py` calls `load_cuda` unconditionally on the CUDA
route). Without MSVC's C++ build tools the kernel cannot be built, so the operator cannot run, so
neither the backbone nor a fine-tune of it is available on this machine.

**The missing piece is the "Desktop development with C++" workload of Visual Studio.** That is a
multi-gigabyte install and a machine-level change; it is not something to start unattended in the
middle of a scheduled cycle.

## What VisionHOPE IS good for here, once it runs

Its thesis is the one this project's diagnosis converged on, and `PEER_VISIONHOPE.md` already
records it:

> a system whose learning rule is fixed cannot adapt to what it is looking at -- it can only move
> along an axis somebody chose in advance.

figpipe's mutation loop was exactly that: a fixed comparison (`min_margin = 0.1` as a literal)
applied repeatedly. Rounds 65-78 fixed the *expressing* half (patches can now be proposed and
judged) but the loop still cannot **generate** a hypothesis. SRNL's contribution is a **learned
update rule**, which is the missing half.

That is a research direction for the mutation loop, **not** a replacement for the VLM. The two are
unrelated subsystems.

## The honest state of the VLM question

The screen was run on the four most capable of the **9 vision-capable local models**:

    gemma4:latest        2/4  [OOXX]   failed both panel-count controls, answered 0
    qwen3.8:27b          3/4  [XOOO]   failed blank, reported 1 panel on a white page
    qwen3.6:latest       3/4  [OXOO]   failed noise, reported 1 panel on pure texture
    gemma3:12b           3/4  [XOOO]   failed blank, reported 1 panel on a white page

**None passed.** Every failure is the same failure: inventing a panel where there is none. Three of
four is not "close" — a model that fabricates structure on a blank page cannot be trusted on a
figure where the structure is ambiguous.

That result is now reproducible in one command (`scripts/vlm_field_controls.py --model <name>`,
non-zero exit on any failure), so a better model can be screened without touching the judging path.

## The CPU path was checked and does not exist

`chunk.py` has `if not x.is_cuda:` branches, so it looked like there might be a fallback. There is
not. `models/srnl.py:114` raises unconditionally:

    ValueError: SRNL inputs and memories must be on the same CUDA device

So the operator has no CPU implementation at all, and the CUDA route requires `load_inline`, which
requires a C++ compiler. Both routes are closed on this machine.

`vswhere -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64` returns **empty** on a machine
whose only Visual Studio is "Community 2026" -- the IDE is installed and the C++ workload is not.

## What would actually unblock the vision channel

In order of cost:

1. **Install the C++ workload** (`Microsoft.VisualStudio.Workload.VCTools`) — unblocks VisionHOPE,
   which is a *backbone*, and would still need a task head and training data to answer figure
   questions. Realistically weeks, not a cycle.
2. **Try a local VLM that passes the controls.** 59 models installed, 9 vision-capable, 4 screened.
   The harness is one command and the bar is exact.
3. **Run the benchmark's vision channel with a hosted model.** The channel is defined by the
   benchmark; using its intended instrument is the only way the 0.65 share becomes a real number
   rather than a substitute.

## What this note is not

It is not a refusal. The clone, the venv, the CUDA torch and the package install are all on disk and
verified; the only missing piece is a compiler, and it is named above. If the C++ workload is
installed, `SRNL` should run and the adoption can proceed to the part that matters.
