READER STUDY: does the figure figpipe picks look closer to the reference?

WHAT YOU ARE JUDGING
    For each pair you get three images:
        pNN_reference   the published figure whose style is the target
        pNN_left        a candidate rendered in SOME published figure's style
        pNN_right       a candidate rendered in ANOTHER published figure's style

    The two candidates use IDENTICAL data and layout. ONLY the style differs: typography, palette,
    stroke weight, spines, aspect. One of them was styled from the reference itself; the other from a
    different figure in the same paper.

YOUR TASK
    For each pair, answer ONE question: WHICH CANDIDATE LOOKS CLOSER TO THE REFERENCE?
    Fill in answers.csv:

        pair,your_choice
        p01,left
        p02,right
        ...

    Answer every row. If a pair is a genuine coin-flip, write `tie` -- a tie is data, and guessing
    destroys the signal.

WHAT HAPPENS WITH YOUR ANSWERS
    `python scripts/reader_study.py --score` compares your choices with the answer key. The interesting
    number is not your raw accuracy -- it is whether your choices AGREE WITH THE METRIC. If the metric
    ranks a figure better than a reader does, the metric is measuring something other than what a reader
    sees, and that invalidates a claim this project has been making.

    30 pairs. At chance you would agree with the metric on about half.

WHAT THIS STUDY CAN AND CANNOT DETECT
    One-sided binomial, chance 0.5, alpha 0.05, with 30 pairs you must agree on
    20/30 = 0.67 to reject chance. If the true agreement is 0.70 the study
    detects it with power 0.73; at 0.80, 0.97.

    THIS IS A LIMIT OF THE CORPUS, NOT OF THE HARNESS: there are 30 same-paper pairs, and a study
    cannot be made stronger by running it on pairs that do not exist.

PLEASE DO NOT
    * open key.json
    * compare the candidates by guessing which one "looks like figpipe"
    * spend more than ~15 seconds per pair
