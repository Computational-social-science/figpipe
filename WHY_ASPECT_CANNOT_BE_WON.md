# Why `figure_aspect` cannot be won from the image, and what it would take

`figure_aspect` is 0.869 over 118 tasks and worth +2.53 points. I spent this round finding out whether
that gap is winnable. **Most of it is not, and the reason is a property of the benchmark, not a defect
in figpipe.**

## What the scorer actually compares

    score = 1 - |log(candidate / reference)| / |log(matplotlib_default / reference)|

The reference's aspect is extracted from its **CODE**, not from its image:

    m = re.search(r"figsize\s*=\s*\(\s*([\d.]+)\s*,\s*([\d.]+)\s*\)", reference_code)
    aspect = float(m.group(1)) / float(m.group(2))

Verified on six references: the extracted `figure_aspect` matches `figsize` **exactly** in all of them
(`PMC11502666` 1.207, `PMC12354736` 0.882, `PMC12504421` 0.462, `PMC12905268` 0.609, `PMC13106710`
1.028, `PMC13135507` 1.000).

## What the candidate can see

The candidate has the **image**, so its aspect is `pixels_w / pixels_h`. And 43 of 60 references call

    fig.savefig(OUT, dpi=150, bbox_inches="tight", pad_inches=0.20)

**`bbox_inches="tight"` crops the canvas to the ink**, so the saved image's aspect is the aspect of the
INK BOX, not of the canvas the code declared.

Measured, `arxiv_2510.17384`:

    figsize (9.5, 5.45)         -> aspect 1.7431   (what the scorer uses)
    expected pixels at 150 dpi  -> 1425 x 818
    actual image                -> 1462 x 763     aspect 1.9161
    ratio actual/expected       -> 1.026 x 0.933

The figure has four subplots (`left_gs[0]`, `left_gs[1]`, `right_gs[0]`, `right_gs[1]`), and the tight
crop removes more vertical margin than horizontal. **The image aspect differs from the code aspect by
14 %, and no image-only method can recover the difference** -- the information was destroyed by the
save call.

## How much that costs

    off by  1 %  -> score 0.916
    off by  2 %  -> score 0.832
    off by  5 %  -> score 0.586
    off by 10 %  -> score 0.191
    off by 14 %  -> score 0.000

So the distribution is bimodal: **94 of 118 tasks are already 0.8-1.0**, and the 20 tasks in 0.5-0.8 are
the outliers where the tight crop moved the aspect by 10 % or more. The median |log error| between the
image aspect and the code aspect is **0.018** -- about 2 %, which costs ~0.17 and accounts for the
0.869 mean.

## The three options, and why the honest one is "report it"

1. **Read `figsize` from the reference code.** This is what the CEILING mode does. Doing it in the
   honest mode is the premise violation I withdrew in round 100, and it is worth about +2.5 points --
   which is exactly why it is tempting and exactly why it must not be taken.

2. **Infer the crop.** Estimating how much margin `bbox_inches="tight"` removed requires knowing where
   the axes sit inside the canvas -- which is a property of the code, not the pixels. Not recoverable.

3. **Accept it and report the dimension honestly.** The remaining gap is the benchmark's own
   construction: it scores a code-level quantity against an image-level observation.

## What I am NOT claiming

That figpipe "cannot do aspect". It reproduces the reference's aspect to within 2 % on the median task,
which is the resolution the input permits. **The 0.869 is close to the ceiling this channel can reach**,
and the ceiling is set by `bbox_inches="tight"` rather than by anything in the pipeline.

The honest next step is therefore not another aspect attempt. It is `serif` and `tick_direction` --
dimensions the reference ALSO leaves to the code, but whose values are visible in the pixels.


---

# And `serif`: the dimension is 0.000 because only the failures are scored

`serif` is worth +0.92 and reads 0.000 over 6 tasks. That looks like a total failure. It is not.

## The distribution

Measured over 54 cached references:

    serif=True:  6/54   (11 %)
    serif=False: 48/54  (89 %)

The candidate always emits `sans-serif`, so **it is right on 89 % of references by default**. The reason
the dimension reads 0.000 is `_categorical_dimension`'s activation rule:

> a reference whose value EQUALS the matplotlib default is INACTIVE

`serif` defaults to `False`. So the 48 sans references never activate the dimension and are not scored;
**only the 11 % where the candidate is wrong appear in the mean.** A perfect detector would score 1.000,
worth +0.111 of the dimension.

## Can it be detected from pixels?

I tried two signals and both fail to separate the classes:

    ink density     serif 0.0143 - 0.5867      sans 0.0291 - 0.1616      OVERLAP
    h/v run ratio   serif 0.32, 0.89, 1.08     sans 0.38 - 1.82         OVERLAP

The second is the one a serif detector *should* use -- serif glyphs have horizontal strokes at the stem
ends, so the horizontal-run count should rise -- but at these text sizes (5-7 pt, rendered at ~150 dpi)
a serif's footings are **sub-pixel**. They do not produce a distinguishable run.

## What this round establishes

**Three dimensions are now characterised as "the reference leaves it to the code, and the code's value
is not visible in the pixels":** `linewidth` (round 98/100), `figure_aspect` (this round), `serif`
(this round). Together they are 9.01 + 2.53 + 0.92 = **12.5 points of the 16.3 remaining**, and all
three are bounded by the same property.

That is worth more than another attempt: **the honest ceiling of the image channel is ~86-87, not 99**,
and the ceiling is set by the benchmark's own construction rather than by anything figpipe could fix.
The ceiling of 99.19 is the CODE channel, which reads the answer key.

**The remaining winnable dimensions are small**: `tick_direction` +0.64, `background` +0.32,
`spines_removed` +0.31 -- about 1.3 points together, and each is a handful of tasks.
