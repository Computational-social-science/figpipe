<!-- source: 2025-Nature-Accurate predictions on small data with a tabular foundation model_Highlights&SI.pdf -->
<!-- source_pdf: D:\2026-AI4S\REFs\2025-Nature-Accurate predictions on small data with a tabular foundation model_Highlights&SI.pdf -->
<!-- pages: 31 ; extracted_by: docling 2.140.0 -->

a protein produced abundantly in the placenta.

Importantly, the authors did not report any

transfer of LNP 55 to the fetus, which is ideal

because the fetus is an 'innocent bystander' in

pre-eclampsia and is thought not to be directly

involved in its origins.

To test the utility of LNP 55 in pregnancy, the

authors demonstrated in two mouse models

of pre-eclampsia that a single intravenous

dose of the LNP 55 formulation successfully

delivered VEGF mRNA to the placenta

without severe adverse outcomes. VEGF

mRNA lowered circulating sFlt-1 levels in the

mother, stimulated blood-vessel growth in the

placenta and prevented the maternal signs of

pre-eclampsia, including high blood pressure

and the leakage of proteins into the urine.

Restricted growth of the fetus is often

associated with pre-eclampsia. In contrast to

medications that lower blood pressure, which

are the standard of care for pre-eclampsia but

don't alleviate the effects on birth weight,

treatment with VEGF mRNA led to fetuses

that were heavier than those of mice that were

not exposed to the treatment, suggesting that

pre-eclampsia-related fetal growth restriction

is reversed by this therapeutic approach.

Swingle and colleagues have advanced the

quest to develop a safe and effective therapy

for women with pre-eclampsia. Nonetheless,

the results still raise questions. For example,

is mRNA that encodes VEGF the appropriate

cargo to transfer to the placenta? Although

previous preclinical studies in rodents have

shown that the VEGF protein can alleviate signs

of pre-eclampsia 7 , VEGF binds efficiently to the

membrane-bound receptors Flt-1 and KDR (ref.

8). Activation of KDR causes the blood-vessel

wall to become more permeable, meaning

that high doses of VEGF might be unsafe.

Furthermore, excessive VEGF in the endome-

trium, the tissue that lines the uterus, is asso-

ciated with complications such as pregnancy

loss in mice 9 . A protein related to VEGF, called

PIGF (placental growth factor), binds to Flt-1

with high affinity but does not bind to KDR,

so PIGF might be a safer alternative to VEGF 10 .

The researchers did not explore the role of

VEGF mRNA delivery in the early stages of pla-

centa formation, which is when pre-eclampsia

starts. In human pre-eclampsia, remodelling

of the spiral artery, a process that increases

blood flow to the placenta, is often impaired.

Rodents have shallow placentas so are not an

ideal model for determining whether VEGF

mRNA would reverse this impairment. Instead,

non-human primate models that have been

characterized in the past few years 11 might

be more robust than rodent models for

studying spiral-artery remodelling. Finally,

LNP 55 is delivered to the spleen as well as

the placenta. Therefore, toxicity related to

potential immune activation would need to

be assessed before studies are done in humans.

The development of interventions for pregnancy complications has sorely lagged behind advances made in therapeutics for cancer, metabolic conditions and rare diseases.

One reason is that there has been insufficient

investment from the biotechnology and

pharmaceutical industries in women's health,

and especially in pregnancy 12 . Related to this,

FDA-imposed restrictions and regulations -

which were probably instigated as a result of

the problems associated with thalidomide, a

drug marketed in the 1950s that caused severe

congenital disabilities when taken during

pregnancy - also present a barrier to entry.

Because most medications cross the barrier

between the placenta and the fetus, extensive

clinical studies are needed to assess both

short-term and long-term effects on newborn

babies. This arduous, but necessary, pathway

undoubtedly increases the cost and extends

the drug-development cycle.

Swingle et al. have introduced an innovative

method to selectively deliver therapeutic

cargo to the placenta without affecting the

fetus. Their approach offers a promising

opportunity to tackle pre-eclampsia, one of

the most common and devastating medical

complications in pregnancy, and one that is

in dire need of intervention.

Machine learning Ravi Thadhani is in the Emory University School of Medicine, Atlanta, Georgia 30322, USA. S. Ananth Karumanchi is in the Cedars- Sinai Medical Center, Los Angeles, California

90048, USA.

e-mails: ravi.thadhani@emory.edu;

sananth.karumanchi@csmc.edu

1. Thadhani, R., Cerdeira, A. S. &amp; Karumanchi, S. A. FASEB J

38, e23441 (2024).

2. Levine, R. J. et al. N. Engl. J. Med. 350, 672­-683 (2004).

3. Thadhani, R. et al. N. Engl. J. Med. Evid. 1, EVIDoa2200161

(2022).

4. Zeisler, H. et al. N. Engl. J. Med. 374, 13-22 (2016).

5. Swingle, K. L. et al. Nature 637, 412-421 (2025).

6. Han, X. et al. Nature Commun. 12, 7233 (2021).

7. Gilbert, J. S. et al. Hypertension 55, 380-385 (2010).

8. Pérez-Gutiérrez, L. &amp; Ferrara, N. Nature Rev. Mol. Cell. Biol.

24, 816-834 (2023).

9. Fan, X. et al. J. Clin. Invest. 124, 4941-4952 (2014).

10. Makris, A. et al. Hypertension 67, 1263-1272 (2016).

11. Aberdeen, G. W., Babischkin, J. S., Lindner, J. R., Pepe, G. J.

&amp; Albrecht, E. D. Endocrinology 163, bqac012 (2022).

12. Chappell, L. C. &amp; David, A. L. PLoS Med. 13, e1002161

(2016).

The authors declare competing interests;

see go.nature.com/4eym9mx for details.

This article was published online on 11 December 2024.

## The AI tool that can interpret any spreadsheet

## Duncan C. McElfresh

Artificial intelligence is already used extensively to infer outcomes from tables of data, but this typically involves creating a model for each task. A one-size-fits-all model just made the process substantially easier. See p.319

Say you run a hospital and you want to estimate which patients have the highest risk of deterioration so that your staff can prioritize their care 1 . You create a spreadsheet in which there is a row for each patient, and columns for relevant attributes, such as age or blood-oxygen level. The final column records whether the person deteriorated during their stay. You can then fit a mathematical model to these data to estimate an incoming patient's deterioration risk. This is a classic example of tabular machine learning, a technique that uses tables of data to make inferences. This usually involves developing - and training - a bespoke model for each task. On page 319, Hollmann et al. 2 report a model that can perform tabular machine learning on any data set without being trained specifically to do so.

Tabular machine learning shares a rich history with statistics and data science. Its methods are foundational to modern artificial intelligence (AI) systems, including large language models (LLMs), and its influence cannot be overstated. Indeed, many online experiences are shaped by tabular machine-learning models, which recommend products, generate advertisements and moderate social-media content 3 . Essential industries such as healthcare and finance are also steadily, if cautiously, moving towards increasing their use of AI.

Despite the field's maturity, Hollmann and colleagues' advance could be revolutionary. The authors' contribution is known as a foundation model, which is a general-purpose model that can be used in a range of settings. You might already have encountered foundation models, perhaps unknowingly, through AI tools, such as ChatGPT and Stable Diffusion.

Figure 1 | A foundation model for tabular machine learning. a, Conventional machine-learning models are trained on individual data sets using mathematical optimization algorithms. A different model needs to be developed and trained for each task, and for each data set. This practice takes years to learn and requires extensive time and computing resources. b, By contrast, a 'foundation' model could be used for any machine-learning task and is pre-trained on the types of

<!-- image -->

data used to train conventional models. This type of model simply reads a data set and can immediately produce inferences about new data points. Hollmann et al. 2 developed a foundation model for tabular machine learning, in which inferences are made on the basis of tables of data. Tabular machine learning is used for tasks as varied as social-media moderation and hospital decision-making, so the authors' advance is expected to have a profound effect in many areas.

These models enable a single tool to offer varied capabilities, including text translation and image generation. So what does a foundation model for tabular machine learning look like?

Let's return to the hospital example. With spreadsheet in hand, you choose a machine-learning model (such as a neural network) and train the model with your data, using an algorithm that adjusts the model's parameters to optimize its predictive performance (Fig. 1a). Typically, you would train several such models before selecting one to use - a labour-intensive process that requires considerable time and expertise. And of course, this process must be repeated for each unique task.

Now, imagine you have a foundation model that - after reading the spreadsheet - can immediately estimate a person's risk of deterioration (Fig. 1b). Then picture this foundation model being usable with any spreadsheet, for any tabular machine-learning task. This is similar to automated machine-learning algorithms, which automate the process of selecting and training models 4 . But, in contrast to automated machine-learning algorithms and conventional tabular machine learning, a tabular foundation model obviates the need for model training entirely. This might sound too good to be true, but this is exactly the type of foundation model that Hollmann and colleagues have built.

The authors' foundation model is called TabPFN, and it is remarkably effective. It can take a user's data set and immediately make inferences about new data points, such as a person who has just arrived at your hypothetical hospital. Using a battery of experiments, Hollmann et al. found that TabPFN consistently outperforms other machine-learning methods - automated or otherwise - for data sets with up to 10,000 rows and 500 columns. It is also more adept than other methods at coping with common data problems such as missing values, outliers and uninformative features. And whereas conventional machine-learning models require minutes or even hours to train, TabPFN can produce inferences for a new data set in fractions of a second.

Hollmann et al. had to overcome several technical barriers to make TabPFN work, and one in particular is worth highlighting. Foundation models need to be 'pre-trained' on a vast amount of data, which prepares them to recognize patterns in data that they have yet to encounter. However, there are not enough tabular data available to train a foundation model effectively. For example, LLMs such as OpenAI's GPT-4 are pre-trained on hundreds of billions of documents (if not more), using sources such as Common Crawl (see commoncrawl.org). By contrast, there are very few tabular data sets: Kaggle, one of the largest online machine-learning platforms, lists about 400,000 data sets (see kaggle.com). And not all of these are tabular.

To overcome this data scarcity, Hollmann et al. paradoxically chose to ignore real data sets entirely. Instead, they pre-trained TabPFN using 100 million randomly generated data sets that mimic the statistical properties of real data. In other words, TabPFN is not built on real data - but rather on its developers' statistical assumptions about how real data behaves. TabPFN's performance rests on the quality of their assumptions.

There are several limitations to Hollmann and colleagues' approach. First, foundation models are black boxes: users cannot interpret how the model makes inferences. Second, the current version of TabPFN might not be effective for data sets that have more than

10,000 rows and 500 columns. Finally, TabPFN is the first tool of its kind and so other limitations and - capabilities - of this strategy have yet to be discovered.

TabPFN could mark the beginning of a fundamental change for tabular machine learning. Data scientists and developers typically spend years learning the art of machine-learning model development. An effective foundation model could transform machine learning by reducing or eliminating the need to train unique models. This could allow practitioners to focus on tasks such as data preparation, model evaluation and model deployment. This might sound excessively optimistic, but recall that, in less than a decade, LLMs have catalysed a seismic shift in natural-language processing 5 . Although tabular foundation models are still in their early stages, a similar transformation for tabular machine learning might have already begun.

Duncan C. McElfresh is at Stanford Health Care, Stanford, California 94305, USA. e-mail: dmcelfre@stanford.edu

1. Hyland, S. L. et al. Nature Med. 26, 364-373 (2020).
2. Hollmann, N. et al. Nature 637, 319-326 (2025).
3. Sartor, G. &amp; Loreggia, A. The Impact of Algorithms for Online Content Filtering or Moderation - Upload Filters. (European Union, 2020).
4. Karmaker, S. K. et al. ACM Comput. Surv. 54, 175 (2022).
5. Gururaja, S. et al. Preprint at arXiv https://doi. org/10.48550/arXiv.2310.07715 (2023).

The author declares no competing interests.

## Article

## Accurate predictions on small data with a tabular foundation model

