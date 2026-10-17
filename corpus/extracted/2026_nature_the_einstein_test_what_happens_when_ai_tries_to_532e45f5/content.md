<!-- source: 2026-Nature-The Einstein test_what happens when AI tries to rediscover relativity.pdf -->
<!-- source_pdf: D:\2026-AI4S\2026-Nature-The Einstein test_what happens when AI tries to rediscover relativity.pdf -->
<!-- pages: 3 ; extracted_by: docling 2.140.0 -->

## COULD AI REDISCOVER RELATIVITY?

Historical language models probe the degree to which AI can make creative breakthroughs.

By Philip Ball

<!-- image -->

I n 1915, Albert Einstein unveiled his general theory of relativity and transformed our view of the fabric of the physical world. The theory, which explains gravitation as a deformation of space-time by mass, is a pinnacle of modern physics that underpins cosmology, from work on black holes to measurements of gravitational waves, and is used routinely to guide space missions and GPS satellites.

It has also become a yardstick for leaders in the field of artificial-intelligence technology, who are asking whether their creations could ever make a breakthrough on that level. At the India AI Summit in New Delhi this February, Demis Hassabis, the co-founder of Google DeepMind in London, proposed training a large language model (LLM) on all that was known before a particular cut-off date - he suggested the year 1911 - to see whether it could reproduce general relativity. "That would be a good test for AGI," Hassabis said, referring to the nebulous concept of artificial general intelligence that is a goal for many in the AI industry.

Such a test needn't specifically involve general relativity. In December 2024, Owain Evans, a researcher at the non-profit organization Truthful AI in Berkeley, California, gave a talk about 'vintage' or 'historical' LLMs, which would be trained only on historical data up to a certain date. Evans asked what such models might be able to rediscover.

This year, several teams have built instances of vintage models, including an effort at Hassabis's test. But their early attempts reveal more about the limitations of current AI than about its strengths.

A relativity-like breakthrough is not inherently out of reach for AI, says Ido Kaminer, a specialist in quantum optics at Technion - Israel Institute of Technology in Haifa, who co-authored a preprint titled 'Can AI follow in Einstein's footsteps?', posted in July 1 .

But, he and his colleagues argue, it won't happen without rethinking some of the principles on which today's models are built.

## Creative leaps

Hassabis had mentioned the Einstein test analogy in media interviews last year, but another Google DeepMind researcher, Tom Zahavy, described it in detail in a position paper posted on his website in January. Titled 'LLMs can't jump' (see go.nature.com/3ykartg), the paper highlights the current inability of LLMs to make jumps of reasoning like Einstein's.

Zahavy wrote, as philosophers of science have long recognized, that such advances require not inductive reasoning that derives a general rule from the accumulation of data or examples, but abductive reasoning: "a creative leap that invents a cause for a singular phenomenon".

That isn't the forte of current AI models, which seem better suited to doing the grunt work of science than to making transformative discoveries. The models look for correlations in vast data sets, through being trained on known examples and then guided by prompts to supply the most statistically likely answers for unknown cases.

This makes them valuable predictive tools and can be helpful when there are plenty of data around. But imaginative leaps, or what twentieth-century historian of science Thomas Kuhn called paradigm shifts in understanding, often arrive when there are few data points to go on, or arise from anomalies that don't quite fit the standard picture.

The way scientists often proceed in such a situation is to develop a 'world model' - an inference about underlying principles - from small amounts of data. For example, careful observations of planetary motions by the seventeenth-century astronomer Johannes Kepler, and the mathematical relations that he deduced, led Isaac Newton to develop his gravitational law and his mechanical laws of motion in response to forces.

The opening of Einstein's handwritten manuscript on his general theory of relativity.

<!-- image -->

Can AI models similarly reason their way from sparse data to general world models? Not currently, argues Sendhil Mullainathan, a computer scientist at the Massachusetts Institute of Technology (MIT) in Cambridge. In a conference paper published in July 2 , he and his colleagues provided an 'orbital mechanics' foundation model with synthetic data on various plan­etary systems that obey Newtonian mechanics.

They found that the model never inferred the true law of gravitation (relating the force between two bodies to their masses and their separation), but inferred a different law for each planetary system, each wrong in a unique way.

Still, LLMs have been making striking advances in mathematics, in ways that suggest they can sometimes intuit logical structures underlying their training data. A finding this May from an AI chatbot, devised by the company OpenAI, that disproved an 80-year-old conjecture by Hungarian mathematician Paul Erdős was a "genuine conceptual advance", says Mullainathan.

