<!-- source: 2025-Nature-A foundation model to predict and capture human cognition&SI.pdf -->
<!-- source_pdf: D:\2026-AI4S\2025-Nature-A foundation model to predict and capture human cognition&SI.pdf -->
<!-- pages: 146 ; extracted_by: docling 2.140.0 -->

## A foundation model to predict and capture human cognition

[https://doi.org/10.1038/s41586-025-09215-4](https://doi.org/10.1038/s41586-025-09215-4)

Received: 26 October 2024

Accepted: 29 May 2025

Published online: 2 July 2025

Open access

<!-- image -->

Check for updates Marcel Binz 1 ✉ , Elif Akata 1 , Matthias Bethge 2 , Franziska Brändle 3,4 , Fred Callaway 5 , Julian Coda-Forno 1 , Peter Dayan 2,4 , Can Demircan 1 , Maria K. Eckstein 6 , Noémi Éltető 4 , Thomas L. Griffiths 7 , Susanne Haridi 1,8 , Akshay K. Jagadish 1,2,4 , Li Ji-An 9 , Alexander Kipnis 1 , Sreejan Kumar 7 , Tobias Ludwig 2,4 , Marvin Mathony 1 , Marcelo Mattar 5 , Alireza Modirshanechi 1 , Surabhi S. Nath 2,4,8 , Joshua C. Peterson 10 , Milena Rmus 1 , Evan M. Russek 7 , Tankred Saanum 1,4 , Johannes A. Schubert 4 , Luca M. Schulze Buschoff 1 , Nishad Singhi 11 , Xin Sui 2,4 , Mirko Thalmann 1 , Fabian J. Theis 12,13,14 , Vuong Truong 4 , Vishaal Udandarao 2,15 , Konstantinos Voudouris 1 , Robert Wilson 16 , Kristin Witte 1 , Shuchen Wu 1 , Dirk U. Wulff 17,18 , Huadong Xiong 16 &amp; Eric Schulz 1

Establishing a unified theory of cognition has been an important goal in psychology 1,2 . A first step towards such a theory is to create a computational model that can predict human behaviour in a wide range of settings. Here we introduce Centaur, a computational model that can predict and simulate human behaviour in any experiment expressible in natural language. We derived Centaur by fine-tuning a stateof-the-art language model on a large-scale dataset called Psych-101. Psych-101 has an unprecedented scale, covering trial-by-trial data from more than 60,000 participants performing in excess of 10,000,000 choices in 160 experiments. Centaur not only captures the behaviour of held-out participants better than existing cognitive models, but it also generalizes to previously unseen cover stories, structural task modifications and entirely new domains. Furthermore, the model's internal representations become more aligned with human neural activity after fine-tuning. Taken together, our results demonstrate that it is possible to discover computational models that capture human behaviour across a wide range of domains. We believe that such models provide tremendous potential for guiding the development of cognitive theories, and we present a case study to demonstrate this.

The human mind is remarkably general 3 . Not only do we routinely make mundane decisions, such as choosing a breakfast cereal or selecting an outfit, but we also tackle complex challenges, such as figuring out how to cure cancer or explore outer space. We learn skills from only a few demonstrations 4 , reason causally 5 and fuel our actions through curiosity 6 . Whether we are climbing mountains, playing video games, or creating captivating art, our versatility defines what it means to be human.

By contrast, most contemporary computational models, whether in machine learning or the cognitive sciences, are domain specific. They are designed to excel at one particular problem and only that problem. Consider, for instance, AlphaGo, which is a computer system created by Google DeepMind to master the game of Go 7 . The system can play this particular game at an impressive level, but it cannot do much beyond that. A similar pattern can be observed in the cognitive sciences. For instance, prospect theory, which is one of the most influential accounts of human cognition, offers valuable insights into how people make choices 8 , but it tells us nothing about how we learn, plan or explore.

If we want to understand the human mind in its entirety, we must move from domain-specific theories to an integrated one. The importance of such a unified approach has already been recognized by the pioneers of our field. For example, in 1990, it was stated that "unified theories of cognition are the only way to bring [our] wonderful, increasing fund of knowledge under intellectual control" 2 . How can we make meaningful progress towards such theories?

An important step towards a unified theory of cognition is to build a computational model that can predict and simulate human behaviour in any domain 2,9 . In this paper, we take up this challenge and introduce Centaur-a foundation model of human cognition 10 . Centaur was designed in a data-driven manner by fine-tuning a state-of-the-art large language model 11 on a large corpus of human behaviour. For this purpose, we curated a large-scale dataset called Psych-101, which covers trial-by-trial data from 160 psychological experiments (see Methods, 'Data collection' and Extended Data Fig. 1). We transcribed each of these experiments into natural language, which provides a

1 Institute for Human-Centered AI, Helmholtz Center, Munich, Germany. 2 University of Tübingen, Tübingen, Germany. 3 University of Oxford, Oxford, UK. 4 Max Planck Institute for Biological Cybernetics, Tübingen, Germany. 5 New York University, New York, NY, USA. 6 Google DeepMind, London, UK. 7 Princeton University, Princeton, NJ, USA. 8 Max Planck School of Cognition, Leipzig, Germany. 9 University of California, San Diego, San Diego, CA, USA. 10 Boston University, Boston, MA, USA. 11 TU Darmstadt, Darmstadt, Germany. 12 Institute of Computational Biology, Helmholtz Center, Munich, Germany. 13 TUM School of Computation, Information and Technology, Technical University of Munich, Munich, Germany. 14 TUM School of Life Sciences, Technical University of Munich, Munich, Germany. 15 University of Cambridge, Cambridge, UK. 16 Georgia Institute of Technology, Atlanta, GA, USA. 17 University of Basel, Basel, Switzerland. 18 Max Planck Institute for Human Development, Berlin, Germany. ✉e-mail: marcel.binz@helmholtz-munich.de

a

Fig. 1 | Overview of Psych-101 and Centaur. a, Psych-101 comprises trial-bytrial data from 160 psychological experiments with 60,092 participants making 10,681,650 choices in total and involving 253,597,411 text tokens. It contains domains such as multi-armed bandits, decision-making, memory,

<!-- image -->

supervised learning, Markov decision processes and others (the examples shown have been stylized and abbreviated for readability). b, Centaur is a foundation of model human cognition that is obtained by adding low-rank adapters to a state-of-the-art language model and fine-tuning it on Psych-101.

common format for expressing vastly different experimental paradigms 12,13 . The resulting dataset has an unprecedented scale, containing more than 10,000,000 human choices and including many canonical studies from domains such as multi-armed bandits, decision-making, memory, supervised learning, Markov decision processes and more (see Fig. 1a for an overview and examples).

We subjected Centaur to a series of rigorous tests and demonstrate that it captures human behaviour at several levels of generalization. First, we show that Centaur predicts behaviour of held-out participants (those who are not part of the training data) better than existing cognitive models in almost every single experiment. We then demonstrate that its ability to capture human behaviour also generalizes to held-out experiments. In this context, we find that Centaur accurately predicts human behaviour under modified cover stories, problem structures and even in entirely new domains. Finally, we show that Centaur's internal representations become more human aligned, even though it was never explicitly trained to capture human neural activity.

Taken together, our results demonstrate that it is possible to discover computational models that capture human behaviour across a wide range of domains. We think that such a predictive model offers many direct opportunities to obtain a better understanding of the human mind 14,15 and we present a case study that demonstrates this potential.

## Model overview

We built Centaur on top of the open-source language model Llama 3.1 70B, a state-of-the-art model pretrained by Meta AI (hereafter, we refer to this model simply as Llama) 11 . Having a large language model as the backbone allowed us to rely on the vast amounts of knowledge that is present in these models. The training process involved fine-tuning on Psych-101 using a parameter-efficient fine-tuning technique known as quantized low-rank adaptation (QLoRA) 16 . QLoRA relies on a frozen four-bit quantized language model as a base model. Although the parameters of the base model are left unchanged, it adds low-rank adapters, which contain only a few additional, trainable parameters (typically represented in a half-precision floating-point format). In our case, we added low-rank adapters of rank r = 8 to all non-embedding layers (that is, all linear layers of the self-attention mechanisms and the feedforward networks), as illustrated in Fig. 1b. With these settings, the newly added parameters amount to 0.15% of the base model's parameters. We then trained the model for one epoch on the entire dataset using a standard cross-entropy loss. We masked out the loss for all tokens that do not correspond to human responses, thereby ensuring that the model focuses on capturing human behaviour and not on completing experimental instructions. The entire training process took approximately five days on an A100 80GB GPU (Methods, 'Fine-tuning procedure').

## Centaur captures human behaviour

We evaluated Centaur on different types of held-out data to demonstrate that it robustly captures human behaviour. In our first analysis, we tested whether it could predict the behaviour of participants who were not part of the training data. For this, we split each transcribed experiment into two parts and used 90% of participants for training and retained 10% for testing. We measured goodness-of-fit to human

## Article

Fig. 2 | Goodness-of-fit on Psych-101. a, Difference in log-likelihood of Centaur and Llama relative to a domain-specific cognitive model for each experiment. A value of zero corresponds to the goodness-of-fit of the domainspecific cognitive model and a value above zero indicates improved goodnessof-fit to human responses. Log-likelihoods are averaged over responses (n = 992,867). Error bars correspond to the standard error of the mean. Centaur outperforms both Llama and a collection of domain-specific cognitive models in almost every experiment (one-sided t-tests: t(1,985,732) = -144.22, P ≤ 0.0001; t(1,985,732) = -127.58, P ≤ 0.0001, respectively). We only included experiments for which we have implemented a domain-specific cognitive model in this graphic and merged different studies using the same paradigm.

<!-- image -->

Extended Data Table 1 contains numerical results for all experiments. b, Model simulations on the horizon task. The plot shows the probability densities over reward and an information bonus parameter for both people and simulated runs of Centaur. c, Model simulations on the two-step task. The plot shows the probability densities over reward and a parameter indicating how model-based learning was for both people and simulated runs of Centaur. d, Model simulations on a social prediction game. The plot shows the probability densities over accuracies of predicting human strategies and strategies of an artificial agent, with matched statistics for both people and simulated runs of Centaur.

choices using negative log-likelihoods averaged across responses (Methods, 'Evaluation metric'). Figure 2a presents the results of this analysis, comparing Centaur with the base model without fine-tuning and a collection of domain-specific models that represent the state-of-the-art in the cognitive-science literature (Extended Data Table 1). Although there was substantial variance in predictability across experiments (Centaur, 0.49; Llama, 0.47), fine-tuning always improved goodness-of-fit. The average difference in log-likelihoods across experiments after fine-tuning was 0.14 (Centaur negative log-likelihood, 0.44; Llama negative log-likelihood, 0.58; one-sided t-test: t(1,985,732) = -144.22, P ≤ 0.0001; Cohen's d, 0.20).

Furthermore, we compared Centaur with the previously mentioned collection of domain-specific cognitive models. These models include, among others, the generalized context model 17 , a prospect theory model 18 and various reinforcement learning models 19,20 (Methods, 'Domain-specific cognitive models'). We observed that Centaur outperforms domain-specific cognitive models in all but one experiment. The average difference in predicting human behaviour to the domain-specific cognitive models was 0.13 (cognitive models, negative log-likelihood, 0.56; one-sided t-test: t(1,985,732) = -127.58, P ≤ 0.0001; Cohen's d, 0.18). Extended Data Figs. 2 and 3 contain more comparisons to models fine-tuned on non-behavioural data and a noise-ceiling analysis.

The previous analyses have focused on predicting human responses conditioned on previously executed behaviour. We may ask whether Centaur can also generate human-like behaviour when simulated in an open-loop fashion (that is, when feeding its own responses back into the model). This setting arguably provides a much stronger test of the model's capabilities and is sometimes also referred to as model falsification 21 . To check whether Centaur survives this test, we ran open-loop simulations in three different experimental paradigms and inspected the distributions of statistics that resulted from these simulations. First, we simulated Centaur on the horizon-task paradigm, a two-armed bandit task used to detect different types of exploration strategies 20 . We found that Centaur (mean = 54.12, s.d. = 2.89) achieved a performance comparable to human participants (mean = 52.78, s.d. = 2.90), which was supported by an equivalence test using the two one-sided t-tests procedure with a ±3-point margin (P = 0.02). Centaur also engaged in a similar level of uncertainty-guided directed exploration (Fig. 2b), a pattern that is notably absent in many contemporary language models 12 .

Fig. 3 | Evaluation in different held-out settings. a, Negative log-likelihoods averaged over responses (n = 9,702) for the two-step task with a modified cover story 23 . b, Negative log-likelihoods averaged over responses (n = 510,154) for a three-armed bandit experiment 25 . c, Negative log-likelihoods averaged over responses (n = 99,204) for an experiment probing logical reasoning 26 with

<!-- image -->

items based on the Law School Admission Test (LSAT). Centaur outperforms both Llama and domain-specific cognitive models when faced with modified cover stories, problem structures and entirely new domains. N/A, not applicable. Error bars show the s.e.m. The image in a is reproduced from ref. 23, Springer Nature Limited. The image in c is reproduced from Wikipedia.org.

We also observed that Centaur does not merely capture the behaviour of the average participant, but rather the distribution over trajectories produced by the entire population. For example, in the two-step task (a well-known paradigm used to tease apart model-free and model-based reinforcement learning 19 ), Centaur, just like human subjects, produced trajectories in which learning is purely model-free, purely model-based and mixtures thereof (as the bimodal distribution in Fig. 2c shows).

Finally, we verified that Centaur fails at predicting non-human behaviour. For this, we considered a study that required participants to predict either human responses or responses of an artificial agent with matched statistics in four canonical economic games 22 . Mirroring the results of the original human study, Centaur accurately predicted human responses (64% accuracy) but struggled to predict artificial responses (35% accuracy; one-sided t-test: t(230) = 20.32, P ≤ 0.0001; Fig. 2d). Taken together, these results demonstrate that Centaur exhibits human-like characteristics across various settings, confirming that it can generate meaningful open-loop behaviour.

## Probing generalization abilities

So far, we have shown that Centaur generalizes to previously unseen participants performing experiments that were part of the training data. A true foundation model of human cognition, however, must also capture behaviour in any arbitrary experiment, even if that experiment was not part of the training data. To probe whether Centaur has this ability, we exposed it to a series of increasingly complex out-of-distribution evaluations.

First, we investigated whether Centaur is robust in the face of changes to the cover story. For this analysis, we relied on data collected in ref. 23, which used the aforementioned two-step task. In addition to the canonical cover story (spaceships travelling to foreign planets in search of treasures), the study introduced a new cover story involving magical carpets. Importantly, Psych-101 includes experiments using the canonical spaceship cover story 24 but no experiments with the magic-carpet cover story. Even so, we found that Centaur captured human behaviour in the magic-carpet experiment of ref. 23 (Fig. 3a). As in our previous analysis, we observed an improvement after fine-tuning, as well as a favourable goodness-of-fit when compared with a domain-specific cognitive model (Centaur negative log-likelihood, 0.51; Llama negative log-likelihood, 0.63; cognitive model negative log-likelihood, 0.61; one-sided t-test comparing Centaur with Llama: t(9,701) = -24.7, P ≤ 0.0001; one-sided t-test comparing Centaur with the domain-specific cognitive model: t(9,701) = -20.7, P ≤ 0.0001; the domain-specific cognitive model used in this analysis was a hybrid model that combined model-based and model-free reinforcement learning) 19 .

In a second out-of-distribution evaluation, we probed whether Centaur is robust to modifications in task structure. To test this, we exposed it to a paradigm known as Maggie's farm 25 . Maggie's farm extends the horizon task paradigm by adding a third option. Psych-101 encompasses several two-armed bandit experiments (including the horizon task) but not Maggie's farm or any other three-armed bandit experiments

Fig. 4 | Human alignment. a, Multidimensional scaling embedding of the ten behavioural metrics in CogBench 33 for different models. b, Pearson correlation coefficients indicating how well human neural activity in the two-step task 37 can be decoded using Centaur's internal representations extracted from different layers. c, Pearson correlation coefficients indicating how well human

<!-- image -->

(it does, however, contain multi-armed bandit experiments with more than three options to choose between). Thus, this analysis provides a test of Centaur's robustness to structural task modifications. We found that Centaur captured human behaviour on Maggie's farm, as shown in Fig. 3b. We again observed a benefit of fine-tuning, as well as a favourable goodness-of-fit compared with a domain-specific cognitive model, which did not generalize well to this setting (Centaur negative log-likelihood, 0.42; Llama negative log-likelihood, 0.62; cognitive model negative log-likelihood, 0.98; one-sided t-test comparing Centaur with Llama: t(510,153) = -204.2, P ≤ 0.0001; one-sided t-test comparing Centaur with the domain-specific cognitive model: t(510,153) = -559.8, P ≤ 0.0001).

Finally, we investigated whether Centaur could capture human behaviour even in entirely new domains. In this context, we considered a study investigating logical reasoning 26 . Although Psych-101 includes probabilistic and causal reasoning problems, we purposefully excluded any studies involving logical reasoning. As in the previous analyses, there was again a positive effect of fine-tuning (Centaur negative log-likelihood, 1.65; Llama negative log-likelihood, 1.92; one-sided t-test: t(198,406) = -50.39, P ≤ 0.0001; Cohen's d, 0.23; Fig. 3c). Note that we did not compare with any domain-specific cognitive model in this setting, because it is unclear how to construct a model that would make any meaningful transfer from training data that does not include any related problems.

We consolidated these results by analysing Centaur on six more out-of-distribution experimental paradigms that were not part of the training data in any shape or form (including moral decision-making 27 , economic games 28 , naturalistic category and reward learning 29 , behavioural propensities 30 and a deep sequential decision task 31 ). Centaur robustly captured human behaviour in all these settings, whereas smaller and non-fine-tuned models did not do so consistently (Extended Data Fig. 4).

As well as analysing human choice data, we also examined whether Centaur could predict human response times. Hick's law 32 indicates that individual response times are a linear function of response entropies. Therefore, we extracted nearly 4,000,000 response times for a subset of experiments in Psych-101 and fitted three linear mixed effects models, each predicting log-transformed response times based on log-transformed response entropies derived from a different computational model. We found that the response entropies derived from Centaur captured a larger proportion of the variance in response times (conditional R 2 , 0.87) than those derived from Llama (conditional R 2 , 0.75, log[BFCentaur, Llama] = 53,773.5) and the cognitive models (conditional R 2 , 0.77, log[BFCentaur, cognitive models] = 14,995.5), thereby highlighting Centaur's ability to predict measures beyond pure choice data.

neural activity in a sentence-reading task 38 can be decoded using Centaur's internal representations extracted from different layers. Control refers to a model that used representations extracted from a randomly initialized transformer model with matched architecture.

To demonstrate that the model does not degrade on problems it was pretrained for, we furthermore verified it on a collection of benchmarks from the machine-learning literature 33,34 . We found that Centaur remains stable in performance-based benchmarks, even improving over the base model in some of them 34 (Extended Data Fig. 5a,b). Finally, in benchmarks that measure human alignment, we observed a shift towards human-like characteristics (Extended Data Fig. 5c). Figure 4a depicts this improved alignment on a low-dimensional embedding derived from ten behavioural metrics in CogBench, a benchmark to test the cognitive abilities of large language models 33 .

## Alignment to human neural activity

Despite being trained to match only human behaviour, we also wondered whether Centaur's internal representations become more aligned with human neural activity. To check whether this is the case, we conducted two analyses in which we predicted human neural activity using the model's internal representations 35,36 . We first conducted a whole-brain analysis in which we predicted functional magnetic resonance imaging (fMRI) measurements of people performing the two-step task 37 . For this, we relied on data collected in a previous study 37 involving 94 participants each making 300 choices. Participants were tested on either the magic-carpet cover story (which we had already used in one of our earlier generalization analyses) or an abstract cover story. Neither of these two cover stories was part of Centaur's training data. We extracted recordings from models' residual stream before each choice and after feedback. We then aggregated human neural activity in each region and regressed the aggregated activity on Centaur's internal representations. This procedure was then repeated separately for each participant and region (Methods, 'Neural alignment'). Figure 4b shows the resulting Pearson correlation coefficients across layers for both Centaur and Llama averaged over measurements (n = 11,374). We found that Centaur's representations consistently outperformed Llama's representations in predicting human neural activity (all pairwise one-sided t-tests, P ≤ 0.001), indicating that fine-tuning a model on large-scale behavioural data aligned its internal representations to human neural activity. It is worth noting that this type of analysis was possible only because of the expressivity of Centaur's representations, and that using representations of a conventional cognitive model led to a substantial drop in performance (dashed line in Fig. 4b). A more fine-grained report of our results is given in Extended Data Fig. 6.

<!-- image -->

Fig. 5 | Model-guided scientific discovery. a, We used Psych-101 and Centaur to guide the development of a cognitive model for a multi-attribute decision-making study 41 . Each panel shows the AIC for the set of models considered at the given stage, starting with the models considered in the original study. b, We asked DeepSeek-R1 to generate an explanation for the human responses and formalized the resulting verbal strategy into a formal

| DeepSeek-R1 explanation                                      | Product A   | Product B   | Response   |
|--------------------------------------------------------------|-------------|-------------|------------|
| The participant employed a two-step decision-making          | 1 0 0 1     | 0 1 1 1     | A          |
| strategy. First, they determined which product had the       | 0 1 1 0     | 1 0 0 0     | B          |
| majority of positive ratings (1s) across all experts. If the | 1 0 0 0     | 0 1 1 0     | A          |
| products were tied in the number of positive ratings, the    | 0 1 1 1     | 1 0 0 1     | B          |
| participant then considered the rating from the highest      | 1 0 0 1     | 0 1 1 1     | A          |
| validity expert to break the tie.                            | 0 1 1 0     | 1 0 0 0     | B          |

computational model. c, We refined this model through scientific regret minimization using Centaur as a reference model. Six data points are shown for which Centaur makes accurate predictions but the DeepSeek-R1-discovered model does not. We then used this information to design a domain-specific cognitive model that is as predictive as Centaur but is still interpretable. The bicycle images in a are reproduced from Flaticon.com.

We expanded these results in a second analysis, for which we relied on a previously collected dataset involving fMRI measurements of people reading simple six-word sentences, such as "That is such a beautiful picture!" 38 . The primary goal of this analysis was to show that neural alignment in unrelated settings remains intact after fine-tuning on cognitive experiments. We focused on a subset of five participants who each passively read 1,000 sentences, spread across 20 experimental runs and two scanning sessions. The presented sentences were extracted from nine corpora and selected to maximize semantic diversity. We closely followed the protocol of the original study and predicted aggregated neural activity across participants in the language network. We repeated this procedure for representations extracted from different layers in both Centaur and Llama. Predictability peaked at around layer 20, as shown in Fig. 4c. This peak is consistent with the hypothesis that the intermediate layers of such models contain the most information. We performed an inverse-weighted meta-analysis 39 on the difference in correlations between Centaur and Llama, and this indicated that there was a significant benefit of fine-tuning when pooling across layers (β = 0.007, 95% confidence interval [0.0002, 0.013], P = 0.045). Although this effect was consistent across layers, it was not statistically significant for any individual layer.

## Model-guided scientific discovery

Psych-101 and Centaur both constitute valuable tools for scientific discovery. In the following section, we present an example of how each of them can be used to improve our understanding of human decision-making. The individual steps of this process are illustrated in Fig. 5.

Psych-101 contains human behavioural data in a natural-language format, which means it can be readily processed and analysed by a language-based reasoning model such as DeepSeek-R1 (ref. 40). To demonstrate this use case, we asked DeepSeek-R1 to generate an explanation of participants' behaviour in a multi-attribute decision-making experiment 41 . In this paradigm, participants are given two different options that are each characterized by various features (in our case, four expert ratings for two products) and they must then decide which of the two options they prefer (Fig. 5a). The model produced several explanations, one of which caught our attention: "The participant employed a two-step decision-making strategy. First, they determined which product had the majority of positive ratings (1 s) across all experts. If the products were tied in the number of positive ratings, the participant then considered the rating from the highest validity expert to break the tie." This strategy combines two well-known heuristic decision-making strategies that, as far as we know, have not been considered in this combination before. We then took this verbal strategy, implemented it as a formal computational model and found that it explained human response behaviour more accurately than the three strategies considered in the original study (a weighted-additive strategy, equal weighting and take-the-best heuristic; Fig. 5b).

However, the DeepSeek-R1-discovered model Akaike information criterion (AIC; 181.7) still fell short of the goodness-of-fit of Centaur (AIC, 72.5), indicating that there is still room for improvement. We therefore used a method known as scientific regret minimization, which uses a black-box predictive model as a reference to identify responses that are in principle predictable but are not captured by a given model 42 . Typically, scientific regret minimization requires the collection of a large-scale experiment-specific dataset to train this predictive model. Centaur, however, can be used out-of-the-box and without the need to collect any domain-specific data, thereby circumventing this step and broadening the scope of scientific regret minimization considerably (indeed, the multi-attribute decision-making data set under consideration contained fewer than 100 participants, placing it far out of reach for conventional scientific regret minimization). When inspecting the responses that were well predicted by Centaur but not by the DeepSeek-R1-discovered model, we observed that they all involved

## Article

problems in which participants chose the option with fewer positive ratings overall but which was rated positively by a higher-validity expert (see Fig. 5c for an illustration of these problems and Methods, 'Model-guided scientific discovery' for further details). This pattern indicates that the switch between the two heuristics is probably not as strict as initially suggested by the DeepSeek-R1-discovered strategy. To capture this, we replaced the either-or rule with a weighted average of both heuristics. We found that the model that resulted from this process matched Centaur in terms of its goodness-of-fit (AIC, 71.7) but was still interpretable. We entered the resulting AIC values of all the models in a group-level model-selection procedure 43 and estimated the protected exceedance probability, which is defined as the probability that a particular model has a higher frequency within a group than all the other candidate models. The protected exceedance probability of the model that resulted from scientific regret minimization was P = 0.83. Notably, the result of this model comparison stands in contrast to the one that was conducted with the original set of models and indicates that people rely on a combination of heuristics when making decisions, as opposed to following a weightedadditive strategy 44 .

## Discussion

In this paper we have introduced Centaur, a foundation model of human cognition that was obtained by fine-tuning a state-of-the-art language model on Psych-101, which is a large-scale dataset of human behaviour. This approach allowed us to leverage the vast knowledge embedded in large language models and also align them with human behaviour 13 . Centaur successfully captured human behaviour and passed a wide range of out-of-distribution checks. It generalized not only to unseen participants, but also to different cover stories, structural variations and entirely new domains. In addition to analysing the model on a behavioural level, we also conducted a series of analyses on its internal representations, in which we found increased alignment with human neural activity.

We also conducted a case study demonstrating how both Psych-101 and Centaur can be used for guiding the development of predictive, yet interpretable, cognitive models. The individual steps of our procedure are generic, so it could serve as a blueprint for model-guided scientific discovery in other experimental paradigms in the future. Looking beyond this example, Centaur finds many more applications in the context of automated cognitive science 45,46 . It may, for instance, be used for in silico prototyping of experimental studies 47 . In this context, one could use the model to figure out which designs lead to the largest effect sizes, how to design a study to reduce the number of required participants or to estimate the power of an effect.

The present paper takes initial steps in leveraging Centaur to gain deeper insights into human cognition, and it also opens up exciting new avenues for future exploration. First, one could further probe Centaur's internal representations to understand how it represents knowledge and processes information. The resulting insights could, in turn, be used to generate hypotheses about knowledge representation and information processing in humans that could be validated in future experimental studies. We believe that tools such as sparse auto-encoders 48 and attention map visualization 49 provide promising avenues towards accomplishing this goal, and we hope to explore them in future studies.

Furthermore, it might also be possible to train models with different architectures from scratch using the dataset that we created in the process of this paper. Doing so would enable us to investigate the neural architecture of human cognition at a scale that could not have been done before. We might, for example, ask questions such as whether human information processing is better described by attention-based architectures 50 or by architectures with a vector-based memory, or how much we can improve by incorporating theories from the neuroscience literature 51 . We expect an eventual outcome of such an approach to contain both domain-specific and domain-general modules, thereby allowing us to investigate the interplay between the two.

As far as we know, Psych-101 is already the broadest and largest dataset of human behaviour available, and we view its development as an ongoing process and plan to develop it further. The focus in its current state is largely on learning and decision-making, but we intend to eventually include more domains, such as psycholinguistics, social psychology and economic games. Experiments with information about individual differences are another source of neglected data in the current iteration of Psych-101. Ideally, we want to include all types of relevant information about subjects (including age, personality traits or socioeconomic status) in the prompt, such that a model trained on these data can capture individual differences. Experiments from developmental psychology or computational psychiatry provide an ideal source for this purpose. Finally, although we have already included some cross-cultural and meta-studies 52-55 , the current iteration still has a strong bias towards a Western, educated, industrialized, rich and democratic (WEIRD) population 56 .

Eventually, we hope to provide any psychological data in a standardized format that facilitates benchmarking, thereby complementing existing efforts from the neuroscience community 57,58 . Although the natural-language format (together with quite a bit of reverse-engineering) used in this work allows us to express a vast range of experimental paradigms, it introduces a selection bias against experiments that cannot be expressed in natural language. The long-term objective should therefore be to move towards a multimodal data format 59 .

## Conclusion

When the idea of a unified model of cognition was first proposed, researchers expressed concern that established areas of cognitive science might react negatively to such a model. In particular, they feared that the approach might be seen as unfamiliar or incompatible with existing theories, just like an "intruder with improper pheromones" 60 . This could lead to an "attack of the killer bees", in which researchers in more-conventional fields would fiercely critique or reject the new model to defend their established approaches. To mitigate these concerns, the concept of a cognitive decathlon was proposed: a rigorous evaluation framework in which competing models of cognition are tested across ten experiments and judged on their cumulative performance in them. In the current work, we applied Centaur to the equivalent of 16 such cognitive decathlons, in which it was tested against numerous established models and consistently won every competition. This outcome indicates that the data-driven discovery of domain-general models of cognition is a promising research direction. The next step for future research should be to translate this domain-general computational model into a unified theory of human cognition 2 .

## Online content

Any methods, additional references, Nature Portfolio reporting summaries, source data, extended data, supplementary information, acknowledgements, peer review information; details of author contributions and competing interests; and statements of data and code availability are available at https://doi.org/10.1038/s41586-025-09215-4.

1. Anderson, J. The Architecture of Cognition (Harvard Univ. Press, 1983).
2. Newell, A. Unified Theories of Cognition (Harvard Univ. Press, 1990).
3. Lake, B. M., Ullman, T. D., Tenenbaum, J. B. &amp; Gershman, S. J. Building machines that learn and think like people. Behav. Brain Sci. 40, e253 (2017).
4. Lake, B. M., Salakhutdinov, R. &amp; Tenenbaum, J. B. Human-level concept learning through probabilistic program induction. Science 350, 1332-1338 (2015).
5. Goddu, M. K. &amp; Gopnik, A. The development of human causal learning and reasoning. Nat. Rev. Psychol. https://doi.org/10.1038/s44159-024-00300-5 (2024).

6. Chu, J. &amp; Schulz, L. E. Play, curiosity, and cognition. Annu. Rev. Dev. Psychol. 2, 317-343 (2020).
7. Silver, D. et al. Mastering the game of Go without human knowledge. Nature 550, 354-359 (2017).
8. Kahneman, D. &amp; Tversky, A. in Handbook of the Fundamentals of Financial Decision Making (eds MacLean, L. C. &amp; Ziemba, W. T.) 99-127 (World Scientific, 2013).
9. Riveland, R. &amp; Pouget, A. Natural language instructions induce compositional generalization in networks of neurons. Nat. Neurosci. 27, 988-999 (2024).
10. Bommasani, R. et al. On the opportunities and risks of foundation models. Preprint at https://arxiv.org/abs/2108.07258 (2021).
11. Grattafiori, A. et al. The Llama 3 herd of models. Preprint at https://arxiv.org/abs/2407.21783 (2024).
12. Binz, M. &amp; Schulz, E. Using cognitive psychology to understand GPT-3. Proc. Natl Acad. Sci. USA 120, e2218523120 (2023).
13. Binz, M. &amp; Schulz, E. Turning large language models into cognitive models. In Proc. 12th International Conference on Learning Representations (ICLR, 2024).
14. Hofman, J. M. et al. Integrating explanation and prediction in computational social science. Nature 595, 181-188 (2021).
15. Rocca, R. &amp; Yarkoni, T. Putting psychology to the test: rethinking model evaluation through benchmarking and prediction. Adv. Methods Pract. Psychol. Sci. https://doi.org/ 10.1177/25152459211026864 (2021).
16. Dettmers, T., Pagnoni, A., Holtzman, A. &amp; Zettlemoyer, L. QLORA: efficient finetuning of quantized LLMs. In Proc. Advances in Neural Information Processing Systems 36 (eds Oh, A. et al.) (NeurIPS, 2023).
17. Nosofsky, R. M. in Formal Approaches in Categorization (eds Pothos, E. M. &amp; Wills, A. J.) 18-39 (Cambridge Univ. Press, 2011).
18. Peterson, J. C., Bourgin, D. D., Agrawal, M., Reichman, D. &amp; Griffiths, T. L. Using large-scale experiments and machine learning to discover theories of human decision-making. Science 372, 1209-1214 (2021).
19. Daw, N. D., Gershman, S. J., Seymour, B., Dayan, P. &amp; Dolan, R. J. Model-based influences on humans' choices and striatal prediction errors. Neuron 69, 1204-1215 (2011).
20. Wilson, R. C., Geana, A., White, J. M., Ludvig, E. A. &amp; Cohen, J. D. Humans use directed and random exploration to solve the explore-exploit dilemma. J. Exp. Psychol. Gen. 143, 2074-2081 (2014).
21. Palminteri, S., Wyart, V. &amp; Koechlin, E. The importance of falsification in computational cognitive modeling. Trends Cogn. Sci. 21, 425-433 (2017).
22. van Baar, J. M., Nassar, M. R., Deng, W. &amp; FeldmanHall, O. Latent motives guide structure learning during adaptive social choice. Nat. Hum. Behav. 6, 404-414 (2022).
23. Feher da Silva, C. &amp; Hare, T. A. Humans primarily use model-based inference in the two-stage task. Nat. Hum. Behav. 4, 1053-1066 (2020).
24. Kool, W., Cushman, F. A. &amp; Gershman, S. J. When does model-based control pay off? PLoS Comput. Biol. 12, e1005090 (2016).
25. Dubois, M. &amp; Hauser, T. U. Value-free random exploration is linked to impulsivity. Nat. Commun. 13, 4542 (2022).
26. Jansen, R. A., Rafferty, A. N. &amp; Griffiths, T. L. A rational model of the Dunning-Kruger effect supports insensitivity to evidence in low performers. Nat. Hum. Behav. 5, 756-763 (2021).
27. Awad, E. et al. The Moral Machine experiment. Nature 563, 59-64 (2018).
28. Akata, E. et al. Playing repeated games with large language models. Nat. Hum. Behav. https://doi.org/10.1038/s41562-025-02172-y (2025).
29. Demircan, C. et al. Evaluating alignment between humans and neural network representations in image-based learning tasks. In Proc. Advances in Neural Information Processing Systems 37 (eds Globerson, A. et al.) (NeurIPS, 2024).
30. Singh, M., Richie, R. &amp; Bhatia, S. Representing and predicting everyday behavior. Comput. Brain Behav. 5, 1-21 (2022).
31. Xu, H. A., Modirshanechi, A., Lehmann, M. P., Gerstner, W. &amp; Herzog, M. H. Novelty is not surprise: human exploratory and adaptive behavior in sequential decision-making. PLoS Comput. Biol. 17, e1009070 (2021).
32. Hick, W. E. On the rate of gain of information. Q. J. Exp. Psychol. 4, 11-26 (1952).
33. Coda-Forno, J., Binz, M., Wang, J. X. &amp; Schulz, E. CogBench: a large language model walks into a psychology lab. Proc. Mach. Learn. Res. 235, 9076-9108 (2024).
34. Kipnis, A., Voudouris, K., Schulze Buschoff, L. M. &amp; Schulz, E. metabench - a sparse benchmark of reasoning and knowledge in large language models. In Proc. 13th International Conference on Learning Representations (ICLR, 2025).
35. Yamins, D. L. K. et al. Performance-optimized hierarchical models predict neural responses in higher visual cortex. Proc. Natl Acad. Sci. USA 111, 8619-8624 (2014).
36. Schrimpf, M. et al. The neural architecture of language: integrative modeling converges on predictive processing. Proc. Natl Acad. Sci. USA 118, e2105646118 (2021).
37. Feher da Silva, C., Lombardi, G., Edelson, M. &amp; Hare, T. A. Rethinking model-based and model-free influences on mental effort and striatal prediction errors. Nat. Hum. Behav. 7, 956-969 (2023).
38. Tuckute, G. et al. Driving and suppressing the human language network using large language models. Nat. Hum. Behav. 8, 544-561 (2024).
39. Cochran, W. G. The combination of estimates from different experiments. Biometrics 10, 101-129 (1954).
40. DeepSeek-AI et al. DeepSeek-R1: incentivizing reasoning capability in LLMs via reinforcement learning. Preprint at https://arxiv.org/abs/2501.12948 (2025).
41. Hilbig, B. E. &amp; Moshagen, M. Generalized outcome-based strategy classification: comparing deterministic and probabilistic choice models. Psychon. Bull. Rev. 21, 1431-1443 (2014).
42. Agrawal, M., Peterson, J. C. &amp; Griffiths, T. L. Scaling up psychology via scientific regret minimization. Proc. Natl Acad. Sci. USA 117, 8825-8835 (2020).
43. Rigoux, L., Stephan, K. E., Friston, K. J. &amp; Daunizeau, J. Bayesian model selection for group studies - revisited. Neuroimage https://doi.org/10.1016/j.neuroimage.2013.08.065 (2014).
44. Binz, M., Gershman, S. J., Schulz, E. &amp; Endres, D. Heuristics from bounded meta-learned inference. Psychol. Rev. 129, 1042-1077 (2022).
45. Musslick, S. et al. Automating the practice of science: opportunities, challenges, and implications. Proc. Natl. Acad. Sci. USA 122, e2401238121 (2025).
46. Rmus, M., Jagadish, A. K., Mathony, M., Ludwig, T. &amp; Schulz, E. Generating computational cognitive models using large language models. Preprint at https://arxiv.org/abs/2502.00879 (2025).
47. Dillion, D., Tandon, N., Gu, Y. &amp; Gray, K. Can AI language models replace human participants? Trends Cogn. Sci. 27, 597-600 (2023).
48. Huben, R., Cunningham, H., Smith, L. R., Ewart, A. &amp; Sharkey, L. Sparse autoencoders find highly interpretable features in language models. In Proc. 12th International Conference on Learning Representations (ICLR, 2024).
49. Chefer, H., Gur, S. &amp; Wolf, L. Transformer interpretability beyond attention visualization. In Proc. 2021 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) 782-791 (IEEE, 2021).
50. Vaswani, A. et al. Attention is all you need. In Proc. Advances in Neural Information Processing Systems 30 (eds Guyon, I. et al.) (NeurIPS, 2017).
51. Zador, A. et al. Catalyzing next-generation artificial intelligence through NeuroAI. Nat. Commun. 14, 1597 (2023).
52. Ruggeri, K. et al. The globalizability of temporal discounting. Nat. Hum. Behav. 6, 1386-1397 (2022).
53. Wulff, D. U., Mergenthaler-Canseco, M. &amp; Hertwig, R. A meta-analytic review of two modes of learning and the description-experience gap. Psychol. Bull. 144, 140-176 (2018).
54. Frey, R., Pedroni, A., Mata, R., Rieskamp, J. &amp; Hertwig, R. Risk preference shares the psychometric structure of major psychological traits. Sci. Adv. 3, e1701381 (2017).
55. Enkavi, A. Z. et al. Large-scale analysis of test-retest reliabilities of self-regulation measures. Proc. Natl Acad. Sci. USA 116, 5472-5477 (2019).

56. Henrich, J., Heine, S. J. &amp; Norenzayan, A. Most people are not WEIRD. Nature 466, 29 (2010).

57. Schrimpf, M. et al. Integrative benchmarking to advance neurally mechanistic models of human intelligence. Neuron 108, 413-423 (2020).
58. Poldrack, R. A. et al. The past, present, and future of the brain imaging data structure (BIDS). Imaging Neurosci. 2, 1-19 (2024).
59. Schulze Buschoff, L. M., Akata, E., Bethge, M. &amp; Schulz, E. Visual cognition in multimodal large language models. Nat. Mach. Intell. https://doi.org/10.1038/s42256-024-00963-y (2025).
60. Vere, S. A. A cognitive process shell. Behav. Brain Sci. 15, 460-461 (1992).

Publisher's note Springer Nature remains neutral with regard to jurisdictional claims in published maps and institutional affiliations.

<!-- image -->

Open Access This article is licensed under a Creative Commons Attribution 4.0 International License, which permits use, sharing, adaptation, distribution and reproduction in any medium or format, as long as you give appropriate

credit to the original author(s) and the source, provide a link to the Creative Commons licence, and indicate if changes were made. The images or other third party material in this article are included in the article's Creative Commons licence, unless indicated otherwise in a credit line to the material. If material is not included in the article's Creative Commons licence and your intended use is not permitted by statutory regulation or exceeds the permitted use, you will need to obtain permission directly from the copyright holder. To view a copy of this licence, visit http://creativecommons.org/licenses/by/4.0/.

- © The Author(s) 2025

## Article

## Methods

## Data collection

We constructed Psych-101 by transcribing data from 160 psychological experiments into natural language. Each prompt was designed to include the entire trial-by-trial history of a complete session from a single participant. The experiments included were selected using the following criteria: publicly available data on a trial-by-trial level; the possibility of transcription into text without a significant loss of information; and coverage of a broad spectrum of domains. The transcription of each experiment was done manually by the authors. Approval from the institutional review board was obtained by the individual studies as required. We designed our natural-language prompts using the following principles: instructions should follow the original study as closely as possible; simplifications were made where appropriate; and a maximum prompt length of roughly 32,768 tokens was used. Full information about all the experiments included is provided in the Supplementary Information, Example prompts.

## Fine-tuning procedure

Llama 3.1 70B was the base model for our fine-tuning procedure. We used a parameter-efficient fine-tuning technique known as QLoRA 16 , which adds so-called low-rank adapters to each layer of a four-bit quantized base model. The base model was kept fixed during fine-tuning and only the parameters of the low-rank adapters were adjusted. We added low-rank adapters of rank r = 8 to all linear layers of the self-attention mechanisms and the feedforward networks. Each low-rank adapter modifies the forward pass as follows:

<!-- formula-not-decoded -->

where XW is the (quantized) linear transformation of the base model and XL1L2 is the low-rank adapter component, with X being the input to the layer with dimensionality h and Y being the output of the layer with dimensionality o. The hyperparameter α controls the trade-off between the two. R is the set of real numbers. Low-rank adapter computations were performed in half-precision floating-point format. For further details on this technique, please see the original work 16 .

We fine-tuned the model for one epoch on the entire dataset using a standard cross-entropy loss (we experimented with prolonged training but found that this led to overfitting). We only back-propagated the loss at human responses and masked out the loss for all other tokens. The effective batch size was set to 32, the learning rate to 0.00005 and the weight decay to 0.01. We used an 8-bit AdamW optimizer 61 with a linearly increasing warm up over the first 100 gradient steps. The fine-tuning procedure was implemented using the unsloth library (https://unsloth.ai/).

We have also trained a smaller version of Centaur, called Minitaur, that uses Llama 3.1 8B as the base model following the same recipe. Minitaur captures human behaviour close to its training distribution but generalizes less robustly than the larger model to out-of-distribution experiments (Extended Data Fig. 7). Nevertheless, we believe that Minitaur is useful for prototyping because it does not require access to any specific hardware (it runs, for instance, on the free GPU instances in Google Colab).

## Evaluation metric

We used (negative) log-likelihoods averaged over responses as our evaluation metric. For experiments with multi-token responses, we summed log-likelihoods within a response and averaged across responses. We used one-sided t-tests whenever we tested whether Centaur outperformed a competing model in predicting human behaviour, because our hypotheses were directional and based on the prior expectation that Centaur would perform better. Because the number of observations in our analyses is generally large, reported significant effects survive after correcting for multiple comparisons where appropriate.

## Domain-specific cognitive models

We selected as our baseline models 14 cognitive and statistical models that together cover most of the experiments in Psych-101. Further details regarding the included models and their specifications are provided in Supplementary Information, Modelling details.

For our main analysis, we were interested in predicting the behaviour of held-out participants. Therefore, we fitted a joint set of parameters for all participants in the training data and evaluated how well a model with these parameters predicts the responses of held-out participants. Mirroring the evaluation metric for the language-based models, we evaluated goodness-of-fit using (negative) log-likelihoods averaged over responses.

For the out-of-distribution evaluations, we fitted model parameters using the most similar experiment in the training set, and then we evaluated how well a model with the resulting parameters predicts human responses in the unseen setting. The most similar experiment for the magic-carpet version of the two-step task was a two-step task experiment with the default spaceship cover story. The most similar experiment for Maggie's farm was the horizon task. We included no baseline model for the logical reasoning task, because none of the experiments in the training data were similar to it.

## Neural alignment

The neural alignment analysis on the two-step task was conducted using data collected in a previous study 37 . We used a regularized linear regression model to predict fMRI data from internal representations of Centaur and Llama (a separate model was used for each participant and region). We fitted each of these models on data from two scanning blocks and evaluated them on data from the third. The regularization strength was selected using a nested cross-validation procedure. For each run, we split the beta maps into cortical and subcortical regions of interest (ROI) using the Schaefer 2018 atlas with 100 ROIs 62 . We averaged the betas within each ROI, reducing the number of betas from the number of voxels to the number of ROIs. All cortical and subcortical ROIs from the atlas were evaluated. Reported Pearson correlation coefficients correspond to the average across all ROIs.

Internal representations were extracted from the models' residual stream and transformed using a principal component analysis. We set the number of retained components such that they explained 95% of the variance.

The fMRI data were preprocessed using fMRIPrep 24.0 (ref. 63). We used the default settings of fMRIPrep, and all the scans were aligned to the MNI152NLin2009cAsym atlas 64 . To extract effect estimates for each subtrial of the task (such as the second step of the fifth trial, or the feedback of the tenth trial), we built separate general linear models (GLMs). Each GLM included the subtrial of interest as a separate regressor, whose z-scored beta estimates were used for the alignment analysis. This part of the data was not modelled using other regressors. Furthermore, we included different regressors capturing all the first steps, all the second steps and all the feedback steps. Finally, we used six rotation and translation estimates as well as framewise displacement as noise regressors. The haemodynamic response was modelled using the spm 65 model. A high-pass filter of 0.01 Hz and a Gaussian kernel with 6 mm full-width at half-maximum was applied. The GLMs were built using nilearn 66 .

The neural alignment analysis on the sentence-reading task was conducted using publicly available code from the original study 38 . No other changes were made apart from replacing GPT2-XL with Centaur and Llama. Please see the original study 38 for further details.

## Model-guided scientific discovery

In our model-guided scientific discovery analysis, we focused on participants in the test set to avoid any potential contamination issues. We fitted parameters of all cognitive models individually for each participant using a maximum-likelihood estimation. Models were compared with each other using the AIC. The three models from the original study were implemented by the following equations:

<!-- formula-not-decoded -->

,

where xA and xB are vectors containing four expert ratings (either 0 or 1) and β is a free parameter controlling the noise level.

We prompted DeepSeek-R1 (in the Distill-Llama-70B variant) to generate explanations of human decision-making; the corresponding prompt is provided in Supplementary Information, Model-guided scientific discovery. We then formalized the explanation shown in Fig. 5b into the following computational model:

<!-- formula-not-decoded -->

For the scientific regret minimization pipeline, we computed the difference in log-likelihoods between Centaur and the DeepSeekR1-discovered model. We visualized and inspected the ten data points with the greatest difference. This process resulted in the following computational model:

<!-- formula-not-decoded -->

where σ is a free parameter constrained between 0 and 1 that controls the trade-off between the two strategies.

## Reporting summary

Further information on research design is available in the Nature Portfolio Reporting Summary linked to this article.

## Data availability

Psych-101 is publicly available on the Huggingface platform at https:// huggingface.co/datasets/marcelbinz/Psych-101. The test set is accessible under a CC-BY-ND-4.0 licence through a gated repository at https:// huggingface.co/datasets/marcelbinz/Psych-101-test.

## Code availability

Centaur is available on the Huggingface platform at https://huggingface. co/marcelbinz/Llama-3.1-Centaur-70B-adapter. The extra code needed to reproduce our results is available at https://github.com/marcelbinz/ Llama-3.1-Centaur-70B.

61. Loshchilov, I. &amp; Hutter, F. Decoupled weight decay regularization. In Proc. 7th International Conference on Learning Representations (ICLR, 2019).
62. Schaefer, A. et al. Local-global parcellation of the human cerebral cortex from intrinsic functional connectivity MRI. Cereb. Cortex 28, 3095-3114 (2018).
63. Esteban, O. et al. fMRIPrep: a robust preprocessing pipeline for functional MRI. Nat. Methods 16, 111-116 (2019).
64. Fonov, V. S., Evans, A. C., McKinstry, R. C., Almli, C. R. &amp; Collins, D. L. Unbiased nonlinear average age-appropriate brain templates from birth to adulthood. Neuroimage 47, S102 (2009).
65. Friston, K. J., Ashburner, J. T., Kiebel, S. J., Nichols, T. E. &amp; Penny, W. D. (eds) Statistical Parametric Mapping: The Analysis of Functional Brain Images (Elsevier, 2011).
66. Gau, R. nilearn. GitHub https://github.com/nilearn/nilearn (2024).
67. Yax, N., Oudeyer, P.-Y. &amp; Palminteri, S. Assessing contamination in large language models: introducing the LogProber method. Preprint at https://arxiv.org/abs/2408.14352 (2024).
68. Warner, B. et al. Smarter, better, faster, longer: a modern bidirectional encoder for fast, memory efficient, and long context finetuning and inference. Preprint at https://arxiv.org/ abs/2412.13663 (2024).
69. Wang, Z. et al. HelpSteer2-Preference: complementing ratings with preferences. In Proc. 13th International Conference on Learning Representations (ICLR, 2025).
70. Teknium, R., Quesnelle, J. &amp; Guang, C. Hermes 3 technical report. Preprint at https://arxiv. org/abs/2408.11857 (2024).
71. Lin, S., Hilton, J. &amp; Evans, O. TruthfulQA: measuring how models mimic human falsehoods. In Proc. 60th Annual Meeting of the Association for Computational Linguistics (eds Muresan, S. et al.) 3214-3252 (Association for Computational Linguistics, 2022).

Acknowledgements Funding was from the Max Planck Society (to P.D.), the Humboldt Foundation (to P.D.), the Volkswagen Foundation (to E.S.) and the NOMIS Foundation (to T.L.G.). P.D. is a member of the Machine Learning Cluster of Excellence (EXC number 2064/1, project number 39072764) and of the Else Kröner Medical Scientist Kolleg 'ClinbrAIn: Artificial Intelligence for Clinical Brain Research'. This work was supported by the Helmholtz Association's Initiative and Networking Fund on the HAICORE@FZJ partition. S.K. is supported by a Google PhD Fellowship. No researchers at Google DeepMind used Llama for this research. We thank N. Scharfenberg for contributions to the data collection.

Author contributions Project lead: M. Binz. Data curation: E.A., F.B., M. Binz, F.C., J.C.-F., C.D., M.K.E., N.É., S.H., A.K.J., L.J.-A., A.K., S.K., T.L., S.S.N., J.C.P., E.M.R., T.S., J.A.S., L.M.S.B., N.S., X.S., M.T., V.T., K.W., S.W., D.U.W. and H.X. Data quality control: E.A., M. Binz, J.C.-F., C.D., S.H. and L.M.S.B. Model training: M. Binz and V.U. Model evaluation: M. Binz, J.C.-F., A.K., M.T. and K.V. Domain-specific models: M. Binz, J.C.-F., C.D., A.K.J., M. Mathony, A.M., M.R. and T.L. Neural analyses: M. Binz, C.D., S.K., M. Mattar and E.M.R. First draft: M. Binz and E.S. Conception and design: M. Binz, M. Bethge, P.D., T.L.G., M. Mattar, F.J.T., R.W. and E.S. Review and editing: M. Binz, E.A., M. Bethge, F.B., F.C., J.C.-F., P.D., C.D., M.K.E., N.É., T.L.G., S.H., A.K.J., L.J.-A., A.K., S.K., T.L., M. Mathony, M. Mattar, A.M., S.S.N., J.C.P., M.R., E.M.R., T.S., J.A.S., L.M.S.B., N.S., X.S., M.T., F.J.T., V.T., V.U., K.V., R.W., K.W., S.W., D.U.W., H.X. and E.S.

Funding Open access funding provided by Helmholtz Zentrum München - Deutsches Forschungszentrum für Gesundheit und Umwelt (GmbH).

Competing interests F.J.T. consults for Immunai, CytoReason, Cellarity, BioTuring and Genbio. AI, and has an ownership interest in Dermagnostix and Cellarity. The remaining authors declare no competing interests.

## Additional information

Supplementary information The online version contains supplementary material available at https://doi.org/10.1038/s41586-025-09215-4.

Correspondence and requests for materials should be addressed to Marcel Binz. Peer review information Nature thanks Russell Poldrack, Giosue Baggio and the other, anonymous, reviewer(s) for their contribution to the peer review of this work. Reprints and permissions information is available at http://www.nature.com/reprints.

<!-- image -->

Extended Data Fig. 1 | Psych-101. a, Proportion of domains included in Psych-101. b, Word cloud of experimental paradigms included in Psych-101. c, We performed a data contamination analysis using the LogProber method 67 for every experimental paradigm in Psych-101. LogProber fits a two-parameter exponential model to the cumulative log-likelihood of each sequence being checked for contamination. High acceleration (log B) suggests that a prompt is memorized from the pretraining data. Following the results presented in the original work 67 , we set a threshold for possible contamination to log B ≥ 1.

This analysis indicated no evidence of contamination. d, Two-dimensional embedding of the experiments used in this paper. To obtain this embedding, we took the corresponding natural language prompts up to the point of the first human choice, extracted a vector-based representation for them using ModernBERT 68 , and finally projected these representations onto two dimensions using multidimensional scaling. Purple dots correspond to experiments from Psych-101, whereas the colored dots correspond to the indicated evaluation experiment.

<!-- image -->

Extended Data Fig. 2 | Negative log-likelihoods of Centaur and alternative Llama variants on Psych-101. To rule out the hypothesis that finetuning on any data aligns a model with human behavior, we compared Centaur to various Llama variants finetuned for other purposes (i.e. non-cognitive tasks). Nemotron 69 is finetuned for instruction-following. Hermes 70 is finetuned for various purposes, including agentic capabilities, roleplaying, reasoning, multiturn conversation, and long context coherence. Reflection is finetuned for reasoning. None of the Llama variants captures human behavior better than the base model, ruling out the hypothesis that finetuning generally leads to models that are better at predicting human behavior. Error bars correspond to the standard error of the mean, taken over responses.

## Article

Extended Data Fig. 3 | Noise ceiling analysis. We conducted a noise ceiling analysis to better understand the capabilities of Centaur. It is not straightforward to estimate the noise ceiling for experiments with sequential dependencies, which includes the majority of Psych-101. Hence, we focused on two experiments for which such an analysis is possible: a, the choices13k data set 18 and b, an intertemporal choice experiment 52 . In both cases, we found that Centaur substantially exceeds the estimated noise ceiling. This is possible

<!-- image -->

because Centaur can pick up on context-dependent patterns that are not captured by standard noise ceiling analyses. Therefore, we have performed an additional analysis testing how well Centaur can predict human responses if we prompt it to predict each response independently. We use the suffix "ind." to indicate this way of prompting the model. Centaur still matches the performance of domain-specific cognitive models when context-independent prompts are used, amounting to roughly half of the estimated noise ceiling.

Extended Data Fig. 4 | Further out-of-distribution evaluations. Each subplot shows negative log-likelihoods for a different experiment. None of these paradigms were included in Psych-101, hence they provide a stress test for a model's generalization capabilities. Centaur robustly captured human behavior in all of these settings, while smaller and non-finetuned models did not do so consistently. Error bars correspond to the standard error of the mean, taken over responses. We state one-sided t-tests comparing the negative log-likelihoods of Centaur to those of Llama in brackets.

<!-- image -->

a, Negative log-likelihoods on moral decision-making 27 (t(181388) = -103.54, p ≤ 0.0001). b, Negative log-likelihoods on economic games 1 (t(7798) = -11.69, p ≤ 0.0001). c, Negative log-likelihoods on naturalistic category learning 1 (t(21838) = -14.05, p ≤ 0.0001). d, Negative log-likelihoods on behavioral propensities 30 (t(156230) = -11.06, p ≤ 0.0001). e, Negative log-likelihoods on naturalistic reward learning 1 (t(9838) = -12.63, p ≤ 0.0001). f, Negative loglikelihoods on a deep sequential decision task 31 (t(6092) = -1.06, p = 0.144).

## Article

Extended Data Fig. 5 | metabench and CogBench results. a, Results for metabench 34 , a sparse benchmark containing several canonical benchmarks from the machine learning literature. We find that Centaur maintains the level of performance of Llama, indicating that finetuning on human behavior did not lead to deterioration in other tasks (ARC: z = -0.126, p = 0.9, GSM8K: z = -0.529, p = 0.597, HellaSwag: z = 0.0, p = 1.0, MMLU: z = 0.0, p = 1.0, Winogrande: z = -0.556, p = 0.578). Performance on TruthfulQA 71 - which measures how models mimic human falsehoods - even improved significantly with finetuning (z = 2.312, p = 0.021; all z-test were two-sided). b, Performance-based metrics from CogBench 33 , a benchmark that includes ten behavioral metrics derived from seven cognitive psychology experiments. We find that - relative to Llama - Centaur's performance improves in all experiments (Probabilistic reasoning:

<!-- image -->

z = 6.371, p ≤ 0.0001, Horizon task: z = 22.176, p ≤ 0.0001, Restless bandit: z = 7.317, p ≤ 0.0001, Instrumental learning: z = 0.126, p = 0.45, Two-step task: z = 1.458, p = 0.072, Balloon analog risk task: z = 1.496, p = 0.067; all z-test were one-sided). c, Behavioral metrics from CogBench. We observe that Centaur becomes more similar to human subjects in all ten behavioral metrics (Prior weighting: z = 2.176, p = 0.015, Likelihood weighting: z = 1.131, p = 0.129, Directed exploration: z = 0.525, p = 0.3, Random exploration: z = 2.014, p = 0.022, Meta-cognition: z = 2.206, p = 0.014, Learning rate: z = 0.477, p = 0.317, Optimism bias: z = 0.78, p = 0.218, Model-basedness: z = 9.608, p ≤ 0.0001, Temporal discounting: z = 2.594, p = 0.005, Risk taking: z = 1.612, p = 0.053; all z-test were one-sided).

<!-- image -->

## Extended Data Fig. 6 | Finegrained neural alignment results in the two-step

task. a, Pearson correlation coefficients between the predicted activity from Centaur's representations and the BOLD data shown on a surface brain (image created with nilearn 66 ). Centaur achieves the most accurate predictions in the left motor cortex. As participants performed the task with their right hand in the scanner, this effect may be explained by Centaur's strong performance in predicting choices. b, Predictive performance of Centaur's representations against alternatives for ROIs that have been identified as behaviorally relevant in previous work. Cortical scores are averaged over the corresponding bilateral parcels in the Schaefer atlas. The accumbens is defined based on the Harvard-Oxford atlas. Pearson correlation coefficients are shown for layer 20 but exhibit a similar pattern across all layers. Centaur outperformed Llama and the cognitive model in predicting activity in accumbens, the ROI from the original study that showed a reward prediction error effect 19,37 . We found a similar pattern in the medial PFC, another region that showed an effect in the original article 37 , as well as in the sensory and motor cortices.

## Article

Extended Data Fig. 7 | Log-likelihood comparison between Centaur and Minitaur on the analyses from the main text. a, Negative log-likelihoods relative to the domain-specific cognitive models on held-out participants from Psych-101. Error bars correspond to the standard error of the mean, taken over

<!-- image -->

responses. b, Negative log-likelihoods for the two-step task with a modified cover story. c, Negative log-likelihoods for a three-armed bandit experiment. d, Negative log-likelihoods for an experiment probing logical reasoning with items based on the Law School Admission Test (LSAT).

## Extended Data Table 1 | Psych-101 metrics

Full negative log-likelihoods on held-out participants.

Supplementary information

## A foundation model to predict and capture human cognition

In the format provided by the authors and unedited

Nature | www.nature.com/nature

## A foundation model of human cognition

## Supplementary Information (SI)

| Supplementary Methods                                                           | 4      |
|---------------------------------------------------------------------------------|--------|
| Model-guided scientific discovery . . . . . . . . . . . . . . . . . . . . . .   | . . 4  |
| Modeling details . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  | . . 4  |
| Generalized context model . . . . . . . . . . . . . . . . . . . . . . .         | . . 4  |
| Prospect theory model . . . . . . . . . . . . . . . . . . . . . . . . .         | . . 5  |
| Hyperbolic discounting model . . . . . . . . . . . . . . . . . . . . .          | . . 5  |
| Dual-systems model . . . . . . . . . . . . . . . . . . . . . . . . . .          | . . 5  |
| Rescorla-Wagner model . . . . . . . . . . . . . . . . . . . . . . . .           | . . 6  |
| Rescorla-Wagner model with context . . . . . . . . . . . . . . . . .            | . . 6  |
| Linear regression model . . . . . . . . . . . . . . . . . . . . . . . .         | . . 7  |
| Weighted-additive model . . . . . . . . . . . . . . . . . . . . . . . .         | . . 7  |
| Decision-updated reference point model . . . . . . . . . . . . . . .            | . . 7  |
| Odd-one-out model . . . . . . . . . . . . . . . . . . . . . . . . . . .         | . . 8  |
| Multi-task reinforcement learning model . . . . . . . . . . . . . . .           | . . 8  |
| GP-UCB model . . . . . . . . . . . . . . . . . . . . . . . . . . . . .          | . . 8  |
| Rational model . . . . . . . . . . . . . . . . . . . . . . . . . . . . .        | . . 9  |
| Lookup table model . . . . . . . . . . . . . . . . . . . . . . . . . .          | . . 9  |
| Supplementary Notes                                                             | 9      |
| Newell test . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | . . 9  |
| Behave as an (almost) arbitrary function of the environment . . .               | . . 9  |
| Operate in real time . . . . . . . . . . . . . . . . . . . . . . . . . .        | . . 10 |
| Exhibit rational, that is, effective adaptive behavior . . . . . . . .          | . . 10 |
| Use vast amounts of knowledge about the environment . . . . . . .               | . . 10 |
| Behave robustly in the face of error, the unexpected, and the unknown           | 10     |
| Integrate diverse knowledge . . . . . . . . . . . . . . . . . . . . . .         | . . 10 |
| Use (natural) language . . . . . . . . . . . . . . . . . . . . . . . . .        | . . 10 |
| Exhibit self-awareness and a sense of self . . . . . . . . . . . . . . .        | . . 11 |
| Learn from its environment . . . . . . . . . . . . . . . . . . . . . .          | . . 11 |
| Acquire capabilities through development . . . . . . . . . . . . . .            | . . 11 |
| Arise through evolution . . . . . . . . . . . . . . . . . . . . . . . .         | . . 11 |
| Be realizable within the brain . . . . . . . . . . . . . . . . . . . . .        | . . 11 |
| Example prompts . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .   | . . 11 |
| Shepard categorization . . . . . . . . . . . . . . . . . . . . . . . . .        | . . 11 |

| Drifting four-armed bandit                         | . . . . . . . . . . . . . . . . . . . . . . . . 13                                                                           |
|----------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------|
| Multiple-cue judgment . .                          | . . . . . . . . . . . . . . . . . . . . . . . . . 15                                                                         |
| Recall and recognition . .                         | . . . . . . . . . . . . . . . . . . . . . . . . . 17                                                                         |
| N-back . . . . . . . . . . .                       | . . 20                                                                                                                       |
| Digit span . . . . . . . . .                       | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 23                           |
| Go/no-go . . . . . . . . .                         | . . . . . . . . . . . . . . . . . . . . . . . . . 27                                                                         |
| Recent probes . . . . . . .                        | . . . . . . . . . . . . . . . . . . .                                                                                        |
| Horizon task . . . . . . .                         | . . . . . . 29 . . . . . . . . . . . . . . . . . . . . . . . . . 31                                                          |
| Gardening task . . . . . .                         | . . . . . . . . . . 34                                                                                                       |
| Columbia card task . . . .                         | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 35                                           |
| Balloon analog risk task .                         | . . . . . . . . . . . . . . . . . . . . . . . . . 37                                                                         |
| Experiential-symbolic task                         | . . . 40                                                                                                                     |
| Two-armed bandit                                   | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 41                     |
| Conditional associative learning                   | . . . . . . . . . . . . . . . . . . . . . . 44                                                                               |
| THINGS odd-one-out . .                             | . . . . . . . . . . . . . . . . . . . . . . . . . 46                                                                         |
| Multi-attribute decision-making                    | . . . . . . . . . . . . . . . . . . . . . . 48                                                                               |
| Grammar judgement . . .                            | . . . . . . . . . . . . . . . . . . . . . . . . . 49                                                                         |
| Two-step task . . . . . . .                        | . . . . . . . . . . . . . . . . . . . . . . . . . 52                                                                         |
| Two-step task . . . . . . .                        | . . . . . . . . . . . . . . . . . . . . . . . . . 53                                                                         |
| Risky choice                                       | . . 55                                                                                                                       |
| Tile-revealing task                                | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 57   |
| Probabilistic instrumental                         | learning . . . . . . . . . . . . . . . . . . . . 64                                                                          |
| Medin categorization                               | . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                          |
| Zoopermarket . . . . . . .                         | . . 66 . . . . . . . . . . . . . . . . . . . . . . . . . 68                                                                  |
| choices13k . . . . . . . . .                       | . . . . . . 70                                                                                                               |
| CPC18 . . . . . . . . . . .                        | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 72                                   |
| Episodic long-term memory                          | . . . . . . . . . . . . . . . . . . . . . . . . 74                                                                           |
| Intertemporal choice . . .                         | . . . . . . . . . . . . . . . . . . . . . . . . . 75                                                                         |
| Horizon task . . . . . . . Structured bandit       | . . . . . . . . . . . . . . . . . . . . . . . . . 76 . . 79                                                                  |
| Horizon task                                       | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 81   |
|                                                    | Weather prediction task . . . . . . . . . . . . . . . . . . . . . .                                                          |
| Iowa gambling task . . . .                         | . . . . 84 . . . . . . . . . . . . 86                                                                                        |
|                                                    | . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                          |
| Virtual subway network .                           | . . . . . . 88                                                                                                               |
| Multi-task reinforcement learning                  | . . . . . . . . . . . . . . . . . . . . . . . . . . . 89                                                                     |
| Horizon task . . . . . . . Horizon                 | . . . . . . . . . . . . . . . . . . . . . . . . . 91 task . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 94 |
| Aversive learning . . . . .                        | . . . . . . . . . . . . . . . . . . . . . . . . .                                                                            |
| Spatially correlated                               | 96 bandit . . . . . . . . . . . . . . . . . 98                                                                               |
| multi-armed Serial reaction time task .            | . . . . . . . 100                                                                                                            |
| Decisions from description                         | . .                                                                                                                          |
|                                                    | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 102                                        |
| Decisions from                                     | experience . . . . . . . . . . . . . . . . . . . . . . . . . 102                                                             |
| Changing bandit . . . . . Probabilistic reasoning  | . . . . . . . . . . . . . . . . . . . . . . . . . 105 . . . . . . . . . . . . . . .                                          |
| . .                                                | . . . . . . . . . . 107                                                                                                      |
| Two-step task . . . . . . . data . . . . . . . . . | . . . . . . . . . . . . . . . . . . . . . . . . . 109 . . . . . . . . . . . . . . . . . . . . . . . . . 111                  |

| Two-step task (modified cover story) . . . . . .   | . . . . . . . . . . . . . 111   |
|----------------------------------------------------|---------------------------------|
| Maggie's farm (modified problem structure) . .     | . . . . . . . . . . . . . 113   |
| Logical reasoning (entirely novel domain) . . .    | . . . . . . . . . . . . . 114   |
| Two-step task (neural alignment) . . . . . . . .   | . . . . . . . . . . . . . 116   |
| Sentence reading (neural alignment) . . . . . .    | . . . . . . . . . . . . . 118   |

## Supplementary Methods

## Model-guided scientific discovery

We generated an explanation for the behavior of every participant in the multiattribute decision-making study of [1] using DeepSeek-R1 based on the following prompt template:

In the following, you will see a transcript of a psychological experiment. Participant responses are highlighted within "&lt;&lt;" and "&gt;&gt;" characters. Your job will be to explain what strategies that participant used to solve the given task. Your explanation should be targeted at an expert cognitive scientist.

### START OF TRANSCRIPT ###

[TRANSCRIPT]

### END OF TRANSCRIPT ###

Please explain what strategies that participant used to solve the given task in less than two hundred words:

## Modeling details

In the following, we list the domain-specific cognitive and statistical models used in our comparison. Each model was implemented in PyTorch [2]. We optimized a joint set of parameters for all participants in the training data by maximizing log-likelihoods of their choices and then evaluated how well a model with these parameters predicts choices of held-out participants. The optimization procedure involved 1000 iterations over the entire training set, and relied on a gradient-based algorithm [3] with an initial learning rate of 0.1. We use ✶ to denote the indicator function that takes a value of one if the argument is true and zero otherwise.

## Generalized context model

Reference: [4]

This model was used for the following experiments:

- Shepard categorization
- Medin categorization
- Weather prediction task

It uses the following log-likelihood:

<!-- formula-not-decoded -->

where xt are the features of the item observed at trial t and yt is the corresponding class label. β is a free parameter of the model.

## Prospect theory model

Reference: [5]

This model was used for the following experiments:

- CPC18
- choices13k
- Decisions from description

It uses the following log-likelihood:

<!-- formula-not-decoded -->

where pi is the vector of probabilities and xi is the vector of values for each possible outcome in option i. β, a, b, c, d, e, f, and g are free parameters of the model.

## Hyperbolic discounting model

Reference: [6]

This model was used for the following experiments:

- Intertemporal choice

It uses the following log-likelihood:

<!-- formula-not-decoded -->

where xi is the reward and γi is the delay of delivery for option i. β and a are free parameters of the model.

## Dual-systems model

Reference: [7]

This model was used for the following experiments:

- Two-step task

It uses the following log-likelihood:

<!-- formula-not-decoded -->

where QMB s,i and QMF s,i are model-based and model-free value estimates that are computed as described in [7]. β and τ are free parameters of the model. We also included a stickiness term for the first stage choices, which is omitted for brevity in the equations above.

## Rescorla-Wagner model

Reference: [8]

This model was used for the following experiments:

- Drifting four-armed bandit
- Horizon task
- Two-armed bandit
- Probabilistic instrumental learning
- Iowa gambling task
- Changing bandit
- Decisions from experience

It uses the following log-likelihood:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

where rt is the reward obtained in trial t. α+, α-, a, b, c, and d are free parameters of the model.

## Rescorla-Wagner model with context

Reference: [9]

This model was used for the following experiments:

- Conditional associative learning

It uses the following log-likelihood:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

where rt is the reward obtained in trial t. α, β, and d are free parameters of the model.

## Linear regression model

Reference: [10]

This model was used for the following experiments:

- Multiple-cue judgment
- Gardening task

It uses the following log-likelihood for multiple-cue judgment:

<!-- formula-not-decoded -->

It uses the following log-likelihood for the gardening task:

<!-- formula-not-decoded -->

and the following learning rule for both tasks:

<!-- formula-not-decoded -->

where rt is the reward obtained in trial t and xt are the observed features. α, β, γ, and d are free parameters of the model.

## Weighted-additive model

Reference: [11]

This model was used for the following experiments:

- Multi-attribute decision-making

It uses the following log-likelihood:

<!-- formula-not-decoded -->

where xi is the vector of features for option i. w are free parameters of the model.

## Decision-updated reference point model

Reference: [12]

This model was used for the following experiments:

- Columbia card task

It uses the following log-likelihood:

```
p(ct = sample|xwin, xloss, pwin, ploss) ∝ exp (h · (xwin · pwin + xloss · ploss) + i) p(ct = stop|xwin, xloss, pwin, ploss) ∝ exp (j) π (p) = sigmoid (a) + sigmoid (b) · p u (v) = {sigmoid (c) · vsigmoid(d) where v ≥ 0 -sigmoid (e) · (-sigmoid (f) v)sigmoid(g) where v < 0
```

where xwin and xloss are the values that can be won or lost respectively, and pwin and ploss are the corresponding probabilities. a, b, c, d, e, f, g, h, i, and j are free parameters of the model.

## Odd-one-out model

Reference: [13]

This model was used for the following experiments:

- THINGS odd-one-out

It uses the following log-likelihood:

<!-- formula-not-decoded -->

where xi, xj, and xk are the observed objects with their corresponding embeddings xi, xj, and xk ∈ R16 that are free parameters of the model.

## Multi-task reinforcement learning model

Reference: [14]

This model was used for the following experiments:

- Multi-task reinforcement learning
- Zoopermarket

## GP-UCB model

Reference: [15]

This model was used for the following experiments:

- Spatially correlated multi-armed bandit
- Structured bandit

It uses the following log-likelihood:

<!-- formula-not-decoded -->

where mi,t and si,t are obtained via Gaussian Process regression with a radial basis function kernel as described in [15]. β and γ are free parameters of the model.

## Rational model

Reference: N/A

This model was used for the following experiments:

- Balloon analog risk task
- N-back
- Digit span
- Go/no-go
- Recent probes
- Serial reaction time task

It uses the following log-likelihood:

<!-- formula-not-decoded -->

where j is the optimal choice at trial t. Θ ∈ RNc×Nc are free parameters of the model.

## Lookup table model

Reference: N/A

This model was used for the following experiments:

- Grammar judgement

It uses the following log-likelihood:

<!-- formula-not-decoded -->

where Θ ∈ RT×Nc are free parameters of the model.

## Supplementary Notes

## Newell test

Together with his call for unified theories of cognition [16, 17], Newell outlined a set of criteria that a unified computational model should fulfill. Centaur is the first model to satisfy the majority of these criteria (see Table 1). Most importantly, it (1) behaves as an almost arbitrary function of the environment, (2) operates in real time, and (3) relies on vast amounts of knowledge about the world. We provide an extended discussion on Newell's criteria in the following.

## Behave as an (almost) arbitrary function of the environment

This is the most important criterion according to Newell. Centaur fulfills it more than any previous model as shown by our extensive analysis. Yet, Centaur's scope is still limited to psychological experiments that can be expressed in natural language. It will be an important avenue for future research to transfer this ability to real-world applications.

Supplementary Table 1 Newell test for a theory of cognition.

| Criterion                                                             | Fulfilled by Centaur   |
|-----------------------------------------------------------------------|------------------------|
| Behave as an (almost) arbitrary function of the environment           | ✓                      |
| Operate in real time                                                  | ✓                      |
| Exhibit rational, that is, effective adaptive behavior                | ✓                      |
| Use vast amounts of knowledge about the environment                   | ✓                      |
| Behave robustly in the face of error, the unexpected, and the unknown | ✓                      |
| Integrate diverse knowledge                                           | ✓                      |
| Use (natural) language                                                | ✓                      |
| Exhibit self-awareness and a sense of self                            | •                      |
| Learn from its environment                                            | ✓                      |
| Acquire capabilities through development                              | ✗                      |
| Arise through evolution                                               | ✗                      |
| Be realizable within the brain                                        | ✓                      |

## Operate in real time

Centaur can simulate human behavior in (almost) real-time. For example, running an open-loop simulation of a typical two-step task experiment takes around 30 minutes, while it takes around 20 minutes for the average human participant. We believe that inference time could be further optimized to fully close this gap.

## Exhibit rational, that is, effective adaptive behavior

Bayesian inference is the gold standard for rational and adaptive behavior [18]. Previous work has shown that systems that engage in in-context learning implement Bayesian inference implicitly [19]. In-context learning is at the heart of Centaur, thereby making it a rational and adaptive system.

## Use vast amounts of knowledge about the environment

Large language models are the biggest knowledge bases we have to date. As Centaur is built on top of a state-of-the-art language model, it fulfills this criterion by design.

## Behave robustly in the face of error, the unexpected, and the unknown

Our extensive out-of-distribution evaluations clearly demonstrate that Centaur has this ability.

## Integrate diverse knowledge

This was originally a criterion on symbols and abstractions [16]. At the basic level, Centaur is a system that processes language. Language is a symbolic system, meaning that Centaur fulfills this criterion.

## Use (natural) language

No further elaboration is required.

## Exhibit self-awareness and a sense of self

This is a tricky criterion as Centaur is trained on a population of individuals. Yet, to make good predictions about the future, Centaur needs to make inferences about the person who has produced a given trajectory, and in order to do that it requires a representation of that person [20].

## Learn from its environment

Psych-101 contains many experiments that require learning from an environment. Centaur does well in those experiments, thereby clearly satisfying this criterion.

## Acquire capabilities through development

Centaur makes no claims about how human behavior might arise through development.

## Arise through evolution

Centaur makes no claims about how human behavior might arise through evolution.

## Be realizable within the brain

We have shown that Centaur's internal representations are robust predictors of human neural activity. Even though there is clearly a gap between the transformer architecture that Centaur is based on and the human brain, Centaur still represents the current state-of-the-art when looking at neural alignment to human subjects.

## Example prompts

The following sections present the experiments contained in Psych-101 in detail. Example prompts are truncated to 4096 characters but otherwise shown as is.

## Shepard categorization

Data source: [21]

Number of experiments: 1

Number of participants: 85

Number of choices: 29776

## Example prompt:

You will be shown several examples of geometric objects.

Your task is to learn a rule that allows you to tell whether an object belongs to the E or K category.

For each presented object, you will be asked to make a category judgment by pressing the corresponding key and then you will receive feedback.

You will encounter four different problems with different rules.

You encounter a new problem with a new rule determining which objects belong to each category:

```
You see a big black square. You press <<K>>. The correct category is K. You see a small black triangle. You press <<K>>. The correct category is E. You see a big white triangle. You press <<E>>. The correct category is K. You see a small white triangle. You press <<E>>. The correct category is E. You see a small white square. You press <<E>>. The correct category is E. You see a small black square. You press <<K>>. The correct category is E. You see a big white square. You press <<E>>. The correct category is K. You see a big black triangle. You press <<E>>. The correct category is K. You see a big white square. You press <<E>>. The correct category is K. You see a big black square. You press <<E>>. The correct category is K. You see a small white triangle. You press <<K>>. The correct category is E. You see a small black triangle. You press <<K>>. The correct category is E. You see a big white triangle. You press <<E>>. The correct category is K. You see a small white square. You press <<K>>. The correct category is E. You see a small black square. You press <<K>>. The correct category is E. You see a big black triangle. You press <<E>>. The correct category is K. You see a small white square. You press <<E>>. The correct category is E. You see a small black square. You press <<E>>. The correct category is E. You see a big white triangle. You press <<K>>. The correct category is K. You see a small black triangle. You press <<K>>. The correct category is E. You see a small white triangle. You press <<E>>. The correct category is E. You see a big white square. You press <<K>>. The correct category is K. You see a big black triangle. You press <<E>>. The correct category is K. You see a big black square. You press <<E>>. The correct category is K. You see a small black triangle. You press <<E>>. The correct category is E. You see a small white square. You press <<K>>. The correct category is E. You see a small black square. You press <<E>>. The correct category is E. You see a big black square. You press <<K>>. The correct category is K. You see a big white square. You press <<K>>. The correct category is K. You see a big white triangle. You press <<K>>. The correct category is K. You see a small white triangle. You press <<E>>. The correct category is E. You see a big black triangle. You press <<K>>. The correct category is K. You see a small white square. You press <<E>>. The correct category is E. You see a big black triangle. You press <<K>>. The correct category is K. You see a big black triangle. You press <<K>>. The correct category is K. You see a small white triangle. You press <<E>>. The correct category is E. You see a big white triangle. You press <<K>>. The correct category is K. You see a small white triangle. You press <<E>>. The correct category is E. You see a small black triangle. You press <<E>>. The correct category is E. You see a small black square. You press <<E>>. The correct category is E. You see a small black triangle. You press <<E>>. The correct category is E. You see a big white square. You press <<K>>. The correct category is K. You see a big black square. You press <<K>>. The correct category is K. You see a big white square. You press <<K>>. The correct category is K.
```

```
You see a big black square. You press <<K>>. The correct category is K. You see a small black square. You press <<E>>. The correct category is E. You see a big white triangle. You press <<E>>. The correct category is K. You see a small white square. You press <<E>>. The correct category is E. You see a big white square. You press <<K>>. The correct category is K. You see
```

## Drifting four-armed bandit

```
Data source: [22] Number of experiments: 1 Number of participants: 869 Number of choices: 125952
```

## Example prompt:

You will be asked to repeatedly choose between four different options labeled L, G, O, and U.

You select an option by pressing the corresponding key on your keyboard.

Each time you select an option, you will get a different number of points. Your goal is to win as many points as possible.

```
You press <<L>> and get 84.0 points. You press <<G>> and get 90.0 points. You press <<O>> and get 53.0 points. You press <<U>> and get 24.0 points. You press <<G>> and get 92.0 points. You press <<G>> and get 78.0 points. You press <<L>> and get 71.0 points. You press <<L>> and get 75.0 points. You press <<G>> and get 80.0 points. You press <<G>> and get 80.0 points. You press <<G>> and get 91.0 points. You press <<G>> and get 90.0 points. You press <<U>> and get 29.0 points. You press <<O>> and get 45.0 points. You press <<G>> and get 81.0 points. You press <<G>> and get 75.0 points. You press <<G>> and get 82.0 points. You press <<G>> and get 82.0 points. You press <<G>> and get 87.0 points. You press <<G>> and get 85.0 points. You press <<G>> and get 87.0 points. You press <<G>> and get 87.0 points. You press <<G>> and get 79.0 points. You press <<G>> and get 75.0 points.
```

```
You press <<L>> and get 61.0 points. You press <<O>> and get 40.0 points. You press <<U>> and get 37.0 points. You press <<G>> and get 72.0 points. You press <<G>> and get 73.0 points. You press <<L>> and get 66.0 points. You press <<G>> and get 57.0 points. You press <<L>> and get 64.0 points. You press <<L>> and get 63.0 points. You press <<L>> and get 61.0 points. You press <<O>> and get 54.0 points. You press <<U>> and get 30.0 points. You press <<L>> and get 59.0 points. You press <<O>> and get 56.0 points. You press <<O>> and get 46.0 points. You press <<L>> and get 59.0 points. You press <<G>> and get 63.0 points. You press <<G>> and get 63.0 points. You press <<G>> and get 58.0 points. You press <<L>> and get 53.0 points. You press <<O>> and get 60.0 points. You press <<O>> and get 59.0 points. You press <<L>> and get 52.0 points. You press <<O>> and get 54.0 points. You press <<U>> and get 23.0 points. You press <<G>> and get 52.0 points. You press <<O>> and get 52.0 points. You press <<L>> and get 67.0 points. You press <<L>> and get 71.0 points. You press <<L>> and get 71.0 points. You press <<L>> and get 69.0 points. You press <<G>> and get 46.0 points. You press <<O>> and get 47.0 points. You press <<U>> and get 19.0 points. You press <<L>> and get 63.0 points. You press <<L>> and get 58.0 points. You press <<L>> and get 62.0 points. You press <<L>> and get 53.0 points. You press <<L>> and get 59.0 points. You press <<L>> and get 65.0 points. You press <<G>> and get 58.0 points. You press <<O>> and get 54.0 points. You press <<L>> and get 61.0 points. You press <<G>> and get 66.0 points. You press <<O>> and get 62.0 points.
```

```
You press <<L>> and get 61.0 points. You press <<G>> and get 56.0 points. You press <<O>> and get 58.0 points. You press <<L>> and get 49.0 points. You press <<O>> and get 50.0 points. You press <<G>> and get 63.0 points. You press <<G>> and get 68.0 points. You press <<G>> and get 56.0 points. You press <<G>> and get 59.0 points. You press <<G>> and get 66.0 points. You press <<G>> and get 56.0 points. You press <<G>> and get 56.0 points. You press <<L>> and get 48.0 points. You press <<G>> and get 59.0 points. You press <<G>> and get 55.0 points. You press <<O>> and get 51.0 points. You press <<O>> and get 58.0 points. You press <<O>> and get 51.0 points. You press <<O>> and get 62.0 points. You press <<O>> and get 64.0 points. You press <<O>> and get 60.0 points. You press <<O>> and get 62.0 points. You press <<O>> and get 64.0 points. You press <<O>> and get 50.0 points. You press <<U>> and get 40.0 points. You press <<O>> and get 50.0 points. You press <<G>> and get 49.0 points. You press <<L>> and get 33.0 points. You press <<G>> and get 55.0 points. You press <<O>> and get 78.0 points. You press <<O>> and get 79.0 points. You press <<O>> and get 85.0 points. You press <<O>> and get 82.0 points. You press <<O>> and get 83.0 po
```

## Multiple-cue judgment

```
Data source: [23] Number of experiments: 3 Number of participants: 232 Number of choices: 52464
```

## Example prompt:

Your task is to estimate the blood concentration of the hormone Caldionine based on information about the amount of two other hormones, Progladine and Amalydine, in multiple individuals' urine.

Both Progladine and Amalydine can take five values (very little, a little, average, a lot, very much).

Caldionine can take nine values (extremely low, very low, low, somewhat low, normal, somewhat high, high, very high, extremely high).

Your goal is to estimate the concentration of Caldionine correctly.

You will receive feedback about the actual concentration after making your estimate. This feedback will stop at some point.

Progladine: a lot. Amalydine: very much. You say that the Caldionine concentration is &lt;&lt;high&gt;&gt;. That is incorrect. The correct concentration of Caldionine is somewhat low.

Progladine: average. Amalydine: a lot. You say that the Caldionine concentration is &lt;&lt;somewhat low&gt;&gt;. That is correct. The correct concentration of Caldionine is indeed somewhat low.

Progladine: a lot. Amalydine: average. You say that the Caldionine concentration is &lt;&lt;normal&gt;&gt;. That is incorrect. The correct concentration of Caldionine is somewhat high.

Progladine: average. Amalydine: a little. You say that the Caldionine concentration is &lt;&lt;low&gt;&gt;. That is incorrect. The correct concentration of Caldionine is somewhat high.

Progladine: a little. Amalydine: average. You say that the Caldionine concentration is &lt;&lt;normal&gt;&gt;. That is incorrect. The correct concentration of Caldionine is somewhat low.

Progladine: a lot. Amalydine: a little. You say that the Caldionine concentration is &lt;&lt;very high&gt;&gt;. That is incorrect. The correct concentration of Caldionine is high.

Progladine: very little. Amalydine: very little. You say that the Caldionine concentration is &lt;&lt;normal&gt;&gt;. That is correct. The correct concentration of Caldionine is indeed normal.

Progladine: very much. Amalydine: a little. You say that the Caldionine concentration is &lt;&lt;very high&gt;&gt;. That is correct. The correct concentration of Caldionine is indeed very high.

Progladine: a lot. Amalydine: very little. You say that the Caldionine concentration is &lt;&lt;very high&gt;&gt;. That is correct. The correct concentration of Caldionine is indeed very high.

Progladine: a little. Amalydine: a little. You say that the Caldionine concentration is &lt;&lt;normal&gt;&gt;. That is correct. The correct concentration of Caldionine is indeed normal.

Progladine: a little. Amalydine: very little. You say that the Caldionine concentration is &lt;&lt;somewhat high&gt;&gt;. That is correct. The correct concentration of Caldionine is indeed somewhat high.

Progladine: very little. Amalydine: a little. You say that the Caldionine concentration is &lt;&lt;somewhat low&gt;&gt;. That is correct. The correct concentration of Caldionine is indeed somewhat low.

Progladine: very much. Amalydine: a lot. You say that the Caldionine concentration is &lt;&lt;very high&gt;&gt;. That is incorrect. The correct concentration of Caldionine is somewhat high.

Progladine: a little. Amalydine: very much. You say that the Caldionine concentration is &lt;&lt;very low&gt;&gt;. That is correct. The correct concentration of Caldionine is indeed very low.

Progladine: average. Amalydine: very much. You say that the Caldionine concentration is &lt;&lt;low&gt;&gt;. That is correct. The correct concentration of Caldionine is indeed low.

Progladine: very much. Amalydine: average. You say that the Caldionine concentration is &lt;&lt;somewhat high&gt;&gt;. That is incorrect. The correct concentration of Caldionine is high.

Progladine: average. Amalydine: very little. You say that the Caldionine concentration is &lt;&lt;high&gt;&gt;. That is correct. The correct concentration of Caldionine is indeed high.

Progladine: a little. Amalydine: a lot. You say that the Caldionine concentration is &lt;&lt;normal&gt;&gt;. That is incorrect. The correct concentration of Caldionine is low.

Progladine: very much. Amalydine: very much. You say that the Caldionine concentration is &lt;&lt;normal&gt;&gt;. That is correct. The correct concentration of Caldionine is indeed normal.

Progladine: a lot. Amalydine: a lot. You say that the Caldionine concentration is &lt;&lt;normal&gt;&gt;. That is correct.

## Recall and recognition

Data source: [24]

Number of experiments: 1

Number of participants: 424

Number of choices: 109201

## Example prompt:

You study the following 20 word pairs:

FILE, GERMAN STANDS, RISES OFFICER, FUEL CLASSROOM, JOURNEY TERRITORY, EDUCATIONAL TRANSPORTATION, AGREEMENT SIGNIFICANT, SPECIALIZED TUBE, ENEMY CLUB, RAPID LEGAL, CONCEPT TOWARDS, VICTORY RARELY, BAY ELECTION, ROYAL

BELONG, SUPREME

FRIGHTENED, PLAINS SLAVES, FILM NURSE, GOLDEN POLITICS, WINGS

STOMACH, WHISPERED BOXES, TOM You will now view a single pair of words. Your task is to indicate if the pair of words you see on the screen was studied as a pair on the list you just studied (by pressing D) or was not a pair (by pressing N). You view the word pair SPECIALIZED, POLITICS. You press &lt;&lt;N&gt;&gt;. You view the word pair TOWARDS, VICTORY. You press &lt;&lt;D&gt;&gt;. You view the word pair SUPREME, BELONG. You press &lt;&lt;D&gt;&gt;. You view the word pair WINGS, OFFICER. You press &lt;&lt;D&gt;&gt;. You view the word pair CONCEPT, FRIGHTENED. You press &lt;&lt;N&gt;&gt;. You view the word pair GERMAN, NURSE. You press &lt;&lt;N&gt;&gt;. You view the word pair BAY, RARELY. You press &lt;&lt;D&gt;&gt;. You view the word pair FILE, GOLDEN. You press &lt;&lt;N&gt;&gt;. You view the word pair JOURNEY, LEGAL. You press &lt;&lt;N&gt;&gt;. You view the word pair CLASSROOM, ENEMY. You press &lt;&lt;N&gt;&gt;. You view the word pair ROYAL, ELECTION. You press &lt;&lt;D&gt;&gt;. You view the word pair BOXES, TOM. You press &lt;&lt;D&gt;&gt;. You view the word pair TERRITORY, EDUCATIONAL. You press &lt;&lt;D&gt;&gt;. You view the word pair WHISPERED, STOMACH. You press &lt;&lt;D&gt;&gt;. You view the word pair STANDS, RISES. You press &lt;&lt;D&gt;&gt;. You view the word pair AGREEMENT, TUBE. You press &lt;&lt;N&gt;&gt;. You view the word pair FUEL, TRANSPORTATION. You press &lt;&lt;N&gt;&gt;. You view the word pair CLUB, RAPID. You press &lt;&lt;D&gt;&gt;. You view the word pair SLAVES, FILM. You press &lt;&lt;D&gt;&gt;. You view the word pair PLAINS, SIGNIFICANT. You press &lt;&lt;N&gt;&gt;. You study the following 20 word pairs: METALS, BEAUTY SHORE, COLONISTS HIGHEST, FASHION INFLUENCED, FLEW SHADOW, GRANDFATHER MOTOR, DISAPPEARED DETAIL, SHOULDERS REPORTS, MALE PAINT, COMMUNITIES STORM, RESULTING SELECTION, NIGHTS APPLICATION, FELLOW

DESIGN, PRINCIPLE

```
POSSIBILITY, AFRICAN REMOVE, TRAIL STAFF, JUSTICE SECTIONS, TRADITIONAL CLAY, MIXED TEA, AGRICULTURE PATIENT, LIMIT You will now view a single word item. Your task is to type the other word in the pair. For example if you studied BRICK, BRACK and you now see BRICK, your response should be BRACK. The spelling does not matter; focus on providing as many responses as possible. If you cannot recall the word, answer DON'T REMEMBER. You view the word STAFF. You answer <<JUSTICE>>. You view the word MOTOR. You answer <<DON'T REMEMBER>>. You view the word INFLUENCED. You answer <<DON'T REMEMBER>>. You view the word DETAIL. You answer <<SHOULDER>>. You view the word REMOVE. You answer <<DON'T REMEMBER>>. You view the word PATIENT. You answer <<LIMITED>>. You view the word PAINT. You answer <<COMMUNITY>>. You view the word STORM. You answer <<RESULTS>>. You view the word TEA. You answer <<ARIGCULTURE>>. You view the word SHADOW. You answer <<GRANDFATHER>>. You view the word APPLICATION. You answer <<FELLOW>>. You view the word METALS. You answer <<BEAUTY>>. You view the word POSSIBILITY. You answer <<AFRICANS>>. You view the word DESIGN. You answer <<PRINCPLE>>. You view the word SHORE. You answer <<DON'T REMEMBER>>. You view the word HIGHEST. You answer <<DON'T REMEMBER>>. You view the word CLAY. You answer <<MIXED>>. You view the word REPORTS. You answer <<DON'T REMEMBER>>. You view the word SECTIONS. You answer <<DON'T REMEMBER>>. You view the word SELECTION. You answer <<DON'T REMEMBER>>. You study the following 20 word pairs: DEFENSE, EXPANSION PROGRESS, PROMISE EGG, ATTRACTIVE CRYING, RECOGNIZE PURE, AUNT OBTAINED, FEATURE
```

TRAVELED, FLOWER

INCREASINGLY, FEMALE POURED, VALUABLE TIGHT, HOLDS BIGGER, HONOR DRUG, SPENDING DOUBLE, OUTPUT ESTABLISH, CRITICAL DRIED, CHRISTMAS PROCESSING, NUMEROUS MEASURES, PARAGRAPH AFFAIRS, MOVEMENTS DAMAGE, FED

WARS, CONTRACT You will now view a single word item. Your task is to indicate if the item you view was on the list you just studied (by pressing D) or not on the list (by pressing N). You view the word EXPANSION. You press &lt;&lt;D&gt;&gt;. N-back Data source: [25] Number of experiments: 1 Number of participants: 470 Number of choices: 200821 Example prompt: You will view a stream of letters on the screen, one letter at a time. At the beginning of a block, you are told a number N. You have to remember the last N letters you saw since the beginning of the block. If the letter you see matches the letter N trials ago, press W, otherwise press D. The case of the letter is irrelevant, so "t" matches "T" for example. If you make more than 5 mistakes in a block, N is decreased by 1. If you make fewer than 3 mistakes in a block, N is increased by 1. You will go through 20 blocks with 20+N trials each.

```
Block 0, N = 2: You see the letter d. You see the letter g. You see the letter D and press <<W>>. You see the letter v. You see the letter B. You see the letter V.
```

You see the letter d.

```
You see the letter g. You see the letter D and press <<W>>. You see the letter t. You see the letter G. You see the letter B and press <<D>>. You see the letter G. You see the letter g and press <<W>>. You see the letter g and press <<W>>. You see the letter v. You see the letter V. You see the letter B. You see the letter G. You see the letter G. You see the letter G and press <<W>>. You see the letter G. Block 1, N = 1: You see the letter g. You see the letter D and press <<D>>. You see the letter D. You see the letter d and press <<W>>. You see the letter D. You see the letter d and press <<W>>. You see the letter v. You see the letter b and press <<D>>. You see the letter V. You see the letter t and press <<D>>. You see the letter d. You see the letter b and press <<D>>. You see the letter G. You see the letter t and press <<D>>. You see the letter D. You see the letter t and press <<D>>. You see the letter t. You see the letter b and press <<D>>. You see the letter B. You see the letter B and press <<W>>. You see the letter v. Block 2, N = 1: You see the letter g. You see the letter g and press <<W>>. You see the letter d. You see the letter d and press <<W>>. You see the letter T. You see the letter v.
```

```
You see the letter V. You see the letter D and press <<W>>. You see the letter g. You see the letter G and press <<W>>. You see the letter t. You see the letter D and press <<D>>. You see the letter t. You see the letter g and press <<D>>. You see the letter g. You see the letter D and press <<W>>. You see the letter d. You see the letter V. You see the letter B. You see the letter v and press <<D>>. You see the letter V. Block 3, N = 1: You see the letter T. You see the letter d and press <<W>>. You see the letter t. You see the letter V and press <<D>>. You see the letter v. You see the letter B and press <<D>>. You see the letter b. You see the letter D and press <<D>>. You see the letter d. You see the letter d and press <<W>>. You see the letter G. You see the letter B and press <<D>>. You see the letter G. You see the letter d. You see the letter G. You see the letter v and press <<D>>. You see the letter B. You see the letter t and press <<D>>. You see the letter T. You see the letter T and press <<W>>. You see the letter T. Block 4, N = 1: You see the letter d. You see the letter d and press <<W>>. You see the letter d. You see the letter V and press <<D>>. You see the letter V.
```

```
You see the letter v and press <<D>>. You see the letter B. You see the letter B and press <<W>>. You see the letter g. You see the letter B. You see the letter t. You see the letter D. You see the letter d. You see the letter B. You see the letter B. You see the letter t. You see the letter d. You see the letter G. You see the letter d. You see the letter v. You see the letter t. Block 5, N = 1: You see the letter v. You see the letter t and press <<D>>. You see the letter D. You see the letter V and press <<D>>. You see the letter v. You see the letter D and press <<D>>. You see the letter D. You see the letter B and press <<D>>. You see the letter g. You see the letter v and press <<D>>. You see the letter d. You see the letter g. You see the letter G. You see the letter D and press <<D>>. You see the letter b. You see the letter v. You see the letter V. You see the letter D and press <<D>>. You see the Digit span Data source: [25] Number of experiments: 1 Number of participants: 472 Number of choices: 97012
```

## Example prompt:

You will view a series of digits and are then asked to recall them in the order you have seen them by pressing the corresponding keys.

After having recalled all digits, please press 'S' to indicate the end of your recalled sequence.

```
The digits are the following: [4, 8, 2] You press <<4>>. You press <<8>>. You press <<2>>. You press <<S>>.
```

You will view a series of digits and are then asked to recall them in the order you have seen them by pressing the corresponding keys.

After having recalled all digits, please press 'S' to indicate the end of your recalled sequence.

```
The digits are the following: [5, 2, 8, 5] You press <<5>>. You press <<2>>. You press <<8>>. You press <<5>>. You press <<S>>.
```

You will view a series of digits and are then asked to recall them in the order you have seen them by pressing the corresponding keys.

After having recalled all digits, please press 'S' to indicate the end of your recalled sequence.

```
The digits are the following: [9, 2, 8, 2, 5] You press <<9>>. You press <<2>>. You press <<8>>. You press <<2>>. You press <<5>>. You press <<S>>.
```

You will view a series of digits and are then asked to recall them in the order you have seen them by pressing the corresponding keys.

After having recalled all digits, please press 'S' to indicate the end of your recalled sequence.

```
The digits are the following: [8, 1, 4, 8, 4, 9] You press <<8>>. You press <<1>>.
```

```
You press <<4>>. You press <<8>>. You press <<8>>. You press <<1>>. You press <<S>>.
```

You will view a series of digits and are then asked to recall them in the order you have seen them by pressing the corresponding keys.

After having recalled all digits, please press 'S' to indicate the end of your recalled sequence.

```
The digits are the following: [5, 1, 7, 1, 6, 3] You press <<7>>. You press <<1>>. You press <<5>>. You press <<1>>. You press <<6>>. You press <<3>>. You press <<S>>.
```

You will view a series of digits and are then asked to recall them in the order you have seen them by pressing the corresponding keys.

After having recalled all digits, please press 'S' to indicate the end of your recalled sequence.

```
The digits are the following: [5, 9, 5, 9, 1] You press <<5>>. You press <<9>>. You press <<5>>. You press <<9>>. You press <<1>>. You press <<S>>.
```

You will view a series of digits and are then asked to recall them in the order you have seen them by pressing the corresponding keys.

After having recalled all digits, please press 'S' to indicate the end of your recalled sequence.

```
The digits are the following: [7, 2, 5, 8, 2, 6] You press <<7>>. You press <<7>>. You press <<2>>. You press <<8>>. You press <<5>>. You press <<2>>.
```

```
You press <<S>>.
```

You will view a series of digits and are then asked to recall them in the order you have seen them by pressing the corresponding keys.

After having recalled all digits, please press 'S' to indicate the end of your recalled sequence.

```
The digits are the following: [8, 5, 8, 3, 9, 4] You press <<8>>. You press <<5>>. You press <<8>>. You press <<3>>. You press <<9>>. You press <<4>>. You press <<S>>.
```

You will view a series of digits and are then asked to recall them in the order you have seen them by pressing the corresponding keys.

After having recalled all digits, please press 'S' to indicate the end of your recalled sequence.

```
The digits are the following: [9, 6, 9, 5, 1, 7, 1] You press <<9>>. You press <<6>>. You press <<9>>. You press <<5>>. You press <<7>>. You press <<1>>. You press <<7>>. You press <<S>>.
```

You will view a series of digits and are then asked to recall them in the order you have seen them by pressing the corresponding keys.

After having recalled all digits, please press 'S' to indicate the end of your recalled sequence.

```
The digits are the following: [7, 2, 5, 9, 1, 8] You press <<7>>. You press <<2>>. You press <<5>>. You press <<9>>. You press <<1>>. You press <<8>>. You press <<S>>.
```

You will view a series of digits and are then asked to recall them in the order you have seen them by pressing the corresponding keys.

After having recalled all digits, please

## Go/no-go

Data source: [25]

Number of experiments: 1

Number of participants: 463

Number of choices: 150517

## Example prompt:

In this task, you need to emit responses to certain stimuli and omit responses to others.

You will see one of two colours, colour1 or colour2, on the screen in each trial.

You need to press button X when you see colour1 and press nothing when you see colour2.

You need to respond as quickly as possible.

You will be doing 10 practice trials followed by 350 test trials.

```
You see colour1 and press nothing. You see colour2 and press <<X>> in 753.0ms. You see colour2 and press <<X>> in 381.0ms. You see colour2 and press nothing. You see colour1 and press <<X>> in 473.0ms. You see colour1 and press <<X>> in 713.0ms. You see colour2 and press nothing. You see colour1 and press <<X>> in 364.0ms. You see colour2 and press nothing. You see colour1 and press <<X>> in 378.0ms. You see colour1 and press <<X>> in 794.0ms. You see colour1 and press <<X>> in 436.0ms. You see colour1 and press <<X>> in 427.0ms. You see colour1 and press <<X>> in 337.0ms. You see colour1 and press <<X>> in 269.0ms. You see colour1 and press <<X>> in 312.0ms. You see colour1 and press <<X>> in 273.0ms. You see colour2 and press nothing. You see colour1 and press <<X>> in 288.0ms. You see colour1 and press <<X>> in 276.0ms. You see colour1 and press <<X>> in 314.0ms. You see colour1 and press <<X>> in 309.0ms. You see colour1 and press <<X>> in 320.0ms. You see colour1 and press <<X>> in 342.0ms. You see colour1 and press <<X>> in 301.0ms.
```

```
You see colour1 and press <<X>> in 289.0ms. You see colour2 and press nothing. You see colour1 and press <<X>> in 360.0ms. You see colour2 and press <<X>> in 424.0ms. You see colour2 and press nothing. You see colour1 and press <<X>> in 525.0ms. You see colour1 and press <<X>> in 306.0ms. You see colour1 and press <<X>> in 387.0ms. You see colour1 and press <<X>> in 292.0ms. You see colour1 and press <<X>> in 317.0ms. You see colour1 and press <<X>> in 270.0ms. You see colour1 and press <<X>> in 278.0ms. You see colour2 and press nothing. You see colour1 and press <<X>> in 277.0ms. You see colour1 and press <<X>> in 311.0ms. You see colour1 and press <<X>> in 338.0ms. You see colour1 and press <<X>> in 323.0ms. You see colour1 and press <<X>> in 304.0ms. You see colour1 and press <<X>> in 323.0ms. You see colour1 and press <<X>> in 354.0ms. You see colour1 and press <<X>> in 292.0ms. You see colour1 and press <<X>> in 302.0ms. You see colour1 and press <<X>> in 309.0ms. You see colour2 and press nothing. You see colour1 and press <<X>> in 340.0ms. You see colour1 and press <<X>> in 603.0ms. You see colour1 and press <<X>> in 289.0ms. You see colour1 and press <<X>> in 284.0ms. You see colour1 and press <<X>> in 275.0ms. You see colour1 and press <<X>> in 299.0ms. You see colour2 and press nothing. You see colour1 and press <<X>> in 265.0ms. You see colour1 and press <<X>> in 267.0ms. You see colour2 and press nothing. You see colour1 and press <<X>> in 274.0ms. You see colour1 and press <<X>> in 382.0ms. You see colour1 and press <<X>> in 272.0ms. You see colour2 and press nothing. You see colour1 and press <<X>> in 258.0ms. You see colour1 and press <<X>> in 305.0ms. You see colour1 and press <<X>> in 320.0ms. You see colour1 and press <<X>> in 261.0ms. You see colour1 and press <<X>> in 275.0ms. You see colour2 and press nothing. You see colour1 and press <<X>> in 424.0ms.
```

```
You see colour1 and press <<X>> in 266.0ms. You see colour1 and press <<X>> in 273.0ms. You see colour1 and press <<X>> in 287.0ms. You see colour1 and press <<X>> in 437.0ms. You see colour1 and press <<X>> in 293.0ms. You see colour1 and press <<X>> in 297.0ms. You see colour1 and press <<X>> in 308.0ms. You see colour1 and press <<X>> in 313.0ms. You see colour1 and press <<X>> in 373.0ms. You see colour1 and press <<X>> in 390.0ms. You see colour1 and press <<X>> in 304.0ms. You see colour1 and press <<X>> in 334.0ms. You see colour1 and press <<X>> in 326.0ms. You see colour1 and press <<X>> in 382.0ms. You see colour1 and press <<X>> in 803.0ms. You see colour1 and press <<X>> in 430.0ms. You see colour1 and press <<X>> in 324.0ms.
```

You see colour

## Recent probes

Data source: [25]

Number of experiments: 1

Number of participants: 471

Number of choices: 34714

## Example prompt:

You will repeatedly observe sequences of six letters.

You have to remember these letters before they disappear.

Afterward, you will be prompted with one letter. You have to answer whether the letter was part of the six previous letters.

If you think it was, you have to press C. If you think it was not, press Q.

You are shown the letters ['C', 'I', 'Q', 'F', 'W', 'Z']. You see the letter Y. You press &lt;&lt;Q&gt;&gt;.

You are shown the letters ['I', 'Q', 'C', 'D', 'M', 'V']. You see the letter U. You press &lt;&lt;Q&gt;&gt;.

You are shown the letters ['I', 'O', 'C', 'X', 'A', 'Q']. You see the letter M. You press &lt;&lt;C&gt;&gt;.

You are shown the letters ['Z', 'C', 'W', 'I', 'J', 'O']. You see the letter C. You press &lt;&lt;Q&gt;&gt;.

You are shown the letters ['Q', 'M', 'F', 'V', 'P', 'E']. You see the letter W. You press &lt;&lt;C&gt;&gt;.

You are shown the letters ['W', 'F', 'U', 'M', 'B', 'Q']. You see the letter V. You press &lt;&lt;Q&gt;&gt;.

- You are shown the letters ['R', 'U', 'F', 'J', 'W', 'D']. You see the letter W. You press &lt;&lt;C&gt;&gt;.
- You are shown the letters ['X', 'U', 'R', 'Y', 'H', 'F']. You see the letter X. You press &lt;&lt;Q&gt;&gt;.
- You are shown the letters ['R', 'Q', 'M', 'X', 'V', 'U']. You see the letter W. You press &lt;&lt;C&gt;&gt;.
- You are shown the letters ['G', 'Q', 'M', 'N', 'R', 'O']. You see the letter V. You press &lt;&lt;Q&gt;&gt;.
- You are shown the letters ['T', 'P', 'Q', 'M', 'W', 'G']. You see the letter X. You press &lt;&lt;Q&gt;&gt;.
- You are shown the letters ['P', 'J', 'Q', 'S', 'D', 'T']. You see the letter J. You press &lt;&lt;Q&gt;&gt;.
- You are shown the letters ['J', 'R', 'H', 'Q', 'F', 'P']. You see the letter F. You press &lt;&lt;C&gt;&gt;.
- You are shown the letters ['B', 'V', 'J', 'G', 'R', 'H']. You see the letter R. You press &lt;&lt;Q&gt;&gt;.
- You are shown the letters ['X', 'J', 'V', 'L', 'B', 'D']. You see the letter B. You press &lt;&lt;Q&gt;&gt;.
- You are shown the letters ['N', 'M', 'J', 'C', 'V', 'X']. You see the letter C. You press &lt;&lt;Q&gt;&gt;.
- You are shown the letters ['N', 'T', 'J', 'R', 'M', 'W']. You see the letter C. You press &lt;&lt;Q&gt;&gt;.
- You are shown the letters ['N', 'T', 'J', 'E', 'I', 'D']. You see the letter N. You press &lt;&lt;Q&gt;&gt;.
- You are shown the letters ['J', 'T', 'N', 'K', 'C', 'B']. You see the letter T. You press &lt;&lt;C&gt;&gt;.
- You are shown the letters ['M', 'O', 'N', 'T', 'P', 'J']. You see the letter O. You press &lt;&lt;Q&gt;&gt;.
- You are shown the letters ['O', 'Q', 'W', 'U', 'M', 'N']. You see the letter Q. You press &lt;&lt;C&gt;&gt;.
- You are shown the letters ['Q', 'Z', 'Y', 'O', 'I', 'W']. You see the letter I. You press &lt;&lt;C&gt;&gt;.
- You are shown the letters ['Z', 'A', 'Y', 'F', 'Q', 'G']. You see the letter Q. You press &lt;&lt;C&gt;&gt;.
- You are shown the letters ['Z', 'M', 'Y', 'P', 'A', 'B']. You see the letter X. You press &lt;&lt;Q&gt;&gt;.
- You are shown the letters ['L', 'X', 'M', 'Z', 'Y', 'N']. You see the letter B. You press &lt;&lt;Q&gt;&gt;.
- You are shown the letters ['M', 'J', 'X', 'C', 'L', 'U']. You see the letter P. You press &lt;&lt;Q&gt;&gt;.
- You are shown the letters ['S', 'J', 'E', 'H', 'X', 'M']. You see the letter M. You press &lt;&lt;C&gt;&gt;.
- You are shown the letters ['F', 'I', 'E', 'A', 'J', 'S']. You see the letter X. You press &lt;&lt;Q&gt;&gt;.
- You are shown the letters ['D', 'U', 'I', 'M', 'O', 'T']. You see the letter Q. You press

&lt;&lt;Q&gt;&gt;.

You are shown the letters ['I', 'D', 'U', 'G', 'Q', 'W']. You see the letter B. You press &lt;&lt;Q&gt;&gt;.

You are shown the letters ['U', 'I', 'B', 'L', 'D', 'Z']. You see the letter W. You press &lt;&lt;Q&gt;&gt;.

You are shown the letters ['U', 'E', 'B', 'I', 'H', 'R']. You see the letter I. You press &lt;&lt;C&gt;&gt;.

You are shown the letters ['S', 'B', 'U', 'E', 'F', 'N']. You see the letter I. You press &lt;&lt;Q&gt;&gt;.

You are shown the letters ['Y', 'S', 'Q', 'U', 'B', 'A']. You see the letter Y. You press &lt;&lt;C&gt;&gt;.

You are shown the letters ['Q', 'V', 'Y', 'S', 'H', 'O']. You see the letter H. You press &lt;&lt;C&gt;&gt;.

You are shown the letters ['V', 'Z', 'P', 'D', 'Q', 'Y']. You see the letter H. You press &lt;&lt;C&gt;&gt;.

You are shown the letters ['Z', 'P', 'V', 'W', 'L', 'N']. You see the letter H. You press &lt;&lt;Q&gt;&gt;.

You are shown the letters ['U', 'S', 'Z', 'V', 'P', 'M']. You see the letter W. You press &lt;&lt;Q&gt;&gt;.

You are shown the letters ['U', 'Y', 'Z', 'S', 'C', 'G']. You see the letter W. You press &lt;&lt;Q&gt;&gt;.

## Horizon task

Data source: [26]

Number of experiments: 1

Number of participants: 26

Number of choices: 29120

## Example prompt:

You are participating in multiple games involving two slot machines, labeled I and H.

The two slot machines are different across different games.

Each time you choose a slot machine, you get some points.

You choose a slot machine by pressing the corresponding key.

Each slot machine tends to pay out about the same amount of points on average.

Your goal is to choose the slot machines that will give you the most points across the experiment.

The first 4 trials in each game are instructed trials where you will be told which slot machine to choose.

After these instructed trials, you will have the freedom to choose for either 1 or 6 trials.

Game 1. There are 10 trials in this game.

You are instructed to press I and get 73 points.

You are instructed to press H and get 91 points.

```
You are instructed to press I and get 68 points. You are instructed to press H and get 95 points. You press <<I>> and get 71 points. You press <<H>> and get 96 points. You press <<I>> and get 57 points. You press <<I>> and get 30 points. You press <<I>> and get 54 points. You press <<H>> and get 81 points. Game 2. There are 10 trials in this game. You are instructed to press I and get 38 points. You are instructed to press I and get 1 points. You are instructed to press I and get 18 points. You are instructed to press H and get 44 points. You press <<I>> and get 5 points. You press <<I>> and get 3 points. You press <<H>> and get 53 points. You press <<I>> and get 6 points. You press <<H>> and get 37 points. You press <<H>> and get 50 points. Game 3. There are 5 trials in this game. You are instructed to press H and get 24 points. You are instructed to press H and get 34 points. You are instructed to press I and get 68 points. You are instructed to press I and get 53 points. You press <<I>> and get 57 points. Game 4. There are 10 trials in this game. You are instructed to press H and get 53 points. You are instructed to press I and get 57 points. You are instructed to press H and get 45 points. You are instructed to press H and get 51 points. You press <<H>> and get 37 points. You press <<I>> and get 35 points. You press <<I>> and get 51 points. You press <<I>> and get 37 points. You press <<I>> and get 29 points. You press <<H>> and get 53 points. Game 5. There are 5 trials in this game. You are instructed to press H and get 46 points. You are instructed to press I and get 9 points. You are instructed to press H and get 38 points. You are instructed to press H and get 36 points.
```

You press &lt;&lt;H&gt;&gt; and get 37 points.

Game 6. There are 5 trials in this game.

You are instructed to press I and get 35 points.

You are instructed to press I and get 36 points.

You are instructed to press I and get 27 points.

You are instructed to press H and get 49 points.

You press &lt;&lt;H&gt;&gt; and get 41 points.

Game 7. There are 5 trials in this game.

You are instructed to press H and get 53 points.

You are instructed to press H and get 59 points.

You are instructed to press I and get 80 points.

You are instructed to press I and get 99 points.

You press &lt;&lt;H&gt;&gt; and get 54 points.

Game 8. There are 10 trials in this game.

You are instructed to press H and get 21 points.

You are instructed to press I and get 43 points.

You are instructed to press H and get 18 points.

You are instructed to press H and get 19 points.

You press &lt;&lt;H&gt;&gt; and get 26 points.

You press &lt;&lt;H&gt;&gt; and get 21 points.

You press &lt;&lt;I&gt;&gt; and get 47 points.

You press &lt;&lt;I&gt;&gt; and get 37 points.

You press &lt;&lt;I&gt;&gt; and get 37 points.

You press &lt;&lt;I&gt;&gt; and get 36 points.

Game 9. There are 5 trials in this game.

You are instructed to press H and get 47 points.

You are instructed to press H and get 41 points.

You are instructed to press I and get 40 points.

You are instructed to press I and get 35 points.

You press &lt;&lt;I&gt;&gt; and get 30 points.

Game 10. There are 5 trials in this game.

You are instructed to press I and get 69 points.

You are instructed to press I and get 69 points.

You are instructed to press H and get 65 points.

You are instructed to press I and get 68 points.

You press &lt;&lt;I&gt;&gt; and get 63 points.

Game 11. There are 10

## Gardening task

Data source: [27]

Number of experiments: 1

Number of participants: 320

Number of choices: 192000

## Example prompt:

You are going to plant trees in two different gardens labeled North and South. The trees look different from each other regarding their leafiness and branchiness.

There are 5 levels of leafiness (0, 1, 2, 3, 4) and 5 levels of branchiness (0, 1, 2, 3, 4). In each round, you get presented with a tree.

You can accept to plant the tree by pressing T and reject to plant it by pressing N. If you accept to plant the tree and your answer is correct, you will be rewarded with points, otherwise, you will lose some points.

If you reject to plant the tree, you will not be rewarded (0 points).

Your task is to learn which type of tree grows best in each garden.

During the training phase, there will be feedback on every trial about your decisions. During the testing phase, there will be no feedback for your decision.

You get a tree with level 3 of leafiness and level 0 of branchiness in the South garden. You press &lt;&lt;T&gt;&gt; and get -50 points. You would have gotten 0 points, had you rejected to plant the tree.

You get a tree with level 4 of leafiness and level 0 of branchiness in the North garden. You press &lt;&lt;T&gt;&gt; and get -50 points. You would have gotten 0 points, had you rejected to plant the tree.

You get a tree with level 1 of leafiness and level 1 of branchiness in the South garden. You press &lt;&lt;T&gt;&gt; and get -25 points. You would have gotten 0 points, had you rejected to plant the tree.

You get a tree with level 3 of leafiness and level 1 of branchiness in the North garden. You press &lt;&lt;T&gt;&gt; and get -25 points. You would have gotten 0 points, had you rejected to plant the tree.

You get a tree with level 0 of leafiness and level 4 of branchiness in the North garden. You press &lt;&lt;T&gt;&gt; and get 50 points. You would have gotten 0 points, had you rejected to plant the tree.

You get a tree with level 2 of leafiness and level 2 of branchiness in the North garden. You press &lt;&lt;N&gt;&gt; and get 0 points. You would have gotten 0 points, had you accepted to plant the tree.

You get a tree with level 0 of leafiness and level 2 of branchiness in the South garden. You press &lt;&lt;T&gt;&gt; and get 0 points. You would have gotten 0 points, had you rejected to plant the tree.

You get a tree with level 4 of leafiness and level 3 of branchiness in the North garden. You press &lt;&lt;N&gt;&gt; and get 0 points. You would have gotten -50 points, had you accepted to plant the tree.

You get a tree with level 1 of leafiness and level 1 of branchiness in the North garden.

You press &lt;&lt;T&gt;&gt; and get 25 points. You would have gotten 0 points, had you rejected to plant the tree.

You get a tree with level 2 of leafiness and level 1 of branchiness in the South garden. You press &lt;&lt;N&gt;&gt; and get 0 points. You would have gotten -25 points, had you accepted to plant the tree.

You get a tree with level 4 of leafiness and level 4 of branchiness in the North garden. You press &lt;&lt;N&gt;&gt; and get 0 points. You would have gotten -50 points, had you accepted to plant the tree.

You get a tree with level 1 of leafiness and level 3 of branchiness in the South garden. You press &lt;&lt;N&gt;&gt; and get 0 points. You would have gotten 25 points, had you accepted to plant the tree.

You get a tree with level 0 of leafiness and level 2 of branchiness in the South garden. You press &lt;&lt;N&gt;&gt; and get 0 points. You would have gotten 0 points, had you accepted to plant the tree.

You get a tree with level 4 of leafiness and level 1 of branchiness in the South garden. You press &lt;&lt;T&gt;&gt; and get -25 points. You would have gotten 0 points, had you rejected to plant the tree.

You get a tree with level 4 of leafiness and level 0 of branchiness in the North garden. You press &lt;&lt;N&gt;&gt; and get 0 points. You would have gotten -50 points, had you accepted to plant the tree.

You get a tree with level 1 of leafiness and level 1 of branchiness in the South garden. You press &lt;&lt;T&gt;&gt; and get -25 points. You would have gotten 0 points, had you rejected to plant the tree.

You get a tree with level 0 of leafiness and level 2 of branchiness in the South garden. You press &lt;&lt;N&gt;&gt; and get 0 points. You would have gotten 0 points, had you accepted to plant the tree.

You get a

## Columbia card task

Data source: [28]

Number of experiments: 1

Number of participants: 1368

Number of choices: 613299

## Example prompt:

You will play a games with 84 rounds.

In each round, you will be presented with 32 face-down cards.

Every card is either a gain card or a loss card.

If you turn over a gain card, the gain amount of that card (between 10 and 600 points) will be added to your current game score.

If you turn over a loss card, the loss amount of that card (between 25 and 750 points) will be subtracted from your game score.

In different rounds, between 1 and 28 cards are loss cards.

Loss and gain amounts also differ between rounds.

```
You may keep turning over cards as long as you keep encountering gain cards. You may also stop the round at any point and claim your current payout. If you encounter a loss card, the round ends immediately. Your gains and losses will be summed up to give you your final score for each round. Press E to turn a card over, or C to stop the round and claim your current payout. Round 1: You will be awarded 150 points for turning over a gain card. You will lose 75 points for turning over a loss card. There are 20 loss cards in this round. You press <<E>> and turn over a loss card. Your current score is -75. The round has now ended because you encountered a loss card. Your final score for this round is -75. Round 2: You will be awarded 50 points for turning over a gain card. You will lose 100 points for turning over a loss card. There are 1 loss cards in this round. You press <<E>> and turn over a gain card. Your current score is 50. You press <<E>> and turn over a gain card. Your current score is 100. You press <<E>> and turn over a gain card. Your current score is 150. You press <<E>> and turn over a gain card. Your current score is 200. You press <<E>> and turn over a loss card. Your current score is 100. The round has now ended because you encountered a loss card. Your final score for this round is 100. Round 3: You will be awarded 200 points for turning over a gain card. You will lose 100 points for turning over a loss card. There are 10 loss cards in this round. You press <<E>> and turn over a gain card. Your current score is 200. You press <<E>> and turn over a gain card. Your current score is 400. You press <<E>> and turn over a gain card. Your current score is 600. You press <<C>> and claim your payout. Your final score for this round is 600. Round 4: You will be awarded 200 points for turning over a gain card. You will lose 50 points for turning over a loss card. There are 28 loss cards in this round. You press <<C>> and claim your payout. Your final score for this round is 0. Round 5: You will be awarded 20 points for turning over a gain card.
```

```
You will lose 750 points for turning over a loss card. There are 1 loss cards in this round. You press <<E>> and turn over a gain card. Your current score is 20. You press <<E>> and turn over a gain card. Your current score is 40. You press <<E>> and turn over a gain card. Your current score is 60. You press <<E>> and turn over a gain card. Your current score is 80. You press <<E>> and turn over a gain card. Your current score is 100. You press <<C>> and claim your payout.
```

## Your final score for this round is 100. Round 6: You will be awarded 300 points for turning over a gain card. You will lose 100 points for turning over a loss card. There are 16 loss cards in this round. You press &lt;&lt;E&gt;&gt; and turn over a loss card. Your current score is -100. The round has now ended because you encountered a loss card. Your final score for this round is -100. Round 7: You will be awarded 10 points for turning over a gain card. You will lose 500 points for turning over a loss card. There are 3 loss cards in this round. You press &lt;&lt;E&gt;&gt; and turn over a gain card. Your current score is 10. You press &lt;&lt;E&gt;&gt; and turn over a gain card. Your current score is 20. You press &lt;&lt;E&gt;&gt; and turn over a gain card. Your current score is 30. You press &lt;&lt;E&gt;&gt; and turn over a gain card. Your current score is 40. You press &lt;&lt;C&gt;&gt; and claim your payout. Your final score for this round is 40. Round 8: You will be awarded 10 points for turning over a gain card. You will lose 250 points for turning over a loss Balloon analog risk task Data source: [28] Number of experiments: 1 Number of participants: 1331 Number of choices: 1496974 Example prompt: Throughout the task, you will be presented with balloons, one at a time. In each step, you can choose to pump up the balloon by pressing H and you will

accumulate 1 point for each pump.

At any point, you can stop pumping up the balloon by pressing W and you will collect your accumulated points.

You will repeat this procedure on multiple different balloons.

It is your choice to determine how much to pump up the balloon, but be aware that at some point the balloon will explode.

If the balloon explodes before you collect your accumulated points, then you move on to the next balloon and the points are lost.

## Balloon 1:

```
You press <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>>. The balloon was inflated too much and explodes.
```

## Balloon 2:

```
You press <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<W>>. You stop inflating the balloon and get 60 points.
```

## Balloon 3:

```
You press <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>>. The balloon was inflated too much and explodes.
```

## Balloon 4:

```
You press <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>>. The balloon was inflated too much and explodes.
```

## Balloon 5:

```
You press <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>>. The balloon was inflated too much and explodes.
```

## Balloon 6:

```
You press <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>>
```

&lt;&lt;H&gt;&gt; &lt;&lt;W&gt;&gt;. You stop inflating the balloon and get 18 points.

## Balloon 7:

```
You press <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>>. The balloon was inflated too much and explodes. Balloon 8: You press <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<W>>. You stop inflating the balloon and get 23 points. Balloon 9: You press <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<W>>. You stop inflating the balloon and get 26 points. Balloon 10: You press <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<W>>. You stop inflating the balloon and get 35 points. Balloon 11: You press <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<W>>. You stop inflating the balloon and get 35 points. Balloon 12: You press <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<W>>. You stop inflating the balloon and get 50 points. Balloon 13: You press <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>>
```

```
<<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>> <<H>>
```

## Experiential-symbolic task

Data source: [29]

Number of experiments: 4

Number of participants: 346

Number of choices: 70608

## Example prompt:

This experiment is composed of three parts.

In each round of the first part, you have to choose between one of two options represented by letters.

In a given pair, one option is, on average, more advantageous compared to the other.

You can win or lose the following outcomes: 1.0 points and -1.0 points.

In the second part, there will be two types of options.

The first type of option is represented by the letters you already encountered during the previous part.

Note that the options maintain the same odds of winning or losing a point as in the first part.

The second type of option is represented by an explicit description of the odds of winning or losing a point.

In each round of the third part, you will be presented with the options you met in the first and the second part.

This is the occasion to test your knowledge of each options's outcome.

You will be asked to indicate (in percentages), what are the odds that a given option makes you win a point.

You can choose an option by pressing its corresponding key.

Your goal for the first two parts is to maximize the amount of received points.

Your goal in the third part is to guess as accurately as possible.

You can choose between option Q and option L. You press &lt;&lt;Q&gt;&gt; and get 1.0 points. You would have gotten 1.0 points had you chosen option L instead.

You can choose between option Z and option H. You press &lt;&lt;Z&gt;&gt; and get 1.0 points. You would have gotten 1.0 points had you chosen option H instead.

You can choose between option D and option X. You press &lt;&lt;X&gt;&gt; and get 1.0 points. You would have gotten -1.0 points had you chosen option D instead.

You can choose between option U and option C. You press &lt;&lt;C&gt;&gt; and get 1.0 points. You would have gotten 1.0 points had you chosen option U instead.

You can choose between option U and option C. You press &lt;&lt;C&gt;&gt; and get -1.0 points. You would have gotten 1.0 points had you chosen option U instead.

You can choose between option D and option X. You press &lt;&lt;X&gt;&gt; and get 1.0

```
points. You would have gotten 1.0 points had you chosen option D instead. You can choose between option Z and option H. You press <<Z>> and get 1.0 points. You would have gotten -1.0 points had you chosen option H instead. You can choose between option Z and option H. You press <<Z>> and get 1.0 points. You would have gotten 1.0 points had you chosen option H instead. You can choose between option D and option X. You press <<X>> and get -1.0 points. You would have gotten 1.0 points had you chosen option D instead. You can choose between option D and option X. You press <<D>> and get 1.0 points. You would have gotten 1.0 points had you chosen option X instead. You can choose between option Q and option L. You press <<Q>> and get 1.0 points. You would have gotten -1.0 points had you chosen option L instead. You can choose between option D and option X. You press <<X>> and get -1.0 points. You would have gotten 1.0 points had you chosen option D instead. You can choose between option D and option X. You press <<D>> and get 1.0 points. You would have gotten -1.0 points had you chosen option X instead. You can choose between option Q and option L. You press <<Q>> and get -1.0 points. You would have gotten -1.0 points had you chosen option L instead. You can choose between option Q and option L. You press <<L>> and get -1.0 points. You would have gotten 1.0 points had you chosen option Q instead. You can choose between option Q and option L. You press <<Q>> and get 1.0 points. You would have gotten -1.0 points had you chosen option L instead. You can choose between option Q and option L. You press <<Q>> and get -1.0 points. You would have gotten 1.0 points had you chosen option L instead. You can choose between option U and option C. You press <<C>> and get -1.0 points. You would have gotten 1.0 points had you chosen option U instead. You can choose between option U and option C. You press <<C>> and get -1.0 points. You would have gotten -1.0 points had you chosen option U instead.
```

You can choose between option Q and option L. You press &lt;&lt;Q&gt;&gt; and get 1.0 poi

## Two-armed bandit

Data source: [30]

Number of experiments: 2

Number of participants: 80

Number of choices: 16000

## Example prompt:

In this task, you have to repeatedly choose between two slot machines labeled U and P.

You can choose a slot machine by pressing its corresponding key.

When you select one of the machines, you will win or lose points.

Machine U will not always give you the same points when you select it again, but machine P will always give 0 points when you select it.

Your goal is to choose the slot machines that will give you the most points.

You will receive feedback about the outcome after making a choice.

You will play 20 games in total, each with a different pair of slot machines. Each game will consist of 10 trials.

```
Game 1: You press <<U>> and get -1 points. You press <<U>> and get 0 points. You press <<U>> and get 2 points. You press <<U>> and get -1 points. You press <<U>> and get 1 points. You press <<U>> and get -1 points. You press <<U>> and get -1 points. You press <<U>> and get -1 points. You press <<U>> and get 1 points. You press <<U>> and get 1 points. Game 2: You press <<U>> and get -1 points. You press <<U>> and get -1 points. You press <<U>> and get -2 points. You press <<U>> and get 0 points. You press <<U>> and get -1 points. You press <<P>> and get 0 points. You press <<P>> and get 0 points. You press <<P>> and get 0 points. You press <<P>> and get 0 points. You press <<P>> and get 0 points. Game 3: You press <<U>> and get -2 points. You press <<U>> and get -1 points. You press <<P>> and get 0 points. You press <<P>> and get 0 points. You press <<P>> and get 0 points. You press <<U>> and get -4 points. You press <<P>> and get 0 points. You press <<P>> and get 0 points. You press <<P>> and get 0 points. You press <<P>> and get 0 points. Game 4: You press <<U>> and get 2 points. You press <<U>> and get 0 points. You press <<U>> and get 2 points. You press <<U>> and get 1 points. You press <<U>> and get 2 points.
```

```
You press <<U>> and get -1 points. You press <<U>> and get 0 points. You press <<U>> and get 2 points. You press <<U>> and get 1 points. You press <<U>> and get 0 points. Game 5: You press <<U>> and get 0 points. You press <<U>> and get 1 points. You press <<U>> and get 1 points. You press <<U>> and get 0 points. You press <<U>> and get 2 points. You press <<U>> and get 1 points. You press <<U>> and get 2 points. You press <<U>> and get 1 points. You press <<U>> and get 2 points. You press <<U>> and get 1 points. Game 6: You press <<U>> and get 3 points. You press <<U>> and get 2 points. You press <<U>> and get 0 points. You press <<U>> and get 2 points. You press <<U>> and get 2 points. You press <<U>> and get 2 points. You press <<U>> and get 1 points. You press <<U>> and get 3 points. You press <<U>> and get 2 points. You press <<U>> and get 1 points. Game 7: You press <<U>> and get -1 points. You press <<U>> and get -3 points. You press <<P>> and get 0 points. You press <<P>> and get 0 points. You press <<P>> and get 0 points. You press <<P>> and get 0 points. You press <<P>> and get 0 points. You press <<P>> and get 0 points. You press <<P>> and get 0 points. You press <<P>> and get 0 points. Game 8: You press <<U>> and get 0 points. You press <<U>> and get -1 points.
```

```
You press <<P>> and get 0 points. You press <<P>> and get 0 points. You press <<P>> and get 0 points. You press <<P>> and get 0 points. You press <<P>> and get 0 points. You press <<P>> and get 0 points. You press <<P>> and get 0 points. You press <<P>> and get 0 points. Game 9: You press <<U>> and get 2 points. You press <<U>> and get 3 points. You press <<U>> and get 4 points. You press <<U>> and get 1 points. You press <<U>> and get 1 points. You press <<U>> and get 2 points. You press <<U>> and get 2 points. You press <<U>> and get 2 points. You press <<U>> and get -1 points. You press <<U>> and get 2 points. Game 10: You press <<U>> and get 1 points. You press <<U>> and get 0 points. You press <<U>> and get 0 points. You press <<U>> and get 1 points. You press <<U>> and get -1 points. You press <<U>> and get -2 points. You press <<U>> and get 1 points. You press <<U>> and get 2 points. You press <<U>> and get 1 points. You pr
```

## Conditional associative learning

```
Data source: [31] Number of experiments: 1 Number of participants: 74 Number of choices: 40539
```

## Example prompt:

You are presented with a series of stimuli, each associated with one of three possible responses.

Your goal is to learn which response is the correct one for each stimulus.

When a stimulus is presented, you can press one of three keys to respond.

The three responses available are S, F, and A.

After your response, you will receive feedback: 1 point for a correct response, or 0 points for an incorrect response.

The correct response for one stimulus does not inform you about the correct response for another stimulus.

You will play 13 games, each with a different mapping from stimuli to responses.

## Game 1:

```
There are 6 different stimuli. You see stimulus 1. You press <<S>> and get 0 points. You see stimulus 0. You press <<F>> and get 0 points. You see stimulus 4. You press <<A>> and get 1 points. You see stimulus 5. You press <<S>> and get 0 points. You see stimulus 3. You press <<F>> and get 1 points. You see stimulus 3. You press <<F>> and get 1 points. You see stimulus 4. You press <<A>> and get 1 points. You see stimulus 2. You press <<S>> and get 0 points. You see stimulus 1. You press <<S>> and get 0 points. You see stimulus 5. You press <<S>> and get 0 points. You see stimulus 2. You press <<S>> and get 0 points. You see stimulus 0. You press <<A>> and get 0 points. You see stimulus 3. You press <<F>> and get 1 points. You see stimulus 3. You press <<F>> and get 1 points. You see stimulus 5. You press <<A>> and get 1 points. You see stimulus 1. You press <<A>> and get 0 points. You see stimulus 4. You press <<A>> and get 1 points. You see stimulus 1. You press <<S>> and get 0 points. You see stimulus 0. You press <<S>> and get 1 points. You see stimulus 5. You press <<S>> and get 0 points. You see stimulus 4. You press <<A>> and get 1 points. You see stimulus 2. You press <<S>> and get 0 points. You see stimulus 0. You press <<S>> and get 1 points. You see stimulus 2. You press <<S>> and get 0 points. You see stimulus 3. You press <<F>> and get 1 points. You see stimulus 1. You press <<A>> and get 0 points. You see stimulus 5. You press <<A>> and get 1 points. You see stimulus 4. You press <<A>> and get 1 points. You see stimulus 0. You press <<S>> and get 1 points. You see stimulus 1. You press <<S>> and get 0 points. You see stimulus 3. You press <<F>> and get 1 points. You see stimulus 4. You press <<A>> and get 1 points. You see stimulus 0. You press <<S>> and get 1 points. You see stimulus 2. You press <<S>> and get 0 points. You see stimulus 2. You press <<S>> and get 0 points. You see stimulus 3. You press <<F>> and get 1 points.
```

```
You see stimulus 5. You press <<S>> and get 0 points. You see stimulus 1. You press <<A>> and get 0 points. You see stimulus 0. You press <<F>> and get 0 points. You see stimulus 5. You press <<F>> and get 0 points. You see stimulus 4. You press <<A>> and get 1 points. You see stimulus 4. You press <<A>> and get 1 points. You see stimulus 1. You press <<A>> and get 0 points. You see stimulus 3. You press <<F>> and get 1 points. You see stimulus 2. You press <<F>> and get 1 points. You see stimulus 2. You press <<F>> and get 1 points. You see stimulus 3. You press <<F>> and get 1 points. You see stimulus 0. You press <<F>> and get 0 points. You see stimulus 1. You press <<F>> and get 1 points. You see stimulus 5. You press <<F>> and get 0 points. You see stimulus 0. You press <<F>> and get 0 points. You see stimulus 5. You press <<F>> and get 0 points. You see stimulus 4. You press <<A>> and get 1 points. You see stimulus 2. You press <<A>> and get 0 points. You see stimulus 0. You press <<F>> and get 0 points. You see stimulus 0. You press <<F>> and get 0 points. You see stimulus 1. You press <<A>> and get 0 points. You see stimulus 2. You press <<A>> and get 0 points. You see stimulus 1. You press <<A>> and get 0 points. You see stimulus 4. You press <<A>> and get 1 points. You see stimulus 4. You press <<A>> and get 1 points. You see stimulus 2. You press <<S>> and get 0 points. You see stimulus 5. You press <<S>> and get 0 points. You see stimulus 5. You press <<F>> and get 0 points.
```

## THINGS odd-one-out

Data source: [32]

Number of experiments: 1

Number of participants: 11122

Number of choices: 2611240

## Example prompt:

You will be presented with triplets of objects, which will be assigned to the keys B, J, and K.

In each trial, please indicate which object you think is the odd one out by pressing the corresponding key.

In other words, please choose the object that is the least similar to the other two.

B: prune, J: nail polish, and K: diskette. You press &lt;&lt;K&gt;&gt;.

```
B: ladle, J: water bottle, and K: pug. You press <<K>>.
```

```
B: punch, J: hair, and K: lollipop. You press <<J>>. B: oar, J: mug, and K: macaroni. You press <<B>>. B: towel, J: hot tub, and K: mallet. You press <<K>>. B: train set, J: hot-water bottle, and K: treasure. You press <<J>>. B: shutter, J: cleaver, and K: toe. You press <<K>>. B: straw, J: sweeper, and K: baton. You press <<J>>. B: footprint, J: beehive, and K: skunk. You press <<B>>. B: cash machine, J: thermostat, and K: mandolin. You press <<K>>. B: orange, J: throne, and K: stir fry. You press <<J>>. B: boy, J: burrito, and K: microscope. You press <<J>>. B: pheasant, J: sponge, and K: orchid. You press <<J>>. B: forklift, J: clipper, and K: hip. You press <<J>>. B: candelabra, J: beard, and K: glue. You press <<J>>. B: raccoon, J: hammer, and K: roulette wheel. You press <<B>>. B: wing, J: beanie, and K: girl. You press <<B>>. B: piggy bank, J: footrest, and K: sandal. You press <<B>>. B: knee, J: cornhusk, and K: tuning fork. You press <<B>>. B: anklet, J: bedpost, and K: ice cube. You press <<B>>. B: mannequin, J: stove, and K: coin. You press <<K>>. B: tortellini, J: cantaloupe, and K: sequin. You press <<K>>. B: coffee filter, J: fingerprint, and K: rose. You press <<B>>. B: porcupine, J: christmas tree, and K: corkscrew. You press <<B>>. B: freezer, J: coat rack, and K: puffin. You press <<K>>. B: maggot, J: mouth, and K: stockings. You press <<B>>. B: soap, J: hot-water bottle, and K: knitting needle. You press <<K>>. B: mosquito net, J: baklava, and K: beanbag. You press <<J>>. B: skewer, J: baklava, and K: propeller. You press <<K>>. B: nail polish, J: goose, and K: pizza. You press <<J>>. B: face mask, J: cinnamon, and K: toilet paper. You press <<B>>. B: bag, J: eel, and K: trampoline. You press <<J>>. B: lightbulb, J: moose, and K: curling iron. You press <<J>>. B: dumbwaiter, J: jigsaw puzzle, and K: lamb. You press <<K>>. B: eyeliner, J: shopping basket, and K: flipper. You press <<K>>. B: bowtie, J: wooden leg, and K: kangaroo. You press <<K>>. B: puffin, J: wire cutters, and K: battery. You press <<B>>. B: toilet, J: rack, and K: star fruit. You press <<K>>. B: stingray, J: cork, and K: fire pit. You press <<B>>. B: bun, J: snow, and K: tinsel. You press <<J>>. B: almond, J: trailer, and K: paper. You press <<B>>. B: anteater, J: chalice, and K: wedge. You press <<B>>. B: scone, J: pie, and K: ant. You press <<K>>. B: heater, J: aircraft carrier, and K: joystick. You press <<B>>. B: comic book, J: playing card, and K: organ. You press <<K>>. B: flag, J: measuring cup, and K: strawberry. You press <<B>>.
```

- B: bunkbed, J: tractor, and K: windshield. You press &lt;&lt;B&gt;&gt;.

B: aircraft carrier, J: prism, and K: turban. You press &lt;&lt;K&gt;&gt;. B: egg, J: scrambled egg, and K: doorknocker. You press &lt;&lt;K&gt;&gt;. B: microscope, J: stained glass, and K: strainer. You press &lt;&lt;J&gt;&gt;. B: polygraph, J: hairdryer, and K: harness. You press &lt;&lt;J&gt;&gt;. B: chip, J: iguana, and K: hedge. You press &lt;&lt;B&gt;&gt;. B: tick, J: binder, and K: shoelace. You press &lt;&lt;B&gt;&gt;. B: nut, J: yogurt, and K: jug. You press &lt;&lt;K&gt;&gt;. B: hairpin, J: giraffe, and K: fur coat. You press &lt;&lt;B&gt;&gt;. B: lasagna, J: statue, and K: bookshelf. You press &lt;&lt;B&gt;&gt;. B: grill, J: catapult, and K: sonogram. You press &lt;&lt;K&gt;&gt;. B: fondue, J: pill, and K: firewood. You press &lt;&lt;K&gt;&gt;. B: sunroof, J: onion, and K: flan. You press &lt;&lt;B&gt;&gt;.

B: wreck, J: bungee, and K: cockroach. You press &lt;&lt;K&gt;&gt;.

## Multi-attribute decision-making

```
Data source: [1] Number of experiments: 1 Number of participants: 73 Number of choices: 7008
```

## Example prompt:

You are repeatedly presented with two options, labeled A and R.

Each option represents a fictitious product and you have to infer which product is superior in terms of quality.

You select a product by pressing the corresponding key.

For each decision, you are provided with four expert ratings (with 1 representing a positive and 0 representing a negative rating).

The four experts differ in their validity.

The ratings of experts are given in descending order of their validity (having validities of 90%, 80%, 70%, and 60%).

```
Product A ratings: [0 1 1 1]. Product R ratings: [1 0 0 1]. You press <<A>>. Product A ratings: [1 1 1 1]. Product R ratings: [0 0 1 1]. You press <<A>>. Product A ratings: [1 0 0 0]. Product R ratings: [0 0 0 1]. You press <<A>>. Product A ratings: [1 1 1 0]. Product R ratings: [0 0 1 0]. You press <<A>>. Product A ratings: [0 1 1 1]. Product R ratings: [1 1 1 0]. You press <<R>>. Product A ratings: [0 1 0 1]. Product R ratings: [1 1 0 0]. You press <<R>>. Product A ratings: [0 0 1 1]. Product R ratings: [1 0 1 0]. You press <<R>>. Product A ratings: [1 0 0 1]. Product R ratings: [0 1 1 1]. You press <<R>>. Product A ratings: [0 1 1 1]. Product R ratings: [1 0 0 1]. You press <<A>>. Product A ratings: [0 1 1 1]. Product R ratings: [1 1 1 0]. You press <<R>>. Product A ratings: [1 0 1 0]. Product R ratings: [0 0 1 1]. You press <<A>>. Product A ratings: [1 1 0 0]. Product R ratings: [0 1 0 1]. You press <<A>>. Product A ratings: [1 0 0 0]. Product R ratings: [0 1 1 0]. You press <<R>>.
```

```
Product A ratings: [1 0 0 1]. Product R ratings: [0 1 1 1]. You press <<R>>. Product A ratings: [1 1 1 1]. Product R ratings: [0 0 1 1]. You press <<A>>. Product A ratings: [1 0 0 0]. Product R ratings: [0 0 0 1]. You press <<A>>. Product A ratings: [1 1 0 1]. Product R ratings: [0 0 0 1]. You press <<A>>. Product A ratings: [1 0 0 1]. Product R ratings: [0 1 1 1]. You press <<R>>. Product A ratings: [0 1 0 1]. Product R ratings: [1 1 0 0]. You press <<R>>. Product A ratings: [1 0 1 1]. Product R ratings: [0 0 0 0]. You press <<A>>. Product A ratings: [1 0 0 0]. Product R ratings: [0 0 0 1]. You press <<A>>. Product A ratings: [0 1 1 1]. Product R ratings: [1 1 1 0]. You press <<R>>. Product A ratings: [0 1 1 0]. Product R ratings: [1 0 0 0]. You press <<A>>. Product A ratings: [1 1 1 0]. Product R ratings: [0 1 1 1]. You press <<A>>. Product A ratings: [0 0 0 0]. Product R ratings: [1 1 0 0]. You press <<R>>. Product A ratings: [0 1 1 1]. Product R ratings: [1 0 0 1]. You press <<A>>. Product A ratings: [0 0 0 0]. Product R ratings: [1 1 0 0]. You press <<R>>. Product A ratings: [1 0 0 0]. Product R ratings: [0 1 1 0]. You press <<R>>. Product A ratings: [0 0 0 0]. Product R ratings: [1 1 0 0]. You press <<R>>. Product A ratings: [0 1 1 1]. Product R ratings: [1 0 0 1]. You press <<A>>. Product A ratings: [0 0 0 1]. Product R ratings: [1 0 0 0]. You press <<R>>. Product A ratings: [1 0 0 0]. Product R ratings: [0 1 1 0]. You press <<R>>. Product A ratings: [1 1 0 0]. Product R ratings: [0 0 0 0]. You press <<A>>. Product A ratings: [1 1 0 0]. Product R ratings: [0 1 0 1]. You press <<A>>. Product A ratings: [1 0 0 0]. Product R ratings: [0 0 0 1]. You press <<A>>. Product A ratings: [0 0 0 1]. Product R ratings: [1 0 0 0]. You press <<R>>. Product A ratings: [1 0 1 0]. Product R ratings: [0 0 1 1]. You press <<A>>. Product A ratings: [1 1 0 0]. Product R ratings: [0 0 0 0]. You press <<A>>. Product A ratings: [0 0 1 1]. Product R ratings: [1 0 1 0]. You press <<R>>. Product A ratings: [1 0 0 0]. Product R ratings: [0 1 1 0]. You press <<R>>. Product A ratings: [1 1 1 0]. Product R ratings: [0 0 1 0]. You press <<A>>. Product A ratings: [1 0 0 1]. Product R ratings: [0 1 1 1]. You press <<R>>. Product A ratings: [1 0 1 0]. Product R ratings: [0 0 1 1]. You press <<A>>. Product A ratings: [0 1 1 0]. Product R ratings: [1 0 0 0]. You press <<A>>. Product A ratings: [1 1 0 0]. Product R ratings: [0 1 0 1]. You press <<A>>. Product A ratings: [0 1 1 0]. Product R ratings: [1 0 0 0]. You press <<A>>. Product A ratings: [1 0 0 0
```

## Grammar judgement

```
Data source: [33] Number of experiments: 1 Number of participants: 3192 Number of choices: 89376
```

## Example prompt:

You're about to answer a set of 20 questions about grammar. How many of the 20 questions do you think you will answer correctly?

You say &lt;&lt;4&gt;&gt;.

Compared to other participants in this study, how well do you think you will do? Marking 90% means you will do better than 90% of participants, marking 10% means you will do better than only 10%, and marking 50% means that you will perform better than half of the participants.

You say &lt;&lt;50&gt;&gt;%. On a scale of 0 to 10, how difficult is recognizing correct grammar for the average participant? You say &lt;&lt;6&gt;&gt;. On a scale of 0 to 10, how difficult is recognizing correct grammar for you? You say &lt;&lt;6&gt;&gt;. You will now see twenty questions. In each question, some part of each sentence is in square brackets. Five choices for rephrasing that part follow each sentence; one choice repeats the original, and the other four are different. Your task is to use the buttons J, E, V, H, and G to select the grammatically correct choice. Q1. The school-age child faces a formidable task when during the first few years of classroom experiences [he or she is expected to master the printed form of language.] The choices are: V: he or she expects to master the printed form of language. E: he or she is expected to master the printed form of language. H: he or she faces expectations of mastering the printed form of language. J: mastery of the printed form of language is expected of him or her. G: mastery of print is expected by his or her teacher. You press &lt;&lt;E&gt;&gt;. Q2. He came to the United States as a young [man, he found] a job as a coal miner. The choices are: H: man, he found G: man and found E: man and there he was able to find V: man and then finding J: man and had found You press &lt;&lt;H&gt;&gt;. Q3. To a large degree, [poetry, along with all the other arts, is] a form of imitation.

The choices are:

E: poetry, along with all the other arts, is

V: poetry along with all the other arts is

J: poetry, along with all the other arts, are

G: poetry, and other arts, is

H: poetry and art are You press &lt;&lt;V&gt;&gt;.

Q4. Delegates to the political convention found [difficulty to choose] a candidate from among the few nominated.

The choices are:

E: difficulty to choose

G: it difficult in making the choice of

V: choosing difficult when selecting

J: making a choice difficult in selecting

```
H: it difficult to choose You press <<E>>.
```

Q5. Reading in any language can be viewed as a developmental task much the same as learning to walk, to cross the street independently, to care for one's possessions, or [accepting responsibility for one's own decisions.]

The choices are:

J: accepting responsibility for one's own decisions.

V: accepting one's own decisions responsibly.

H: to accept responsibility for one's own decisions.

E: accepting responsibility and making one's own decisions.

G: to make one's own decisions.

You press &lt;&lt;G&gt;&gt;.

Q6. Sea forests of giant kelp, which fringe only one coastline in the Northern Hemisphere, [is native to shores] throughout the Southern Hemisphere.

The choices are:

E: is native to shores

V: is native to most shores

G: are native only in shores

J: are native

H: are native to shores

You press &lt;&lt;J&gt;&gt;.

Q7. Taking an occasional respite between chapters or assignments is more desirable [than a long, continuous period of study.

The choices are:

E: than a long, continuous period of study.

G: than a period of long, continuous study.

V: than a long period of continuous study.

J: than studying for a long, continuous period.

H: than a study period long and continuous.

You press &lt;&lt;V&gt;&gt;.

Q8. Like so many characters in Russian fiction, [Crime and Punishment exhibits] a behavior so foreign to the American temperament that many readers find the story rather incredible.

```
The choices are: J: Crime and Punishment exhibits H: those in Crime and Punishment exhibit G: those in Crime and Punishment exhibits V: often exhibiting E: characterized by You press <<G>>.
```

Q9. Don Quixote provides a cross section of Spanish life, thought, and [portrays the feelings of many Spaniards] at the end of the chivalric age.

The choices are:

H: portrays th

## Two-step task

Data source: [34]

Number of experiments: 2

Number of participants: 181

Number of choices: 52861

## Example prompt:

Each day you will either be presented with spaceships P and F or with spaceships Z and J.

These spaceships will take you to two different planets L and Q.

You can take a spaceship by pressing the corresponding key.

Each planet has one alien on it and each alien has its own space treasure mine.

When you arrive at a planet, you will ask the alien for space treasure from its mine.

When you ask the alien, you will find out whether you got space treasure.

However, sometimes the alien will not bring up any treasure.

The quality of each alien's mine will change during the game.

Before you choose a spaceship, you will be told whether there is a treasure multiplier.

If there is a treasure multiplier, you will receive 5 times the amount of treasure you will find.

Your goal is to get as much treasure as possible over the next 200 days.

There is no treasure multiplier. You are presented with spaceships F and P. You press &lt;&lt;P&gt;&gt;. You end up on planet L. You find 7 pieces of space treasure. You receive 7 pieces of space treasure.

There is no treasure multiplier. You are presented with spaceships F and P. You press &lt;&lt;F&gt;&gt;. You end up on planet Q. You find 0 pieces of space treasure. You receive 0 pieces of space treasure.

There is no treasure multiplier. You are presented with spaceships J and Z. You press &lt;&lt;Z&gt;&gt;. You end up on planet L. You find 7 pieces of space treasure. You receive 7 pieces of space treasure.

There is no treasure multiplier. You are presented with spaceships Z and J. You press

&lt;&lt;Z&gt;&gt;. You end up on planet L. You find 7 pieces of space treasure. You receive 7 pieces of space treasure.

There is no treasure multiplier. You are presented with spaceships Z and J. You press &lt;&lt;Z&gt;&gt;. You end up on planet L. You find 8 pieces of space treasure. You receive 8 pieces of space treasure.

There is a treasure multiplier. You are presented with spaceships F and P. You press &lt;&lt;P&gt;&gt;. You end up on planet L. You find 6 pieces of space treasure. You receive 30 pieces of space treasure.

There is a treasure multiplier. You are presented with spaceships F and P. You press &lt;&lt;P&gt;&gt;. You end up on planet L. You find 8 pieces of space treasure. You receive 40 pieces of space treasure.

There is no treasure multiplier. You are presented with spaceships J and Z. You press &lt;&lt;Z&gt;&gt;. You end up on planet L. You find 9 pieces of space treasure. You receive 9 pieces of space treasure.

There is no treasure multiplier. You are presented with spaceships P and F. You press &lt;&lt;P&gt;&gt;. You end up on planet L. You find 8 pieces of space treasure. You receive 8 pieces of space treasure.

There is a treasure multiplier. You are presented with spaceships J and Z. You press &lt;&lt;Z&gt;&gt;. You end up on planet L. You find 9 pieces of space treasure. You receive 45 pieces of space treasure.

There is a treasure multiplier. You are presented with spaceships P and F. You press &lt;&lt;P&gt;&gt;. You end up on planet L. You find 9 pieces of space treasure. You receive 45 pieces of space treasure.

There is no treasure multiplier. You are presented with spaceships J and Z. You press &lt;&lt;Z&gt;&gt;. You end up on planet L. You find 8 pieces of space treasure. You receive 8 pieces of space treasure.

There is a treasure multiplier. You are presented with spaceships J and Z. You press &lt;&lt;Z&gt;&gt;. You end up on planet L. You find 9 pieces of space treasure. You receive 45 pieces of space treasure.

There is no treasure multiplier. You are presented with spaceships Z and J. You press &lt;&lt;Z&gt;&gt;. You end up on planet L. You find 5 pieces of space treasure. You receive 5 pieces of space treasure.

There is no treasure multiplier. You are presented with spaceships Z and J. You press &lt;&lt;Z&gt;&gt;. You end up on planet L. You find 6 pieces of space treasure. You receive 6 pieces of space treasure.

There is a treasure multiplier. You are presented with spaceships P and F. You press &lt;&lt;P&gt;&gt;. You end up on planet L. You find 8 pieces of space treasure. You receive 40 pieces of space treasure.

There is no treasure multiplier. You are presented with spaceships J and Z. You press &lt;&lt;Z&gt;&gt;. You end up on planet L. You find 7 pieces of space treasure.

## Two-step task

Data source: [35]

Number of experiments: 2

Number of participants: 367

Number of choices: 67041

## Example prompt:

Each day you will either be presented with spaceships G and S or with spaceships T and N.

These spaceships will take you to two different planets R and Z.

You can take a spaceship by pressing the corresponding key.

Each planet has one alien on it and each alien has its own space treasure mine.

When you arrive at a planet, you will ask the alien for space treasure from its mine.

When you ask the alien, you will find out whether you got space treasure.

However, sometimes the alien's mine will dig up antimatter.

Antimatter is bad because each piece will destroy a piece of space treasure, reducing the total amount of treasure that you have.

The quality of each alien's mine will change during the game.

Your goal is to get as much treasure and as little antimatter as possible over the next 125 days.

You are presented with spaceships N and T. You press &lt;&lt;T&gt;&gt;. You end up on planet R. You find 1 pieces of antimatter.

You are presented with spaceships T and N. You do not respond in time on this day. You do not go to any planet. You find nothing.

You are presented with spaceships N and T. You press &lt;&lt;N&gt;&gt;. You end up on planet Z. You find 4 pieces of space treasure.

You are presented with spaceships T and N. You press &lt;&lt;N&gt;&gt;. You end up on planet Z. You find 4 pieces of space treasure.

You are presented with spaceships S and G. You press &lt;&lt;S&gt;&gt;. You end up on planet Z. You find 5 pieces of space treasure.

You are presented with spaceships T and N. You press &lt;&lt;N&gt;&gt;. You end up on planet Z. You find 3 pieces of space treasure.

You are presented with spaceships N and T. You press &lt;&lt;N&gt;&gt;. You end up on planet Z. You find 4 pieces of space treasure.

You are presented with spaceships T and N. You press &lt;&lt;N&gt;&gt;. You end up on planet Z. You find 2 pieces of space treasure.

You are presented with spaceships S and G. You press &lt;&lt;S&gt;&gt;. You end up on planet Z. You find 1 pieces of space treasure.

You are presented with spaceships T and N. You press &lt;&lt;N&gt;&gt;. You end up on planet Z. You find 3 pieces of antimatter.

You are presented with spaceships T and N. You press &lt;&lt;T&gt;&gt;. You end up on planet R. You find 2 pieces of space treasure.

You are presented with spaceships G and S. You press &lt;&lt;G&gt;&gt;. You end up on planet R. You find 4 pieces of space treasure.

You are presented with spaceships S and G. You press &lt;&lt;G&gt;&gt;. You end up on planet R. You find 2 pieces of space treasure.

You are presented with spaceships T and N. You press &lt;&lt;T&gt;&gt;. You end up on planet R. You find 3 pieces of space treasure.

You are presented with spaceships T and N. You press &lt;&lt;T&gt;&gt;. You end up on planet R. You find 5 pieces of space treasure.

You are presented with spaceships N and T. You press &lt;&lt;T&gt;&gt;. You end up on planet R. You find 4 pieces of space treasure.

You are presented with spaceships S and G. You press &lt;&lt;G&gt;&gt;. You end up on planet R. You find 4 pieces of space treasure.

You are presented with spaceships S and G. You press &lt;&lt;G&gt;&gt;. You end up on planet R. You find nothing.

You are presented with spaceships T and N. You press &lt;&lt;T&gt;&gt;. You end up on planet R. You find 3 pieces of antimatter.

You are presented with spaceships T and N. You press &lt;&lt;N&gt;&gt;. You end up on planet Z. You find 2 pieces of space treasure.

You are presented with spaceships S and G. You press &lt;&lt;S&gt;&gt;. You end up on planet Z. You find 2 pieces of space treasure.

You are presented with spaceships S and G. You press &lt;&lt;S&gt;&gt;. You end up on planet Z. You find 4 pieces of space treasure.

You are presented with spaceships S and G. You press &lt;&lt;S&gt;&gt;. You end up on planet Z. You find 4 pieces of space treasure.

You are presented with spaceships N and T. You press &lt;&lt;N&gt;&gt;. You end up on planet Z. You find 4 pieces of space treasure.

You are presented with spaceships N and T. You press &lt;&lt;N&gt;&gt;. You end up on planet Z. You find 5 pieces of space treasure.

You are presented with spaceships S and G. You press &lt;&lt;S&gt;&gt;. You end up on planet Z. You find 3 pieces of space treasure.

You are presented with spaceships G and S. You press &lt;&lt;S&gt;&gt;. You end up on planet Z. You find 4 pieces of space treasure.

You are presented with spaceships S and G. Yo

## Risky choice

Data source: [36]

Number of experiments: 1

Number of participants: 1755

Number of choices: 499728

## Example prompt:

You will play multiple rounds of a gambling game.

In each round, you will be presented with 6 different gambles labeled: Q, N, E, S, H, and K.

You will have to choose one of the gambles and receive a payoff for doing so.

The payoff you receive depends on both the gamble you choose and also the color of a ball we pull out of a jar with 100 colored balls.

There are a different number of balls of each color on every round.

The colors with more balls are more likely to be chosen.

Before making your choice, you may check how much different gambles are worth for different ball colors.

Each time you check a gamble will cost you 4 points.

To choose or check a gamble, first press the corresponding key, followed by typing "stop" (for choosing) or the ball color you would like to check.

A new round begins.

There are 50 pink balls, 19 red balls, 15 black balls, and 16 maroon balls.

You press &lt;&lt;Q&gt;&gt; and then type &lt;&lt;pink&gt;&gt;. The payoff for this combination would be -105 points.

You press &lt;&lt;E&gt;&gt; and then type &lt;&lt;pink&gt;&gt;. The payoff for this combination would be 47 points.

You press &lt;&lt;H&gt;&gt; and then type &lt;&lt;pink&gt;&gt;. The payoff for this combination would be 91 points.

You press &lt;&lt;H&gt;&gt; and then type &lt;&lt;stop&gt;&gt;. A maroon ball is chosen, and you earn -16 points.

A new round begins.

There are 2 pink balls, 47 red balls, 14 black balls, and 37 maroon balls.

You press &lt;&lt;Q&gt;&gt; and then type &lt;&lt;red&gt;&gt;. The payoff for this combination would be -168 points.

You press &lt;&lt;E&gt;&gt; and then type &lt;&lt;red&gt;&gt;. The payoff for this combination would be 209 points.

You press &lt;&lt;H&gt;&gt; and then type &lt;&lt;red&gt;&gt;. The payoff for this combination would be 22 points.

You press &lt;&lt;E&gt;&gt; and then type &lt;&lt;stop&gt;&gt;. A maroon ball is chosen, and you earn 25 points.

A new round begins.

There are 13 pink balls, 1 red balls, 47 black balls, and 39 maroon balls.

You press &lt;&lt;Q&gt;&gt; and then type &lt;&lt;black&gt;&gt;. The payoff for this combination would be -101 points.

You press &lt;&lt;E&gt;&gt; and then type &lt;&lt;black&gt;&gt;. The payoff for this combination would be -98 points.

You press &lt;&lt;H&gt;&gt; and then type &lt;&lt;black&gt;&gt;. The payoff for this combination would be 32 points.

You press &lt;&lt;H&gt;&gt; and then type &lt;&lt;stop&gt;&gt;. A maroon ball is chosen, and you earn -85 points.

A new round begins.

There are 7 pink balls, 15 red balls, 76 black balls, and 2 maroon balls.

You press &lt;&lt;N&gt;&gt; and then type &lt;&lt;black&gt;&gt;. The payoff for this combination would be -108 points.

You press &lt;&lt;Q&gt;&gt; and then type &lt;&lt;black&gt;&gt;. The payoff for this combination would be -191 points.

You press &lt;&lt;S&gt;&gt; and then type &lt;&lt;black&gt;&gt;. The payoff for this combination would be -222 points.

You press &lt;&lt;K&gt;&gt; and then type &lt;&lt;stop&gt;&gt;. A black ball is chosen, and you earn -90 points.

A new round begins.

There are 17 pink balls, 54 red balls, 16 black balls, and 13 maroon balls.

You press &lt;&lt;Q&gt;&gt; and then type &lt;&lt;red&gt;&gt;. The payoff for this combination would be 138 points.

You press &lt;&lt;N&gt;&gt; and then type &lt;&lt;red&gt;&gt;. The payoff for this combination would be 171 points.

You press &lt;&lt;E&gt;&gt; and then type &lt;&lt;red&gt;&gt;. The payoff for this combination would be -197 points.

You press &lt;&lt;N&gt;&gt; and then type &lt;&lt;stop&gt;&gt;. A red ball is chosen, and you earn 171 points.

A new round begins.

There are 1 pink balls, 38 red balls, 25 black balls, and 36 maroon balls.

You press &lt;&lt;N&gt;&gt; and then type &lt;&lt;red&gt;&gt;. The payoff for this combination would be -124 points.

You press &lt;&lt;E&gt;&gt; and then type &lt;&lt;red&gt;&gt;. The payoff for this combination would be -158 points.

You press &lt;&lt;S&gt;&gt; and then type &lt;&lt;red&gt;&gt;. The payoff for this combination would be -114 points.

You press &lt;&lt;H&gt;&gt; and then type &lt;&lt;stop&gt;&gt;. A black ball is chosen, and you earn 338 points.

A new round begins.

There are 37 pink balls, 44 red balls, 17 black balls, and 2 maroon balls.

You press &lt;&lt;Q&gt;&gt; and then type &lt;&lt;red&gt;&gt;. The payoff for this combination would be -198 points.

You press &lt;&lt;S&gt;&gt; and then type &lt;&lt;red&gt;&gt;. The payoff for this combination would be 39 points.

You press &lt;&lt;H&gt;&gt; and then type &lt;&lt;red&gt;&gt;. The payoff for this combination would be -63 points.

You press &lt;&lt;E&gt;&gt; and then type &lt;&lt;stop&gt;&gt;. A red ball is chosen, and you earn 51 points.

A new round begins.

There are 12 pink balls, 32 red balls, 45

## Tile-revealing task

Data source: [37]

Number of experiments: 1

Number of participants: 707

Number of choices: 321738

## Example prompt:

You are playing a game where you are revealing patterns on a binary grid.

Each turn you will be presented with a 7x7 grid of tiles.

If you give the location on the grid with an "X" on it, then it will either turn into a "1" or a "0".

Please give the location as a [row, column] pair where both row and column take values between 0 and 6.

Do not give the location on the grid where there is already a "1" or a "0".

Your job is to reveal as many 1s as possible while revealing as little 0s as possible.

The game ends when you have revealed all 1s on the grid.

You will have 25 boards to complete, each with a different underlying pattern.

```
You are currently solving board 1. The board state is now: XXXXXXX XXXXXXX XXXXXXX XXX1XXX XXXXXXX XXXXXXX XXXXXXX You choose <<[2, 2]>> and get a miss! The board state is now: XXXXXXX XXXXXXX XX0XXXX XXX1XXX XXXXXXX XXXXXXX XXXXXXX You choose <<[2, 4]>> and get a miss! The board state is now: XXXXXXX XXXXXXX XX0X0XX XXX1XXX XXXXXXX XXXXXXX XXXXXXX You choose <<[2, 3]>> and get a hit!
```

```
The board state is now: XXXXXXX XXXXXXX XX010XX XXX1XXX XXXXXXX XXXXXXX XXXXXXX You choose <<[1, 3]>> and get a miss! The board state is now: XXXXXXX XXX0XXX XX010XX XXX1XXX XXXXXXX XXXXXXX XXXXXXX You choose <<[3, 4]>> and get a hit! The board state is now: XXXXXXX XXX0XXX XX010XX XXX11XX XXXXXXX XXXXXXX XXXXXXX You choose <<[3, 2]>> and get a hit! The board state is now: XXXXXXX XXX0XXX XX010XX XX111XX XXXXXXX XXXXXXX XXXXXXX You choose <<[3, 5]>> and get a hit! The board state is now: XXXXXXX XXX0XXX XX010XX XX1111X XXXXXXX
```

```
XXXXXXX XXXXXXX You choose <<[3, 6]>> and get a hit! The board state is now: XXXXXXX XXX0XXX XX010XX XX11111 XXXXXXX XXXXXXX XXXXXXX You choose <<[3, 1]>> and get a hit! You are currently solving board 2. The board state is now: XXXXXXX X1XXXXX XXXXXXX XXXXXXX XXXXXXX XXXXXXX XXXXXXX You choose <<[2, 1]>> and get a miss! The board state is now: XXXXXXX X1XXXXX X0XXXXX XXXXXXX XXXXXXX XXXXXXX XXXXXXX You choose <<[0, 1]>> and get a miss! The board state is now: X0XXXXX X1XXXXX X0XXXXX XXXXXXX XXXXXXX XXXXXXX XXXXXXX You choose <<[1, 2]>> and get a hit!
```

The board state is now:

```
X0XXXXX X11XXXX X0XXXXX XXXXXXX XXXXXXX XXXXXXX XXXXXXX You choose <<[1, 0]>> and get a hit! The board state is now: X0XXXXX 111XXXX X0XXXXX XXXXXXX XXXXXXX XXXXXXX XXXXXXX You choose <<[1, 3]>> and get a hit! The board state is now: X0XXXXX 1111XXX X0XXXXX XXXXXXX XXXXXXX XXXXXXX XXXXXXX You choose <<[1, 4]>> and get a hit! The board state is now: X0XXXXX 11111XX X0XXXXX XXXXXXX XXXXXXX XXXXXXX XXXXXXX You choose <<[1, 5]>> and get a miss! The board state is now: X0XXXXX 111110X X0XXXXX XXXXXXX XXXXXXX XXXXXXX
```

```
XXXXXXX You choose <<[0, 0]>> and get a miss! The board state is now: 00XXXXX 111110X X0XXXXX XXXXXXX XXXXXXX XXXXXXX XXXXXXX You choose <<[2, 2]>> and get a miss! The board state is now: 00XXXXX 111110X X00XXXX XXXXXXX XXXXXXX XXXXXXX XXXXXXX You choose <<[2, 3]>> and get a hit! The board state is now: 00XXXXX 111110X X001XXX XXXXXXX XXXXXXX XXXXXXX XXXXXXX You choose <<[3, 3]>> and get a hit! The board state is now: 00XXXXX 111110X X001XXX XXX1XXX XXXXXXX XXXXXXX XXXXXXX You choose <<[0, 3]>> and get a hit! The board state is now: 00X1XXX
```

111110X

```
X001XXX XXX1XXX XXXXXXX XXXXXXX XXXXXXX You choose <<[4, 3]>> and get a hit! You are currently solving board 3. The board state is now: XXXXXXX XXXXXXX XXXXXXX XXXXXXX XXXXXXX XXX1XXX XXXXXXX You choose <<[4, 2]>> and get a hit! The board state is now: XXXXXXX XXXXXXX XXXXXXX XXXXXXX XX1XXXX XXX1XXX XXXXXXX You choose <<[3, 1]>> and get a hit! The board state is now: XXXXXXX XXXXXXX XXXXXXX X1XXXXX XX1XXXX XXX1XXX XXXXXXX You choose <<[2, 0]>> and get a hit! The board state is now: XXXXXXX XXXXXXX 1XXXXXX X1XXXXX XX1XXXX XXX1XXX XXXXXXX
```

## You choose &lt;&lt;[1, 1]&gt;&gt; and get a miss! The board state is now: XXXXXXX X0XXXXX 1XXXXXX X1XXXXX XX1XXXX XXX1XXX XXXXXXX You choose &lt;&lt;[2, 2]&gt;&gt; and get a miss! The board state is now: XXXXXXX X0XXXXX 1X0XXXX X1XXXXX XX1XXXX XXX1XXX XXXXXXX You choose &lt;&lt;[3, 3]&gt;&gt; and get a hit! The board state is now: XXXXXXX X0XXXXX Probabilistic instrumental learning Data source: [38] Number of experiments: 2 Number of participants: 77 Number of choices: 7392

## Example prompt:

You are going to visit four different casinos (named 1, 2, 3, and 4) 24 times each. Each casino owns two slot machines that return either 0 or 0.5 points stochastically with different probabilities.

You can play one of the machines in order to win points by pressing the corresponding key.

Your goal is to maximize the sum of received points within all visits.

You go to casino 3. You can choose between machines B and C. You press &lt;&lt;B&gt;&gt; and receive 0.0 points.

You go to casino 4. You can choose between machines P and T. You press &lt;&lt;T&gt;&gt; and receive 0.5 points.

- You go to casino 4. You can choose between machines P and T. You press &lt;&lt;T&gt;&gt; and receive 0.5 points.
- You go to casino 3. You can choose between machines B and C. You press &lt;&lt;B&gt;&gt; and receive 0.0 points.
- You go to casino 1. You can choose between machines F and I. You press &lt;&lt;I&gt;&gt; and receive 0.0 points.
- You go to casino 1. You can choose between machines F and I. You press &lt;&lt;F&gt;&gt; and receive 0.0 points.
- You go to casino 2. You can choose between machines L and J. You press &lt;&lt;L&gt;&gt; and receive 0.5 points.
- You go to casino 3. You can choose between machines B and C. You press &lt;&lt;B&gt;&gt; and receive 0.0 points.
- You go to casino 4. You can choose between machines P and T. You press &lt;&lt;T&gt;&gt; and receive 0.0 points.
- You go to casino 3. You can choose between machines B and C. You press &lt;&lt;C&gt;&gt; and receive 0.0 points.
- You go to casino 4. You can choose between machines P and T. You press &lt;&lt;P&gt;&gt; and receive 0.5 points.
- You go to casino 1. You can choose between machines F and I. You press &lt;&lt;F&gt;&gt; and receive 0.5 points.
- You go to casino 2. You can choose between machines L and J. You press &lt;&lt;L&gt;&gt; and receive 0.5 points.
- You go to casino 2. You can choose between machines L and J. You press &lt;&lt;L&gt;&gt; and receive 0.5 points.
- You go to casino 1. You can choose between machines F and I. You press &lt;&lt;F&gt;&gt; and receive 0.0 points.
- You go to casino 2. You can choose between machines L and J. You press &lt;&lt;J&gt;&gt; and receive 0.5 points.
- You go to casino 1. You can choose between machines F and I. You press &lt;&lt;I&gt;&gt; and receive 0.0 points.
- You go to casino 1. You can choose between machines F and I. You press &lt;&lt;F&gt;&gt; and receive 0.0 points.
- You go to casino 2. You can choose between machines L and J. You press &lt;&lt;J&gt;&gt; and receive 0.0 points.
- You go to casino 2. You can choose between machines L and J. You press &lt;&lt;L&gt;&gt; and receive 0.5 points.
- You go to casino 3. You can choose between machines B and C. You press &lt;&lt;B&gt;&gt; and receive 0.5 points.
- You go to casino 3. You can choose between machines B and C. You press &lt;&lt;B&gt;&gt; and receive 0.0 points.
- You go to casino 2. You can choose between machines L and J. You press &lt;&lt;L&gt;&gt; and receive 0.5 points.
- You go to casino 3. You can choose between machines B and C. You press &lt;&lt;C&gt;&gt; and receive 0.5 points.

You go to casino 2. You can choose between machines L and J. You press &lt;&lt;L&gt;&gt;

and receive 0.0 points.

You go to casino 1. You can choose between machines F and I. You press &lt;&lt;I&gt;&gt; and receive 0.0 points.

You go to casino 4. You can choose between machines P and T. You press &lt;&lt;P&gt;&gt; and receive 0.0 points.

You go to casino 4. You can choose between machines P and T. You press &lt;&lt;T&gt;&gt; and receive 0.5 points.

You go to casino 4. You can choose between machines P and T. You press &lt;&lt;T&gt;&gt; and receive 0.5 points.

You go to casino 1. You can choose between machines F and I. You press &lt;&lt;I&gt;&gt; and receive 0.5 points.

You go to casino 4. You can choose between machines P and T. You press &lt;&lt;P&gt;&gt; and receive 0.5 points.

You go to casino 3. You can choose between machines B and C. You press &lt;&lt;C&gt;&gt; and receive 0.5 points.

You go to casino 2. You can choose between machines L and J. You press &lt;&lt;L&gt;&gt; and receive 0.5 points.

You go to casino 3. You can choose between machines B and C. You press &lt;&lt;C&gt;&gt; and receive 0.5 points.

You go to casino 4. You can choose between machines P and T. You press &lt;&lt;P&gt;&gt; and receive 0.5 points.

You go to casino 3. You can choose between machines B and C. You press &lt;&lt;C&gt;&gt; and receive 0.5 points.

You go to casino 4. You can choose between machines P and T. You press &lt;&lt;P&gt;&gt; and receive 0.5 point

## Medin categorization

Data source: [39]

Number of experiments: 2

Number of participants: 228

Number of choices: 37848

## Example prompt:

You will observe a series of objects, one at a time.

The objects differ along three binary dimensions: shape (square vs. triangle), size (1.50 inch vs. 0.75 inch), and shading (black vs. white).

Each dimension is indicated by the three digits, for example, '121' means a square, 0.75 inch, black object.

Based on some combination of the three dimensions, each object belongs to one of two categories, W or N.

You have to assign each object to one of the two categories by pressing the corresponding key.

If your choice is correct, you get a point, otherwise you lose a point.

Your goal is to get as many points as possible.

At some point, you begin a 'test block' in which you will see eight objects. Here, you have to assign each object to one of the two categories as before. Furthermore, you have to rate how typical the object is for the category you chose, on a scale from 1 to 9.

```
1 means 'not at all typical', and 9 means 'most typical'. You see the image 112, press <<W>> and get 1 points. You see the image 121, press <<N>> and get 0 points. You see the image 212, press <<W>> and get 0 points. You see the image 211, press <<N>> and get 0 points. You see the image 221, press <<W>> and get 0 points. You see the image 122, press <<W>> and get 0 points. You see the image 122, press <<N>> and get 1 points. You see the image 221, press <<W>> and get 0 points. You see the image 121, press <<N>> and get 0 points. You see the image 212, press <<N>> and get 1 points. You see the image 211, press <<N>> and get 0 points. You see the image 112, press <<W>> and get 1 points. You see the image 112, press <<W>> and get 1 points. You see the image 212, press <<N>> and get 1 points. You see the image 221, press <<W>> and get 0 points. You see the image 211, press <<N>> and get 0 points. You see the image 121, press <<N>> and get 0 points. You see the image 122, press <<W>> and get 0 points. You see the image 212, press <<N>> and get 1 points. You see the image 221, press <<W>> and get 0 points. You see the image 211, press <<N>> and get 0 points. You see the image 121, press <<N>> and get 0 points. You see the image 112, press <<W>> and get 1 points. You see the image 122, press <<W>> and get 0 points. You see the image 122, press <<N>> and get 1 points. You see the image 112, press <<W>> and get 1 points. You see the image 121, press <<N>> and get 0 points. You see the image 221, press <<N>> and get 1 points. You see the image 212, press <<N>> and get 1 points. You see the image 211, press <<N>> and get 0 points. You see the image 112, press <<W>> and get 1 points. You see the image 212, press <<N>> and get 1 points. You see the image 122, press <<W>> and get 0 points. You see the image 211, press <<N>> and get 0 points. You see the image 221, press <<W>> and get 0 points. You see the image 121, press <<N>> and get 0 points. You see the image 122, press <<N>> and get 1 points. You see the image 212, press <<W>> and get 0 points.
```

```
You see the image 211, press <<N>> and get 0 points.
```

```
You see the image 221, press <<N>> and get 1 points. You see the image 112, press <<W>> and get 1 points. You see the image 121, press <<W>> and get 1 points. You see the image 121, press <<W>> and get 1 points. You see the image 211, press <<N>> and get 0 points. You see the image 221, press <<N>> and get 1 points. You see the image 212, press <<N>> and get 1 points. You see the image 122, press <<W>> and get 0 points. You see the image 112, press <<W>> and get 1 points. You see the image 212, press <<N>> and get 1 points. You see the image 112, press <<W>> and get 1 points. You see the image 121, press <<N>> and get 0 points. You see the image 122, press <<W>> and get 0 points. You see the image 221, press <<N>> and get 1 points. You see the image 211, press <<N>> and get 0 points. You see the image 112, press <<W>> and get 1 points. You see the image 122, press <<W>> and get 0 points. You see the image 121, press <<N>> and get 0 points. You see the image 221, press <<N>> and get 1 points. You see the image 212, press <<W>> and get 0 points.
```

You see the image 211, p

## Zoopermarket

Data source: [40]

Number of experiments: 3

Number of participants: 96

Number of choices: 34442

## Example prompt:

You will have to repeatedly feed animals with fruits.

Each fruit contains two vitamins.

Every animal has a different preference for the vitamins.

The vitamin contents and the preferences are both given as vectors with two entries.

Your points are calculated as the dot product of the vitamin content with the preference of the current animal.

For example, let us assume that you have to feed the elephant who has a preference [-1 1].

Then, if you feed the elephant a fruit with vitamin content [-1 1], this would yield 2 points.

If you feed it a fruit with vitamins [1 0], this would yield -1 points.

You have to buy the fruits in a market, in which you can go left or right for two steps.

You can press I to go left, and V to go right.

Per round, you always collect two fruits.

There are eight animals in total and you have to feed one, two, or three of them in each block.

```
In each block, there are twelve trials with different animals in random order. After these twelve trials, there are three more in which you have to feed new animals. The fruits in the market are rearranged after each block, meaning that you have to relearn the positions. Your goal is to maximize the points obtained. A new block starts. The locations of the fruits in the market got scrambled. You have to feed the crocodile. It has the preference [1 1]. You press <<V>> and find the apple which has the vitamins [-1 -1]. You get -2 points. You press <<V>> and find the orange which has the vitamins [0 1]. You get 1 points. You have to feed the crocodile. It has the preference [1 1]. You press <<V>> and find the apple which has the vitamins [-1 -1]. You get -2 points. You press <<I>> and find the blueberry which has the vitamins [-1 1]. You get 0 points. You have to feed the crocodile. It has the preference [1 1]. You press <<I>> and find the strawberry which has the vitamins [1 1]. You get 2 points. You press <<V>> and find the grapes which has the vitamins [ 1 -1]. You get 0 points. You have to feed the crocodile. It has the preference [1 1]. You press <<I>> and find the strawberry which has the vitamins [1 1]. You get 2 points. You press <<V>> and find the grapes which has the vitamins [ 1 -1]. You get 0 points. You have to feed the kangaroo. It has the preference [-1 0]. You press <<V>> and find the apple which has the vitamins [-1 -1]. You get 1 points. You press <<I>> and find the blueberry which has the vitamins [-1 1]. You get 1 points. You have to feed the kangaroo. It has the preference [-1 0]. You press <<V>> and find the apple which has the vitamins [-1 -1]. You get 1 points. You press <<I>> and find the blueberry which has the vitamins [-1 1]. You get 1 points. You have to feed the crocodile. It has the preference [1 1]. You press <<I>> and find the strawberry which has the vitamins [1 1]. You get 2 points. You press <<V>> and find the grapes which has the vitamins [ 1 -1]. You get 0 points. You have to feed the kangaroo. It has the preference [-1 0]. You press <<V>> and find the apple which has the vitamins [-1 -1]. You get 1
```

points.

You press &lt;&lt;I&gt;&gt; and find the blueberry which has the vitamins [-1 1]. You get 1 points.

You have to feed the kangaroo. It has the preference [-1 0].

You press &lt;&lt;V&gt;&gt; and find the apple which has the vitamins [-1 -1]. You get 1 points.

You press &lt;&lt;I&gt;&gt; and find the blueberry which has the vitamins [-1 1]. You get 1 points.

You have to feed the kangaroo. It has the preference [-1 0].

You press &lt;&lt;V&gt;&gt; and find the apple which has the vitamins [-1 -1]. You get 1 points.

You press &lt;&lt;I&gt;&gt; and find the blueberry which has the vitamins [-1 1]. You get 1 points.

You have to feed the kangaroo. It has the preference [-1 0].

You press &lt;&lt;V&gt;&gt; and find the apple which has the vitamins [-1 -1]. You get 1 points.

You press &lt;&lt;I&gt;&gt; and find the blueberry which has the vitamins [-1 1]. You get 1 points.

You have to feed the crocodile. It has the preference [1 1].

You press &lt;&lt;V&gt;&gt; and find the apple which has the vitamins [-1 -1]. You get -2 points.

You press &lt;&lt;V&gt;&gt; and find the orange which has the vitamins [0 1]. You get 1 points.

You

## choices13k

Data source: [5]

Number of experiments: 1

Number of participants: 13735

Number of choices: 1097375

## Example prompt:

You will encounter a series of gambling problems where you have to select between two options.

You can select an option by pressing the corresponding key.

For some problems, you are told the points you received and missed out on after each selection, while for others this information is suppressed.

In cases where the probabilities are unknown, they sum up to one and remain constant within a problem.

Option L delivers 10.0 points with 80.0% chance, or -25.0 points with 20.0% chance.

Option B delivers 0.0 points with 20.0% chance, or 5.0 points with 80.0% chance.

You press &lt;&lt;B&gt;&gt;. You receive 5.0 points by selecting this option. You would have received 10.0 points had you chosen the other option.

You press &lt;&lt;B&gt;&gt;. You receive 5.0 points by selecting this option. You would have received -25.0 points had you chosen the other option.

You press &lt;&lt;B&gt;&gt;. You receive 5.0 points by selecting this option. You would have received 10.0 points had you chosen the other option.

You press &lt;&lt;B&gt;&gt;. You receive 5.0 points by selecting this option. You would have received -25.0 points had you chosen the other option.

You press &lt;&lt;B&gt;&gt;. You receive 0.0 points by selecting this option. You would have received -25.0 points had you chosen the other option.

Option L delivers either 30.0 points with 100.0% chance, or 30.0 points with 0.0% chance.

Option B delivers either 0.0 points with unknown chance, or 42.0 points with unknown chance.

You press &lt;&lt;L&gt;&gt;. You receive 30.0 points by selecting this option. You would have received 42.0 points had you chosen the other option.

You press &lt;&lt;L&gt;&gt;. You receive 30.0 points by selecting this option. You would have received 0.0 points had you chosen the other option.

You press &lt;&lt;L&gt;&gt;. You receive 30.0 points by selecting this option. You would have received 42.0 points had you chosen the other option.

You press &lt;&lt;L&gt;&gt;. You receive 30.0 points by selecting this option. You would have received 42.0 points had you chosen the other option.

You press &lt;&lt;B&gt;&gt;. You receive 42.0 points by selecting this option. You would have received 30.0 points had you chosen the other option.

Option L delivers 8.0 points with 100.0% chance, or 8.0 points with 0.0% chance.

Option B delivers 5.0 points with 95.0% chance, or 54.0 points with 5.0% chance.

You press &lt;&lt;B&gt;&gt;. You receive 5.0 points by selecting this option. You would have received 8.0 points had you chosen the other option.

You press &lt;&lt;B&gt;&gt;. You receive 5.0 points by selecting this option. You would have received 8.0 points had you chosen the other option.

You press &lt;&lt;B&gt;&gt;. You receive 5.0 points by selecting this option. You would have received 8.0 points had you chosen the other option.

You press &lt;&lt;B&gt;&gt;. You receive 5.0 points by selecting this option. You would have received 8.0 points had you chosen the other option.

You press &lt;&lt;B&gt;&gt;. You receive 5.0 points by selecting this option. You would have received 8.0 points had you chosen the other option.

Option L delivers 20.0 points with 100.0% chance, or 20.0 points with 0.0% chance.

Option B delivers 15.0 points with 99.0% chance, 47.5 points with 0.0078% chance, 48.5 points with 0.0547% chance, 49.5 points with 0.1641% chance, 50.5 points with 0.2734% chance, 51.5 points with 0.2734% chance, 52.5 points with 0.1641% chance, 53.5 points with 0.0547% chance, or 54.5 points with 0.0078% chance.

You press &lt;&lt;B&gt;&gt;. You receive 15.0 points by selecting this option. You would have received 20.0 points had you chosen the other option.

You press &lt;&lt;B&gt;&gt;. You receive 15.0 points by selecting this option. You would have received 20.0 points had you chosen the other option.

You press &lt;&lt;B&gt;&gt;. You receive 15.0 points by selecting this option. You would have received 20.0 points had you chosen the other option.

You press &lt;&lt;B&gt;&gt;. You receive 15.0 points by selecting this option. You would have received 20.0 points had you chosen the other option.

You press &lt;&lt;B&gt;&gt;. You receive 15.0 points by selecting this option. You would have received 20.0 points had you chosen the other option.

Option L delivers 15.0 points with 5.0% chance, or 9.0 points with 95.0%

## CPC18

Data source: [41]

Number of experiments: 1

Number of participants: 216

Number of choices: 162000

## Example prompt:

You will encounter a series of gambling problems where you have to select between two options.

You can select an option by pressing the corresponding key.

You will encounter each problem 25 times.

In the first five encounters, you will not receive feedback.

In the remaining 20 encounters, you will receive feedback about the outcomes of both options.

In cases where the probabilities are stated to be unknown, they sum up to one and remain constant within a problem.

Option F delivers 3 points with 80.0% chance, 94 points with 1.25% chance, 95 points with 5.0% chance, 96 points with 7.5% chance, 97 points with 5.0% chance, 98 points with 1.25% chance.

Option X delivers -19 points with 50.0% chance, 59 points with 50.0% chance.

You press &lt;&lt;X&gt;&gt;.

You press &lt;&lt;X&gt;&gt;.

You press &lt;&lt;X&gt;&gt;.

You press &lt;&lt;X&gt;&gt;.

You press &lt;&lt;X&gt;&gt;.

You press &lt;&lt;X&gt;&gt; and gain 59 points. You would have gained 3 points had you chosen option F.

You press &lt;&lt;X&gt;&gt; and gain 59 points. You would have gained 98 points had you chosen option F.

You press &lt;&lt;X&gt;&gt; and gain 59 points. You would have gained 3 points had you chosen option F.

You press &lt;&lt;X&gt;&gt; and lose 19 points. You would have gained 95 points had you chosen option F.

You press &lt;&lt;X&gt;&gt; and lose 19 points. You would have gained 3 points had you chosen option F. You press &lt;&lt;X&gt;&gt; and gain 59 points. You would have gained 3 points had you chosen option F. You press &lt;&lt;X&gt;&gt; and lose 19 points. You would have gained 3 points had you chosen option F. You press &lt;&lt;X&gt;&gt; and lose 19 points. You would have gained 3 points had you chosen option F. You press &lt;&lt;F&gt;&gt; and gain 3 points. You would have lost 19 points had you chosen option X. You press &lt;&lt;X&gt;&gt; and lose 19 points. You would have gained 3 points had you chosen option F. You press &lt;&lt;X&gt;&gt; and lose 19 points. You would have gained 3 points had you chosen option F. You press &lt;&lt;X&gt;&gt; and gain 59 points. You would have gained 3 points had you chosen option F. You press &lt;&lt;X&gt;&gt; and gain 59 points. You would have gained 3 points had you chosen option F. You press &lt;&lt;X&gt;&gt; and lose 19 points. You would have gained 3 points had you chosen option F. You press &lt;&lt;X&gt;&gt; and lose 19 points. You would have gained 96 points had you chosen option F. You press &lt;&lt;X&gt;&gt; and gain 59 points. You would have gained 3 points had you chosen option F. You press &lt;&lt;X&gt;&gt; and lose 19 points. You would have gained 3 points had you chosen option F. You press &lt;&lt;X&gt;&gt; and gain 59 points. You would have gained 98 points had you chosen option F. You press &lt;&lt;X&gt;&gt; and gain 59 points. You would have gained 3 points had you chosen option F.

You press &lt;&lt;X&gt;&gt; and lose 19 points. You would have gained 3 points had you chosen option F.

Option F delivers -12 points with 95.0% chance, 47 points with 2.5% chance, 49 points with 1.25% chance, 53 points with 0.625% chance, 61 points with 0.3125% chance, 77 points with 0.15625% chance, 109 points with 0.078125% chance, 173 points with 0.078125% chance.

```
Option X delivers -9 points with 100.0% chance. You press <<F>>. You press <<F>>. You press <<F>>. You press <<F>>. You press <<F>>.
```

You press &lt;&lt;F&gt;&gt; and lose 12 points. You would have lost 9 points had you chosen option X.

You press &lt;&lt;F&gt;&gt; and lose 12 points. You would have lost 9 points had you chosen option X.

You press &lt;&lt;F&gt;&gt; and lose 12 points. You would have lost 9 points had you chosen option X.

You press &lt;&lt;F&gt;&gt; and lose 12 points. You would have lost 9 points had you chosen option X.

You press &lt;&lt;F&gt;&gt; and lose 12 points. You would have lost 9 points had you chosen option X.

You press &lt;&lt;F&gt;&gt; and lose 12 points. You would have lost 9 points had you chosen option X.

You press &lt;&lt;F&gt;&gt; and lose 12 points. You would have lost 9 points had you chosen option X.

You press &lt;&lt;F&gt;&gt; and lose 12 points. You would have lost 9 points had you chosen option X.

You press &lt;&lt;F&gt;&gt; and gain 49 points. You would have lost 9 points had you chosen option X.

You press &lt;&lt;F&gt;&gt; and gain 53 points. You would have lost 9 points had you chosen option X.

You press &lt;&lt;F&gt;&gt; and lose 12 points. You would have lost 9 points had you chosen option X.

You press &lt;&lt;F&gt;&gt; and lose 12 points. You would

## Episodic long-term memory

Data source: [42]

Number of experiments: 3

Number of participants: 132

Number of choices: 18649

## Example prompt:

In this experiment, you will go through three cycles of three tasks.

Each cycle concerns itself with a list of 30 words for you to study.

In the first task of each cycle, you will go through the list.

You need to remember the words indicated by a red border.

For each word, please make a judgement on whether the object is larger or smaller than a football, and press the key "O" if the object is larger than a football, and the key "M" if it is smaller instead.

In the second task of each cycle, you will try to solve as many arithmetic equations as you can in one minute.

In the third task of each cycle, you will recall the words that you memorized in the first task of that cycle.

## List 1, task 1:

You see the word "church", surrounded by a blue border. You press &lt;&lt;O&gt;&gt;. The word disappears but the blue border stays for another 3 seconds before disappearing.

You see the word "robot", surrounded by a blue border. You press &lt;&lt;O&gt;&gt;. The word disappears but the blue border stays for another 3 seconds before disappearing. You see the word "jewelry", surrounded by a red border. You press &lt;&lt;M&gt;&gt;. The word disappears but the red border stays for another 3 seconds before disappearing. You see the word "skull", surrounded by a blue border. You press &lt;&lt;O&gt;&gt;. The word disappears but the blue border stays for another 3 seconds before disappearing. You see the word "apple", surrounded by a blue border. You press &lt;&lt;M&gt;&gt;. The word disappears but the blue border stays for another 3 seconds before disappearing. You see the word "garden", surrounded by a blue border. You press &lt;&lt;O&gt;&gt;. The word disappears but the blue border stays for another 3 seconds before disappearing. You see the word "pipe", surrounded by a red border. You press &lt;&lt;M&gt;&gt;. The word disappears but the red border stays for another 3 seconds before disappearing. You see the word "needle", surrounded by a red border. You press &lt;&lt;M&gt;&gt;. The word disappears but the red border stays for another 3 seconds before disappearing. You see the word "circus", surrounded by a red border. You press &lt;&lt;O&gt;&gt;. The word disappears but the red border stays for another 3 seconds before disappearing. You see the word "towel", surrounded by a blue border. You press &lt;&lt;M&gt;&gt;. The word disappears but the blue border stays for another 3 seconds before disappearing. You see the word "rabbit", surrounded by a blue border. You press &lt;&lt;M&gt;&gt;. The word disappears but the blue border stays for another 3 seconds before disappearing. You see the word "diamond", surrounded by a red border. You press &lt;&lt;M&gt;&gt;. The word disappears but the red border stays for another 3 seconds before disappearing. You see the word "cocktail", surrounded by a red border. You press &lt;&lt;M&gt;&gt;. The word disappears but the red border stays for another 3 seconds before disappearing. You see the word "satellite", surrounded by a red border. You press &lt;&lt;O&gt;&gt;. The word disappears but the red border stays for another 3 seconds before disappearing. You see the word "sweater", surrounded by a blue border. You press &lt;&lt;O&gt;&gt;. The word disappears but the blue border stays for another 3 seconds before disappearing. You see the word "planet", surrounded by a red border. You press &lt;&lt;O&gt;&gt;. The word disappears but the red border stays for another 3 seconds before disappearing. You see the word "pizza", surrounded by a blue border. You press &lt;&lt;O&gt;&gt;. The word disappears but the blue border stays for another 3 seconds before disappearing. You see the word "forest", surrounded by a blue border. You press &lt;&lt;O&gt;&gt;. The word disappears but the blue border stays for another 3 seconds before disappearing. You see the word "carpet", surrounded by a blue border. You press &lt;&lt;O&gt;&gt;. The word disappears but the blue border stays for another 3 seconds before disappearing. You see the word "highway", surrounded by a red border. You press &lt;&lt;O&gt;&gt;. The word disappears but the red border stays for another 3 seconds before disappearing. You see the word "jeep", surrounded by a blue border. You press &lt;&lt;O&gt;&gt;. The word disappears but the blue border stays for another 3 seconds before disappearing. You see t

## Intertemporal choice

Data source: [43]

Number of experiments: 1

Number of participants: 11937

Number of choices: 142236

## Example prompt:

In the following you will be presented with multiple choices between two options G and C.

Please name which option you would prefer by pressing the corresponding key.

You have the choice between receiving 500$ immediately (press G) or receiving 550$ in one year (press C). You press &lt;&lt;G&gt;&gt;.

You have the choice between receiving 500$ immediately (press G) or receiving 600$ in one year (press C). You press &lt;&lt;C&gt;&gt;.

You have the choice between paying 500$ immediately (press G) or paying 550$ in one year (press C). You press &lt;&lt;G&gt;&gt;.

You have the choice between paying 500$ immediately (press G) or paying 510$ in one year (press C). You press &lt;&lt;C&gt;&gt;.

You have the choice between receiving 5000$ immediately (press G) or receiving 5500$ in one year (press C). You press &lt;&lt;G&gt;&gt;.

You have the choice between receiving 5000$ immediately (press G) or receiving 6000$ in one year (press C). You press &lt;&lt;C&gt;&gt;.

You have the choice between receiving 500$ in one year (press G) or receiving 600$ in two years (press C). You press &lt;&lt;C&gt;&gt;.

You have the choice between receiving 500$ immediately (press G) or receiving 700$ in two years (press C). You press &lt;&lt;C&gt;&gt;.

You have the choice between wait 500$ immediately (press G) or wait 600$ in one year (press C). You press &lt;&lt;C&gt;&gt;.

You have the choice between receive 500$ immediately (press G) or receive 600$ in one year (press C). You press &lt;&lt;C&gt;&gt;.

## Horizon task

Data source: [44]

Number of experiments: 1

Number of participants: 78

Number of choices: 25336

## Example prompt:

You are participating in multiple games involving two slot machines, labeled J and R.

The two slot machines are different across different games.

Each time you choose a slot machine, you get some points.

You choose a slot machine by pressing the corresponding key.

Each slot machine tends to pay out about the same amount of points on average.

Your goal is to choose the slot machines that will give you the most points across the experiment.

The first 4 trials in each game are instructed trials where you will be told which slot machine to choose.

After these instructed trials, you will have the freedom to choose for either 1 or 6 trials.

```
Game 1. There are 10 trials in this game. You are instructed to press J and get 57 points. You are instructed to press R and get 29 points. You are instructed to press J and get 66 points. You are instructed to press R and get 38 points. You press <<R>> and get 45 points. You press <<R>> and get 38 points. You press <<R>> and get 49 points. You press <<J>> and get 59 points. You press <<R>> and get 28 points. You press <<R>> and get 51 points. Game 2. There are 10 trials in this game. You are instructed to press J and get 76 points. You are instructed to press J and get 89 points. You are instructed to press R and get 61 points. You are instructed to press J and get 74 points. You press <<R>> and get 59 points. You press <<J>> and get 72 points. You press <<J>> and get 61 points. You press <<R>> and get 70 points. You press <<R>> and get 73 points. You press <<J>> and get 65 points. Game 3. There are 10 trials in this game. You are instructed to press R and get 60 points. You are instructed to press R and get 43 points. You are instructed to press J and get 54 points. You are instructed to press J and get 65 points. You press <<R>> and get 56 points. You press <<J>> and get 38 points. You press <<R>> and get 56 points. You press <<J>> and get 61 points. You press <<R>> and get 59 points. You press <<J>> and get 56 points. Game 4. There are 5 trials in this game. You are instructed to press J and get 36 points. You are instructed to press J and get 43 points. You are instructed to press R and get 57 points.
```

You are instructed to press R and get 49 points. You press &lt;&lt;R&gt;&gt; and get 63 points. Game 5. There are 5 trials in this game. You are instructed to press R and get 44 points. You are instructed to press J and get 45 points. You are instructed to press R and get 29 points. You are instructed to press J and get 38 points. You press &lt;&lt;R&gt;&gt; and get 43 points. Game 6. There are 5 trials in this game. You are instructed to press R and get 74 points. You are instructed to press R and get 70 points. You are instructed to press R and get 61 points. You are instructed to press J and get 77 points. You press &lt;&lt;J&gt;&gt; and get 74 points. Game 7. There are 5 trials in this game. You are instructed to press J and get 36 points. You are instructed to press R and get 50 points. You are instructed to press J and get 49 points. You are instructed to press J and get 34 points. You press &lt;&lt;R&gt;&gt; and get 48 points. Game 8. There are 10 trials in this game. You are instructed to press J and get 54 points. You are instructed to press R and get 64 points. You are instructed to press R and get 63 points. You are instructed to press R and get 52 points. You press &lt;&lt;J&gt;&gt; and get 63 points. You press &lt;&lt;J&gt;&gt; and get 65 points. You press &lt;&lt;R&gt;&gt; and get 70 points. You press &lt;&lt;J&gt;&gt; and get 69 points. You press &lt;&lt;R&gt;&gt; and get 64 points. You press &lt;&lt;J&gt;&gt; and get 64 points. Game 9. There are 5 trials in this game. You are instructed to press J and get 57 points. You are instructed to press R and get 50 points. You are instructed to press R and get 57 points. You are instructed to press J and get 72 points. You press &lt;&lt;R&gt;&gt; and get 47 points. Game 10. There are 10 trials in this game.

You are instructed to press R and get 21 points.

```
You are instructed to press J and get 26 points. You are instructed to press J and get 52 points. You are instructed to press J and get 27 points. You press <<R>> and get 21 points. You press <<J>> a
```

## Structured bandit

```
Data source: [45]
```

```
Number of experiments: 5 Number of participants: 534 Number of choices: 160200
```

## Example prompt:

You will be playing a game for 30 rounds.

Each round contains 10 trials.

In each trial, you have to select one option that will generate a reward between 0 and 50 points.

You can choose between options 1, 2, 3, 4, 5, 6, 7 and 8 by pressing the corresponding key.

After each round the options reset and each option can produce different rewards in the following round.

Your goal is to maximize your reward.

```
You are playing round 1: You press <<1>> and get 13.927462234 points. You press <<2>> and get 36.7688570508 points. You press <<1>> and get 14.2022179045 points. You press <<1>> and get 14.255711791 points. You press <<1>> and get 14.0630012349 points. You press <<1>> and get 13.7662251776 points. You press <<1>> and get 14.0950976416 points. You press <<1>> and get 13.9059322374 points. You press <<1>> and get 13.7876455405 points. You press <<1>> and get 14.0791620504 points. You are playing round 2: You press <<1>> and get 7.9614376644 points. You press <<1>> and get 8.0581019194 points. You press <<1>> and get 7.8981838872 points. You press <<1>> and get 7.6801851393 points. You press <<1>> and get 7.8750440099 points. You press <<1>> and get 7.8730616431 points. You press <<1>> and get 7.9118344028 points. You press <<1>> and get 8.134691905 points.
```

```
You press <<1>> and get 7.3146307967 points. You press <<1>> and get 7.5832954876 points. You are playing round 3: You press <<1>> and get 45.5086514616 points. You press <<1>> and get 45.4708060494 points. You press <<1>> and get 45.9992623342 points. You press <<1>> and get 45.2562607277 points. You press <<1>> and get 45.4858045741 points. You press <<1>> and get 45.5714527483 points. You press <<1>> and get 45.6341629546 points. You press <<1>> and get 45.0394158823 points. You press <<1>> and get 45.4305272183 points. You press <<1>> and get 45.5876540303 points. You are playing round 4: You press <<1>> and get 11.3846751956 points. You press <<1>> and get 11.5363886375 points. You press <<1>> and get 11.7231131775 points. You press <<1>> and get 11.6522950289 points. You press <<1>> and get 11.526071202 points. You press <<1>> and get 11.8137491734 points. You press <<1>> and get 11.3114379632 points. You press <<1>> and get 11.9434174388 points. You press <<1>> and get 11.2375196571 points. You press <<1>> and get 11.7253908566 points. You are playing round 5: You press <<1>> and get 6.3035553498 points. You press <<1>> and get 6.1091934289 points. You press <<1>> and get 5.8593245302 points. You press <<1>> and get 6.7472106803 points. You press <<1>> and get 5.8960908181 points. You press <<1>> and get 6.4056392625 points. You press <<1>> and get 6.2178725578 points. You press <<1>> and get 6.0009585684 points. You press <<1>> and get 6.5478514159 points. You press <<1>> and get 6.1982281156 points. You are playing round 6: You press <<1>> and get 7.6893330342 points. You press <<1>> and get 7.3522351643 points. You press <<1>> and get 7.5121866021 points. You press <<1>> and get 7.7384186564 points. You press <<1>> and get 6.8107475324 points.
```

```
You press <<4>> and get 24.8575884026 points. You press <<2>> and get 13.8675683188 points. You press <<1>> and get 7.8646759927 points. You press <<4>> and get 24.9148267139 points. You press <<2>> and get 13.7239940234 points. You are playing round 7: You press <<1>> and get 4.8637779497 points. You press <<4>> and get 21.4211685718 points. You press <<2>> and get 9.9283331067 points. You press <<1>> and get 4.3283739798 points. You press <<1>> and get 4.2486815414 points. You press <<2>> and get 9.7358045234 points. You press <<3>> and get 15.5522984698 points. You press <<4>> and get 21.1157043351 points. You press <<4>> and get 21.2293801786 points. You press <<4>> and get 21.2346665196 points. You are playing round 8: You press <<5>> and get 21.2600225368 points. You press <<6>> and get 14.9281922416 points. You press <<6>> and get 15.1378822594 points. You press <<6>> and get 15.0143768307 points.
```

```
You press <<8>> and get 2.1704472833 points. You press <<7>> and get 8.4601420045 points. You press <<5>> and get
```

```
Horizon task Data source: [46] Number of experiments: 1 Number of participants: 78 Number of choices: 43680
```

## Example prompt:

You are participating in multiple games involving two slot machines, labeled F and N.

The two slot machines are different across different games.

Each time you choose a slot machine, you get some points.

You choose a slot machine by pressing the corresponding key.

Each slot machine tends to pay out about the same amount of points on average.

Your goal is to choose the slot machines that will give you the most points across the experiment.

The first 4 trials in each game are instructed trials where you will be told which slot machine to choose.

After these instructed trials, you will have the freedom to choose for either 1 or 6 trials.

```
Game 1. There are 5 trials in this game. You are instructed to press F and get 63 points. You are instructed to press N and get 60 points. You are instructed to press N and get 64 points. You are instructed to press N and get 74 points. You press <<N>> and get 65 points. Game 2. There are 10 trials in this game. You are instructed to press N and get 36 points. You are instructed to press N and get 41 points. You are instructed to press F and get 40 points. You are instructed to press F and get 33 points. You press <<N>> and get 44 points. You press <<N>> and get 34 points. You press <<F>> and get 48 points. You press <<F>> and get 50 points. You press <<N>> and get 38 points. You press <<F>> and get 35 points. Game 3. There are 5 trials in this game. You are instructed to press F and get 18 points. You are instructed to press N and get 51 points. You are instructed to press N and get 41 points. You are instructed to press F and get 23 points. You press <<N>> and get 42 points. Game 4. There are 10 trials in this game. You are instructed to press F and get 65 points. You are instructed to press N and get 55 points. You are instructed to press N and get 68 points. You are instructed to press N and get 61 points. You press <<F>> and get 54 points. You press <<N>> and get 74 points. You press <<N>> and get 71 points. You press <<N>> and get 42 points. You press <<F>> and get 63 points. You press <<N>> and get 53 points. Game 5. There are 10 trials in this game. You are instructed to press N and get 18 points. You are instructed to press F and get 53 points. You are instructed to press F and get 50 points.
```

```
You are instructed to press N and get 19 points. You press <<F>> and get 46 points. You press <<F>> and get 44 points. You press <<N>> and get 10 points. You press <<F>> and get 42 points. You press <<F>> and get 39 points. You press <<F>> and get 44 points. Game 6. There are 10 trials in this game. You are instructed to press F and get 13 points. You are instructed to press N and get 51 points. You are instructed to press F and get 1 points. You are instructed to press N and get 36 points. You press <<N>> and get 38 points. You press <<N>> and get 36 points. You press <<N>> and get 52 points. You press <<N>> and get 36 points. You press <<N>> and get 27 points. You press <<F>> and get 12 points. Game 7. There are 5 trials in this game. You are instructed to press F and get 65 points. You are instructed to press N and get 50 points. You are instructed to press F and get 74 points. You are instructed to press F and get 55 points. You press <<N>> and get 72 points. Game 8. There are 10 trials in this game. You are instructed to press N and get 29 points. You are instructed to press F and get 42 points. You are instructed to press F and get 40 points. You are instructed to press F and get 42 points. You press <<F>> and get 53 points. You press <<F>> and get 47 points. You press <<N>> and get 40 points. You press <<N>> and get 41 points. You press <<F>> and get 38 points. You press <<F>> and get 51 points. Game 9. There are 5 trials in this game. You are instructed to press N and get 60 points. You are instructed to press N and get 66 points. You are instructed to press F and get 61 points. You are instructed to press F and get 65 points. You press <<N>> and get 54 points.
```

Game 10. There are 10 trials in this game.

You are instructed to press F and get 44 points.

You are instructed to pr

## Weather prediction task

Data source: [47]

Number of experiments: 1

Number of participants: 23

Number of choices: 4600

## Example prompt:

You will be playing a game in which you pretend to be a weather forecaster.

In each trial, you will see between one and three tarot cards.

Your task is to decide if the combination of cards presented predicts rainy weather (by pressing E) or fine weather (by pressing J).

You are seeing the following: card 2, card 4. You press &lt;&lt;E&gt;&gt;. You are correct, the weather is indeed rainy.

You are seeing the following: card 1, card 2. You press &lt;&lt;J&gt;&gt;. You are correct, the weather is indeed fine.

You are seeing the following: card 3, card 4. You press &lt;&lt;J&gt;&gt;. You are wrong, the weather is rainy.

You are seeing the following: card 2, card 3. You press &lt;&lt;J&gt;&gt;. You are correct, the weather is indeed fine.

You are seeing the following: card 1. You press &lt;&lt;E&gt;&gt;. You are wrong, the weather is fine.

You are seeing the following: card 1, card 2, card 3. You press &lt;&lt;E&gt;&gt;. You are wrong, the weather is fine.

You are seeing the following: card 1, card 2, card 4. You press &lt;&lt;J&gt;&gt;. You are wrong, the weather is rainy.

You are seeing the following: card 1, card 2, card 4. You press &lt;&lt;E&gt;&gt;. You are correct, the weather is indeed rainy.

You are seeing the following: card 3, card 4. You press &lt;&lt;E&gt;&gt;. You are correct, the weather is indeed rainy.

You are seeing the following: card 3, card 4. You press &lt;&lt;E&gt;&gt;. You are correct, the weather is indeed rainy.

You are seeing the following: card 1. You press &lt;&lt;J&gt;&gt;. You are correct, the weather is indeed fine.

You are seeing the following: card 1, card 4. You press &lt;&lt;J&gt;&gt;. You are correct, the weather is indeed fine.

You are seeing the following: card 4. You press &lt;&lt;E&gt;&gt;. You are wrong, the weather is fine.

You are seeing the following: card 3, card 4. You press &lt;&lt;E&gt;&gt;. You are correct, the weather is indeed rainy.

You are seeing the following: card 1, card 2. You press &lt;&lt;J&gt;&gt;. You are correct, the weather is indeed fine.

You are seeing the following: card 3, card 4. You press &lt;&lt;E&gt;&gt;. You are correct, the weather is indeed rainy.

You are seeing the following: card 2. You press &lt;&lt;J&gt;&gt;. You are correct, the weather is indeed fine.

You are seeing the following: card 1, card 4. You press &lt;&lt;J&gt;&gt;. You are wrong, the weather is rainy.

You are seeing the following: card 1, card 4. You press &lt;&lt;J&gt;&gt;. You are correct, the weather is indeed fine.

You are seeing the following: card 1. You press &lt;&lt;J&gt;&gt;. You are correct, the weather is indeed fine.

You are seeing the following: card 1, card 3, card 4. You press &lt;&lt;J&gt;&gt;. You are correct, the weather is indeed fine.

You are seeing the following: card 2. You press &lt;&lt;J&gt;&gt;. You are correct, the weather is indeed fine.

You are seeing the following: card 1, card 2. You press &lt;&lt;J&gt;&gt;. You are correct, the weather is indeed fine.

You are seeing the following: card 2, card 3, card 4. You press &lt;&lt;E&gt;&gt;. You are correct, the weather is indeed rainy.

You are seeing the following: card 3. You press &lt;&lt;J&gt;&gt;. You are correct, the weather is indeed fine.

You are seeing the following: card 1, card 2, card 3. You press &lt;&lt;J&gt;&gt;. You are wrong, the weather is rainy.

You are seeing the following: card 3, card 4. You press &lt;&lt;E&gt;&gt;. You are correct, the weather is indeed rainy.

You are seeing the following: card 1, card 3. You press &lt;&lt;J&gt;&gt;. You are correct, the weather is indeed fine.

You are seeing the following: card 1, card 4. You press &lt;&lt;J&gt;&gt;. You are wrong, the weather is rainy.

You are seeing the following: card 2, card 3, card 4. You press &lt;&lt;E&gt;&gt;. You are wrong, the weather is fine.

You are seeing the following: card 2, card 4. You press &lt;&lt;E&gt;&gt;. You are correct, the weather is indeed rainy.

You are seeing the following: card 4. You press &lt;&lt;J&gt;&gt;. You are wrong, the weather is rainy.

You are seeing the following: card 1, card 2. You press &lt;&lt;J&gt;&gt;. You are correct, the weather is indeed fine.

You are seeing the following: card 1, card 3, card 4. You press &lt;&lt;E&gt;&gt;. You are correct, the weather is indeed rainy.

You are seeing the following: card 4. You press &lt;&lt;J&gt;&gt;. You are wrong, the weather is rainy.

You are seeing the following: card 1, card 2. You press &lt;&lt;J&gt;&gt;. You are correct, the weather is indeed fine.

You are seeing the follow

## Iowa gambling task

```
Data source: [48] Number of experiments: 9 Number of participants: 511 Number of choices: 55435
```

## Example prompt:

You see in front of you four decks of cards labeled H, V, J, and D.

You get a loan of 2000$ of play money.

You have to select one card at a time, from any of the four decks, for 100 trials.

You select a card from a deck by pressing the corresponding key.

After turning a card, you win some money, the amount varies with the deck.

You sometimes also have to pay a penalty, which also varies with the deck.

Your goal is to maximize profit on the loan of the play money.

```
You press <<H>>. You win 100.0$ and lose 200.0$. You press <<H>>. You win 100.0$ and lose 150.0$. You press <<V>>. You win 100.0$ and lose 0.0$. You press <<D>>. You win 50.0$ and lose 250.0$. You press <<J>>. You win 50.0$ and lose 0.0$. You press <<V>>. You win 100.0$ and lose 0.0$. You press <<H>>. You win 100.0$ and lose 0.0$. You press <<V>>. You win 100.0$ and lose 0.0$. You press <<D>>. You win 50.0$ and lose 0.0$. You press <<V>>. You win 100.0$ and lose 0.0$. You press <<J>>. You win 50.0$ and lose 0.0$. You press <<J>>. You win 50.0$ and lose 0.0$. You press <<H>>. You win 100.0$ and lose 300.0$. You press <<V>>. You win 100.0$ and lose 0.0$. You press <<V>>. You win 100.0$ and lose 1250.0$. You press <<D>>. You win 50.0$ and lose 0.0$. You press <<J>>. You win 50.0$ and lose 50.0$. You press <<H>>. You win 100.0$ and lose 0.0$. You press <<V>>. You win 100.0$ and lose 0.0$. You press <<D>>. You win 50.0$ and lose 0.0$. You press <<J>>. You win 50.0$ and lose 0.0$. You press <<D>>. You win 50.0$ and lose 0.0$. You press <<V>>. You win 100.0$ and lose 0.0$. You press <<H>>. You win 100.0$ and lose 0.0$. You press <<D>>. You win 50.0$ and lose 0.0$. You press <<H>>. You win 100.0$ and lose 0.0$. You press <<J>>. You win 50.0$ and lose 50.0$. You press <<D>>. You win 50.0$ and lose 0.0$. You press <<V>>. You win 100.0$ and lose 0.0$.
```

```
You press <<H>>. You win 100.0$ and lose 0.0$. You press <<V>>. You win 100.0$ and lose 0.0$. You press <<D>>. You win 50.0$ and lose 0.0$. You press <<H>>. You win 100.0$ and lose 250.0$. You press <<J>>. You win 50.0$ and lose 50.0$. You press <<D>>. You win 50.0$ and lose 0.0$. You press <<V>>. You win 100.0$ and lose 0.0$. You press <<H>>. You win 100.0$ and lose 350.0$. You press <<V>>. You win 100.0$ and lose 0.0$. You press <<D>>. You win 50.0$ and lose 0.0$. You press <<J>>. You win 50.0$ and lose 0.0$. You press <<H>>. You win 100.0$ and lose 300.0$. You press <<V>>. You win 100.0$ and lose 0.0$. You press <<D>>. You win 50.0$ and lose 0.0$. You press <<V>>. You win 100.0$ and lose 1250.0$. You press <<H>>. You win 100.0$ and lose 0.0$. You press <<V>>. You win 100.0$ and lose 0.0$. You press <<D>>. You win 50.0$ and lose 0.0$. You press <<J>>. You win 50.0$ and lose 50.0$. You press <<H>>. You win 100.0$ and lose 0.0$. You press <<V>>. You win 100.0$ and lose 0.0$. You press <<D>>. You win 50.0$ and lose 0.0$. You press <<J>>. You win 50.0$ and lose 50.0$. You press <<H>>. You win 100.0$ and lose 0.0$. You press <<V>>. You win 100.0$ and lose 0.0$. You press <<D>>. You win 50.0$ and lose 250.0$. You press <<J>>. You win 50.0$ and lose 0.0$. You press <<D>>. You win 50.0$ and lose 0.0$. You press <<V>>. You win 100.0$ and lose 0.0$. You press <<H>>. You win 100.0$ and lose 150.0$. You press <<H>>. You win 100.0$ and lose 200.0$. You press <<H>>. You win 100.0$ and lose 350.0$. You press <<V>>. You win 100.0$ and lose 0.0$. You press <<V>>. You win 100.0$ and lose 0.0$. You press <<V>>. You win 100.0$ and lose 0.0$. You press <<V>>. You win 100.0$ and lose 0.0$. You press <<V>>. You win 100.0$ and lose 0.0$. You press <<V>>. You win 100.0$ and lose 0.0$. You press <<D>>. You win 50.0$ and lose 0.0$. You press <<V>>. You win 100.0$ and lose 0.0$. You press <<V>>. You win 100.0$ and lose 1250.0$. You press <<J>>. You win 50.0$ and lose 0.0$. You press <<J>>. You win 50.0$ and lose 50.0$. You press <<D>>. You win 50.0$ and lose 0.0$. You press <<V>>. You win 100.0$ and lose 0.0$.
```

```
You press <<V>>. You win 100.0$ and lose 0.0$. You press <<V>>. You win 100.0$ and lose 0.0$. You press <<D>>. You win 50.0$ and lose 0.0$. Yo
```

## Virtual subway network

Data source: [49]

Number of experiments: 4

Number of participants: 789

Number of choices: 227923

## Example prompt:

Imagine that you are a tourist and you have to navigate the subway network in an unfamiliar town.

In each round, you will have to navigate from a starting station to a goal station.

Please try to plan your trip as quickly as possible.

During your trip, you will see the name of the current station and its neighboring stations in all four directions.

If there is no neighboring station in a particular direction, there will be a circle instead of a station name.

You can go north by pressing G, west by pressing B, south by pressing V, and east by pressing C.

When you reach the goal station, press Z to end the round and start the next round.

The new starting station is 1 and the goal station is 3.

Your station: 1. Neighboring stations: circle on the north, 2 on the east, circle on the south, and 9 on the west. You press &lt;&lt;B&gt;&gt;.

Your station: 9. Neighboring stations: circle on the north, 1 on the east, 8 on the south, and circle on the west. You press &lt;&lt;V&gt;&gt;.

Your station: 8. Neighboring stations: 9 on the north, circle on the east, 7 on the south, and circle on the west. You press &lt;&lt;V&gt;&gt;.

Your station: 7. Neighboring stations: 8 on the north, 6 on the east, circle on the south, and circle on the west. You press &lt;&lt;C&gt;&gt;.

Your station: 6. Neighboring stations: circle on the north, 5 on the east, circle on the south, and 7 on the west. You press &lt;&lt;C&gt;&gt;.

Your station: 5. Neighboring stations: 4 on the north, circle on the east, circle on the south, and 6 on the west. You press &lt;&lt;G&gt;&gt;.

Your station: 4. Neighboring stations: 3 on the north, circle on the east, 5 on the south, and circle on the west. You press &lt;&lt;G&gt;&gt;.

Your station: 3. Neighboring stations: 2 on the north, circle on the east, 4 on the south, and circle on the west. You press &lt;&lt;Z&gt;&gt;.

You are successful.

The new starting station is 1 and the goal station is 3.

Your station: 1. Neighboring stations: circle on the north, 2 on the east, circle on the south, and 9 on the west. You press &lt;&lt;B&gt;&gt;.

Your station: 9. Neighboring stations: circle on the north, 1 on the east, 8 on the south, and circle on the west. You press &lt;&lt;V&gt;&gt;.

Your station: 8. Neighboring stations: 9 on the north, circle on the east, 7 on the south, and circle on the west. You press &lt;&lt;V&gt;&gt;.

Your station: 7. Neighboring stations: 8 on the north, 6 on the east, circle on the south, and circle on the west. You press &lt;&lt;C&gt;&gt;.

Your station: 6. Neighboring stations: circle on the north, 5 on the east, circle on the south, and 7 on the west. You press &lt;&lt;C&gt;&gt;.

Your station: 5. Neighboring stations: 4 on the north, circle on the east, circle on the south, and 6 on the west. You press &lt;&lt;G&gt;&gt;.

Your station: 4. Neighboring stations: 3 on the north, circle on the east, 5 on the south, and circle on the west. You press &lt;&lt;G&gt;&gt;.

Your station: 3. Neighboring stations: 2 on the north, circle on the east, 4 on the south, and circle on the west. You press &lt;&lt;Z&gt;&gt;.

You are successful.

The new starting station is 4 and the goal station is 6.

Your station: 4. Neighboring stations: 3 on the north, circle on the east, 5 on the south, and circle on the west. You press &lt;&lt;V&gt;&gt;.

Your station: 5. Neighboring stations: 4 on the north, circle on the east, circle on the south, and 6 on the west. You press &lt;&lt;B&gt;&gt;.

Your station: 6. Neighboring stations: circle on the north, 5 on the east, circle on the south, and 7 on the west. You press &lt;&lt;Z&gt;&gt;.

You are successful.

The new starting station is 1 and the goal station is 7.

Your station: 1. Neighboring stations: circle on the north, 2 on the east, circle on the south, and 9 on the west. You press &lt;&lt;B&gt;&gt;.

Your station: 9. Neighboring stations: circle on the north, 1 on the east, 8 on the south, and circle on the west. You press &lt;&lt;V&gt;&gt;.

Your station: 8. Neighboring stations: 9 on the north, circle on the east, 7 on the south, and circle on the west. You press &lt;&lt;V&gt;&gt;.

Your station: 7. Neighboring stations: 8 on the north, 6 on the east, circle on the south, and circle on the west. You press &lt;&lt;Z&gt;&gt;.

You are successful.

The new starting station is 9 and the goal station is 7.

Your station: 9. Neighboring stations: circle

## Multi-task reinforcement learning

Data source: [14]

Number of experiments: 2

Number of participants: 380

Number of choices: 76760

## Example prompt:

You will explore a castle, walking from room to room.

In each room, you will find different amounts of resources: wood, stone, and iron.

In each room, there are three doors that lead to different rooms.

The doors are labeled I, P, and G.

You have to choose the right doors to find the most valuable resources.

You choose a door by pressing the corresponding key.

At the beginning of each round, you will be shown how valuable the resources are.

These values are given as market prices for wood, stone, and iron.

Multiplying the prices with the amounts of resources and adding them up yields a reward.

You want to maximize the cumulative reward.

After every round, you will start in room 0 again and see the new market prices.

The current market prices are 1 for wood, -1 for stone, and 0 for iron.

You are in room 0. You press &lt;&lt;P&gt;&gt; and you find 0 wood, 0 stone, and 0 iron. You get 0 points.

You are in room 2. You press &lt;&lt;P&gt;&gt; and you find 100 wood, 100 stone, and 0 iron. You get 0 points.

The current market prices are -1 for wood, 1 for stone, and 0 for iron.

You are in room 0. You press &lt;&lt;I&gt;&gt; and you find 0 wood, 0 stone, and 0 iron. You get 0 points.

You are in room 1. You press &lt;&lt;G&gt;&gt; and you find 70 wood, 70 stone, and 70 iron. You get 0 points.

The current market prices are -1 for wood, 1 for stone, and 0 for iron.

You are in room 0. You press &lt;&lt;P&gt;&gt; and you find 0 wood, 0 stone, and 0 iron. You get 0 points.

You are in room 2. You press &lt;&lt;G&gt;&gt; and you find 0 wood, 90 stone, and 0 iron. You get 90 points.

The current market prices are -2 for wood, 1 for stone, and 0 for iron.

You are in room 0. You press &lt;&lt;P&gt;&gt; and you find 0 wood, 0 stone, and 0 iron. You get 0 points.

You are in room 2. You press &lt;&lt;G&gt;&gt; and you find 0 wood, 90 stone, and 0 iron. You get 90 points.

The current market prices are 1 for wood, -2 for stone, and 0 for iron.

You are in room 0. You press &lt;&lt;I&gt;&gt; and you find 0 wood, 0 stone, and 0 iron. You get 0 points.

You are in room 1. You press &lt;&lt;G&gt;&gt; and you find 70 wood, 70 stone, and 70 iron. You get -70 points.

The current market prices are -1 for wood, 1 for stone, and 0 for iron.

You are in room 0. You press &lt;&lt;P&gt;&gt; and you find 0 wood, 0 stone, and 0 iron. You get 0 points.

You are in room 2. You press &lt;&lt;G&gt;&gt; and you find 0 wood, 90 stone, and 0 iron. You get 90 points.

The current market prices are 1 for wood, -2 for stone, and 0 for iron.

You are in room 0. You press &lt;&lt;P&gt;&gt; and you find 0 wood, 0 stone, and 0 iron. You get 0 points.

You are in room 2. You press &lt;&lt;G&gt;&gt; and you find 0 wood, 90 stone, and 0 iron. You get -180 points.

The current market prices are 1 for wood, -1 for stone, and 0 for iron.

You are in room 0. You press &lt;&lt;G&gt;&gt; and you find 0 wood, 0 stone, and 0 iron. You get 0 points.

You are in room 3. You press &lt;&lt;P&gt;&gt; and you find 0 wood, 100 stone, and 60 iron. You get -100 points.

The current market prices are 1 for wood, -2 for stone, and 0 for iron.

You are in room 0. You press &lt;&lt;I&gt;&gt; and you find 0 wood, 0 stone, and 0 iron. You get 0 points.

You are in room 1. You press &lt;&lt;G&gt;&gt; and you find 70 wood, 70 stone, and 70 iron. You get -70 points.

The current market prices are -1 for wood, 1 for stone, and 0 for iron.

You are in room 0. You press &lt;&lt;P&gt;&gt; and you find 0 wood, 0 stone, and 0 iron. You get 0 points.

You are in room 2. You press &lt;&lt;G&gt;&gt; and you find 0 wood, 90 stone, and 0 iron. You get 90 points.

The current market prices are 1 for wood, -2 for stone, and 0 for iron.

You are in room 0. You press &lt;&lt;I&gt;&gt; and you find 0 wood, 0 stone, and 0 iron. You get 0 points.

You are in room 1. You press &lt;&lt;G&gt;&gt; and you find 70 wood, 70 stone, and 70 iron. You get -70 points.

The current market prices are -2 for wood, 1 for stone, and 0 for iron.

You are in room 0. You press &lt;&lt;P&gt;&gt; and you find 0 wood, 0 stone, and 0 iron. You get 0 points.

You are in room 2. You press &lt;&lt;G&gt;&gt; and you find 0 wood, 90 stone, and 0 iron. You get 90 points.

The current market prices are 1 for wood, -2 for stone, and 0 for iron.

You are in room 0. You press &lt;&lt;I&gt;&gt; and you find 0 wood, 0 stone, and 0 iron. You get 0 points.

You are in room

## Horizon task

Data source: [50]

Number of experiments: 1

Number of participants: 36

Number of choices: 15290

## Example prompt:

You are participating in multiple games involving two slot machines, labeled M and U.

The two slot machines are different across different games. Each time you choose a slot machine, you get some points.

You choose a slot machine by pressing the corresponding key.

Each slot machine tends to pay out about the same amount of points on average.

Your goal is to choose the slot machines that will give you the most points across the experiment.

The first 4 trials in each game are instructed trials where you will be told which slot machine to choose.

After these instructed trials, you will have the freedom to choose for either 1 or 6 trials.

```
Game 1. There are 10 trials in this game. You are instructed to press U and get 45 points. You are instructed to press M and get 25 points. You are instructed to press U and get 38 points. You are instructed to press M and get 12 points. You press <<U>> and get 38 points. You press <<U>> and get 42 points. You press <<U>> and get 44 points. You press <<U>> and get 35 points. You press <<U>> and get 42 points. You press <<U>> and get 45 points. Game 2. There are 10 trials in this game. You are instructed to press U and get 71 points. You are instructed to press M and get 35 points. You are instructed to press U and get 71 points. You are instructed to press M and get 26 points. You press <<U>> and get 61 points. You press <<U>> and get 55 points. You press <<U>> and get 61 points. You press <<U>> and get 61 points. You press <<U>> and get 67 points. You press <<U>> and get 69 points. Game 3. There are 5 trials in this game. You are instructed to press U and get 50 points. You are instructed to press M and get 43 points. You are instructed to press M and get 46 points. You are instructed to press U and get 45 points. You press <<U>> and get 61 points.
```

Game 4. There are 10 trials in this game.

```
You are instructed to press U and get 52 points. You are instructed to press M and get 51 points. You are instructed to press U and get 57 points. You are instructed to press M and get 54 points. You press <<U>> and get 67 points. You press <<U>> and get 58 points. You press <<U>> and get 68 points. You press <<U>> and get 57 points. You press <<U>> and get 68 points. You press <<U>> and get 65 points. Game 5. There are 10 trials in this game. You are instructed to press U and get 32 points. You are instructed to press M and get 32 points. You are instructed to press M and get 38 points. You are instructed to press U and get 33 points. You press <<M>> and get 37 points. You press <<M>> and get 48 points. You press <<M>> and get 38 points. You press <<M>> and get 49 points. You press <<M>> and get 36 points. You press <<M>> and get 48 points. Game 6. There are 5 trials in this game. You are instructed to press U and get 74 points. You are instructed to press M and get 51 points. You are instructed to press M and get 72 points. You are instructed to press M and get 76 points. You press <<U>> and get 57 points. Game 7. There are 10 trials in this game. You are instructed to press U and get 40 points. You are instructed to press U and get 34 points. You are instructed to press M and get 31 points. You are instructed to press M and get 37 points. You press <<U>> and get 41 points. You press <<U>> and get 43 points. You press <<U>> and get 47 points. You press <<U>> and get 41 points. You press <<U>> and get 44 points. You press <<U>> and get 45 points. Game 8. There are 5 trials in this game. You are instructed to press U and get 56 points. You are instructed to press M and get 59 points.
```

```
You are instructed to press M and get 48 points. You are instructed to press M and get 48 points. You press <<U>> and get 71 points.
```

Game 9. There are 5 trials in this game. You are instructed to press U and get 46 points. You are instructed to press M and get 46 points. You are instructed to press U and get 47 points. You are instructed to press U and get 56 points. You press &lt;&lt;U&gt;&gt; and get 47 points.

Game 10. There are 10 trials in this game.

You are instructed to press M and get 49 points.

You are instructed to p

## Horizon task

Data source: [8] and unpublished data from the authors

Number of experiments: 5

Number of participants: 221

Number of choices: 138875

## Example prompt:

You are participating in multiple games involving two slot machines, labeled C and A.

The two slot machines are different across different games.

Each time you choose a slot machine, you get some points.

You choose a slot machine by pressing the corresponding key.

Each slot machine tends to pay out about the same amount of points on average.

Your goal is to choose the slot machines that will give you the most points across the experiment.

The first 4 trials in each game are instructed trials where you will be told which slot machine to choose.

After these instructed trials, you will have the freedom to choose for either 1 or 6 trials.

```
Game 1. There are 5 trials in this game. You are instructed to press A and get 66 points. You are instructed to press A and get 80 points. You are instructed to press C and get 29 points. You are instructed to press A and get 75 points. You press <<A>> and get 81 points.
```

Game 2. There are 10 trials in this game.

You are instructed to press A and get 69 points.

```
You are instructed to press A and get 50 points. You are instructed to press C and get 51 points. You are instructed to press A and get 64 points. You press <<C>> and get 42 points. You press <<A>> and get 54 points. You press <<A>> and get 64 points. You press <<A>> and get 64 points. You press <<A>> and get 57 points. You press <<C>> and get 55 points. Game 3. There are 10 trials in this game. You are instructed to press A and get 31 points. You are instructed to press C and get 43 points. You are instructed to press A and get 26 points. You are instructed to press C and get 36 points. You press <<C>> and get 26 points. You press <<C>> and get 41 points. You press <<C>> and get 44 points. You press <<C>> and get 44 points. You press <<C>> and get 43 points. You press <<C>> and get 53 points. Game 4. There are 10 trials in this game. You are instructed to press C and get 65 points. You are instructed to press A and get 77 points. You are instructed to press A and get 52 points. You are instructed to press C and get 73 points. You press <<C>> and get 61 points. You press <<C>> and get 81 points. You press <<C>> and get 70 points. You press <<C>> and get 67 points. You press <<A>> and get 62 points. You press <<C>> and get 68 points. Game 5. There are 10 trials in this game. You are instructed to press A and get 70 points. You are instructed to press C and get 19 points. You are instructed to press A and get 43 points. You are instructed to press C and get 41 points. You press <<A>> and get 53 points. You press <<C>> and get 19 points. You press <<A>> and get 61 points. You press <<A>> and get 68 points. You press <<A>> and get 62 points. You press <<C>> and get 46 points.
```

```
Game 6. There are 10 trials in this game. You are instructed to press C and get 63 points. You are instructed to press A and get 44 points. You are instructed to press C and get 49 points. You are instructed to press C and get 47 points. You press <<A>> and get 52 points. You press <<A>> and get 52 points. You press <<C>> and get 55 points. You press <<A>> and get 51 points. You press <<A>> and get 34 points. You press <<C>> and get 56 points. Game 7. There are 5 trials in this game. You are instructed to press C and get 61 points. You are instructed to press A and get 44 points. You are instructed to press A and get 41 points. You are instructed to press A and get 47 points. You press <<A>> and get 29 points. Game 8. There are 5 trials in this game. You are instructed to press C and get 51 points. You are instructed to press A and get 76 points. You are instructed to press C and get 54 points. You are instructed to press A and get 84 points. You press <<C>> and get 58 points. Game 9. There are 10 trials in this game. You are instructed to press C and get 54 points. You are instructed to press A and get 14 points. You are instructed to press A and get 15 points. You are instructed to press C and get 46 points. You press <<A>> and get 20 points. You press <<C>> and get 44 points. You press <<A>> and get 16 points. You press <<C>> and get 46 points.
```

## You press Aversive learning Data source: [51] Number of experiments: 1 Number of participants: 57 Number of choices: 18240

## Example prompt:

You are going to predict the probability of electric shocks associated with two visual stimuli.

First, you will have to indicate the probability that a stimulus predicts a shock at the current moment in time on a rating bar (between 0 and 100 percent).

After that, the outcome for each stimulus will be presented visually.

An upcoming shock will be indicated by a square over the stimulus, while a no-shock outcome will be indicated by a circle.

Finally, shocks will be delivered after you have learned about the outcome visually. If both stimuli indicate a shock, they will be presented one after the other in random order.

The shock probability fluctuates over time such that one stimulus has a stable probability while the other varies.

Stimulus J and K are shown on the screen. You predict that the shock probability for stimulus J is &lt;&lt;50.0&gt;&gt;% and the shock probability for stimulus K is &lt;&lt;50.0&gt;&gt;%. After that, a circle is shown over stimulus J, and a square is shown over stimulus K. Finally, a shock is delivered for stimulus K.

Stimulus J and K are shown on the screen. You predict that the shock probability for stimulus J is &lt;&lt;50.0&gt;&gt;% and the shock probability for stimulus K is &lt;&lt;59.33&gt;&gt;%. After that, a square is shown over stimulus J, and a circle is shown over stimulus K. Finally, a shock is delivered for stimulus J.

Stimulus J and K are shown on the screen. You predict that the shock probability for stimulus J is &lt;&lt;55.72&gt;&gt;% and the shock probability for stimulus K is &lt;&lt;59.33&gt;&gt;%. After that, a circle is shown over stimulus J, and a circle is shown over stimulus K. Finally, no shocks are delivered.

Stimulus J and K are shown on the screen. You predict that the shock probability for stimulus J is &lt;&lt;55.72&gt;&gt;% and the shock probability for stimulus K is &lt;&lt;59.33&gt;&gt;%. After that, a circle is shown over stimulus J, and a circle is shown over stimulus K. Finally, no shocks are delivered.

Stimulus J and K are shown on the screen. You predict that the shock probability for stimulus J is &lt;&lt;55.72&gt;&gt;% and the shock probability for stimulus K is &lt;&lt;59.33&gt;&gt;%. After that, a circle is shown over stimulus J, and a circle is shown over stimulus K. Finally, no shocks are delivered.

Stimulus J and K are shown on the screen. You predict that the shock probability for stimulus J is &lt;&lt;55.72&gt;&gt;% and the shock probability for stimulus K is &lt;&lt;59.33&gt;&gt;%. After that, a circle is shown over stimulus J, and a square is shown over stimulus K. Finally, a shock is delivered for stimulus K.

Stimulus J and K are shown on the screen. You predict that the shock probability for stimulus J is &lt;&lt;55.72&gt;&gt;% and the shock probability for stimulus K is &lt;&lt;62.42&gt;&gt;%. After that, a circle is shown over stimulus J, and a circle is shown over stimulus K. Finally, no shocks are delivered.

Stimulus J and K are shown on the screen. You predict that the shock probability for stimulus J is &lt;&lt;55.72&gt;&gt;% and the shock probability for stimulus K is &lt;&lt;62.42&gt;&gt;%. After that, a circle is shown over stimulus J, and a circle is shown over stimulus K. Finally, no shocks are delivered.

Stimulus J and K are shown on the screen. You predict that the shock probability for stimulus J is &lt;&lt;55.72&gt;&gt;% and the shock probability for stimulus K is &lt;&lt;62.42&gt;&gt;%. After that, a square is shown over stimulus J, and a square is shown over stimulus K. Finally, shocks are delivered for both stimulus J and stimulus K.

Stimulus J and K are shown on the screen. You predict that the shock probability for stimulus J is &lt;&lt;58.2&gt;&gt;% and the shock probability for stimulus K is &lt;&lt;65.0&gt;&gt;%. After that, a circle is shown over stimulus J, and a square is shown over stimulus K. Finally, a shock is delivered for stimulus K.

Stimulus J and K are shown on the screen. You predict that the shock probability for stimulus J is &lt;&lt;58.2&gt;&gt;% and the shock probability for stimulus K is &lt;&lt;67.48&gt;&gt;%. After that, a circle is shown over stimulus J, and a circle is shown over stimulus K. Finally, no shocks are delivered.

Stimulus J and K are shown on the screen. You predict that the shock probability for stimulus J is &lt;&lt;58.2&gt;&gt;% and the shock probability

## Spatially correlated multi-armed bandit

Data source: [15]

Number of experiments: 1

Number of participants: 78

Number of choices: 9360

## Example prompt:

You will be presented with a series of 16 different environments to explore.

In each trial, you can select an option between numbers 1 and 30 by pressing the corresponding key.

By selecting any of these options, you will earn points associated with each unique option.

Imagine these options 1 through 30 as lying next to each other in an ordered line; options closer to each other tend to have similar rewards as rewards tend to cluster together.

For each environment, you will be able to make either 5 or 10 choices.

When you made all your choices in a given environment, you will start making choices in the next unexplored environment.

The rewards underlying the different options are different in each environment so you will learn them anew for each environment.

Each environment starts with the value of a single option revealed.

When you choose the number corresponding to a different option, you will be told the value of that option and receive those points.

Previously revealed options, including the starting option, can also be reselected, although there may be small changes in the point value.

It is your task to gain as many points as possible across all 16 environments.

## Environment number 1:

The value of option 4 is 76. You have 5 choices to make in this environment.

```
You press <<5>> and receive 61 points. You press <<3>> and receive 64 points. You press <<6>> and receive 42 points. You press <<2>> and receive 49 points. You press <<11>> and receive 22 points. Environment number 2: The value of option 2 is 65. You have 10 choices to make in this environment. You press <<3>> and receive 68 points. You press <<1>> and receive 40 points. You press <<9>> and receive 10 points. You press <<17>> and receive 51 points. You press <<18>> and receive 35 points. You press <<16>> and receive 54 points. You press <<14>> and receive 48 points. You press <<23>> and receive 64 points. You press <<22>> and receive 53 points. You press <<23>> and receive 65 points. Environment number 3: The value of option 22 is 37. You have 5 choices to make in this environment. You press <<13>> and receive 30 points. You press <<7>> and receive 67 points. You press <<8>> and receive 77 points. You press <<6>> and receive 32 points. You press <<9>> and receive 57 points. Environment number 4: The value of option 16 is 34. You have 10 choices to make in this environment. You press <<5>> and receive 77 points. You press <<6>> and receive 53 points. You press <<4>> and receive 79 points. You press <<3>> and receive 41 points. You press <<22>> and receive 25 points. You press <<29>> and receive 41 points. You press <<26>> and receive 46 points. You press <<12>> and receive 64 points. You press <<11>> and receive 41 points. You press <<13>> and receive 55 points. Environment number 5: The value of option 19 is 26. You have 5 choices to make in this environment. You press <<8>> and receive 42 points. You press <<3>> and receive 44 points. You press <<24>> and receive 37 points.
```

```
You press <<29>> and receive 35 points. You press <<15>> and receive 48 points. Environment number 6: The value of option 16 is 44. You have 10 choices to make in this environment. You press <<9>> and receive 32 points. You press <<4>> and receive 43 points. You press <<21>> and receive 26 points. You press <<26>> and receive 5 points. You press <<1>> and receive 13 points. You press <<6>> and receive 9 points. You press <<12>> and receive 27 points. You press <<18>> and receive 36 points. You press <<23>> and receive 23 points. You press <<17>> and receive 21 points. Environment number 7: The value of option 2 is 36. You have 5 choices to make in this environment. You press <<9>> and receive 49 points. You press <<16>> and receive 72 points. You press <<17>> and receive 59 points. You press <<15>> and receive 49 points. You press <<17>> and receive 58 points. Environment number 8: The value of option 9 is 66. You have 10 choices to make in this environment. You press <<10>> and receive 66 points. You press <<8>> and receive 37 points. You press <<11>> and receive 38 points. You pr Serial reaction time task Data source: [52] Number of experiments: 2 Number of participants: 238 Number of choices: 238000 Example prompt: Press the instructed key. Act as fast and accurately as possible. The instruction is to press D, you press <<D>> in 1375 ms. That is correct. The instruction is to press K, you press <<K>> in 1960 ms. That is correct.
```

- The instruction is to press J, you press &lt;&lt;J&gt;&gt; in 1043 ms. That is correct.

```
The instruction is to press F, you press <<F>> in 718 ms. That is correct. The instruction is to press D, you press <<D>> in 568 ms. That is correct. The instruction is to press K, you press <<K>> in 527 ms. That is correct. The instruction is to press J, you press <<J>> in 587 ms. That is correct. The instruction is to press K, you press <<K>> in 565 ms. That is correct. The instruction is to press J, you press <<J>> in 541 ms. That is correct. The instruction is to press F, you press <<F>> in 631 ms. That is correct. The instruction is to press D, you press <<D>> in 456 ms. That is correct. The instruction is to press K, you press <<K>> in 480 ms. That is correct. The instruction is to press J, you press <<J>> in 627 ms. That is correct. The instruction is to press J, you press <<J>> in 1816 ms. That is correct. The instruction is to press F, you press <<F>> in 731 ms. That is correct. The instruction is to press D, you press <<D>> in 563 ms. That is correct. The instruction is to press K, you press <<K>> in 401 ms. That is correct. The instruction is to press J, you press <<J>> in 472 ms. That is correct. The instruction is to press D, you press <<D>> in 414 ms. That is correct. The instruction is to press K, you press <<K>> in 412 ms. That is correct. The instruction is to press J, you press <<J>> in 439 ms. That is correct. The instruction is to press F, you press <<F>> in 612 ms. That is correct. The instruction is to press K, you press <<K>> in 468 ms. That is correct. The instruction is to press J, you press <<J>> in 497 ms. That is correct. The instruction is to press F, you press <<F>> in 397 ms. That is correct. The instruction is to press D, you press <<D>> in 318 ms. That is correct. The instruction is to press K, you press <<K>> in 374 ms. That is correct. The instruction is to press J, you press <<J>> in 327 ms. That is correct. The instruction is to press F, you press <<F>> in 604 ms. That is correct. The instruction is to press D, you press <<D>> in 300 ms. That is correct. The instruction is to press K, you press <<K>> in 555 ms. That is correct. The instruction is to press J, you press <<J>> in 314 ms. That is correct. The instruction is to press K, you press <<K>> in 441 ms. That is correct. The instruction is to press J, you press <<J>> in 474 ms. That is correct. The instruction is to press F, you press <<D>> in 394 ms. That is incorrect. The instruction is to press K, you press <<K>> in 586 ms. That is correct. The instruction is to press K, you press <<K>> in 528 ms. That is correct. The instruction is to press J, you press <<J>> in 466 ms. That is correct. The instruction is to press F, you press <<F>> in 434 ms. That is correct. The instruction is to press D, you press <<D>> in 355 ms. That is correct. The instruction is to press J, you press <<K>> in 390 ms. That is incorrect. The instruction is to press F, you press <<F>> in 769 ms. That is correct. The instruction is to press D, you press <<D>> in 416 ms. That is correct. The instruction is to press K, you press <<K>> in 395 ms. That is correct. The instruction is to press K, you press <<K>> in 601 ms. That is correct. The instruction is to press J, you press <<J>> in 475 ms. That is correct. The instruction is to press J, you press <<J>> in 549 ms. That is correct.
```

```
The instruction is to press F, you press <<F>> in 438 ms. That is correct. The instruction is to press D, you press <<D>> in 327 ms. That is correct. The instruction is to press K, you press <<K>> in 438 ms. That is correct. The instruction is to press J, you press <<J>> in 342 ms. That is correct. The instruction is to press F, you press <<F>> in 456 ms. That is correct. The instruction is to press D, you press <<D>> in 380 ms. That is correct. The instruction is to press K, you press <<K¿ Decisions from description Data source: [53] Number of experiments: 1 Number of participants: 1981 Number of choices: 28153 Example prompt: You will choose from two monetary lotteries by pressing W or H. The lotteries offer different points with different probabilities. Your choice will trigger a random draw from the chosen lottery that will be added to your bonus. Your goal is to maximize your bonus. You will be presented with multiple choice problems consisting of different lotteries varying in outcomes and probabilities. Lottery W offers 4.0 points with 80.0% probability or 0.0 points with 20.0% probability. Lottery H offers 3.0 points with 100.0% probability. You press <<H>>. Lottery W offers 4.0 points with 20.0% probability or 0.0 points with 80.0% probability. Lottery H offers 3.0 points with 25.0% probability, or 0.0 points with 75.0% probability. You press <<H>>. Lottery W offers -3.0 points with 100.0% probability. Lottery H offers -32.0 points with 10.0% probability, or 0.0 points with 90.0% probability. You press <<W>>. Decisions from experience Data source: [53] Number of experiments: 79
```

Number of participants: 3942

## Example prompt:

You can sample from two monetary lotteries by pressing K or D.

The lotteries offer different points with different probabilities.

Initially, you will not know the outcomes and probabilities of the lotteries, but you can learn about them through sampling.

Whenever you sample, a random draw from the selected lottery will be generated, which does not affect your bonus.

You can sample from the lotteries in whatever order and for as long as you like.

Whenever you feel ready, you can stop sampling by pressing X and then choose one lottery for real by pressing the corresponding key.

This choice will then trigger a random draw from the chosen lottery that will be added to your bonus.

Your goal is to maximize your bonus.

You will be presented with multiple choice problems consisting of different lotteries varying in outcomes and probabilities.

You encounter a new choice problem:

```
You press <<K>> and observe 4.0 points. You press <<K>> and observe 4.0 points. You press <<K>> and observe 4.0 points. You press <<K>> and observe 4.0 points. You press <<K>> and observe 0.0 points. You press <<K>> and observe 4.0 points. You press <<K>> and observe 4.0 points. You press <<K>> and observe 4.0 points. You press <<K>> and observe 4.0 points. You press <<K>> and observe 4.0 points. You press <<K>> and observe 0.0 points. You press <<K>> and observe 4.0 points. You press <<D>> and observe 3.0 points. You press <<D>> and observe 3.0 points. You press <<D>> and observe 3.0 points. You press <<D>> and observe 3.0 points. You press <<D>> and observe 3.0 points. You press <<D>> and observe 3.0 points. You press <<D>> and observe 3.0 points. You press <<D>> and observe 3.0 points. You press <<D>> and observe 3.0 points. You press <<D>> and observe 3.0 points. You press <<D>> and observe 3.0 points. You press <<D>> and observe 3.0 points. You press <<D>> and observe 3.0 points. You press <<D>> and observe 3.0 points.
```

```
You press <<D>> and observe 3.0 points. You press <<D>> and observe 3.0 points. You press <<K>> and observe 4.0 points. You press <<K>> and observe 4.0 points. You press <<K>> and observe 4.0 points. You press <<K>> and observe 4.0 points. You press <<K>> and observe 0.0 points. You press <<K>> and observe 4.0 points. You press <<X>> to stop sampling and then press <<K>>. You encounter a new choice problem: You press <<K>> and observe 0.0 points. You press <<K>> and observe 0.0 points. You press <<K>> and observe 0.0 points. You press <<D>> and observe 0.0 points. You press <<D>> and observe 0.0 points. You press <<D>> and observe 0.0 points. You press <<D>> and observe 0.0 points. You press <<D>> and observe 3.0 points. You press <<K>> and observe 0.0 points. You press <<K>> and observe 0.0 points. You press <<K>> and observe 4.0 points. You press <<K>> and observe 0.0 points. You press <<K>> and observe 0.0 points. You press <<K>> and observe 0.0 points. You press <<K>> and observe 0.0 points. You press <<K>> and observe 4.0 points. You press <<K>> and observe 0.0 points. You press <<K>> and observe 4.0 points. You press <<K>> and observe 0.0 points. You press <<K>> and observe 0.0 points. You press <<K>> and observe 0.0 points. You press <<K>> and observe 0.0 points. You press <<K>> and observe 0.0 points. You press <<K>> and observe 0.0 points. You press <<K>> and observe 0.0 points. You press <<K>> and observe 0.0 points. You press <<K>> and observe 0.0 points. You press <<K>> and observe 0.0 points. You press <<K>> and observe 0.0 points. You press <<D>> and observe 0.0 points. You press <<D>> and observe 0.0 points. You press <<D>> and observe 0.0 points. You press <<D>> and observe 3.0 points. You press <<D>> and observe 0.0 points.
```

```
You press <<D>> and observe 0.0 points. You press <<D>> and observe 0.0 points. You press <<D>> and observe 0.0 points. You press <<D>> and observe 0.0 points. You press <<D>> and observe 0.0 points. You press <<D>> and observe 3.0 points. You press <<D>> and observe 0.0 points. You press <<D>> and observe 0.0 points. You press <<D>> and observe 0.0 points. You press <<D>> and observe 0.0 points.
```

## Changing bandit

Data source: [54]

```
Number of experiments: 1 Number of participants: 30 Number of choices: 141000
```

## Example prompt:

You are participating in multiple games involving two slot machines, labeled M and V.

The two slot machines are different in different games.

Each time you choose a slot machine, you get points (choosing the same slot machine will not always give you the same points).

You select a slot machine by pressing the corresponding key.

The expected points change randomly, abruptly, and independently with a hazard rate (which you will be told).

When the points change, the new expected point value assigned to that slot machine is sampled from a uniform distribution (from 1 to 99 points).

For example, if the hazard rate is 0.1, the expected points of the machines change with 10%.

Your goal is to choose the slot machine that will give you the most points.

```
Game 1. The hazard rate is 0.1. There are 100 trials in this game. You press <<M>> and get 65 points. You press <<V>> and get 58 points. You press <<M>> and get 65 points. You press <<M>> and get 65 points. You press <<V>> and get 5 points. You press <<M>> and get 65 points. You press <<M>> and get 65 points. You press <<M>> and get 65 points. You press <<V>> and get 60 points. You press <<M>> and get 65 points. You press <<M>> and get 65 points.
```

```
You press <<V>> and get 39 points. You press <<M>> and get 65 points. You press <<M>> and get 65 points. You press <<M>> and get 65 points. You press <<M>> and get 65 points. You press <<V>> and get 87 points. You press <<V>> and get 82 points. You press <<V>> and get 82 points. You press <<V>> and get 56 points. You press <<M>> and get 65 points. You press <<M>> and get 65 points. You press <<M>> and get 65 points. You press <<M>> and get 65 points. You press <<V>> and get 28 points. You press <<M>> and get 65 points. You press <<M>> and get 65 points. You press <<M>> and get 65 points. You press <<M>> and get 65 points. You press <<M>> and get 65 points. You press <<M>> and get 65 points. You press <<M>> and get 65 points. You press <<M>> and get 65 points. You press <<M>> and get 65 points. You press <<M>> and get 65 points. You press <<M>> and get 65 points. You press <<M>> and get 65 points. You press <<M>> and get 65 points. You press <<M>> and get 10 points. You press <<V>> and get 28 points. You press <<V>> and get 28 points. You press <<V>> and get 28 points. You press <<V>> and get 28 points. You press <<V>> and get 28 points. You press <<V>> and get 28 points. You press <<V>> and get 28 points. You press <<M>> and get 13 points. You press <<V>> and get 28 points. You press <<V>> and get 28 points. You press <<V>> and get 28 points. You press <<V>> and get 28 points. You press <<V>> and get 28 points. You press <<M>> and get 13 points. You press <<V>> and get 29 points. You press <<M>> and get 88 points. You press <<M>> and get 88 points.
```

```
You press <<M>> and get 88 points. You press <<M>> and get 88 points. You press <<M>> and get 88 points. You press <<M>> and get 88 points. You press <<V>> and get 47 points. You press <<M>> and get 88 points. You press <<M>> and get 53 points. You press <<V>> and get 18 points. You press <<M>> and get 3 points. You press <<V>> and get 18 points. You press <<V>> and get 18 points. You press <<V>> and get 18 points. You press <<V>> and get 18 points. You press <<V>> and get 18 points. You press <<V>> and get 18 points. You press <<V>> and get 18 points. You press <<M>> and get 49 points. You press <<M>> and get 49 points. You press <<M>> and get 49 points. You press <<M>> and get 49 points. You press <<M>> and get 49 points. You press <<M>> and get 49 points. You press <<M>> and get 49 points. You press <<M>> and get 49 points. You press <<V>> and get 71 points. You press <<V>> and get 71 points. You press <<M>> and get 68 points. You press <<V>> and get 59 points. You press <<M>> and get 68 points. You press <<M>> and get 68 points. You press <<M>> and get 68 points. You press <<M>> and get 68 points. You press <<M>> and get 68 points. You press <<M>> and get 68 points. You press <<M>> and get 68 points. You press <<M>> and get 68 points. You press <<M>> and get 68 points. You press <<M>> and g
```

## Probabilistic reasoning

Data source: [55]

Number of experiments: 2

Number of participants: 128

Number of choices: 19740

## Example prompt:

You have to estimate the probability of a series of weather-related queries.

Please respond by typing your estimated probabilities.

What is the probability that the weather will be icy and not frosty on a random day in England? You estimate &lt;&lt;20&gt;&gt;%.

What is the probability that the weather will be not normal or not typical on a random day in England? You estimate &lt;&lt;50&gt;&gt;%.

What is the probability that the weather will be not frosty on a random day in England? You estimate &lt;&lt;65&gt;&gt;%.

If the weather in England is not frosty on a random day, what is the probability that the weather will also be not icy on the same day? You estimate &lt;&lt;40&gt;&gt;%.

If the weather in England is icy on a random day, what is the probability that the weather will also be not frosty on the same day? You estimate &lt;&lt;20&gt;&gt;%.

If the weather in England is typical on a random day, what is the probability that the weather will also be normal on the same day? You estimate &lt;&lt;50&gt;&gt;%.

What is the probability that the weather will be icy and frosty on a random day in England? You estimate &lt;&lt;35&gt;&gt;%.

What is the probability that the weather will be normal on a random day in England? You estimate &lt;&lt;50&gt;&gt;%.

What is the probability that the weather will be icy or frosty on a random day in England? You estimate &lt;&lt;35&gt;&gt;%.

What is the probability that the weather will be not icy or not frosty on a random day in England? You estimate &lt;&lt;60&gt;&gt;%.

If the weather in England is not typical on a random day, what is the probability that the weather will also be not normal on the same day? You estimate &lt;&lt;40&gt;&gt;%.

What is the probability that the weather will be normal and typical on a random day in England? You estimate &lt;&lt;30&gt;&gt;%.

What is the probability that the weather will be not normal on a random day in England? You estimate &lt;&lt;20&gt;&gt;%.

If the weather in England is not frosty on a random day, what is the probability that the weather will also be icy on the same day? You estimate &lt;&lt;20&gt;&gt;%.

If the weather in England is not normal on a random day, what is the probability that the weather will also be typical on the same day? You estimate &lt;&lt;40&gt;&gt;%.

If the weather in England is icy on a random day, what is the probability that the weather will also be frosty on the same day? You estimate &lt;&lt;60&gt;&gt;%.

If the weather in England is not icy on a random day, what is the probability that the weather will also be not frosty on the same day? You estimate &lt;&lt;60&gt;&gt;%.

What is the probability that the weather will be typical on a random day in England? You estimate &lt;&lt;70&gt;&gt;%.

What is the probability that the weather will be typical or not normal on a random day in England? You estimate &lt;&lt;50&gt;&gt;%.

What is the probability that the weather will be typical and not normal on a random day in England? You estimate &lt;&lt;30&gt;&gt;%.

What is the probability that the weather will be not normal and not typical on a random day in England? You estimate &lt;&lt;40&gt;&gt;%.

If the weather in England is frosty on a random day, what is the probability that the weather will also be not icy on the same day? You estimate &lt;&lt;60&gt;&gt;%.

What is the probability that the weather will be frosty or not icy on a random day in England? You estimate &lt;&lt;65&gt;&gt;%.

If the weather in England is not typical on a random day, what is the probability that the weather will also be normal on the same day? You estimate &lt;&lt;34&gt;&gt;%.

If the weather in England is normal on a random day, what is the probability that the weather will also be not typical on the same day? You estimate &lt;&lt;45&gt;&gt;%.

If the weather in England is normal on a random day, what is the probability that the weather will also be typical on the same day? You estimate &lt;&lt;10&gt;&gt;%.

What is the probability that the weather will be icy or not frosty on a random day in England? You estimate &lt;&lt;40&gt;&gt;%.

What is the probability that the weather will be frosty on a random day in England? You estimate &lt;&lt;40&gt;&gt;%.

If the weather in England is frosty on a random day, what is the probability that the weather will also be icy on the same day? You estimate &lt;&lt;40&gt;&gt;%.

If the weather in England is not icy on a random day, what is the probability that the wea

## Two-step task

Data source: [56]

Number of experiments: 1

Number of participants: 139

Number of choices: 55878

## Example prompt:

You are participating in a space treasure game.

In this game, you will be visiting two alien planets in search of treasure.

Each planet has two aliens on it.

The blue aliens live on the blue planet.

The red aliens live on the red planet.

When you visit a planet, you can choose an alien to trade with by pressing the corresponding button.

When you trade with an alien, it will either give you treasure or junk.

Your goal is to figure out, and trade with, the aliens that are most likely to give you treasure.

To visit a planet, you will choose one rocket ship from two by pressing the corresponding button.

They have different designations.

Each rocket ship has a planet it will fly to most of the time.

But sometimes they will take you to the other planet!

Remember the following hints:

1. How likely an alien is to give you treasure will change over time, but this change will be slow.

2. Whether you get treasure depends only on the alien you choose to trade with.

3. If there is an alien you want to trade with, remember to pick the rocket ship that is most likely to take you to that alien's planet.

You are presented with two spaceships called S and C. You press &lt;&lt;S&gt;&gt;. You end up on the blue planet. You see a blue alien named D and a blue alien named R. You press &lt;&lt;R&gt;&gt;. You find junk.

You are presented with two spaceships called S and C. You press &lt;&lt;S&gt;&gt;. You end up on the blue planet. You see a blue alien named D and a blue alien named R. You press &lt;&lt;D&gt;&gt;. You find treasure.

You are presented with two spaceships called S and C. You press &lt;&lt;S&gt;&gt;. You end up on the blue planet. You see a blue alien named D and a blue alien named R. You press &lt;&lt;D&gt;&gt;. You find junk.

You are presented with two spaceships called S and C. You press &lt;&lt;C&gt;&gt;. You end up on the red planet. You see a red alien named G and a red alien named V. You press &lt;&lt;V&gt;&gt;. You find junk.

You are presented with two spaceships called S and C. You press &lt;&lt;S&gt;&gt;. You end up on the red planet. You see a red alien named G and a red alien named V. You press &lt;&lt;G&gt;&gt;. You find treasure.

You are presented with two spaceships called S and C. You press &lt;&lt;S&gt;&gt;. You end up on the blue planet. You see a blue alien named D and a blue alien named R. You press &lt;&lt;D&gt;&gt;. You find junk.

You are presented with two spaceships called S and C. You press &lt;&lt;S&gt;&gt;. You end up on the blue planet. You see a blue alien named D and a blue alien named R. You press &lt;&lt;R&gt;&gt;. You find junk.

You are presented with two spaceships called S and C. You press &lt;&lt;C&gt;&gt;. You end up on the red planet. You see a red alien named G and a red alien named V. You press &lt;&lt;G&gt;&gt;. You find junk.

You are presented with two spaceships called S and C. You press &lt;&lt;C&gt;&gt;. You end up on the blue planet. You see a blue alien named D and a blue alien named R. You press &lt;&lt;D&gt;&gt;. You find junk.

You are presented with two spaceships called S and C. You press &lt;&lt;S&gt;&gt;. You end up on the blue planet. You see a blue alien named D and a blue alien named R. You press &lt;&lt;R&gt;&gt;. You find treasure.

You are presented with two spaceships called S and C. You press &lt;&lt;S&gt;&gt;. You end up on the red planet. You see a red alien named G and a red alien named V. You press &lt;&lt;V&gt;&gt;. You find treasure.

You are presented with two spaceships called S and C. You press &lt;&lt;S&gt;&gt;. You end up on the red planet. You see a red alien named G and a red alien named V. You press &lt;&lt;V&gt;&gt;. You find treasure.

You are presented with two spaceships called S and C. You press &lt;&lt;S&gt;&gt;. You end up on the blue planet. You see a blue alien named D and a blue alien named R. You press &lt;&lt;D&gt;&gt;. You find treasure.

You are presented with two spaceships called S and C. You press &lt;&lt;S&gt;&gt;. You end up on the blue planet. You see a blue alien named D and a blue alien named R. You press &lt;&lt;R&gt;&gt;. You find junk.

You are presented with two spaceships called S and C. You press &lt;&lt;S&gt;&gt;. You end up on the red planet. You see a red alien named G and a red alien named V. You press &lt;&lt;V&gt;&gt;. You find junk.

You are presented with two spaceships called S and C. You press &lt;&lt;S&gt;&gt;. You end up on the blue planet. You see a blue alien named D and a blue alien

## Evaluation data

## Two-step task (modified cover story)

Data source: [57]

Number of experiments: 1 Number of participants: 24 Number of choices: 9702

## Example prompt:

You are playing the role of a musician living in a fantasy land.

You play the flute for gold coins to an audience of genies, who live inside magic lamps on Pink Mountain and Blue Mountain.

Pink Mountain has genies H and J, and Blue Mountain has genies A and E.

Each genie lives in a lamp with the corresponding letter on it.

When you arrive on a mountain, you can pick up a lamp and rub it.

If the genie is in the mood for music, he will come out of his lamp, listen to a song, and give you a gold coin.

Each genie's interest in music changes with time.

To go to the mountains, you chose one of two magic carpets, which you purchase from a magician, who enchants them to fly.

Magic carpet K generally flies to Pink Mountain, and magic carpet O generally flies to Blue Mountain.

However, on rare occasions a strong wind blowing from that mountain makes flying there too dangerous because the wind might blow you off the carpet.

In this case, the carpet is forced to land instead on the other mountain.

You can take a magic carpet or pick up a lamp and rub it by pressing the corresponding key.

Your goal is to get as many coins as possible over the next 201 days.

You are presented with magic carpets K and O. You press &lt;&lt;K&gt;&gt;. You end up on Pink Mountain. You see lamp H and lamp J. You rub lamp &lt;&lt;H&gt;&gt;. You receive 0 coins.

You are presented with magic carpets O and K. You press &lt;&lt;K&gt;&gt;. You end up on Pink Mountain. You see lamp H and lamp J. You rub lamp &lt;&lt;J&gt;&gt;. You receive 1

coins.

You are presented with magic carpets K and O. You press &lt;&lt;K&gt;&gt;. You end up on Pink Mountain. You see lamp H and lamp J. You rub lamp &lt;&lt;J&gt;&gt;. You receive 1 coins.

You are presented with magic carpets O and K. You press &lt;&lt;K&gt;&gt;. You end up on Pink Mountain. You see lamp H and lamp J. You rub lamp &lt;&lt;J&gt;&gt;. You receive 1 coins.

You are presented with magic carpets K and O. You press &lt;&lt;K&gt;&gt;. You end up on Pink Mountain. You see lamp H and lamp J. You rub lamp &lt;&lt;J&gt;&gt;. You receive 0 coins.

You are presented with magic carpets O and K. You press &lt;&lt;O&gt;&gt;. You end up on Blue Mountain. You see lamp A and lamp E. You rub lamp &lt;&lt;A&gt;&gt;. You receive 1 coins.

You are presented with magic carpets O and K. You press &lt;&lt;O&gt;&gt;. You end up on Blue Mountain. You see lamp A and lamp E. You rub lamp &lt;&lt;A&gt;&gt;. You receive 0 coins.

You are presented with magic carpets K and O. You press &lt;&lt;O&gt;&gt;. You end up on Blue Mountain. You see lamp A and lamp E. You rub lamp &lt;&lt;E&gt;&gt;. You receive 1 coins.

You are presented with magic carpets K and O. You press &lt;&lt;O&gt;&gt;. You end up on Blue Mountain. You see lamp A and lamp E. You rub lamp &lt;&lt;E&gt;&gt;. You receive 0 coins.

You are presented with magic carpets O and K. You press &lt;&lt;K&gt;&gt;. You end up on Pink Mountain. You see lamp H and lamp J. You rub lamp &lt;&lt;J&gt;&gt;. You receive 0 coins.

You are presented with magic carpets O and K. You press &lt;&lt;K&gt;&gt;. You end up on Pink Mountain. You see lamp H and lamp J. You rub lamp &lt;&lt;H&gt;&gt;. You receive 0 coins.

You are presented with magic carpets O and K. You press &lt;&lt;O&gt;&gt;. You end up on Blue Mountain. You see lamp A and lamp E. You rub lamp &lt;&lt;A&gt;&gt;. You receive 1 coins.

You are presented with magic carpets K and O. You press &lt;&lt;O&gt;&gt;. You end up on Pink Mountain. You see lamp H and lamp J. You rub lamp &lt;&lt;J&gt;&gt;. You receive 1 coins.

You are presented with magic carpets K and O. You press &lt;&lt;O&gt;&gt;. You end up on Blue Mountain. You see lamp A and lamp E. You rub lamp &lt;&lt;A&gt;&gt;. You receive 0 coins.

You are presented with magic carpets O and K. You press &lt;&lt;K&gt;&gt;. You end up on Blue Mountain. You see lamp A and lamp E. You rub lamp &lt;&lt;A&gt;&gt;. You receive 1 coins.

You are presented with magic carpets K and O. You press &lt;&lt;O&gt;&gt;. You end up on Pink Mountain. You see lamp H and lamp J. You rub lamp &lt;&lt;J&gt;&gt;. You receive 0 coins.

You are presented with magic carpets K and O. You press &lt;&lt;K&gt;&gt;. You end up on Pink Mountain. You see lamp H and lamp J. You rub lamp &lt;&lt;J&gt;&gt;. You receive 0 coins.

You are presented with magic carpets O and K. You press &lt;&lt;O&gt;&gt;. You end up on Blue Mountain. You see lamp A and lamp E. You rub lamp &lt;&lt;A&gt;&gt;. You receive 0 coins.

You are presented with magic carpets O and K. You pr

## Maggie's farm (modified problem structure)

```
Data source: [58] Number of experiments: 1 Number of participants: 658 Number of choices: 921200 Example prompt: You are participating in multiple games involving three apple trees, labeled S, F, and N. The three apple trees are different across different games. Each time you choose an apple tree, you get an apple of a given size. You choose an apple tree by pressing the corresponding key. Each apple tree tends to provide apples of about the same size on average. Your goal is to choose the apple trees that will give you the largest apples across the experiment. The first few trials in each game are instructed trials where you will be told which apple tree to choose. After these instructed trials, you will have the freedom to choose for either 1 or 6 trials. Game 1. There are 8 trials in this game. You are instructed to press F and get an apple with size 3.0 centimeters. You are instructed to press N and get an apple with size 2.0 centimeters. You press <<S>> and get an apple with size 4.0 centimeters. You press <<S>> and get an apple with size 4.0 centimeters. You press <<S>> and get an apple with size 4.0 centimeters. You press <<F>> and get an apple with size 5.0 centimeters. You press <<N>> and get an apple with size 5.0 centimeters. You press <<N>> and get an apple with size 4.0 centimeters. Game 2. There are 10 trials in this game. You are instructed to press F and get an apple with size 9.0 centimeters. You are instructed to press N and get an apple with size 2.0 centimeters. You are instructed to press F and get an apple with size 10.0 centimeters. You are instructed to press F and get an apple with size 10.0 centimeters. You press <<F>> and get an apple with size 10.0 centimeters. You press <<F>> and get an apple with size 8.0 centimeters. You press <<F>> and get an apple with size 9.0 centimeters.
```

```
You press <<F>> and get an apple with size 7.0 centimeters. You press <<F>> and get an apple with size 9.0 centimeters. You press <<F>> and get an apple with size 10.0 centimeters. Game 3. There are 8 trials in this game. You are instructed to press S and get an apple with size 2.0 centimeters. You are instructed to press F and get an apple with size 6.0 centimeters. You press <<F>> and get an apple with size 5.0 centimeters. You press <<F>> and get an apple with size 6.0 centimeters. You press <<F>> and get an apple with size 6.0 centimeters. You press <<F>> and get an apple with size 5.0 centimeters. You press <<F>> and get an apple with size 6.0 centimeters. You press <<F>> and get an apple with size 7.0 centimeters. Game 4. There are 11 trials in this game. You are instructed to press F and get an apple with size 5.0 centimeters. You are instructed to press S and get an apple with size 6.0 centimeters. You are instructed to press F and get an apple with size 4.0 centimeters. You are instructed to press F and get an apple with size 4.0 centimeters. You are instructed to press N and get an apple with size 2.0 centimeters. You press <<S>> and get an apple with size 6.0 centimeters. You press <<S>> and get an apple with size 5.0 centimeters. You press <<S>> and get an apple with size 3.0 centimeters. You press <<S>> and get an apple with size 4.0 centimeters. You press <<N>> and get an apple with size 2.0 centimeters. You press <<S>> and get an apple with size 4.0 centimeters. Game 5. There are 5 trials in this game. You are instructed to press S and get an apple with size 6.0 centimeters. You are instructed to press F and get an apple with size 7.0 centimeters. You are instructed to press S and get an apple with size 6.0 centimeters. You are instructed to press S and get an apple with size 5.0 centimeters. You press <<S>> and get an apple with size 6.0 centimeters. Game 6. There are 11 trials in this game. You are instructed to press S and get an apple with size 6.0 centimeters. You are instructed to press S and get an apple with size 4.0 centimeters. You are instructed to press S and get an apple with size 5.0 centimeters. You are instructed to press F and get an apple with size 3.0 centimeters. You are instructed to press N and get an apple with size 4.0 centimeters. You press <<S>> and get an apple with size 6.0 centime
```

## Logical reasoning (entirely novel domain)

Data source: [33]

Number of experiments: 1

Number of participants: 3543

Number of choices: 99204

Example prompt:

You're about to answer a set of 20 questions about logical reasoning. How many of the 20 questions do you think you will answer correctly?

You say &lt;&lt;12&gt;&gt;.

Compared to other participants in this study, how well do you think you will do? Marking 90% means you will do better than 90% of participants, marking 10% means you will do better than only 10%, and marking 50% means that you will perform better than half of the participants.

You say &lt;&lt;70&gt;&gt;%.

On a scale of 0 to 10, how difficult is solving logical reasoning problems for the average participant?

You say &lt;&lt;6&gt;&gt;.

On a scale of 0 to 10, how difficult is solving logical reasoning problems for you?

You say &lt;&lt;4&gt;&gt;.

You will be presented with brief passages or statements and will be required to evaluate their reasoning or determine what inferences you can logically draw from the passage.

Your task is to use the buttons D, Z, F, O, and X to select the best answer choice, even though more than one choice may present a possible answer.

Q1. Life imitates art. Which of the following, if true, most strongly supports the previous statement?

The choices are:

- Z: When Warren Beatty filmed Reds, he tried to suggest not only the chaos of the Russian Revolution but also its relationship to the present.

X: The number of professional ballet companies has increased over the last five years, but the number of dance majors has decreased.

D: On Tuesday, the business section of the newspaper had predicted the drop in interest rates that occurred on Friday.

O: Truman Capote wrote In Cold Blood as a result of a series of brutal slayings by two crazed killers.

F: Soon after the advent of color television, white shirts became less popular as dressy attire for men, and pastel-colored shirts began to sell well.

You press &lt;&lt;F&gt;&gt;.

Q2. On average, federal workers receive salaries 35.5 percent higher than privatesector salaries. For instance, federal workers in California average $19,206 a year, 25 percent higher than the average pay in the private sector, which is $15,365. This information would best support which of the following opinions?

The choices are:

- Z: Private-sector salaries in California are above average.
- X: The private sector is being paid fairly.
- O: Federal jobs are more secure than private-sector jobs.
- D: Public-sector work is more difficult than private-sector work.
- F: Federal pay is out of line.

You press &lt;&lt;Z&gt;&gt;.

- Q3. No high jumper entered the track meet unless he or she was a track club member. No track club member both entered the meet and was a high jumper. Which of the following conclusions can be correctly drawn from the two previous sentences?

The choices are:

- F: No one but high jumpers entered the meet.
- D: Only track club members entered the meet.
- X: No track club members entered the meet.
- Z: No high jumper entered the meet.
- O: Some track club members entered the meet.

You press &lt;&lt;Z&gt;&gt;.

- Q4. About 33% of American men between 25 and 50 are overweight. Research has shown that in most cases men between 25 and 50 who are overweight are more subject to heart disease than men who are not overweight. Which of the following is the most logical conclusion to this argument?

The choices are:

- D: Therefore, 33% of the American men between 25 and 50 should lose weight.
- O: Therefore, if 33% of the American men between 25 and 50 were to lose weight, they would reduce their risk of heart disease.
- X: Therefore, if the men between 25 and 50 who are overweight were to lose weight, they would reduce their risk of heart disease by 33%.
- Z: Therefore, if 33% of American men were to lose weight, they would reduce their risk of heart disease.
- F: Therefore, if the overweight men between 25 and 50 were to lose weight, their risk of heart disease would be reduced.

You press &lt;&lt;F&gt;&gt;.

- Q5. All computer geniuses are also brilliant mathematicians. Therefore, some computer geniuses don't require calculators for simple multiplication facts. Which of the following is the least necessary assumption for the previous conclusion to be logically correct?

The choices are:

F: Some brilliant mathematicians don't require calcul

## Two-step task (neural alignment)

Data source: [59]

Number of experiments: 1

Number of participants: 94

Number of choices: 28153

## Example prompt:

You are playing multiple rounds of a game. Your goal is to collect as many gold coins as possible as you visit different states. If you are in state C, you have the choice between options B and H. If you are in state S, you have the choice between options G and X. Picking one of these options may result in a gold coin. How likely an option leads to a gold coin slowly changes during the game. Picking option O generally leads to state C, and picking option N generally leads to state S. However, on rare occasions you will end up in the other state. You can select an option by pressing the corresponding key. You are presented with options O and N. You press &lt;&lt;N&gt;&gt;. You end up in state S. You are presented with option G and option X. You press &lt;&lt;X&gt;&gt;. You receive 1 coins. You are presented with options O and N. You press &lt;&lt;N&gt;&gt;. You end up in state S. You are presented with option G and option X. You press &lt;&lt;X&gt;&gt;. You receive 1 coins. You are presented with options N and O. You press &lt;&lt;N&gt;&gt;. You end up in state S. You are presented with option G and option X. You press &lt;&lt;X&gt;&gt;. You receive 1 coins. You are presented with options N and O. You press &lt;&lt;O&gt;&gt;. You end up in state C. You are presented with option B and option H. You press &lt;&lt;B&gt;&gt;. You receive 1 coins. You are presented with options N and O. You press &lt;&lt;O&gt;&gt;. You end up in state S. You are presented with option G and option X. You press &lt;&lt;X&gt;&gt;. You receive 1 coins. You are presented with options N and O. You press &lt;&lt;O&gt;&gt;. You end up in state C. You are presented with option B and option H. You press &lt;&lt;B&gt;&gt;. You receive 1 coins. You are presented with options O and N. You press &lt;&lt;N&gt;&gt;. You end up in state S. You are presented with option G and option X. You press &lt;&lt;X&gt;&gt;. You receive 0 coins. You are presented with options O and N. You press &lt;&lt;N&gt;&gt;. You end up in state C. You are presented with option B and option H. You press &lt;&lt;H&gt;&gt;. You receive 1 coins. You are presented with options N and O. You press &lt;&lt;O&gt;&gt;. You end up in state C. You are presented with option B and option H. You press &lt;&lt;H&gt;&gt;. You receive 1 coins.

You are presented with options N and O. You press &lt;&lt;O&gt;&gt;. You end up in state S. You are presented with option G and option X. You press &lt;&lt;G&gt;&gt;. You receive 0 coins.

You are presented with options O and N. You press &lt;&lt;N&gt;&gt;. You end up in state S. You are presented with option G and option X. You press &lt;&lt;X&gt;&gt;. You receive 1 coins.

You are presented with options N and O. You press &lt;&lt;O&gt;&gt;. You end up in state C. You are presented with option B and option H. You press &lt;&lt;H&gt;&gt;. You receive 1 coins.

You are presented with options O and N. You press &lt;&lt;N&gt;&gt;. You end up in state S. You are presented with option G and option X. You press &lt;&lt;X&gt;&gt;. You receive 0 coins.

You are presented with options O and N. You press &lt;&lt;N&gt;&gt;. You end up in state S. You are presented with option G and option X. You press &lt;&lt;G&gt;&gt;. You receive 0 coins.

You are presented with options N and O. You press &lt;&lt;O&gt;&gt;. You end up in state C. You are presented with option B and option H. You press &lt;&lt;B&gt;&gt;. You receive 1 coins.

You are presented with options O and N. You press &lt;&lt;N&gt;&gt;. You end up in state S. You are presented with option G and option X. You press &lt;&lt;X&gt;&gt;. You receive 1 coins.

You are presented with options N and O. You press &lt;&lt;O&gt;&gt;. You end up in state S. You are presented with option G and option X. You press &lt;&lt;X&gt;&gt;. You receive 1 coins.

You are presented with options O and N. You press &lt;&lt;N&gt;&gt;. You end up in state S. You are presented with option G and option X. You press &lt;&lt;X&gt;&gt;. You receive 1 coins.

You are presented with options O and N. You press &lt;&lt;N&gt;&gt;. You end up in state S. You are presented with option G and option X. You press &lt;&lt;X&gt;&gt;. You receive 0 coins.

You are presented with options O and N. You press &lt;&lt;N&gt;&gt;. You end up in state C. You are presented with option B and option H. You press &lt;&lt;H&gt;&gt;. You receive 1 coins.

You are presented with options O and N. You press &lt;&lt;N&gt;&gt;. You end up in state C. You are presented with option B and option H. You press &lt;&lt;H&gt;&gt;. You receive 1 coins.

You are presented with options N and O.

## Sentence reading (neural alignment)

Data source: [60]

Number of experiments: 1

Number of participants: 5

Number of choices: 0

Example prompt:

We were sitting on the couch.

## Supplementary Information References

- [1] Hilbig, B. E. &amp; Moshagen, M. Generalized outcome-based strategy classification: Comparing deterministic and probabilistic choice models. Psychonomic bulletin &amp; review 21, 1431-1443 (2014).
- [2] Paszke, A. et al. PyTorch: an imperative style, high-performance deep learning library (Curran Associates Inc., Red Hook, NY, USA, 2019).
- [3] Defazio, A. et al. The road less scheduled (2024). URL https://arxiv.org/abs/ 2405.15682. 2405.15682.
- [4] Nosofsky, R. M. The generalized context model: An exemplar model of classification. Formal approaches in categorization 18-39 (2011).
- [5] Peterson, J. C., Bourgin, D. D., Agrawal, M., Reichman, D. &amp; Griffiths, T. L. Using large-scale experiments and machine learning to discover theories of human decision-making. Science 372, 1209-1214 (2021).
- [6] Van den Bos, W. &amp; McClure, S. M. Towards a general model of temporal discounting. Journal of the experimental analysis of behavior 99, 58-73 (2013).
- [7] Daw, N. D., Gershman, S. J., Seymour, B., Dayan, P. &amp; Dolan, R. J. Modelbased influences on humans' choices and striatal prediction errors. Neuron 69, 1204-1215 (2011).
- [8] Wilson, R. C., Geana, A., White, J. M., Ludvig, E. A. &amp; Cohen, J. D. Humans use directed and random exploration to solve the explore-exploit dilemma. Journal of experimental psychology: General 143, 2074 (2014).
- [9] Sutton, R. S. &amp; Barto, A. G. Reinforcement learning: An introduction (MIT press, 2018).
- [10] Gershman, S. J. A unifying probabilistic view of associative learning. PLoS computational biology 11, e1004567 (2015).
- [11] Czerlinski, J., Gigerenzer, G. &amp; Goldstein, D. G. How good are simple heuristics? (1999).
- [12] Pedroni, A. et al. A prospect theory account of the "hot" columbia card task (2018).
- [13] Hebart, M. N., Zheng, C. Y., Pereira, F. &amp; Baker, C. I. Revealing the multidimensional mental representations of natural objects underlying human similarity judgements. Nature human behaviour 4, 1173-1185 (2020).
- [14] Tomov, M. S., Schulz, E. &amp; Gershman, S. J. Multi-task reinforcement learning in humans. Nature Human Behaviour 5, 764-773 (2021).

- [15] Wu, C. M., Schulz, E., Speekenbrink, M., Nelson, J. D. &amp; Meder, B. Generalization guides human exploration in vast decision spaces. Nature human behaviour 2, 915-924 (2018).
- [16] Newell, A. Unified Theories of Cognition (Harvard University Press, Cambridge, 1990).
- [17] Anderson, J. R. &amp; Lebiere, C. The newell test for a theory of cognition. Behavioral and brain Sciences 26, 587-601 (2003).
- [18] Anderson, J. R. The adaptive character of thought (Erlbaum, Hillsdale, NJ, 1990).
- [19] Binz, M. et al. Meta-learned models of cognition. Behavioral and Brain Sciences 1-38 (2023).
- [20] Andreas, J. Goldberg, Y., Kozareva, Z. &amp; Zhang, Y. (eds) Language models as agent models. (eds Goldberg, Y., Kozareva, Z. &amp; Zhang, Y.) Findings of the Association for Computational Linguistics: EMNLP 2022, 5769-5779 (Association for Computational Linguistics, Abu Dhabi, United Arab Emirates, 2022). URL https://aclanthology.org/2022.findings-emnlp.423.
- [21] Badham, S. P., Sanborn, A. N. &amp; Maylor, E. A. Deficits in category learning in older adults: Rule-based versus clustering accounts. Psychology and Aging 32, 473 (2017).
- [22] Bahrami, B. &amp; Navajas, J. 4 arm bandit task dataset (2022). URL osf.io/f3t2a.
- [23] Collsi¨o¨o, A., Juslin, P. &amp; Winman, A. Is numerical information always beneficial? verbal and numerical cue-integration in additive and non-additive tasks. Cognition 240, 105584 (2023).
- [24] Cox, G. E., Hemmer, P., Aue, W. R. &amp; Criss, A. H. Information and processes underlying semantic and episodic memory across tasks, items, and individuals. Journal of Experimental Psychology: General 147, 545 (2018).
- [25] Enkavi, A. Z. et al. Large-scale analysis of test-retest reliabilities of self-regulation measures. Proceedings of the National Academy of Sciences 116, 5472-5477 (2019).
- [26] Feng, S. F., Wang, S., Zarnescu, S. &amp; Wilson, R. C. The dynamics of exploreexploit decisions reveal a signal-to-noise mechanism for random exploration. Scientific reports 11, 3077 (2021).
- [27] Flesch, T., Balaguer, J., Dekker, R., Nili, H. &amp; Summerfield, C. Comparing continual task learning in minds and machines. Proceedings of the National Academy of Sciences 115, E10313-E10322 (2018).

- [28] Frey, R., Pedroni, A., Mata, R., Rieskamp, J. &amp; Hertwig, R. Risk preference shares the psychometric structure of major psychological traits. Science advances 3, e1701381 (2017).
- [29] Garcia, B., Lebreton, M., Bourgeois-Gironde, S. &amp; Palminteri, S. Experiential values are underweighted in decisions involving symbolic options. Nature human behaviour 7, 611-626 (2023).
- [30] Gershman, S. J. Deconstructing the human algorithms for exploration. Cognition 173, 34-42 (2018).
- [31] Collins, A. G., Brown, J. K., Gold, J. M., Waltz, J. A. &amp; Frank, M. J. Working memory contributions to reinforcement learning impairments in schizophrenia. Journal of Neuroscience 34, 13747-13756 (2014).
- [32] Hebart, M. N. et al. Things-data, a multimodal collection of large-scale datasets for investigating object representations in human brain and behavior. Elife 12, e82580 (2023).
- [33] Jansen, R. A., Rafferty, A. N. &amp; Griffiths, T. L. A rational model of the dunningkruger effect supports insensitivity to evidence in low performers. Nature Human Behaviour 5, 756-763 (2021).
- [34] Kool, W., Cushman, F. A. &amp; Gershman, S. J. When does model-based control pay off? PLoS computational biology 12, e1005090 (2016).
- [35] Kool, W., Gershman, S. J. &amp; Cushman, F. A. Cost-benefit arbitration between multiple reinforcement-learning systems. Psychological science 28, 1321-1333 (2017).
- [36] Krueger, P. M., Callaway, F., Gul, S., Griffiths, T. L. &amp; Lieder, F. Identifying resource-rational heuristics for risky choice. Psychological Review (2024).
- [37] Kumar, S., Dasgupta, I., Daw, N. D., Cohen, J. D. &amp; Griffiths, T. L. Disentangling abstraction from statistical pattern matching in human and machine learning. PLoS computational biology 19, e1011316 (2023).
- [38] Lefebvre, G., Lebreton, M., Meyniel, F., Bourgeois-Gironde, S. &amp; Palminteri, S. Behavioural and neural characterization of optimistic reinforcement learning. Nature Human Behaviour 1, 0067 (2017).
- [39] Levering, K. R., Conaway, N. &amp; Kurtz, K. J. Revisiting the linear separability constraint: New implications for theories of human category learning. Memory &amp; cognition 48, 335-347 (2020).
- [40] Ludwig, T., Siegel, M. &amp; Schulz, E. Human multi-task learning: the why and what (2023). URL http://dx.doi.org/10.32470/CCN.2023.1528-0.

- [41] Plonsky, O., Apel, R., Erev, I., Ert, E. &amp; Tennenholtz, M. When and how can social scientists add value to data scientists? a choice prediction competition for human decision making. Unpublished Manuscript (2018).
- [42] Popov, V. &amp; Dames, H. Intent matters: Resolving the intentional versus incidental learning paradox in episodic long-term memory. Journal of Experimental Psychology: General 152, 268 (2023).
- [43] Ruggeri, K. et al. The globalizability of temporal discounting. Nature Human Behaviour 6, 1386-1397 (2022).
- [44] Sadeghiyeh, H. et al. Temporal discounting correlates with directed exploration but not with random exploration. Scientific reports 10, 4020 (2020).
- [45] Schulz, E., Franklin, N. T. &amp; Gershman, S. J. Finding structure in multi-armed bandits. Cognitive psychology 119, 101261 (2020).
- [46] Somerville, L. H. et al. Charting the expansion of strategic exploratory behavior during adolescence. Journal of experimental psychology: general 146, 155 (2017).
- [47] Speekenbrink, M., Channon, S. &amp; Shanks, D. R. Learning strategies in amnesia. Neuroscience &amp; Biobehavioral Reviews 32, 292-310 (2008).
- [48] Steingroever, H. et al. Data from 617 healthy participants performing the iowa gambling task: A "many labs" collaboration. Journal of Open Psychology Data 3, e5-e5 (2015).
- [49] Tomov, M. S., Yagati, S., Kumar, A., Yang, W. &amp; Gershman, S. J. Discovery of hierarchical representations for efficient planning. PLoS computational biology 16, e1007594 (2020).
- [50] Waltz, J. A., Wilson, R. C., Albrecht, M. A., Frank, M. J. &amp; Gold, J. M. Differential effects of psychotic illness on directed and random exploration. Computational Psychiatry (Cambridge, Mass.) 4, 18 (2020).
- [51] Wise, T., Michely, J., Dayan, P. &amp; Dolan, R. J. A computational account of threat-related attentional bias. PLoS computational biology 15, e1007341 (2019).
- [52] Wu, S., ´Eltet˝o, N., Dasgupta, I. &amp; Schulz, E. Chunking as a rational solution to the speed-accuracy trade-off in a serial reaction time task. Scientific reports 13, 7680 (2023).
- [53] Wulff, D. U., Mergenthaler-Canseco, M. &amp; Hertwig, R. A meta-analytic review of two modes of learning and the description-experience gap. Psychological bulletin 144, 140 (2018).
- [54] Xiong, H.-D., Ji-An, L., Mattar, M. &amp; Wilson, R. Neural network modeling reveals diverse human exploration behaviors via state space analysis (2023).

- [55] Zhu, J.-Q., Sanborn, A. N. &amp; Chater, N. The bayesian sampler: Generic bayesian inference causes incoherence in human probability judgments. Psychological review 127, 719 (2020).
- [56] Zorowitz, S. &amp; Niv, Y. Data from two-step task pilots (2023). URL osf.io/2tgjd.
- [57] Feher da Silva, C. &amp; Hare, T. A. Humans primarily use model-based inference in the two-stage task. Nature Human Behaviour 4, 1053-1066 (2020).
- [58] Dubois, M. &amp; Hauser, T. U. Value-free random exploration is linked to impulsivity. Nature Communications 13, 4542 (2022).
- [59] Feher da Silva, C., Lombardi, G., Edelson, M. &amp; Hare, T. A. Rethinking modelbased and model-free influences on mental effort and striatal prediction errors. Nature Human Behaviour 7, 956-969 (2023).
- [60] Tuckute, G. et al. Driving and suppressing the human language network using large language models. Nature Human Behaviour 8, 544-561 (2024).