[https://doi.org/10.1038/s41586-024-08328-6](https://doi.org/10.1038/s41586-024-08328-6)

Received: 17 May 2024

Accepted: 31 October 2024

Published online: 8 January 2025

Open access

<!-- image -->

Check for updates Noah Hollmann 1,2,3,7 ✉ , Samuel Müller 1,7 ✉ , Lennart Purucker 1 , Arjun Krishnakumar 1 , Max Körfer 1 , Shi Bin Hoo 1 , Robin Tibor Schirrmeister 4,5 &amp; Frank Hutter 1,3,6 ✉

Tabular data, spreadsheets organized in rows and columns, are ubiquitous across scientific fields, from biomedicine to particle physics to economics and climate science 1,2 . The fundamental prediction task of filling in missing values of a label column based on the rest of the columns is essential for various applications as diverse as biomedical risk models, drug discovery and materials science. Although deep learning has revolutionized learning from raw data and led to numerous high-profile success stories 3-5 , gradient-boosted decision trees 6-9 have dominated tabular data for the past 20 years. Here we present the Tabular Prior-data Fitted Network (TabPFN), a tabular foundation model that outperforms all previous methods on datasets with up to 10,000 samples by a wide margin, using substantially less training time. In 2.8 s, TabPFN outperforms an ensemble of the strongest baselines tuned for 4 h in a classification setting. As a generative transformer-based foundation model, this model also allows fine-tuning, data generation, density estimation and learning reusable embeddings. TabPFN is a learning algorithm that is itself learned across millions of synthetic datasets, demonstrating the power of this approach for algorithm development. By improving modelling abilities across diverse fields, TabPFN has the potential to accelerate scientific discovery and enhance important decision-making in various domains.

Throughout the history of artificial intelligence, manually created algorithmic components have been replaced with better-performing end-to-end learned ones. Hand-designed features in computer vision, such as SIFT (Scale Invariant Feature Transform) 10 and HOG (Histogram of Oriented Gradients) 11 , have been replaced by learned convolutions; grammar-based approaches in natural language processing have been replaced by learned transformers 12 ; and the design of customized opening and end-game libraries in game playing has been superseded by end-to-end learned strategies 3,13 . Here we extend this end-to-end learning to the ubiquitous domain of tabular data.

The diversity of tabular data sets them apart from unprocessed modalities such as text and images. While in language modelling for example the meaning of a word is consistent across documents, in tabular datasets the same value can mean fundamentally different things. A drug discovery dataset, for example, might record chemical properties, whereas another dataset in materials science might document thermal and electric properties. This specialization leads to a proliferation of smaller, independent datasets and associated models. To illustrate, on the popular tabular benchmarking website openml.org, 76% of the datasets contain less than 10,000 rows at the time of writing.

Deep learning methods have traditionally struggled with tabular data, because of the heterogeneity between datasets and the heterogeneity of the raw data itself: Tables contain columns, also called features, with various scales and types (Boolean, categorical, ordinal, integer, floating point), imbalanced or missing data, unimportant features, outliers and so on. This made non-deep-learning methods, such as tree-based models, the strongest contender so far 14,15 .

However, these traditional machine learning models have several drawbacks. Without substantial modifications, they yield poor out-of-distribution predictions and poor transfer of knowledge from one dataset to another 16 . Finally, they are hard to combine with neural networks, as they do not propagate gradients.

As a remedy, we introduce TabPFN, a foundation model for smallto medium-sized tabular data. This new supervised tabular learning method can be applied to any small- to moderate-sized dataset and yields dominant performance for datasets with up to 10,000 samples and 500 features. In a single forward pass, TabPFN significantly outperforms state-of-the-art baselines on our benchmarks, including gradient-boosted decision trees, even when these are allowed 4 h of tuning, a speedup of 5,140× (classification) and 3,000× (regression). Finally, we demonstrate various foundation model characteristics of TabPFN, including fine-tuning, generative abilities and density estimation.

## Principled in-context learning

TabPFN leverages in-context learning (ICL) 17 , the same mechanism that led to the astounding performance of large language models, to

1 Machine Learning Lab, University of Freiburg, Freiburg, Germany. 2 Computational Medicine, Berlin Institute of Health at Charité, Universitätsmedizin Berlin, Berlin, Germany. 3 Prior Labs, Freiburg, Germany. 4 Neuromedical AI Lab, Department of Neurosurgery, Medical Center - University of Freiburg, Faculty of Medicine, University of Freiburg, Freiburg, Germany. 5 Medical Physics, Department of Diagnostic and Interventional Radiology, Medical Center - University of Freiburg, Faculty of Medicine, University of Freiburg, Freiburg, Germany. 6 ELLIS Institute Tübingen, Tübingen, Germany. 7 These authors contributed equally: Noah Hollmann, Samuel Müller. ✉e-mail: noah@priorlabs.ai; samuelgabrielmuller@gmail.com; fh@cs.uni-freiburg.de

## Article

Fig. 1 | Overview of the proposed method. a, The high-level overview of TabPFN pre-training and usage. b, The TabPFN architecture. We train a model to solve more than 100 million synthetic tasks. Our architecture is an adaptation of the

<!-- image -->

generate a powerful tabular prediction algorithm that is fully learned. Although ICL was first observed in large language models, recent work has shown that transformers can learn simple algorithms such as logistic regression through ICL 18-21 . Prior-data Fitted Networks (PFNs) have shown that even complex algorithms, such as Gaussian Processes and Bayesian Neural Networks, can be approximated with ICL 22 . ICL enables us to learn a wider space of possible algorithms, including cases for which a closed-form solution does not exist.

We build on a preliminary version of TabPFN 23 , which demonstrated the applicability of in-context-learning 17 for tabular data in principle but had many limitations that rendered it inapplicable in most cases. Based on a series of improvements, the new TabPFN scales to 50× larger datasets; supports regression tasks, categorical data and missing values; and is robust to unimportant features and outliers.

The key idea behind TabPFN is to generate a large corpus of synthetic tabular datasets and then train a transformer-based 12 neural network to learn to solve these synthetic prediction tasks. Although traditional approaches require hand-engineered solutions for data challenges such as missing values, our method autonomously learns effective strategies by solving synthetic tasks that include these challenges. This approach leverages ICL as a framework for exemplar-based declarative programming of algorithms. We design desired algorithmic behaviour by generating diverse synthetic datasets that demonstrate the desired behaviour and then train a model to encode an algorithm that satisfies it. This shifts the algorithm design process from writing explicit instructions to defining input-output examples, opening up possibilities for creating algorithms in various domains. Here, we apply this approach to the high-impact field of tabular learning, generating a powerful tabular prediction algorithm.

Our ICL approach differs fundamentally from standard supervised deep learning. Usually, models are trained per dataset, upd­ ating model parameters on individual samples or batches according to hand-crafted weight-updating algorithms, such as Adam 24 .

standard transformer encoder that is adapted for the two-dimensional data encountered in tables.

At inference time, the learned model is applied to test samples. By contrast, our approach is trained across datasets and is applied to entire datasets at inference time rather than individual samples. Before being applied to real-world datasets, the model is once pre-trained on millions of synthetic datasets representing different prediction tasks. At inference time, the model receives an unseen dataset with both labelled training and unlabelled test samples and performs training and prediction on this dataset in a single neural network forward pass.

Figures 1 and 2 outline our approach:

1. Data generation: we define a generative process (referred to as our prior) to synthesize diverse tabular datasets with varying relationships between features and targets, designed to capture a wide range of potential scenarios that our model might encounter. We sample millions of datasets from the generative process. For each dataset, a subset of samples has their target values masked, simulating a supervised prediction problem. Further details of our prior design are shown in the section 'Synthetic data based on causal models'.
2. Pre-training: we train a transformer model, our PFN, to predict the masked targets of all synthetic datasets, given the input features and the unmasked samples as context. This step is done only once during model development, learning a generic learning algorithm that can be used to predict any dataset.
3. Real-world prediction: the resulting trained model can now be applied to arbitrary unseen real-world datasets. The training samples are provided as context to the model, which predicts the labels of these unseen datasets through ICL.

Our approach also has a theoretical foundation as described in ref. 22. It can be viewed as approximating Bayesian prediction for a prior defined by the synthetic datasets. The trained PFN will approximate the posterior predictive distribution p( , , ) test test train train ̂ ∣ y X X y and thus return a Bayesian prediction for the specified distribution over artificial datasets used during PFN pre-training.

Fig. 2 | Overview of the TabPFN prior. a, For each dataset, we first sample high-level hyperparameters. b, Based on these hyperparameters, we construct a structural causal model that encodes the computational function generating the dataset. Each node holds a vector and each edge in the computational graph implements a function according to one of the connection types. In step 1, using random noise variables we generate initialization data, which is fed into the root nodes of the graphs and propagated through the computational graph

<!-- image -->

for each to-be-generated sample. In step 2, we randomly sample feature and target node positions in the graph, labelled F and T, respectively. In step 3, we extract the intermediate data representations at the sampled feature and target node positions. In step 4, we post-process the extracted data. c, We retrieve the final datasets. We plot interactions of feature pairs and the node colour represents the class of the sample.

## An architecture designed for tables

The transformer architecture is currently the favoured architecture for flexible deep learning and foundation models 4,5 . Transformer models work on sequences and combine information between sequence items using so-called attention mechanisms 25 , allowing them to effectively capture long-range dependencies and learn complex relationships in data. Although transformer-based models can be applied to tabular data 26,27 , TabPFN addresses two key limitations inherent to them. First, as transformers are designed for sequences, they treat the input data as a single sequence, not using the tabular structure. Second, machine learning models are often used in a fit-predict model, in which a model is fitted on the training set once and then reused for multiple test datasets. Transformer-based ICL algorithms, however, receive train and test data in a single pass and thus perform training and prediction at once. Thus, when a fitted model is reused, it has to redo computations for the training set.

To better use the tabular structure, we propose an architecture that assigns a separate representation to each cell in the table, inspired by refs. 22,28. Our architecture, visualized in Fig. 1b, uses a two-way attention mechanism, with each cell attending to the other features in its row (that is, its sample) and then attending to the same feature across its column (that is, all other samples). This design enables the architecture to be invariant to the order of both samples and features and enables more efficient training and extrapolation to larger tables than those encountered during training, in terms of both the number of samples and features.

To mitigate repeating computations on the training set for each test sample in a fit-predict setting, our model can separate the inference on the training and test samples. This allows us to perform ICL on the training set once, save the resulting state and reuse it for multiple test set inferences. On datasets with 10,000 training samples and 10 features, our optimized train-state caching results in inference speedups of around 300× on CPU (from 32 s to 0.1 s) and 6× on GPU. With 10× more features (100), the speedups increase to 800× on CPU and 30× speedup on GPU. These measurements focus solely on the core inference process, excluding pre-processing and ensembling steps detailed in the section 'Inference details'. The lower speedups on GPUs are because of an underutilization of their massively parallel architecture.

We further optimize the memory and compute requirements of the architecture by computing layer norms in half-precision, using flash attention 29 , activation checkpointing and sequential computation of the state. Our optimizations reduce the memory requirements by a factor of four, resulting in less than 1,000 bytes per cell. This enables the prediction on datasets with up to 50 million cells (for example, 5 million rows × 10 features) on a single H100 GPU.

For regression tasks, we use a piece-wise constant output distribution, following refs. 22,30, which allows our models to predict a probability distribution of target values instead of a single value, including, for example, bimodal distributions.

## Synthetic data based on causal models

The performance of TabPFN relies on generating suitable synthetic training datasets that capture the characteristics and challenges of real-world tabular data. To generate such datasets, we developed an approach based on structural causal models (SCMs) 31 . SCMs provide a formal framework for representing causal relationships and generative processes underlying the data. By relying on synthetic data instead of large collections of public tabular data, we avoid common problems of foundational models, such as privacy and copyright infringements, contaminating our training data with test data 32 or limited data availability.

As shown in Fig. 2, our generative pipeline first samples high-level hyperparameters, such as dataset size, number of features and difficulty level, to govern the overall properties of each synthetic dataset.

## Article

Fig. 3 | The behaviour of TabPFN and a set of baselines on simple functions. In all plots, we use orange for the ground truth and blue for model predictions. a, Each column represents a different toy function, each having a single feature (along the x-axis) and a target (along the y-axis). TabPFN can model a lot of

<!-- image -->

different functions, including noisy functions. b, TabPFN can model distributions over outputs out of the box, which is exemplified by predicting the light intensity pattern in a double-slit experiment after observing the positions of 1,000 photons.

Guided by these hyperparameters, we construct a directed acyclic graph specifying the causal structure underlying the dataset.

To generate each sample within a dataset, we propagate randomly generated noise, called our initialization data, through the root nodes of the causal graph. This initialization data are generated by sampling from a random normal or uniform distribution with varying degrees of non-independence between samples, see section 'Initialization data sampling'. As these data traverse the edges of the computational graph, we apply a diverse set of computational mappings: small neural networks with linear or nonlinear activations (for example, sigmoid, ReLU (rectified linear unit), modulo, sine), discretization mechanisms for generating categorical features and decision tree structures to encode local, rule-based dependencies. At each edge, we add Gaussian noise, introducing uncertainty into the generated data. We save the intermediate data representations at each node to be retrieved later. See section 'Computational edge mappings' for details.

After traversing the causal graph, we extract the intermediate representations at the sampled feature and target nodes, yielding a sample consisting of feature values and an associated target value.

By incorporating various data challenges and complexities into the synthetic datasets, we create a training ground that allows TabPFN to develop strategies for handling similar issues in real-world datasets. For instance, consider the case of missing values, commonly present in tabular data. By exposing TabPFN to synthetic datasets with varying patterns and fractions of missing values in our synthetic data generation process, the model learns effective ways of handling missing values that generalize to real-world datasets. We apply post-processing techniques to further enhance the realism and challenge the robustness of the learned prediction algorithms. This includes warping with the Kumaraswamy distribution 33 , introducing complex nonlinear distortions and quantization mimicking discretized features. See section 'Post-processing' for details.

Through this generative process, we created a massive corpus of around 100 million synthetic datasets per model training, each with a unique causal structure, feature types and functional characteristics.

## Qualitative analysis

We first analyse the behaviour of TabPFN on toy problems to build intuition and disentangle the impact of various dataset characteristics. As regression problems are easier to visualize, we focus on these in our qualitative analysis. In Fig. 3a, we compare TabPFN with a diverse set of standard predictors, with all methods using default settings.

Linear (ridge) regression can naturally model only linear functions, leading to simple and interpretable predictions but catastrophic failure on many of the toy functions. Multilayer perceptrons (MLPs) 34 perform worse on datasets with highly non-smooth patterns 14 . This is especially apparent for the step function. TabPFN, by contrast, models either function type, smooth or non-smooth, out of the box. This includes a good approximation to step functions despite TabPFN being a neural network. CatBoost 9 , representative of tree-based methods, fits only piece-wise constant functions. Although this leads to approximation errors and unintuitive predictions, it avoids catastrophic failures.

The main advantage of TabPFN over all baselines is its inherent ability to model uncertainty at no extra cost. Whereas classical regression methods output a single real-valued prediction, TabPFN returns a target distribution, capturing the uncertainty of predictions. These uncertainty modelling abilities of TabPFN extend beyond simple distributions and can handle complex, multi-modal distributions. Figure 3b shows this by modelling the density of light reaching a detector screen in a double-slit experiment 35 for different slit distances and widths. In this classic experiment, photons are sent through two slits creating a multi-modal intensity pattern because of the wave-like interference behaviour of light. TabPFN predicts these intricate patterns in just a single forward pass, requiring only 1.2 s. By contrast, traditional methods such as CatBoost require training multiple quantile models at different quantiles and reconstructing the distribution from these predictions. Even after tuning CatBoost specifically for this task, it produced substantially worse predictions compared with TabPFN, see Fig. 3b. With default settings, CatBoost requires 169.3 s and yields further deteriorated results. Qualitatively, we observe that TabPFN is more accurate in predicting very low densities and has fewer artefacts compared with CatBoost.

Fig. 4 | Comparison of TabPFN on our test benchmarks, containing datasets with up to 10,000 samples and 500 features. Performance was normalized per dataset before aggregation using all baselines; intervals represent the 95% confidence interval. Wilcoxon P refers to the two-sided Wilcoxon signed-rank test P value 54 . a, Average performance of the default as well as the tuned versions of TabPFN and our baselines. All methods are tuned for ROC AUC or RMSE, respectively, thus decreasing the representativeness of the secondary metrics. LGBM, LightGBM; MLP, multilayer perceptron; SVM, support vector machines;

<!-- image -->

RF, random forest; CB, CatBoost; XGB, XGBoost; Lin, logistic regression for classification and ridge regression for regression tasks. Plots on the right-hand side show a magnified analysis of the strongest baselines considered. b, A perdataset comparison of TabPFN with its strongest baseline, CatBoost. Each dot is the average score on one dataset. c, The impact of hyperparameter tuning for the considered methods. The x-axis shows the average time required to fit and predict with the algorithm.

## Quantitative analysis

We quantitatively evaluate TabPFN on two dataset collections: the AutoML Benchmark 36 and OpenML-CTR23 37 . These benchmarks comprise diverse real-world tabular datasets, curated for complexity, relevance and domain diversity. From these benchmarks, we use the 29 classification datasets and 28 regression datasets that have up to 10,000 samples, 500 features and 10 classes. We further evaluated additional benchmark suites from refs. 14,15, as well as five Kaggle competitions from the Tabular Playground Series.

We compared TabPFN against state-of-the-art baselines, including tree-based methods (random forest 38 , XGBoost (XGB) 7 , CatBoost 9 , LightGBM 8 ), linear models, support vector machines (SVMs) 39 and MLPs 34 .

Evaluation metrics include ROC AUC (area under the receiver operating characteristic curve; One-vs-Rest) and accuracy for classification, and R 2 (coefficient of determination) and negative RMSE (root mean squared error) for regression. Scores were normalized per dataset, with 1.0 representing the best and 0.0 the worst performance with respect to all baselines.

For each dataset and method, we ran 10 repetitions with different random seeds and train-test splits (90% train, 10% test). We tuned hyperparameters using random search with five-fold cross-validation, with time budgets ranging from 30 s to 4 h. All methods were evaluated using eight CPU cores, with TabPFN additionally using a consumer-grade GPU (RTX 2080 Ti; other methods did not benefit from this, see Extended Data Fig. 2d). TabPFN was pre-trained once using eight NVIDIA RTX 2080 GPUs over 2 weeks, allowing for ICL on all new datasets in a single forward pass. These modest computational requirements make similar research accessible to academic labs. For details, refer to the section 'Detailed evaluation protocol'.

## Comparison with state-of-the-art baselines

Figure 4a demonstrates the strong out-of-the-box performance of TabPFN compared with tuned and default configurations of XGBoost, CatBoost and a random forest. For classification tasks, TabPFN surpasses CatBoost, the strongest default baseline, by 0.187 (0.939 compared with 0.752) in normalized ROC AUC in the default setting and by 0.13 (0.952 compared with 0.822) in the tuned setting. For regression, TabPFN outperforms CatBoost in normalized RMSE by 0.051 (0.923 compared with 0.872) in the default setting and by 0.093 (0.968 compared with 0.875) in the tuned setting. In Fig. 4b, we show per-dataset comparisons. Although for some datasets CatBoost outperforms TabPFN, TabPFN wins on most of the datasets.

Figure 4c shows how the performance of TabPFN and the baselines improve with more time spent on hyperparameter search. The default of TabPFN, taking 2.8 s on average for classification and 4.8 s for regression, outperforms all baselines, even when tuning them for 4 h-a speedup of 5,140× and 3,000×, respectively. We show comparisons on a larger number of metrics in Extended Data Tables 1 and 2.

As shown in Extended Data Fig. 2, similar to our primary benchmarks, TabPFN substantially outperformed all baselines on the benchmarks of refs. 14,15. The benchmark of ref. 14 is particularly noteworthy because on this benchmark, tree-based methods were previously found to excel. Moreover, we show in Extended Data Table 6 that default TabPFN outperforms default CatBoost on all five Kaggle competitions with less than 10,000 training samples from the latest completed Tabular Playground Series.

## Evaluating diverse data attributes

In Fig. 5a,b, we show the robustness of TabPFN to dataset characteristics that are traditionally hard to handle for neural-network-based approaches 14,23 .

Figure 5a provides an analysis of the performance of TabPFN across various dataset types. First, we add uninformative features (randomly

## Article

Fig. 5 | Robustness across datasets and performance comparison with tuned ensembles. a, A comparison of modified datasets. We can see that TabPFN is not more vulnerable to the modifications compared with baselines. We also see that TabPFN reproduces the accuracy of CatBoost (default) with only half the training samples provided. Here we normalize scores per dataset (sharing one normalization across all modifications of one experiment) to avoid negative outliers. b, We split the test datasets by data characteristics and

<!-- image -->

analyse the performance per subgroup. c, Classification performance. Left, the win rate of TabPFN (PHE) against AutoGluon (with one tie excluded); right, the ROC AUC score over time for tuning each method, with the first marker representing the default configuration for the non-ensembling methods. d, Regression performance presented as in c but using the RMSE metric. Intervals represent the 95% confidence interval and Wilcoxon P refers to the two-sided Wilcoxon signed-rank test P value 54 .

shuffled features from the original dataset) and outliers (multiply each cell with 2% probability with a random number between 0 and the outlier factor). The results show that TabPFN is very robust to uninformative features and outliers, something typically hard for neural networks, as can be seen with the MLP baseline. Second, although dropping either samples or features hurts the performance of all methods, with half the samples TabPFN still performs as well as the next best method using all samples.

In Fig. 5b, we split our test datasets into subgroups and perform analyses per subgroup. We create subgroups based on the presence of categorical features, missing values, number of samples and number of features in the datasets. The sample- and feature-number subgroups are split such that a third of the datasets fall into each group. We can see that none of these characteristics strongly affect the performance of TabPFN relative to the other methods. However, we note that these results should not be taken as evidence that TabPFN scales well beyond the 10,000 samples and 500 features considered here. We show four further ablations in Extended Data Fig. 1.

## Comparison with tuned ensemble methods

We compare the performance of TabPFN with AutoGluon 1.0 (ref. 40), which combines various machine learning models, including our baselines, into a stacked ensemble 41 , tunes their hyperparameters and then generates the final predictions using post hoc ensembling (PHE) 42,43 . It thus represents a different class of methods compared with individual baselines.

To assess whether TabPFN can also be improved by a tuned ensemble approach, we introduce TabPFN (PHE). TabPFN (PHE) automatically combines only TabPFN models with PHE and tunes their hyperparameters using a random portfolio from our search space. We detail this approach in the section 'TabPFN (PHE)'.

Figure 5c-d compares the performance of TabPFN, TabPFN (PHE), AutoGluon and CatBoost. For TabPFN (PHE) and AutoGluon, we start with a minimal budget of 300 s for tuning because AutoGluon otherwise does not reliably return results. In just 2.8 s, TabPFN (default) outperforms AutoGluon for classification tasks, even if AutoGluon is allowed up to 4 h, a 5.140× speedup. TabPFN (PHE) further improves performance leading to an average normalized ROC AUC score of 0.971, compared with 0.939 for TabPFN (default) and 0.914 for AutoGluon. For regression tasks, tuning hyperparameters is more important. Here, TabPFN (PHE) outperforms AutoGluon (allowed 4 h) after its minimal tuning budget of 300 s, a 48× speedup.

## Foundation model with interpretability

Apart from its strong predictive performance, TabPFN exhibits key foundation model abilities, such as data generation, density estimation, learning reusable embeddings and fine-tuning. We showcase these abilities through proof-of-concept experiments on the German Credit Dataset 44 , which contains credit risk information and the mfeat-factors 45 dataset classifying handwritten digits based on a tabular representation.

TabPFN can estimate the probability density function of numerical features, as shown in Fig. 6a, and the probability mass function of categorical features. Computing the sample densities enables anomaly detection to identify issues such as fraud, equipment failures, medical emergencies or low-quality data.

TabPFN also allows synthesizing new tabular data samples that mimic real-world dataset characteristics as shown in Fig. 6b. This enables applications such as data augmentation or privacy-preserving data sharing 46 .

The architecture of TabPFN yields meaningful feature representations that can be reused for downstream tasks such as data imputation and clustering. We extract and visualize learned embeddings from the mfeat-factors dataset in Fig. 6c, showing improved class separation compared with the raw data on the first two principal components.

Fig. 6 | Showcase of the application of TabPFN as tabular foundation model. a,b, On the German Credit Dataset, we perform data density estimation (a) and generation of new synthetic samples (b). c, We show our learned embeddings are useful representations of each sample on the handwritten digits dataset

<!-- image -->

(mfeat-factors) with different classes forming different clusters. d, We demonstrate fine-tuning TabPFN for a specific set of tasks. Fine-tuned on a dataset containing various sine curves (top), we see the model makes more accurate predictions on another sine curve dataset.

Furthermore, we demonstrate the ability of TabPFN to improve performance through fine-tuning on related datasets. Unlike tree-based methods, the neural architecture of TabPFN enables fine-tuning on specific dataset classes. We conduct proof-of-concept experiments using sine curve datasets with varying offsets between fine-tuning and test data. Figure 6d shows an example fine-tuning result. Our analysis across 50 runs (Extended Data Fig. 4) shows that TabPFN successfully transfers knowledge even when labels differ significantly between fine-tuning and test tasks, with performance improving as distributions become more similar. This could, for example, enable fine-tuning for a range of datasets from medical studies to obtain an improved general model for medical diagnosis tasks. For details, refer to section 'Foundation model abilities'.

Finally, we have developed a methodology to easily interpret the predictions of TabPFN. Interpretability is crucial for building trust and accountability when deploying models in high-stakes domains. We support the computation of feature importance through SHAP 47 (Shapley Additive Explanations), a game-theoretic approach to explain predictions. SHAP values represent the contribution of each feature to the output of the model. Extended Data Fig. 3 compares the feature importance and impact for logistic regression, CatBoost and TabPFN. TabPFN achieves high accuracy while learning simple, interpretable feature relationships. By contrast, logistic regression is interpretable but less accurate, whereas CatBoost is accurate but qualitatively less interpretable because of complex, non-smooth decision boundaries.

## Conclusion

TabPFN represents a major change in tabular data modelling, leveraging ICL to autonomously discover a highly efficient algorithm that outperforms traditional human-designed approaches on datasets with up to 10,000 samples and 500 features. This shift towards foundation models trained on synthetic data opens up new possibilities for tabular data analysis across various domains.

Potential future directions include scaling to larger datasets 48 , handling data drift 49 , investigating fine-tuning abilities across related tabular tasks 50 and understanding the theoretical foundations of our approach 51 . Future work could also explore creating specialized priors to handle data types such as time series 52 and multi-modal data, or specialized modalities such as ECG, neuroimaging data 53 and genetic data. As the field of tabular data modelling continues to evolve, we believe that foundation models, such as TabPFN, will play a key part in empowering researchers. To facilitate the widespread use of TabPFN, in the section 'User guide' we discuss how to use it effectively.

## Online content

Any methods, additional references, Nature Portfolio reporting summaries, source data, extended data, supplementary information, acknowledgements, peer review information; details of author contributions and competing interests; and statements of data and code availability are available at https://doi.org/10.1038/s41586-024-08328-6.

1. Borisov, V. et al. Deep neural networks and tabular data: a survey. IEEE Trans. Neural Netw. Learn. Syst. 35, 7499-7519 (2024).
2. van Breugel, B. &amp; van der Schaar, M. Position: why tabular foundation models should be a research priority. In Proc. 41st International Conference on Machine Learning 48976-48993 (PMLR, 2024).
3. Silver, D. et al. Mastering the game of go with deep neural networks and tree search. Nature 529, 484-489 (2016).
4. Jumper, J. M. et al. Highly accurate protein structure prediction with AlphaFold. Nature 596, 583 - 589 (2021).
5. OpenAI. GPT-4 Technical Report. Preprint at https://arxiv.org/abs/2303.08774 (2023).
6. Friedman, J. H. Greedy function approximation: a gradient boosting machine. Ann. Stat. 1189-1232 (2001).
7. Chen, T. &amp; Guestrin, C. Xgboost: A scalable tree boosting system. In Proc. 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (eds Krishnapuram, B. et al.) 785-794 (ACM Press, 2016).
8. Ke, G. et al. Lightgbm: A highly efficient gradient boosting decision tree. In Proc. 30th International Conference on Advances in Neural Information Processing Systems (eds Guyon, I. et al.) 3149-3157 (Curran Associates, 2017).
9. Prokhorenkova, L., Gusev, G., Vorobev, A., Dorogush, A. &amp; Gulin, A. CatBoost: unbiased boosting with categorical features. In Proc. 30th International Conference on Advances in Neural Information Processing Systems (eds Bengio, S. et al.) 6639-6649 (Curran Associates, 2018).
10. Lowe, D. G. Distinctive image features from scale-invariant keypoints. Int. J. Comput. Vis. 60, 91-110 (2004).
11. Dalal, N. &amp; Triggs, B. Histograms of oriented gradients for human detection. In Proc. 2005 IEEE Computer Society Conference on Computer Vision and Pattern Recognition (CVPR'05) 886-893 (IEEE, 2005).
12. Vaswani, A. et al. Attention is all you need. In Proc. 30th International Conference on Advances in Neural Information Processing Systems (eds Guyon, I. et al.) 6000-6010 (Curran Associates, 2017).
13. Silver, D. et al. Mastering the game of go without human knowledge. Nature 550, 354-359 (2017).
14. Grinsztajn, L., Oyallon, E. &amp; Varoquaux, G. Why do tree-based models still outperform deep learning on typical tabular data? In Proc. 36th International Conference on Neural Information Processing Systems Vol. 35, 507-520 (ACM, 2022).
15. McElfresh, D. et al. When do neural nets outperform boosted trees on tabular data? In Proc. 37th International Conference on Neural Information Processing System Vol. 36, 76336-76369 (ACM, 2024).
16. Goodfellow, I., Bengio, Y. &amp; Courville, A. Deep Learning (MIT Press, 2016).
17. Brown, T. et al. Language models are few-shot learners. In Proc. Advances in Neural Information Processing Systems (eds Larochelle, H. et al.) Vol. 33, 1877-1901 (Curran Associates, 2020).
18. Garg, S., Tsipras, D., Liang, P. S. &amp; Valiant, G. What can transformers learn in-context? A case study of simple function classes. In Proc. Advances in Neural Information Processing Systems Vol. 35, 30583-30598 (ACM, 2022).

## Article

19. Akyürek, E., Schuurmans, D., Andreas, J., Ma, T. &amp; Zhou, D. What learning algorithm is in-context learning? Investigations with linear models. In Proc. The Eleventh International Conference on Learning Representations (ICLR, 2023).
20. Von Oswald, J. et al. Transformers learn in-context by gradient descent. In Proc. 40th International Conference on Machine Learning 35151-35174 (PMLR, 2023).
21. Zhou, H. et al. What algorithms can transformers learn? A study in length generalization. In Proc. The Twelfth International Conference on Learning Representations (ICLR, 2024).
22. Müller, S., Hollmann, N., Pineda-Arango, S., Grabocka, J. &amp; Hutter, F. Transformers can do Bayesian inference. In Proc. The Tenth International Conference on Learning Representations (ICLR, 2022).
23. Hollmann, N., Müller, S., Eggensperger, K. &amp; Hutter, F. TabPFN: a transformer that solves small tabular classification problems in a second. In Proc. The Eleventh International Conference on Learning Representations (ICLR, 2023).
24. Kingma, D. &amp; Ba, J. Adam: A method for stochastic optimization. In Proc. International Conference on Learning Representations (ICLR, 2015).
25. Bahdanau, D., Cho, K. &amp; Bengio, Y. Neural machine translation by jointly learning to align and translate. In Proc. 3rd International Conference on Learning Representations (eds Bengio, Y. &amp; LeCun, Y.) (ICLR, 2015).
26. Gorishniy, Y., Rubachev, I., Khrulkov, V. &amp; Babenko, A. Revisiting deep learning models for tabular data. In Proc. Advances in Neural Information Processing Systems 34 (eds Ranzato, M. et al.) 18932-18943 (NeurIPS, 2021).
27. Zhu, B. et al. XTab: cross-table pretraining for tabular transformers. In Proc. 40th International Conference on Machine Learning (eds Krause, A. et al.) 43181-43204 (PMLR, 2023).
28. Lorch, L., Sussex, S., Rothfuss, J., Krause, A. &amp; Schölkopf, B. Amortized inference for causal structure learning. In Proc. Advances in Neural Information Processing Systems (eds Koyejo, S. et al.) Vol. 35, 13104-13118 (ACM, 2022).
29. Dao, T., Fu, D., Ermon, S., Rudra, A. &amp; Ré, C. Flashattention: fast and memory-efficient exact attention with io-awareness. In Proc. Advances in Neural Information Processing Systems (eds Koyejo, S. et al.) Vol. 35, 16344-16359 (2022).
30. Torgo, L. &amp; Gama, J. Regression using classification algorithms. Intell. Data Anal. 1, 275-292 (1997).
31. Pearl, J. Causality 2nd edn (Cambridge Univ. Press, 2009).
32. Jiang, M. et al. Investigating Data Contamination for Pre-training Language Models. Preprint at https://arxiv.org/abs/2401.06059 (2024).
33. Kumaraswamy, P. A generalized probability density function for double-bounded random processes. J. Hydrol. 46, 79-88 (1980).
34. Rosenblatt, F. Principles of Neurodynamics: Perceptrons and the Theory of Brain Mechanisms. Report No. 1196-0-8 (Cornell Aeronautical Lab, 1961).
35. Young, T. I. The bakerian lecture. experiments and calculations relative to physical optics. Philos. Trans. R. Soc. Lond. 94, 1-16 (1804).
36. Gijsbers, P. et al. AMLB: an AutoML benchmark. J. Mach. Learn. Res. 25, 1-65 (2024).
37. Fischer, S. F., Feurer, M. &amp; Bischl, B. OpenML-CTR23 - a curated tabular regression benchmarking suite. In Proc. AutoML Conference 2023 (Workshop) (AutoML, 2023).
38. Breimann, L. Random forests. Mach. Learn. 45, 5-32 (2001).
39. Cortes, C. &amp; Vapnik, V. Support-vector networks. Mach. Learn. 20, 273-297 (1995).
40. Erickson, N. et al. Autogluon-tabular: robust and accurate automl for structured data. Preprint at https://arxiv.org/abs/2003.06505 (2020).
41. Wolpert, D. Stacked generalization. Neural Netw. 5, 241-259 (1992).
42. Caruana, R., Niculescu-Mizil, A., Crew, G. &amp; Ksikes, A. Ensemble selection from libraries of models. In Proc. 21st International Conference on Machine Learning (ed. Greiner, R.) (Omnipress, 2004).
43. Purucker, L. O. et al. Q(D)O-ES: Population-based quality (diversity) optimisation for post hoc ensemble selection in AutoML. In Proc. International Conference on Automated Machine Learning Vol. 224 (PMLR, 2023).
44. Hofmann, H. Statlog (German Credit Data). UCI Machine Learning Repository https://doi. org/10.24432/C5NC77 (1994).
45. Duin, R. Multiple Features. UCI Machine Learning Repository https://doi.org/10.24432/ C5HC70 (1998).
46. Rajotte, J.-F. et al. Synthetic data as an enabler for machine learning applications in medicine. iScience 25, 105331 (2022).
47. Lundberg, S. M. &amp; Lee, S.-I. A unified approach to interpreting model predictions. In Proc. Advances in Neural Information Processing Systems (eds Guyon, I. et al.) Vol. 30, 4765-4774 (Curran Associates, 2017).
48. Feuer, B. et al. TuneTables: context optimization for scalable prior-data fitted networks. In Proc. 38th Conference on Neural Information Processing Systems (NeurIPS, 2024).
49. Helli, K., Schnurr, D., Hollmann, N., Müller, S. &amp; Hutter, F. Drift-resilient tabPFN: In-context learning temporal distribution shifts on tabular data. In Proc. 38th Conference on Neural Information Processing Systems (NeurIPS, 2024).
50. Thomas, V. et al. Retrieval &amp; fine-tuning for in-context tabular models. In Proc. 1st Workshop on In-Context Learning at the 41st International Conference on Machine Learning (ICML, 2024).
51. Nagler, T. Statistical foundations of prior-data fitted networks. In Proc. 40th International Conference on Machine Learning (eds Krause, A. et al.) Vol. 202, 25660-25676 (PMLR, 2023).
52. Dooley, S., Khurana, G. S., Mohapatra, C., Naidu, S. V. &amp; White, C. ForecastPFN: syntheticallytrained zero-shot forecasting. In Proc. 37th Conference on Advances in Neural Information Processing Systems (eds Oh, A. et al.) (NeurIPS, 2023).
53. Czolbe, S. &amp; Dalca, A. V. Neuralizer: General neuroimage analysis without re-training. In Proc. IEEE/CVF Conference on Computer Vision and Pattern Recognition 6217-6230 (IEEE, 2023).
54. Wilcoxon, F. in Breakthroughs in Statistics: Methodology and Distribution (eds Kotz, S. &amp; Johnson, N. L.) 196-202 (Springer, 1992).

Publisher's note Springer Nature remains neutral with regard to jurisdictional claims in published maps and institutional affiliations.

<!-- image -->

Open Access This article is licensed under a Creative Commons Attribution 4.0 International License, which permits use, sharing, adaptation, distribution and reproduction in any medium or format, as long as you give appropriate

credit to the original author(s) and the source, provide a link to the Creative Commons licence, and indicate if changes were made. The images or other third party material in this article are included in the article's Creative Commons licence, unless indicated otherwise in a credit line to the material. If material is not included in the article's Creative Commons licence and your intended use is not permitted by statutory regulation or exceeds the permitted use, you will need to obtain permission directly from the copyright holder. To view a copy of this licence, visit http://creativecommons.org/licenses/by/4.0/.

- © The Author(s) 2025

## Methods

## User guide

When to use TabPFN. TabPFN excels in handling small- to medium-sized datasets with up to 10,000 samples and 500 features (Fig. 4 and Extended Data Table 1). For larger datasets and highly non-smooth regression datasets, approaches such as CatBoost 9 , XGB 7 or AutoGluon 40 are likely to outperform TabPFN.

Although TabPFN provides a powerful drop-in replacement for traditional tabular data models such as CatBoost, similar to these models, it is intended to be only one component in the toolkit of a data scientist. Achieving top performance on real-world problems often requires domain expertise and the ingenuity of data scientists. As for other modelling approaches, data scientists should continue to apply their skills and insights in feature engineering, data cleaning and problem framing to get the most out of TabPFN. We hope that the training speed of TabPFN will facilitate faster iterations in the data science workflow.

Limitations of TabPFN. The limitations of TabPFN are as follows: (1) the inference speed of TabPFN may be slower than highly optimized approaches such as CatBoost; (2) the memory usage of TabPFN scales linearly with dataset size, which can be prohibitive for very large datasets; and (3) our evaluation focused on datasets with up to 10,000 samples and 500 features; scalability to larger datasets requires further study.

Computational and time requirements. TabPFN is computationally efficient and can run on consumer hardware for most datasets. However, training on a new dataset is recommended to run on a (consumer) GPU as this speeds it up by one to three orders of magnitude. Although TabPFN is very fast to train, it is not optimized for real-time inference tasks. For a dataset with 10,000 rows and 10 columns, our model requires 0.2 s (0.6 s without GPU) to perform a prediction for one sample, whereas CatBoost (default) can do the same in 0.0002 s. In ref. 55, further optimizing TabPFN specifically for inference tasks has already been explored, resulting in four times faster inference performance compared with even XGBoost, but so far also reducing predictive quality. Refer to the section 'Details on the neural architecture' for details on the memory usage and runtime complexity of TabPFN.

Data preparation. TabPFN can handle raw data with minimal preprocessing. If we simply provide the data in a tabular format (NumPy matrix), TabPFN will automatically handle missing values, encode categorical variables and normalize features. Although TabPFN works well out of the box, we can further improve the performance using dataset-specific pre-processing. This can also be partly done automatically with our PHE technique or manually by modifying the default settings. When manually pre-processing data, we should keep in mind that the neural network of TabPFN expects roughly normally distributed features and targets after all pre-processing steps. If we, for example, know that a feature follows a log distribution, it might help to exponentiate it before feeding it to TabPFN. As TabPFN does z-normalization of all inputs, scaling does not affect the predictions. As for all algorithms, however, using domain knowledge to combine or remove features can increase performance.

Hyperparameter tuning. TabPFN provides strong performance out of the box without extensive hyperparameter tuning (see section 'Comparison with state-of-the-art baselines'). If we have additional computational resources, we can further optimize the performance of TabPFN using hyperparameter optimization (HPO) or the PHE technique described in the section 'TabPFN (PHE)'. Our implementation directly provides HPO with random search and PHE.

## Details on the neural architecture

Our architecture is a variation of the original transformer encoder 12 and the original PFN architecture 22 , but it treats each cell in the table as a separate time position, similar to that in ref. 28. Therefore, it can generalize to more training samples as well as features than seen during training.

Figure 1b details our new architecture. All features that go into our architecture are first mapped to floating point values, that is, categoricals are transformed to integers. These values are subjected to z-normalization using the mean and standard deviation for each feature separately across the whole training set. These values are now encoded with simple linear encoders. Each layer first has an attention over features, followed by an attention over samples, both of which operate separately on each column or row, respectively. These two sub-layers are followed by an MLP sublayer. Each sublayer is followed by a residual addition and a half-precision layer norm.

We found that encoding groups of features can be even more effective compared with encoding one value per representation. For our hyperparameter search space, we selected six architectures for classification and five for regression. In three of the six classification models and four of the five regression models, including the TabPFN default, a transformer position encodes two features of one example; in others, it represents one value.

Although the inter-feature attention is a classical fully connected attention, our inter-sample attention does not allow the test samples to attend to each other but only to the training data. Therefore, we make sure that the test samples do not influence each other or the training set representations. To allow our model to differentiate features more easily that have the same statistics, for example, two features that have the same entries just in different orders, we use random feature embeddings that we add to all embeddings before the first layer. We generate one embedding per feature by projecting a random vector of one-fourth the size of our embeddings through a learned linear layer and add this to all embeddings representing an instance of that feature.

As the representations of training samples are not influenced by the test set, we cache the keys and values of the training samples to allow splitting training and inference. We use a special variant of multi-query attention for our inter-sample attention from test samples 56 to save memory when caching representations. In our variant, we use all keys and values for the attention between samples of the training set, but repeatedly use the first key and value for attention from the test samples. This allows caching only one key or value vector pair per cell in the training set that is fed into our inter-sample attention of new test samples.

The compute requirements of this architecture scale quadratically with the number of samples (n) and the number of features (m), that is O(n 2 + m 2 ), and the memory requirements scale linearly in the dataset size, O(n ⋅ m).

Finally, we found that pre-processing inputs can help performance, thus we can perform z-normalization of all inputs across the sample dimension and add an extra input for each cell that indicates whether the input was missing; the input itself is set to 0 in these cases. All inputs are finally linearly encoded into the embedding dimension of TabPFN.

## Details on the causal generative process

An SCM ≔ G Z ϵ ( , ) consists of a collection Z ≔ (z1, …, zk) of structural assignments (called mechanisms): z f z ϵ = ( , ), i i i i PA ( ) G where G i PA ( ) is the set of parents of node i (its direct causes) in the underlying directed acyclic graph (DAG) G (the causal graph), fi is a (potentially nonlinear) deterministic function and ϵi is a noise variable. Causal relationships in G are represented by edges pointing from causes to effects 31 . As our prior is a sampling procedure, we can make a lot of choices on, for example, the graph size or complexity. By defining a probability

## Article

distribution over these hyperparameters in the prior, the posterior predictive distribution approximated by TabPFN at inference time implicitly represents a Bayesian ensemble, jointly integrating over a weighted hyperparameter space. The specific hyperparameter ranges and sampling strategies are chosen to cover a diverse set of scenarios that we expect to encounter in real-world tabular data.

Graph structure sampling. The structural causal models underlying each dataset are based on a DAG G. We sample these graphs using the growing network with redirection sampling method 57 , a preferential attachment process that generates random scale-free networks. We either sample a single connected component or merge multiple disjoint subgraphs. Disjoint subgraphs lead to features that are marginally independent of the target if they are not connected to the target node, reflecting real-world scenarios with uninformative predictors.

To control the complexity of the sampled DAGs, we use two hyperparameters: the number of nodes N and the redirection probability P. N is sampled from a log-uniform distribution, N a b log ~ ( , ) U , where a and b are hyperparameters controlling the range of the graph size. The redirection probability P is sampled from a gamma distribution, P ~ Γ(α, β), where α and β are shape and rate parameters, respectively. Larger values of N yield graphs with more nodes, whereas smaller values of P lead to denser graphs with more edges on average 57 .

Computational edge mappings. In our implementation, each SCM node and sample is represented as a vector in Rd . When propagating data through the SCM, the deterministic functions fi at each edge map the input vectors to an output vector using four types of computational modules:

1. Small neural networks: here we initialize weight matrices R W∈ d d × using Xavier initialization 58 and apply a linear transformation Wx + b to the input vectors R x∈ d , where b∈ d R is a bias vector. After the linear projection, we apply element-wise nonlinear activation functions R R σ : → d d , randomly sampled from a set, including identity, logarithm, sigmoid, absolute value, sine, hyperbolic tangent, rank operation, squaring, power functions, smooth ReLU 59 , step function and modulo operation.
2. Categorical feature discretization: to generate categorical features from the numerical vectors at each node, we map the vector to the index of the nearest neighbour in a set of per node randomly sampled vectors {p1, …, pK} for a feature with K categories. This discrete index will be observed in the feature set as a categorical feature. We sample the number of categories K from a rounded gamma distribution with an offset of 2 to yield a minimum number of classes of 2. To further use these discrete class assignments in the computational graph, they need to be embedded as continuous values. We sample a second set of embedding vectors p p { ′,…, ′ } K 1 for each class and transform the classes to these embeddings.
3. Decision trees: to incorporate structured, rule-based dependencies, we implement decision trees in the SCMs. At certain edges, we select a subset of features and apply decision boundaries on their values to determine the output 60 . The decision tree parameters (feature splits, thresholds) are randomly sampled per edge.
4. Noise injection: at each edge, we add random normal noise from the normal distribution N σ I (0, ) 2 .

Initialization data sampling. For each to-be-generated sample, we randomly generate initialization data ϵ that is inserted at the DAG root nodes and then propagated through the computational graph. The noise variables ϵ are generated according to one of three sampling mechanisms:

1. Normal: ϵ σ ~ (0, ) ϵ 2 N , where σϵ 2 is a hyperparameter.
2. Uniform: U ϵ a a ~ (- , ), where a is a hyperparameter.
3. Mixed: for each root node, we randomly select either a normal or uniform distribution to sample the initialization noise ϵ from.

Furthermore, we sample input data with varying degrees of nonindependence for some datasets. Here we first sample a random fraction ρ of samples to serve as prototypes x x *,…, * M 1 , where M = ρn and n is the dataset size. Then, for each input vector xi to be sampled, we assign weights αij to the prototypes and linearly mix the final input as

<!-- formula-not-decoded -->

where ∑jαij = 1. The weights αij are sampled from a multinomial distribution, αi ~ Multinomial(β), where β is a temperature hyperparameter controlling the degree of non-independence: larger β yields more uniform weights, whereas smaller β concentrates the weights on fewer prototypes per sample.

Post-processing. Each dataset is post-processed randomly with one or more of the following post-processings: (1) For some datasets, we use the Kumaraswamy feature warping, introducing nonlinear distortions 33 to features as done in ref. 61. (2) We quantize some continuous features into buckets of randomly sampled cardinality K, mimicking binned or discretized features commonly encountered in datasets. We map a feature value x to the index of the bucket it falls into, determined by K + 1 bin edges sampled from the set of values this feature takes. (3) To introduce scenarios for dynamic imputation and handling of incomplete datasets, a common challenge in data science, we randomly designate a fraction ρmiss of the data as missing according to the missing completely at random strategy. Each value is masked as missing with probability ρmiss, independently of the data values.

Target generation. To generate target labels for regression tasks, we select a randomly chosen continuous feature without post-processing. For classification labels, we select a random categorical feature that contains up to 10 classes. Thus, natively our method is limited to predicting at most 10 classes. This number can be increased by pre-training on datasets with a larger number of classes or by using approaches such as building a one-vs-one classifier, one-vs-rest classifier or building on approaches such as error-correcting output codes (ECOC) 62 .

## Training details

The training loss of any PFN is the cross-entropy between the targets of held-out samples of synthetic datasets and the model pre­ diction. For a test set (Xtest, ytest) = Dtest, the training loss is given by L q D = [- log ( | , )] ∪D p D θ PFN (( , ) ) ( ) test test train test test train y X E X y  . By minimizing this loss, the PFN learns to approximate the true Bayesian posterior predictive distribution for a chosen prior over datasets (and potentially their latent variables) D, as shown in ref. 22.

We trained our final models for approximately 2,000,000 steps with a batch size of 64 datasets. That means the models used for TabPFN are trained on around 130,000,000 synthetically generated datasets each. One training run requires around 2 weeks on one node with eight Nvidia RTX 2080 Ti GPUs. We sample the number of training samples for each dataset uniformly up to 2,048 and use a fixed validation set size of 128. We sample the number of features using a beta distribution (k = 0.95, b = 8.0) that we linearly scale to the range 1-160. To avoid peaks in memory usage, the total size of each table was restricted to be below 75,000 cells by decreasing the number of samples for large numbers of features.

We chose the hyperparameters for the prior based on random searches, in which we use only a single GPU per training and evaluate on our development set, see section 'Quantitative analysis'. We used the Adam optimizer 24 with linear warmup and cosine annealing 63 and tested a set of learning rates in [0.0001, 0.0005], using the one with the lowest final training loss.

## Inference details

To get the most performance out of TabPFN, it is crucial to optimize its inference pipeline. We generally always apply TabPFN in a small ensemble, in which we perform pre-processing or post-processing of the data differently for each ensemble member.

As our models are not fully permutation invariant, for each ensemble member, we shuffle the feature order, approximating order invariance 64 . For classification tasks, we additionally randomly permute the labels. We also apply a temperature to the softmax distribution of our model outputs for calibration.

Apart from the above, we use a subset of the following for each of our default ensemble members:

1. Quantile + Id: we quantize the inputs to equally spaced values bet­ ween 0 and 1, but keep a copy of each original feature. This effectively doubles the number of features passed to TabPFN.
2. Category shuffling: the labels of categorical features with low cardinality are shuffled.
3. SVD: an SVD compression of the features is appended to the features.
4. Outlier removal: all outliers, more than 12 standard deviations from the mean, are removed.
5. Power transform: each feature (or the label for regression) is transformed using a Yeo-Johnson transformation to stabilize the variance and make the data more normally distributed.
6. One-hot encoding: categorical features are encoded using one-hot encoding, in which each category is represented as a binary vector.

For PHE and hyperparameter tuning of TabPFN, we use a larger set of pre-processing techniques that additionally include a logarithmic, an exponential and a KDI transformation 65 . These transformations help address nonlinear relationships, skewed distributions and varying scales among features.

To calibrate prediction uncertainty, we apply a softmax temperature (default T = 0.9) by dividing logits before the softmax calculation:

<!-- formula-not-decoded -->

where zi are the logits, T is the temperature and P(yi∣x) is the calibrated probability. We offer the option to generate second-order polynomial features by multiplying up to 50 randomly selected feature pairs:

<!-- formula-not-decoded -->

where S is the set of randomly chosen feature pairs. This can capture nonlinear interactions between features. This option is disabled by default. To ensure proper handling of duplicate samples given the sample permutation invariance of our architecture, we add a unique sample identifier feature. This is a random number drawn from a standard normal distribution, ensuring each sample is treated distinctly in the attention mechanism. We also provide an option for subsampling in each estimator, to increase ensemble diversity, which performs random sampling without replacement. This option is disabled by default.

Regression details. To enable our model to do classification on a large range of scales and target distributions, we use the following approach. During pre-training, we rescale our regression targets to have zero mean and a standard deviation of 1 (z-score). To decide where the borders between our features lie, we draw a large sample of datasets from our prior and choose the 1/5,000 quantiles from this distribution. At inference time, we bring the real-world data to a similar range by again applying z-score normalization. Furthermore, we allow applying a range of transforms, including a power transform as part of our default. All of the transforms, including the z-score are inverted at prediction time by applying the inverse of the transform to the borders between buckets. This is equivalent to applying the inverse of the transform to the random variable represented by our output distribution but for the half-normals used on the sides for full support 22 . This is because all transforms are strictly monotone and the borders represent positions on the cumulative distribution function.

Data grouping based on random forest. To perform well on very heterogeneous datasets, we also propose to use random trees to split the training data into smaller more homogeneous datasets. This technique is used only when performing HPO or PHE for TabPFN. It is especially useful for TabPFN as our model performs best on small datasets.

The pre-processing for a single ensemble member, that is, a single tree, works as follows: we use a standard random tree with feature and sample bootstrapping and Gini impurity loss. For each leaf node of the decision tree, we store the subset of training samples that fall into that node and train a TabPFN on these. To predict the class label for a test sample x, we determine the TabPFN to use by passing x through the decision tree. We set the minimal leaf size to be large (500-2,000) such that the resulting data groups are large enough to train a strong model.

## TabPFN (PHE)

To further enhance the inference performance of TabPFN, in TabPFN (PHE), we use PHE for a fixed portfolio of TabPFN configurations from our search space detailed in Extended Data Table 5. For TabPFN (PHE), we first use holdout validation to sequentially evaluate models from the portfolio until a time limit is reached. After all models are evaluated once, we repeat holdout validation with new data splits until the time limit is reached. Then, we ensemble all evaluated TabPFN models by aggregating their predictions with a weighted arithmetic mean. We learn the weights using greedy ensemble selection (GES) 42,66 with 25 iterations on prediction data from holdout validation. Finally, we prune each zero-weighted model, refit all remaining models on all data and return the weighted average of their predictions.

Following standard practice in AutoML, we use GES because its predictive performance is often superior to the best individual model 43,67-69 . Owing to its ICL, we expect TabPFN to overfit the training data less than predictions of traditionally trained algorithms; thus, we opt for (repeated) holdout validation (as in Auto-Sklearn 1; ref. 67) instead of (repeated) cross-validation (as in AutoGluon 40 ). Moreover, as GES usually produces sparse weight vectors 43,69 , we expect the final ensemble after pruning each zero-weighted model to consist of a smaller number of models than for other ensembling approaches, such as bagging. Consequently, PHE can also improve the inference efficiency of a TabPFN ensemble compared with other ensembling approaches.

## Foundation model abilities

Density estimation. The combination of a regression and a classification TabPFN can be used as a generative model for tabular data, not only modelling targets but features as well. Let x y = {( , )} i i i N =1 D denote the original dataset, where x R ∈ i d is a d-dimensional feature vector and yi is the corresponding target value, and let qθ represent our trained TabPFN model, either a regression or classification model depending on the target type. We aim to approximate the joint distribution of a new example and its label x p y ( , ) D ∣ . To do this, we factorize the joint distribution as

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

where we only condition on a subset of the features in the training set ( j :,&lt; D ). The feature order of the joint density factorization influences

## Article

the estimated densities. To reduce variance from this source, we apply a permutation sampling approximation of Janossy Pooling at inference time, in which we average the outputs of Nj feature permutations, with Nj = 24 in our experiments 64 .

As we cannot condition on an empty feature set for technical reasons, we condition the prediction of the first feature x1, on a feature with random noise, that is, no information.

The above factorization of the density of a sample (equation (5)) is completely tractable and we thus use it to estimate the likelihood for data points. This enables tasks such as anomaly detection and outlier identification.

Synthetic data generation. We can leverage the generative abilities of TabPFN (see section 'Density estimation') to synthesize new tabular data samples that mimic the characteristics of a given real-world dataset, by simply following the factorization in equation (5) and sampling each feature step by step. The generated synthetic samples (x*, y*) can be used for various purposes, such as data augmentation, privacy-preserving data sharing and scenario simulation.

Embeddings. TabPFN can be used to retrieve meaningful feature representations or embeddings. Given a dataset x y = {( , )} i i i N =1 D , the goal is to learn a mapping R R f : → θ d k that transforms the original d-dimensional feature vectors xi into an embedding space of dimension k. The resulting embeddings f ( )∈ θ i k R x capture the learned relationships between features and can be used for downstream tasks. To use TabPFN for this problem, we simply use the target-column representations of its final layer as embeddings.

## Detailed evaluation protocol

To rigorously assess the performance and robustness of TabPFN, we conduct a comprehensive quantitative evaluation on standard tabular dataset benchmarks, comparing against state-of-the-art baselines under a standardized protocol.

Default configuration of TabPFN. Unlike traditional algorithms, in-context-learned algorithms do not have hyperparameters that directly control their training procedure. Instead, hyperparameters for inference of TabPFN only control the pre-processing of data and post-processing of predictions (for example, feature scaling or softmax temperature). Our default configuration (TabPFN (default)) for both classification and regression is optimized for accurate predictions with minimal fitting time. Here, we apply the same model multiple times with different pre- and post-processors and take the average over the predictions, yielding a four-way (eight-way for regression) ensemble. The settings for our data processing were obtained through a hyperparameter search optimized on our development datasets. The exact settings chosen are listed in Extended Data Table 5. We emphasize that, as for other foundation models (such as GPT), we trained our TabPFN model once and used the same model to perform ICL in a forward pass on all new datasets.

Baselines. We compare with tree-based methods, such as random forests 38 , XGBoost 7 , CatBoost 9 and LightGBM 8 , the state of the art for experts to perform predictions on tabular data 14,15 . We also compare with simpler methods, such as ridge regression 70 , logistic regression and SVMs 39 . Although standard neural networks, which unlike TabPFN do not use ICL, were shown to underperform for small (&lt;10,000 samples) tabular data 1,14,71 , as a point of reference, we still consider a simple neural network, the MLP.

Tabular dataset benchmarks. We perform our analysis on two widely used and publicly available benchmark suites: the standard AutoML benchmark 36 and the recent regression benchmark OpenML-CTR23 (ref. 37). Both benchmarks comprise a diverse set of real-world tabular datasets, carefully curated to be representative of various domains and data characteristics. The authors of the benchmark suite selected these datasets based on criteria such as sufficient complexity, real-world relevance, absence of free-form text features and diversity of problem domains.

For our quantitative analysis of TabPFN for classification tasks, we use a set of test datasets comprising all 29 datasets from the AutoML benchmark with up to 10,000 samples, 500 features and 10 classes. For regression tasks, the AutoML benchmark contains only 16 datasets matching these constraints. To increase statistical power, we augmented this set with all datasets matching our constraints from the recent OpenML-CTR23 benchmark, yielding a test set of 28 unique regression datasets in total. Extended Data Tables 3 and 4 provide full details for our test sets of classification and regression datasets, respectively.

We further evaluated additional benchmark suites from refs. 14,15. In ref. 14, there are 22 tabular classification datasets selected based on criteria such as heterogeneous columns, moderate dimensionality and sufficient difficulty. In ref. 15, there is a collection of 176 classification datasets, representing one of the largest tabular data benchmarks. However, the curation process for these datasets may not be as rigorous or quality controlled as for AutoML Benchmark and OpenML-CTR23. We also evaluated five Kaggle competitions with less than 10,000 training samples from the latest completed Tabular Playground Series.

Development datasets. To decide on the hyperparameters of TabPFN, as well as our hyperparameter search spaces, we considered another set of datasets, our development datasets. We carefully selected datasets to be non-overlapping with our test datasets described above. The list of development datasets can be found in Supplementary Tables 5 and 6. We considered the mean of normalized scores (ROC/RMSE) and rank quantiles and chose the best model configurations on these development datasets.

Metrics and cross-validation. To obtain scores for classification tasks, we use two widely adopted evaluation metrics: ROC AUC (One-vs-Rest) and accuracy. ROC AUC averages performance over different sensitivity-specificity trade-offs, and accuracy measures the fraction of samples labelled correctly.

For regression tasks, we use R 2 and negative RMSE as evaluation metrics. R 2 represents the proportion of variance in the target column that the model can predict. RMSE is the root of the average squared magnitude of the errors between the predicted and actual values. As we use negative RMSE, for all our four metrics higher values indicate a better fit.

To increase statistical validity, for each dataset and method in our test datasets, we evaluated 10 repetitions, each with a different random seed and train-test split (90% train and 10% test samples; all methods used the same cross-validation splits, defined by OpenML 72 ). We average the scores of all repetitions per dataset. Then, to average scores across datasets, we normalize per dataset following previous benchmarks 36,40 . The absolute scores are linearly scaled such that a score of 1.0 corresponds to the highest value achieved by any method on that dataset, whereas a score of 0 represents the lowest result. This normalization allows for building meaningful averages across datasets with very different score ranges. We provide absolute performance numbers in Supplementary Data Tables 1-2. All confidence intervals shown are 95% confidence intervals.

We tuned all methods with a random search using five-fold crossvalidation with ROC AUC/RMSE up to a given time budget, ranging from half a minute to 4 h. The first candidate in the random search was the default setting supplied in the implementation of the method and was also used if not a single cross-validation run finished before the time budget was consumed. See the section 'Qualitative analysis' for the used search spaces per method. All methods were evaluated using 8 CPU

cores. Moreover, TabPFN makes use of a 5-year-old consumer-grade GPU (RTX 2080 Ti). We also tested GPU acceleration for the baselines. However, as Extended Data Fig. 2 shows, this did not improve performance, probably because of the small dataset sizes.

## Data availability

All datasets evaluated are publicly available on openml.org or kaggle. com. We have provided scripts in our code repository that automate the process of downloading and evaluating the datasets. These scripts contain dataset identifiers, as well as exact data splitting and processing procedures.

## Code availability

Our code is available at https://priorlabs.ai/tabpfn-nature/ (https:// doi.org/10.5281/zenodo.13981285). We also provide an API that allows users to run TabPFN with minimal coding experience or without the availability of specific computing hardware such as a GPU. The code is designed to be modular and easily installable in a standard Python environment. The code to generate synthetic pre-training data has not been released with our models. We aim to enable researchers and practitioners to easily integrate TabPFN into their workflows and apply it to their specific tabular data tasks. We encourage users to provide feedback, report issues, and contribute to the further development of TabPFN. This open release aims to facilitate collaboration and accelerate the adoption and advancement of TabPFN in various research and application domains.

55. Müller, A., Curino, C. &amp; Ramakrishnan, R. Mothernet: a foundational hypernetwork for tabular classification. Preprint at https://arxiv.org/abs/2312.08598 (2023).
56. Shazeer, N. Fast transformer decoding: one write-head is all you need. Preprint at https:// arxiv.org/abs/1911.02150 (2019).
57. Krapivsky, P. L. &amp; Redner, S. Organization of growing random networks. Phys. Rev. E 63, 066123 (2001).
58. Glorot, X. &amp; Bengio, Y. Understanding the difficulty of training deep feedforward neural networks. In Proc. 13th International Conference on Artificial Intelligence and Statistics 249-256 (JMLR, 2010).
59. Nair, V. &amp; Hinton, G. Rectified linear units improve restricted Boltzmann machines. In Proc. 27th International Conference on Machine Learning (eds Fürnkranz, J. &amp; Joachims, T.) 807-814 (Omnipress, 2010).
60. Quinlan, J. R. Induction of decision trees. Mach. Learn. 1, 81-106 (1986).
61. Müller, S., Feurer, M., Hollmann, N. &amp; Hutter, F. PFNS4BO: in-context learning for Bayesian optimization. In Proc. 40th International Conference on Machine Learning 25444-25470 (PMLR, 2023).
62. Dietterich, T. G. &amp; Bakiri, G. Solving multiclass learning problems via error-correcting output codes. J. Artif. Intell. Res. 2, 263-286 (1994).
63. Loshchilov, I. &amp; Hutter, F. SGDR: Stochastic gradient descent with warm restarts. In Proc. 5th International Conference on Learning Representations (ICLR, 2017).
64. Murphy, R. L., Srinivasan, B., Rao, V. A. &amp; Ribeiro, B. Janossy pooling: learning deep permutation-invariant functions for variable-size inputs. In Proc. 7th International Conference on Learning Representations (ICLR, 2019).
65. McCarter, C. The kernel density integral transformation. Transact. Mach. Learn. Res. https://openreview.net/pdf?id=6OEcDKZj5j (2023).
66. Caruana, R., Munson, A. &amp; Niculescu-Mizil, A. Getting the most out of ensemble selection. In Proc. 6th IEEE International Conference on Data Mining (eds Clifton, C. et al.) 828-833 (IEEE, 2006).
67. Feurer, M. et al. in Automated Machine Learning: Methods, Systems, Challenges (eds Hutter, F. et al.) Ch. 6 (Springer, 2019).
68. Purucker, L. &amp; Beel, J. Assembled-OpenML: creating efficient benchmarks for ensembles in AutoML with OpenML. In Proc. First International Conference on Automated Machine Learning (AutoML, 2022).
69. Purucker, L. &amp; Beel, J. CMA-ES for post hoc ensembling in AutoML: a great success and salvageable failure. In Proc. International Conference on Automated Machine Learning Vol. 224, 1-23 (PMLR, 2023).
70. Hoerl, A. E. &amp; Kennard, R. W. Ridge regression: biased estimation for nonorthogonal problems. Technometrics 12, 55-67 (1970).
71. Shwartz-Ziv, R. &amp; Armon, A. Tabular data: deep learning is not all you need. Inf. Fusion 81, 84-90 (2022).
72. Vanschoren, J., van Rijn, J. N., Bischl, B. &amp; Torgo, L. OpenML: networked science in machine learning. SIGKDD Explor. 15, 49-60 (2014).
73. Fix, E. &amp; Hodges, J. L. Discriminatory analysis. Nonparametric discrimination: consistency properties. Int. Stat. Rev. 57, 238-247 (1989).

Acknowledgements We express our gratitude to the following individuals for their valuable contributions and support. We thank E. Bergman for his assistance with the evaluation of TabPFN, for helping implement the random forest pre-processing, and for his efforts in improving the code quality and documentation. His contributions were instrumental in benchmarking TabPFN and ensuring the reproducibility of our results. We thank A. Gupta and D. Otte for their work on the Inference Server, which enables the fast deployment of TabPFN without the need for a local GPU. Their efforts have greatly enhanced the accessibility and usability of TabPFN. We thank L. Schweizer for his work on exploring the random forest pre-processing for TabPFN further. We thank D. Schnurr and K. Helli for their work on visualization, and D. Schnurr for his specific contributions related to handling missing values. We thank S. M. Lundberg for the collection of visualization methods for feature attribution that we adapted for our work. We thank A. Müller for the insightful discussions related to TabPFN training and for his guidance on identifying and mitigating biases in the prior. His expertise has been invaluable in refining the TabPFN methodology. We are very grateful to C. Langenberg and M. Pietzner for providing insights on medical applications, interpreting model results and offering general advice. Their continued support has been instrumental in shaping this work. We thank S. Stäglich for his outstanding maintenance and support with the cluster infrastructure. We thank B. Lake for his general paper writing advice. We are grateful for the computational resources that were available for this research. Specifically, we acknowledge support by the state of Baden-Württemberg through bwHPC and the German Research Foundation (DFG) through grant no INST 39/963-1 FUGG (bwForCluster NEMO), and by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) under grant no. 417962828. We acknowledge funding by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) under SFB 1597 (SmallData), grant no. 499552394, and by the European Union (through ERC Consolidator Grant DeepLearning 2.0, grant no. 101045765). Views and opinions expressed are however those of the authors only and do not necessarily reflect those of the European Union or the European Research Council. Neither the European Union nor the granting authority can be held responsible for them. F.H. acknowledges the financial support of the Hector Foundation.

