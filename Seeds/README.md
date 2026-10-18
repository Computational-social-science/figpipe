# Seeds — the reproduction targets

`Seeds/0001/` is one published Nature Human Behaviour paper together with the material needed to
reproduce its figures from the original data:

    2026-NHB-The growing concentration of national influence in global science.pdf
    41562_2026_2489_Fig1_HTML.png … Fig7_HTML.png     the published panels, as printed
    dataverse_files/*.R                                the authors' reproduction recipe
    dataverse_files/*.csv / *.pbz2                     the authors' raw data  <-- NOT here

## Why the raw data is not in this repository

Measured 2026-10-18: the twelve raw data files total **1567.5 MB**. A scheduled run's
`git add -A` staged them and committed them, taking the tracked footprint from ~70 MB to
1717.6 MB and failing `tests/test_lean.py::test_tracked_size_is_within_budget`. The owner's
standing instruction is that figpipe must evolve *and* stay slim ("避免自身不断无节制地体积增长"),
so 1.5 GB of third-party cache cannot live in version control or in the worktree.

The files were **moved, not deleted**, to:

    E:\2026-AI4S\dataverse_cache\0001\dataverse_files\

They are the dataverse deposit published with the paper; re-downloading restores them exactly.
`.gitignore` now ignores `Seeds/**/dataverse_files/*.csv` and `*.pbz2` so a future
`git add -A` cannot repeat the mistake, and `scripts/cron_run.py` refuses to stage a commit
whose files exceed a size budget.

## What follows from this

The paper, its printed panels and its R recipe stay tracked (3.75 MB total): those are the
*structure* — what the figure looks like and how it was made. The raw tables are the *cache*:
large, replaceable, and not the thing figpipe is learning from. Reproducing this paper's
seven-panel plate is a concrete test case for `figpipe.composite`, and the recipe in
`dataverse_files/` says which data file feeds which panel.
