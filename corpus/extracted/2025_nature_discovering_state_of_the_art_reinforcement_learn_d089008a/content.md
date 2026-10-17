<!-- source: 2025-Nature_Discovering state-of-the-art reinforcement learning algorithms&SI.pdf -->
<!-- source_pdf: D:\2026-AI4S\REFs\Information Seeking\2025-Nature_Discovering state-of-the-art reinforcement learning algorithms&SI.pdf -->
<!-- pages: 28 ; extracted_by: docling 2.140.0 -->

## Discovering state-of-the-art reinforcement learning algorithms

[https://doi.org/10.1038/s41586-025-09761-x](https://doi.org/10.1038/s41586-025-09761-x)

Received: 11 December 2024

Accepted: 15 October 2025

Published online: 22 October 2025

Open access

<!-- image -->

Check for updates Junhyuk Oh 1,2 ✉ , Gregory Farquhar 1,2 , Iurii Kemaev 1,2 , Dan A. Calian 1,2 , Matteo Hessel 1 , Luisa Zintgraf 1 , Satinder Singh 1 , Hado van Hasselt 1 &amp; David Silver 1 ✉

Humans and other animals use powerful reinforcement learning (RL) mechanisms that have been discovered by evolution over many generations of trial and error. By contrast, artificial agents typically learn using handcrafted learning rules. Despite decades of interest, the goal of autonomously discovering powerful RL algorithms has proven to be elusive 1-6 . Here we show that it is possible for machines to discover a state-of-the-art RL rule that outperforms manually designed rules. This was achieved by meta-learning from the cumulative experiences of a population of agents across a large number of complex environments. Specifically, our method discovers the RL rule by which the agent's policy and predictions are updated. In our large-scale experiments, the discovered rule surpassed all existing rules on the well-established Atari benchmark and outperformed a number of state-of-the-art RL algorithms on challenging benchmarks that it had not seen during discovery. Our findings suggest that the RL algorithms required for advanced artificial intelligence may soon be automatically discovered from the experiences of agents, rather than manually designed.

The primary goal of artificial intelligence is to design agents that, like humans, can predict and act in complex environments to achieve goals. Many of the most successful agents are based on reinforcement learning (RL), in which agents learn by interacting with environments. Decades of research have produced ever more efficient RL algorithms, resulting in numerous landmarks in artificial intelligence, including the mastery of complex competitive games such as Go 7 , chess 8 , StarCraft 9 and Minecraft 10 , the invention of new mathematical tools 11 , or the control of complex physical systems 12 .

Unlike humans, whose learning mechanism has been naturally discovered by biological evolution, RL algorithms are typically manually designed. This is usually slow and laborious, and limited by reliance on human knowledge and intuition. Although a number of attempts have been made to automatically discover learning algorithms 1-6 , none have proven to be sufficiently efficient and general to replace hand-designed RL systems.

In this work, we introduce an autonomous method for discovering RL rules solely through the experience of many generations of agents interacting with various environments (Fig. 1a). The discovered RL rule achieves state-of-the-art performance on a variety of challenging RL benchmarks. The success of our method contrasts previous work in two dimensions. First, whereas previous methods searched over narrow spaces of RL rules (for example, hyperparameters 13,14 or policy loss 1,6 ), our method allows the agent to explore a far more expressive space of potential RL rules. Second, whereas previous work focused on meta-learning in simple environments (for example, grid-worlds 3,15 ), our method meta-learns in complex and diverse environments at a much larger scale.

To choose a general space of discovery, we observe that the essential component of standard RL algorithms is a rule that updates one or more predictions, as well as the policy itself, towards targets that are functions of quantities such as future rewards and future predictions. Examples of RL rules based on different targets include temporal-difference learning 16 , Q-learning 17 , proximal policy optimization (PPO) 18 , auxiliary tasks 19 , successor features 20 and distributional RL 21 . In each case, the choice of target determines the nature of the predictions, for example, whether they become value functions, models or successor features.

In our framework, an RL rule is represented by a meta-network that determines the targets towards which the agent should move its predictions and policy (Fig. 1c). This allows the system to discover useful predictions without pre-defined semantics, as well as how they are used. The system may in principle rediscover past RL rules, but the flexible functional form also allows the agent to invent new RL rules that may be specifically adapted to environments of interest.

During the discovery process, we instantiate a population of agents, each of which interacts with its own instance of an environment taken from a diverse set of challenging tasks. Each agent's parameters are updated according to the current RL rule. We then use the meta-gradient method 13 to incrementally improve the RL rule such that it could lead to better-performing agents.

Our large-scale empirical results show that our discovered RL rule, which we call DiscoRL, surpasses all existing RL rules on the environments in which it was meta-learned. Notably, this includes Atari games 22 , arguably the most established and informative of RL benchmarks. Furthermore, DiscoRL achieved state-of-the-art performance on a number of other challenging benchmarks, such as ProcGen 23 , that it had never been exposed to during discovery. We also show that the performance and generality of DiscoRL improves further as more diverse and complex environments are used in discovery. Finally, our analysis shows that DiscoRL has discovered unique prediction semantics that meta-network, together with rewards and episode termination indicators from the environment (omitted for simplicity in the figure). Using this information, the meta-network produces targets for all of the agent's predictions from the current and future time steps. The agent is updated to minimize the prediction errors with respect to their targets. LSTM, long short-term memory. d, Metaoptimization. The meta-parameters of the meta-network are updated by taking a meta-gradient step calculated from backpropagation through the agent's update process (θ0 → θN), where the meta-objective is to maximize the collective returns of the agents in their environments.

Fig. 1 | Discovering an RL rule from a population of agents. a, Discovery. Multiple agents, interacting with various environments, are trained in parallel according to the learning rule, defined by the meta-network. In the meantime, the meta-network is optimized to improve the agents' collective performances. b, Agent architecture. An agent produces the following outputs: (1) a policy (π), (2) an observation-conditioned prediction vector (y), (3) action-conditioned prediction vectors (z), (4) action values (q) and (5) an auxiliary policy prediction (p). The semantics of y and z are determined by the meta-network. c, Meta-network architecture. A trajectory of the agent's outputs is given as input to the

<!-- image -->

are distinct from existing RL concepts such as value functions. To the best of our knowledge, this is the empirical evidence that surpassing manually designed RL algorithms in terms of both generality and efficiency is finally within reach.

## Discovery method

Our discovery approach involves two types of optimization: agent optimization and meta-optimization. Agent parameters are optimized by updating their policies and predictions towards the targets produced by the RL rule. Meanwhile, the meta-parameters of the RL rule are optimized by updating its targets to maximize the cumulative rewards of the agents.

## Agent network

Much RL research considers what predictions an agent should make (for example, values), and what loss function should be used to learn those predictions (for example, temporal-difference (TD) learning) and improve the policy (for example, policy gradient). Instead of hand-crafting them, we define an expressive space of predictions without pre-defined semantics and meta-learn what the agent needs to optimize by representing it using a meta-network. It is desirable to maintain the ability to represent key ideas in existing RL algorithms, while supporting a large space of novel algorithmic possibilities.

To this end, we let the agent, parameterized by θ, output two types of predictions in addition to a policy (π): an observation-conditioned vector prediction y(s) ∈ ℝ n of arbitrary size n and an action-conditioned vector prediction z(s, a) ∈ ℝ m of arbitrary size m, where s and a are an observation and an action, respectively (Fig. 1b). The form of these predictions stems from the fundamental distinction between prediction and control 16 . For example, value functions are commonly divided into state-value functions v(s) (for prediction) and actionvalue functions q(s, a) (for control), and many other concepts in RL, such as rewards and successor features, also have an observationconditioned version and an action-conditioned version. Therefore, the functional form of the predictions (y, z) is general enough to represent, but is not restricted to, many existing fundamental concepts in RL.

## Article

In addition to the predictions to be discovered, in most of our experiments the agent makes predictions with pre-defined semantics. Specifically, the agent produces an action-value function q(s, a) and an action-conditional auxiliary policy prediction p(s, a) 8 . This encourages the discovery process to focus on discovering new concepts through y and z.

## Meta-network

A large proportion of modern RL rules use the forward view of RL 16 . In this view, the RL rule receives a trajectory from time step t to t + n, and uses this information to update the agent's predictions or policy. They typically update the predictions or policy towards bootstrapped targets, that is, towards future predictions.

Correspondingly, our RL rule uses a meta-network (Fig. 1c) as a function that determines targets towards which the agent should move its predictions and policy. To produce targets at time step t, the meta-network receives as input a trajectory of the agent's predictions and policy as well as rewards and episode termination from time step t to t + n. It uses a standard long short-term memory 24 to process these inputs, although other architectures may be used (Extended Data Fig. 3).

The choice of inputs and outputs to the meta-network maintains certain desirable properties of handcrafted RL rules. First, the metanetwork can deal with any observation and with discrete action spaces of any size. This is possible because the meta-network does not receive the observation directly as input, but only indirectly via predictions. In addition, it processes action-specific inputs and outputs by sharing weights across action dimensions. As a result it can generalize to radically different environments. Second, the meta-network is agnostic to the design of the agent network, as it sees only the output of the agent network. As long as the agent network produces the required form of outputs (π, y, z), the discovered RL rule can generalize to arbitrary agent architectures or sizes. Third, the search space defined by the meta-network includes the important algorithmic idea of bootstrapping. Fourth, as the meta-network processes both policy and predictions together, it can not only meta-learn auxiliary tasks 25 but also directly use predictions to update the policy (for example, to provide a baseline for variance reduction). Finally, outputting targets is strictly more expressive than outputting a scalar loss function, as it includes semi-gradient methods such as Q-learning in the search space. While building on these properties of standard RL algorithms, the rich parametric neural network allows the discovered rule to implement algorithms with potentially much greater efficiency and contextual nuance.

## Agent optimization

The agent's parameters (θ) are updated to minimize the distance from its predictions and policy to the targets from the meta-network. The agent's loss function can be expressed as:

<!-- formula-not-decoded -->

where s and a are distributed according to the policy πθ, and D(p, q) is a distance function between p and q. We chose the Kullback-Leibler divergence as the distance function, as it is sufficiently general and has previously been found to make meta-optimization easier 3 . Here πθ, y θ, zθ and π^ , ^y, z ^ are the outputs of the agent network and the meta-network, respectively, with a softmax function applied to normalize each vector.

The auxiliary loss Laux is used for predictions with pre-defined semantics: action values (q) and auxiliary policy predictions (p) as follows: Laux = D(q^ , qθ(s, a)) + D(^p, pθ(s, a)), where q^ is an action-value target from Retrace 26 projected to a two-hot vector 8 , and ^p = πθ(s′) is the policy at the one-step future state. To be consistent with the rest of losses, we use the Kullback-Leibler divergence as the distance function D.

## Meta-optimization

Our goal is to discover an RL rule, represented by the meta-network with meta-parameters η, that allows agents to maximize rewards in a variety of training environments. This discovery objective J(η) and its meta-gradient ∇η J(η) can be expressed as:

<!-- formula-not-decoded -->

where E indicates an environment sampled from a distribution and θ denotes agent parameters induced by an initial parameter distribution and their evolution over the course of learning with the RL rule. E J θ γ r ( ) = [∑ ] t t t , where γ is the discount factor and rt is the reward at step t, is the expected discounted sum of rewards, which is the typical RL objective. The meta-parameters are optimized using gradient ascent following the above equations.

To estimate the meta-gradient, we instantiate a population of agents that learn according to the meta-network in a set of sampled environments. To ensure this approximation is close to the true distribution of interest, we use a large number of complex environments taken from challenging benchmarks, in contrast to previous work that focused on a small number of simple environments. As a result the discovery process surfaces diverse RL challenges, such as the sparsity of rewards, the task horizon, and the partial observability or stochasticity of environments.

Each agent's parameters are periodically reset to encourage the update rule to make fast learning progress within a limited agent lifetime. As in previous work on meta-gradient RL 13 , the meta-gradient term ∇η J(η) can be divided into two gradient terms by the chain rule: ∇ηθ and ∇θ J(θ). The first term can be understood as a gradient over the agent update procedure 27 , whereas the second term is the gradient of the standard RL objective. To estimate the first term, we iteratively update the agent multiple times and backpropagate through the entire update procedure, as illustrated in Fig. 1d. To make it tractable, we backpropagate over 20 agent updates using a sliding window. Finally, to estimate the second term, we use the advantage actor-critic method 28 . To estimate the advantage, we train a meta-value function, which is a value function used only for discovery.

## Empirical result

We implemented our discovery method with a large population of agents in a set of complex environments. We call the discovered RL rule DiscoRL. In evaluation, the aggregated performance was measured by the interquartile mean (IQM) of normalized scores for benchmarks that consist of multiple tasks, which has proven to be a statistically reliable metric 29 .

## Atari

The Atari benchmark 22 , one of the most studied benchmarks in the history of RL, consists of 57 Atari 2600 games. They require complex strategies, planning and long-term credit assignment, making it non-trivial for AI agents to master. Hundreds of RL algorithms have been evaluated on this benchmark over the past decade, which include MuZero 8 and Dreamer 10 .

To see how strong the rule can be when discovered directly from this benchmark, we meta-trained an RL rule, Disco57, and evaluated it on the same 57 games (Fig. 2a). In this evaluation, we used a network architecture that has a number of parameters comparable to the number used by MuZero. This is a larger network than the one used during discovery; the discovered RL rule must therefore generalize to this setting. Disco57 achieved an IQM of 13.86, outperforming all existing RL rules 8,10,14,30 on the Atari benchmark, with a substantially higher wall-clock efficiency compared with the state-of-the-art MuZero (Extended Data Fig. 4). This shows that our method can automatically discover a strong RL rule from such challenging environments.

Fig. 2 | Evaluation of DiscoRL. a-f, Performance of DiscoRL compared to humandesigned RL rules on Atari (a), ProcGen (b), DMLab (c), Crafter (d; figure inset shows results for 1 million environment steps), NetHack (e), and Sokoban (f). The x axis represents the number of environment steps in millions. The y axis represents the human-normalized IQM score for benchmarks consisting of multiple tasks (Atari, ProcGen and DMLab-30) and average return for the rest. Disco57 (blue) is discovered from the Atari benchmark and Disco103 (orange)

<!-- image -->

is discovered from Atari, ProcGen and DMLab-30 benchmarks. The shaded areas show 95% confidence intervals. The dashed lines represent manually designed RL rules such as MuZero 8 , efficient memory-based exploration agent (MEME) 30 , Dreamer 10 , self-tuning actor-critic algorithm (STACX) 14 , importance-weighted actor-learner architecture (IMPALA) 34 , deep Q-network (DQN) 51 , phasic policy gradient (PPG) 52 , proximal policy optimization (PPO) 18 , and Rainbow 53 .

## Article

Fig. 3 | Properties of discovery process. a, Discovery efficiency. The best DiscoRL was discovered within 3 simulations of the agent's lifetimes (200 million steps) per game. b, Scalability. DiscoRL becomes stronger on the ProcGen benchmark (30 million environment steps for all methods) as the training set of environments grows. c, Ablation. The plot shows the performances of variations of DiscoRL on Atari. 'Without auxiliary prediction' is meta-learned

<!-- image -->

without the auxiliary prediction (p). 'Small agents' uses a smaller agent network during discovery. 'Without prediction' is meta-learned without learned predictions (y, z). 'Without value' is meta-learned without the value function (q). 'Toy environments' is meta-learned from 57 grid-world tasks instead of Atari games.

## Generalization

We further investigated the generality of Disco57 by evaluating it on a variety of held-out benchmarks that it was never exposed to during discovery. These benchmarks include unseen observation and action spaces, diverse environment dynamics, various reward structures and unseen agent network architectures. Meta-training hyperparameters were tuned on only training environments (that is, Atari) to prevent the rule from being implicitly optimized for held-out benchmarks.

The result on the ProcGen 23 benchmark (Fig. 2b and Extended Data Table 2), which consists of 16 procedurally generated two-dimensional games, shows that Disco57 outperformed all existing published methods, including MuZero 8 and PPO 18 , even though it had never interacted with ProcGen environments during discovery. In addition, Disco57 achieved a competitive performance on Crafter 31 (Fig. 2d and Extended Data Table 5), where the agent needs to learn a wide spectrum of abilities to survive. Disco57 reached the third place on the leaderboard of NetHack NeurIPS 2021 Challenge 32 (Fig. 2e and Extended Data Table 4), where more than 40 teams participated. Unlike the top submitted agents in the competition 33 , Disco57 did not use any domain-specific knowledge for defining subtasks or reward shaping. For a fair comparison, we trained an agent with the importance weighted actor-learner architecture (IMPALA) algorithm 34 using the same settings as Disco57. IMPALA's performance was much weaker, suggesting that Disco57 has discovered a more efficient RL rule than standard approaches. In addition to environments, Disco57 turned out to be robust to a range of agent-specific settings such as network size, replay ratio and hyperparameters in evaluation (Extended Data Fig. 1).

## Complex and diverse environments

To understand the importance of complex and diverse environments for discovery, we further scaled up meta-learning with additional environments. Specifically, we discovered another rule, Disco103, using a more diverse set of 103 environments consisting of the Atari, ProcGen and DMLab-30 35 benchmarks. This rule performs similarly on the Atari benchmark while improving scores on every other seen and unseen benchmark in Fig. 2. In particular, Disco103 reached human-level performance on Crafter and neared MuZero's state-of-the-art performance on Sokoban 36 . These results show that the more complex and diverse the set of environments used for discovery, the stronger and more general the discovered rule becomes, even on held-out environments that were not seen during discovery. Discovering Disco103 required no changes to the discovery method compared with Disco57 other than the set of environments. This shows that the discovery process itself is robust, scalable and general.

To further investigate the importance of using complex environments, we ran our discovery process on 57 grid-world tasks that are extended from previous work 3 , using the same meta-learning settings as for Disco57. The new rule had a significantly worse performance (Fig. 3c) on the Atari benchmark. This verifies our hypothesis about the importance of meta-learning directly from complex and challenging environments. While using such environments was crucial, there was no need for a careful curation of the correct set of environments; we simply used popular benchmarks from the literature.

## Efficiency and scalability

To further understand the scalability and efficiency of our approach, we evaluated multiple Disco57s over the course of discovery (Fig. 3a). The best rule was discovered within approximately 600 million steps per Atari game, which amounts to just 3 experiments across 57 Atari games. This is arguably more efficient than the manual discovery of RL rules, which typically requires many more experiments to be executed, in addition to the time of the human researchers.

Furthermore, DiscoRL performed better on the unseen ProcGen benchmark as more Atari games were used for discovery (Fig. 3b), showing that the resulting RL rule scales well with the number and diversity of environments used for discovery. In other words, the performance of the discovered rule is a function of data (that is, environments) and compute.

## Effect of discovering new predictions

To study the effect of the discovered semantics of predictions (y, z in Fig. 1b), we compared different rules by varying the outputs of the agent, with and without certain types of prediction. The result in Fig. 3c shows that the use of a value function markedly improves the discovery process, which highlights the importance of this fundamental concept of RL. However, the result in Fig. 3c also shows the importance of discovering new prediction semantics (y and z) beyond pre-defined predictions. Overall, increasing the scope of discovery compared with previous work 1-6 was essential. In the following section, we provide further analysis to uncover what semantics have been discovered.

## Analysis

## Qualitative analysis

We analysed the nature of the discovered rule, using Disco57 as a case study (Fig. 4). Qualitatively, the discovered predictions spike in advance of salient events such as receiving rewards or changes in the entropy of the policy (Fig. 4a). We also investigated which features of the observation cause the meta-learned predictions to respond strongly, by measuring the gradient norm associated with each part of the observation. The result in Fig. 4b shows that meta-learned predictions tend to pay attention to objects that may be relevant in the future, which is distinct from where the policy and the value function pay attention to. These results indicate that DiscoRL has learned to identify and predict salient events over a modest horizon, and thus complements existing concepts such as the policy and value function.

Fig. 4 | Analysis of DiscoRL. a, Behaviour of discovered predictions. The plot shows how the agent's discovered prediction (y) changes along with other quantities in Ms Pacman (left) and Breakout (right). 'Confidence' is calculated as negative entropy. Spikes in prediction confidence are correlated with upcoming salient events. For example, they often precede large rewards in Ms Pacman and strong action preferences in Breakout. b, Gradient analysis. Each contour shows where each prediction focuses on in the observation through a gradient analysis in Beam Rider. The predictions tend to focus more on enemies at a distance, whereas the policy and the value tend to focus on nearby enemies and the scoreboard, respectively. c, Prediction analysis. Future entropy and large-reward

<!-- image -->

events can be better predicted from discovered predictions. The shaded areas represent 95% confidence intervals. d, Bootstrapping horizon. The plot shows how much the prediction target produced by DiscoRL changes when the prediction at each time step is perturbed. The individual curves correspond to 16 randomly sampled trajectories and the bold curve corresponds to the average over them. e, Reliance on predictions. The plot shows the performance of the controlled DiscoRL on Ms Pacman without bootstrapping when updating predictions and without using predictions at all. The shaded areas represent 95% confidence intervals.

## Information analysis

To confirm the qualitative findings, we further investigated what information is contained in the predictions. We first collected data from the DiscoRL agent on 10 Atari games and trained a neural network to predict quantities of interest from either the discovered predictions, the policy or the value function. The results in Fig. 4c show that the discovered predictions contain greater information about upcoming large rewards and the future policy entropy, compared with the policy and value. This suggests that the discovered predictions may capture unique task-relevant information that is not well captured by the policy and value.

## Emergence of bootstrapping

We also found evidence that DiscoRL uses a bootstrapping mechanism. When the meta-network's prediction input at future time steps (zt+k) is perturbed, it strongly affects the target ^ t z (Fig. 4d). This means that the future predictions are used to construct targets for the current predictions. This bootstrapping mechanism and the discovered predictions turned out to be critical for performance (Fig. 4e). If the y and z inputs to the meta-network are set to zero when computing their targets ^y and ^z (thus preventing bootstrapping), performance degrades substantially. If the y and z inputs are set to zero for computing all targets including the policy target, the performance drops even further. This shows the discovered predictions are heavily used to inform the policy update, rather than just serving as auxiliary tasks.

## Article

## Previous work

The idea of meta-learning, or learning to learn, in artificial agents dates back to the 1980s 37 , with proposals to train meta-learning systems with backpropagation of gradients 38 . The core idea of using a slower meta-learning process to meta-optimize a fast learning or adaptation process 39,40 has been studied for numerous applications in various contexts, including transfer learning 41 , continual learning 42 , multi-task learning 43 , hyperparameter optimization 44 and automated machine learning 45 .

Early efforts to use meta-learning for RL agents comprised attempts to meta-learn information-seeking behaviours 46 . Many later works have focused on meta-learning a small number of hyperparameters of an existing RL algorithm 13,14 . Such approaches have produced promising results but cannot markedly depart from the underlying handcrafted algorithms. Another line of work has attempted to eschew inductive biases by meta-learning entirely black-box algorithms implemented, for example, as recurrent neural networks 47 or as a synaptic learning rule 48 . Although conceptually appealing, these methods are prone to overfit to tasks seen in meta-training 49 .

The idea of representing knowledge using a wider class of predictions was first introduced in temporal-difference networks 50 but without any meta-learning mechanism. A similar idea has been explored for meta-learning auxiliary tasks 25 . Our work extends this idea to effectively discover an entire loss function that the agent optimizes, covering a much broader range of possible RL rules. Furthermore, unlike previous work, the discovered knowledge can generalize to unseen environments.

Recently, there have been growing interests in discovering generalpurpose RL rules 1,3-6,15 . However, most of them were limited to small agents and simple tasks, or the scope of discovery was limited to a partial RL rule. Therefore, their rules were not extensively compared with state-of-the-art rules on challenging benchmarks. In contrast, we search over a larger space of rules, including entirely new predictions, and scale up to a large number of complex environments for discovery. As a result, we demonstrate that it is possible to discover a general-purpose RL rule that outperforms a number of state-of-the-art rules on challenging benchmarks.

## Conclusion

Enabling machines to discover learning algorithms for themselves is one of the most promising ideas in artificial intelligence owing to its potential for open-ended self-improvement. This work has taken a step towards machine-designed RL algorithms that can compete with and even outperform some of the best manually designed algorithms in challenging environments. We also showed that the discovered rule becomes stronger and more general as it gets exposed to more diverse environments. This suggests that the design of RL algorithms for advanced AI may in the future be led by machines that can scale effectively with data and compute.

## Online content

Any methods, additional references, Nature Portfolio reporting summaries, source data, extended data, supplementary information, acknowledgements, peer review information; details of author contributions and competing interests; and statements of data and code availability are available at https://doi.org/10.1038/s41586-025-09761-x.

1. Kirsch, L., van Steenkiste, S. &amp; Schmidhuber, J. Improving generalization in meta reinforcement learning using learned objectives. In Proc. International Conference on Learning Representations (ICLR, 2020).
2. Kirsch, L. et al. Introducing symmetries to black box meta reinforcement learning. In Proc. AAAI Conference on Artificial Intelligence 36, 7202-7210 (Association for the Advancement of Artificial Intelligence, 2022).
3. Oh, J. et al. Discovering reinforcement learning algorithms. In Proc. Adv. Neural Inf. Process. Syst. 33, 1060-1070 (NeurIPS, 2020).
4. Xu, Z. et al. Meta-gradient reinforcement learning with an objective discovered online. In Proc. Adv. Neural Inf. Process. Syst. 33, 15254-15264 (NeurIPS, 2020).
5. Houthooft, R. et al. Evolved policy gradients. In Proc. Adv. Neural Inf. Process. Syst. 31, 5405-5414 (NeurIPS, 2018).
6. Lu, C. et al. Discovered policy optimisation. In Proc. Adv. Neural Inf. Process. Syst. 35, 16455-16468 (NeurIPS, 2022).
7. Silver, D. et al. Mastering the game of Go with deep neural networks and tree search. Nature 529, 484-489 (2016).
8. Schrittwieser, J. et al. Mastering Atari, Go, chess and shogi by planning with a learned model. Nature 588, 604-609 (2020).
9. Vinyals, O. et al. Grandmaster level in StarCraft II using multi-agent reinforcement learning. Nature 575, 350-354 (2019).
10. Hafner, D., Pasukonis, J., Ba, J. &amp; Lillicrap, T. Mastering diverse control tasks through world models. Nature 640, 647-653 (2025).
11. Fawzi, A. et al. Discovering faster matrix multiplication algorithms with reinforcement learning. Nature 610, 47-53 (2022).
12. Degrave, J. et al. Magnetic control of tokamak plasmas through deep reinforcement learning. Nature 602, 414-419 (2022).
13. Xu, Z., van Hasselt, H. P. &amp; Silver, D. Meta-gradient reinforcement learning. In Proc. Adv. Neural Inf. Process. Syst. 31, 2402-2413 (NeurIPS, 2018).
14. Zahavy, T. et al. A self-tuning actor-critic algorithm. In Proc. Adv. Neural Inf. Process. Syst. 33, 20913-20924 (NeurIPS, 2020).
15. Jackson, M. T. et al. Discovering general reinforcement learning algorithms with adversarial environment design. In Proc. Adv. Neural Inf. Process. Syst. 36, 79980-79998 (NeurIPS, 2023).
16. Sutton, R. S. &amp; Barto, A. G. Reinforcement learning: An Introduction (MIT Press, 2018).
17. Watkins, C. J. &amp; Dayan, P. Q-learning. Mach. Learn. 8, 279-292 (1992).
18. Schulman, J., Wolski, F., Dhariwal, P., Radford, A. &amp; Klimov, O. Proximal policy optimization algorithms. Preprint at https://arxiv.org/abs/1707.06347 (2017).
19. Jaderberg, M. et al. Reinforcement learning with unsupervised auxiliary tasks. In Proc. International Conference on Learning Representations (ICLR, 2017).
20. Barreto, A. et al. Successor features for transfer in reinforcement learning. In Proc. Adv. Neural Inf. Process. Syst. 30, 4055-4065 (NeurIPS, 2017).
21. Bellemare, M. G., Dabney, W. &amp; Munos, R. A distributional perspective on reinforcement learning. In Proc. International Conference on Machine Learning 449-458 (PMLR, 2017).
22. Bellemare, M. G., Naddaf, Y., Veness, J. &amp; Bowling, M. The arcade learning environment: an evaluation platform for general agents. J. Artif. Intell. Res. 47, 253-279 (2013).
23. Cobbe, K., Hesse, C., Hilton, J. &amp; Schulman, J. Leveraging procedural generation to benchmark reinforcement learning. In Proc. International Conference on Machine Learning 2048-2056 (PMLR, 2020).
24. Hochreiter, S. &amp; Schmidhuber, J. Long short-term memory. Neural Comput. 9, 1735-1780 (1997).
25. Veeriah, V. et al. Discovery of useful questions as auxiliary tasks. In Proc. Adv. Neural Inf. Process. Syst. 32, 9306-9317 (NeurIPS, 2019).
26. Munos, R., Stepleton, T., Harutyunyan, A. &amp; Bellemare, M. Safe and efficient offpolicy reinforcement learning. In Proc. Adv. Neural Inf. Process. Syst. 29, 1054-1062 (NeurIPS, 2016).
27. Finn, C., Abbeel, P. &amp; Levine, S. Model-agnostic meta-learning for fast adaptation of deep networks. In Proc. International Conference on Machine Learning 70, 1126-1135 (PMLR, 2017).
28. Mnih, V. et al. Asynchronous methods for deep reinforcement learning. In Proc. International Conference on Machine Learning 48, 1928-1937 (PMLR, 2016).
29. Agarwal, R., Schwarzer, M., Castro, P. S., Courville, A. C. &amp; Bellemare, M. Deep reinforcement learning at the edge of the statistical precipice. In Proc. Adv. Neural Inf. Process. Syst. 34, 29304-29320 (NeurIPS, 2021).
30. Kapturowski, S. et al. Human-level Atari 200x faster. In Proc. International Conference on Learning Representations (ICLR, 2023).
31. Hafner, D. Benchmarking the spectrum of agent capabilities. In Proc. International Conference on Learning Representations (ICLR, 2022).
32. Küttler, H. et al. The nethack learning environment. In Proc. Adv. Neural Inf. Process. Syst. 33, 7671-7684 (NeurIPS, 2020).
33. Hambro, E. et al. Insights from the NeurIPS 2021 NetHack challenge. In Proc. NeurIPS 2021 Competitions and Demonstrations Track 41-52 (PMLR, 2022).
34. Espeholt, L. et al. IMPALA: scalable distributed deep-RL with importance weighted actorlearner architectures. In Proc. International Conference on Learning Representations (ICLR, 2018).
35. Beattie, C. et al. DeepMind Lab. Preprint at https://arxiv.org/abs/1612.03801 (2016).
36. Racanière, S. et al. Imagination-augmented agents for deep reinforcement learning. In Proc. Adv. Neural Inf. Process. Syst. 30, 5690-5701 (NeurIPS, 2017).
37. Schmidhuber, J. Evolutionary Principles in Self-referential Learning, or on Learning How to Learn: the Meta-meta-… Hook. PhD thesis, Technische Univ. München (1987).
38. Schmidhuber, J. A possibility for implementing curiosity and boredom in model-building neural controllers. In Proc. International Conference on Simulation of Adaptive Behavior: from Animals to Animats 222-227 (MIT Press, 1991).
39. Schmidhuber, J., Zhao, J. &amp; Wiering, M. Simple Principles of Metalearning. Report No. IDSIA-69-96 (Istituto Dalle Molle Di Studi Sull Intelligenza Artificiale, 1996).
40. Thrun, S. &amp; Pratt, L. Learning to Learn: Introduction and Overview 3-17 (Springer, 1998).
41. Pan, S. J. &amp; Yang, Q. A survey on transfer learning. IEEE Trans. Knowl. Data Eng. 22, 1345-1359 (2009).
42. Parisi, G. I., Kemker, R., Part, J. L., Kanan, C. &amp; Wermter, S. Continual lifelong learning with neural networks: a review. Neural Netw. 113, 54-71 (2019).
43. Caruana, R. Multitask learning. Mach. Learn. 28, 41-75 (1997).
44. Feurer, M. &amp; Hutter, F. Hyperparameter Optimization 3-33 (Springer, 2019).
45. Yao, Q. et al. Taking human out of learning applications: a survey on automated machine learning. Preprint at https://www.arxiv.org/abs/1810.13306v3 (2018).
46. Storck, J., et al. Reinforcement driven information acquisition in non-deterministic environments. In International Conference on Artificial Neural Networks 2, 159-164 (ICANN, 1995).

47. Duan, Y. et al. RL 2 : fast reinforcement learning via slow reinforcement learning. Preprint at https://arxiv.org/abs/1611.02779 (2016).
48. Niv, Y., Joel, D., Meilijson, I. &amp; Ruppin, E. Evolution of reinforcement learning in uncertain environments: a simple explanation for complex foraging behaviors. Adapt. Behav. 10, 5-24 (2002).
49. Xiong, Z., Zintgraf, L., Beck, J., Vuorio, R. &amp; Whiteson, S. On the practical consistency of meta-reinforcement learning algorithms. Preprint at https://arxiv.org/abs/2112.00478 (2021).
50. Sutton, R. S. &amp; Tanner, B. Temporal-difference networks. In Proc. Adv. Neural Inf. Process. Syst. 17, 1377-1384 (NeurIPS, 2004).
51. Mnih, V., Kavukcuoglu, K., Silver, D. et al. Human-level control through deep reinforcement learning. Nature 518, 529-533 (2015).
52. Cobbe, K., Hilton, J., Klimov, O., and Schulman, J. Phasic policy gradient. In Proc. International Conference on Machine Learning 139, 2020-2027 (PMLR, 2021).
53. Hessel, M. et al. Rainbow: combining improvements in deep reinforcement learning. In Proc. AAAI Conference on Artificial Intelligence 32, 3215-3222 (Association for the Advancement of Artificial Intelligence, 2018).

Publisher's note Springer Nature remains neutral with regard to jurisdictional claims in published maps and institutional affiliations.

<!-- image -->

Open Access This article is licensed under a Creative Commons AttributionNonCommercial-NoDerivatives 4.0 International License, which permits any non-commercial use, sharing, distribution and reproduction in any medium or

format, as long as you give appropriate credit to the original author(s) and the source, provide a link to the Creative Commons licence, and indicate if you modified the licensed material. You do not have permission under this licence to share adapted material derived from this article or parts of it. The images or other third party material in this article are included in the article's Creative Commons licence, unless indicated otherwise in a credit line to the material. If material is not included in the article's Creative Commons licence and your intended use is not permitted by statutory regulation or exceeds the permitted use, you will need to obtain permission directly from the copyright holder. To view a copy of this licence, visit http:// creativecommons.org/licenses/by-nc-nd/4.0/.

© The Author(s) 2025

## Article Methods

## Meta-network

The meta-network maps a trajectory of agent outputs along with relevant quantities from the environment to targets: m f s f s : ( ), ( ), η θ t θ t - ↦ a r b f s f s a r b ^ ^ ^ , , ,…, ( ), ( ), , , , , , t t t θ t n θ t n t n t n t n + + + + + - π y z where η repre­ sents meta-parameters, and fθ = [πθ(s), yθ(s), zθ(s), qθ(s)] is the agent output with parameters θ. a, r and b are an action taken by the agent, a reward and an episode termination indicator, respectively. θ - is an exponential moving average of parameters θ. This functional form allows the meta-network to search over a strictly larger space of rules compared with meta-learning a scalar loss function. This is further discussed in Supplementary Information.

The meta-network processes the inputs by unrolling a long short-term memory (LSTM) backwards in time as illustrated in Fig. 1c. This allows it to take into account n-step future information to produce targets, as in multi-step RL methods such as temporal-difference methods TD(λ) 54 . We found that this architecture is computationally more efficient than alternatives such as transformers, while achieving a similar performance, as shown in Extended Data Fig. 3b.

The action-specific inputs and outputs are processed in the meta-network using shared weights over the action dimension, and an intermediate embedding is computed by averaging across it. This allows the meta-network to process any number of actions. More details about it can be found in Supplementary Information.

To allow the meta-network to discover a wider class of algorithms, such as reward normalization, that require maintaining statistics over an agent's lifetime, we add an additional recurrent neural network. This 'meta-RNN' is unrolled forward across agent updates (from θi to θi+1), rather than across time steps in an episode. The core of the meta-RNN is another LSTM module. For each of the agent updates, the whole batch of trajectories is embedded into a single vector that is passed to this LSTM. The meta-RNN can potentially capture the learning dynamics throughout the agent's lifetime, producing targets that are adaptive to the specific agent and the environment. The meta-RNN slightly improved the overall performance, as shown in Extended Data Fig. 3a. Further details are described in Supplementary Information.

## Meta-optimization stabilization

A number of challenges arise when we discover at a large scale, mainly because of unbalanced gradient signals coming from agents in different environments and myopic gradients caused by long lifetimes of agents. We introduce a few methods to alleviate these problems.

First, when estimating the advantage term in the advantage actorcritic method to estimate ∇θ J(θ) in the meta-gradient, we normalize the advantage term as follows: A = (A - μ)/σ, where A is a normalized advantage and μ and σ are the exponentially moving average and standard deviation of advantages accumulated over the agent's lifetime. We found that this makes the scale of the advantage term balanced across different environments. In addition, when aggregating the metagradient from the population of agents, we take the average of the meta-gradients over all agents after applying a separate Adam optimizer to the meta-gradient calculated from each agent: η η g ← + ∑ ADAM( ) n i n i 1 =1 , where gi is the meta-gradient estimation from the ith agent in the population. We found that this helps to normalize the magnitude of the meta-gradients from each agent.

We add two meta-regularization losses (Lent and LKL) to the metaobjective J(η) as follows: E E J θ L θ L θ [ ( ) - ( ) - ( )] θ ent KL E . L θ ( ) =- s a ent , E H s H a [ ( ( )) + ( (s, ))] θ θ y z is an entropy regularization of predictions y and z, where H(⋅) is the entropy of the given categorical distribution. We found that this helps prevent the predictions from converging prematurely. L θ D ^ ( ) = ( || ) θ KL KL - π π is the Kullback-Leibler divergence between the policy of a target network with an exponential moving average of the agent parameters (θ - ) and the meta-network's policy target (π^ ). This prevents the meta-network from proposing excessively aggressive updates that could lead to collapse.

It is noted that these methods are used only to stabilize metaoptimization, and they do not determine how the agents are updated. The meta-learned rule still solely determines how the agents are updated.

## Implementation details

We developed a framework that uses JAX library 55,56 and distributes computation across tensor processing units (TPUs) 57 inspired by the Podracer architectures 58 . In this framework, each agent is simulated independently, with the meta-gradients of all agents being calculated in parallel. The meta-parameters are updated synchronously by aggregating meta-gradients across all agents. We used MixFlow-MG 59 to minimize the computational cost of the runs.

For Disco57, we instantiate 128 agents by cycling through the 57 Atari environments in lexicographic order. For Disco103, we instantiate 206 agents, with two copies of each environment from Atari, ProcGen and DMLab-30. Disco57 was discovered using 1,024 TPUv3 cores for 64 hours, and Disco103 was discovered using 2,048 TPUv3 cores for 60 hours.

The meta-value function used to calculate the meta-gradient is updated using V-Trace 34 , with a discount factor of 0.997 and a TD(λ) coefficient of 0.95. The meta-value function and agent networks are optimized using an Adam optimizer with a learning rate of 0.0003. For meta-parameter updates, we use the Adam optimizer with a learning rate of 0.001 and gradient clipping of 1.0. Each agent is updated based on a batch of 96 trajectories with 29 time steps each. In each batch, on-policy trajectories and trajectories sampled from the replay buffer are mixed, with replay trajectories accounting for 90% of each batch. At each meta-step, 48 trajectories are generated to calculate the meta-gradient and update the meta-value function.

Each agent's parameters are reset after it has consumed its allocated experience budget. When resetting, a new experience budget is sampled from the categories (200 million, 100 million, 50 million, 20 million) with a weight inversely proportional to the budget, such that the same amount of total experience is sampled in each category. This was based on our observation that much of learning happens early in the lifetime and demonstrated a marginal improvement in our preliminary small-scale investigation.

## Hyperparameters and evaluation

For evaluation on held-out benchmarks, we only tuned the learning rate from {0.0001, 0.0003, 0.0005}. The rest of the hyperparameters were selected based on baseline algorithms from the literature.

The evaluation on Atari games (shown in Fig. 2a and Extended Data Table 1) used a version of the IMPALA 34 network with an increased parameter count that matches the agent network size used by MuZero 8 . Specifically, we used a network with 4 convolutional residual blocks with 256, 384, 384 and 256 filters, a shared fully connected final layer of 768 dimensions, and an LSTM-based action-conditional predictions component that is composed of an LSTM with a 1,024 hidden state dimension and a 1,024-dimensional fully connected layer. DMLab-30 evaluations (Fig. 2c and Extended Data Table 3) use the same action space discretization and agent network architecture as used in IMPALA. See Extended Data Table 6 for the list of hyperparameters. To verify the statistical significance of our evaluations, we used two random seeds for initialization on each environment from Atari, ProcGen and DMLab, three seeds on Crafter and NetHack, and five seeds on Sokoban.

## Analysis details

For the prediction analysis in Fig. 4c, we train multiple 3-layer perceptrons (MLPs) with 128, 64 and 32 hidden units for each layer respectively. The MLPs are trained to predict quantities such as future entropy and rewards from the outputs of an agent that has been trained on different Atari games using Disco57. We use 10 Atari games (Alien, Amidar, Battle Zone, Frostbite, Gravitar, Qbert, Riverraid, Road Runner, Robotank and Zaxxon). The values shown in Fig. 4c are R 2 scores for future entropy and test accuracy for large-reward events using fivefold cross-validation. Extended Data Fig. 2 provides an additional prediction analysis for more quantities. For high-dimensional outputs (y, z, za), we used a larger 3-layer MLP with 256 hidden units each.

## Data availability

No external data were used for the results presented in the article.

## Code availability

We provide the meta-training and evaluation code, with the metaparameters of Disco103, under an open source licence at https://github. com/google-deepmind/disco\_rl. All of the benchmarks presented in the article are publicly available.

54. Sutton, R. S. Learning to predict by the methods of temporal differences. Mach. Learn. 3, 9-44 (1988).
55. Bradbury, J. et al. JAX: composable transformations of Python+ NumPy programs. http://github.com/jax-ml/jax (2018).
56. DeepMind et al. The DeepMind JAX ecosystem. GitHub http://github.com/googledeepmind (2020).
57. Jouppi, N. P. et al. In-datacenter performance analysis of a tensor processing unit. In Proc. Annual International Symposium on Computer Architecture 1-12 (ICSA, 2017).
58. Hessel, M. et al. Podracer architectures for scalable reinforcement learning. Preprint at https://arxiv.org/abs/2104.06272 (2021).
59. Kemaev, I., Calian, D. A., Zintgraf, L. M., Farquhar, G. &amp; van Hasselt, H. Scalable meta-learning via mixed-mode differentiation. In Proc. International Conference on Machine Learning 267, 29687-19605 (PMLR, 2025).

Acknowledgements We thank S. Flennerhag, Z. Marinho, A. Filos, S. Bhupatiraju, A. György and A. A. Rusu for their feedback and discussions about related ideas; B. Huergo Muñoz, M. Kroiss and D. Horgan for their help with the engineering infrastructure; R. Hadsell, K. Kavukcuoglu, N. de Freitas and O. Vinyals for their high-level feedback on the project; and S. Osindero and D. Precup for their feedback on an early version of this work.

Author contributions J.O., I.K., G.F. and D.A.C. contributed equally. J.O., G.F., I.K., D.A.C. and L.Z. developed and analysed the method with advice from H.v.H., S.S. and D.S. J.O., G.F., M.H., D.A.C. and I.K. evaluated the method. I.K. led engineering with contributions from J.O., D.C. and G.F. J.O. and G.F. wrote the paper with contributions from L.Z. and D.A.C. H.v.H., S.S. and D.S. advised the team. J.O. and D.S. led the project.

Competing interests A patent application(s) directed to aspects of the work described has been filed and is pending as of the date of manuscript submission. Google LLC has ownership and potential commercial interests in the work described.

## Additional information

Supplementary information The online version contains supplementary material available at https://doi.org/10.1038/s41586-025-09761-x.

Correspondence and requests for materials should be addressed to Junhyuk Oh or David Silver.

Peer review information Nature thanks Kenji Doya, Joel Lehman and the other, anonymous, reviewer(s) for their contribution to the peer review of this work.

Reprints and permissions information is available at http://www.nature.com/reprints.

## Article

Extended Data Fig. 1 | Robustness of DiscoRL. The plots show the performance of Disco57 and Muesli on Ms Pacman by varying agent settings. 'Discovery' and 'Evaluation' represent the setting used for discovery and evaluation, respectively. (a) Each rule was evaluated on various agent network sizes. (b) Each rule was evaluated on various replay ratios, which define the

<!-- image -->

proportion of replay data in a batch compared to on-policy data. (c) A sweep over optimisers (Adam or RMSProp), learning rates, weight decays, and gradient clipping thresholds was evaluated (36 combinations in total) and ranked according to the final score.

<!-- image -->

Extended Data Fig. 2 | Detailed results for the regression and classification analysis. Each cell represents the test score of one MLP model that has been trained to predict some quantity (columns) given the agent's outputs (rows).

## Article

Extended Data Fig. 3 | Effect of meta-network architecture. (a) The x-axis represents the number of environment steps in evaluation and the y-axis the IQM on the Atari benchmark. All methods are discovered from 16 randomly selected Atari games. The meta-RNN component slightly improves performance. The shaded areas show 95% confidence intervals. (b) The x-axis represents the number of environment steps in evaluation and the y-axis the IQM on the

<!-- image -->

Atari benchmark. All methods are discovered from 16 randomly selected Atari games. Each curve corresponds to a different meta-network architecture, with varying number of LSTM hidden units, or its LSTM component is replaced by a transformer. The choice of the meta-net architecture minimally affects performance. The shaded areas show 95% confidence intervals.

<!-- image -->

Extended Data Fig. 4 | Computational cost comparison. The x-axis represents the amount of TPU hours spent for evaluation. The y-axis represents the performance on the Atari benchmark. Each algorithm was evaluated on 57 Atari games for 200 M environment steps. DiscoRL reached MuZero's final performance with approximately 40% less computation.

## Article

## Extended Data Table 1 | Atari57 result

Each algorithm was evaluated at 200 M environment steps. The best result for each game is shown in bold.

## Extended Data Table 2 | ProcGen result

Best result for each game shown in bold. The agents were trained and evaluated on 500 training levels.

## Article

## Extended Data Table 3 | DMLab-30 result

Best result for each task shown in bold.

## Extended Data Table 4 | NetHack result

Comparison to top 4 submissions from the "Final (Neural)" leaderboard of the NetHack NeurIPS 2021 Challenge 33 . Note that median scores were used for ranking submissions on the leaderboard, whereas we report mean scores to be consistent with other benchmarks.

## Article

## Extended Data Table 5 | Crafter result

Dreamer, Rainbow, PPO, Disco57 @1 M and Disco103 @1 M all use the same data budget of 1 M environment steps, while Disco57 @20 M and Disco103 @20 M use 20 M steps.

## Extended Data Table 6 | Hyperparameters of agents in evaluation

## Supplementary information

## Discovering state-of-the-art reinforcement learning algorithms

In the format provided by the authors and unedited

Nature | www.nature.com/nature

## Discovering state-of-the-art reinforcement learning algorithms (Supplementary information)

Junhyuk Oh † , Greg Farquhar † , Iurii Kemaev † , Dan A. Calian † , Matteo Hessel, Luisa Zintgraf, Satinder Singh, Hado van Hasselt, David Silver

All authors are affiliated with Google DeepMind.

† These authors contributed equally to this work.

## Contents

| 1 Design of Meta-Learned Rule   | 1 Design of Meta-Learned Rule   | 1 Design of Meta-Learned Rule                                   | 2                                   |
|---------------------------------|---------------------------------|-----------------------------------------------------------------|-------------------------------------|
|                                 | 1.1 .                           | Search space . . . . . . . . . . . . . . . . . . . . . . . . .  | . . . . . . . . . . . . . . . . . 2 |
|                                 | 1.2                             | Generality of meta-learning targets . . . . . . . . . . . . . . | . . . . . . . . . . . . . . . . . 4 |
|                                 | 1.3                             | Distance function . . . . . . . . . . . . . . . . . . . . . . . | . . . . . . . . . . . . . . . . . 4 |
| 2                               | Meta-Network                    | Details                                                         | 5                                   |
|                                 | 2.1                             | Action-invariant architecture . . . . . . . . . . . . . . . . . | . . . . . . . . . . . . . . . . . 5 |
|                                 | 2.2                             | Meta-RNN architecture . . . . . . . . . . . . . . . . . . . .   | . . . . . . . . . . . . . . . . . 6 |
| 3                               |                                 | Meta-Optimisation Details                                       | 6                                   |
| List of Figures                 | List of Figures                 | List of Figures                                                 |                                     |
| 1                               |                                 | Approximation of C51 and PPOwith meta-network . . . . .         | . . . . . . . . . . . . . . . . . 3 |
|                                 | 2                               | Expressiveness of target-based rule . . . . . . . . . . . . . . | . . . . . . . . . . . . . . . . . 3 |
|                                 | 3                               | Gradient norm of different loss functions . . . . . . . . . . . | . . . . . . . . . . . . . . . . . 5 |
|                                 | 4                               | Meta-network illustration . . . . . . . . . . . . . . . . . . . | . . . . . . . . . . . . . . . . . 5 |
| List of Tables                  | List of Tables                  | List of Tables                                                  | List of Tables                      |
|                                 | 1                               | Meta-network inputs . . . . . . . . . . . . . . . . . . . . .   | . . . . . . . . . . . . . . . . . 2 |

Table 1: Meta-network inputs. For each input, we give examples of the RL algorithmic concepts that inspire it, and example algorithms that use such inputs in computing their objectives. To represent a scalar with y or z, the agent could use a sparse vector, or encode the scalar using a categorical representation (like the two-hot value representation used in prior work 3 ). θ - represents exponentially moving parameters.

| Input                         | Inspiration                                                                                                                                      |
|-------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| y(s)                          | V(s) [A2C 1 , PPO 2 , MuZero 3 , Muesli 4 , Dreamer 5 ] Distributional V(s) [DA2C 6 ]                                                            |
| z(s, a)                       | Q(s, a) [DQN 7 , MuZero, Muesli, Dreamer] Distributional Q(s,a) [C51 8 ] Successor Features [GPI 9 ] Next-state reward [MuZero, Muesli, Dreamer] |
| π(s, a)                       | Policy losses and targets [PG, PPO, MPO 10 ] Entropy regularisation [A2C, PPO]                                                                   |
| yθ -(s), zθ -(s,a), πθ -(s,a) | Target networks [DQN, C51, TD3 11 ]                                                                                                              |
| µ(s, ataken)                  | Off-policy corrections [PPO, IMPALA 12 , Retrace 13 ]                                                                                            |
| r(s, ataken)                  | Necessary for RL                                                                                                                                 |
| episode termination           | Necessary for RL                                                                                                                                 |
| q(s, a)                       | Avoid requirement to rediscover concept of action-value [DQN] Semantics are defined by the hardcoded Laux                                        |

## 1 Design of Meta-Learned Rule

The architecture of the meta-learned rule was designed such that its search space encompasses many foundational concepts from existing reinforcement learning (RL) rules. Additionally, some components were designed to make meta-optimisation easier without compromising the generality of the meta-learned rule. The following sections discuss how the meta-learned rule relates to hand-crafted algorithms (Sec. 1.1), why meta-learning targets is more general than meta-learning loss (Sec. 1.2), and why the meta-learned rule is easier to optimise compared to alternatives (Sec. 1.3).

## 1.1 Search space

Our meta-learned rule requires the agent to produce an observation-conditional vector prediction (y(s) ∈ Rm ) and an action-conditional vector prediction (z(s, a) ∈ Rm ). The meta-network takes these predictions as input, along with other agent outputs, rewards, and an episode-termination indicator. The meta-network outputs are targets towards which the agent's predictions may be updated.

This basic structure, as well as the specific inputs chosen for the meta-network, are designed to incorporate the underlying principles of successful hand-crafted algorithms. Table 1 enumerates the full set of meta-network inputs and describes their relation to existing RL algorithms.

The expressiveness of this functional signature for the meta-network would allow DiscoRL, with an unbounded capacity of the meta-network, a sufficient dimensionality of y and z, and an appropriate distance function, to represent the objective functions of many standard algorithms, including A2C, DQN, and C51.

In practice, we have a limited capacity meta-network, fixed dimensionality of y and z, and choose to use a KL-divergence distance function for its favorable meta-optimisation behaviour (see below). Even with these constraints, we find that our meta-network can effectively represent sophisticated target-generating functions from hand-crafted algorithms, like the distributional bootstrap and projection of C51 (see Figure 1).

## Limitations

As is common in human-led RL research, we focused on a broad but somewhat restricted class of algorithms. For example, the meta-network does not directly get access to observations of the environment. This promotes generalisation across environments, but precludes learning models of observations, inverse dynamics models, or observation-based auxiliary tasks like pixel control 14 . There is no dedicated transition-model component, so while DiscoRL can make multi-step predictions about the future, these may not be conditional on multi-action sequences, as in some model-based algorithms. Other more exotic pieces of information about the state of the agent, such as the internal activations of its network, are also not accessible to the metanetwork, so objectives like feature control 14 cannot be represented. Lastly, the scope of discovery space does not include the data sampling and collection mechanism. DiscoRL was discovered with sampling actions from the softmax policy with a replay buffer for learning from off-policy experiences..

Fig. 1: Approximation of C51 and PPO with meta-network. (a) The meta-network was trained to predict C51 value targets on an online synthetic data. The data was generated by a mixture of Gaussians for the distributional value. (Left) The meta-network achieved a near-zero loss for approximating C51 targets. The next-value baseline uses vt+1 as a prediction. (Right) The meta-network approximately matched the groundtruth C51 target for a non-trivial multi-modal target after training. (b) The meta-network was trained to predict PPO-Clipped ratio on an online synthetic data. It was able to outperform two baselines: a constant zero and PPO ratio without clipping.

<!-- image -->

Fig. 2: Target-based rules can approximate temporal-difference rules, whereas loss-based rules cannot. Given two scalar input values (x = [v,v′ ]), we consider a simple temporal-difference (TD) loss, L∗ (x) = 1 2 ||v-{v′}||2 , where {·} stops the gradient flow for value bootstrapping. We train two variants of neural networks to approximate the TD gradients with respect to each input value as follows: ∂L∗ ∂v = v-v′ and ∂ L∗ ∂v′ =0. (a) In the loss network, the loss is defined as L= fθ (x) where fθ is a neural network parameterised by θ. (b) In the target network, the loss is given by L =D( fθ (x),x), where D is a L2 distance function, and fθ (x) : R2 ↦→R2 is a neural network that produces a target for each input value. (c) In both cases, θ is updated to approximate the TD gradients by minimising the loss L(θ) = 1 2 ||gmeta -gTD||2 , where gmeta = ∇xL(x) and gTD = ∇xL∗ (x), for randomly sampled values x = [v, v′ ]. The target network approximates TD gradients better than the loss network.

<!-- image -->

## 1.2 Generality of meta-learning targets

In this section, we show that meta-learning target functions instead of loss functions provides a strictly larger space of update rules for discovery. Our approach meta-learns a target function towards which the agent updates its predictions. To simplify notations without loss of generality, let us define the agent's loss function as follows:

<!-- formula-not-decoded -->

where ˆ y = f (y) is a target produced by meta-network f , and y is a prediction from the agent. D(·, ·) is a distance function between two vectors. The gradient with respect to the agent's prediction ∇yL defines an update rule, i.e., howmuch the agent should adjust its prediction.

A conceptually simpler alternative would be to directly meta-learn a loss function (i.e., L = f (y)) such that backpropagation through the meta-network directly gives a gradient ∇yL = ∇y f (y). This approach has been widely adopted in prior work 15-17 .

The space of gradient fields that each approach can represent can be written as

<!-- formula-not-decoded -->

where F is the function space that neural networks can represent. We show that Gloss ⊆Gtarget by showing that for any gradient field gloss ∈Gloss, there exists gtarget ∈Gtarget that can approximate gloss arbitrarily well. The below is the sketch of the proof.

Let D( ˆ y,y) = 1 2 ∥ˆ y-y∥2 be the squared L2 distance. For this choice of D, the effective gradient field for the target function is gtarget =∇yD( ˆ y, y) = y - ˆ y. Define a target function ˆ y = y-∇y f (y). Since neural networks are universal function approximators, this can be approximated by a neural network h ∈ F such that h(y) = ˆ y = y-∇y f (y) = y-gloss. Therefore, for any gloss ∈ Gloss, we can find gtarget ∈ Gtarget such that gtarget ≈ gloss by choosing an appropriate target and using the L2 distance as a loss. Therefore, Gloss ⊆ Gtarget. This argument is not specific to L2 distances, and can be extended to other smooth loss functions.

As an illustrative example, consider the policy gradient: ∇πLPG = Q(s,a)∇π logπ(a|s). This can be represented as a target-based loss L = 1 2 ∥ ˆπ -π∥2 with ˆπ =π-Q(s,a)∇π logπ(a|s) such that ∇πL=π- ˆπ = ∇πLPG.

Furthermore, the target-based rule can represent update rules that the loss-based rule cannot represent. By construction, the gradient vector fields of loss-based rules ∇y f (y) are always conservative, as they are the gradients of scalar potential functions. On the other hand, the gradient vector fields of many existing RL losses are not necessarily conservative. For example, semi-gradients for value bootstrapping cannot be represented as the gradient of a potential function. To empirically show this, we trained two neural networks, a loss network and a target network, to approximate the gradient of a simplified temporal-difference (TD) loss. The result in Fig. 2 shows that the target-based approach can approximate TD gradients, whereas the loss-based approach cannot. Therefore, meta-learning targets can search over a strictly larger space of update rules, including semi-gradient update rules in TD, than the update rules that meta-learned losses can capture in previous work.

## 1.3 Distance function

We use KL-divergence as the distance function between targets from the meta-network and the agent's predictions and policy: D( ˆ y, y) = DKL( ˆ y||y). This is because the gradient norm of KL-divergence function with respect to its input is bounded, whereas alternative distance functions such as L2 distance have unbounded gradient norms. To illustrate this, we visualise the gradient norms of different loss functions using a scalar prediction and a scalar target in Fig. 3. We found that using alternatives such as L2 distance can lead to meta-gradient explosion, making meta-optimisation unstable. A similar result was reported in a prior work on meta-gradient 18 .

Fig. 3: Gradient norm of different loss functions. Each image visualises the L1 norm of the gradient with respect to the scalar prediction (y) given each loss function. In 'Grad' and 'PolicyGrad', the target ˆ y is directly used as the gradient with respect to the input y and logσ(y), which result in unbounded gradients. L2 distance also produces large gradients as the prediction is farther away from the target, whereas the gradients are bounded between (-1, 1) in KL divergence.

<!-- image -->

Fig. 4: Meta-network illustration. (a) Per-action inputs (e.g., π(s,a),z(s,a)) are projected to embeddings using an encoder network φenc whose weights are shared across action dimension. The action-specific embeddings are averaged and concatenated to the per-state embedding. This is given as input to the LSTM that is unrolled over environment steps. The LSTM state is copied and concatenated to each action embedding, which is transformed to a policy target ˆπ using a shared decoder network φdec. Meanwhile, the LSTM output is also decoded to prediction targets ( ˆ y, ˆ z). (b) Meta-RNN is unrolled forward over agent update iterations. For each iteration, it takes as input the average of embeddings over all timesteps in each agent update. The output of meta-RNN is used as an additional input to the decoder when generating targets in (a) (not illustrated for simplicity).

<!-- image -->

## 2 Meta-Network Details

## 2.1 Action-invariant architecture

As illustrated in Fig. 4a our meta-network is action-invariant, as it can process inputs corresponding to any number of actions. To enable this, the meta-network processes the action-conditional inputs (e.g., π(s,ak), z(s, ak) for all action indices k) by first embedding each one into an (action-conditional) embedding h 1 ak using a neural network (φenc) with shared weights over the action dimension. Then, the meta-network extracts the embedding corresponding to the action taken in the environment h 1 a as well as the average embedding across all actions 1 K ∑k h 1 ak , and feeds these as inputs into the LSTM. The resulting functional form can thus process any number of actions, as the number of parameters of the meta-network does not depend on the number of actions. To produce outputs for each possible action (e.g. ˆπ), the LSTM output along with the action-conditional input embedding are fed through a separate output module.

The procedure may be summarised as follows:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

The full architecture is included in the released code (https://github.com/google-deepmind/disco\_rl).

## 2.2 Meta-RNN architecture

Fig. 4b shows the conceptual design of the meta-RNN. It is an additional recurrent module that takes as each input the embedding of an entire trajectory of data used for an agent update. It is unrolled forward over sequential agent updates, rather than over timesteps in an episode like the core LSTM of the metanetwork. The meta-RNN state is used as an additional input to the decoder for generating targets in Fig. 4a (not illustrated for simplicity).

The motivation behind the meta-RNN is to allow the meta-network to go beyond human-designed rules by taking into account the learning dynamics of the agent throughout its lifetime. Specifically, Meta-RNN allows the meta-network to capture information such as the sparsity and scale of rewards, and episode lengths to provide adaptive updates (e.g., reward normalisation).

## 3 Meta-Optimisation Details

When updating the meta-value function for A2C, we compute an exponential moving average of the first and second moment of the advantage with a decay of 0.99, and use this to perform advantage normalisation when calculating the A2C gradient.

During meta-optimisation, the agent parameters are updated using the Adam optimiser. We found it useful for meta-optimisation stability to suppress the dependence of the updated parameters θ on the second moment Adam statistics (implemented with a 'stop\_gradient' on the optimiser statistics). This is reasonable as our meta-optimisation horizon is shorter than the effective horizon on which these statistics are updated.

## References

- [1] Mnih, V. et al. Asynchronous methods for deep reinforcement learning. International conference on machine learning (2016).
- [2] Schulman, J., Wolski, F., Dhariwal, P., Radford, A. &amp; Klimov, O. Proximal policy optimization algorithms. arXiv preprint arXiv:1707.06347 (2017).
- [3] Schrittwieser, J. et al. Mastering atari, go, chess and shogi by planning with a learned model. Nature 588, 604-609 (2020).
- [4] Hessel, M. et al. Muesli: Combining improvements in policy optimization. International conference on machine learning (2021).
- [5] Hafner, D., Pasukonis, J., Ba, J. &amp; Lillicrap, T. Mastering diverse control tasks through world models. Nature (2025).

- [6] Li, S., Bing, S. &amp; Yang, S. Distributional advantage actor-critic. arXiv preprint arXiv:1806.06914 (2018).
- [7] Mnih, V. et al. Human-level control through deep reinforcement learning. nature 518, 529-533 (2015).
- [8] Bellemare, M. G., Dabney, W. &amp; Munos, R. A distributional perspective on reinforcement learning. International conference on machine learning (2017).
- [9] Barreto, A. et al. Successor features for transfer in reinforcement learning. Advances in neural information processing systems 30 (2017).
- [10] Abdolmaleki, A. et al. Maximum a posteriori policy optimisation. arXiv preprint arXiv:1806.06920 (2018).
- [11] Fujimoto, S., Hoof, H. &amp;Meger, D. Addressing function approximation error in actor-critic methods. International conference on machine learning (2018).
- [12] Espeholt, L. et al. IMPALA: Scalable distributed deep-rl with importance weighted actor-learner architectures. International conference on machine learning (2018).
- [13] Munos, R., Stepleton, T., Harutyunyan, A. &amp; Bellemare, M. Safe and efficient off-policy reinforcement learning. Advances in neural information processing systems 29 (2016).
- [14] Jaderberg, M. et al. Reinforcement learning with unsupervised auxiliary tasks. arXiv preprint arXiv:1611.05397 (2016).
- [15] Houthooft, R. et al. Evolved policy gradients. Advances in neural information processing systems 31 (2018).
- [16] Kirsch, L., van Steenkiste, S. &amp; Schmidhuber, J. Improving generalization in meta reinforcement learning using learned objectives. International conference on learning representations (2020).
- [17] Xu, Z. et al. Meta-gradient reinforcement learning with an objective discovered online. Advances in neural information processing systems 33 (2020).
- [18] Oh, J. et al. Discovering reinforcement learning algorithms. Advances in neural information processing systems 33 (2020).