Author contributions N.H. improved the prior of the model; added regression support, unsupervised capabilities and inference optimizations; and contributed to the experiments and wrote the paper. S.M. improved the neural network architecture, training and efficiency; added inference optimizations; and contributed to experiments and wrote the paper. L.P. improved the inference interface of the model; contributed to hyperparameter tuning; added post hoc ensembling of TabPFN models; contributed to benchmarking; and wrote the paper. A.K. added inference optimizations and Kaggle experiments. M.K. contributed to inference optimizations. S.B.H. contributed to the usability of our code. R.T.S. contributed to preliminary architectural experiments to speed up inference and helped revise the first draft of the paper. F.H. contributed technical advice and ideas, contributed to the random forest pre-processing, managed collaborations and funding, and wrote the paper.

Competing interests The following patent applications invented by S.M. and F.H. and filed by R. Bosch are related to this work: DE202021105192U1 and DE102021210775A1. The authors do not have any ownership rights to these patent applications. F.H. and N.H. are affiliated with PriorLabs, a company focused on developing tabular foundation models. The authors declare no other competing interests.

## Additional information

Supplementary information The online version contains supplementary material available at https://doi.org/10.1038/s41586-024-08328-6.

Correspondence and requests for materials should be addressed to Noah Hollmann, Samuel Müller or Frank Hutter.

