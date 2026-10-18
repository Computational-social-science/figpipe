<!-- source: ! 2025-Nature-Optimizing generative AI by backpropagating language model feedback&SI.pdf -->
<!-- source_pdf: D:\2025-LLMs&LRMs\zero-shot CoT\! 2025-Nature-Optimizing generative AI by backpropagating language model feedback&SI.pdf -->
<!-- pages: 60 ; extracted_by: docling 2.140.0 -->

## Optimizing generative AI by backpropagating language model feedback

[https://doi.org/10.1038/s41586-025-08661-4](https://doi.org/10.1038/s41586-025-08661-4)

Received: 12 June 2024

Accepted: 16 January 2025

Published online: 19 March 2025

<!-- image -->

Check for updates Mert Yuksekgonul 1,4 ✉ , Federico Bianchi 1,4 , Joseph Boen 2,4 , Sheng Liu 2,4 , Pan Lu 2,4 , Zhi Huang 2,4 , Carlos Guestrin 1,3 &amp; James Zou 1,2,3 ✉

Recent breakthroughs in artificial intelligence (AI) are increasingly driven by systems orchestrating multiple large language models (LLMs) and other specialized tools, such as search engines and simulators. So far, these systems are primarily handcrafted by domain experts and tweaked through heuristics rather than being automatically optimized, presenting a substantial challenge to accelerating progress. The development of artificial neural networks faced a similar challenge until backpropagation and automatic differentiation transformed the field by making optimization turnkey. Analogously, here we introduce TextGrad, a versatile framework that performs optimization by backpropagating LLM-generated feedback to improve AI systems. By leveraging natural language feedback to critique and suggest improvements to any part of a system-from prompts to outputs such as molecules or treatment plans-TextGrad enables the automatic optimization of generative AI systems across diverse tasks. We demonstrate TextGrad's generality and effectiveness through studies in solving PhD-level science problems, optimizing plans for radiotherapy treatments, designing molecules with specific properties, coding, and optimizing agentic systems. TextGrad empowers scientists and engineers to easily develop impactful generative AI systems.

Large language models (LLMs) are transforming how breakthrough artificial intelligence (AI) systems are built 1 . The new generation of AI applications increasingly operate as compound systems, orchestrating multiple sophisticated components-from LLM-based agents to specialized tools such as simulators and web search engines. For instance, a system of LLMs communicating with symbolic solvers can solve olympiad-level maths problems 2 ; and a system of LLMs using search engines and code interpreter tools performs comparably to human competitive programmers 3 and solves real-world GitHub issues 4 . Despite these advances, many of these breakthroughs came from systems that are handcrafted by domain experts. Therefore, developing automated optimization algorithms is one of the most crucial challenges to build compound systems with LLMs and accelerate future breakthroughs 5-7 .

For the past 15 years, many advances in AI have relied on neural networks and differentiable optimization 8-12 . Components of neural networks (for example, two artificial neurons) communicate through differentiable functions such as matrix multiplications 13 . Therefore, communicating numerical gradients through each component by backpropagation 14 , which provides the direction to adjust each parameter to improve a model, has been the natural way to train AI models. However, differential optimization does not work easily for the new generation of generative AI systems because these systems often involve natural language interactions, black-box LLMs or external tools, making backpropagating of numerical gradients difficult.

To address this challenge, we introduce TextGrad to perform automatic 'differentiation' via text. While neural networks communicate through numerical values, modern AI systems communicate through unstructured data such as text, code, and images. In TextGrad, each AI system is transformed into a computation graph where components exchange these rich, unstructured variables through complex (not necessarily differentiable) functions. We use 'differentiation' as a metaphor, where LLMs provide feedback (dubbed 'textual gradients' 15 ) in the form of informative and interpretable natural language critiques, describing how each variable should be modified to improve the overall system. Textual gradients are propagated through arbitrary functions, such as LLM application-programming-interface (API) calls, simulators or external numerical solvers. Notably, the text feedback does not target the parameters of the underlying neural networks, and is thus compatible with black-box APIs.

We demonstrate the power of TextGrad in diverse domains, ranging from question-answering benchmarks to radiotherapy treatment plan optimization and molecule generation (Fig. 1), all with a single framework without modifications for different tasks. LLMs can provide rich, legible and expressive natural language feedback to variables in this wide range of domains, such as proposing modifications to molecules, prompts to other LLMs and code snippets. Our framework is built on the premise that current state-of-the-art LLMs can reason about individual components and subtasks of the system that they optimize. Our results demonstrate the promise of TextGrad to automatically improve generative AI systems and its outputs.

## Article

<!-- image -->

c

1.

Analogy in abstractions

Input

Model

Loss

Optimizer Maths PyTorch TextGrad

- Automatic differentiation 2.

PyTorch and TextGrad share the same syntax for backpropagation and optimization Forward pass Backward pass Updating variable

<!-- image -->

g

Code at iteration t + 1

You will answer a reasoning question. Think step by step. The last line of your response should be of the following format: 'Answer: $VALUE' where VALUE is a numerical value.

Prompt at initialization (accuracy = 77.8%)

You will answer a reasoning question. List each item and its quantity in a clear and consistent format, such as '- Item: Quantity'. Sum the values directly from the list and provide a concise summation. Ensure the final answer is clearly indicated in the format: 'Answer: $VALUE' where VALUE is a numerical value. Verify the relevance of each item to the context of the query and handle potential errors or ambiguities in the input. Double-check the final count to ensure accuracy."

Prompt after optimization (accuracy = 91.9%)

<!-- image -->

Fig. 1 | Overview of TextGrad. a, Neural network and backpropagation using numerical gradients. Backpropagation of gradients is the driving force of deep learning. Numerical gradients of a loss function with respect to variables such as ν1 are backpropagated through hidden states such as h1. b, Black-box AI systems and backpropagation using natural language 'gradients'. We do not have gradients for compound systems of black-box AI systems, but we can construct analogous backpropagation for text-based feedback, forming the basis of TextGrad. c, TextGrad shares the same abstractions and syntax as PyTorch, making it generalizable and easy to learn. In both cases, we use the same abstractions to instantiate network variables θ, target and predicted outputs y and y^, model f, loss function L, and gradient descent optimizer GD. For instance, in TextGrad, a model f can be a blackbox language model, where we consider a prompt to be the parameter we want to optimize. TextGrad mirrors PyTorch's abstraction for backpropagation, enabling optimization across black-box AI systems. d-g, Example applications of TextGrad to optimize molecular structures for properties such as drug-likeness and protein binding affinity (d), optimize solutions to coding problems (e), optimize radiotherapy treatment plans (f) and optimize prompts to improve the reasoning of language models (g).

a

<!-- image -->

```
∂L ∂x = ∇LLM (x, y, ∂L ∂y ) = "Here is a conversation with an LLM: {x|y}." + LLM (Here is a conversation with an LLM: {x|y}. Below are the criticisms on {y}: Explain how to improve {x}.) ∆ b ∂L ∂y
```

```
x new = TGD.step(x, ∂L ∂x ) LLM (Below are the criticisms on {x}: ∂L ∂x Incorporate the criticisms and produce a new variable.) = ∆ c
```

Fig. 2 | Illustrative implementation of TGD and TextGrad's backpropagation.

a, We illustrate how backpropagation works for a system of two language model calls. It is noted that we overload the notation to denote both cases when the output variable does and does not have successors. Here, green text indicates the parameter we want to optimize. b, We show an example implementation of the textual gradient operator. This operator provides a natural language feedback critique to the variable we want to optimize, where the critique

## Backpropagating LLM feedback with TextGrad

We first describe an example to demonstrate what TextGrad looks like for a system of two LLM calls, and give the more general form in Methods. Consider the following system:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

where we use + to denote the concatenation of two strings and use LLM(x) to give x as a prompt to a language model to collect the response. This structure is used frequently where a language model is used for evaluation, for example, in LLM-as-a-judge 16 .

In traditional automatic differentiation, we compute gradients using the chain rule to determine how to modify the numerical variables in a system to improve the system with respect to an objective function. In comparison, TextGrad generates feedback in the form of text to guide the modifications of unstructured variables in a system. It does not compute numerical gradients, but rather provides critiques suggesting specific modifications that would improve the system with respect to an objective function.

To improve an AI system, we instantiate an analogue of the backpro­ pagation 14 algorithm (Fig. 2a). Here, we use ∇LLM for the textual gradient describes how to modify the variable to improve the overall system. Here, the purple text indicates where an LLM is used in these operations. c, Example implementation of one TGD iteration. Given the current variable and the textual gradients (feedback) we collected for this variable, the optimizer seeks to update this variable to improve the whole system. The exact prompts we use are different to ensure generality and flexibility; we use these examples only for exposition.

operator when the forward function is an LLM call. A flexible way to instantiate ∇LLM can be found in Fig. 2b. In particular, this function returns a critique such as "The prediction can be improved by…" where the feedback describes how to modify a variable to improve the overall system with respect to an objective function, analogously to numerical gradients. In this context, a modifiable component can be a prompt, an intermediate output or the final prediction. In Fig. 2a, to backpropagate feedback to the prompt, we first collect feedback to the prediction variable using the evaluation. Then, given this feedback and the (LLM(Prompt + Question)) call, we collect the feedback on the prompt. More generally, we apply this procedure using the feedback obtained for all successors of a variable.

In numerical gradient descent, the parameter θ is combined with the gradients with respect to a loss function L by subtraction, for example, L L ( ) θ θ θ , = - θ θ new ∂ ∂ ∂ ∂ . Continuing the gradient-based optimization analogy, we use textual gradient descent (TGD), where the variable is updated using the feedback. In Fig. 2c, we show a concrete way to instantiate TGD. This step uses the textual gradient to modify components in ways that improve the system with respect to the objective function.

In automatic differentiation, the objective function is typically a differentiable function, such as mean-squared error. In TextGrad, the objective can be a complex and potentially non-differentiable or black-box function, where the domain and codomain of the function can be unstructured data. This choice adds important generality and

## Article

flexibility to the framework. For instance, we show that the objective function can be obtained by prompting a language model, an output of a code interpreter running unit tests or outputs of molecular simulation engines. A simple objective function using an LLM can look like the following:

Loss (question, solution) = LLM("Below is a multi-choice question and a solution: {question, solution} Your job is to investigate the solution. Critically go through reasoning steps, and. see if the prediction could be incorrect."),

where we can use this evaluation signal to optimize the code snippet, powered by the well-documented potential of LLMs to self-critique and self-improve 17-22 .

We use TextGrad to solve two broad categories of tasks. First, in test-time optimization, we directly treat a solution to a problem-for example, a code snippet, the solution to a question or a molecule-as an optimization variable. For instance, in the above question-answering objective function, we have a solution that we would like to improve at test time. Our framework produces the textual gradients for and iteratively improves the solution variable. Second, in prompt optimization, the goal is to find a prompt that improves the performance of an LLM in multiple queries for a task. For example, we may want to find a system prompt to an LLM that improves the performance on mathematical reasoning questions. In particular, we want the system prompt to generalize to work for new problems, in contrast to test-time optimization where the only goal is to improve a variable for the problem at hand at test time. Crucially, both types of problem are solved without handcrafting the framework.

We demonstrate the flexibility of TextGrad in a diverse array of applications. First, we optimize code snippets to solve hard problems from LeetCode, an online programming learning platform. Next, we optimize solutions to scientific questions. Third, we optimize prompts to guide the reasoning of LLMs. Fourth, we optimize radiotherapy treatment plans for patients with prostate cancer. Finally, we optimize compound systems involving multiple variables and longer chains. Furthermore, in Supplementary Note 8.1, we discuss how we optimize chemical structures for molecular property maximization as a case study. Across a dataset of 58 target proteins, TextGrad shows improved performance in ligand design compared with alternative molecule optimization methods (Extended Data Figs. 1 and 2).

## Code optimization

In code optimization, the goal is to modify a code to improve its correctness or runtime complexity. We often have a computation graph like the following:

```
Refinement objective = LLM (Problem + Code + Test-time instruction + Test results),
```

where we optimize the code to solve a given problem with limited, local unit-test supervision, and self-evaluation through a test instruction asking to critique the current iteration of the code. Figure 1e shows an example problem: "You are given an array nums of size n consisting of distinct integers from 1 to n and a positive integer k. Return the number of non-empty subarrays in nums that have a median equal to k". The first solution proposed by gpt-4o does not pass the tests. TextGrad identifies an edge case in the first solution and provides a suggestion on how to improve it. The optimized implementation passes all tests.

We use the LeetCode Hard dataset 23 to benchmark code optimization. LeetCode is an online platform that offers coding practice questions in preparation for technical interviews. The dataset contains examples of hard coding problems that are challenging for both humans and language models, where the success metric is completion rate (passing all test cases).

In LeetCode Hard, using gpt-4o in a zero-shot setting gets a 26% completion rate, whereas Reflexion 23 , a state-of-the-art self-refinement baseline, gets a 31% completion rate (Extended Data Fig. 3). With TextGrad, we achieve a completion rate of 36%. These improvements are more significant considering that Reflexion was run with in-context demonstrations and TextGrad did not use any demonstrations (that is, zero shot). We provide more details around the dataset, baselines and prompts in Supplementary Note 3.

## Solution optimization

In solution optimization, the goal is to improve the solution to a problem such as a question about quantum mechanics. We have the following relation:

Solution refinement objective

= LLM (Question + Solution + Test-time instruction),

where the parameter we optimize is the solution, and the loss function is obtained by an evaluation of the solution. In each iteration, the LLM is prompted with the question, current solution and a test-time instruction asking to critique the current iteration. Although an LLM may not get the solution to a problem right at the first attempt, it can improve the solution through iterative refinement 19,23 .

We explore solution optimization in question-answering datasets. We use Google-proof Question Answering (GPQA) 24 , a recent benchmark where multiple-choice questions in physics, biology and chemistry are created and labelled by domain experts who have or are pursuing PhD degrees; two challenging subsets (machine learning and college physics) of the Massive Multitask Language Understanding (MMLU) 25 question-answering benchmark that is used to track the progress of language modelling with undergraduate-level questions; MathVista 26 and ScienceQA 27 to test the visual question-answering ability in scientific domains.

With TextGrad, we improve the performance of gpt-4o across these benchmarks (Extended Data Fig. 4a). We improve the performance in MMLU subsets from 85.7% to 88.4% (machine learning) and from 91.2% to 95.1% (college physics), and GPQA from 51.0% to 55.0%. For multimodal reasoning tasks, compared with Reflexion, TextGrad achieves performance gains of 2.1% and 2.2% on MathVista and ScienceQA-IMG (the multimodal setting of ScienceQA). We provide further details in Supplementary Note 4.

## Prompt optimization for reasoning

LLMs show impressive performance in reasoning tasks, but their performance can be sensitive to the prompt used to guide their behaviour. With the right prompt, their reasoning can be significantly improved 28 . In prompt optimization, the goal is to find a prompt to guide the behaviour of an LLM such that it performs well on a given task. Often, we have a computation graph like the following:

<!-- formula-not-decoded -->

where we have a question, an answer to the question, and an evaluation indicating the quality of the output given the ground-truth answer. For instance, for a question-answering task, the evaluation metric could be the accuracy of the answer.

Here, given a handful of training examples to optimize a prompt, the goal is to maximize the performance of an LLM on the given task.

In our experiments, our goal is to improve the performance of a weaker and cheaper model (for example, gpt-3.5-turbo) using the feedback generated by stronger models (for example, gpt-4o). This task is useful in practice because after paying a fixed cost to optimize a prompt, the prompt-optimized weaker model can be used with cheaper inference costs instead of the stronger and more expensive model. Notably, we can decompose a prompt into instruction and in-context examples 1 , and apply the same strategy to optimize them jointly using textual gradients. For instance, we can initialize the in-context examples using input-output samples from the training dataset, then optimize them using TGD.

We use two standard reasoning tasks (object counting and word sorting) from Big Bench Hard 29 and the GSM8k grade-school maths problem-solving dataset 30 . Across the three datasets, TextGrad improves the performance of the zero-shot prompt (Extended Data Fig. 5a). TextGrad outperforms OPRO 31 , performs similarly to the state-of-the-art prompt optimization framework DSPy 5 for word sorting and GSM8k, and improves over it by 7.0% for object counting. We report ablations in Supplementary Table 1, finding that (1) jointly optimizing demonstrations and the instruction in a prompt improves the performance the most, and (2) optimizing the instruction alone still outperforms other existing methods. We provide examples of optimized instructions and demonstrations in Extended Data Fig. 5.

We perform further ablations to analyse the scalability and robustness of TextGrad. In Supplementary Note 6.1, we perform optimization using Llama-3.1-70B 32 , finding that optimizing the prompts using TextGrad for less capable open-source models is also effective. In Supplementary Note 6.2, we study the robustness of the optimized prompts, finding that prompts optimized for gpt-3.5-turbo can be transferred to open-source models such as Qwen-2.5 33 and Llama-3.2-9B 32 to improve their performance. Finally, in Supplementary Note 6.3, we study the cost-accuracy frontier of the methods, finding that TextGrad brings Pareto improvements.

## Radiotherapy treatment plan optimization

Radiotherapy is a cancer treatment that uses beams of intense energy, such as X-rays, to kill cancer cells. Before treatment, a team of radiation oncologists and planners collaborate to design an effective treatment plan. This involves determining the necessary dose of radiotherapy and pinpointing the exact locations that need treatment.

Treatment planning involves essentially a two-loop multi-objective optimization problem, where the inner loop aims to optimize the radiation dose delivery to the tumour (planning target volume (PTV)) while protecting healthy organs (organs at risk (OARs)), given the importance weights. The outer loop optimizes these importance weights to trade-off treatment effectiveness with protection. The main challenge lies in translating clinical goals into the weighted objective function. Currently, planners rely on time-consuming trial-and-error approaches to adjust importance weights, making the process time-consuming and costly 34,35 .

We apply TextGrad to perform the outer loop optimization. We perform this optimization at test time with gpt-4o over the importance weights represented as a string, for example, θ = "weight for PTV: [PTV WEIGHT], weight for bladder: [BLADDER WEIGHT], weight for rectum: [RECTUM WEIGHT], weight for femoral heads: [FH WEIGHT], weight for body: [BODY WEIGHT]". The evaluation uses the treatment plan P and the clinical goals g using an LLM:

θ P θ g ( ) = LLM( ( ), ), L

and the new importance weights are obtained by performing TGD. To further improve the LLM's capability to understand the relationship between the importance weights θ and the resulting plan P from the inner-loop optimizer, we provide a set of paired plans and their corresponding importance weights P θ {( , )} i i i N =1 as in-context examples for TGD. To evaluate a treatment plan, we adopt several commonly used metrics. We consider the mean dose delivered to the target/organ volume, as well as Dq, which denotes the minimum dose received by q% of the target/organ volume.

First, we show that the textual gradients generated by TextGrad provide meaningful feedback for this problem. As shown in Fig. 3a, when there is dose spillage outside the PTV, the textual gradient suggests an increase in the importance weight for the PTV. This adjustment results in a more uniform and confined dose for the PTV. However, this can lead to insufficient protection of the bladder and rectum as their relative weights are reduced. Therefore, in the following step, the feedback suggests slightly increasing the weights for the bladder and rectum, resulting in better protection (Fig. 3b,c).

We compared TextGrad-optimized plans with clinically approved plans used to treat five patients with prostate cancer. Although automated planning systems exist 36-39 , they have yet to become standard practice and cannot be used as a reliable source of ground truth. Therefore, manually designed and clinically approved plans continue to serve as the gold standard. In Fig. 3d, we assess TextGrad's capabilities in achieving clinical goals for the PTV region. TextGrad outperforms clinical plans, achieving a higher mean dose, and a D95 that exactly matches the prescribed dose, where D95 denotes the minimum dose received by 95% of the target/organ volume. In Fig. 3e, we focus on the protection of healthy organs. TextGrad-optimized plans achieve lower mean doses for these healthy organs, suggesting better organ protection than human-optimized plans. Overall, these results are presented as an illustrative demonstration of TextGrad's potential rather than a definitive statement on clinical effectiveness. In Extended Data Fig. 6, we show that TextGrad also outperforms a Bayesian optimization algorithm, and give further details in Methods.

## Optimizing compound AI systems

Finally, we investigate the ability of TextGrad to optimize compound AI systems involving multiple variables and longer chains of reasoning.

Our first study focuses on Chameleon 40 , a sophisticated agentic system with multiple LLM modules using diverse tools. Chameleon integrates various tools to tackle a broad range of tasks, leveraging abilities such as visual perception and knowledge retrieval. However, its original planning and execution pipeline is static with no feedback mechanism, which can lead to error accumulation as the steps progress.

To address this, we use TextGrad to optimize the solution steps provided by Chameleon. This process starts with a standard forward pass through all modules. Subsequently, it iteratively optimizes each module's output, starting from the first module and progressing to the last. For each module, the optimization process evaluates the final response using a loss function, computes gradients via TextGrad and backpropagates these gradients to update the module's output. By introducing this feedback loop, we address the limitations of static execution in the original Chameleon system. We evaluate this approach using ScienceQA-IMG, which requires the coordination of multiple tools in visual perception and knowledge retrieval (Supplementary Note 9).

The results in Fig. 4 show the effectiveness of TextGrad in optimizing Chameleon. Through the identification of errors in reasoning traces and iterative backpropagation of textual gradients to refine module outputs (as shown in Fig. 4a,b), TextGrad achieves a 5.7% increase over the baseline performance with 2 optimization iterations, and a 7.7% gain with 3 iterations (Fig. 4e). These findings highlight the potential of TextGrad to enhance compound systems like Chameleon.

In our second study, we use TextGrad to improve the spatial reasoning ability of multimodal models. In visual question answering, images are presented alongside questions related to the content of the images. To guide the model in answering the questions, we provide instructional prompts, such as "Answer the question based on the image, let's think

## Article

| Target   | Method               | Mean dose (Gy)   | D 95 (Gy)    |
|----------|----------------------|------------------|--------------|
|          | Clinical goal        | 70.20            | 70.20        |
| PTV      | Radiation oncologist | +1.97 (0.36)     | -0.10 (0.15) |
|          | TextGrad             | +0.51 (0.09)     | +0.00 (0.00) |

Fig. 3 | Radiotherapy treatment plan optimization. We visualize the backpropagated textual gradients adjusting importance weights of PTVs and OARs to balance tumour targeting and protection of OARs. a, The evolution of a plan from initialization to iteration 5. b, TextGrad iteratively improves the mean dose and reduces the dose variance of the PTV, achieving the clinical goal. c, TextGrad keeps the exposure for the bladder and rectum below clinically

<!-- image -->

allowed maximums. d,e, TextGrad-optimized plans have better dose metrics (mean dose and D95) for PTV than clinically optimized plans (d), and lower doses on the bladder and rectum, indicating better protection of OARs (e). Overall, these results are presented as an illustration of TextGrad's potential rather than a statement on actual clinical effectiveness. Values in bold indicate the best performing scores.

| Organ e   | Method               | Mean dose (Gy)   |
|-----------|----------------------|------------------|
| Bladder   | Radiation oncologist | 22.39 (5.55)     |
| Bladder   | TextGrad             | 20.92 (0.79)     |
| Rectum    | Radiation oncologist | 23.88 (6.45)     |
| Rectum    | TextGrad             | 17.18 (4.20)     |

step by step". Another language model evaluates the solution using a loss function prompt. Here we use TextGrad to jointly optimize the two sets of prompts-instructional prompt for the answer generation and the loss prompt for the evaluation-as well as the generated solution itself. All of these can be treated as separate variables in TextGrad, and optimized jointly. For evaluation, we use High-Quality Hallucination Benchmark (HQH) 41 , a spatial reasoning dataset with 1,600 visual question-answering pairs. The results in Fig. 4f show that optimizing solutions and prompts jointly with TextGrad achieves a 9% improvement over gpt-4o with chain of thought 42 and outperforms Reflexion.

## Discussion

TextGrad is built on three principles: (1) it is a general and performant framework that is not handcrafted for a specific application domain; (2) it is easy to use, mirroring PyTorch abstractions, thus allowing knowledge transfer; and (3) it is fully open source. Through TextGrad, we obtained state-of-the-art results in code optimization and PhD-level question answering, optimized prompts, and provided proof-of-concept results in optimizing molecules and treatment plans.

| Dataset       | Method                                  |   Accuracy (%) |
|---------------|-----------------------------------------|----------------|
| ScienceQA-IMG | Chameleon                               |           77.5 |
| ScienceQA-IMG | TextGrad (2 iterations of optimization) |           83.2 |
| ScienceQA-IMG | TextGrad (3 iterations of optimization) |           85.2 |

Fig. 4 | Optimizing compound AI systems. a, TextGrad enhances the solution generated by Chameleon, an agentic system that generates a plan followed by tool execution. We treat the output of each module as a separate variable to optimize and improve them. b, Textual gradients are computed and backpropagated through the tool execution chain. c, TextGrad iteratively optimizes the answer to a multimodal question. To improve the spatial reasoning ability of multimodal language models in visual question answering,

<!-- image -->

| Dataset   | Method                                      |   Accuracy (%) |
|-----------|---------------------------------------------|----------------|
| HQH       | Chain of thought                            |           70.0 |
| HQH       | Reflexion                                   |           72.0 |
| HQH       | TextGrad (prompt and solution optimization) |           79.0 |

we treat loss prompt, the instruction and the solution as variables to jointly optimize and improve them. d, With an example in HQH, we show how TextGrad jointly optimizes the prompts and solutions. e,f, TextGrad yields accuracy improvements of 7.7% and 9% on ScienceQA-IMG (e) and on HQH (f), respectively. Values in bold indicate the best performing scores. Bus image in d reproduced from ref. 41 under a Creative Commons licence CC BY 4.0.

## Article

Previous studies have explored using LLMs as optimizers for prompt engineering and self-improvement 5,23,31 . Although these frameworks demonstrated the capabilities of LLMs in specific domains such as prompt optimization, our work introduces a general framework based uniquely on backpropagating natural language feedback that extends beyond prompts to optimize diverse components including code, molecules and treatment plans.

There are various limitations that motivate future work to realize the potential of optimization frameworks powered by LLMs. We hope that TextGrad can be used to accelerate iterative processes in scientific discovery and increase the productivity of engineering efforts. Second, there is a large design space for algorithms to backpropagate textual feedback. We believe that there are many connections to be drawn between numerical optimization, automatic differentiation and TextGrad. Finally, although we conducted proof-of-concept applications of TextGrad to design molecules and treatment plans with in silico validations, the ultimate test requires experimental and clinical assessments, which are outside of the scope of this paper.

As AI systems shift from training individual models to optimizing compound systems with multiple interacting LLM components and tools, we need a new generation of optimizers. TextGrad combines the reasoning power of LLMs with the decomposable efficiency of backpropagation to create a general framework to optimize AI systems.

## Online content

Any methods, additional references, Nature Portfolio reporting summaries, source data, extended data, supplementary information, acknowledgements, peer review information; details of author contributions and competing interests; and statements of data and code availability are available at https://doi.org/10.1038/s41586-025-08661-4.

1. Brown, T. et al. Language models are few-shot learners. Adv. Neural Inf. Process. Syst. 33, 1877-1901 (2020).
2. Trinh, T. H., Wu, Y., Le, Q. V., He, H. &amp; Luong, T. Solving olympiad geometry without human demonstrations. Nature 625, 476-482 (2024).
3. Li, Y. et al. Competition-level code generation with alphacode. Science 378, 1092-1097 (2022).
4. Yang, J. et al. SWE-agent: agent-computer interfaces enable automated software engineering. In Adv. Neural Inf. Process. Syst. 37 (NeurIPS, 2024).
5. Khattab, O. et al. DSPy: Compiling declarative language model calls into state-of-the-art pipelines. In The Twelfth International Conference on Learning Representations (2024).
6. Zaharia, M. et al. The shift from models to compound AI systems. BAIR https://bair.berkeley. edu/blog/2024/02/18/compound-ai-systems/ (2024).
7. Zhou, Y. et al. Large language models are human-level prompt engineers. In The Eleventh International Conference on Learning Representations (2023).
8. Krizhevsky, A., Sutskever, I. &amp; Hinton, G. E. Imagenet classification with deep convolutional neural networks. In Adv. Neural Inf. Process. Syst. 25 (NeurIPS, 2012).
9. Jumper, J. et al. Highly accurate protein structure prediction with AlphaFold. Nature 596, 583-589 (2021).
10. Fawzi, A. et al. Discovering faster matrix multiplication algorithms with reinforcement learning. Nature 610, 47-53 (2022).
11. Mankowitz, D. J. et al. Faster sorting algorithms discovered using deep reinforcement learning. Nature 618, 257-263 (2023).
12. Merchant, A. et al. Scaling deep learning for materials discovery. Nature 624, 80-85 (2023).
13. Goodfellow, I., Bengio, Y. &amp; Courville, A. Deep Learning (MIT Press, 2016).
14. Rumelhart, D. E., Hinton, G. E. &amp; Williams, R. J. Learning representations by backpropagating errors. Nature 323, 533-536 (1986).
15. Pryzant, R. et al. Automatic prompt optimization with "gradient descent" and beam search. In Proc. 2023 Conference on Empirical Methods in Natural Language Processing (eds Bouamor, H. et al.) 7957-7968 (Association for Computational Linguistics, 2023).
16. Zheng, L. et al. Judging LLM-as-a-judge with MH-bench and chatbot arena. Adv. Neural Inf. Process. Syst. 36, 46595-46623 (2023).
17. Li, X. et al. AlpacaEval: an automatic evaluator of instruction-following models. GitHub https://github.com/tatsu-lab/alpaca\_eval (2023).
18. Bai, Y. et al. Training a helpful and harmless assistant with reinforcement learning from human feedback. Preprint at https://arxiv.org/abs/2204.05862 (2022).
19. Madaan, A. et al. Self-refine: iterative refinement with self-feedback. In Adv. Neural Inf. Process. Syst. 36 (NeurIPS, 2023).
20. Stiennon, N. et al. Learning to summarize with human feedback. In Adv. Neural Inf. Process. Syst. 33, 3008-3021 (2020).
21. Yuan, W. et al. Self-rewarding language models. In Forty-first International Conference on Machine Learning (2024).
22. Dubois, Y. et al. AlpacaFarm: a simulation framework for methods that learn from human feedback. In Adv. Neural Inf. Process. Syst. 36 (NeurIPS, 2023).
23. Shinn, N., Cassano, F., Gopinath, A., Narasimhan, K. &amp; Yao, S. Reflexion: language agents with verbal reinforcement learning. Adv. Neural Inf. Process. Syst. 36, 8634-8652 (2023).
24. Rein, D. et al. GPQA: a graduate-level Google-proof Q&amp;A benchmark. In First Conference on Language Modeling (2024).
25. Hendrycks, D. et al. Measuring massive multitask language understanding. In The Ninth International Conference on Learning Representations (2021).
26. Lu, P. et al. MathVista: evaluating mathematical reasoning of foundation models in visual contexts. In The Twelfth International Conference on Learning Representations (2024).
27. Lu, P. et al. Learn to explain: multimodal reasoning via thought chains for science question answering. Adv. Neural Inf. Process. Syst. 35, 2507-2521 (2022).
28. Liu, P. et al. Pre-train, prompt, and predict: a systematic survey of prompting methods in natural language processing. ACM Comput. Surv. 55, 1-35 (2023).
29. Suzgun, M. et al. Challenging BIG-bench tasks and whether chain-of-thought can solve them. In Findings of the Association for Computational Linguistics: ACL 2023 13003-13051 (Association for Computational Linguistics, 2023).
30. Cobbe, K. et al. Training verifiers to solve math word problems. Preprint at https://arxiv. org/abs/2110.14168 (2021).
31. Yang, C. et al. Large language models as optimizers. In The Twelfth International Conference on Learning Representations (2024).
32. Dubey, A. et al. The Llama 3 herd of models. Preprint at https://arxiv.org/abs/2407.21783 (2024).
33. Yang, A. et al. Qwen2 technical report. Preprint at https://arxiv.org/abs/2407.10671 (2024).
34. Khan, F. M., Gibbons, J. P. &amp; Sperduto, P. W. Khan's Treatment Planning in Radiation Oncology (Lippincott Williams &amp; Wilkins (Wolters Kluwer), 2016).
35. Hussein, M., Heijmen, B. J. M., Verellen, D. &amp; Nisbet, A. Automation in intensity modulated radiotherapy treatment planning-a review of recent innovations. Br. J. Radiol. 91, 20180270 (2018).
36. Kisling, K. et al. Radiation planning assistant-a streamlined, fully automated radiotherapy treatment planning system. J. Vis. Exp. 134, e57411 (2018).
37. Huang, C., Nomura, Y., Yang, Y. &amp; Xing, L. Meta-optimization for fully automated radiation therapy treatment planning. Phys. Med. Biol. 67, 055011 (2022).
38. Yang, Y. &amp; Xing, L. Clinical knowledge-based inverse treatment planning. Phys. Med. Biol. 49, 5101 (2004).
39. Liu, S. et al. Automated radiotherapy treatment planning guided by gpt-4vision. Preprint at https://arxiv.org/abs/2406.15609 (2024).
40. Lu, P. et al. Chameleon: plug-and-play compositional reasoning with large language models. Adv. Neural Inf. Process. Syst. 36, 43447-43478 (2023).
41. Yan, B., Zhang, J., Yuan, Z., Shan, S. &amp; Chen, X. Evaluating the quality of hallucination benchmarks for large vision-language models. Preprint at https://arxiv.org/abs/2406.17115 (2024).
42. Wei, J. et al. Chain-of-thought prompting elicits reasoning in large language models. Adv. Neural Inf. Process. Syst. 35, 24824-24837 (2022).

Publisher's note Springer Nature remains neutral with regard to jurisdictional claims in published maps and institutional affiliations.

Springer Nature or its licensor (e.g. a society or other partner) holds exclusive rights to this article under a publishing agreement with the author(s) or other rightsholder(s); author self-archiving of the accepted manuscript version of this article is solely governed by the terms of such publishing agreement and applicable law.

- © The Author(s), under exclusive licence to Springer Nature Limited 2025

## Methods

Throughout the paper, unless otherwise specified, we use the gpt-4o-2024-05-13 version of gpt-4o and the gpt-3.5-turbo-0125 version of gpt-3.5.

## The general case for backpropagation

The abstraction readily applies to arbitrarily complex systems. Define a computation graph by

<!-- formula-not-decoded -->

where v is a variable in the graph, V is the set of all variables in the graph, and SuccessorsOf returns the successors and PredecessorsOf returns the predecessors of a variable. Generally speaking, the value of v can be unstructured data, such as natural language text or images. For most of the results and exposition in this paper, v is natural language text.

Furthermore, let us have fv as the transformation that consumes a set of variables and produces the variable v. For instance, we can use an LLM or numerical simulator as a transformation. As different functions will have different ways to compute gradients and collect feedback for, we will generally use ∇f to denote the gradient function for a function f. For the sake of exposition, we will omit the subscript when the function is obvious.

The gradients are computed by

<!-- formula-not-decoded -->

where we collect the set of gradients from all successor variables w of v. Intuitively, we get feedback from every context in which a variable v was used, and aggregate them.

The equation above recursively computes the gradients of the downstream objective with respect to the desired variables v in the graph. The ∇f function takes as input the gradients of L with respect to the successors of a given variable v, the value of the variable v and the successors themselves. It is noted that the final gradient variable comprises a set of contexts and feedback for any place a variable was used in.

Finally, to update any desired variable v in the graph, we can use an optimizer step:

<!-- formula-not-decoded -->

which updates the value of v based on its current value and the gradients. For a computation graph where there are n edges, each iteration of optimization performs at most n additional language model calls to compute gradients (one call using the gradient operator for each edge in the computation graph). For the concrete implementations of operations in TextGrad, see Supplementary Note 1. For the complete algorithm, see Algorithm 1 in Supplementary Note 1.

## Code optimization

Reflexion is the state-of-the-art method on the LeetCode Hard dataset. Their approach prompts an LLM to self-reflect on code snippets and the errors that were generated at test time using candidate unit tests. Given the self-reflection, the LLM is prompted again to provide an updated piece of code, conditioned on the self-reflection and the errors. We ran Reflexion on LeetCode Hard using gpt-4o using one in-context demonstration to guide the behaviour (one shot). In addition to Reflexion, we also run a zero-shot baseline using gpt-4o mimicking the same zero-shot baseline described in the Reflexion paper. In contrast to Reflexion, TextGrad runs in a zero-shot setting, without any demonstrations. In Extended Data Fig. 3a, we show the code refinement objective used in this paper.

We ran the experiment five times with five different seeds and we averaged the results. At each iteration of optimization, TextGrad makes one call to gpt-4o to evaluate the test-time loss, one call to collect textual gradients and one call to update the code snippet. The number of coding problems in LeetCode Hard is 39.

## Solution optimization

The objective function for the refinement can be found in Extended Data Fig. 4b. Similarly, we report the objective used for multimodal solution optimization in Supplementary Note 4.

GPQA is a recent benchmark where challenging multiple-choice questions in physics, biology and chemistry are created and labelled by domain experts who have or are pursuing PhD degrees. In this benchmark, experts and skilled non-experts are reported to achieve 81% and 22% accuracy, respectively, demonstrating the difficulty of the questions. We also use two challenging subsets (machine learning and college physics) of the MMLU question-answering benchmark that is used to track the progress of language modelling and whether LLMs reached human-level performance. Here the expert human accuracy on average is around 90%.

We further test solution optimization in multimodal problems, specifically the MathVista and ScienceQA tasks. MathVista is a comprehensive benchmark for evaluating models' capabilities in mathematical reasoning with visual contexts. It contains seven mathematical reasoning categories including arithmetic reasoning, algebraic reasoning and statistical reasoning, and requires fine-grained visual understanding across natural images, diagrams, charts and graphs. We utilize the testmini split with 1,000 examples for evaluation. ScienceQA is a multimodal benchmark of multiple-choice questions in scientific domains. It covers three subjects: nature science, social science and language science, featuring a diverse set of domains and topics. We conduct experiments on ScienceQA-IMG, the test split in multimodal setting, which consists of 2,017 examples. We provide further details on format and prompts in Supplementary Note 4.

We report three baselines. First, the reported results in the gpt-4o release document states 53.6% accuracy. However, their official implementation uses a temperature of 0.5 for generations, thus we also test gpt-4o with temperature 0 and chain of thought (CoT) prompting provided in the official implementation. For TextGrad, we perform three iterations of test-time updates (that is, update the solution three times) and perform majority voting across all solutions to get the final answer. We use string-based metrics to compute the final accuracy of each answer. Finally, we report Reflexion as another baseline, where we also run their algorithm with three iterations (that is, update the answer three times) and perform majority voting across all solutions to get the final answer.

## Prompt optimization

Here, we use TextGrad in a minibatch stochastic gradient descent setting 43 . In particular, at each iteration, we use a few training examples for training. A pseudocode and short implementation can be found in the snippet above. Full details of prompt optimization can be found in Supplementary Note 5.

Furthermore, we can decompose a prompt into an instruction and in-context demonstrations, and apply the same strategy to optimize them jointly using textual gradients. For instance, we can initialize the in-context demonstrations using input-output samples from the training dataset, then optimize them using TGD.

We explore improving the performance of gpt-3.5-turbo using gpt-4o to provide feedback during backpropagation. In particular, although the forward model that performs the reasoning is gpt-3.5-turbo, we use gpt-4o to provide the feedback and improve the prompt. We use a batch size of 3 with 12 iterations, that is, the model sees 36 training examples in total, sampled randomly with replacement. After each iteration, we run a validation loop with the validation set of the datasets,

## Article

and if the performance is better than the previous iteration we update the prompt, which consists of a separate instruction variable, and the in-context demonstrations.

We explore prompt optimization in multiple datasets, including the two standard reasoning tasks (object counting and word sorting) from Big Bench Hard (randomly split into 51/100/99 train/validation/ test samples) and GSM8k grade-school maths problem solving (using train/validation/test splits from DSPy). For GSM8k and object counting, we use a string-based exact match metric to quantify accuracy (that is, whether the final number provided in the response is the same as the ground-truth answer). For word sorting, we use an LLM to compare the response and the ground-truth answer. We give more details about the tasks, prompts and example queries in Supplementary Note 5.1.

We have three main baselines:

1. Zero-shot CoT. We initialize all prompts as a zero-shot CoT prompt, where a model is instructed to 'Think step by step' to explain its reasoning before giving its answer. This strategy is well known to be a strong baseline for prompting.
2. DSPy is a state-of-the-art language model programming and prompt optimization framework; thus we use it as the reference baseline. We instantiate DSPy's BootstrappedFewShotRandomSearch optimizer with ten candidate programs and eight few-shot examples. This optimizer identifies demonstrations to include in the prompt as few-shot examples. This selection is done through generating traces of LLM inputs and outputs that individually pass the metric (in this case, accuracy) and includes CoT reasoning. DSPy then app­ lies random search over subsets of up to size eight shots with these demonstrations.
3. OPRO is one of the first methods to use LLMs as optimizers, where given a set of prompts and their performance, an optimizer LLM generates new candidate prompts. We use all of the hyperparameters as reported in the paper. At each iteration OPRO generates 8 candidate prompts by prompting the optimizer LLM with 20 best-performing prompts along with their performance, and 3 exemplars from the dataset. We perform eight iterations of this procedure.

## Treatment planning

The dataset used in this study comprised imaging and treatment plans for five patients with prostate cancer who underwent intensity-modulated radiation therapy. The available data for each patient includes computed tomography scans, delineated anatomical structures and clinically approved treatment plans obtained via Eclipse.

As we mentioned in the results, TextGrad is used to optimize the hyperparameters (for example, importance weights for PTV and OARs) of the inner-loop numerical optimizer that generates the treatment plan. This optimization is done using a variation of TextGrad, that is, 'projected gradient descent with momentum updates'. In particular, three prostate cancer treatment plans optimized by clinicians, along with their corresponding hyperparameters, are provided as in-context examples. These examples guide the updates of the hyperparameters. Moreover, the historical hyperparameters and the textual gradients from past iterations, as an analogy to momentum, are also included in the prompts for updating the hyperparameters. This additional context helps refine the optimization process. The optimization will be stopped if the loss suggests all protocols meet, otherwise, it will be stopped if the maximum number of iterations (we set it to ten) is reached.

The importance weights are all initialized at 100 for different organs. The dose objectives are set to 70.20 for PTV, 0.00 for bladder and rectum, and 30.00 for femoral heads and body, and fixed during optimization.

To evaluate a treatment plan, we adopt several frequently used dose metrics, as a plan cannot be evaluated using a single metric. We consider the mean dose delivered to the target/organ volume, as well as Dq, which denotes the minimum dose received by q% of the target/organ volume.

Throughout our experiments, we compare the plans generated by TextGrad with multiple baselines. Our first baseline uses plans generated by certified physicists from our institution with multiple years of experience in developing treatment plans across various cancer types. Our second baseline uses plans produced using Bayesian optimization, which optimizes hyperparameters θ (for example, importance weights for PTV and OARs) by employing a weighted sum of multiple plan evaluation metrics 44 as the objective function. Specifically, the objective is defined as

<!-- formula-not-decoded -->

where mi represents the plan evaluation metric derived from the generated plan with hyperparameter θ, and mi denotes the corresponding clinical goal. The term pi indicates the rank of importance for each plan evaluation metric.

For PTV, we use the mean dose and D95 as evaluation metrics with m =70.20, assigning them an importance rank p of 1. For the OARs, that is, bladder and rectum, we consider the mean dose, D5, and D50 with m =0.00, and an importance rank p of 2.

We implement Bayesian optimization using Optuna 45 . The number of optimization trials in Optuna is set to 50. For all hyperparameters, we configure the suggest\_float range to [100, 400], while leaving the remaining parameters as default.

In Extended Data Fig. 6, we show additional results on comparing TextGrad-optimized plan with clinicians optimized plans. Although Bayesian optimization can optimize the plan quality metric (PQM) score function, it produces significantly worse results, particularly in terms of dose conformity, and converges slowly, typically requiring an average of 21.3 iterations. In contrast, our method, TextGrad, generates high-quality plans in just ten iterations. The results illustrate the effectiveness of TextGrad in guiding iterative improvements in optimization but do not constitute a direct evaluation of clinical utility.

## Optimizing compound AI systems

Optimizing the Chameleon agentic system. The original Chameleon system is described in Algorithm 2 (Supplementary Note 9). It consists of a planner P and a module inventory of tools M. Given an input query q, the planner generates a plan p q ← ( ; ) P M that specifies a sequence of modules to execute. Executing the plan starts from an empty cache c =∅ 0 . At each step t, the chosen module M t is run as y t ← M t (q; c t-1 ), after which the cache is updated: c t ← update\_cache(c t-1 , y t ). After all T steps, the final response is r = y T .

We augment this procedure, as shown in Algorithm 3 (Supplementary Note 9), by introducing textual gradient-based optimization. After an initial forward pass, we iteratively refine each module's output. We quantify the final response quality via a loss function L, compute textual gradients using TextGrad and propagate these gradients back to earlier steps in the chain, adjusting their outputs accordingly. This iterative process gradually improves the intermediate reasoning steps and, consequently, the final answer. We evaluate the original and TextGrad-optimized systems on ScienceQA-IMG and experiment with two and three optimization iterations to study the impact of iteration count. Details are available at Supplementary Note 9.

Improving spatial reasoning ability by jointly optimizing prompts and solutions. We apply TextGrad to improve spatial reasoning ability on the visual question-answering task. In visual question answering, instructional prompts are used to guide the model in answering the questions following. We further compute the objective in TextGrad by prompting a language model and treating both the prompts embedded in the loss function and the instructional prompts as variables to be optimized. The generated solutions to the questions are optimized together.

We split the HQH dataset into 70/30/100 (train/validation/test) splits, out of the 200 samples in the relation question type. The complete optimization process is as follows. We first warm up the optimization process where the instructions to the language model that specify the task, and the instructions for the loss function used to evaluate generated answers are optimized in an alternating fashion with a batch size set to ten (in total seven iterations). We use the prompts that achieve the best validation accuracy for test-time optimization. At test time, each solution is optimized for three iterations (that is, update the solution three times). Majority voting across all solutions is performed to get the final answer.

## Molecule optimization

As a proof of concept, we also explore TextGrad's applications to molecular optimization, and demonstrate how our framework can be used to interface with domain-specific tools in scientific tasks (Supplementary Note 8).

We optimize chemical molecules encoded as text (simplified molecular input line entry system (SMILES) strings) with respect to one or several molecular scoring functions. We restrict our scoring functions to in silico methods, namely, Autodock Vina, which measures the binding affinity of a molecule against a target protein, and quantitative estimate of drug-likeness (QED), which measures how 'druglike' a molecule is. We initialize a molecule as a small starting fragment, and perform several iterations of optimization using TGD. At each iteration, the loss is constructed by concatenating each score into a single 'textual' loss.

We evaluate our methods using two baselines: (1) molecular characteristics of approved drugs against a matched set of protein targets (Extended Data Fig. 1); and (2) oracle efficiency compared with state-of-the-art molecular optimization algorithms (Extended Data Fig. 2). We observe that TextGrad produces molecules with a similar distribution to its clinical counterparts across both optimized and non-optimized molecular properties, but with low structural similarity to approved drugs or existing compounds. Compared with state-of-the-art molecular optimization algorithms, TextGrad consistently produces higher-performing molecules while using fewer evaluations on a diverse set of protein targets. Although promising, we caution that the practical value of these molecules is limited and should be taken as a proof of concept only. Our evaluations are limited by their reliance on in silico property predictors, which are not accurate substitutes for thorough experimental and clinical evaluation.

## Data availability

We used publicly available data to evaluate TextGrad. Details on how to access the data is available at https://github.com/zou-group/textgrad.

## Code availability

The TextGrad code and experiments are available at https://github. com/zou-group/textgrad and https://doi.org/10.5281/zenodo.14497017 (ref. 46).

43. Bottou, L. Large-scale machine learning with stochastic gradient descent. In Proc. COMPSTAT'2010 (eds Lechevallier, Y. &amp; Saporta, G.) 177-186 (Physica-Verlag, 2010).
44. Wang, Q. et al. High-dimensional automated radiation therapy treatment planning via bayesian optimization. Med. Phys. 50, 3773-3787 (2023).
45. Akiba, T., Sano, S., Yanase, T., Ohta, T. &amp; Koyama, M. Optuna: a next-generation hyperparameter optimization framework. In Proc. 25th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (2019).
46. Bianchi, F. et al. zou-group/textgrad: v0.1.6. Zenodo https://doi.org/10.5281/zenodo.14497017 (2024).

Acknowledgements We thank D. Yilmaz, F. Dinc, B. Ergun, Y. Sun, I. Covert, K. Swanson, O. Faruk Akgun, Y. Efe, O. Khattab, K. Y. Wu, E. Wu, K. Vodrahalli, O. Pastor Serrano, P. J. Chia, J. Tagliabue, N. Thakkar, E. Simon, S. Eyuboglu, I. Gao, L. Chen and members of the Zou group and the Guestrin group for their support and comments on this work. This work was supported by funding from the Chan-Zuckerberg Biohub. C.G. was supported by funding from the Chan-Zuckerberg Biohub, Stanford HAI, AFOSR Grant FA9550-21-1-0397, gifts from Google and IBM.

Author contributions M.Y. and J.Z. conceptualized the research and led the overall project. M.Y. developed the primary codebase and led prompt optimization and solution optimization. M.Y., F.B. and J.B. designed the abstractions. F.B. led code optimization. J.B. led molecule optimization. S.L. led treatment planning optimization and compound system optimization. P.L. led solution optimization in multimodal settings and compound system optimization. Z.H. and C.G. advised the project. J.Z. supervised the project. All authors contributed to the preparation of the paper and approved the final version.

Competing interests The authors declare no competing interests.

## Additional information

Supplementary information The online version contains supplementary material available at https://doi.org/10.1038/s41586-025-08661-4.

Correspondence and requests for materials should be addressed to Mert Yuksekgonul or James Zou.

Peer review information Nature thanks Kai-Wei Chang and the other, anonymous, reviewer(s) for their contribution to the peer review of this work. Peer reviewer reports are available. Reprints and permissions information is available at http://www.nature.com/reprints.

## Article

<!-- image -->

Extended Data Fig. 1 | See next page for caption.

Extended Data Fig. 1 | Molecule optimization via text. TextGrad optimizes a starting benzene fragment to improve its druglikeness (higher QED) and binding affinity (lower vina score) to the protein receptor PPARA. The textual gradients for the first three iterations are shown in (a), and the performance of all ten iterations compared to clinically approved molecules targeting PPARA in (c). The molecule at the final iteration has low structural similarity with its most similar clinically approved counterpart, and better QED and Vina scores (d) with a highly plausible pose geometry shown in (e). Across 29 targets and three initial fragments, TextGrad successfully designs molecules with similar vina scores and greater QED scores than clinically approved molecules (b).

## Article

Extended Data Fig. 2 | Comparing TextGrad to to other molecule

<!-- image -->

optimization methods. (a) Scaled mean top-5 AUCs for each method across all 58 protein targets. (b) Sample trajectories. For each algorithm, we selected the best performing trajectory to visualize, as measured by scaled Top-5 AUC, for the protein target listed, with the shaded error bars representing the standard error across the three repetitions (seeds/initial molecules). The blue star indicates the iteration at which TextGrad's early stopping condition was triggered.

## a

## b

## Code Refinement Objective

LLM ("You are an intelligent assistant used as an evaluator, and part of an optimization system. You will analyze a code implementation for a coding problem and unit test results. The code will be tested with harder tests, so do not just check if the code passes the provided tests. Think about the correctness of the code and its performance in harder test cases. Give very concise feedback. Investigate the code problem and the provided implementation. For each failed unit test case, start analyzing it by saying "The code did not pass this test because...". Explain why the current implementation is not getting the expected output. Do not provide a revised implementation. Carefully suggest why there are issues with the code and provide feedback."

{Test-time Instruction}

**The coding problem:**

## {Problem}

**Code generated that must be evaluated for correctness and runtime performance**

## {Code}

**The test results:**

{Local test Results})

| Task          | Method                                    | Completion Rate (%)   |
|---------------|-------------------------------------------|-----------------------|
| LeetCode Hard | Zero-shot                                 | 26                    |
| LeetCode Hard | Reflexion (1 demonstration, 5 iterations) | 31 ± 1.2              |
| LeetCode Hard | (0 demonstrations, 5 iterations) TextGrad | 36 ± 1.8              |

Extended Data Fig. 3 | Code optimization details. (a) We show the test-time objective we use for code optimization. (b) We report the results for LeetCode Hard using gpt-4o. We report the standard deviation over five random seeds in brackets.

## a

c

|                                        | Dataset                               | Method                                                             | Accuracy (%)                       |
|----------------------------------------|---------------------------------------|--------------------------------------------------------------------|------------------------------------|
| Natural Language Problem Solving Tasks | Google-proof QA MMLU-Machine Learning | CoT Reflexion GPT-4o best reported TextGrad CoT Reflexion TextGrad | 51.0 51.0 53.6 55.0 85.7 85.7 88.4 |
|                                        | MMLU-College Physics                  | CoT Reflexion TextGrad                                             | 91.2 94.1 95.1                     |
| Multimodal Solving Tasks               | MathVista                             | CoT Reflexion TextGrad                                             | 63.8 64.0 66.1                     |
| Problem                                | ScienceQA-IMG                         | CoT Reflexion TextGrad                                             | 91.6 90.2 92.4                     |

<!-- image -->

## b

## Solution Refinement Objective

LLM ("Below is a multi-choice question and a prediction. You are a critical and creative scientist. Your job is to investigate the prediction. Critically go through reasoning steps, and see if there is a reason why the prediction could be incorrect.

Question: {Question} Use the Janusian Process, think about whether alternative answers could be true.

Answer by the language model: { Solution } ")

## Example: Multimodal solution optimization for visual mathematical reasoning

<!-- image -->

Question:What is the sum of the accuracies of the algorithms fat and acre?

## Solution at initialization:

To find the sum of the accuracies of the algorithms "fat" and "acre," we need to accurately interpret the values from the bar chart.

From the chart: The accuracy of "fat" is represented by the fourth bar from the left, which shows an accuracy of 6. The accuracy of "acre" is represented by the last bar on the right, which shows an accuracy of 4.

Now, we add these two values together: 6 + 4 = 10. The correct sum of the accuracies of the algorithms "fat" . and "acre" is 10.

## Output of the loss function based on multimodal context:

The existing answer provides a clear and logical approach to solving the problem by interpreting the bar chart and summing the accuracies of the specified algorithms. However, there is an error in the interpretation of the values from the chart .

Upon reviewing the bar chart: The accuracy of "fat" is represented by the fifth bar from the left, which shows an accuracy of 5. The accuracy of "acre" is represented by the last bar on the right, which shows an accuracy of 4.

## Solution after optimization:

To find the sum of the accuracies of the algorithms "fat" and "acre," we need to accurately interpret the values from the bar chart.

From the chart: The accuracy of "fat" is represented by the fifth bar from the left, which shows an accuracy of 5. The accuracy of "acre" is represented by the last bar on the right, which shows an accuracy of 4.

Now, we add these two values together: 5 + 4 = 9. The correct sum of the accuracies of the algorithms "fat" and "acre" is 9.

Extended Data Fig. 4 | Solution optimization details. (a) Solution optimization for zero-shot question answering with gpt-4o. TextGrad outperforms the baselines consistently across different tasks. (b) We show the test-time objective objective we use for solution optimization. (c) We show an example where the mistake in the solution is identified in the test-time objective, and later the updated solution fixes the mistake.

| Dataset a       | Method        | Accuracy (%)   |
|-----------------|---------------|----------------|
| Object Counting | CoT OPRO DSPy | 77.8 82.8      |
| Object Counting | TextGrad      | 84.9 91.9      |
| Word Sorting    | CoT           | 76.7           |
| Word Sorting    | OPRO          | 77.8           |
| Word Sorting    | DSPy          | 79.8           |
| Word Sorting    | TextGrad      | 80.8           |
| GSM8k           | CoT           | 76.7           |
| GSM8k           | OPRO          | 77.8           |
| GSM8k           | DSPy          | 79.8           |
| GSM8k           | TextGrad      | 80.8           |

c

b

## Example: TextGrad optimized prompt for gpt-3.5-turbo-0125

Prompt at initialization (GSM8k Accuracy = 72.9%): You will answer a mathematical reasoning question. Think step by step. The last line of your response should be of the following format: ' Answer: $VALUE' where VALUE is a numerical value.

## Prompt after optimization(GSM8k Accuracy = 81.1%):

You will answer a mathematical reasoning question. Restate the problem in your own words to ensure understanding. Break down the problem into smaller steps explaining each calculation in detail. Verify each ste and re-check your calculations for accuracy. Use prope mathematical notation andmaintain consistency with the context of the question. Always conclude with the final answer in the following format: ' Answer: $VALUE' where VALUE is a numerical value.

## Example: TextGrad-optimized in-context demonstrations for gpt-3.5-turbo-0125

## Demonstrations at initialization:

Input: I have 1 banana, 4 strawberries, 1 apple, 2 peaches, 1 plum, 1 blackberry, and 2 raspberries. How many fruits do I have? Answer: 12

Input: I have 1 blackberry, 1 peach, 1 nectarine, 1 plum, 1 raspberry, 1 orange, 1 strawberry, 1 banana, 2 apples, and 4 grapes. How many fruits do I have? Answer: 14

Input: I have 1 apple, 3 bananas, 1 strawberry, 1 peach, 3 oranges, 1 plum, 1 raspberry, 2 grapes, 1 nectarine, and 1 blackberry. How many fruits do I have? Answer: 15

## Demonstrations after optimization:

Input: I have a banana, four strawberries, an apple, two peaches, a plum, a blackberry, and two raspberries. How many fruits do I have? Ground Truth Response: To find the total number of fruits, we add up the quantities of each type of fruit mentioned in the input. Banana: 1, Strawberries: 4, Apple: 1, Peaches: 2, Plum: 1, Blackberry: 1, Raspberries: 2. Adding these quantities together, we get 1 + 4 + 1 + 2 + 1 + 1 + 2 = 12. Answer: 12

Input: I have a blackberry, a peach, a nectarine, a plum, a raspberry, an orange, a strawberry, a banana, two apples, and four grapes. How many fruits do I have? Ground Truth Response: To find the total number of fruits, we add up the quantities of each type of fruit mentioned in the input. Blackberry: 1, Peach: 1, Nectarine: 1, Plum: 1, Raspberry: 1, Orange: 1, Strawberry: 1, Banana: 1, Apples: 2, Grapes: 4. Adding these quantities together, we get 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 2 + 4 = 14. Answer: 14

Input: I have an apple, three bananas, a strawberry, a peach, three oranges, a plum, a raspberry, two grapes, a nectarine, and a blackberry. How many fruits do I have? Ground Truth Response: To find the total number of fruits, we add up the quantities of each type of fruit mentioned in the input. Apple: 1, Bananas: 3, Strawberry: 1, Peach: 1, Oranges: 3, Plum: 1, Raspberry: 1, Grapes: 2, Nectarine: 1, Blackberry: 1. Adding these quantities together, we get 1 + 3 + 1 + 1 + 3 + 1 + 1 + 2 + 1 + 1 = 15. Answer: 15

Extended Data Fig. 5 | Prompt optimization details. (a) With TextGrad, we optimize a system prompt for gpt-3.5-turbo using gpt-4o as the gradient engine that provides the feedback during backpropagation. Supplementary Table 1

includes ablations with instruction-only and demonstration-only optimization with TextGrad. (b) We show an example of an optimized instruction for GSM8k. (c) We show an example of optimized in-context demonstrations for GSM8k.

## Article

## a

| Target   | Method                | Mean dose [Gy]   | Min dose [Gy]   | Max dose [Gy]   | D [Gy] 95    |
|----------|-----------------------|------------------|-----------------|-----------------|--------------|
| PTV      | Clinical Goal         | 70.20            | ≈ 70.20         | ≈ 70.20         | 70.20        |
| PTV      | Bayesian Optimization | +4.84 (1.65)     | -9.33 (2.38)    | +17.42 (2.88)   | +0.00 (0.07) |
| PTV      | Radiation Oncologist  | +1.97 (0.36)     | -8.88 (2.31)    | +4.66 (0.82)    | -0.10 (0.15) |
| PTV      | TextGrad              | +0.51 (0.09)     | -8.48 (2.38)    | +3.63 (0.87)    | +0.00 (0.00) |

## b

| Target   | Method                | Mean dose [Gy]   | D5            | D50           |
|----------|-----------------------|------------------|---------------|---------------|
| Rectum   | Bayesian Optimization | 24.47 (9.30)     | 62.01 (10.79) | 18.74 (12.12) |
|          | Radiation Oncologist  | 23.88 (6.45)     | 64.26 (10.00) | 20.04 (5.50)  |
|          | TextGrad              | 17.18 (4.20)     | 58.82 (18.81) | 9.54 (0.70)   |
| Bladder  | Bayesian Optimization | 26.15 (5.64)     | 63.57 (8.82)  | 22.19 (5.71)  |
|          | Radiation Oncologist  | 22.39 (5.55)     | 67.81 (6.44)  | 14.78 (8.42)  |
|          | TextGrad              | 20.92 (0.79)     | 65.96 (6.96)  | 14.11 (3.17)  |

Extended Data Fig. 6 | Treatment planning details. (a) We display the several dose metrics of the PTV target for all the clinical and TextGrad optimized plans, including the mean and minimum doses, as well as the D95. For all the metrics, we include the average deviations from the clinical goal across five plans and the standard deviation in brackets. Values in bold represent the best for each PTV target. (b) We show mean dose to capture OAR sparing. Lower values demonstrate better OAR sparing which is desirable, as this number indicates organs at risk, which should not get more than dosage than what is listed in the clinical guidelines. For all the metrics, we include the average mean dose across five plans and the standard deviation in brackets.

## Supplementary information

## Optimizing generative AI by backpropagating language model feedback

In the format provided by the authors and unedited

Nature | www.nature.com/nature

## Supplementary Note 1 TextGrad details

## Supplementary Note 1.1 Variables

Variables are the nodes in the computation graph. Below are the most important attributes of Variables:

1. Value is the unstructured data that the variable contains. Throughout this manuscript, all values are text data.
2. Role description is an informative string that describes the role of the variable in the computation graph. We use these roles to let the user inject knowledge into the graph and guide the optimization behavior. More information is described below.
3. Gradients are the natural language feedback provided by the LLMs during the backward pass. These describe the changes to make the variable so that the downstream loss can be improved. For an example backward operation that populates gradients, please read Supplementary Note 1.3.
4. Predecessors are the set of variables that are used to generate a given variable. For instance, if we are giving an instruction to an LLM and getting a response, the instruction would be the predecessor of the response. During the backward pass, the gradients on the successor are passed to its predecessors, to provide guidance around how to improve the downstream objective.
5. Requires grad indicates whether or not the gradients will be populated during the backward pass, analogous to PyTorch. For instance, if the user does not wish to compute gradients for a question, then simply write Variable(value=question, requires\_grad=False, ...) to indicate this.

Role description. In TextGrad, each variable has a role description. In particular, this is a string that describes the role of the variable in the computation graph, such as "system prompt to the language model" or "prediction by the language model" . While sometimes populated automatically, in general role descriptions are one of the primary ways to inject user knowledge into the optimization process.

Empirically, we find that role descriptions can significantly steer the optimization process. For instance, setting the role of a prediction to be "the final numerical answer to the language model" guides the Textual Gradient Descent optimizer, that prompts a language model to update the value of the variable using the feedback, to update the variable such that it is only a numerical value. In comparison, a role description such as "the reasoning for the solution and the final prediction" guides the optimizer to produce the reasoning along with the final prediction.

Here is an example usage:

```
1 import textgrad as tg 2 3 system_prompt = tg.Variable("You will be given a question and think step -by-step.", requires_grad=True , role_description="system prompt to the language model that will be reused across queries") 4 5 model = tg.BlackBoxLLM(system_prompt=system_prompt)
```

Code Snippet 1 An example usage of a role description.

## Supplementary Note 1.2 Backpropagation

The backpropagation algorithm in TextGrad mirrors existing autograd frameworks for deep learning. See Algorithm 1 for the pseudocode.

## Algorithm 1 Backpropagation in TextGrad

```
1: Input: Variables v ∈ V in a graph, loss variable L, backward engine (LLM) M that will provide textual gradients 2: # Initializing gradients 3: for each v ∈ V do 4: v.gradients = ∅ 5: end for 6: # Topological Sorting 7: Q⇐TopologicalSort(G) 8: # Backpropagation 9: for v in Q do 10: # Populate gradients in predecessors 11: for each u ∈ PredecessorsOf(v) do 12: # We omit subscript v in f. f is the function that generates v, and ∇f is the backward operation for that function. 13: # Semantically, it provides feedback to the variable u, given how v is produced, and the feedback we already collected for v. 14: u.gradients.add (∇f (u, v, ∂L ∂v )) 15: end for 16: end for
```

## Supplementary Note 1.3 Functions

TextGrad offers several operations where both the forward and backward computations are defined - as such, these operations are composable. The abstract textgrad.autograd.Function class has two methods: forward and backward, mirroring the PyTorch syntax. Each function has to define both of these methods. Below, we describe a couple of the most used operations in this paper.

LLMCall function. Currently, the most crucial operation in TextGrad is the call to language models.

Forward mode. The forward mode is simple: We make a call to an LLM, through an API or through the local machine. When a call is made, all the input variables are registered as the predecessors of the response from the LLM. For instance, if we ask a question to an LLM using an instruction and a question variable, the response variable's predecessors will be [instruction, question]. When doing the backward pass, the gradients on the response will be backpropagated to question and instruction.

Backward mode. To ensure the backward function runs smoothly and generally, we add the following glossary to the system prompt:

## Glossary for backward mode of the LLMCall function

### Glossary of tags that will be sent to you:

# - &lt;LM \_ SYSTEM \_ PROMPT&gt;: The system prompt for the language model.

# - &lt;LM \_ INPUT&gt;: The input to the language model.

# - &lt;LM \_ OUTPUT&gt;: The output of the language model.

# - &lt;OBJECTIVE \_ FUNCTION&gt;: The objective of the optimization task.

# - &lt;VARIABLE&gt;: Specifies the span of the variable.

# - &lt;ROLE&gt;: The role description of the variable.

Using these tags, the LLM is made aware of the objective, the role and the value of the variable to give feedback to, and the full conversation in the forward mode.

This glossary is provided in the system prompt to the backward engine LLM:

## System prompt for the backward mode of the LLMCall function

You are part of an optimization system that improves a given text (i.e. the variable). You are the gradient (feedback) engine. Your only responsibility is to give intelligent and creative feedback and constructive criticism to variables, given an objective specified in &lt;OBJECTIVE \_ FUNCTION&gt; and &lt;/OBJECTIVE \_ FUNCTION&gt; tags. The variables may be solutions to problems, prompts to language models, code, or any other text-based variable. Pay attention to the role description of the variable, and the context in which it is used. You should assume that the variable will be used in a similar context in the future. Only provide strategies, explanations, and methods to change in the variable. DO NOT propose a new version of the variable, that will be the job of the optimizer. Your only job is to send feedback and criticism (compute 'gradients'). For instance, feedback can be in the form of 'Since language models have the X failure mode... ' , 'Adding X can fix this error because... ' , 'Removing X can improve the objective function because... ' , 'Changing X to Y would fix the mistake ... ' , that gets at the downstream objective.

If a variable is already working well (e.g. the objective function is perfect, an evaluation shows the response is accurate), you should not give feedback. {GLOSSARY}

Most of this setup aims to ensure that the user does not have to modify the gradient computation. All of our experiments in the diverse set of applications are done with the same backward mode.

For instance, an example prompt for the gradient computation looks like the following:

## An example backward mode prompt for the LLMCall function

You will give feedback to a variable with the following role: &lt;ROLE&gt; system prompt to a language model &lt;/ROLE&gt;.

Here is a conversation with a language model (LM):

&lt;LM\_SYSTEM\_PROMPT&gt; You will answer a reasoning question. Think step by step. Always conclude the last line of your response should be of the following format: 'Answer: $VALUE' where VALUE is a numerical value. &lt;/LM\_SYSTEM\_PROMPT&gt;

&lt;LM\_INPUT&gt; I have a chicken, a frog, a mouse, a cat, two pigs, and two rabbits. How many animals do I have? &lt;/LM\_INPUT&gt;

&lt;LM\_OUTPUT&gt; To find the total number of animals, we simply add up the number of each type of animal: 1 chicken + 1 frog + 1 mouse + 1 cat + 2 pigs + 2 rabbits = 8 animals. Answer: 8 &lt;/LM\_OUTPUT&gt;

This conversation is part of a larger system. The &lt;LM\_OUTPUT&gt; was later used as response from the language model.

&lt;OBJECTIVE\_FUNCTION&gt; Your goal is to give feedback to the variable to address the following feedback on the &lt;LM\_OUTPUT&gt;. To improve the runtime of the string-based function that checks if the prediction is correct, consider the following feedback:

1. **Simplify the Response**: For example, instead of "To find the total number of animals, we simply add (...) + 2 pigs + 2 rabbits = 8 animals. Answer: 8", a more concise response like "Total animals: 8" would be more efficient.

. . .

By implementing these strategies, the response from the language model can be optimized to improve the runtime of the string-based function that checks if the prediction is correct. &lt;/OB-JECTIVE\_FUNCTION&gt;

We are interested in giving feedback to the system prompt to a language model. Specifically, give feedback to the following span of text:

&lt;VARIABLE&gt; You will answer a reasoning question. Think step by step. (...) following format: 'Answer: $VALUE' where VALUE is a numerical value. &lt;/VARIABLE&gt;

Given the above history, describe how the system prompt to a language model could be improved to improve the &lt;OBJECTIVE\_FUNCTION&gt;. Be very creative, critical, and intelligent.

## Addition operation. In numerical optimization, we have the following:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

In numerical derivatives, due to the linearity of addition, we have:

<!-- formula-not-decoded -->

In particular, the backward function for the addition operation passes the gradients on the output of the addition operation to its inputs:

<!-- formula-not-decoded -->

Similarly, in TextGrad, we have the tg.sum operation, which lets the gradients (feedback) on the output variable pass to the input variables:

<!-- formula-not-decoded -->

where we use \n to indicate concatenation.

Use case. One canonical use case for the addition operation is the batch optimization case. In particular, we implement minibatch gradient descent when performing prompt optimization (3).

## Supplementary Note 1.4 Textual gradient descent implementation

Similar to backward computations, we strive to preserve generality in the implementation of TGD. In particular, we use the same glossary of tags provided above to inject information to the optimization process.

The current system prompt to the optimizer call is the following:

## System prompt for the TextualGradientDescent optimizer.

You are part of an optimization system that improves text (i.e., variable). You will be asked to creatively and critically improve prompts, solutions to problems, code, or any other text-based variable. You will receive some feedback, and use the feedback to improve the variable. The feedback may be noisy, identify what is important and what is correct. Pay attention to the role description of the variable, and the context in which it is used. This is very important: You MUST give your response by sending the improved variable between &lt;IMPROVED \_ VARIABLE&gt; improved variable &lt;/IMPROVED \_ VARIABLE&gt; tags. The text you send between the tags will directly replace the variable.

{GLOSSARY}

Below is an example prompt to the optimizer:

<!-- image -->

## Supplementary Note 2 Optimizer extensions

## Supplementary Note 2.1 Batch optimization

In batch optimization, we use the tg.sum function described above. In particular, gradients propagating from multiple instances are concatenated together, thus the optimizer sees all of the feedback to a variable coming from multiple sources.

The syntax is as simple as the following:

```
1 losses = [loss_fn(answer , model(question)) for question , answer in batch] 2 total_loss = tg.sum(losses) 3 total_loss.backward()
```

Code Snippet 2 An example use for batch optimization for question answering.

## Supplementary Note 2.2 Constrained optimization with natural language constraints

In TextGrad it is possible use constraints when optimizing variables. These constraints are all defined as natural language descriptions. For example, one can prompt optimizer to update the variable but to conclude its response with an answer during the update:

&lt;CONSTRAINTS&gt; "The last line of your response should be of the following format: 'Answer: $LETTER' where LETTER is one of ABCD."

```
Example constrained optimization prompt You must follow the following constraints: </CONSTRAINTS>
```

In general, the constraint post-fix is appended to the optimizer's prompt, where the constraints are written within the &lt;CONSTRAINTS&gt; {constraint text} &lt;/CONSTRAINTS&gt; tags.

In code, the user can simply pass in the constraints to the TGD optimizer:

```
1 constraints = ["The last line of your response should be of the following format: 'Answer: \$LETTER' where LETTER is one of ABCD."] 2 optimizer = TextualGradientDescent(parameters=[solution], constraints= constraints )
```

Code Snippet 3 An example use for constraints when updating the solution to a problem.

## Supplementary Note 2.3 Momentum

TextGrad supports the use of Momentum in the Textual Gradient Descent. In standard SGD momentum uses a linear combination of past gradients and the most recent one to define a new gradient to update a variable. Similarly, TextGrad keeps track of past iterations of the variable. This postfix is appended to the prompt for the optimizer.

```
1 optimizer = TextualGradientDescent(parameters=[solution], momentum_window=3)
```

Code Snippet 4 How to enable momentum using 3 previous steps in the

TextualGradientDescent optimizer.

## Momentum prompt

```
Here are the past iterations of this variable: <PAST _ ITERATIONS> {past _ values} </PAST _ ITERATIONS>
```

## Supplementary Note 2.4 In-context examples

LLMs have shown an impressive ability to learn in-context from a few examples [1]. In-context examples can be utilized to improve textual gradients and update variables effectively. These examples serve as references to illustrate the characteristics of optimized variables. When in-context examples are applied, TextGrad adopts the following prompt to incorporate them:

## In-context examples prompt

```
You must base on the following examples when modifying the {role _ description}: <EXAMPLES> {in _ context _ examples} </EXAMPLES>
```

By leveraging these examples, TextGrad can better understand and implement the properties of optimized variables, enhancing the overall optimization process.

## Supplementary Note 3 Code optimization

## Supplementary Note 3.1 Methodology

Baseline details. We re-run Reflexion [2] using the code by the authors currently available online. We had to make minor changes to ensure it ran correctly in our setting but we also contacted the original authors and ask feedback on our edits to ensure our evaluation was consistent. Moreover, we had to re-extract the LeetCodeHard [2] dataset using the authors' pipeline; this means that it is likely that the dataset we are using in this manuscript is not the same dataset that was used in the Reflexion paper. While this dataset contains a set of simple tests to check if the code works as expected, the real evaluation in this context is given by passing the tests on the LeetCode platform.

Reflexion is run with a one-shot prompt that is meant to instruct the model on how to provide feedback. The pipeline run by Reflexion is as follows: given in input a prompt to generate code, a language model generates a first solution. If this solution passes the local tests, it is then submitted to the LeetCode platform to be evaluated on harder tests. However, if the solution does not pass the tests, we ask for feedback through Reflexion and optimize the code. Once again, if the new solution passes the local tests, we submit it to the LeetCode platform. We do this optimization for five iterations.

## Example query for LeetCode Hard

```
def minimumTime(grid: List[List[int]]) -> int: """
```

You are given a 'm x n' matrix 'grid' consisting of non-negative integers where 'grid[row][col]' represents the minimum time required to be able to visit the cell '(row, col)', which means you can visit the cell '(row, col)' only when the time you visit it is greater than or equal to 'grid[row][col]'.

You are standing in the top-left cell of the matrix in the '0th' second, and you must move to any adjacent cell in the four directions: up, down, left, and right. Each move you make takes 1 second.

Return the minimum time required in which you can visit the bottom-right cell of the matrix. If you cannot visit the bottom-right cell, then return '-1'.

Example 1:

```
Input: grid = [[0,1,3,2],[5,1,2,5],[4,3,8,6]] Output: 7 Explanation: One of the paths that we can take is the following: - at t = 0, we are on the cell (0,0). - at t = 1, we move to the cell (0,1). It is possible because grid[0][1] <= 1. - at t = 2, we move to the cell (1,1). It is possible because grid[1][1] <= 2. - at t = 3, we move to the cell (1,2). It is possible because grid[1][2] <= 3. - at t = 4, we move to the cell (1,1). It is possible because grid[1][1] <= 4. - at t = 5, we move to the cell (1,2). It is possible because grid[1][2] <= 5. - at t = 6, we move to the cell (1,3). It is possible because grid[1][3] <= 6. - at t = 7, we move to the cell (2,3). It is possible because grid[2][3] <= 7. The final time is 7. It can be shown that it is the minimum time possible. Example 2: Input: grid = [[0,2,4],[3,2,1],[1,0,4]] Output: -1 Explanation: There is no path from the top left to the bottom-right cell. Constraints: * '0 <= grid[i][j] <= 105'
```

```
* 'm == grid.length' * 'n == grid[i].length' * '2 <= m, n <= 1000' * '4 <= m * n <= 105' * 'grid[0][0] == 0' """
```

## Supplementary Note 4 Solution optimization

```
1 # Assume we have the test_dataset 2 question , answer = test_dataset[i] 3 # Initialize the test time loss function 4 # This has the system prompt provided above as 'Solution Refinement Objective ' 5 test_time_loss_fn = MultipleChoiceTestTime() 6 # Get a zero -shot solution from an LLM 7 solution: Variable = zero_shot_llm(question) 8 # Optimize the solution itself 9 optimizer = tg.TextualGradientDescent(parameters=[solution]) 10 11 for iteration in range(max_iterations): 12 optimizer . zero_grad () 13 # Note how the loss is self -supervised (does not depend on any ground truth .) 14 loss = test_time_loss_fn(question , solution) 15 # Populate the gradients , and update the solution 16 loss . backward () 17 optimizer . step ()
```

Code Snippet 5 A representative implementation of solution optimization in TextGrad.

## Supplementary Note 4.1 Methods

For the CoT 0-shot prediction, we use the question template and system prompt released with GPT-4o in the simple-evals repository. In particular, to closely match their evaluations, we use the ChatGPT system prompt: "You are ChatGPT, a large language model trained by OpenAI, based on the GPT-4 architecture. \n Knowledge cutoff: 2023-12 \n Current date: 2024-04-01" . Further, we use the following template:

## Multiple choice question answering template

Answer the following multiple choice question. The last line of your response should be of the following format: 'Answer: $LETTER' (without quotes) where LETTER is one of ABCD. Think step by step before answering.

```
{Question} A) {A} B) {B} C) {C} D) {D}
```

During optimization, we provide the constraint to the optimizer that the prediction should conclude with an answer, following the simple-evals repository, through the following constraint description: "The last line of your response should be of the following format: 'Answer: $LETTER' (without quotes) where LETTER is one of ABCD. " .

For solution refinement for multimodal question answering, we use the following objective:

## Solution refinement objective for multimodal question answering

## For visual mathematical reasoning:

LLM("Please evaluate the existing answer to the visual math problem without solving it yourself. Verify that the answer provides accurate reasoning logic to address the question.

```
Image: {Image data} Question: {Question} Answer by the language model: {Solution}")
```

## For visual scientific reasoning:

LLM("Please evaluate the existing answer to the visual scientific problem without solving it yourself. Verify that the answer accurately understands the image, provides appropriate knowledge and reasoning logic to address the question.

```
Image: {Image data} Question: {Question} Answer by the language model: {Solution}"
```

GPQA Diamond subset contains 198 questions. MMLU Machine Learning subset contains 112 questions, and College Physics subset contains 92 questions. At each iteration of optimization, we make one call to gpt-4o to evaluate the test time loss, one call to collect gradients, and one call to update the solution.

## Supplementary Note 4.2 Prompts

Below is an example for GPQA Diamond task [3]:

## Example query for GPQA Diamond

What is the concentration of calcium ions in a solution containing 0.02 M stochiometric Ca-EDTA complex (we assume that the pH is ideal, T = 25 °C). KCa-EDTA = 5 × 10 10 .

A) 5.0×10-3 M

B) 1.0×10-2 M

C) 6.3×10-7 M

D) 2.0×10-2 M