The AI didn't just search its way to an answer by brute force, he says; the solution needed new, small abstractions along the way. At the same time, the disproof did bring together ideas already extant in the mathematical literature - so, in that way, it wasn't an Einstein-like flash of discovery from seemingly nowhere.

## A moment in time

After Hassabis brought up the 1911 test, independent AI researcher Michael Hla, in San Francisco, California, tried something like it. Writing on his website in March, Hla said that he trained an LLM he calls Machina Mirabilis on pre-1900 data, to see if it could produce quantum mechanics, Einstein's special theory of relativity (1905) and general relativity (see go.nature.com/4gnqph5).

Hla gave it helpful nudges: in one instance, he prompted it with observations about the photoelectric effect (in which light knocks electrons from metal plates), which would later be explained by Einstein's quantization of light. In another case, he gave it the essence of the 'elevator' thought experiment that would lead Einstein to general relativity.

In some cases, Hla argues, the model showed "glimpses of intuition". For example, when presented with the photoelectric effect, it stated that the light "breaks up into a multitude of distinct impulses" (hinting at the idea of light quanta). But the LLM failed in most cases, lacked any true understanding of the physics it adduced, and at times was "parroting words that seem plausible", but seemingly without "any sort of strong internal representation of the world to reason from", Hla wrote.

Hla also found that it's very hard to train such a historically constrained LLM, when the data are riddled with broken English and artefacts from digitizing printed material.

That's also what independent computer scientist Nick Levine and his co-workers found in work presented online in April (see go.nature.com/4ilz5sp), in which they attempted to build a vintage AI model using only what was known up to 1930 - a year chosen because works published in that year entered the public domain in the United States at the start of 2026.

With such a model, says Levine, who is based in San Francisco, in principle "we could try to test questions around things that were developed in the 1930s", such as Turing machines (a central concept in the theory of computation), Gödel's incompleteness theorem in the foundations of mathematics, or the particles called neutrinos (postulated in print in 1934).

Levine and his colleagues discovered that it is hard to create a vintage model fed on only what

## Feature

was known up to 1930; the training materials are maddeningly leaky. "If you ask it about what happened in the 1950s, often it'll just accidentally answer," says Levine - and often correctly. The supposedly pre-1930s model, for example, answered questions on the administration of Franklin D. Roosevelt, who was US president from 1933 to 1945. Filtering out information from after a certain date is difficult when data sets aren't precisely or accurately dated.

All the same, Levine (who worked for a time as a quantitative forecaster in economics), thinks that ultimately it should be possible to ask this "1930 mind" to make forecasts, which could include "the kinds of things that you'd see in a prediction market".

Prediction-type AI models, he says, could work for forecasting scientific discovery, too. He anticipates testing whether a model trained on data up to, say, January of this year could come up with a discovery now known to have been made in June. "I would predict that a model [like this] will make a non-trivial discovery, just because of the scale of the data and resources involved."

Researchers at the University of Zurich in Switzerland have created an entire family of historical models, in a project called Ranke-4B (see go.nature.com/46efotz). These are trained on time-stamped text with historically resonant cut-offs of 1913, 1929, 1933, 1939 and 1946. Team member and economist Daniel Göttlich, now at the Swiss Federal Institute of Technology (ETH) in Zurich, says that there aren't enough historical data or computing resources available to make these as strong as modern LLMs, so he hopes to test only whether a historical LLM might generate ideas with traces of future advances. "What we are testing for, figuratively speaking, is not so much genius, but sparks of genius," he says.

## Too many theories

There's no obvious obstacle to an AI language model producing, say, the general theory of relativity, argues computer scientist Jacob Andreas at MIT, as a probabilistic output among many other, entirely bogus, theories about a given body of data.

The problem, he says, is that it's hard to distinguish between theories that are correct, or at least worth testing, and those that are wrong. This was the issue, for example, with the various (erroneous) 'gravitational laws' generated by the orbital-mechanics model of Mullainathan and his colleagues. In mathematics, by contrast, it's possible to immediately verify each step in an LLM's workings as true or false.

This reflects a distinction between the ways in which LLMs and humans devise theories: people rarely build a range of possible theories probabilistically and then go about finding which, if any, is correct.