Peer review information Nature thanks Duncan McElfresh, Oleksandr Shchur and the other, anonymous, reviewer(s) for their contribution to the peer review of this work.

Reprints and permissions information is available at http://www.nature.com/reprints.

## Article

<!-- image -->

Extended Data Fig. 1 | Performance comparison across additional dataset characteristics, extending Fig. 5. This figure shows the relative performance of different methods when datasets are split based on specific attributes. Error bars represent 95% confidence intervals. While performance differences are generally subtle across these splits, the most notable variation is observed for datasets with outliers in the target variable, though confidence intervals still overlap.

<!-- image -->

<!-- image -->

Extended Data Fig. 2 | Performance comparisons of TabPFN and baselines on additional benchmark datasets and with GPU support. (a) Classification performance on the Grinsztajn medium-sized benchmark with categorical features, across 7 datasets. (b) Classification performance on the Grinsztajn medium-sized benchmark with numerical features, across its 15 datasets. (c) Classification performance on the TabZilla benchmark, consisting of 102 datasets with fewer than 10,000 rows of data, 500 features, and 10 classes.

<!-- image -->

<!-- image -->

Duplicated datasets and those with fewer than 5 samples per class were removed to enable 5-fold cross-validation. (d) Performance Over Time Comparison with CPU vs. GPU Hardware: The performance over time when running our strongest baselines with eight CPUs (CPU) vs. eight CPUs and on one GPU (+GPU) on our classification test benchmark. AutoGluon automatically decides which models to train with what resources. For CatBoost and XGB, we specified that the models should train with GPU. Intervals represent 95% CI.