An example query for multimodal question answering benchmark, ScienceQAIMG [4], is shown below:

## Example query for ScienceQA-IMG

You will answer a scientific question based on an image. Please ensure you accurately interpret the image and think step by step. The last line of your answer should be formatted as follows: 'Answer: (X) Your Option. '

Context: Below is a food web from an ocean ecosystem in Monterey Bay, off the coast of California. A food web models how the matter eaten by organisms moves through an ecosystem. The arrows in a food web represent how matter moves between organisms in an ecosystem.

## &lt;image of a food web&gt;

Question: In this food web, which organism contains matter that eventually moves to the sea cucumber?

## Choices:

- (A) bat star
- (B) kelp
- (C) kelp bass
- (D) black rockfish

Reflexion baseline. In their closes question answering setting, [2] uses the ground truth supervision signal during test-time optimization. To make their approach applicable to solution optimization, we give the Reflexion algorithm access to our test-time objectives. In particular, in their reflection step, Reflexion uses our test time loss function and their own prompts to revise the solutions at test time. Otherwise, we are using their prompts and in-context examples shared in their official repository. For multimodal reasoning and hallucination tasks, we prompt gpt-4o to generate image descriptions conditioned on the input query. This approach preserves the image's informational content necessary for question answering while reducing the number of input tokens to fit within the input context window limit. We determine the optimal number of trials based on peak performance in the downstream task.

