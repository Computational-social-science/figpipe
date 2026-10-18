# third_party/mcts — vendored, unmodified

Source: detikzify/detikzify/mcts (https://github.com/potamides/detikzify), Apache-2.0
repository; the MCTS package itself carries the MIT licence (ImparaAI), reproduced in
LICENSE. Files copied verbatim: node.py, montecarlo.py. No modifications.

Why vendored instead of reimplemented: a tree search is small, well understood, and this
one is already correct; reimplementing it would add a second bug surface for no benefit.
figpipe uses it for program-space search over template variants (figpipe/search.py), with a
DETERMINISTIC node evaluator — the peer project uses the same library with a learned image
metric (ImageSim), which needs a GPU; ours scores with the audit and style profile.

Obligations: keep LICENSE and this notice; state the origin in any redistribution.