## Article

Extended Data Fig. 3 | Comparing SHAP (SHapley Additive exPlanations) summary plots between TabPFN and baselines. We compare SHAP feature importance and impact for Logistic Regression, TabPFN, and CatBoost on the "Default of Credit Card Clients" dataset. The top features visualized are credit amount, age, and duration. Each point represents a single instance, with the color indicating the value of the checking status feature (blue for low, red for high), illustrating its interaction with the respective feature on the x-axis.

<!-- image -->

We see that Logistic Regression is most interpretable due to the simple underlying functions. However, Logistic Regression has poor predictive accuracy, and the learned functions are unintuitive when looking at the outer bounds of features. TabPFN has good predictive accuracy and learns simple, interpretable functions. CatBoost is the least interpretable, with unclear patterns and wide variation in SHAP values per sample. This figure is adapted from Lundberg et al. 47 .

Extended Data Fig. 4 | Finetuning TabPFN on 2-dimensional sine curve datasets. (a) Examples of 2D sine curve datasets with different offsets. (b) Finetuning loss curves for 50 runs with random train-test offsets. Colors indicate the offset between train and test. TabPFN shows positive transfer,

<!-- image -->

with better performance for more similar distributions. For a dataset shift of π, the inverse label needs to be predicted in the test set, compared to the finetuning data. However, TabPFN still generalizes when finetuned on this data.

## Article

## Extended Data Table 1 | Aggregated results on the 29 AMLB classification Benchmark datasets

Scores are normalized on all the baselines shown in this table, with the weakest score set to 0.0 and the highest to 1.0, per dataset. All baselines are optimized for ROC AUC thus trading-off representativeness of secondary metrics. Times for TabPFN refer to times on GPU. Datasets are available via OpenML https://www.openml.org/search?type=data&amp;sort=runs&amp;id={OPENML\_ID}. Exact train-test splits defined by OpenML tasks with task numbers in our code datasets/benchmark\_dids.py.

## Extended Data Table 2 | Aggregated results on the 28 AMLB and OpenML-CTR23 regression Benchmark datasets

Scores are normalized on all the baselines shown in this table, with the weakest score set to 0.0 and the highest to 1.0, per dataset. K-Nearest Neighbors 73 performed significantly worse than the considered baselines. All baselines are optimized for RMSE as an objective thus trading-off representativeness of secondary metrics. Times for TabPFN refer to times on GPU. Datasets are available via OpenML https://www.openml.org/search?type=data&amp;sort=runs&amp;id={OPENML\_ID}. Exact train-test splits defined by OpenML tasks with task numbers in our code datasets/ benchmark\_dids.py.

## Article

## Extended Data Table 3 | List of test datasets used for primary evaluation of classification tasks

All classification tasks from the AutoML Benchmark 36 with fewer 10,000 samples and 500 features. The benchmark comprises diverse real-world tabular datasets, curated for complexity, relevance, and domain diversity.

## Extended Data Table 4 | List of test datasets used for primary evaluation of regression tasks

All regression tasks from the AutoML 36 and OpenML-CTR23 37 Benchmarks with fewer 10,000 samples and 500 features. The benchmark comprises diverse real-world tabular datasets, curated for complexity, relevance, and domain diversity.

## Article

## Extended Data Table 5 | Hyperparameter defaults and search space for TabPFN and our baselines

## Extended Data Table 6 | Performance on Kaggle Data Science Challenges

Performance of default CatBoost and default TabPFN on all 5 Kaggle classification or regression competitions from the Tabular Playground Series Season 3 with late submission enabled, fewer than 10,000 rows of data, 500 features, and 10 classes. We report the private score averaged over 5 seeds. For Episode 5, as ordinal regression can be treated as a classification or regression task, for both CatBoost and TabPFN we tried both the regression and the classification model and chose the better of the two (regression for CatBoost; classification for TabPFN). Arrows indicate the optimization direction for each metric. We emphasize that these results only compare Catboost and TabPFN on the raw competition data, not using any of the tricks the ingenious Kaggle community applies, such as use of domain knowledge, data cleaning, special feature engineering, postprocessing and ensembling; nevertheless, these techniques can be combined with TabPFN, and we hope that TabPFN's improved base model performance will allow Kagglers to achieve even better results with them.

## 1 Supplementary Tables

Supplementary Table 1: Raw Performance Scores per Dataset for the Classification Test Benchmark. The table presents the mean and standard deviation of the ROC AUC score across all folds per dataset for each compared method after four hours. These are the raw results used to generate our main classification results. The second column details the OpenML tasks and dataset IDs.

<!-- image -->

Supplementary Table 2: Raw Performance Scores per Dataset for the Regression Test Benchmark. The table presents the mean and standard deviation of the negative RMSE across all folds per dataset for each compared method after four hours. These are the raw results used to generate our main regression results. The second column details the OpenML tasks and dataset IDs.

<!-- image -->

Supplementary Table 3: Raw Performance Scores per Dataset for the Grinsztajn Medium-Sized Benchmark. The table presents the mean and standard deviation of the ROC AUC score across all folds per dataset for each compared method after four hours. The second column details the OpenML tasks and dataset IDs.

<!-- image -->

Supplementary Table 4: Raw Performance Scores per Dataset for the TabZilla Benchmark. The table presents the mean and standard deviation of the ROC AUC score across all folds per dataset for each compared method after one hour. The second column details the OpenML tasks and dataset IDs. The second column details the OpenMLtask and dataset IDs.

<!-- image -->