## Example: Multimodal solution optimization for visual scientific reasoning

## &lt;image of an orange tree&gt;

Question: An adult orange tree can grow seeds. Which part of the orange tree makes the seeds? (A) the flowers (B) the fruit

## Solution at initialization:

The image shows an orange tree with numerous fruits and flowers, indicating different stages of the reproductive process. Flowers are pollinated, leading to the fertilization of ovules, which develop into seeds. These seeds are then encased within the fruit as it forms.

The flowers of the orange tree are pollinated, leading to the development of seeds within the ovules of the flowers. These seeds are then encased within the fruit as the flower turns into the fruit. Therefore, the part of the orange tree that makes the seeds is the fruit. Answer: (B) the fruit

## Output of the loss function based on multimodal context:

The existing answer provides a detailed explanation of the biological process of seed formation in fruit trees, which is accurate. It correctly identifies that flowers are pollinated, leading to the development of seeds within the ovules, and these seeds are then encased within the fruit. The answer also correctly interprets the image, noting the presence of both fruits and flowers on the orange tree.

However, there is a slight misinterpretation in the final conclusion. While the seeds are indeed found within the fruit, the part of the tree that initially makes the seeds is the flower, as the seeds develop from the fertilized ovules within the flowers.

## Solution after optimization:

The image shows an orange tree with numerous fruits and flowers, indicating different stages of the reproductive process. Flowers are pollinated, leading to the fertilization of ovules, which develop into seeds. These seeds are then encased within the fruit as it forms.