Think, for example, of physicist Erwin Schrödinger writing down his equation for quantum wave mechanics a century ago - even today, researchers are still wondering about his thought processes.

"Almost certainly it was not the case that his mental process looked like randomly generating a bunch of theory-like statements and then checking which ones were consistent with the actual observations," says Andreas.

There is also the problem of deciding whether an idea is worth pursuing in the first place. LLMs, for instance, "don't have a good notion of what an interesting mathematical theorem is", says Andreas. He adds that the models' ability to discern what's important "is actually where they're furthest behind human experts".

## Seeking a new paradigm

Transformative shifts in scientific understanding often come from attending to small discrepancies, outliers of precisely the kind that AI models tend to average away. "Human discovery in physics has historically often relied on a capacity for persistent 'obsession' - a cognitive style that allows a researcher to hold onto an outlier idea over years," say Kaminer and his colleagues.

## "What we are testing for is not so much genius, but sparks of genius."

Take, for example, physicist Max Planck's refusal to accept that his formula for blackbody radiation gave results close enough to the spectra measured experimentally. That determination led him, in 1900, to postulate the quantization of energy (a problem considered by Hla's Machina Mirabilis). There was arguably even less empirical motivation for special relativity - contrary to the common view, Einstein was not greatly troubled by experimental failures to detect a putative 'ether' through which light was suggested to travel.

More generally, breakthroughs in science rarely just fall out of a set body of empirical data: they come from a continual and subtle interplay between theories or concepts, experiments and experimental techniques. This is particularly true in disciplines such as molecular biology, which, unlike much of physics, aren't governed by a small set of well-defined underlying laws.

With this in mind, some researchers are developing automated systems that can select and plan experiments, conduct them robotically, and formulate hypotheses from the results 3,4 .

But even here, advances sometimes come from a change in mindset rather than fresh pivotal data. For example, intrinsically disordered proteins were thought to crystallize too poorly for X-ray analysis until researchers realized that they had no stable structure and came to see disorder as a feature, not a bug.

And examples of what would now be called biomolecular condensates - droplet-like clusters in cells - had been seen, unremarked, for many decades before the conceptual idea arose.

Could AI ever emulate such leaps of faith, reasoning or perception? That challenge, says Andreas, "probably looks more like figuring out how to automate these kinds of unconscious, ineffable leaps of intuition than it does a classical search procedure that we already know how to implement".

For a task of this type, says Mullainathan, "LLMs are not the right object by themselves". He thinks we need models trained not just on the corpus of knowledge but also on real-world data - on what the physical world is like - and on "mathematical space": how to manipulate mathematical objects. These requirements "are lagging behind in the current era", he says.

AI discovery systems will also need new performance goals, beyond merely making good statistical predictions. Relativity-scale discoveries, says Kaminer, will come from these systems "only if we optimize them for more than predictive accuracy, rewarding also simplicity, explanatory reach, and more".

There doesn't yet seem to be much incentive to create AI models that reason more like humans do. This is what computer scientist Rich Sutton at the University of Alberta in Edmonton, Canada, has called the bitter lesson of AI: that "building in how we think we think does not work in the long run". All that tends to make a difference to the performance of the algorithm is more computing power and training data. The perceived value of such AI models typically comes down to whether they make good, fast and accurate predictions, without necessarily saying anything about the physical process underlying a phenomenon. (Google DeepMind's protein-structure tool AlphaFold, for example, does not solve the problem of understanding how proteins fold, but merely sidesteps it by predicting their folded shape.)

Andreas suspects that, at least initially, LLMs will come up with only very modest discoveries "where we understand already what the important problem is", and for which the answer lies with "borrowing a solution or drawing an analogy that exists in some other area already".

And then, he says, human researchers might think, "Damn, I wish I had done a second PhD in this other field, so that I would have been able to see that."

That's not, however, what anyone said about general relativity. "They just thought, where did that come from?", says Andreas.

Philip Ball is a science writer based in London.

1. Shalyt, M., Regev, N., Soljačić, M. &amp; Kaminer, I. Preprint at arXiv https://doi.org/10.48550/arXiv.2607.27794 (2026).
2. Vafa, K., Chang, P. G., Rambachan, A. &amp; Mullainathan, S. Proc. 42nd Int. Conf. Mach. Learn. 267, 60727-60747 (2025).
3. Cooper, A. I. et al. Sci. Robot. 10, eadv7932 (2025).
4. Klimesch, J. et al. Nature 657, 47-58 (2026).