| Dataset Name                                                              | Task (Dataset) RF                                      | AutoGluon                                                                                                      | CatBoost                                                                | KNN                                           | LightGBM                                                                           | Linear                                                       | Regression MLP                                        | SVM                                                   | XGB                                                   | TabPFN (PHE)                                                  | TabPFN                                                        |
|---------------------------------------------------------------------------|--------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------|-----------------------------------------------|------------------------------------------------------------------------------------|--------------------------------------------------------------|-------------------------------------------------------|-------------------------------------------------------|-------------------------------------------------------|---------------------------------------------------------------|---------------------------------------------------------------|
| ada_agnostic pc4                                                          | 3896 (1043)                                            | 0.9105 (± 0.0152) 0.9070 (± 0.0145) (± 0.0195) 0.9548 (± 0.0176)                                               | 0.8537 (± 0.0178)                                                       | 0.9077 (± 0.0138)                             | 0.9013 (± 0.0141) (± 0.0201)                                                       | 0.8969 (± 0.0145)                                            | 0.8863 (± 0.0175)                                     | 0.8838 (± 0.0129)                                     | 0.9107 (± 0.0136)                                     | 0.9059 (± 0.0139)                                             | 0.9060 (± 0.0138)                                             |
| pc3                                                                       | 3902 (1049) 0.9527 3903 (1050) 0.8659 0.0396)          | (± 0.0382) 0.8501 (± 0.0348) 0.0931) 0.8431 (±                                                                 | 0.8439 (± 0.0505) 0.7911 (± 0.0604)                                     | 0.9452 (± 0.8432 (±                           | 0.0220) 0.9416 0.0340) 0.8490 (±                                                   | 0.9065 (± 0.0306) 0.7907 (± 0.0419)                          | 0.9198 (± 0.0319) 0.8220 (± 0.0390)                   | 0.9053 (± 0.0362) 0.7299 (± 0.0583)                   | 0.9495 (± 0.0164) 0.8604 (± 0.0380)                   | 0.9589 (± 0.0164) 0.8584 (± 0.0371)                           | 0.9550 (± 0.0202) 0.8618 (± 0.0372)                           |
| kc2 kc1                                                                   | 3913 (1063) (± 0.0828) 3917 (1067) (± 0.0368)          | 0.8360 (± 0.8422 (± 0.0299) 0.8265 (±                                                                          | 0.0972) 0.8154 (± 0.0392) 0.7619 (±                                     | 0.0888) 0.8423 0.0509) 0.8060                 | (± 0.0965) 0.8429 (± 0.0361) 0.8317                                                | 0.8406 (± 0.0880) 0.7989 (± 0.0358)                          | 0.6788 (± 0.2587) 0.8025 (± 0.0354)                   | 0.8446 (± 0.0881) 0.8460 (± 0.7985 (± 0.0347)         | 0.0914) 0.8306 (± 0.0365)                             | 0.8323 (± 0.0933) 0.8502 (± 0.0284)                           | 0.8358 (± 0.0924) 0.8481 (± 0.0317)                           |
| pc1                                                                       | 3918 (1068) 0.0475)                                    | 0.8953 (± 0.0417) (±                                                                                           | 0.8064 (±                                                               | 0.0774)                                       | (± 0.0561) 0.8579                                                                  | 0.8299 (± 0.0569)                                            | 0.8076 (± 0.0540)                                     | 0.7369 (± 0.1141)                                     | 0.8803 (± 0.0537)                                     | 0.9092 (± 0.0412)                                             | 0.9066 (± 0.0390)                                             |
| musk                                                                      | 3950 (1116) 0.0000)                                    | 0.8791 1.0000 (± 0.0001) 1.0000 (±                                                                             | 0.0603) 0.0000) 0.9956 (± 0.0176)                                       | 0.8663 0.0019) 1.0000                         | (± (± 0.0000) 1.0000 (±                                                            | 1.0000 (± 0.0000)                                            | 1.0000 (± 0.0000)                                     | 1.0000 (± 0.0000)                                     | 0.7418 (± 0.0746)                                     | 0.9997 (± 0.0011)                                             | 1.0000 (± 0.0000)                                             |
| balancescale mfeatfactors                                                 | 11 (11) 0.0337) 12 (12) 0.0020)                        | 0.9983 (± 0.0035) 0.9586 (± (± 0.0009) 0.9988 (± 0.0016)                                                       | 0.9078 (± 0.0350) 0.9969 (± 0.0027)                                     | 0.9989 (± 0.9990 (± (±                        | 0.0019) 0.8549 (± 0.0010) 0.9984                                                   | 0.9726 (± 0.0130) 0.9985 (± 0.0016)                          | 0.9809 (± 0.0090) 0.9988 (± 0.0016)                   | 0.9983 (± 0.0030) 0.9995 (± 0.0007)                   | 0.9985 (± 0.0026) 0.9990 (± 0.0013)                   | 1.0000 (± 0.0000) 0.9997 (± 0.0004)                           | 1.0000 (± 0.0000) 0.9997 (± 0.0004)                           |
| breastcancer 145799 (13)                                                  | 0.9993 0.7119 (± 0.1080) 0.0000)                       | 0.0961) 0.6963 (± 0.0957) 1.0000 (± 0.0000)                                                                    | 0.6447 (±                                                               | 0.0830) 0.6734                                | (± 0.1218) 0.7233 (±                                                               | 0.6830 (± 0.0995)                                            | 0.6230 (± 0.1506) 1.0000 (± 0.0000)                   | 0.7254 (± 0.0989) 1.0000 (± 0.0000)                   | 0.7121 (± 0.1132) 1.0000 (± 0.0000)                   | 0.7216 (± 0.0887) 1.0000 (± 0.0000)                           | 0.7381 (± 0.0970)                                             |
| acuteinflammations banknoteauthentication                                 | 10089 (1455) 10093 (1462)                              | 1.0000 (± 0.0000) 1.0000 (± 0.0000) (± 0.0000)                                                                 | 1.0000 (± 0.9987 (± 0.0028)                                             | 0.0000) 1.0000 (± 1.0000 (±                   | 0.0000) 1.0000 (± 0.0000) 0.9999 (± 0.0002)                                        | 1.0000 (± 0.0000) 0.9998 (± 0.0004)                          | 0.9998 (± 0.0005)                                     | 1.0000 (± 0.0000)                                     | 1.0000 (± 0.0000) 0.7556 (±                           | 1.0000 (± 0.0000)                                             | 1.0000 (± 0.0000) 1.0000 (± 0.0000)                           |
| bloodtransfusionservicecenter cardiotocography                            | 10101 (1464) 9979 (1466)                               | 1.0000 0.7448 (± 0.0580) 0.7570 (± 0.0543) 1.0000 (± 0.0000) 1.0000 (± 0.0000)                                 | 0.7292 (± 0.0595) 1.0000 (± 0.0000)                                     | 0.7381 (± 1.0000 (±                           | 0.0509) 0.7368 (± 0.0556) 0.0000) 1.0000 (± 0.0000)                                | 0.7593 (± 0.0434) 1.0000 (± 0.0000)                          | 0.6585 (± 0.1373) 1.0000 (± 0.0000)                   | 0.7364 (± 0.0501) 1.0000 (± 0.0000)                   | 0.0446) 1.0000 (± 0.0000)                             | 0.7621 (± 0.0447) 1.0000 (± 0.0000)                           | 0.7615 (± 0.0409) 1.0000 (± 0.0000)                           |
| fertility                                                                 | 9984 (1473) (± 0.2830) 9985 (1475) (± 0.0096)          | 0.5667 (± 0.3646) 0.5188 (± 0.3248) 0.8611 (± 0.0097) 0.8510 (± 0.0089)                                        | 0.6733 (± 0.7942 (±                                                     | 0.2230) 0.6858 0.0115) 0.8516                 | (± 0.2759) 0.5826 (± 0.0101) 0.8523                                                | 0.4042 (± 0.2946) 0.7097 (± 0.0129)                          | 0.5674 (± 0.2456) 0.7788 (± 0.0107)                   | 0.5333 (± 0.2981) 0.7550 (± 0.0310)                   | 0.6934 (± 0.3310) 0.8554 (± 0.0079)                   | 0.5458 (± 0.3544) 0.8609 (± 0.0081)                           | 0.5576 (± 0.2688) 0.8580 (± 0.0085)                           |
| firstordertheoremproving                                                  | 145847 (± 0.0416)                                      | (± 0.0135) 0.6307 (± 0.0372)                                                                                   | 0.5920 (±                                                               | 0.0298) 0.6583                                | 0.0371) 0.6036                                                                     | 0.9284 (± 0.0425)                                            | 0.6702 (±                                             | 0.9027 (± 0.0553)                                     | 0.7054 (± 0.0425)                                     | (± 0.0000)                                                    | 0.9999 (± 0.0002)                                             |
| hillvalley ilpd 9971                                                      | (1479) (1480) (± 0.0428)                               | 0.9754 0.7481 (± 0.0537) 0.7421 (± 0.0692)                                                                     | 0.6740 (±                                                               | (± 0.0548) 0.7154 (±                          | 0.0629) 0.7237                                                                     | 0.7552 (± 0.0677)                                            | 0.0747) 0.7557 (± 0.0631)                             | 0.6799 (± 0.0547)                                     | 0.7193 (± 0.0706)                                     | 1.0000 0.7595 (± 0.0544)                                      | 0.7586 (± 0.0634)                                             |
| ozonelevel8hr (± 0.0508) phoneme                                          | 9978 (1487) 0.9118 (± 0.0345) 9952 (1489) 0.0097) 9957 | 0.9336 (± 0.0192) 0.9313 (± 0.0190) 0.9733 (± 0.0076) 0.9634 (± 0.0092) 0.9421                                 | 0.8691 0.9319 (±                                                        | 0.9233 (± 0.0252) 0.9597 (± (±                | 0.9212 (± 0.0094) 0.9635 (± 0.0425) 0.9333                                         | 0.9148 (± 0.0295) 0.9217 0.8136 (± 0.0218) 0.9247 (± 0.0321) | (± 0.0254) 0.8916 (± 0.0117) 0.9272 (±                | 0.0264) 0.9314 (± 0.9103 (± 0.0117) 0.9225 (± 0.0357) | 0.0179) 0.9352 0.9640 (± 0.0087) 0.9345 (± 0.0384)    | (± 0.0184) 0.9733 (± 0.0073)                                  | 0.9272 (± 0.0217) 0.9724 (± 0.0075) 0.9386 (± 0.0322)         |
| qsarbiodeg                                                                | (1494) 0.0309)                                         | (± 0.0316) 0.9287 (± 0.0395)                                                                                   | 0.0137) 0.9056 (± 0.0344)                                               | 0.9276                                        | (±                                                                                 |                                                              | 0.0323)                                               |                                                       |                                                       | 0.9409 (± 0.0311)                                             |                                                               |
| wallrobotnavigation mfeatfourier                                          | 9960 (1497) 14 (14)                                    | 1.0000 (± 0.0000) 1.0000 (± 0.0000) 0.9878 (± 0.0037) 0.9852 (± 0.0037)                                        | 0.9653 (± 0.0050) 0.9757 (± 0.0068)                                     | 0.9999 (± 0.9842 (±                           | 0.0002) 0.9999 (± 0.0000) 0.0038) 0.9830 (± 0.0032)                                | 0.9085 (± 0.0068) 0.9814 (± 0.0043)                          | 0.9908 (± 0.0015) 0.9795 (± 0.0053)                   | 0.9904 (± 0.0019) 0.9860 (± 0.0039)                   | 1.0000 (± 0.0000) 0.9834 (± 0.0042)                   | 1.0000 (± 0.0000) 0.9921 (± 0.0026)                           | 1.0000 (± 0.0000) 0.9908 (± 0.0022)                           |
| semeion                                                                   | 9964 (1501) 0.0013)                                    | 0.9986 (± 0.0009) 0.9985 (± 0.0009) 0.9947                                                                     | 0.9938 (±                                                               | 0.0029) 0.9974                                | 0.0017) 0.9966 (± (±                                                               | 0.9957 (± 0.0026)                                            | 0.9962 (± 0.0019)                                     | 0.9990 (± 0.0006)                                     | 0.9980 (± 0.0016)                                     | 0.9987 (± 0.0006)                                             | 0.9984 (± 0.0009)                                             |
| wdbc bankmarketing                                                        | 9946 (1510) 0.0135) 9899 (1558) 0.0162)                | 0.9958 (± 0.0070) (± 0.0081) 0.9188 (± 0.0149) 0.9167 (± 0.0171)                                               | 0.9883 (± 0.0137) 0.7474 (± 0.0333)                                     | (± 0.9939 (± 0.9094 (±                        | 0.0081) 0.9896 0.0163) 0.9073                                                      | 0.9942 (± 0.0088) 0.8904 (± 0.0259)                          | 0.9898 (± 0.0155) 0.8765 (± 0.0187)                   | 0.9887 (± 0.0165) 0.8855 (± 0.0216)                   | 0.9945 (± 0.0069) 0.8927 (± 0.0511)                   | 0.9958 (± 0.0080) (± 0.0132)                                  | 0.9950 (± 0.0087) 0.9298 (± 0.0115)                           |
| breastw mfeatkarhunen                                                     | 15 (15) 0.0074)                                        | 0.9948 (± 0.0048) 0.9961 (±                                                                                    | 0.9903 (±                                                               | 0.0087) 0.9903 (±                             | (± 0.0083) 0.9922 (± (±                                                            | 0.9948 (± 0.0053) 0.9972 (±                                  | 0.9946 (± 0.0065) 0.9973 (±                           | 0.9955 (± 0.0046) 0.9996 (± 0.0003)                   | 0.9931 (± 0.0065) 0.9991 (± 0.0005)                   | 0.9293 0.9952 (± 0.0041)                                      | 0.9950 (± 0.0051)                                             |
|                                                                           | 16 (16) 0.0010)                                        | 0.9996 (± 0.0002) 0.9994 (±                                                                                    | 0.0047) 0.0004) 0.9965 (± 0.0020)                                       | 0.0023) 0.9988                                | (± 0.0009) 0.9982                                                                  | 0.0016)                                                      | 0.0015)                                               |                                                       |                                                       | 0.9997 (± 0.0004)                                             | 0.9997 (± 0.0003)                                             |
| satimage eucalyptus                                                       | 2074 (182) (± 0.0028) 2079 (188) (± 0.0200)            | 0.9944 (± 0.0013) 0.9923 (± 0.9349 (± 0.0170) 0.9160 (± 0.0192)                                                | 0.9861 (± 0.0029) 0.8439 (± 0.0153)                                     | 0.9916 (± 0.9131                              | 0.0020) 0.9899 (± 0.0183) 0.9146 (± 0.0076)                                        | 0.9765 (± 0.0056) 0.9138 (± 0.0180)                          | 0.9850 (± 0.0031) 0.9082 (± 0.0150)                   | 0.9903 (± 0.0021) 0.9061 (± 0.0134)                   | 0.9924 (± 0.0020) 0.9075 (± 0.0218)                   | 0.9955 (± 0.0013) 0.9365 (± 0.0151)                           | 0.9951 (± 0.0015) 0.9348 (± 0.0144)                           |
| mfeatmorphological anneal                                                 | 18 (18) 0.0082) 2867 (1) 0.0008)                       | 0.9774 (± 0.0065) 0.9652 (± 0.0072) (± 0.0423) 0.9999 (± 0.0005)                                               | 0.9562 (± 0.0113) 0.9838 (± 0.0329)                                     | 0.9637 0.9980 (±                              | 0.9629 0.0053)                                                                     | 0.9660 (± 0.0076) 0.9810 (± 0.0355)                          | 0.9623 (± 0.0073) (±                                  | 0.9681 (± 0.0081) 0.9935 (± 0.0176)                   | 0.9629 (± 0.0068) 0.9972 (± 0.0080)                   | 0.9698 (± 0.0061) 0.9996 (±                                   | 0.9686 (± 0.0075) 1.0000 (± 0.0001)                           |
|                                                                           |                                                        | 0.9196 0.9768 (±                                                                                               |                                                                         |                                               | (± 0.9997 (± 0.9751                                                                |                                                              | 0.9938 0.0100) 0.9819 (± 0.0022)                      | 0.9920 (± 0.0016)                                     | 0.9755 (± 0.0035)                                     | 0.0009)                                                       | 0.9854 (± 0.0017)                                             |
| mfeatzernike cjs                                                          | 22 (22) 14967 (23380)                                  | 0.9953 (± 0.0014) 1.0000 (± 0.0000) 1.0000 (±                                                                  | 0.0027) 0.9781 (± 0.0000) 0.8777 (± 0.0619)                             | 0.0041) 0.9743 (± 0.0114) 1.0000 (± (±        | 0.0034) (± 0.0038) 0.0000) 0.9600 (± 0.0073) 0.5906 (± 0.0827)                     | 0.9815 (± 0.0018) 0.7120 (± 0.0174) 0.6296 (± 0.0610)        | 0.8011 (± 0.0102) 0.5209 (± 0.1281)                   | 0.8028 (± 0.0118) 0.6447 (± 0.0977)                   | 0.8447 (± 0.0878) 0.5626 (± 0.0865)                   | 0.9900 (± 0.0023) 1.0000 (± 0.0000)                           | 1.0000 (± 0.0000) 0.6245 (± 0.0784)                           |
| dressessales cmc                                                          | 125920 (23381) 23 (23) 0.0329)                         | 0.6054 (± 0.0565) 0.6125 (± 0.7472 (± 0.0305) 0.7464 (±                                                        | 0.5474 (± 0.6377 (±                                                     | 0.0740) 0.6155 0.0313) 0.7461                 | 0.0658) 0.0390) 0.7463                                                             | 0.7028 (±                                                    | 0.6979 (± 0.0336)                                     | 0.6850 (± 0.0399) (± 0.0000)                          | 0.7429 (± 0.0351)                                     | 0.5934 (± 0.0770) (± 0.0322)                                  | 0.7532 (± 0.0287)                                             |
| mushroom                                                                  | 24 (24) 0.0000) 0.0461)                                | 1.0000 (± 0.0000) 1.0000 (± 0.9306 (±                                                                          | 0.0305) 0.0000) 1.0000 (± 0.0349)                                       | (± 0.0000) 1.0000 (± (±                       | (± 0.0000) 1.0000 (± 0.0447) 0.9139 (±                                             | 0.0407) 1.0000 (± 0.0000) 0.8807 (± 0.0747)                  | 1.0000 (± 0.0000) 0.8608 (± 0.0870)                   | 1.0000 0.8782 (± 0.0668)                              | 1.0000 (± 0.0000)                                     | 0.7557 1.0000 (± 0.0000)                                      | 1.0000 (± 0.0000) 0.9375 (± 0.0310)                           |
| colic colic                                                               | 25 (25) 27 (27) 0.0635) 28 (28)                        | 0.9262 (± 0.0374) 0.8913 (± 0.0580) 0.8986 (± 0.9999 (± 0.0001)                                                | 0.8548 (± 0.8403 (± 0.9992 (±                                           | 0.0827) 0.9178 0.8876 0.9998                  | 0.8962 (± 0.9996 (±                                                                | 0.8769 (± 0.0607) 0.9993 (±                                  | 0.8625 (± 0.0636) 0.9997 (± 0.0002)                   | 0.8664 (± 0.0843) 0.9999 (± 0.0001)                   | 0.6636 (± 0.1232) 0.8899 (± 0.0627) 0.9999 (± 0.0001) | 0.9412 (± 0.0350) 0.8875 (± 0.0597) 0.9999 (±                 | 0.9047 (± 0.0510) 0.9999 (± 0.0001)                           |
| optdigits                                                                 | 0.0002)                                                | 0.9999 (±                                                                                                      | 0.0708) 0.0001) 0.0312) 0.9096                                          | 0.0921) 0.0010) 0.0402)                       | (± 0.0519) 0.0002) 0.0355)                                                         | 0.9281 (±                                                    | 0.9167 (± 0.0472)                                     | 0.9188 (± 0.0407)                                     | 0.9352 (± 0.0374)                                     | 0.9413 (±                                                     | 0.9410 (± 0.0355)                                             |
| creditapproval pageblocks                                                 | 29 (29) 0.0464) 30 (30) 0.0077)                        | 0.9380 (± 0.0341) 0.9383 (± 0.9949 (± 0.0027) 0.9940 (± 0.0032)                                                | (±                                                                      | (± 0.9398 (±                                  | 0.9321 (±                                                                          | 0.0004) 0.0365)                                              | 0.9863 (± 0.0078)                                     |                                                       |                                                       | 0.0001) 0.0391) 0.9943 (± 0.0035)                             | 0.9947 (± 0.0035)                                             |
| scene creditg                                                             | 3485 (312) 0.0189) 31 (31) 0.0344)                     | 0.9931 (± 0.0071) 0.9884 (± 0.0127) (± 0.0350) 0.7970 (± 0.0396)                                               | 0.9639 (± 0.0171) 0.9834 (± 0.0139) 0.7431 (± 0.0298)                   | 0.9932 (± 0.9886 0.7782                       | 0.0032) 0.9913 (± 0.0134) 0.9472 (± 0.7935 (±                                      | 0.9823 (± 0.0080) 0.9925 (± 0.0081) 0.7870 (±                | 0.9857 (± 0.0185) (±                                  | 0.9873 (± 0.0054) 0.9890 (± 0.0116) 0.7883 (± 0.0232) | 0.9944 (± 0.0026) 0.9883 (± 0.0123) 0.7949 (± 0.0365) | (± 0.0094) (± 0.0331)                                         | 0.9922 (± 0.0089) 0.8006 (±                                   |
| hayesroth                                                                 | 146063 (329) 0.0381) 146065 (334)                      | 0.7956 0.9620 (± 0.0354) 0.9631 (± 0.0339) 1.0000 (± 0.0000)                                                   | 0.8758 (± 0.0613)                                                       | (± (± 0.9664 (±                               | 0.0447) 0.0319) 0.9506 (±                                                          | 0.0412) 0.7837 (± 0.1028)                                    | 0.6759 0.0800) 0.7694 (± 0.0771)                      | 0.9359 (± 0.0410)                                     | 0.9729 (± 0.0394)                                     | 0.9916 0.7945 0.9729 (± 0.0302)                               | 0.0419) 0.9674 (± 0.0398) 1.0000 (± 0.0000)                   |
| monksproblems2                                                            | 0.0059) 35 (35) 0.0019) 3510 (375)                     | 0.9539 0.9989 (± 0.0019) 0.9985 1.0000 (± 0.0001)                                                              | 0.7967 (± 0.9990 (±                                                     | 1.0000 (± 0.9978 (±                           | 0.0000) 0.9946 (± 0.9989 (± (±                                                     | 0.5252 (± 0.0937) 0.9987 (± 0.0022)                          | 1.0000 (± 0.0000) 0.9986 (± 0.0021)                   | 1.0000 (± 0.0000) 0.9986 (± 0.0024)                   | 1.0000 (± 0.0000) 0.9990 (± 0.0021)                   | 1.0000 (± 0.0000) (± 0.0019) (± 0.0000)                       | 0.9989 (± 0.0021) 1.0000 (± 0.0000)                           |
| dermatology JapaneseVowels                                                | 0.0002) 3512 (377)                                     | 0.9999                                                                                                         | (± 0.0309) (± 0.0023) (± 0.0001) 0.9994 (± 0.0006)                      | 0.0474) 0.0015) 0.0004) 0.9998                | 0.0029) 0.0001)                                                                    | 0.9972 (± 0.0006)                                            | 0.9985 (± 0.0005)                                     | 0.9999 (± 0.0001) 0.9999 (± 0.0002)                   | 0.9999 (± 0.0001)                                     | 0.9990 1.0000 1.0000 (±                                       | 1.0000 (± 0.0000)                                             |
| synthetic_control diabetes sick                                           | 0.0006) 37 (37) 0.0461) 3021 (38)                      | 1.0000 (± 0.0000) 0.9997 0.8365 (± 0.0518) 0.8427 (± 0.9985 (± 0.0009)                                         | (± 0.9995 (± 0.0439) 0.8054 (±                                          | (± 0.0008) 0.9994 (±                          | 0.9994 0.0010) 0.9997 (± 0.8296 (±                                                 | 0.9997 (± 0.0003) 0.8324 (± 0.9520 (±                        | 0.9990 (± 0.0007) 0.8426 (± 0.0541) 0.9473 (± 0.0315) | 0.8375 (± 0.0564)                                     | 0.9998 (± 0.0005) 0.8355 (± 0.0482) 0.9983 (± 0.0009) | 0.0000) (± 0.0432) (± 0.0008)                                 | 0.8456 (± 0.0429) 0.9987 (± 0.0011)                           |
|                                                                           | (± 0.0019) 3 (3)                                       | 0.9985 (±                                                                                                      | 0.9400 (±                                                               | 0.8250 (± 0.9981 (±                           | 0.0394) 0.0010) 0.9967                                                             | 0.0591)                                                      |                                                       | 0.9512 (± 0.0204)                                     |                                                       | 0.8511                                                        | 0.9997 (± 0.0005)                                             |
| krvskp                                                                    | 0.0011) 125921                                         | 0.9998 (± 0.0003) 0.9998 (±                                                                                    | 0.0009) 0.0004) 0.9900 (± 0.0117)                                       | 0.0504) 0.0288) 0.0040) 0.9995                | (± 0.0008) 0.9990                                                                  | 0.0224) 0.9955 (± 0.0028)                                    | 0.9998 (± 0.0003)                                     | 0.9999 (± 0.0002)                                     | 0.9994 (± 0.0010)                                     | 0.9990 0.9995 (± 0.0007)                                      | 0.9520 (± 0.0156)                                             |
| LEDdisplaydomain7digit SpeedDating carevaluation                          | (40496) 0.0136) 146607 (40536) 0.0128) 146192 (40664)  | 0.9526 (± 0.0133) 0.9531 (± 0.8821 (± 0.0116) 0.8762 (± 0.0125) 1.0000 (± 0.0000)                              | 0.9335 (± 0.7087 (± 0.9927 (±                                           | 0.0218) 0.9569 (± 0.8794                      | (± 0.0132) 0.9539 (± 0.0108) 0.8670                                                | 0.9584 (± 0.0113) 0.8561 (±                                  | 0.9538 (± 0.0122) 0.8355 (± 0.0149) 0.9998 (± 0.0004) | 0.9537 (± 0.0141) 0.8610 (± 0.0124) 1.0000 (± 0.0000) | 0.9570 (± 0.0122) 0.8818 (± 0.0129)                   | 0.9530 (± 0.0127) 0.8734 (± 0.9999 (±                         | 0.8720 (± 0.0129) 0.9998 (± 0.0003)                           |
| dna                                                                       | 0.0016) 167140 (40670)                                 | 0.9956 (± 0.0024)                                                                                              | 0.9642 (±                                                               | 0.0187) (± 0.9999 (± 0.9949 (±                | (± 0.9973 (± 0.9937 (±                                                             | 0.0138) 0.9922 (± 0.0026) 0.9945 (± 0.0033)                  | 0.9919 (± 0.0030)                                     | 0.9942 (± 0.0035)                                     | 0.9999 (± 0.0001) 0.9955 (± 0.0025)                   | 0.0119) 0.0002) (± 0.0025)                                    | 0.9953 (± 0.0025)                                             |
| postoperativepatientdata                                                  | 0.0032) 146210 (40683) 0.2763) 167141 (40701)          | 0.4821 (± 0.2380)                                                                                              | 0.9998 (± 0.0007) 0.9951 (± 0.0027) 0.3948 (± 0.2865) 0.9233 (± 0.0188) | 0.0032) 0.0067) (± 0.1552)                    | 0.0002) 0.0031) 0.1394) 0.4631                                                     | 0.4143 (± 0.1817) 0.8624 (± 0.0201)                          | 0.5258 (± 0.1795) 0.9155 (± 0.0198)                   | 0.4738 (± 0.1472)                                     | 0.4274 (± 0.1235)                                     | 0.9954 0.3500 (±                                              | 0.3329 (± 0.1902) 0.9313 (± 0.0139)                           |
| churn                                                                     | 0.0216) 145793 (40733)                                 | 0.9321 (± 0.0230) 0.8586 (± 0.0216)                                                                            | 0.3768 0.8479 (± 0.0300)                                                | 0.3925 (± 0.0335) 0.9227                      | (± 0.0213) 0.9171 (±                                                               |                                                              |                                                       | 0.9013 (± 0.0225)                                     | 0.9205 (± 0.0245)                                     | 0.1953) 0.9238 (± 0.0202) (± 0.0225)                          | 0.8565 (± 0.0242)                                             |
| yeast Satellite                                                           | 0.0228) 167211 (40900)                                 | 0.8590 (± 0.0217) 0.9965 (± 0.0033) (± 0.0167)                                                                 | 0.8346 (± 0.9275 (±                                                     | (± 0.8550 (± 0.9840 (±                        | 0.0207) 0.8519 (± 0.0260) 0.9832                                                   | 0.8418 (± 0.0227) 0.9923 (± 0.0115)                          | 0.8483 (± 0.0248) 0.9956 (± 0.0037)                   | 0.8555 (± 0.0195) 0.9917 (± 0.0117)                   | 0.8564 (± 0.0221) 0.9761 (± 0.0423)                   | 0.8591 0.9975 (± 0.0018)                                      | 0.9964 (± 0.0048)                                             |
| MiceProtein car                                                           | 146800 (40966) 146821 (40975) 146824 (40979)           | 0.9909 1.0000 (± 0.0000) 1.0000 (± 0.0001) 1.0000 (± 0.0000) 1.0000 (± 0.0000) 0.9996 (± 0.0004) 0.9996 0.9423 | 0.0581) 0.9991 (± 0.0019) 0.9927 (± 0.0032)                             | 0.9999 (± 1.0000 (±                           | (± 0.0265) 0.0001) 0.9999 (± 0.0002) 0.9995 (± 0.0005) 0.9989 (± 0.0011)           | 0.9997 (± 0.0008) 0.9922 (± 0.0027)                          | 0.9996 (± 0.0008) 0.9998 (± 0.0004) 0.9981 (± 0.0013) | 1.0000 (± 0.0000) 1.0000 (± 0.0000) 0.9996 (± 0.0003) | 1.0000 (± 0.0001) 1.0000 (± 0.0001) 0.9995 (± 0.0004) | 1.0000 (± 0.0000) (± 0.0000) 0.9996 (± 0.0005)                | 1.0000 (± 0.0000) 1.0000 (± 0.0000) 0.9997 (± 0.0003)         |
| mfeatpixel Australian                                                     | 146818 (40981)                                         | (± 0.0004) 0.9429 (± 0.0199) (± 0.0214)                                                                        | 0.9976 (± 0.0024) 0.9216 (± 0.0278)                                     | 0.9991 0.9399                                 | 0.0001) (± 0.0007) (± 0.0178)                                                      | 0.9975 (± 0.0015) 0.9311 (± 0.0244)                          | 0.8269 (± 0.1744)                                     | 0.9289 (± 0.0187)                                     | 0.9403 (± 0.0201)                                     | 1.0000 0.9468 (± 0.0197)                                      | 0.9433 (± 0.0206)                                             |
| wilt                                                                      | 146817 (40982) 146820 (40983)                          | 0.9712 (± 0.0047) 0.9687 (± 0.0061) 0.9942 (± 0.0110) 0.9931 (± 0.0078) 0.9967 (± 0.0012)                      | 0.9245 (± 0.0126) 0.8539 (± 0.0447)                                     | 0.9660 (± 0.9929 (±                           | 0.9385 (± 0.0199) 0.9637 (± 0.0076) 0.9856 (± 0.0168) 0.9957 (± 0.0014)            | 0.9325 (± 0.0088) 0.9751 (± 0.0111)                          | 0.9442 (± 0.0081) 0.9343 (± 0.0373) 0.9860 (± 0.0051) | 0.9499 (± 0.0089) 0.9937 (± 0.0050) 0.9915 (± 0.0035) | 0.9687 (± 0.0038) 0.9909 (± 0.0103) 0.9961 (± 0.0016) | 0.9788 (± 0.0032) 0.9950 (± 0.0077) 0.9974 (± 0.0012)         | 0.9783 (± 0.0033) 0.9946 (± 0.0087) 0.9972 (± 0.0013)         |
| steelplatesfault segment                                                  | 146822 (40984)                                         | 0.9962 (± (± 0.0548)                                                                                           | 0.9867 (± 0.0037) (±                                                    | 0.9958 (±                                     | 0.0060) 0.0066) (± 0.0693)                                                         | 0.9853 (± 0.0047)                                            | 0.9024 (± 0.1109)                                     | 0.9474 (± 0.0696)                                     | 0.9506 (± 0.0569)                                     | 0.9561 (±                                                     | 0.9576 (± 0.0622)                                             |
| climatemodelsimulationcrashes sonar jasmine                               | 146819 (40994) 39 (40) 0.0580) 168911 (41143)          | 0.9596 0.9536 (± 0.0197) 0.8879 (± 0.0185)                                                                     | 0.0016) 0.0584) 0.8629 0.9151 0.8519                                    | 0.1091) 0.9371 (± 0.9453                      | 0.0018) 0.9155 0.9187 (± 0.8849 (±                                                 | 0.9509 (± 0.0655) 0.8667 (± 0.8496 (±                        | 0.8881 (± 0.0461) 0.8470 (± 0.0215)                   | 0.9685 (± 0.0224) 0.8584 (± 0.0197)                   | 0.9506 (± 0.0330) 0.8794 (± 0.0176)                   | 0.0631) 0.9580 (± 0.8904 (±                                   | 0.9663 (± 0.8861 (±                                           |
| philippine                                                                | 0.0169) 190410 (41145)                                 | 0.8772 (± 0.0143)                                                                                              | 0.9538 (± 0.9637 (± 0.0194) 0.8825 (± 0.0201) 0.8632 (± 0.0154)         | 0.0602) 0.0257) 0.8726 0.0120) 0.8660         | 0.0602) 0.0345) 0.0171) 0.0148) 0.8437 (±                                          | 0.8019 (±                                                    | 0.7991 (± 0.0226)                                     | 0.7974 (± 0.0205)                                     | 0.8643 (± 0.0153)                                     | 0.0222) 0.9751 (±                                             | 0.0195) 0.0166) 0.9685 (± 0.0055)                             |
| sylvine                                                                   | 0.0162) 168912 (41146)                                 | 0.9926 (± 0.0034)                                                                                              | (± (± 0.7735 (± 0.8931 (±                                               | (± (± 0.9883                                  | 0.0045) 0.9817                                                                     | 0.0554) 0.0159) 0.9660 (±                                    | 0.9746 (± 0.0056)                                     | 0.9731 (± 0.0065)                                     | 0.9879 (± 0.0034)                                     | 0.0138) 0.0043) 0.9972 (± 0.0017)                             | 0.9967 (± 0.0018)                                             |
| glass haberman                                                            | 0.0044) 40 (41) 0.0203) 42 (43)                        | 0.9627 (± 0.0197) 0.7467 (± 0.0740)                                                                            | 0.9882 (± 0.0043) 0.9674 (± 0.0201) 0.7007 (± 0.0832)                   | 0.9435 0.6804                                 | (± (± (± 0.0174) (± 0.0918)                                                        | 0.0218) 0.0062) 0.8870 (± 0.6687 (±                          | 0.8656 (± 0.0389) 0.6321 (± 0.1074)                   | 0.9109 (± 0.0482) 0.6576 (± 0.0553)                   | 0.9366 (± 0.0365) 0.6829 (± 0.1120)                   | 0.9749 (± 0.0200) 0.7021 (± 0.0857)                           | 0.9709 (± 0.0281) 0.6893 (± 0.0864)                           |
|                                                                           | 0.0870) 3540 (448) 0.1051)                             | 0.9076 (± 0.0796) 0.8753                                                                                       | 0.0096) 0.8860 (± 0.0582) 0.6117 (± 0.1130) 0.7841 (± 0.1073)           | 0.6179 (±                                     | (± 0.9586 (± 0.6779 (± 0.0885) 0.8646 (±                                           | 0.0422) 0.0933) 0.9378 (±                                    | 0.8221 (± 0.2038)                                     | 0.8821 (± 0.1180)                                     | 0.6241 (± 0.2107)                                     | 0.8990 (±                                                     | 0.8712 (± 0.0928)                                             |
| analcatdata_boxing1 spambase irish                                        | 43 (44) 3543 (451)                                     | 0.9913 (± 0.0064) 1.0000 (± 0.0000) 0.9425 (± 0.0065)                                                          | 0.1232) 0.9550 0.9999                                                   | 0.0098) 0.9904 0.0003) 1.0000                 | (± 0.0065) (± 0.0000)                                                              | 0.0627) 0.9718 (± 0.0092) 1.0000 (±                          | 0.9819 (± 0.0076) 1.0000 (± 0.7836 (± 0.0093)         | 0.9786 (± 0.0078) 1.0000 (± 0.7943 (± 0.0037)         | 0.9901 (± 0.0061) 0.9358 (± 0.0641)                   | 0.1038) 0.9909 (± 1.0000 (±                                   | 0.9904 (± 0.0062) 1.0000 (±                                   |
|                                                                           | 14969 (4538)                                           | 1.0000 (± 0.0001)                                                                                              | (± 0.0064) 0.0025) 0.0089) 0.8380                                       | 0.0108) 0.9164                                | (± 0.0070)                                                                         | 0.7616 (± 0.0091)                                            | 0.0000) 1.0000 (± 0.0000)                             | 0.0000) 1.0000 (± 0.0000)                             | 0.9193 (± 0.0068)                                     | 0.0065) 0.0000) 0.9495 (± 0.0054)                             | 0.9407 (± 0.0082)                                             |
| GesturePhaseSegmentationProcessed analcatdata_authorship analcatdata_dmft | 0.5889                                                 | 0.9893 (± 0.9989 (± 0.9182 (± 1.0000 (±                                                                        | (± (± (± 1.0000 (± 0.0001)                                              | 1.0000 (±                                     | 0.9876 (± 0.0058) 1.0000 (± 0.0000) 0.8968 (± 0.0074) 1.0000 (± 0.0001) (± 0.0419) | 0.0000) 1.0000 (± 0.0000) 0.0294)                            | 0.5710 (± 0.0393)                                     | 0.5907 (± 0.0343)                                     | 1.0000 (± 0.0000)                                     | 1.0000 (±                                                     | 0.0000) 1.0000 (±                                             |
| splice profb                                                              | 3549 (458) 3560 (469) 45 (46) 3561 (470)               | (± 0.0404) 0.9957 (± 0.0032) 0.8062 (± 0.0620)                                                                 | 0.0001) 0.5835 (± 0.0383) 0.9952 (± 0.0030) 0.7978 (± 0.0483) (±        | (± 0.0286) (± 0.0049) (± 0.0583)              | 0.0000) (± 0.0373) (± 0.0036) (± 0.0740)                                           | 0.5792 (± 0.9933 (± 0.6538 (±                                | 0.9918 (± 0.0032) 0.6604 (± 0.0508)                   | 0.9948 (± 0.0038) 0.6347 (± 0.0577)                   | 0.5881 (± 0.0325) 0.9949 (± 0.0021) 0.5674 (± 0.0370) | 0.0000) 0.5951 (± 0.0294) 0.9955 (± 0.0030) 0.6550 (± 0.0560) | 0.0000) 0.5943 (± 0.0260) 0.9947 (± 0.0033) 0.6850 (± 0.0533) |
| tae                                                                       | 47 (48)                                                | 0.8113 (± 0.0769) 0.8436                                                                                       | 0.5464 0.9764 0.5649 0.7170 (±                                          | 0.5834 0.9944 0.7255 0.8005 (±                | 0.6078 0.9943 0.6460 0.0689) 0.8131                                                | 0.0033) 0.6678 (±                                            | 0.6421 (± 0.1195)                                     | 0.7020 (± 0.0664)                                     | 0.8313 (± 0.0742)                                     | 0.8254 (± 0.0639)                                             | 0.8300 (± 0.0783)                                             |
| heartc labor                                                              | 48 (49)                                                | 0.9194 (± 0.0526) 0.9750 (± 0.0527)                                                                            | 0.9020 (± 0.9542 (±                                                     | 0.9178 (± 0.9375 (±                           | (± 0.0027) (± 0.0664) (± 0.0725) 0.9171 (± 0.9833 (±                               | 0.0455) 0.0982) 0.9138 (± 0.0263) 0.9875 (±                  | 0.9112 (± 0.0422) 0.9750 (± 0.0791)                   | 0.9128 (± 0.0368) 0.9833 (± 0.0527)                   | 0.9036 (± 0.0536) 0.9875 (± 0.0395)                   | 0.9212 (± 0.0306)                                             | 0.9230 (±                                                     |
| tictactoe                                                                 | 4 (4) 49 (50)                                          | 1.0000 (± 0.0000)                                                                                              | 0.0741) 0.0253) 0.0623) 0.0000) 0.9993                                  | 0.0714) 0.0391) 1.0000                        | 0.0316) 0.1062) 0.0000) 0.9983 (±                                                  | 0.9973 (±                                                    | 0.9987 (± 0.0014)                                     | 1.0000 (± 0.0000)                                     | 1.0000 (± 0.0000)                                     | 1.0000 (± 1.0000 (±                                           | 0.0295) 0.9875 (± 0.0395) 1.0000 (±                           |
| hearth                                                                    | 50 (51) 53 (54)                                        | 0.9153 (± 0.9708 (± 1.0000 (± 0.9078 (± 0.0357) 0.9398 (± 0.0132)                                              | 0.1084) (± 0.0008) 0.8973 (± 0.0430) 0.9031 (± 0.0122)                  | (± 0.8901 (± 0.9323 (±                        | 0.0234) 0.0527) 0.0012) 0.9108 (± 0.0309) 0.9320 (± 0.0114)                        | 0.0395) 0.0019) 0.9115 (± 0.9484 (±                          | 0.8800 (± 0.0732) 0.9342 (± 0.0197)                   | 0.9028 (± 0.0327) 0.9663 (± 0.0100)                   | 0.8698 (± 0.0493) 0.9347 (± 0.0154)                   | 0.0000) 0.0000) 0.9126 (± 0.9750 (±                           | 0.0000) 0.9112 (± 0.0350) 0.9735 (± 0.0059)                   |
| vehicle hepatitis                                                         | 54 (55)                                                | 0.9043 (± 0.0517) 0.9737 (± 0.0062) 0.8399 (± 0.1399) 0.9880 (± 0.0125)                                        | (± 0.1135) (± 0.0210)                                                   | 0.1377) 0.7939 0.0546) 0.9766                 | 0.0373) 0.0110) 0.1213) 0.8704 (± 0.0171) 0.9785 (±                                | 0.8516 (± 0.9181 (±                                          | 0.7974 (± 0.1451) 0.9714 (± 0.0232)                   | 0.7975 (± 0.1248) 0.9803 (± 0.0203)                   | 0.8636 (± 0.1093)                                     | 0.0415) 0.8781 (±                                             | 0.8718 (± 0.1112) 0.9880 (± 0.0149)                           |
| ionosphere                                                                | 145984 (59)                                            | 0.8619                                                                                                         | 0.8206 0.9278 0.0129) 0.9987                                            | 0.0042) 0.9827                                | 0.0310) 0.9967 (±                                                                  | 0.0322) 0.0118) 0.1167) 0.0565) 0.9987 (±                    |                                                       |                                                       | 0.9811 (± 0.0199)                                     | 0.0054) 0.1160) 0.9894 (± 0.0136)                             | 0.9987 (± 0.0042)                                             |
| iris cylinderbands                                                        | 59 (61) 14954 (6332)                                   | 0.9987 (± 0.0042) 0.9238 (± 0.0477)                                                                            | (± (± 0.0563) 0.8221 0.1428) 0.6778                                     | (± (± 0.0691) 0.9141                          | 0.1159) 0.0549) 0.9086 (± 0.1652)                                                  | 0.0042) 0.8229 (± 0.0717) 0.7231 (± 0.1844)                  | 0.9493 (± 0.0687) 0.8659 (± 0.0752)                   | 0.9987 (± 0.0042) 0.8793 (± 0.0672)                   | 0.9927 (± 0.0152) 0.8839 (± 0.0720)                   | 0.9987 (± 0.0042) 0.8983 (± 0.0577)                           | 0.8936 (± 0.0656) 0.7611 (± 0.1363)                           |
|                                                                           | 3602 (736)                                             | 0.7311 (± 0.1269) 0.9433 (± 0.0715)                                                                            | 0.9762 0.9947 (± 0.9067 (± (± (± 0.0597)                                | 0.1487) 0.6844 0.0413) 0.9343                 | 0.0203) 0.7256 (± 0.0625) 0.9180 (±                                                | 0.9060 (± 0.0806)                                            | 0.6856 (± 0.1932) 0.7488 (± 0.1836)                   | 0.7461 (± 0.1628) 0.9432 (± 0.0580)                   | 0.6969 (± 0.1737)                                     | 0.7583 (± 0.1434)                                             | 0.9592 (± 0.0508)                                             |
| fri_c0_100_5                                                              | 3620 (754)                                             | 0.9944 (± 0.0119)                                                                                              | (± (± (± 0.9472 (± 0.9901 (±                                            | (± (± (± (± 0.9831 (±                         | 0.0072) 0.0493) 0.9944 (±                                                          | 0.9887 (± 0.0196)                                            | 0.9633 (± 0.0598)                                     | 1.0000 (±                                             | 0.9428 (± 0.0731)                                     | 0.9427 (± 0.0676)                                             | 0.9972 (± 0.0088)                                             |
| visualizing_environmental rabe_266 visualizing_livestock                  | 3647 (782) 3731 (867)                                  | 0.8391 (± 0.1330)                                                                                              | 0.6978 0.9548 0.9972 (± 0.0088) 0.8417 (± 0.1389)                       | 0.5000 (±                                     | 0.1486) 0.1034) 0.0117) 0.8139 (± 0.1533) 0.0157)                                  | 0.8900 (± 0.0837)                                            | 0.8685 (± 0.1182)                                     | 0.0000) 0.8085 (± 0.1472)                             | 0.9931 (± 0.0176) 0.7658 (± 0.1936)                   | 0.9972 (± 0.0088) 0.8512 (± 0.1329)                           | 0.8530 (± 0.1929)                                             |
| pollen                                                                    | 3735 (871)                                             | 0.4921 (± 0.0215) 0.9701 (± 0.0505)                                                                            | 0.4782 (± 0.0234) 0.9764 (± 0.0403)                                     | 0.0190) (± 0.1127) (± 0.0196) (± 0.0778)      | 0.4824 (± 0.9764 (± 0.0499)                                                        | 0.4871 (± 0.0119) 0.9639 (±                                  | 0.5024 (± 0.9389 (± 0.1012)                           | 0.4980 (± 0.9451 (±                                   | 0.4856 (± 0.0252) 0.8479 (± 0.2554)                   | 0.4845 (± 0.0197) 0.9812 (± 0.0422)                           | 0.4937 (± 0.0213)                                             |
| analcatdata_chlamydia                                                     | 1.0000                                                 | (± 0.0000)                                                                                                     | 0.8191 0.4927 0.9090 1.0000 (±                                          | 0.0228) 0.0000) 0.4906 (± 0.5965 (± 0.9963 (± | 0.9701 (± 0.0505)                                                                  | 0.9701 (± 0.0505)                                            | 0.9701 (± 0.0505)                                     | 0.9701 (± 0.0505)                                     | 0.9701 (± 0.0505)                                     | 0.9701 (± 0.0505)                                             | 0.9701 (± 0.0505)                                             |
| 0.0166) (± 0.0000) (± 0.2052)                                             | 0.0154) 0.0845) 1.0000 (± 0.0000)                      | 0.9468 (± 0.0717)                                                                                              | (± 0.0000) (± 0.0733) 0.8871                                            | 0.0359) 0.8932 (±                             | 0.0000) 0.9975 (± 0.7375 (± 0.9839 (±                                              | 0.0503) 0.0079) 0.1229)                                      | 1.0000 0.6325                                         | 0.9465 (± 0.0751)                                     | 1.0000 (± 0.0000) 0.9507 (± 0.0541)                   | 1.0000 (± 0.9592 (±                                           | 1.0000 (± 0.9548 (± 0.0735)                                   |
| transplant fri_c3_100_5                                                   | 3739 (875) 3748 (885) 3779 (916) 3797 (934)            | 0.9917 (± 0.0051)                                                                                              | 1.0000 0.9223 0.9861 (± 0.0101)                                         | 0.0000) (± 0.0760) (± 0.0150)                 | 0.2410) 0.0119) 1.0000 0.1120) 0.9345 (± 0.0071) 0.9823 (± 0.0446) 0.9608          |                                                              | 0.9833 (± 0.0092)                                     | 0.9757 (± 0.0116)                                     | 0.9906 (± 0.0039)                                     | 0.9905 (±                                                     | 0.9916 (± 0.0062)                                             |
| socmob                                                                    |                                                        |                                                                                                                | 0.9818 0.8634 (± 0.0420)                                                | 0.9877 0.9593                                 | 0.0000) 0.9750 (± 0.0174)                                                          | 0.0068) 0.8833 (± 0.0504)                                    |                                                       | 0.9149 (± 0.0346)                                     | (± 0.0383) 0.9779                                     | 0.0000) 0.0072) (±                                            |                                                               |
|                                                                           |                                                        |                                                                                                                |                                                                         |                                               |                                                                                    |                                                              | 0.8889 (± 0.0454)                                     |                                                       | 0.9408                                                |                                                               |                                                               |
|                                                                           |                                                        |                                                                                                                |                                                                         |                                               | (± (± 0.0724) (± 0.0097) (± 0.0191)                                                |                                                              |                                                       |                                                       |                                                       |                                                               |                                                               |
|                                                                           |                                                        |                                                                                                                | 0.9619 (± 0.0191)                                                       |                                               |                                                                                    |                                                              |                                                       |                                                       |                                                       |                                                               |                                                               |
|                                                                           |                                                        | 0.9466 (± 0.0468)                                                                                              |                                                                         |                                               |                                                                                    |                                                              |                                                       |                                                       |                                                       |                                                               |                                                               |
|                                                                           | 9 (9)                                                  |                                                                                                                |                                                                         |                                               |                                                                                    |                                                              |                                                       |                                                       |                                                       |                                                               |                                                               |
| autos                                                                     |                                                        |                                                                                                                |                                                                         |                                               |                                                                                    |                                                              |                                                       |                                                       |                                                       | 0.0606) 0.0193)                                               |                                                               |

Supplementary Table 5: List of development datasets used to validate classification tasks. We only take the first 10000 rows of all datasets and drop datasets with more than 500 features or 10 classes to keep the datasets similar to our test dataset distribution. We detected overlap with the test set by checking for duplicate names and meta-data characteristics (rows, features, missing values).

| Dataset Name                      | OpenML ID   | Features   | Samples   | Targets   | Categorical Feats.   | Numerical Feats.   |
|-----------------------------------|-------------|------------|-----------|-----------|----------------------|--------------------|
| adaprior                          | 1037        | 14         | 4562      | 2         | 8                    | 6                  |
| allbp                             | 40707       | 29         | 3772      | 3         | 23                   | 6                  |
| analcatdata_asbestos              | 459         | 3          | 83        | 2         | 2                    | 1                  |
| analcatdata_cyyoung8092           | 465         | 10         | 97        | 2         | 3                    | 7                  |
| ar3                               | 1060        | 29         | 63        | 2         | 0                    | 29                 |
| ar6                               | 1064        | 29         | 101       | 2         | 0                    | 29                 |
| baseball                          | 185         | 16         | 1340      | 3         | 1                    | 15                 |
| birds                             | 40588       | 278        | 645       | 2         | 2                    | 276                |
| blogger                           | 1463        | 5          | 100       | 2         | 5                    | 0                  |
| breast-tissue                     | 1465        | 9          | 106       | 6         | 0                    | 9                  |
| cjs                               | 473         | 34         | 2796      | 6         | 2                    | 32                 |
| clean1                            | 40665       | 168        | 476       | 2         | 0                    | 168                |
| cleveland-nominal                 | 40711       | 7          | 303       | 5         | 7                    | 0                  |
| compas-two-years                  | 42192       | 13         | 5278      | 2         | 6                    | 7                  |
| confidence                        | 468         | 3          | 72        | 6         | 0                    | 3                  |
| corral                            | 40669       | 6          | 160       | 2         | 6                    | 0                  |
| delta_ailerons                    | 803         | 5          | 7129      | 2         | 0                    | 5                  |
| dermatology                       | 35          | 34         | 366       | 6         | 33                   | 1                  |
| eye_movements                     | 44130       | 20         | 7608      | 2         | 0                    | 20                 |
| GAMETES_Epistasis                 | 40646       | 20         | 1600      | 2         | 20                   | 0                  |
| grub-damage                       | 338         | 8          | 155       | 4         | 6                    | 2                  |
| heart-c                           | 49          | 13         | 303       | 2         | 7                    | 6                  |
| heart-h                           | 51          | 13         | 294       | 2         | 7                    | 6                  |
| heart-statlog                     | 53          | 13         | 270       | 2         | 0                    | 13                 |
| heloc                             | 45026       | 22         | 10000     | 2         | 0                    | 22                 |
| hill-valley                       | 1479        | 100        | 1212      | 2         | 0                    | 100                |
| ionosphere                        | 59          | 34         | 351       | 2         | 0                    | 34                 |
| JapaneseVowels                    | 375         | 14         | 9961      | 9         | 0                    | 14                 |
| jungle_chess_2pcs_endgame         | 40997       | 46         | 4704      | 3         | 26                   | 20                 |
| _panther_lion led24               | 40677       | 24         | 3200      | 10        | 24                   | 0                  |
| mc1                               | 1056        | 38         | 9466      | 2         | 0                    | 38                 |
| Midwest_Survey_nominal            | 42532       | 27         | 2778      | 10        | 27                   | 0                  |
| mw1                               | 1071        | 37         | 403       | 2         | 0                    | 37                 |
| national-longitudinal-survey-     | 43892       | 16         | 4908      | 2         | 7                    | 9                  |
| binary                            | 42793       | 2          | 75        | 4         | 0                    | 2                  |
| olindda_outliers page-blocks      | 30          | 10         | 5473      | 5         | 0                    | 10                 |
| penguins                          | 42585       | 6          | 344       | 3         | 2                    | 4                  |
| regime_alimentaire                | 42172       | 19         | 202       | 2         | 16                   | 3                  |
| ringnorm                          | 1496        | 20         | 7400      | 2         | 0                    | 20                 |
| rl                                | 44160       | 12         | 4970      | 2         | 7                    | 5                  |
| rmftsa_sleepdata                  | 679         | 2          | 1024      | 4         | 0                    | 2                  |
| scene                             | 312         | 299        | 2407      | 2         | 5                    | 294                |
| Smartphone-Based_Recognition      | 4153        | 66         | 180       | 6         | 0                    | 66                 |
| squash-stored                     | 340         | 24         | 52        | 3         | 3                    | 21                 |
| synthetic_control                 | 377         | 60         | 600       | 6         | 0                    | 60                 |
| teachingAssistant                 | 1115        | 6          | 151       | 3         | 4                    | 2                  |
| thyroid-allbp                     | 40474       | 26         | 2800      | 5         | 20                   | 6                  |
| thyroid-ann                       | 40497       | 21         | 3772      | 3         | 0                    | 21                 |
| Titanic tokyo1                    | 40704       | 3 44       | 2201      | 2         | 0 2                  | 3                  |
|                                   | 40705 45545 | 6          | 959 954   | 2 2       | 4                    | 42                 |
| Tour-and-Travels-Churn            |             |            |           |           |                      | 2                  |
| user-knowledge volcanoes-a1       | 1508        | 5 3        | 403       | 5         | 0                    | 5 3                |
|                                   | 1527        |            | 3252      | 5         | 0                    | 0                  |
| vote                              | 56 60       | 16         | 435       | 2         | 16                   |                    |
| waveform-5000 wholesale-customers | 1511        | 40 8       | 5000 440  | 3 2       | 0 1                  | 40 7               |
| xd6                               | 40693       | 9          | 973       | 2         | 9                    | 0                  |

Supplementary Table 6: List of development datasets used to validate regression tasks. We only take the first 10000 rows of all datasets and drop datasets with more than 500 features or 10 classes to keep the datasets similar to our test dataset distribution. We detected overlap with the test set by checking for duplicate names and meta-data characteristics (rows, features, missing values).

| Dataset Name                 | OpenML ID   | Features   | Samples   | Targets   | Categorical Feats.   | Numerical Feats.   |
|------------------------------|-------------|------------|-----------|-----------|----------------------|--------------------|
| AAPL_stock_price_2021_2022   | 43878       | 5          | 346       | 334       | 0                    | 5                  |
| ames_housing                 | 43926       | 80         | 2930      | 1032      | 46                   | 34                 |
| analcatdata_apnea3           | 555         | 3          | 450       | 159       | 2                    | 1                  |
| analcatdata_birthday         | 456         | 3          | 365       | 336       | 3                    | 0                  |
| analcatdata_gviolence        | 518         | 8          | 74        | 73        | 0                    | 8                  |
| analcatdata_michiganacc      | 551         | 3          | 108       | 26        | 2                    | 1                  |
| analcatdata_supreme          | 44055       | 7          | 4052      | 10        | 5                    | 2                  |
| arsenic-male-bladder         | 482         | 4          | 559       | 14        | 1                    | 3                  |
| autoMpg                      | 196         | 7          | 398       | 129       | 3                    | 4                  |
| autoPrice                    | 207         | 15         | 159       | 145       | 0                    | 15                 |
| balloon                      | 512         | 1          | 2001      | 365       | 0                    | 1                  |
| bodyfat                      | 560         | 14         | 252       | 176       | 0                    | 14                 |
| boston_corrected             | 543         | 19         | 506       | 455       | 3                    | 16                 |
| chatfield_4                  | 695         | 12         | 235       | 211       | 0                    | 12                 |
| chscase_vine2                | 689         | 2          | 468       | 160       | 0                    | 2                  |
| cloud                        | 210         | 5          | 108       | 94        | 2                    | 3                  |
| cocomo_numeric               | 1051        | 16         | 60        | 49        | 15                   | 1                  |
| CPMP-2015-runtime-regression | 41928       | 23         | 2108      | 1161      | 1                    | 22                 |
| cps_85_wages                 | 534         | 10         | 534       | 238       | 7                    | 3                  |
| cpu_act                      | 44132       | 21         | 8192      | 56        | 0                    | 21                 |
| cpu_small                    | 227         | 12         | 8192      | 56        | 0                    | 12                 |
| crimecommunitynums           | 41968       | 126        | 1994      | 46        | 0                    | 126                |
| crimecommunitynums2          | 41969       | 126        | 1994      | 46        | 0                    | 126                |
| debutanizer                  | 23516       | 7          | 2394      | 2337      | 0                    | 7                  |
| DEE                          | 42360       | 6          | 365       | 365       | 0                    | 6                  |
| delta_elevators              | 198         | 6          | 9517      | 26        | 0                    | 6                  |
| ELE-2                        | 42362       | 4          | 1056      | 1011      | 0                    | 4                  |
| fishcatch                    | 232         | 7          | 158       | 101       | 2                    | 5                  |
| GeographicalOriginalofMusic  | 4544        | 117        | 1059      | 1057      | 0                    | 117                |
| kc1-numeric                  | 1070        | 94         | 145       | 24        | 0                    | 94                 |
| kdd_coil_1                   | 567         | 11         | 316       | 166       | 3                    | 8                  |
| kidney                       | 553         | 6          | 76        | 20        | 3                    | 3                  |
| laser                        | 42364       | 4          | 993       | 191       | 0                    | 4                  |
| mauna-loa-atmospheric-co2    | 41187       | 6          | 2225      | 581       | 1                    | 5                  |
| meta                         | 566         | 21         | 528       | 436       | 2                    | 19                 |
| MIP-2016-PAR10-regression    | 41938       | 144        | 1090      | 924       | 1                    | 143                |
| mtp                          | 405         | 202        | 4450      | 800       | 0                    | 202                |
| plasma_retinol               | 511         | 13         | 315       | 257       | 3                    | 10                 |
| pm10                         | 522         | 7          | 500       | 117       | 0                    | 7                  |
| pollen                       | 529         | 4          | 3848      | 3784      | 0                    | 4                  |
| puma32H                      | 308         | 32         | 8192      | 7861      | 0                    | 32                 |
| QSAR_fish_toxycity           | 44028       | 6          | 908       | 827       | 0                    | 6                  |
| rabe_265                     | 660         | 6          | 51        | 47        | 0                    | 6                  |
| rabe_266                     | 663         | 2          | 120       | 96        | 0                    | 2                  |
| RAM_price                    | 40601       | 1          | 333       | 219       | 0                    | 1                  |
| residential_building         | 42366       | 108        | 372       | 117       | 0                    | 108                |
| S1                           | 42110       | 2          | 5000      | 15        | 0                    | 2                  |
| stock_fardamento02           | 42545       | 6          | 6277      | 113       | 1                    | 5                  |
| treasury                     | 42367       | 15         | 1049      | 570       | 0                    | 15                 |
| triazines                    | 206         | 60         | 186       | 102       | 0                    | 60                 |
| visualizing_soil             | 44056       | 4          | 8641      | 40        | 1                    | 3                  |
| weather_ankara weather_izmir | 42368 42369 | 9 9        | 321 1461  | 251 489   | 0 0                  | 9 9                |
|                              | 503         | 14         | 6574      | 779       |                      |                    |
| wind                         |             |            |           |           | 0                    | 14                 |