In summary, the flowers of the orange tree are pollinated, leading to the development of seeds within the ovules of the flowers. These seeds are then encased within the fruit as the flower turns into the fruit. Therefore, the part of the orange tree that initially makes the seeds is the flower. Answer: (A) the flowers

## Supplementary Note 5 Prompt optimization

```
1 # Initialize the system prompt 2 system_prompt = tg.Variable( 3 "You are a helpful language model. Think step by step.", 4 requires_grad =True , 5 role_description="system prompt to the language model" 6 ) 7 8 # Set up the model object 'parameterized by' the prompt. 9 model = tg.BlackboxLLM(system_prompt=system_prompt) 10 11 # Optimize the system prompt 12 optimizer = tg.TextualGradientDescent(parameters=[system_prompt]) 13 14 for iteration in range(max_iterations): 15 batch_x , batch_y = next(train_loader) 16 optimizer . zero_grad () 17 # Do the forward pass 18 responses = model(batch_x) 19 losses = [loss_fn(response , y) for (response , y) in zip(responses , batch_y )] 20 total_loss = tg.sum(losses) 21 # Perform the backward pass and compute gradients 22 total_loss . backward () 23 # Update the system prompt 24 optimizer . step ()
```

Code Snippet 6 A simple implementation of prompt optimization with TextGrad.

## Supplementary Note 5.1 Tasks

Below, we provide an example query for each of the tasks in the prompt optimization section.

## Example query for Word Sorting

Sort the following words alphabetically: oakland seaborg jacobi membrane trapezoidal allis marmot toggle anthology.

## Example query for Object Counting

I have a couch, a bed, a car, a fridge, two tables, an oven, a toaster, and a chair. How many objects do I have?

## Example query for GSM8k

Amber, Micah, and Ahito ran 52 miles in total. Amber ran 8 miles. Micah ran 3.5 times what Amber ran. How many miles did Ahito run?

For word sorting and object counting, we obtain the datasets from the BBH repository, and we randomly split examples into 51 (training)/100 (validation)/99 (test)

samples. For GSM8k, we use the splits provided in DSPy [5] which has 200 (training)/300 (validation)/1,319 (test) samples.

We use the OPRO algorithm [6] shared in their repository with the default hyperparameters. In particular, the optimizer generates 8 candidates at every timestep, uses 3 in-context exemplars for the task with five optimizer iterations.

Evaluation. For object counting and GSM8k, we use the string-based exact match metric, which looks at the last numerical value provided in the answer, and compares it to the ground truth answer. For word sorting, we prompt gpt-4o to compare the ground truth list to the response provided in the answer, through the following prompt:

## Evaluation system prompt for Word Sorting evaluation

## System prompt:

Below is a question from a question-answering task, the ground truth answer, and reasoning with the final prediction. Is the final prediction correct, i.e. the same as the ground truth answer? Say only 1 (yes) or 0 (no). Return your response within &lt;ACCURACY&gt; &lt;/ACCURACY&gt; tags. E.g., &lt;ACCURACY&gt; 0 &lt;/ACCURACY&gt; or &lt;ACCURACY&gt; 1 &lt;/ACCURACY&gt;.

## Example prompt:

- **Question for the task:** {question}
- **Ground truth answer:** {answer}
- **Reasoning and prediction from the language model:** {prediction}

## Supplementary Note 6 Scalability and feasibility

## Supplementary Note 6.1 Optimization using open-source models

We experiment with using open-source models in two different settings.

To provide further evidence on accessibility, we explore optimization using open-source models. In particular, we test prompt optimization using Llama3.1-70B Instruct [11], which is a recently released open-source model. We use Llama-3.1-70B as an optimizer, and we test optimizing prompts for three different models: Llama-3.2-11B, Mixtral 8x22B [12], and Llama-3.170B itself. We make no changes to the framework for this optimization. We use the Llama turbo endpoints served by Together AI. We use the Meta-Llama-3.1-70B-Instruct-Turbo, Mixtral-8x22B-Instruct-v0.1, Llama-3.2-11B-Vision-Instruct-Turbo endpoints for faster access to these models.

In Table Supplementary Table 2, we show the results for prompt optimization. In particular, we see that prompts optimized for open-source models, using open-source models, can improve their performance. We observe that the degree of improvement is larger for more capable models. As open-source LLMs rapidly progress, we expect TextGrad to be even more useful to a broader audience.

Supplementary Table 1 Prompt optimization for reasoning tasks. With TextGrad, we optimize a system prompt or the in-context examples for gpt-3.5-turbo using gpt-4o as the gradient engine that provides the feedback during backpropagation.

| Dataset             | Method                                                                                                                                                                                                    | Accuracy (%)                  |
|---------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------|
| Object Counting [7] | CoT (0-shot) [8, 9] OPRO [6] (instruction-only, 0 demonstrations) DSPy (BFSR, 8 demonstrations) [5] TextGrad (3 demonstrations) TextGrad (instruction-only, 0 TextGrad (instruction and 3 demonstrations) | 77.8 82.8 84.9 91.9 91.9 91.9 |
| Object Counting [7] | demonstrations)                                                                                                                                                                                           |                               |
| Word Sorting [7]    | CoT (0-shot) [8, 9]                                                                                                                                                                                       | 76.7                          |
| Word Sorting [7]    | OPRO [6] (instruction-only, 0 demonstrations)                                                                                                                                                             | 77.8                          |
| Word Sorting [7]    | DSPy (BFSR, 8 demonstrations) [5]                                                                                                                                                                         | 79.8                          |
| Word Sorting [7]    | TextGrad (3 demonstrations)                                                                                                                                                                               | 78.8                          |
| Word Sorting [7]    | TextGrad (instruction-only, 0 demonstrations)                                                                                                                                                             | 79.8                          |
| Word Sorting [7]    | TextGrad (instruction and 3 demonstrations)                                                                                                                                                               | 80.8                          |
| GSM8k [10]          | CoT (0-shot) [8, 9]                                                                                                                                                                                       | 72.9                          |
| GSM8k [10]          | OPRO [6] (instruction-only, 0 demonstrations)                                                                                                                                                             | 76.8                          |
| GSM8k [10]          | DSPy (BFSR, 8 demonstrations) [5]                                                                                                                                                                         | 81.1                          |
| GSM8k [10]          | TextGrad (3 demonstrations)                                                                                                                                                                               | 80.1                          |
| GSM8k [10]          | TextGrad (instruction-only, 0 demonstrations)                                                                                                                                                             | 81.1                          |
| GSM8k [10]          | TextGrad (instruction and 3 demonstrations)                                                                                                                                                               | 82.4                          |

## Supplementary Note 6.2 Robustness of optimized prompts

To further the evidence on accessibility, we test the transferability of prompts optimized for gpt-3.5-turbo. In particular, we take the prompts optimized for gpt-3.5-turbo, and use them as prompts to various other open-source models. This is to demonstrate that once the optimization is done, without having to do it again, the optimized variables can transfer between different models.

We use Llama-3.1-8B Instruct and Llama-3.1-70B Instruct from Together AI, Qwen-2.5 models [13] from Huggingface's Transformers [14] library, and Gemini-1.5Flash [15] from the Gemini family.

In Table Supplementary Table 3, we present the results. Overall, prompts optimized for closed-source models using closed-source models transfer well to other models. In particular, we observe a greater degree of transferability for more capable models, and again we expect this degree of improvement to only get better as open-source models are becoming more capable.

## Supplementary Note 6.3 Cost-accuracy analysis

We report the cost-accuracy frontier of prompt optimization in Supplementary Fig. 1. In particular, we compare the fixed cost of optimizing a prompt for gpt-3.5-turbo using the existing techniques to the performance obtained via that method. This cost is paid once to optimize a prompt. On x-axis we report this cost, and on the y-axis, we report the performance.

Supplementary Table 2 Prompt optimization for reasoning tasks using open-source models. We optimize system prompts and in-context demonstrations for various models using TextGrad with Llama-3.1-70B Instruct as the gradient engine that provides feedback during backpropagation and the optimizer.

| Dataset             | Method Llama-3.2-11B Vision Instruct [11]   | Accuracy (%)   |
|---------------------|---------------------------------------------|----------------|
| Object Counting [7] | CoT (0-shot) [8, 9]                         | 82.8 89.4      |
|                     | TextGrad (instruction and 3 demonstrations) |                |
| Word Sorting [7]    | CoT (0-shot) [8, 9]                         | 63.6           |
|                     | TextGrad (instruction and 3 demonstrations) | 64.6           |
| GSM8k [10]          | CoT (0-shot) [8, 9]                         | 86.1           |
|                     | TextGrad (instruction and 3 demonstrations) | 86.1           |
|                     | Mixtral 8x22B Instruct [12]                 |                |
| Object Counting [7] | CoT (0-shot) [8, 9]                         | 87.9           |
|                     | TextGrad (instruction and 3 demonstrations) | 89.8           |
|                     | CoT (0-shot) [8, 9]                         | 71.7           |
| Word Sorting [7]    | TextGrad (instruction and 3 demonstrations) | 78.3           |
| GSM8k [10]          | CoT (0-shot) [8, 9]                         | 91.3           |
|                     | TextGrad (instruction and 3 demonstrations) | 91.3           |
|                     | Llama-3.1-70B Instruct [11]                 |                |
| Object Counting [7] | CoT (0-shot) [8, 9]                         | 85.9           |
|                     | TextGrad (instruction and 3 demonstrations) | 93.1           |
| Word Sorting [7]    | CoT (0-shot) [8, 9]                         | 87.9           |
|                     | TextGrad (instruction and 3 demonstrations) | 95.8           |
| GSM8k [10]          | CoT (0-shot) [8, 9]                         | 94.8           |
|                     | TextGrad (instruction and 3 demonstrations) | 95.1           |

Overall, we highlight two observations. First, TextGrad consistently lies on the Pareto frontier. Second, the fixed cost of running prompt optimization is often less than $1, highlighting that prompt optimization is not expensive to perform with these methods.

Secondly, we report the cost-accuracy frontier for solution optimization also in Supplementary Fig. 1. Here, we report the average cost of running test-time optimization using gpt-4o for a given instance. This means for every test instance we run this algorithm, we incur this cost.

We again observe that TextGrad is at the Pareto frontier here, and the cost of running optimization per instance is usually less than $0.10. This again highlights that running optimization using these models is often not expensive.

Supplementary Table 3 Transferability of optimized prompts. We test the transferability of prompts optimized for gpt-3.5-turbo using TextGrad on different models. Overall, optimized prompts improve the performance of various open-source and closed models, with up to 10% absolute performance gains.

| Model                  | Dataset                      | Method                                  | Accuracy       |
|------------------------|------------------------------|-----------------------------------------|----------------|
| Gemini-1.5-Flash       | GSM8k                        | CoT TextGrad-Transfer                   | 91.1 92.3      |
| Gemini-1.5-Flash       | Object Counting              | CoT TextGrad-Transfer                   | 86.9 81.8      |
| Gemini-1.5-Flash       | Word Sorting                 | CoT TextGrad-Transfer                   | 59.6 70.7      |
| Qwen-2.5-14B Instruct  | GSM8k                        | CoT TextGrad-Transfer CoT               | 94.6 94.9 85.9 |
| Qwen-2.5-14B Instruct  | Object Counting Word Sorting | TextGrad-Transfer CoT TextGrad-Transfer | 86.9 32.3 33.3 |
| Qwen-2.5-32B Instruct  | GSM8k                        | CoT TextGrad-Transfer                   | 95.6 96.6      |
| Qwen-2.5-32B Instruct  | Object Counting              | CoT TextGrad-Transfer                   | 83.8 92.9      |
|                        | Word Sorting                 | CoT TextGrad-Transfer                   | 47.5 55.6      |
|                        | GSM8k                        | CoT TextGrad-Transfer                   | 86.8           |
| Llama-3.1-8B Instruct  | Object Counting              | CoT TextGrad-Transfer                   | 86.8 86.9 94.9 |
|                        | Word Sorting                 | CoT TextGrad-Transfer                   | 46.5 45.5      |
| Llama-3.1-70B Instruct | GSM8k                        | CoT TextGrad-Transfer                   | 94.4 94.0      |
| Llama-3.1-70B Instruct | Object Counting              | CoT TextGrad-Transfer                   | 94.9 96.0      |
| Llama-3.1-70B Instruct | Word Sorting                 | CoT TextGrad-Transfer                   | 73.7 84.8      |

Supplementary Fig. 1 Cost-accuracy frontier for prompt optimization (top row) and instance optimization (bottom row). We observe that prompt optimization often has a cost less than $1, and instance optimization often has a cost of less than $0.1, highlighting that optimization with TextGrad is inexpensive.

<!-- image -->

## Supplementary Note 7 Treatment plan optimization

## Supplementary Note 7.1 Prompts

Radiotherapy treatment plan evaluation can based on various dimensions, therefore there is no single score that can indicate the quality of plans. We adopt LLM to compute the "loss" by prompting it to assess the plan quality with clinical protocols. Specifically, LLM is used to compare each protocol with the current plan and produce the final assessment.

## Supplementary Note 7.2 Inner-loop optimization for treatment planning

We employ a two-loop optimization approach [16], which includes i) an inner loop for inverse planning and ii) an outer loop for optimizing the hyperparameters of the inner loop. The inner loop focuses on traditional fluence map optimization, seeking to determine the optimal fluence map x by minimizing a cost function that combines multiple weighted objectives for various targets and organs at risk. This cost function is defined as:

<!-- formula-not-decoded -->

Here, {wt}Nt t=1 and {ws}Ns s=1 are the importance weights (the hyperparameters optimized by TextGrad) that balance the various objectives for Nt PTV targets and Ns OARs, respectively. K denotes the dose influence matrix, which specifies the dose per fluence unit delivered to each voxel in the volume by each beamlet. {dt}Nt t=1 and {ds}Ns s=1 are the scalar objective doses for each structure. The cost function essentially penalizes squared deviations from the target objective doses for the PTV targets and penalizes squared overdosing for the OARs only when doses exceed ds. The Heaviside function Θ is used to ensure the objective considers only positive values. The minimization is constrained to positive x values and ensures that D95 - the minimum dose received by 95% of the structure volume - matches the prescribed dose for the clinical goal. We use matRad [17] with interior point algorithms to solve the inner-loop optimization.

In clinical practice, evaluating radiotherapy treatment plans involves balancing multiple quality metrics (e.g., mean dose, D95), without a clear consensus on their relative importance. This complexity makes it difficult to design a unified "score function" that combines these metrics into a single objective for direct optimization. Additionally, many of these metrics are non-differentiable, which complicates the use of gradient-based optimization techniques. As a result, designing an effective optimization algorithm for the outer loop is both challenging and critical for successful automatic radiation oncology treatment planning.

## Treatment plan loss prompt

Please act as an impartial and objective professional radiation oncologist. Your job is to evaluate the quality of radiation therapy treatment plans based on their dose volume histogram. You should consider the following protocols: &lt;Clinical Protocols&gt;

Note that the order above does not indicate priority; always prioritize the regions that have protocols that are more significantly violated.

Here is the dose-volume histograms of the candidate plans for evaluation; each entry in the dose-volume histograms (DVH) table indicates the percentage of volume receiving a dose higher than a certain Gy (specified in the first column).

&lt;DVH table&gt;

We also provide the statistics of the above DVH table for ease of evaluation. &lt;DVH statistics&gt;

Now, based on the protocols, and the DVH, please evaluate the plans. Avoid any positional biases and ensure that the order in which the responses are presented does not influence your decision. Be as objective as possible. Your answer must:

1. (Evidence) Extract the corresponding entries from the DVH table based on the factors to consider.
2. (Interpretation) Based on the extracted entries from DVH table, interpret them as: {percentage}% of volume encompassing the dose more than {dose} Gy for {organ}.
3. (Analysis) Combine the interpretation and the factors, analyze whether each of the numerical factors are met.

Based on the analysis on DVH tables, you need to produce a final evaluation. When all factors are satisfied, you should always answer no improvement is needed. If improvements are required, please provide suggestions on where to improve. Please ensure to follow the format below to return the evaluation results:

&lt;FINAL&gt; Decision: [The plan does/doesn't need to be improved.] Reasons: [list all factors that are not satisfied with detailed reasons, e.g. protocol X on (PTV/rectum/bladder/fh/body) is not satisfied because ...] &lt;/FINAL&gt;

The final answer in the end must strictly follow the format above.

Previous works have typically used a weighted sum of multiple metrics, often referred to as a Plan Quality Metrics (PQMs), as the objective in the outer loop. Since some of these metrics are non-differentiable, [18] applied Bayesian Optimization (BO) to optimize the hyperparameters in the outer loop. Following their approach, we use Optuna [19] to implement Bayesian optimization for PQM as our baseline.

## Supplementary Note 8 Molecule optimization

## Supplementary Note 8.1 Molecule optimization

TextGrad supports a variety of optimization problems, including multi-objective optimization tasks commonly found in science and engineering applications. For example, in drug discovery, researchers seek to discover or design molecules that maximize a variety of objectives with regards to synthesizability, efficacy, and safety [20, 21]. To demonstrate TextGrad's applications to multi-objective optimization, we apply TextGrad to drug molecule optimization, and show how our framework can interface with computational tools and optimize chemical structures towards simultaneously improving their binding affinity and druglikeness as measured by in silico oracles.

Task. A critical consideration for potential drug molecules is their binding affinity, which represents the strength of the interactions between the molecule and its protein target. Drug designers seek molecules with high binding affinities to relevant drug targets, as they require lower and less frequent doses to achieve efficacy. This affinity can be quantified by free energy ∆G, which describes the ratio of probabilities between bound and unbound ligand-receptor pairs. ∆G can be estimated using "docking" simulations of protein-ligand binding [22, 23]. In our experiments, we employ the Vina score from the Autodock Vina tool, a widely used physics-based docking simulator [24]. A more negative Vina score indicates that the drug is predicted to be more likely to bind to its intended target.

Potential drug molecules are also evaluated by their druglikeness, which estimates how the molecule will behave in vivo, with respect to solubility, permeability, metabolic stability and transporter effects. Molecules with high druglikeness are more likely to be absorbed by the body and reach their targets [25]. One metric for "druglikeness" is the Quantitative Estimate of Druglikeness (QED) score, a weighted composite score of chemical characteristics such as molecular weight, lipophilicity, polar surface area, among others. The QED score ranges from 0 to 1, where 1 indicates high druglikeness [26].

Though there are many more considerations for successful molecules, in our experiments, we restrict our objectives to minimizing the Vina score and maximizing the QED. Since each score evaluates different considerations in molecular design, optimizing one does not necessarily imply improvement in the other. Thus, optimizing molecules that simultaneously improve both objectives is non-trivial.

Methods. We apply TextGrad to drug molecule optimization by encoding molecules as SMILES strings and constructing a multi-objective loss from the Vina and QED scores. Namely, we perform test-time optimization over SMILES strings, where the gradients generated by TextGrad with respect to the multi-objective loss are used to update the text representing the molecule:

Evaluation = LLM((Affinity(SMILESi, target), Druglikeness(SMILESi)),

(H8)

<!-- formula-not-decoded -->

We use gpt-4o as our LLM with the prompt text found in Supplementary Note 8.3. At each iteration, the current molecule is evaluated by estimating its binding affinity to the target protein using the Vina score from Autodock Vina and using the QED score for druglikeness from RDKit (Supplementary Note 8.2). Each molecule is initialized as a small chemical fragment from a functional group. We apply TextGrad to all 58 targets in the DOCKSTRING molecule evaluation benchmark [27]. These 58 targets consist of clinically relevant proteins sampled from a variety of structural classes, 29 of which have clinically approved drugs. For each target, we optimize a starting fragment using TextGrad for up to 10 iterations (Supplementary Note 8.8), for 3 unique initial fragments. To evaluate our performance, we compare the characteristics of the molecules generated by TextGrad to clinically approved drugs for the respective protein (Supplementary Note 8.4).

Results. For all 58 targets, TextGrad consistently generates molecules with improved binding affinity and druglikeness irrespective of the initial starting fragment (Supplementary Note 8.5). For the 29 protein targets with clinically approved drugs, we observe that TextGrad generates molecules with highly competitive affinity and druglikeness when compared to clinical molecules evaluated using the same loss function (Extended Data Fig. 1b). The resulting molecules exhibit unique structures compared to their clinical approved counterparts and existing compounds (Supplementary Note 8.6), while maintaining similar in silico safety profiles (Supplementary Note 8.7). By combining specialized tools from computational chemistry with the general knowledge and reasoning capabilities of LLMs, TextGrad enables users to perform molecule optimization from arbitrary starting molecules, without the need for additional finetuning datasets, or high-performing initializations from curated compound libraries. Furthermore, TextGrad 's natural language gradients enable users to transparently analyze the optimization process and the impetus for the changes between each molecule in the trajectory. Though promising, we caution that the practical value of the molecules TextGrad has generated are limited. In particular, we optimize over and evaluate only a few properties, all evaluated using in silico objective functions (e.g. Vina, QED, ADMET scores), which are not reliable substitutes for experimental and clinical evaluation.

## Supplementary Note 8.2 Docking and druglikeness evaluation

To optimize molecules, we evaluate the binding affinity and druglikeness of chemical structures encoded as SMILES strings. To compute both metrics, the generated SMILES string is first converted into an octet-complete Lewis dot structure using RDKit's MolFromSmiles functionality. This method "sanitizes" molecules by adding explicit hydrogens, kekulizing aromatic rings, standardizing valence states, and assigning radicals [28]. If this sanitization process fails at any step, whether through a structural ambiguity or an invalid molecule, the QED and Vina scores are replaced with a single string informing TextGrad that the molecule is invalid.

If the generated SMILES string does represent a valid chemical structure, we compute the QED score using RDKit's Chem.QED function. While QED scores can be quickly and reliably computed, docking scores can vary significantly depending on target and ligand structure preparation. To ensure consistency, we calculate Vina scores using the DOCKSTRING package [27], which implements a standardized docking workflow and provides a set of gold-standard targets. In particular, after the ligand has been sanitized by RDKit, DOCKSTRING (de)-protonates it at pH 7.4 using Open Babel, and prepares and refines the 3D geometric structure using the Euclidean distance geometry algorithm ETKG and the classical force field MMFF94. Finally, Gasteiger charges are computed for all ligand atoms, and the resulting structure is saved as a ligand PDBQT file passed to Autodock Vina. For target preparation, the DOCKSTRING benchmark suite provides 58 curated crystal structures of clinically relevant proteins, with the majority at less than 2.5 Å resolution. These structures are specially prepared to improve correlations between theoretical and experimental binding affinities, for example by manual addition of polar hydrogens and removal of residual water and solute molecules. DOCKSTRING also standardizes simulation parameters such as numerical seeds, search box coordinates, and sampling exhausitivity, to ensure reproducible scoring.

## Supplementary Note 8.3 Objective functions

Once the scores have been computed, they are passed to an LLM in the following format.

## Molecule optimization prompt

Given a docking and a druglikeness score, and a molecule as a SMILES string provide a short criticism to improve the druglikeness of this molecule and its binding affinity with the protein {protein\_name}. For docking, lower is better (less than -10 is considered good) and for druglikeness, 1 is the best and 0 is the worst (greater than 0.8 is considered good). In terms of prioritization, the docking score is {vina\_qed\_ratio} times as important as the druglikeness score. Make sure your criticism is very succinct and to the point.

```
SMILES: {smiles_string}, Docking: {Vina}, Druglikeness: {QED}
```

```
# if smiles_string is valid # if smiles_string is invalid SMILES: {smiles_string}, This molecule is invalid.
```

In practice, drug efficacy is typically a higher priority than absorbtion efficiency [29, 30], so we set the vina\_qed\_ratio to be 10. Empirically, we observe that by scaling this prioritization factor, we can tune TextGrad's generation towards molecules with differing binding affinity and druglikness tradeoffs (Supplementary Note 8.9). This prioritization also allows us to simplify post-hoc selection and ranking of the generated molecules with a single "overall" score defined as follows, where a lower overall score soverall indicates a better molecule:

<!-- formula-not-decoded -->

Since the QED score is bounded between 0 and 1, and the Vina score typically ranges between -3.0 to -12.0 kcal/mol, soverall with the default vina\_qed\_ratio = 10 places approximately 10 times more emphasis on binding affinity than druglikeness as desired.

## Supplementary Note 8.4 Benchmarks

To benchmark the performance of TextGrad generated molecules, we compare their characteristics to clinically approved drugs for the same protein targets found in DrugBank, a database of 16, 619 drugs [31]. To ensure that the DrugBank molecules were both comparable and high quality, we filtered for drugs that were small molecules, had full clinical approval, and were designed for orthosteric binding with the same active site in the DOCKSTRING benchmark suite. After these filtering criteria, we identified 118 drugs targeting 29 of the 58 DOCKSTRING proteins. When evaluating binding affinity and druglikeness for the clinically approved drugs, we compute the Vina and QED scores using the same tools and workflow described in Supplementary Note 8.2, exactly as applied to the TextGrad molecules.

## Supplementary Note 8.5 Initialization

In practice, molecular optimization is typically accelerated by large scale preoptimization screening, where libraries of millions or even billions of existing chemical structures are scored and ranked by docking, druglikeness, and other metrics. Only the most promising structures, termed "leads" , are further refined by medicinal chemists [32]. While TextGrad is capable of optimizing any initial molecule, in this work, we instead select our three initial molecules from simple fragments of common functional groups, shown in Supplementary Fig. 2 in order to more accurately characterize it's performance and avoid biasing its designs towards existing drugs. These fragments are highly diverse, and belong to different functional groups. Although these initial fragments have differing druglikness and binding affinity characteristics, the impact of the starting fragment on TextGrad's performance is minimal, and TextGrad is capable of generating molecules with high druglikeness and binding affinity from all three fragments.

Supplementary Fig. 2 Molecule initialization. We initialize TextGrad with fragment molecules from three, diverse functional groups and optimize each initial molecule for 10 iterations for all 58 targets in the DOCKSTRING benchmark suite. For each fragment and each protein, we perform post selection on the generated molecules using the summary score outlined in equation H10 and visualize the resulting distribution. We observe that while the initial QED and Vina score distributions of the starting fragments vary greatly, the distribution of the optimized molecules is highly overlapping.

<!-- image -->

## Supplementary Note 8.6 Chemical novelty

One of the primary concerns with using LLM models in scientific discovery is their capacity to simply memorize and regurgitate their training sets instead of performing logical reasoning [33]. Since recent models like gpt-4o are trained on massive, opaque datasets, a key concern is that the molecules TextGrad generates may simply be duplicates of clinically approved molecules for their respective targets. To quantify and test the extent or existence of this "memorization" effect, we compare the molecules that TextGrad generates with approved drugs for their respective protein targets, as well as unrelated but existing druglike chemical compounds.

We first compare TextGrad generated molecules for a particular protein target with all the clinically approved small molecules found in Drugbank for the same target (see Supplementary Note 8.4 for filtering criteria) using the Tversky similarity score on RDKit daylight chemical fingerprints. The Tversky similarity score is not symmetric, and compares substructures between a variant and reference molecule [34]. In our application, this is preferred as it assigns a high score to generated (variant) molecules that contain most or all of the substructures in the Drugbank (reference) molecule, even if there exist other extraneous substructures in the generated molecule that reduce the symmetric overlap between the two molecules. A Tversky score of 1.0 indicates that the TextGrad molecule is a complete subset of the Drugbank molecule, while 0.0 indicates no overlap.

Supplementary Fig. 3 Structural novelty. (a) We observe increasing novelty over optimization updates, where a generated molecule is considered"novel" if there does not exist any existing molecule in ChEMBL with a Tanimoto similarity score greater than 0.8. (b,c,d) We estimate substructure similarity using the Tversky metric between TextGrad molecules and clinically approved drugs for each target. While there are a wide range of similarity scores, we observe that similarity with known drugs has little correlation with molecule performance, suggesting that TextGrad's generation process is weakly influenced by "memorized" knowledge of clinically approved structures.

<!-- image -->

In order to analyze the most relevant chemical structures, we restricted our analysis to a set of high performing TextGrad molecules, rather than all molecules from all iterations. In particular, using the overall score described in Equation H10, we selected the best molecule for each protein target and for each initial fragment, for a total of 87 generated molecules (29 druggable targets x 3 initial fragments) and 118 clinically approved drugs across 29 targets. For each target, we compute all pairwise Tversky scores between the 3 TextGrad molecules and the Drugbank molecules approved for that target, setting the Drugbank molecule as the reference, and the TextGrad molecule as the variant.

We observed that the distribution of Tversky similarity scores was quite broad, with a median of 0.42 but ranging from 0.14 to 0.90 (Supplementary Fig. 3b). However, we observe that Tversky similarity between TextGrad and DrugBnak molecules is actually slightly anti-correlated with molecule performance as measured by the overall score, suggesting that TextGrad 's optimization procedure is at best weakly influenced by prior knowledge of approved drugs. In fact, for a variety of generated molecules along a gradient of similarity scores, the generated molecules exhibit QED and Vina scores that match or even exceed their DrugBank counterparts (Supplementary Fig. 3d). We caution however that this does not imply that the TextGrad molecule holds clinical value, as clinically approved molecules are optimized on far more criteria, and our metrics of binding afinity and druglikeness are computed by in silico oracles that may not reflect experimental behavior.

Beyond the similarity to known drugs, we are also interested in observing if TextGrad is generating novel molecules, or discovering previously unknown properties in existing compounds, for example a strong binding affinity to a protein target in a compound that has not been associated with the protein. To answer this question, we perform a Tanimoto similarity search across all of ChEMBL, a manually curated database of 2.4 million bioactive molecules with drug-like properties [35]. Unlike the Tversky score, the Tanimoto metric measures the symetric overlap between two chemical structures, where 1.0 indicates an exact match, and 0.0 no overlap. We classify a TextGrad compound as novel if and only if there does not exist any molecule in ChEMBL with a with a Tanimoto similarity score over 0.80.

While the starting fragments are known molecules, we observe that as the number of iterations increases, TextGrad generates molecules that are progressively less likely to be previously known compounds. By the 6th iteration, 95% of all the molecules generated by TextGrad across all 58 targets and three starting fragments are novel using the criteria above (Supplementary Fig. 3a). By observing the trajectories of generated molecules and analyzing the textual gradients, we hypothesize that the feedback provided by the Vina and QED scores encourages TextGrad to explore chemical space beyond known molecules by progressively adding and removing combinations of functional groups. Since these chemical updates can form a combinatorial number of unique structures, it is reasonable that TextGrad would reach previously unexplored regions of chemical space in a relatively small number of iterations.

## Supplementary Note 8.7 Extended post-generation analysis

We further evaluate our generated molecules post-generation, focusing on safety profiles related to mutagenisis and clinical toxicity. Mutagenicity refers to the ability of a drug to induce genetic alterations, which may lead to DNA damage and harmful longterm affects. Clinical toxicity refers to a broad range of adverse short or long-term side effects. Importantly, neither druglikeness nor binding affinity are strongly correlated with these criteria, and thus these desirability metrics are not directly optimized or otherwise explicitly encoded in TextGrad's objectives.

To evaluate the propensity for mutagenisis and clinical toxicity, we employ the ADMET-AI model, that predicts these scores from the chemical structures of molecules [36]. ADMET-AI employs a deep learning model trained on multiple relevant datasets. In particular, for mutagenicity, ADMET-AI is trained on 7, 255 drugs from the Ames dataset, a bacterial reverse mutation assay for rapidly screening large numbers of compounds for can induced genetic damage and frameshift mutations. A

Supplementary Fig. 4 Safety properties. We evaluate the predicted harmfulness of TextGrad molecules using the ADMET-AI model and compare them to clinically approved drugs. For both mutagenicity and clinical toxicity, 1.0 indicates a highly likelihood for harm and 0.0 a low likelihood. We observe that TextGrad proposes molecules a similar predicted distributions to clinical counterparts, despite neither metric being directly optimized.

<!-- image -->

predicted label of 1.0 indicates a high likelihood that the drug will induce mutagenesis, while a label of 0.0 indicates a low likelihood. For clinical toxicity, ADMET-AI is trained on the ClinTox dataset, a dataset of 1, 484 drugs consisting of molecules that have failed clinical trials for toxicity reasons and also drugs that are associated with successful trials. Similarly, a predicted label of 1.0 indicates a high likelihood of clinical toxicity, while a label of 0.0 indicates a low likelihood.

Once again, we restrict our analysis to the best performing generated molecules with druggable targets as measured by the overall score, and select the best molecule for each protein target and for each initial fragment, for a total of 87 generated molecules. We then compare their predicted mutagenisis and clinical toxicity to the the 118 clinically approved molecules from DrugBank. We observe that for both Mutagenicity and Clinical Toxicity, the molecules generated by TextGrad have predicted distributions that indicate a low likelihood of harmful effects, and closely match the distributions of the clinically approved molecules. Together, these results show that the molecules generated by TextGrad have favorable predicted safety profiles, even though these criteria are not directly encoded in its loss function. While promising, we caution that these safety profiles do not guarantee that the TextGrad molecule is clinically safe, as we have only investigated two areas of toxicity both predicted by in silico oracles that are not guarantees of clinical behavior.

## Supplementary Note 8.8 Parameter selection and early stopping

In the experiments outlined in Supplementary Note 8.1, we employed early stopping to determine the number of optimization iterations. In particular, we score each molecule produced using a scoring function, and if the mean of the top-K = 5 scores does not improve by more than TOL = 0.1 for more than patience = 5 iterations, the run is terminated, or until the max\_epoch = 10 is reached. Since our objective is both Vina and QED optimization, we use the overall score function defined in Equation H10. In general, a higher value of all the parameters (except TOL) will allow for longer explorations, and we invite users to select these parameters to suit their optimization budgets.

## Supplementary Note 8.9 Multi-objective steerability

We perform additional experiments quantifying the affect of the vina\_qed\_ratio parameter in steering molecule property distributions in our multi-objective optimization experiment.

Using the prompt provided in Supplementary Note 8.3, we set the vina\_qed\_ratio to 50, 25, and 1, respectively. This sequence of values represents an increase in the prioritization of the QED score relative to the Vina. Intuitively, for the value of 50, we essentially instruct TextGrad to disregard the QED score, while at 1, we inform TextGrad that the QED and Vina objectives are equally important. Starting from pentane, we optimize molecules for 10 iterations against all 58 proteins in the DOCKSTRING benchmark, for a total of 58 unique trajectories and 580 molecules.

We observe that tuning the vina\_qed\_ratio alters the distributions of the generated molecules and that an increase in QED prioritization led to a corresponding increase QED values. Conversely, a decrease in Vina prioritization led to a decrease in Vina performance (e.g. higher Vina scores). Using a paired t-test, we observed that the changes in both Vina and QED were statistically significant between the parameter settings of 50 and 1.

Supplementary Fig. 5 Vina/QED steerability. Distributions of molecule properties under different prioritization instructions. We observe a statistically significant worsening (increase) in the Vina scores upon reducing the Vina importance, and a corresponding significant improvement in the QED scores.

<!-- image -->

## Supplementary Note 8.10 Gradient specificity analysis

We perform experiments to quantify the information content and specificity of TextGrad gradients. Concretely, we compare two optimization trajectories.

- Original. In the original TextGrad framework, an initial molecule is modified by computing the loss function against a particular protein and updating its structure based on the gradient computed with respect to the loss. This process is repeated for multiple iterations, with the all gradients computed against the same protein.
- Random. In the random framework, an initial molecule is modified by randomly selecting a gradient from a different molecule docked against a different protein. This process is repeated for the same number of iterations, but with random gradients selected at each iteration.

We evaluate both sequences of molecules using the loss function (QED and Vina Score) against the original protein. If the gradients produced by TextGrad are nontarget specific, we expect that the randomized trajectory to perform as well as the original trajectory.

We compute "original" trajectories for all 58 targets in the DOCKSTRING benchmark, each starting from three initial starting fragments (benzene, pentane, acetamide) for a total of 174 original trajectories. For each original trajectory, we generate 10 random trajectories using the same initial fragment and evaluated against the same target, for a total of 1, 740 random trajectories. Each trajectory, both random and original, was optimized for 10 iterations. While the optimization length was fixed to allow for a comprehensive comparison across multiple targets and for multiple randomizations, we observed that the trends for both the random and original trajectories are readily apparent within 10 iterations.

We observe that random trajectory produces lower performing molecules relative to original trajectory across both QED and Vina metrics. Using a paired t-test across protein targets and initial molecules, we compute the difference between the QED of the final molecule generated in the original trajectory and the mean QED value of the final molecules across the 10 repetitions in the random trajectories. For a total of n = 174 paired trajectory comparisons, we report that the random trajectories have statistically significant lower QED scores than the original trajectories with a p-value of less than 1e-4. We repeat this comparison for the Vina score, and report similar results, with the random trajectories having significantly higher (worse) Vina scores (p &lt; 1e-4). We also observe that random trajectories have a higher incidence of invalid molecules, producing on aggregate 1.5x more invalid SMILES strings than the original trajectory. Using the same statistical procedure for invalidity as the Vina and QED comparison, we report that the significance is p &lt; 1e-2.

## Supplementary Note 8.11 Additional benchmarks

We compare TextGrad to 6 molecular optimization algorithms, described briefly below.

- Graph MCTS. Based on Monte-Carlo Tree Search (MCTS), Graph MCTS applies MCTS to an atom-level molecular graph [37].

a

Supplementary Fig. 6 Gradient sensitivity analysis. (a) Sample performance trajectories under original and randomly selected gradients for different protein targets and initial molecules, using the combined objective score defined by Equation H10, with a vina\_qed\_ratio = 10, identical to the value in the loss prompt. (b) We observe that random trajectories underperform the original across Vina, QED, and percentage of valid molecules. Statistical significance computed using a paired t-test across protein-initial molecule pairs.

<!-- image -->

- REINVENT. Based on Reinforment Learning (RL). REINVENT uses a policy based RL approach to tune RNNs to generate SMILES strings [38].
- REINVENT-Selfies. Similar to REINVENT, but with SELFIES strings instead of SMILES strings [39].
- GP BO. Combines Bayesian Optimization with a Gaussian Process kernel to sample molecular structures [40].
- Smiles GA. A genetic algorithm (GA) that explores molecular space through mutations and crossovers. In Smiles GA, the action space is taken over SMILES strings [41].
- Graph GA. Similar to Smiles GA, except that the action space is defined over molecular graphs [37].

Implementations were taken from the Practical Molecular Optimization (PMO) benchmark suite [39] without modification and with default hyperparameters, with the exception of the Graph MCTS algorithm which accepts an initial molecule (default CC). For Graph MCTS, we replaced the default initial molecule with the same molecule used by TextGrad (pentane, acetamide, or benzene). For a full treatment of their implementation and algorithmic details, we refer the reader to the PMO benchmark and their original publications.

Objective. For this comparison, we modified our original multi-objective of optimizing both the Vina and QED scores to only the Vina score since the benchmark algorithms above only accept single-value objective functions. While it is possible to convert our original task of multi-objective Vina/QED optimization into a weighted single-value objective, we elected to simplify the comparison between algorithms and avoid having to arbitrarily select the QED importance factor.

Evaluation metrics. To compare the performances of different molecular optimization algorithms, we use the scaled AUC top-K metric introduced by the Practical Molecular Optimization benchmark [39], with K = 5. Briefly, the top-K trajectory measures the mean performance of the top K molecules generated at for a given oracle budget (in our setting, number of docking simulations). This is preferred over a single "best" (K = 1) molecule as it rewards algorithms that generate multiple viable candidates. The AUC of the top-K trajectory quantifies both the performance of the molecules generated as well the sample efficiency of the algorithm. In our setting, the objective function is the negative docking score (e.g. maximization) which is an unbounded objective that is variable between proteins. In order to compare algorithm performance across multiple proteins, we scale each trajectory to a [0, 1] range by empirically deriving maximal and minimal AUCs for each protein across the set of algorithms compared. Specifically, for a given protein, we set the maximum AUC Top-K to be the AUC if the highest point in the top-K trajectory across all algorithms was discovered at the first oracle call, while the minimum to be the AUC if the lowest point in the top-k trajectory of all algorithms persisted for all oracle calls.

Set-up. We evaluated the 6 benchmark algorithms and TextGrad over all 58 unique protein targets in the DOCKSTRING benchmark dataset. For each protein target and algorithm, we repeated the optimization run three times for different randomization seeds for REINVENT, REINVENT-Selfies, Graph GA, Smiles GA, and GP BO. In the case of TextGrad and Graph MCTS, the runs were repeated for different initial molecules (benzene, pentane, acetamide). Each run was performed for a maximum oracle budget (e.g. number of docking simulations) of 50. For the benchmark algorithms, we ran all trajectories for the full 50 oracle calls. For TextGrad, in order to limit the number of LLM calls, we employed the early stopping procedure outlined previously. Briefly, if the mean top-K = 5 objective did not improve by more than TOL = 0.1 for more than patience = 5 iterations, the run was terminated. To calculate the AUC of these early stopped runs, we simply extend the last mean top-K objective score for the remaining oracle calls. Since the mean top-K is a non-decreasing function, this prevents us from overestimating TextGrad's performance. In total, this experiment performed a comprehensive evaluation between the

7 algorithms across 58 proteins with 174 trajectories, and generating a total of 8, 700 molecules.

Results. We outline the performance results across all 58 proteins in Extended Data Fig. 2a and sample trajectories in Extended Data Fig. 2b. We conducted a paired t-test between the AUC Top-K of TextGrad for each protein against all other methods. The difference between TextGrad and all other methods was significant, with the greatest difference between TextGrad and Graph MCTCS and the closest between TextGrad and Graph GA. While these results demonstrate the promising potential of TextGrad to optimize molecules, we do not claim that TextGrad is the best method for this particular task, and have included these comparisons as a proofof-concept. Furthermore, we reiterate that the practical value of TextGrad molecules is limited due to our reliance on in silico evaluation, and should not be interpreted as clinically useful.

## Supplementary Note 9 Optimizing compound systems

```
Algorithm 2 Chameleon with single forward pass 1: Input: Query q, module inventory M 2: Output: Final response r 3: # Initialize the cache 4: c0 ⇐ ∅ 5: # Generate the plan from the input query and modules 6: p ⇐P(q;M) 7: # Execute each module in the plan sequentially 8: for t = 1 to T do 9: M t ⇐ SelectModule(p, t) 10: yt ⇐ M t (q; ct-1 ) 11: ct ⇐ update_cache(ct-1 , yt ) 12: end for 13: # The final response is the output of the last module 14: r ⇐ yT 15: Return r
```

Details in optimizing the Chameleon agentic system. The text\_detector tool in Chameleon was implemented using EasyOCR [42], an open-source OCR library. We set its requires\_grad parameter to False, ensuring that this module's output remains static during optimization. Consistent with the original Chameleon architecture, the planner module is a language model that operates without direct access to image inputs, maintaining a strict separation between planning and perception components. For comparison experiments, both the original and our TextGrad-optimized systems used the recent gpt-4o-2024-08-06 version of GPT-4o and were evaluated on 400 test examples from ScienceQA-IMG.

## Algorithm 3 TextGrad optimization for Chameleon

```
1: Input: Query q, module inventory M, loss function L, number of iterations N 2: Output: Optimized final response r 3: # Initialization 4: c0 ⇐ ∅ 5: p ⇐P(q;M) 6: # Initial forward pass 7: for t = 1 to T do 8: M t ⇐ SelectModule(p, t) 9: yt ⇐ M t (q; ct-1 ) 10: ct ⇐ update_cache(ct-1 , yt ) 11: end for 12: r ⇐ yT 13: # Iterative chain optimization 14: for i = 1 to N do 15: for t = 1 to T do 16: l ⇐L(q, r) # Evaluate loss on the final response 17: g ⇐ gradient(l, r) # Compute gradient w.r.t. the final response 18: gt ⇐ backprop(g, yt ) # Backpropagate gradient to module output 19: yt ⇐ update(yt , gt ) # Refine the module output 20: # Forward pass to update downstream modules 21: for k = t + 1 to T do 22: yk ⇐ M k (q; ck-1 ) 23: ck ⇐ update_cache(ck-1 , yk ) 24: end for 25: r ⇐ yT 26: end for 27: end for 28: Return r
```

## Supplementary Note 10 Related Work

One related thread of work investigated the problem of prompt optimization. Practitioners demonstrated that prompt engineering strategies such as intelligently picking few-shot examples and in-context learning, CoT, ensembles can significantly boost performance of LLMs. To automate this process, white-box methods that leverage numerical gradients or probability distributions from LLMs were developed to optimize prompts [43-47], however, these methods cannot be used with closed-source models as they require access to model parameters. Other works investigated using LLMs as prompt optimizers [48-50].

Under prompt optimization, there are three works closest to our philosophy. First, DSPy [5] pioneered the idea of viewing complex LLM-based systems as programs with potentially many layers, and proposes ways to build and optimize them in a programmatic fashion. The framework is extensive, with results improving LLM performance in various question answering, reasoning, and prompt optimization tasks. Our work takes a different perspective that backpropagation and its extensions can be a general and powerful framework to optimize the new generation of AI systems, and perform multiple tasks outside of prompt optimization. In particular, we treat not only instructions or demonstrations as variables to optimize, but also the instances we care about themselves - such as molecules, treatment plans, code snippets, and so on. Second, greatly inspiring to us, Prompt Optimization with Textual Gradients (ProTeGi) [50] defines the Textual Gradients in the context of prompt optimization, where gradients are natural language feedback from LLMs given to the mistakes made during the task. While ProTeGi is built on the textual gradient analogy, we expand this analogy more broadly to automatic differentiation, and going substantially beyond prompt optimization tasks. Third, OPRO [6] is one of the first papers to use LLMs as optimizers. OPRO uses an optimizer LLM to generate solution candidates, and uses the downstream task performance (called "score") to iteratively select and improve available candidates. Importantly, since OPRO relies on a scalar supervision signal to select and improve solution candidates, it is not possible without further innovation to use it in settings such as instance optimization, or settings with multiple components where we use backpropagation. Furthermore, the implementation of the framework depends on the task, unlike the generality of our framework where we do not make any modifications to the implementation for new tasks. Finally, both DSPy, ProTeGi, and OPRO focused on prompt optimization as the key application, while a significant advance of TextGrad, as demonstrated through our diverse applications, is in instance optimization.

More generally, there is an emerging line of work built on the high-level idea of using LLMs as critics or optimizers [2, 6, 48-53]. While many of these earlier frameworks demonstrated the utility of LLMs as optimizers, we propose a single and general framework that was tested successfully in a variety of applications. Within this framework, we can reason about optimizing chains or stacks of LLMs: we propagate natural language feedback. Similarly, once viewed as a general-purpose optimization engine, we can formulate many relevant problems instantiated as a few lines of code in our framework, such as self-refinement of solutions [2, 54].

Building on the optimization analogy, we already transferred several analogies from the traditional optimization literature such as momentum [55] through using earlier iterations in the context, use of batch optimization [56], constrained optimization [57] using natural language constraints, and so on. Our work opens up a large space to design the new generation of optimization algorithms, all within the same framework.

## Supplementary references

- [1] Brown, T., Mann, B., Ryder, N., Subbiah, M., Kaplan, J.D., Dhariwal, P., Neelakantan, A., Shyam, P., Sastry, G., Askell, A., et al.: Language models are few-shot learners. In: Advances in Neural Information Processing Systems, vol. 33, pp. 1877-1901 (2020)
- [2] Shinn, N., Cassano, F., Gopinath, A., Narasimhan, K., Yao, S.: Reflexion: language agents with verbal reinforcement learning. In: Advances in Neural Information Processing Systems, vol. 36, pp. 8634-8652 (2023)
- [3] Rein, D., Hou, B.L., Stickland, A.C., Petty, J., Pang, R.Y., Dirani, J., Michael, J., Bowman, S.R.: GPQA: A graduate-level google-proof q&amp;a benchmark. In: First Conference on Language Modeling (2023)
- [4] Lu, P., Mishra, S., Xia, T., Qiu, L., Chang, K. -W., Zhu, S. -C., Tafjord, O., Clark, P., Kalyan, A.: Learn to explain: Multimodal reasoning via thought chains for science question answering. In: Advances in Neural Information Processing Systems, vol. 35, pp. 2507-2521 (2022)
- [5] Khattab, O., Singhvi, A., Maheshwari, P., Zhang, Z., Santhanam, K., Haq, S., Sharma, A., Joshi, T.T., Moazam, H., Miller, H., et al.: DSPy: Compiling declarative language model calls into state-of-the-art pipelines. In: The Twelfth International Conference on Learning Representations (2024)
- [6] Yang, C., Wang, X., Lu, Y., Liu, H., Le, Q.V., Zhou, D., Chen, X.: Large language models as optimizers. In: The Twelfth International Conference on Learning Representations (2024)
- [7] Suzgun, M., Scales, N., Schärli, N., Gehrmann, S., Tay, Y., Chung, H.W., Chowdhery, A., Le, Q., Chi, E., Zhou, D., Wei, J.: Challenging BIG-bench tasks and whether chain-of-thought can solve them. In: Findings of the Association for Computational Linguistics: ACL 2023, pp. 13003-13051 (2023)
- [8] Wei, J., Wang, X., Schuurmans, D., Bosma, M., Xia, F., Chi, E., Le, Q.V., Zhou, D., et al.: Chain-of-thought prompting elicits reasoning in large language models. In: Advances in Neural Information Processing Systems, vol. 35, pp. 24824-24837 (2022)
- [9] Kojima, T., Gu, S.S., Reid, M., Matsuo, Y., Iwasawa, Y.: Large language models are zero-shot reasoners. In: Advances in Neural Information Processing Systems, vol. 35, pp. 22199-22213 (2022)
- [10] Cobbe, K., Kosaraju, V., Bavarian, M., Chen, M., Jun, H., Kaiser, L., Plappert, M., Tworek, J., Hilton, J., Nakano, R., Hesse, C., Schulman, J.: Training verifiers to solve math word problems. arXiv preprint arXiv:2110.14168 (2021)

- [11] Dubey, A., Jauhri, A., Pandey, A., Kadian, A., Al-Dahle, A., Letman, A., Mathur, A., Schelten, A., Yang, A., Fan, A., et al.: The llama 3 herd of models. arXiv preprint arXiv:2407.21783 (2024)
- [12] Jiang, A.Q., Sablayrolles, A., Roux, A., Mensch, A., Savary, B., Bamford, C., Chaplot, D.S., Casas, D.d.l., Hanna, E.B., Bressand, F., et al.: Mixtral of experts. arXiv preprint arXiv:2401.04088 (2024)
- [13] Yang, A., Yang, B., Hui, B., Zheng, B., Yu, B., Zhou, C., Li, C., Li, C., Liu, D., Huang, F., et al.: Qwen2 technical report. arXiv preprint arXiv:2407.10671 (2024)
- [14] Wolf, T., Debut, L., Sanh, V., Chaumond, J., Delangue, C., Moi, A., Cistac, P., Rault, T., Louf, R., Funtowicz, M., et al.: Transformers: State-of-the-art natural language processing. In: Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing: System Demonstrations, pp. 38-45 (2020)
- [15] Reid, M., Savinov, N., Teplyashin, D., Lepikhin, D., Lillicrap, T., Alayrac, J. - b., Soricut, R., Lazaridou, A., Firat, O., Schrittwieser, J., et al.: Gemini 1.5: Unlocking multimodal understanding across millions of tokens of context. arXiv preprint arXiv:2403.05530 (2024)
- [16] Xing, L., Li, J.G., Donaldson, S., Le, Q.T., Boyer, A.L.: Optimization of importance factors in inverse planning. Physics in Medicine &amp; Biology 44(10), 2525 (1999)
- [17] Wieser, H. -P., Cisternas, E., Wahl, N., Ulrich, S., Stadler, A., Mescher, H., Müller, L. -R., Klinge, T., Gabrys, H., Burigo, L., et al.: Development of the open-source dose calculation and optimization toolkit matrad. Medical Physics 44(6), 25562568 (2017)
- [18] Wang, Q., Wang, R., Liu, J., Jiang, F., Yue, H., Du, Y., Wu, H.: High-dimensional automated radiation therapy treatment planning via bayesian optimization. Medical Physics 50(6), 3773-3787 (2023)
- [19] Akiba, T., Sano, S., Yanase, T., Ohta, T., Koyama, M.: Optuna: A nextgeneration hyperparameter optimization framework. In: Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, pp. 2623-2631 (2019)
- [20] Nicolaou, C.A., Brown, N.: Multi-objective optimization methods in drug design. Drug Discovery Today: Technologies 10(3), 427-435 (2013)
- [21] Hoelder, S., Clarke, P.A., Workman, P.: Discovery of small molecule cancer drugs: successes, challenges and opportunities. Molecular Oncology 6(2), 155-176 (2012)

- [22] Kontoyianni, M.: Docking and virtual screening in drug discovery. Proteomics for Drug Discovery: Methods and Protocols, 255-266 (2017)
- [23] Agarwal, S., Mehrotra, R.: An overview of molecular docking. JSM Chemistry 4(2), 1024-1028 (2016)
- [24] Trott, O., Olson, A.J.: AutoDock Vina: improving the speed and accuracy of docking with a new scoring function, efficient optimization, and multithreading. Journal of Computational Chemistry 31(2), 455-461 (2010)
- [25] Ursu, O., Rayan, A., Goldblum, A., Oprea, T.I.: Understanding drug-likeness. Wiley Interdisciplinary Reviews: Computational Molecular Science 1(5), 760-781 (2011)
- [26] Bickerton, G.R., Paolini, G.V., Besnard, J., Muresan, S., Hopkins, A.L.: Quantifying the chemical beauty of drugs. Nature Chemistry 4(2), 90-98 (2012)
- [27] García-Ortegón, M., Simm, G.N., Tripp, A.J., Hernández-Lobato, J.M., Bender, A., Bacallado, S.: DOCKSTRING: easy molecular docking yields better benchmarks for ligand design. Journal of Chemical Information and Modeling 62(15), 3486-3502 (2022)
- [28] RDKit: Open-source cheminformatics. http://www.rdkit.org
- [29] Hughes, J.P., Rees, S., Kalindjian, S.B., Philpott, K.L.: Principles of early drug discovery. British Journal of Pharmacology 162(6), 1239-1249 (2011)
- [30] Wenlock, M.C., Austin, R.P., Barton, P., Davis, A.M., Leeson, P.D.: A comparison of physiochemical property profiles of development and marketed oral drugs. Journal of Medicinal Chemistry 46(7), 1250-1256 (2003)
- [31] Knox, C., Wilson, M., Klinger, C.M., Franklin, M., Oler, E., Wilson, A., Pon, A., Cox, J., Chin, N.E., Strawbridge, S.A., et al.: Drugbank 6.0: the drugbank knowledgebase for 2024. Nucleic Acids Research 52(D1), 1265-1275 (2024)
- [32] Berry, M., Fielding, B., Gamieldien, J.: Practical considerations in virtual screening and molecular docking. Emerging Trends in Computational Biology, Bioinformatics, and Systems Biology, 487 (2015)
- [33] Birhane, A., Kasirzadeh, A., Leslie, D., Wachter, S.: Science in the age of large language models. Nature Reviews Physics 5(5), 277-280 (2023)
- [34] Nikolova, N., Jaworska, J.: Approaches to measure chemical similarity-a review. QSAR &amp; Combinatorial Science 22(9-10), 1006-1026 (2003)
- [35] Gaulton, A., Bellis, L.J., Bento, A.P., Chambers, J., Davies, M., Hersey, A., Light, Y., McGlinchey, S., Michalovich, D., Al-Lazikani, B., et al.: ChEMBL: a largescale bioactivity database for drug discovery. Nucleic Acids Research 40(D1),

- [36] Swanson, K., Walther, P., Leitz, J., Mukherjee, S., Wu, J.C., Shivnaraine, R.V., Zou, J.: ADMET-AI: A machine learning ADMET platform for evaluation of large-scale chemical libraries. Bioinformatics 40(7), 416 (2024)
- [37] Jensen, J.H.: A graph-based genetic algorithm and generative model/monte carlo tree search for the exploration of chemical space. Chemical Science 10, 3567-3572 (2019)
- [38] Olivecrona, M., Blaschke, T., Engkvist, O., Chen, H.: Molecular de-novo design through deep reinforcement learning. Journal of Cheminformatics 9, 1-14 (2017)
- [39] Gao, W., Fu, T., Sun, J., Coley, C.: Sample efficiency matters: a benchmark for practical molecular optimization. In: Advances in Neural Information Processing Systems, vol. 35, pp. 21342-21357 (2022)
- [40] Tripp, A., Simm, G.N., Hernández-Lobato, J.M.: A fresh look at de novo molecular design benchmarks. In: NeurIPS 2021 AI for Science Workshop (2021)
- [41] Yoshikawa, N., Terayama, K., Sumita, M., Homma, T., Oono, K., Tsuda, K.: Population-based de novo molecule generation, using grammatical evolution. Chemistry Letters 47(11), 1431-1434 (2018)
- [42] AI, J.: EasyOCR (2024). https://jaided.ai/easyocr/
- [43] Shin, T., Razeghi, Y., Logan IV, R.L., Wallace, E., Singh, S.: AutoPrompt: Eliciting knowledge from language models with automatically generated prompts. In: Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP), pp. 4222-4235 (2020)
- [44] Jia, M., Tang, L., Chen, B. -C., Cardie, C., Belongie, S., Hariharan, B., Lim, S. - N.: Visual prompt tuning. In: European Conference on Computer Vision, pp. 709-727 (2022)
- [45] Li, X.L., Liang, P.: Prefix-tuning: Optimizing continuous prompts for generation. In: Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics and the 11th International Joint Conference on Natural Language Processing (Volume 1: Long Papers), pp. 4582-4597 (2021)
- [46] Chen, X., Zhang, N., Xie, X., Deng, S., Yao, Y., Tan, C., Huang, F., Si, L., Chen, H.: Knowprompt: Knowledge-aware prompt-tuning with synergistic optimization for relation extraction. In: Proceedings of the ACM Web Conference 2022, pp. 2778-2788 (2022)
- [47] Sordoni, A., Yuan, E., Côté, M. -A., Pereira, M., Trischler, A., Xiao, Z., Hosseini, A., Niedtner, F., Le Roux, N.: Joint prompt optimization of stacked llms using

- variational inference. In: Advances in Neural Information Processing Systems, vol. 36 (2024)
- [48] Zhou, Y., Muresanu, A.I., Han, Z., Paster, K., Pitis, S., Chan, H., Ba, J.: Large language models are human-level prompt engineers. In: The Eleventh International Conference on Learning Representations (2023)
- [49] Ye, Q., Ahmed, M., Pryzant, R., Khani, F.: Prompt engineering a prompt engineer. In: Findings of the Association for Computational Linguistics: ACL 2024, pp. 355-385 (2024)
- [50] Pryzant, R., Iter, D., Li, J., Lee, Y., Zhu, C., Zeng, M.: Automatic prompt optimization with "gradient descent" and beam search. In: Bouamor, H., Pino, J., Bali, K. (eds.) Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing, pp. 7957-7968 (2023)
- [51] Song, X., Tian, Y., Lange, R.T., Lee, C., Tang, Y., Chen, Y.: Position: Leverage foundational models for black-box optimization. In: Forty-first International Conference on Machine Learning (2024)
- [52] Xiao, T.Z., Bamler, R., Schölkopf, B., Liu, W.: Verbalized machine learning: Revisiting machine learning with language models. arXiv preprint arXiv:2406.04344 (2024)
- [53] Gao, Z., Du, Y., Zhang, X., Ma, X., Han, W., Zhu, S. -C., Li, Q.: Clova: A closed-loop visual assistant with tool usage and update. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pp. 1325813268 (2024)
- [54] Madaan, A., Tandon, N., Gupta, P., Hallinan, S., Gao, L., Wiegreffe, S., Alon, U., Dziri, N., Prabhumoye, S., Yang, Y., et al.: Self-refine: Iterative refinement with self-feedback. In: Advances in Neural Information Processing Systems, vol. 36 (2024)
- [55] Polyak, B.T.: Some methods of speeding up the convergence of iteration methods. USSR Computational Mathematics and Mathematical Physics 4(5), 1-17 (1964)
- [56] Robbins, H., Monro, S.: A stochastic approximation method. The Annals of Mathematical Statistics, 400-407 (1951)
- [57] Boyd, S., Boyd, S.P., Vandenberghe, L.: Convex optimization. Cambridge University Press (2004)