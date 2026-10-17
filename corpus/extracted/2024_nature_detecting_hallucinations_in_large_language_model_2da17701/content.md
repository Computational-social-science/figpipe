<!-- source: !2024-Nature-Detecting hallucinations in large language models using semantic entropy_SI&Highlights.pdf -->
<!-- source_pdf: D:\2026-AI4S\!2024-Nature-Detecting hallucinations in large language models using semantic entropy_SI&Highlights.pdf -->
<!-- pages: 31 ; extracted_by: docling 2.140.0 -->

inhibits the translation of an mRNA that they

studied, and that this inhibition correlates

directly with tRNA cleavage. Furthermore, the

authors found that ANG was associated with

cellular material that corresponds to the 80S

subunit of the ribosome, the functional riboso-

mal unit that enables active mRNA translation.

The authors carried out structural and bio-

chemical analyses of various combinations of

the 80S ribosome, ANG, tRNA (in its states of

either carrying or not carrying an amino acid)

and the protein elongation factor eEF1A (this

brings tRNA to the 'elongating' ribosome,

which has a growing chain of amino acids).

Loveland and colleagues conclude that ANG

occupies a region of the ribosome called the

A-site, which is where the ribosome accepts

the incoming amino-acid-bound tRNA (Fig. 1).

Once bound to a vacant A-site lacking a

tRNA, ANG makes key contacts with the ribo-

some that stabilize the enzyme in a catalyti-

cally active conformation capable of cleaving

tRNA. Incoming tRNAs are held by part of the

ribosome called the P-stalk. As a result, the

anticodon loop of these tRNAs is presented

to the active site of ANG. Thus, the ribosome

has a central role both in activating ANG and in

determining its substrate specificity.

ANG is implicated in the development of

amyotrophic lateral sclerosis (ALS), a fatal

neurodegenerative disease with no cure 12 .

ALS-associated mutations are found through-

out the gene encoding ANG, and many of them

result in diminished RNase activity - activity

that is required for ANG biological functions 13 .

Loveland and colleagues' findings shed light

on how some ALS-associated mutations could

affect ANG activity, even though they are not

parts of, or close to, the enzyme's catalytic

site. Those ALS-associated ANG variants might

affect the enzyme's ability to bind to the ribo-

some and, consequently, its ability to cleave

tRNA.

This study uncovers a surprising example

of relatively recent co-evolution between a

vertebrate-specific RNase and more-ancient

cellular machinery - the ribosome. In the

crowded cytoplasm, ribosomes are one of the

most common macromolecular complexes 14 .

The authors' discovery raises the question

of whether ribosomes can also participate

in other 'moonlighting' activities, such as

being an organizer or platform for functions

unrelated to protein synthesis in response to

specific stimuli, such as stress.

What is the fate of nicked tRNAs? Are they

actively removed by yet-to-be-identified

machinery, or does the ribosome or associated

proteins have roles in the unwinding of nicked

tRNA into tDRs? Do nicked tRNAs themselves

have roles in stress-response signalling or in

ribosome-associated quality controls? Once

bound to the ribosome, can ANG cleave many

incoming tRNAs? Finally, it will be important

to examine the role of ribosome-ANG-tRNA

functional interactions in relation to human

disease. Future studies to extend the biologi-

cal and clinical possibilities opened up by this

work are warranted.

Pavel Ivanov is in the Department of Medicine

at Brigham and Women's Hospital and Harvard

Medical School, Boston, Massachusetts 02115,

USA.

e-mail: pivanov@bwh.harvard.edu

1. Loveland, A. B., Koh, C. S., Ganesan, R., Jacobson, A. &amp;

Korostelev, A. A. Nature 630, 769-776 (2024).

2. Yamasaki, S., Ivanov, P., Hu, G.-F. &amp; Anderson, P.

J. Cell Biol. 185, 35-42 (2009).

3. Fett, J. W. et al. Biochemistry 24, 5480-5486 (1985).

## Artificial intelligence

4. Folkman, J. N. Engl. J. Med. 285, 1182-1186 (1971).

5. Garnett, E. R. &amp; Raines, R. T. Crit. Rev. Biochem. Mol. Biol.

57, 244-260 (2022).

6. Costa, B. et al. Proc. Natl Acad. Sci. USA 120, e2216330120

(2023).

7. Akiyama, Y. et al. Int. J. Mol. Sci. 23, 13100 (2022).

8. Holmes, A. D. et al. Nature Methods 20, 627-628 (2023).

9. Muthukumar, S., Li, C.-T., Liu, R.-J. &amp; Bellodi, C. Nature Rev.

Mol. Cell Biol. 25, 359-378 (2024).

10. Akiyama, Y., Tomioka, Y., Abe, T., Anderson, P. &amp; Ivanov, P.

RNA Biol. 18, 2546-2555 (2021).

11. Saikia, M. et al. J. Biol. Chem. 287, 42708-42725 (2012).

12. Hardiman, O. et al. Nature Rev. Dis. Primers 3, 17071 (2017).

13. Wu, D. et al. Ann. Neurol. 62, 609-617 (2007).

14. Delarue, M. et al. Cell 174, 338-349 (2018).

The author declares no competing interests.

This article was published online on 12 June 2024.

## LLMs can combat LLM hallucinations

## Karin Verspoor

The number of errors produced by an LLM can be reduced by grouping its outputs into semantically similar clusters. Remarkably, this task can be performed by a second LLM, and the method's efficacy can be evaluated by a third. See p.625

Text-generation systems powered by large language models (LLMs) have been enthusiastically embraced by busy executives and programmers alike, because they provide easy access to extensive knowledge through a natural conversational interface. Scientists too have been drawn to both using and evaluating LLMs - finding applications for them in drug discovery 1 , in materials design 2 and in proving mathematical theorems 3 . A key concern for such uses relates to the problem of 'hallucinations', in which the LLM responds to a question (or prompt) with text that seems like a plausible answer, but is factually incorrect or irrelevant 4 . How often hallucinations are produced, and in what contexts, remains to be determined, but it is clear that they occur regularly and can lead to errors and even harm if undetected. On page 625, Farquhar et al. 5 tackle this problem by developing a method for detecting a specific subclass of hallucinations, termed confabulations.

A confabulation is a hallucination that emerges from the LLM unpredictably, owing to internal factors that are unrelated to the prompt. The authors focused on measuring the uncertainty of an LLM's response to a prompt, using the hypothesis that high uncertainty is indicative of a confabulation. They estimated this uncertainty by calculating a quantity called entropy, which can be thought of as the randomness of the possible outputs generated by the model. However, Farquhar et al. measured the uncertainty at the level of meaning - rather than of words - by devising a measure of 'semantic' entropy that is based on LLM-determined similarity. They then used a third LLM to evaluate the accuracy of the response. In short, their approach amounts to fighting fire with fire: the authors propose that LLMs could form an integral component of a strategy for controlling LLMs.

The idea of using statistical language models to capture meaning is not new. In 1957, British linguist John Firth 6 asserted, "you shall know a word by the company it keeps", inspiring a body of computational linguistics research that sought to approximate meaning through the representation of shared contexts. One branch of this research casts a sentence as a mathematical matrix of words (rows) and contexts (columns), enabling the similarity between two words to be determined in terms of the distance between them in 'semantic space' 7 . This work in turn led to modern models for representing word knowledge, and ultimately to the LLMs underpinning OpenAI's ChatGPT and Google DeepMind's Gemini.

The effectiveness of LLMs stems from modelling billions of examples of words used together in sentences, paragraphs and documents, and capturing with high fidelity the statistical patterns of how those words fit of their semantic similarity, and then computed a measure of uncertainty called semantic entropy to identify responses that seem to be a confabulation. A third LLM was used to evaluate the effectiveness of the method by comparing the first LLM's response with a human-written reference answer to determine its correctness.

Figure 1 | A strategy for detecting LLM confabulations. Large language models (LLMs) can produce confabulations, a type of factually incorrect output. Farquhar et al. 5 developed a method for detecting such errors using LLMs. One LLM produced outputs to be evaluated. The authors used a second, 'semantic equivalence' LLM to group a set of possible outputs from the first LLM in terms

<!-- image -->

together. The models provide mathematical tools for computing semantic relationships. There is much debate about whether the models actually capture meaning or understand language in any epistemological or cognitive sense 8,9 , given that they lack any awareness of communicative intent or connection to realworld objects and impacts.

However, it is clear that these models perform well in a range of complex language-processing tasks that involve some comprehension. One such task is textual entailment, in which a person or model determines whether one statement can be inferred from another. For example, the text "Pat purchased a car" implies that the phrase "Pat owns a car" is correct, whereas the text "Pat rode in a car" does not.

Farquhar et al. used LLMs' ability to recognize entailments in their method for detecting confabulations. To do so, the authors took the outputs of one LLM and fed them into a second LLM that was tasked with computing 'semantic equivalence' - determining whether each of two statements implies the other (Fig. 1). The second LLM essentially detected paraphrases, and returned a set of clusters containing semantically equivalent outputs from the first LLM. Farquhar et al. showed that the uncertainty associated with these clusters (the semantic entropy) was a more effective estimate of the first LLM's uncertainty than was the standard word-based entropy. This means that even if the second LLM's calculation of semantic equivalence is not perfect, it is nonetheless helpful.

The authors evaluated their method by using a third LLM to decide whether the first LLM's response matched a reference answer that was written by a human. The team showed that this was a reasonable evaluation strategy by conducting experiments in which humans were asked to judge the equivalence of 100 pairs of model outputs and human answers. The results of the experiments indicate that two humans agree with each other to roughly the same extent that they agree with GPT-4. Nevertheless, reliance on this LLM-based method highlights a broader challenge in evaluating the performance of natural-language-processing systems at the level of meaning equivalence.

Conventional metrics for comparing texts (for example, those used in machine translation tasks) fail easily and are sensitive to lexical choice 10 . They correspond only weakly to human intuitions about text equivalence 11 . Effective evaluation of how well a system output matches a reference answer itself requires measuring meaning-level equivalence rather than word-level matching, which Farquar et al. have succeeded in doing. However, using an LLM to evaluate an LLM-based method does seem circular, and might be biased 12 .

The task of detecting confabulations is related to other problems under active investigation, including the detection of LLM-generated content in the context of academic integrity 13 and of plagiarism 14 through paraphrasing of existing texts. It is also connected to studies aimed at exposing misinformation, such as fake news, or disinformation involving the deliberate creation of false content for deceptive purposes. People can use LLMs to create reworded, misleading or fabricated content through carefully planned prompting strategies 15,16 . Although this is distinct from the sort of internal model uncertainty that drives confabulations, it would be interesting to explore whether the semantic entropy measure of Farquhar and colleagues can be used to address these problems as well.

The robustness of LLM outputs could also be improved through further experimentation with ensembles of LLMs, by deploying individual LLMs in targeted ways to assess specific aspects of the outputs. Along the way, researchers will need to grapple with the issue of whether this approach is truly controlling the output of LLMs, or inadvertently fuelling the fire by layering multiple systems that are prone to hallucinations and unpredictable errors.

Karin Verspoor is in the School of Computing Technologies, RMIT University, Melbourne, Victoria 3000, Australia and in the School of Computing and Information Systems, University of Melbourne, Melbourne, Victoria 3010, Australia.

e-mail: karin.verspoor@rmit.edu.au

1. Vert, J.-P. Nature Biotechnol. 41, 750-751 (2023).
2. Jablonka, K. M. et al. Digit. Discov. 2, 1233-1250 (2023).
3. Frieder, S. et al. Mathematical capabilities of ChatGPT. In Proc. NeurIPS 36 (eds Oh, A. et al.) (NIPS, 2023).
4. Hicks, M. T., Humphries, J. &amp; Slater, J. Ethics Inf. Technol. 26, 38 (2024).
5. Farquhar, S., Kossen, J., Kuhn, L. &amp; Gal, Y. Nature 630, 625-630 (2024).
6. Firth, J. R. Studies in Linguistic Analysis (Blackwell, 1957).
7. Landauer, T. K. &amp; Dumais, S. T. Psych. Rev. 104, 211-240 (1997).
8. Bender, E. M. &amp; Koller, A. in Proc. 58th Ann. Meet. ACL 5185-5198 (Association for Computational Linguistics, 2020).
9. Mitchell, M. &amp; Krakauer, D. C. Proc. Natl Acad. Sci. USA 120, e2215907120 (2023).
10. Zhang, T., Kishore, V., Wu, F., Weinberger, K. Q. &amp; Artzi, Y. In 8th Int.Conf.Learning Represent. (ICLR, 2020); available at https://openreview.net/forum?id=SkeHuCVFDr
11. Wang, L. L. et al. In Proc. 61st Ann. Meet. ACL Vol. 1, 9871-9889 (Association for Computational Linguistics, 2023).
12. Sun, T., He, J., Qiu, X. &amp; Huang, X. In Proc. 2022 Conf. Empirical Methods in Natural Language Processing 3726-3739 (Association for Computational Linguistics, 2022).
13. Koike, R., Kaneko, M. &amp; Okazaki, N. Proc. AAAI Conf. Artificial Intell. 38, 21258-21266 (AAAI, 2024).
14. Li, Y. et al. Preprint at arXiv https://doi.org/10.48550/ arXiv.2405.12689 (2024).
15. Taloni, A., Scorcia, V. &amp; Giannaccare, G. Eye 38, 397-400 (2024).
16. Zhang, Y. et al. Detection vs. Anti-detection: Is Text Generated by AI Detectable? In Wisdom, Well-Being, WinWin (eds Sserwanga, I. et al.) Lecture Notes in Computer Science Vol. 14596 (Springer, 2024).

The author declares competing interests; see go.nature.com/3xexykw for details.

## Detecting hallucinations in large language models using semantic entropy

[https://doi.org/10.1038/s41586-024-07421-0](https://doi.org/10.1038/s41586-024-07421-0)

Received: 17 July 2023

Accepted: 12 April 2024

Published online: 19 June 2024

Open access

<!-- image -->

Check for updates

Sebastian Farquhar 1,2 ✉ , Jannik Kossen 1,2 , Lorenz Kuhn 1,2 &amp; Yarin Gal 1

Large language model (LLM) systems, such as ChatGPT 1 or Gemini 2 , can show impressive reasoning and question-answering capabilities but often 'hallucinate' false outputs and unsubstantiated answers 3,4 . Answering unreliably or without the necessary information prevents adoption in diverse fields, with problems including fabrication of legal precedents 5 or untrue facts in news articles 6 and even posing a risk to human life in medical domains such as radiology 7 . Encouraging truthfulness through supervision or reinforcement has been only partially successful 8 . Researchers need a general method for detecting hallucinations in LLMs that works even with new and unseen questions to which humans might not know the answer. Here we develop new methods grounded in statistics, proposing entropy-based uncertainty estimators for LLMs to detect a subset of hallucinations-confabulations-which are arbitrary and incorrect generations. Our method addresses the fact that one idea can be expressed in many ways by computing uncertainty at the level of meaning rather than specific sequences of words. Our method works across datasets and tasks without a priori knowledge of the task, requires no task-specific data and robustly generalizes to new tasks not seen before. By detecting when a prompt is likely to produce a confabulation, our method helps users understand when they must take extra care with LLMs and opens up new possibilities for using LLMs that are otherwise prevented by their unreliability.

'Hallucinations' are a critical problem 9 for natural language generation systems using large language models (LLMs), such as ChatGPT 1 or Gemini 2 , because users cannot trust that any given output is correct.

Hallucinations are often defined as LLMs generating "content that is nonsensical or unfaithful to the provided source content" 9-11 but they have come to include a vast array of failures of faithfulness and factuality. We focus on a subset of hallucinations which we call 'confabulations' 12 for which LLMs fluently make claims that are both wrong and arbitrary-by which we mean that the answer is sensitive to irrelevant details such as random seed. For example, when asked a medical question "What is the target of Sotorasib?" an LLM confabulates by sometimes answering KRASG12 'C' (correct) and other times KRASG12 'D' (incorrect) despite identical instructions. We distinguish this from cases in which a similar 'symptom' is caused by the following different mechanisms: when LLMs are consistently wrong as a result of being trained on erroneous data such as common misconceptions 13 ; when the LLM 'lies' in pursuit of a reward 14 ; or systematic failures of reasoning or generalization. We believe that combining these distinct mechanisms in the broad category hallucination is unhelpful. Our method makes progress on a portion of the problem of providing scalable oversight 15 by detecting confabulations that people might otherwise find plausible. However, it does not guarantee factuality because it does not help when LLM outputs are systematically bad. Nevertheless, we significantly improve question-answering accuracy for state-of-the-art LLMs, revealing that confabulations are a great source of error at present.

We show how to detect confabulations by developing a quantitative measure of when an input is likely to cause an LLM to generate arbitrary and ungrounded answers. Detecting confabulations allows systems built on LLMs to avoid answering questions likely to cause confabulations, to make users aware of the unreliability of answers to a question or to supplement the LLM with more grounded search or retrieval. This is essential for the critical emerging field of freeform generation in which naive approaches, suited to closed vocabulary and multiple choice, fail. Past work on uncertainty for LLMs has focused on simpler settings, such as classifiers 16,17 and regressors 18,19 , whereas the most exciting applications of LLMs relate to free-form generations.

The term hallucination in the context of machine learning originally comes from filling in ungrounded details, either as a deliberate strategy 20 or as a reliability problem 4 . The appropriateness of the metaphor has been questioned as promoting undue anthropomorphism 21 . Although we agree that metaphor must be used carefully with LLMs 22 , the widespread adoption of the term hallucination reflects the fact that it points to an important phenomenon. This work represents a step towards making that phenomenon more precise.

To detect confabulations, we use probabilistic tools to define and then measure the 'semantic' entropy of the generations of an LLM-an entropy that is computed over meanings of sentences. High entropy corresponds to high uncertainty 23-25 -so semantic entropy is one way to estimate semantic uncertainties. Semantic uncertainty, the broader category of measures we introduce, could be operationalized with other factoids. For each factoid, an LLM generates questions to which that factoid might have been the answer. The original LLM then samples M possible answers to these questions. Finally, we compute the semantic entropy over the answers to each specific question, including the original factoid. Confabulations are indicated by high average semantic entropy for questions associated with that factoid. Here, semantic entropy classifies Fact 1 as probably not a confabulation because generations often mean the same thing, despite very different wordings, which a naive entropy would have missed.

Fig. 1 | Overview of semantic entropy and confabulation detection. a, Naive

<!-- image -->

entropy-based uncertainty measures variation in the exact answers, treating 'Paris', 'It's Paris' and 'France's capital Paris' as different. But this is unsuitable for language tasks for which sometimes different answers mean the same things. Our semantic entropy clusters answers which share meanings before computing the entropy. A low semantic entropy shows that the LLM is confident about the meaning. b, Semantic entropy can also detect confabulations in longer passages. We automatically decompose a long generated answer into

measures of uncertainty, such as mutual information, instead. Entropy in free-form generation is normally hard to measure because answers might mean the same thing (be semantically equivalent) despite being expressed differently (being syntactically or lexically distinct). This causes naive estimates of entropy or other lexical variation scores 26 to be misleadingly high when the same correct answer might be written in many ways without changing its meaning.

By contrast, our semantic entropy moves towards estimating the entropy of the distribution of meanings of free-form answers to questions, insofar as that is possible, rather than the distribution over the 'tokens' (words or word-pieces) which LLMs natively represent. This can be seen as a kind of semantic consistency check 27 for random seed variation. An overview of our approach is provided in Fig. 1 and a worked example in Supplementary Table 1.

Intuitively, our method works by sampling several possible answers to each question and clustering them algorithmically into answers that have similar meanings, which we determine on the basis of whether answers in the same cluster entail each other bidirectionally 28 . That is, if sentence A entails that sentence B is true and vice versa, then we consider them to be in the same semantic cluster. We measure entailment using both general-purpose LLMs and natural language inference (NLI) tools developed specifically for detecting entailment for which we show direct evaluations in Supplementary Tables 2 and 3 and Supplementary Fig. 1. Textual entailment has previously been shown to correlate with faithfulness 10 in the context of factual consistency 29 as well as being used to measure factuality in abstractive summarization 30 , especially when applied at the right granularity 31 .

Semantic entropy detects confabulations in free-form text generation across a range of language models and domains, without previous domain knowledge. Our evaluations cover question answering in trivia knowledge (TriviaQA 32 ), general knowledge (SQuAD 1.1; ref. 33), life sciences (BioASQ 34 ) and open-domain natural questions (NQ-Open 35 ) derived from actual queries to Google Search 36 . In addition, semantic entropy detects confabulations in mathematical word problems (SVAMP 37 ) and in a biography-generation dataset, FactualBio, accompanying this paper.

Our results for TriviaQA, SQuAD, BioASQ, NQ-Open and SVAMP are all evaluated context-free and involve sentence-length answers (96 ± 70 characters, mean ± s.d.) and use LLaMA 2 Chat (7B, 13B and 70B parameters) 38 , Falcon Instruct (7B and 40B) 39 and Mistral Instruct (7B) 40 . In the Supplementary Information, we further consider short-phrase-length answers. Results for FactualBio (442 ± 122 characters) use GPT-4 (ref. 1). At the time of writing, GPT-4 (ref. 1) did not expose output probabilities 41 or hidden states, although it does now. As a result, we propose a discrete approximation of our estimator for semantic entropy which allows us to run experiments without access to output probabilities, which we use for all GPT-4 results in this paper and which performs similarly well.

Our confabulation detection with semantic entropy is more robust to user inputs from previously unseen domains than methods which aim to 'learn' how to detect confabulations from a set of example demonstrations. Our method is unsupervised, meaning that we do not need labelled examples of confabulations. By contrast, supervised methods detect confabulations by learning patterns behind examples of confabulations, assuming that future questions preserve these patterns. But this assumption is often untrue in new situations or with confabulations that human overseers are unable to identify (compare Fig. 17 of ref. 24). As a strong supervised baseline, we compare to an embedding regression method inspired by ref. 24 which trains a logistic regression classifier to predict whether the model correctly answered a question on the basis of the final 'embedding' (hidden state) of the LLM. We also use the P(True) method 24 which looks at the probability with which an LLM predicts that the next token is 'True' when few-shot prompted to compare a main answer with 'brainstormed' alternatives.

Fig. 2 | Detecting confabulations in sentence-length generations. Semantic entropy outperforms leading baselines and naive entropy. AUROC (scored on the y-axes) measures how well methods predict LLM mistakes, which correlate with confabulations. AURAC (likewise scored on the y-axes) measures the

<!-- image -->

Confabulations contribute substantially to incorrect answers given by language models. We show that semantic entropy can be used to predict many incorrect model answers and to improve question-answering accuracy by refusing to answer those questions the model is uncertain about. Corresponding to these two uses, we evaluate two main metrics. First, the widely used area under the receiver operating characteristic (AUROC) curve for the binary event that a given answer is incorrect. This measure captures both precision and recall and ranges from 0 to 1, with 1 representing a perfect classifier and 0.5 representing an un-informative classifier. We also show a new measure, the area under the 'rejection accuracy' curve (AURAC). This studies the case in which the confabulation detection score is used to refuse to answer the questions judged most likely to cause confabulations. Rejection accuracy is the accuracy of the answers of the model on the remaining questions and the area under this curve is a summary statistic over many thresholds (representative threshold accuracies are provided in Supplementary Material). The AURAC captures the accuracy improvement which users would experience if semantic entropy was used to filter out questions causing the highest entropy.

performance improvement of a system that refuses to answer questions which are judged likely to cause confabulations. Results are an average over five datasets, with individual metrics provided in the Supplementary Information.

## Detecting confabulations in QA and math

In Fig. 2, we show that both semantic entropy and its discrete approximation outperform our best baselines for sentence-length generations. These results are averaged across datasets and provide the actual scores on the held-out evaluation dataset. We report the raw average score across held-out evaluation datasets without standard error because the distributional characteristics are more a property of the models and datasets selected than the method. Consistency of relative results across different datasets is a stronger indicator of variation in this case.

Semantic entropy greatly outperforms the naive estimation of uncertainty using entropy: computing the entropy of the length-normalized joint probability of the token sequences. Naive entropy estimation ignores the fact that token probabilities also express the uncertainty of the model over phrasings that do not change the meaning of an output.

Our methods also outperform the supervised embedding regression method both in- and out-of-distribution. In pale-yellow bars we show that embedding regression performance deteriorates when its training data do not match the deployment distribution-which mirrors the common real-world case in which there is a distribution shift between training and deployment 42 -the plotted value is the average metric for embedding regression trained on one of the four 'off-distribution' datasets for that evaluation. This is critical because reliable uncertainty is most important when the data distribution shifts. Semantic entropy also outperforms P(True) which is supervised 'in-context'; that is, it is adapted to the deployment task with a few training examples provided in the LLM prompt itself. The discrete variant of semantic entropy performs similarly to our standard estimator, despite not requiring exact output probabilities.

Averaged across the 30 combinations of tasks and models we study, semantic entropy achieves the best AUROC value of 0.790 whereas naive entropy (0.691), P(True) (0.698) and the embedding regression baseline (0.687) lag behind it. Semantic entropy performs well consistently, with stable performance (between 0.78 and 0.81 AUROC)

## Article

## Table 1 | Semantic entropy applied to examples

| Question                                                                                                              | Model answer                                                                                                                             | Reference answer                                | Generations for entropy                                                                                                                                                            | Prediction - Semantic entropy   | Prediction - Naive entropy   |
|-----------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|------------------------------|
| Refineries, process chemical, power generation, mills and manufacturing plants are under what sector of construction? | Refineries, process chemical, power generation, mills and manufacturing plants are under the industrial sector of construction.          | Industrial or heavy civil or heavy engineering. | • All the above are under the industrial sector of construction.                                                                                                                   | Not confabulation               | Confabulation                |
| Refineries, process chemical, power generation, mills and manufacturing plants are under what sector of construction? | Refineries, process chemical, power generation, mills and manufacturing plants are under the industrial sector of construction.          | Industrial or heavy civil or heavy engineering. | • The refineries, process chemical, power generation, mills and manufacturing plants are under the industrial sector of construction.                                              | Not confabulation               | Confabulation                |
| Refineries, process chemical, power generation, mills and manufacturing plants are under what sector of construction? | Refineries, process chemical, power generation, mills and manufacturing plants are under the industrial sector of construction.          | Industrial or heavy civil or heavy engineering. | • These are all under the heavy industrial sector of construction.                                                                                                                 | Not confabulation               | Confabulation                |
| What is the function of the stard10 protein?                                                                          | The stard10 protein functions as a negative regulator of the mTOR pathway by inhibiting the activity of the mTORC1 and mTORC2 complexes. | STARD10 is a lipid transfer protein.            | • The stard10 protein plays a crucial role in regulating the dynamics of the actin cytoskeleton and cell adhesion during cell migration and cell division.                         | Confabulation                   | Confabulation                |
| What is the function of the stard10 protein?                                                                          | The stard10 protein functions as a negative regulator of the mTOR pathway by inhibiting the activity of the mTORC1 and mTORC2 complexes. | STARD10 is a lipid transfer protein.            | • The stard10 protein functions as a negative regulator of the meiotic recombination process, specifically by inhibiting the activity of the Dmc1 recombinase enzyme.              | Confabulation                   | Confabulation                |
| What is the function of the stard10 protein?                                                                          | The stard10 protein functions as a negative regulator of the mTOR pathway by inhibiting the activity of the mTORC1 and mTORC2 complexes. | STARD10 is a lipid transfer protein.            | • The stard10 protein functions as a regulator of lipid metabolism, promoting the breakdown of lipids in the liver and inhibiting their synthesis in the liver and adipose tissue. | Confabulation                   | Confabulation                |
| Of which European country is 'fado' the national music?                                                               | Portugal.                                                                                                                                | Portugal.                                       | • 'Fado' is the national music of Portugal.                                                                                                                                        | Not confabulation               | Not confabulation            |
| Of which European country is 'fado' the national music?                                                               | Portugal.                                                                                                                                | Portugal.                                       | • 'Fado' is the national music of Portugal.                                                                                                                                        | Not confabulation               | Not confabulation            |
| Of which European country is 'fado' the national music?                                                               | Portugal.                                                                                                                                | Portugal.                                       | • Fado is the national music of Portugal.                                                                                                                                          | Not confabulation               | Not confabulation            |
| When was BSkyB's digital service launched?                                                                            | 1 October 1998.                                                                                                                          | BSkyB's digital service was launched in 1998.   | • BSkyB's digital service was launched in 1998.                                                                                                                                    | Confabulation                   | Not confabulation            |
| When was BSkyB's digital service launched?                                                                            | 1 October 1998.                                                                                                                          | BSkyB's digital service was launched in 1998.   | • BSkyB's digital service was launched on 1 October 1998.                                                                                                                          | Confabulation                   | Not confabulation            |
| When was BSkyB's digital service launched?                                                                            | 1 October 1998.                                                                                                                          | BSkyB's digital service was launched in 1998.   | • BSkyB's digital service was launched on 1 October 1998.                                                                                                                          | Confabulation                   | Not confabulation            |

across the different model families (LLaMA, Falcon and Mistral) and scales (from 7B to 70B parameters) which we study (we report summary statistics for each dataset and model as before). Although semantic entropy outperforms the baselines across all model sizes, P(True) seems to improve with model size, suggesting that it might become more competitive for very capable honest models in settings that the model understands well (which are, however, not the most important cases to have good uncertainty). We use ten generations to compute entropy, selected using analysis in Supplementary Fig. 2. Further results for short-phrase generations are described in Supplementary Figs. 7-10.

The results in Fig. 2 offer a lower bound on the effectiveness of semantic entropy at detecting confabulations. These evaluations determine whether semantic entropy and baseline methods can detect when the answers of the model are incorrect (which we validate against human correctness evaluations in Supplementary Table 4). In addition to errors from confabulations (arbitrary incorrectness), this also includes other types of mistakes for which semantic entropy is not suited, such as consistent errors learned from the training data. The fact that methods such as embedding regression are able to spot other kinds of errors, not just confabulations, but still are outperformed by semantic entropy, suggests that confabulations are a principal category of errors for actual generations.

Examples of questions and answers from TriviaQA, SQuAD and BioASQ, for LLaMA 2 Chat 70B, are shown in Table 1. These illustrate how only semantic entropy detects when the meaning is constant but the form varies (the first row of the table) whereas semantic entropy and naive entropy both correctly predict the presence of confabulations when the form and meaning vary together (second row) and predict the absence of confabulations when the form and meaning are both constant across several resampled generations (third row). In the final row, we give an example in which semantic entropy is erroneously high as a result of overly sensitive semantic clustering relative to the reference answer. Our clustering method distinguishes the answers which provide a precise date from those which only provide a year. For some contexts that would have been correct but in this context the distinction between the specific day and the year is probably irrelevant. This highlights the importance of context and judgement in clustering, especially in subtle cases, as well as the shortcomings of evaluating against fixed reference answers which do not capture the open-ended flexibility of conversational deployments of LLMs.

## Detecting confabulations in biographies

Semantic entropy is most natural for sentences that express a single proposition but the idea of semantic equivalence is trickier to apply to longer passages which express many propositions which might only agree partially 43 . Nevertheless, we can use semantic entropy to detect confabulations in longer generations, such as entire paragraphs of text. To show this, we develop a dataset of biographical generations from GPT-4 (v.0613) for 21 individuals notable enough to have their own Wikipedia page but without extensive online biographies. From each biography generated by GPT-4, we automatically extract propositional factual claims about the individual (150 factual claims in total), which we manually label as true or false.

Fig. 3 | Detecting GPT-4 confabulations in paragraph-length biographies. The discrete variant of our semantic entropy estimator outperforms baselines both when measured by AUROC and AURAC metrics (scored on the y-axis). The AUROC and AURAC are substantially higher than for both baselines. At above 80% of questions being answered, semantic entropy has the highest accuracy. Only when the top 20% of answers judged most likely to be confabulations are rejected does the answer accuracy on the remainder for the P(True) baseline exceed semantic entropy.

<!-- image -->

Applying semantic entropy to this problem is challenging. Naively, one might simply regenerate each sentence (conditioned on the text so far) and then compute semantic entropy over these regenerations. However, the resampled sentences often target different aspects of the biography: for example, one time describing family and the next time profession. This is analogous to the original problem semantic entropy was designed to resolve: the model is uncertain about the right ordering of facts, not about the facts themselves. To address this, we break down the entire paragraph into factual claims and reconstruct questions which might have been answered by those claims. Only then do we apply semantic entropy (Fig. 1) by generating three new answers to each question (selected with analysis in Supplementary Figs. 3 and 4) and computing the semantic entropy over those generations plus the original factual claim. We aggregate these by averaging the semantic entropy over all the questions to get an uncertainty score for each proposition, which we use to detect confabulations. Unaggregated results are shown in Supplementary Figs. 5 and 6.

As GPT-4 did not allow access to the probability of the generation at the time of writing, we use a discrete variant of semantic entropy which makes the further approximation that we can infer a discrete empirical distribution over semantic meaning clusters from only the generations (Methods). This allows us to compute semantic entropy using only the black-box outputs of an LLM. However, we were unable to compute the naive entropy baseline, the standard semantic entropy estimator or the embedding regression baseline for GPT-4 without output probabilities and embeddings.

In Fig. 3 we show that the discrete variant of semantic entropy effectively detects confabulations on this dataset. Its AUROC and AURAC are higher than either a simple 'self-check' baseline-which just asks the LLM whether the factoid is likely to be true-or a variant of P(True) which has been adapted to work for the paragraph-length setting. Discrete semantic entropy has better rejection accuracy performance until 20% of the questions have been rejected at which point P(True) has a narrow edge. This indicates that the questions predicted to cause confabulations are indeed more likely to be wrong.

## Discussion

Our probabilistic approach, accounting for semantic equivalence, detects an important class of hallucinations: those that are caused by a lack of LLM knowledge. These are a substantial portion of the failures at present and will continue even as models grow in capabilities because situations and cases that humans cannot reliably supervise will persist. Confabulations are a particularly noteworthy failure mode for question answering but appear in other domains too. Semantic entropy needs no previous domain knowledge and we expect that algorithmic adaptations to other problems will allow similar advances in, for example, abstractive summarization. In addition, extensions to alternative input variations such as rephrasing or counterfactual scenarios would allow a similar method to act as a form of cross-examination 44 for scalable oversight through debate 45 .

The success of semantic entropy at detecting errors suggests that LLMs are even better at "knowing what they don't know" than was argued by ref. 24-they just don't know they know what they don't know. Our method explicitly does not directly address situations in which LLMs are confidently wrong because they have been trained with objectives that systematically produce dangerous behaviour, cause systematic reasoning errors or are systematically misleading the user. We believe that these represent different underlying mechanisms-despite similar 'symptoms'-and need to be handled separately.

One exciting aspect of our approach is the way it makes use of classical probabilistic machine learning methods and adapts them to the unique properties of modern LLMs and free-form language generation. We hope to inspire a fruitful exchange of well-studied methods and emerging new problems by highlighting the importance of meaning when addressing language-based machine learning problems.

## Online content

Any methods, additional references, Nature Portfolio reporting summaries, source data, extended data, supplementary information, acknowledgements, peer review information; details of author contributions and competing interests; and statements of data and code availability are available at https://doi.org/10.1038/s41586-024-07421-0.

1. GPT-4 technical report. Preprint at https://arxiv.org/abs/2303.08774 (2023).
2. Gemini: a family of highly capable multimodal models. Preprint at https://arxiv.org/abs/ 2312.11805 (2023).
3. Xiao, Y. &amp; Wang, W. Y. On hallucination and predictive uncertainty in conditional language generation. In Proc. 16th Conference of the European Chapter of the Association for Computational Linguistics 2734-2744 (Association for Computational Linguistics, 2021).
4. Rohrbach, A., Hendricks, L. A., Burns, K., Darrell, T. &amp; Saenko, K. Object hallucination in image captioning. In Proc. 2018 Conference on Empirical Methods in Natural Language Processing (eds Riloff, E., Chiang, D., Hockenmaier, J. &amp; Tsujii, J.) 4035-4045 (Association for Computational Linguistics, 2018).
5. Weiser, B. Lawyer who used ChatGPT faces penalty for made up citations. The New York Times (8 Jun 2023).
6. Opdahl, A. L. et al. Trustworthy journalism through AI. Data Knowl. Eng. 146, 102182 (2023).
7. Shen, Y. et al. ChatGPT and other large language models are double-edged swords. Radiology 307, e230163 (2023).
8. Schulman, J. Reinforcement learning from human feedback: progress and challenges. Presented at the Berkeley EECS Colloquium. YouTube www.youtube.com/ watch?v=hhiLw5Q\_UFg (2023).
9. Ji, Z. et al. Survey of hallucination in natural language generation. ACM Comput. Surv.55, 248 (2023).
10. Maynez, J., Narayan, S., Bohnet, B. &amp; McDonald, R. On faithfulness and factuality in abstractive summarization. In Proc. 58th Annual Meeting of the Association for Computational Linguistics (eds Jurafsky, D., Chai, J., Schluter, N. &amp; Tetreault, J.) 1906-1919 (Association for Computational Linguistics, 2020).
11. Filippova, K. Controlled hallucinations: learning to generate faithfully from noisy data. In Findings of the Association for Computational Linguistics: EMNLP 2020 (eds Webber, B., Cohn, T., He, Y. &amp; Liu, Y.) 864-870 (Association for Computational Linguistics, 2020).
12. Berrios, G. Confabulations: a conceptual history. J. Hist. Neurosci. 7, 225-241 (1998).
13. Lin, S., Hilton, J. &amp; Evans, O. Teaching models to express their uncertainty in words. Transact. Mach. Learn. Res. (2022).
14. Evans, O. et al. Truthful AI: developing and governing AI that does not lie. Preprint at https://arxiv.org/abs/2110.06674 (2021).
15. Amodei, D. et al. Concrete problems in AI safety. Preprint at https://arxiv.org/abs/ 1606.06565 (2016).
16. Jiang, Z., Araki, J., Ding, H. &amp; Neubig, G. How can we know when language models know? On the calibration of language models for question answering. Transact. Assoc. Comput. Linguist. 9, 962-977 (2021).

## Article

17. Desai, S. &amp; Durrett, G. Calibration of pre-trained transformers. In Proc. 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP) (eds Webber, B., Cohn, T., He, Y. &amp; Liu, Y.) 295-302 (Association for Computational Linguistics, 2020).
18. Glushkova, T., Zerva, C., Rei, R. &amp; Martins, A. F. Uncertainty-aware machine translation evaluation. In Findings of the Association for Computational Linguistics: EMNLP 2021 (eds Moens, M-F., Huang, X., Specia, L. &amp; Yih, S.) 3920-3938 (Association for Computational Linguistics, 2021).
19. Wang, Y., Beck, D., Baldwin, T. &amp; Verspoor, K. Uncertainty estimation and reduction of pre-trained models for text regression. Transact. Assoc. Comput. Linguist. 10, 680-696 (2022).
20. Baker, S. &amp; Kanade, T. Hallucinating faces. In Proc. Fourth IEEE International Conference on Automatic Face and Gesture Recognition. 83-88 (IEEE, Catalogue no PR00580, 2002).
21. Eliot, L. AI ethics lucidly questioning this whole hallucinating AI popularized trend that has got to stop. Forbes Magazine (24 August 2022).
22. Shanahan, M. Talking about large language models. Commun. Assoc. Comp. Machinery 67, 68-79 (2024).
23. MacKay, D. J. C. Information-based objective functions for active data selection. Neural Comput. 4, 590-604 (1992).
24. Kadavath, S. et al. Language models (mostly) know what they know. Preprint at https:// arxiv.org/abs/2207.05221 (2022).
25. Lindley, D. V. On a measure of the information provided by an experiment. Ann. Math. Stat. 27, 986-1005 (1956).
26. Xiao, T. Z., Gomez, A. N. &amp; Gal, Y. Wat zei je? Detecting out-of-distribution translations with variational transformers. In Workshop on Bayesian Deep Learning at the Conference on Neural Information Processing Systems (NeurIPS, Vancouver, 2019).
27. Christiano, P., Cotra, A. &amp; Xu, M. Eliciting Latent Knowledge (Alignment Research Center, 2021); https://docs.google.com/document/d/1WwsnJQstPq91\_Yh-Ch2XRL8H\_ EpsnjrC1dwZXR37PC8/edit.
28. Negri, M., Bentivogli, L., Mehdad, Y., Giampiccolo, D. &amp; Marchetti, A. Divide and conquer: crowdsourcing the creation of cross-lingual textual entailment corpora. In Proc. 2011 Conference on Empirical Methods in Natural Language Processing 670-679 (Association for Computational Linguistics, 2011).
29. Honovich, O. et al. TRUE: Re-evaluating factual consistency evaluation. In Proc. Second DialDoc Workshop on Document-grounded Dialogue and Conversational Question Answering 161-175 (Association for Computational Linguistics, 2022).
30. Falke, T., Ribeiro, L. F. R., Utama, P. A., Dagan, I. &amp; Gurevych, I. Ranking generated summaries by correctness: an interesting but challenging application for natural language inference. In Proc. 57th Annual Meeting of the Association for Computational Linguistics 2214-2220 (Association for Computational Linguistics, 2019).
31. Laban, P., Schnabel, T., Bennett, P. N. &amp; Hearst, M. A. SummaC: re-visiting NLI-based models for inconsistency detection in summarization. Trans. Assoc. Comput. Linguist. 10, 163-177 (2022).
32. Joshi, M., Choi, E., Weld, D. S. &amp; Zettlemoyer, L. TriviaQA: a large scale distantly supervised challenge dataset for reading comprehension. In Proc. 55th Annual Meeting of the Association for Computational Linguistics 1601-1611 (Association for Computational Linguistics. 2017).
33. Rajpurkar, P., Zhang, J., Lopyrev, K. &amp; Liang, P. SQuAD: 100,000+ questions for machine compression of text. In Proc. 2016 Conference on Empirical Methods in Natural Language Processing (eds Su, J., Duh, K. &amp; Carreras, X.) 2383-2392 (Association for Computational Linguistics, 2016).
34. Tsatsaronis, G. et al. An overview of the BIOASQ large-scale biomedical semantic indexing and question answering competition. BMC Bioinformatics 16, 138 (2015).
35. Lee, K., Chang, M.-W. &amp; Toutanova, K. Latent retrieval for weakly supervised open domain question answering. In Proc. 57th Annual Meeting of the Association for Computational Linguistics 6086-6096 (Association for Computational Linguistics, 2019).
36. Kwiatkowski, T. et al. Natural questions: a benchmark for question answering research. Transact. Assoc. Comput. Linguist. 7, 452-466 (2019).
37. Patel, A., Bhattamishra, S. &amp; Goyal, N. Are NLP models really able to solve simple math word problems? In Proc. 2021 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (eds Toutanova, K. et al.) 2080-2094 (Assoc. Comp. Linguistics, 2021).
38. Touvron, H. et al. Llama 2: open foundation and fine-tuned chat models. Preprint at https://arxiv.org/abs/2307.09288 (2023).
39. Penedo, G. et al. The RefinedWeb dataset for Falcon LLM: outperforming curated corpora with web data, and web data only. In Proc. 36th Conference on Neural Information Processing Systems (eds Oh, A. et al.) 79155-79172 (Curran Associates, 2023)
40. Jiang, A. Q. et al. Mistral 7B. Preprint at https://arxiv.org/abs/2310.06825 (2023).
41. Manakul, P., Liusie, A. &amp; Gales, M. J. F. SelfCheckGPT: Zero-Resource Black-Box hallucination detection for generative large language models. In Findings of the Association for Computational Linguistics: EMNLP 2023 (eds Bouamor, H., Pino, J. &amp; Bali, K.) 9004-9017 (Assoc. Comp. Linguistics, 2023).
42. Mukhoti, J., Kirsch, A., van Amersfoort, J., Torr, P. H. &amp; Gal, Y. Deep deterministic uncertainty: a new simple baseline. In IEEE/CVF Conference on Computer Vision and Pattern Recognition 24384-24394 (Computer Vision Foundation, 2023).
43. Schuster, T., Chen, S., Buthpitiya, S., Fabrikant, A. &amp; Metzler, D. Stretching sentence-pair NLI models to reason over long documents and clusters. In Findings of the Association for Computational Linguistics: EMNLP 2022 (eds Goldberg, Y. et al.) 394-412 (Association for Computational Linguistics, 2022).
44. Barnes, B. &amp; Christiano, P. Progress on AI Safety via Debate. AI Alignment Forum www.alignmentforum.org/posts/Br4xDbYu4Frwrb64a/writeup-progress-on-ai-safety-viadebate-1 (2020).
45. Irving, G., Christiano, P. &amp; Amodei, D. AI safety via debate. Preprint at https://arxiv.org/ abs/1805.00899 (2018).

Publisher's note Springer Nature remains neutral with regard to jurisdictional claims in published maps and institutional affiliations.

<!-- image -->

Open Access This article is licensed under a Creative Commons Attribution 4.0 International License, which permits use, sharing, adaptation, distribution and reproduction in any medium or format, as long as you give appropriate

credit to the original author(s) and the source, provide a link to the Creative Commons licence, and indicate if changes were made. The images or other third party material in this article are included in the article's Creative Commons licence, unless indicated otherwise in a credit line to the material. If material is not included in the article's Creative Commons licence and your intended use is not permitted by statutory regulation or exceeds the permitted use, you will need to obtain permission directly from the copyright holder. To view a copy of this licence, visit http://creativecommons.org/licenses/by/4.0/.

- © The Author(s) 2024

## Methods

Semantic entropy as a strategy for overcoming confabulation builds on probabilistic tools for uncertainty estimation. It can be applied directly to any LLM or similar foundation model without requiring any modifications to the architecture. Our 'discrete' variant of semantic uncertainty can be applied even when the predicted probabilities for the generations are not available, for example, because access to the internals of the model is limited.

In this section we introduce background on probabilistic methods and uncertainty in machine learning, discuss how it applies to language models and then discuss our contribution, semantic entropy, in detail.

## Background

Uncertainty and machine learning. We aim to detect confabulations in LLMs, using the principle that the model will be uncertain about generations for which its output is going to be arbitrary.

One measure of uncertainty is the predictive entropy of the output distribution, which measures the information one has about the output given the input 25 . The predictive entropy (PE) for an input sentence x is the conditional entropy (H) of the output random variable Y with realization y given x,

<!-- formula-not-decoded -->

A low predictive entropy indicates an output distribution which is heavily concentrated whereas a high predictive entropy indicates that many possible outputs are similarly likely.

Aleatoric and epistemic uncertainty. We do not distinguish between aleatoric and epistemic uncertainty in our analysis. Researchers sometimes separate aleatoric uncertainty (uncertainty in the underlying data distribution) from epistemic uncertainty (caused by having only limited information) 46 . Further advances in uncertainty estimation which separate these kinds of uncertainty would enhance the potential for our semantic uncertainty approach by allowing extensions beyond entropy.

Joint probabilities of sequences of tokens. Generative LLMs produce strings of text by selecting tokens in sequence. Each token is a wordpiece that often represents three or four characters (though especially common sequences and important words such as numbers typically get their own token). To compute entropies, we need access to the probabilities the LLM assigns to the generated sequence of tokens. The probability of the entire sequence, s, conditioned on the context, x, is the product of the conditional probabilities of new tokens given past tokens, whose resulting log-probability is x x s s ∑ P P s log ( ) = log ( , ) i i i &lt; ∣ ∣ , where si is the ith output token and s&lt;i denotes the set of previous tokens.

Length normalization. When comparing the log-probabilities of generated sequences, we use 'length normalization', that is, we use an arithmetic mean log-probability, x s P s ∑ log ( , ) N i N i i 1 &lt; ∣ , instead of the sum. In expectation, longer sequences have lower joint likelihoods because of the conditional independence of the token probabilities 47 . The joint likelihood of a sequence of length N shrinks exponentially in N. Its negative log-probability therefore grows linearly in N, so longer sentences tend to contribute more to entropy. We therefore interpret length-normalizing the log-probabilities when estimating the entropy as asserting that the expected uncertainty of generations is independent of sentence length. Length normalization has some empirical success 48 , including in our own preliminary experiments, but little theoretical justification in the literature.

## Principles of semantic uncertainty

If we naively calculate the predictive entropy directly from the probabilities of the generated sequence of tokens, we conflate the uncertainty of the model over the meaning of its answer with the uncertainty over the exact tokens used to express that meaning. For example, even if the model is confident in the meaning of a generation, there are still usually many different ways for phrasing that generation without changing its meaning. For the purposes of detecting confabulations, the uncertainty of the LLM over meanings is more important than the uncertainty over the exact tokens used to express those meanings.

Our semantic uncertainty method therefore seeks to estimate only the uncertainty the LLM has over the meaning of its generation, not the choice of words. To do this, we introduce an algorithm that clusters model generations by meaning and subsequently calculates semantic uncertainty. At a high level this involves three steps:

1. Generation: sample output sequences of tokens from the predictive distribution of a LLM given a context x.
2. Clustering: cluster sequences by their meaning using our clustering algorithm based on bidirectional entailment.
3. Entropy estimation: estimate semantic entropy by summing probabilities of sequences that share a meaning following equation (2) and compute their entropy.

Generating a set of answers from the model. Given some context x as input to the LLM, we sample M sequences, {s (1) , …, s (M) } and record their token probabilities, {P(s (1) ∣x), …, P(s (M) ∣x)}. We sample all our generations from a single model, varying only the random seed used for sampling from the token probabilities. We do not observe the method to be particularly sensitive to details of the sampling scheme. In our implementation, we sample at temperature 1 using nucleus sampling (P = 0.9) (ref. 49) and top-K sampling (K = 50) (ref. 50). We also sample a single generation at low temperature (0.1) as an estimate of the 'best generation' of the model to the context, which we use to assess the accuracy of the model. (A lower sampling temperature increases the probability of sampling the most likely tokens).

Clustering by semantic equivalence. To estimate semantic entropy we need to cluster generated outputs from the model into groups of outputs that mean the same thing as each other.

This can be described using 'semantic equivalence' which is the relation that holds between two sentences when they mean the same thing. We can formalize semantic equivalence mathematically. Let the space of tokens in a language be T . The space of all possible sequences of tokens of length N is then S T ≡ N N . Note that N can be made arbitrarily large to accommodate whatever size of sentence one can imagine and one of the tokens can be a 'padding' token which occurs with certainty for each token after the end-of-sequence token. For some sentence ∈ N s S , composed of a sequence of tokens, s ∈ i T , there is an associated meaning. Theories of meaning are contested 51 . However, for specific models and deployment contexts many considerations can be set aside. Care should be taken comparing very different models and contexts.

Let us introduce a semantic equivalence relation, E( ⋅ , ⋅ ), which holds for any two sentences that mean the same thing-we will operationalize this presently. Recall that an equivalence relation is any reflexive, symmetric and transitive relation and that any equivalence relation on a set corresponds to a set of equivalence classes. Each semantic equivalence class captures outputs that can be considered to express the same meaning. That is, for the space of semantic equivalence classes C the sentences in the set C c∈ can be regarded in many settings as expressing a similar meaning such that s s s s c E ∀ , ′∈ : ( , ′). So we can build up these classes of semantically equivalent sentences by checking if new sentences share a meaning with any sentences we have already clustered and, if so, adding them into that class.

## Article

We operationalize E( ⋅ , ⋅ ) using the idea of bidirectional entailment, which has a long history in linguistics 52 and natural language processing 28,53,54 . A sequence, s, means the same thing as a second sequence, s′, only if the sequences entail (that is, logically imply) each other. For example, 'The capital of France is Paris' entails 'Paris is the capital of France' and vice versa because they mean the same thing. (See later for a discussion of soft equivalence and cases in which bidirectional entailment does not guarantee equivalent meanings).

Importantly, we require that the sequences mean the same thing with respect to the context-key meaning is sometimes contained in the context. For example, 'Paris' does not entail 'The capital of France is Paris' because 'Paris' is not a declarative sentence without context. But in the context of the question 'What is the capital of France?', the one-word answer does entail the longer answer.

Detecting entailment has been the object of study of a great deal of research in NLI 55 . We rely on language models to predict entailment, such as DeBERTa-Large-MNLI 56 , which has been trained to predict entailment, or general-purpose LLMs such as GPT-3.5 (ref. 57), which can predict entailment given suitable prompts.

We then cluster sentences according to whether they bidirectionally entail each other using the algorithm presented in Extended Data Fig. 1. Note that, to check if a sequence should be added to an existing cluster, it is sufficient to check if the sequence bidirectionally entails any of the existing sequences in that cluster (we arbitrarily pick the first one), given the transitivity of semantic equivalence. If a sequence does not share meaning with any existing cluster, we assign it its own cluster.

Computing the semantic entropy. Having determined the classes of generated sequences that mean the same thing, we can estimate the likelihood that a sequence generated by the LLM belongs to a given class by computing the sum of the probabilities of all the possible sequences of tokens which can be considered to express the same meaning as

<!-- formula-not-decoded -->

Formally, this treats the output as a random variable whose eventspace is the space of all possible meaning-classes, C, a sub-σ-algebra of the standard event-space S. We can then estimate the semantic entropy (SE) as the entropy over the meaning-distribution,

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

There is a complication which prevents direct computation: we do not have access to every possible meaning-class c. Instead, we can only sample c from the sequence-generating distribution induced by the model. To handle this, we estimate the expectation in equation (3) using a Rao-Blackwellized Monte Carlo integration over the semantic equivalence classes C,

<!-- formula-not-decoded -->

where ∣ ∣ ∣ P C ( ) = ∑ i P c P c ( ) ( ) i c x x x estimates a categorical distribution over the cluster meanings, that is, ∑iP(Ci∣x) = 1. Without this normalization step cluster 'probabilities' could exceed one because of length normalization, resulting in degeneracies. Equation (5) is the estimator giving our main method that we refer to as semantic entropy throughout the text.

For scenarios in which the sequence probabilities are not available, we propose a variant of semantic entropy which we call 'discrete' semantic entropy. Discrete semantic entropy approximates P(Ci∣x) directly from the number of generations in each cluster, disregarding the token probabilities. That is, we approximate P(Ci∣x) as ∑M I M 1 c Ci = , the proportion of all the sampled answers which belong to that cluster. Effectively, this just assumes that each output that was actually generated was equally probable-estimating the underlying distribution as the categorical empirical distribution. In the limit of M the estimator converges to equation (5) by the law of large numbers. We find that discrete semantic entropy results in similar performance empirically.

We provide a worked example of the computation of semantic entropy in Supplementary Note 1.

## Detecting confabulations in QA and math

Semantic entropy is designed to detect confabulations, that is, model outputs with arbitrary meaning. In our experiments, we use semantic uncertainty to predict model accuracy, demonstrating that confabulations make up a notable fraction of model mistakes. We further show that semantic uncertainty can be used to improve model accuracy by refusing to answer questions when semantic uncertainty is high. Last, semantic uncertainty can be used to give users a way to know when model generations are probably unreliable.

Tasks. We use the datasets BioASQ 34 , SQuAD 33 , TriviaQA 32 , SVAMP 37 and NQ-Open 35 . BioASQ is a life-sciences question-answering dataset based on the annual challenge of the same name. The specific dataset we use is based on the QA dataset from Task B of the 2023 BioASQ challenge (11B). SQuAD is a reading comprehension dataset whose context passages are drawn from Wikipedia and for which the answers to questions can be found in these passages. We use SQuAD 1.1 which excludes the unanswerable questions added in v.2.0 that are deliberately constructed to induce mistakes so they do not in practice cause confabulations to occur. TriviaQA is a trivia question-answering dataset. SVAMP is a word-problem maths dataset containing elementary-school mathematical reasoning tasks. NQ-Open is a dataset of realistic questions aggregated from Google Search which have been chosen to be answerable without reference to a source text. For each dataset, we use 400 train examples and 400 test examples randomly sampled from the original larger dataset. Note that only some of the methods require training, for example semantic entropy does not use the training data. If the datasets themselves are already split into train and test (or validation) samples, we sample our examples from within the corresponding split.

All these datasets are free-form, rather than multiple choice, because this better captures the opportunities created by LLMs to produce free-form sentences as answers. We refer to this default scenario as our 'sentence-length' experiments. In Supplementary Note 7, we also present results for confabulation detection in a 'short-phrase' scenario, in which we constrain model answers on these datasets to be as concise as possible.

To make the problems more difficult and induce confabulations, we do not provide the context passages for any of the datasets. When the context passages are provided, the accuracy rate is too high for these datasets for the latest generations of models to meaningfully study confabulations.

Models. For sentence-length generations we use: Falcon 39 Instruct (7B and 40B), LLaMA 2 Chat 38 (7B, 13B and 70B) and Mistral 40 Instruct (7B).

Baselines. In addition to reporting results for semantic entropy, discrete semantic entropy and naive entropy, we consider two strong baselines.

Embedding regression is a supervised baseline inspired by the P(IK) method 24 . In that paper, the authors fine-tune their proprietary LLM on a dataset of questions to predict whether the model would have been correct. This requires access to a dataset of ground-truth answers to the questions. Rather than fine-tuning the entire LLM in this way, we simply take the final hidden units and train a logistic regression classifier to make the same prediction. By contrast to their method, this is much simpler because it does not require fine-tuning the entire language model, as well as being more reproducible because the solution to the logistic regression optimization problem is not as seed-dependent as the fine-tuning procedure. As expected, this supervised approach performs well in-distribution but fails when the distribution of questions is different from that on which the classifier is trained.

The second baseline we consider is the P(True) method 24 , in which the model first samples M answers (identically to our semantic entropy approach) and then is prompted with the list of all answers generated followed by the highest probability answer and a question whether this answer is "(a) True" or "(b) False". The confidence score is then taken to be the probability with which the LLM responds with 'a' to the multiple-choice question. The performance of this method is boosted with a few-shot prompt, in which up to 20 examples from the training set are randomly chosen, filled in as above, but then provided with the actual ground truth of whether the proposed answer was true or false. In this way, the method can be considered as supervised 'in-context' because it makes use of some ground-truth training labels but can be used without retraining the model. Because of context-size constraints, this method cannot fit a full 20 few-shot examples in the context when input questions are long or large numbers of generations are used. As a result, we sometimes have to reduce the number of few-shot examples to suit the context size and we note this in the Supplementary Material.

Entailment estimator. Any NLI classification system could be used for our bidirectional entailment clustering algorithm. We consider two different kinds of entailment detector.

One option is to use an instruction-tuned LLM such as LLaMA 2, GPT3.5 (Turbo 1106) or GPT-4 to predict entailment between generations. We use the following prompt:

We are evaluating answers to the question {question}

Here are two possible answers:

Possible Answer 1: {text1}

Possible Answer 2: {text2}

Does Possible Answer 1 semantically entail Possible Answer 2? Respond with entailment, contradiction, or neutral.

Alternatively, we consider using a language model trained for entailment prediction, specifically the DeBERTa-large model 56 fine-tuned on the NLI dataset MNLI 58 . This builds on past work towards paraphrase identification based on embedding similarity 59,60 and BERT-style models 61,62 . We template more simply, checking if DeBERTa predicts entailment between the concatenation of the question and one answer and the concatenation of the question and another answer. Note that DeBERTa-large is a relatively lightweight model with only 1.5B parameters which is much less powerful than most of the LLMs under study.

In Supplementary Note 2, we carefully evaluate the benefits and drawbacks of these methods for entailment prediction. We settle on using GPT-3.5 with the above prompt, as its entailment predictions agree well with human raters and lead to good confabulation detection performance.

In Supplementary Note 3, we provide a discussion of the computational cost and choosing the number of generations for reliable clustering.

Prompting templates. We use a simple generation template for all sentence-length answer datasets:

Answer the following question in a single brief but complete sentence.

Question: {question}

Answer:

Metrics and accuracy measurements. We use three main metrics to evaluate our method: AUROC, rejection accuracy and AURAC. Each of these is grounded in an automated factuality estimation measurement relative to the reference answers provided by the datasets that we use.

AUROC, rejection accuracy and AURAC. First, we use the AUROC curve, which measures the reliability of a classifier accounting for both precision and recall. The AUROC can be interpreted as the probability that a randomly chosen correct answer has been assigned a higher confidence score than a randomly chosen incorrect answer. For a perfect

classifier, this is 1.

Second, we compute the 'rejection accuracy at X%', which is the question-answering accuracy of the model on the most-confident X% of the inputs as identified by the respective uncertainty method. If an uncertainty method works well, predictions on the confident subset should be more accurate than predictions on the excluded subset and the rejection accuracy should increase as we reject more inputs.

To summarize this statistic we compute the AURAC-the total area enclosed by the accuracies at all cut-off percentages X%. This should increase towards 1 as given uncertainty method becomes more accurate and better at detecting likely-inaccurate responses but it is more sensitive to the overall accuracy of the model than the AUROC metric.

In Supplementary Note 5, we provide the unaggregated rejection accuracies for sentence-length generations.

Assessing accuracy. For the short-phrase-length generation setting presented in Supplementary Note 7, we simply assess the accuracy of the generations by checking if the F1 score of the commonly used SQuAD metric exceeds 0.5. There are limitations to such simple scoring rules 63 but this method is widely used in practice and its error is comparatively small on these standard datasets.

For our default scenario, the longer sentence-length generations, this measure fails, as the overlap between the short reference answer and our long model answer is invariably too small. For sentence-length generations, we therefore automatically determine whether an answer to the question is correct or incorrect by using GPT-4 to compare the given answer to the reference answer. We use the template:

We are assessing the quality of answers to the following question: {question}

The expected answer is: {reference answer}

The proposed answer is: {predicted answer}

Within the context of the question, does the proposed answer mean the same as the expected answer? Respond only with yes or no.

We make a small modification for datasets with several reference answers: line two becomes "The following are expected answers to this question:" and the final line asks "does the proposed answer mean the same as any of the expected answers?".

In Supplementary Note 6, we check the quality of our automated ground-truth evaluations against human judgement by hand. We find that GPT-4 gives the best results for determining model accuracy and thus use it in all our sentence-length experiments.

## Detecting confabulations in biographies

In this section we describe the application of semantic entropy to confabulation detection in longer model generations, specifically paragraph-length biographies.

We introduce a biography-generation dataset-FactualBioavailable alongside this paper. FactualBio is a collection of biographies of individuals who are notable enough to have Wikipedia pages but not notable enough to have large amounts of detailed coverage, generated by GPT-4 (v.0613). To generate the dataset, we randomly sampled 21 individuals from the WikiBio dataset 64 . For each biography, we generated a list of factual claims contained in each biography using GPT-4, with 150 total factual claims (the total number is only coincidentally a

## Article

round number). For each of these factual claims, we manually determined whether the claim was correct or incorrect. Out of 150 claims, 45 were incorrect. As before, we apply confabulation detection to detect incorrect model predictions, even though there may be model errors which are not confabulations.

Prompting and generation. Given a paragraph-length piece of LLMgenerated text, we apply the following sequence of steps:

1. Automatically decompose the paragraph into specific factual claims using an LLM (not necessarily the same as the original).
2. For each factual claim, use an LLM to automatically construct Q questions which might have produced that claim.
3. For each question, prompt the original LLM to generate M answers.
4. For each question, compute the semantic entropy of the answers, including the original factual claim.
5. Average the semantic entropies over the questions to arrive at a score for the original factual claim.

We pursue this slightly indirect way of generating answers because we find that simply resampling each sentence creates variation unrelated to the uncertainty of the model about the factual claim, such as differences in paragraph structure.

We decompose the paragraph into factual claims using the following prompt:

Please list the specific factual propositions included in the answer above. Be complete and do not leave any factual claims out. Provide each claim as a separate sentence in a separate bullet point.

We found that we agreed with the decompositions in all cases in the dataset.

We then generate six questions for each of the facts from the decomposition. We generate these questions by prompting the model twice with the following:

Following this text:

{text so far}

You see the sentence:

{proposition}

Generate a list of three questions, that might have generated the sentence in the context of the preceding original text, as well as their answers. Please do not use specific facts that appear in the follow-up sentence when formulating the question. Make the questions and answers diverse. Avoid yes-no questions. The answers should not be a full sentence and as short as possible, e.g. only a name, place, or thing. Use the format "1. {question} - {answer}".

These questions are not necessarily well-targeted and the difficulty of this step is the main source of errors in the procedure. We generate three questions with each prompt, as this encourages diversity of the questions, each question targeting a different aspect of the fact. However, we observed that the generated questions will sometimes miss obvious aspects of the fact. Executing the above prompt twice (for a total of six questions) can improve coverage. We also ask for brief answers because the current version of GPT-4 tends to give long, convoluted and highly hedged answers unless explicitly told not to.

Then, for each question, we generate three new answers using the following prompt:

We are writing an answer to the question "{user question}". So far we have written:

{text so far}

The next sentence should be the answer to the following question: {question}

Please answer this question. Do not answer in a full sentence. Answer with as few words as possible, e.g. only a name, place, or thing.

We then compute the semantic entropy over these answers plus the original factual claim. Including the original fact ensures that the estimator remains grounded in the original claim and helps detect situations in which the question has been interpreted completely differently from the original context. We make a small modification to handle the fact that GPT-4 generations often include refusals to answer questions. These refusals were not something we commonly observe in our experiments with LLaMA 2, Falcon or Mistral models. If more than half of the answers include one of the strings 'not available', 'not provided', 'unknown' or 'unclear' then we treat the semantic uncertainty as maximal.

We then average the semantic entropies for each question corresponding to the factual claim to get an entropy for this factual claim.

Despite the extra assumptions and complexity, we find that this method greatly outperforms the baselines.

Entailment estimator. To compute semantic entailment between the original claim and regenerated answers, we rely on the DeBERTa entailment prediction model as we find empirically that DeBERTa predictions result in higher train-set AUROC than other methods. Because DeBERTa has slightly lower recall than GPT-3.5/4, we use a modified set-up for which we say the answers mean the same as each other if at least one of them entails the other and neither is seen to contradict the othera kind of 'non-defeating' bidirectional entailment check rather than true bidirectional entailment. The good performance of DeBERTa in this scenario is not surprising as both factual claims and regenerated answers are relatively short. We refer to Supplementary Notes 2 and 3 for ablations and experiments regarding our choice of entailment estimator for paragraph-length generations.

Baselines. We implement two baselines. First, we implement a variant of the P(True) method, which is adapted to the new setting. For each factoid, we generate a question with answers in the same way as for semantic entropy. We then use the following prompt:

Question: {question}

Here are some brainstormed ideas:

{list of regenerated answers}

Possible answer: {original answer}

Is the possible answer true? Respond with "yes" or "no".

As we cannot access the probabilities GPT-4 assigns to predicting 'yes' and 'no' as the next token, we approximate this using Monte Carlo samples. Concretely, we execute the above prompt ten times (at temperature 1) and then take the fraction of answers which was 'yes' as our unbiased Monte Carlo estimate of the token probability GPT-4 assigns to 'yes'.

As a second, simpler, baseline we check if the model thinks the answer is true. We simply ask:

Following this text:

{text so far}

You see this statement:

{proposition}

Is it likely that the statement is true? Respond with 'yes' or 'no'.

It is interesting that this method ought to perform very well if we think that the model has good 'self-knowledge' (that is, if "models mostly know what they don't know" 24 ) but in fact semantic entropy is much better at detecting confabulations.

## Data availability

The data used for the short-phrase and sentence-length generations are publicly available and the released code details how to access it. We release a public version of the FactualBio dataset as part of the code base for reproducing the paragraph-length experiments.

## Code availability

We release all code used to produce the main experiments. The code for short-phrase and sentence-length experiments can be found at github.com/jlko/semantic\_uncertainty and https://doi.org/10.5281/ zenodo.10964366 (ref. 65). The code for paragraph-length experiments can be found at github.com/jlko/long\_hallucinations and https://doi. org/10.5281/zenodo.10964366 (ref. 65).

46. Der Kiureghian, A. &amp; Ditlevsen, O. Aleatory or epistemic? Does it matter? Struct. Saf. 31, 105-112 (2009).
47. Malinin, A. &amp; Gales, M. Uncertainty estimation in autoregressive structured prediction. In Proceedings of the International Conference on Learning Representations https:// openreview.net/forum?id=jN5y-zb5Q7m (2021).
48. Murray, K. &amp; Chiang, D. Correcting length bias in neural machine translation. In Proc. Third Conference on Machine Translation (eds Bojar, O. et al.) 212-223 (Assoc. Comp. Linguistics, 2018).
49. Holtzman, A., Buys, J., Du, L., Forbes, M. &amp; Choi, Y. The curious case of neural text degeneration. In Proceedings of the International Conference on Learning Representations https://openreview.net/forum?id=rygGQyrFvH (2020).
50. Fan, A., Lewis, M. &amp; Dauphin, Y. Hierarchical neural story generation. In Proc. 56th Annual Meeting of the Association for Computational Linguistics (eds Gurevych, I. &amp; Miyao, Y.) 889-898 (Association for Computational Linguistics, 2018).
51. Speaks, J. in The Stanford Encyclopedia of Philosophy (ed. Zalta, E. N.) (Metaphysics Research Lab, Stanford Univ., 2021).
52. Culicover, P. W. Paraphrase generation and information retrieval from stored text. Mech. Transl. Comput. Linguist. 11, 78-88 (1968).
53. Padó, S., Cer, D., Galley, M., Jurafsky, D. &amp; Manning, C. D. Measuring machine translation quality as semantic equivalence: a metric based on entailment features. Mach. Transl. 23, 181-193 (2009).
54. Androutsopoulos, I. &amp; Malakasiotis, P. A survey of paraphrasing and textual entailment methods. J. Artif. Intell. Res. 38, 135-187 (2010).
55. MacCartney, B. Natural Language Inference (Stanford Univ., 2009).
56. He, P., Liu, X., Gao, J. &amp; Chen, W. Deberta: decoding-enhanced BERT with disentangled attention. In International Conference on Learning Representations https://openreview. net/forum?id=XPZIaotutsD (2021).
57. Brown, T. et al. Language models are few-shot learners. Adv. Neural Inf. Process. Syst. 33, 1877-1901 (2020).
58. Williams, A., Nangia, N. &amp; Bowman, S. R. A broad-coverage challenge corpus for sentence understanding through inference. In Proc. 2018 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (eds Walker, M. et al.) 1112-1122 (Assoc. Comp. Linguistics, 2018).
59. Yu, L., Hermann, K. M., Blunsom, P. &amp; Pulman, S. Deep learning for answer sentence selection. Preprint at https://arxiv.org/abs/1412.1632 (2014).
60. Socher, R., Huang, E., Pennin, J., Manning, C. D. &amp; Ng, A. Dynamic pooling and unfolding recursive autoencoders for paraphrase detection. In Proceedings of the 24th Conference on Neural Information Processing Systems (eds Shawe-Taylor, J. et al.) (2011)
61. He, R., Ravula, A., Kanagal, B. &amp; Ainslie, J. Realformer: Transformer likes residual attention. In Findings of the Association for Computational Linguistics: ACL-IJCNLP 2021 (eds Zhong, C., et al.) 929-943 (Assoc. Comp. Linguistics, 2021).
62. Tay, Y. et al. Charformer: fast character transformers via gradient-based subword tokenization. In Proceedings of the International Conference on Learning Representations https://openreview.net/forum?id=JtBRnrlOEFN (2022).
63. Kane, H., Kocyigit, Y., Abdalla, A., Ajanoh, P. &amp; Coulibali, M. Towards neural similarity evaluators. In Workshop on Document Intelligence at the 32nd conference on Neural Information Processing (2019).
64. Lebret, R., Grangier, D. &amp; Auli, M. Neural text generation from structured data with application to the biography domain. In Proc. 2016 Conference on Empirical Methods in Natural Language Processing (eds Su, J. et al.) 1203-1213 (Association for Computational Linguistics, 2016).
65. Kossen, J., jlko/semantic\_uncertainty: Initial release v.1.0.0. Zenodo https://doi.org/ 10.5281/zenodo.10964366 (2024).

Acknowledgements We thank G. Irving, K. Perlin, J. Richens, L. Rimell and M. Turpin for their comments or discussion related to this work. We thank K. Handa for his help with the human evaluation of our automated accuracy assessment. We thank F. Bickford Smith and L. Melo for their code review. Y.G. is supported by a Turing AI Fellowship funded by the UK government's Office for AI, through UK Research and Innovation (grant reference EP/V030302/1), and delivered by the Alan Turing Institute.

Author contributions S.F. led the work from conception to completion and proposed using bidirectional entailment to cluster generations as a way of computing entropy in LLMs. He wrote the main text, most of the Methods and Supplementary Information and prepared most of the figures. J.K. improved the mathematical formalization of semantic entropy; led the extension of semantic entropy to sentence- and paragraph-length generations; wrote the code for, and carried out, all the experiments and evaluations; wrote much of the Methods and Supplementary Information and prepared drafts of many figures; and gave critical feedback on the main text. L.K. developed the initial mathematical formalization of semantic entropy; wrote code for, and carried out, the initial experiments around semantic entropy and its variants which demonstrated the promise of the idea and helped narrow down possible research avenues to explore; and gave critical feedback on the main text. Y.G. ideated the project, proposing the idea to differentiate semantic and syntactic diversity as a tool for detecting hallucinations, provided high-level guidance on the research and gave critical feedback on the main text; he runs the research laboratory in which the work was carried out.

Competing interests S.F. is currently employed by Google DeepMind and L.K. by OpenAI. For both, this paper was written under their University of Oxford affiliation. The remaining authors declare no competing interests.

## Additional information

Supplementary information The online version contains supplementary material available at https://doi.org/10.1038/s41586-024-07421-0.

Correspondence and requests for materials should be addressed to Sebastian Farquhar. Peer review information Nature thanks Mirella Lapata and the other, anonymous, reviewer(s) for their contribution to the peer review of this work.

Reprints and permissions information is available at http://www.nature.com/reprints.

## Article

Extended Data Fig. 1 | Algorithm outline for bidirectional entailment clustering. Given a set of outputs in response to a context, the bidirectional entailment answer returns a set of sets of outputs which have been classified as sharing a meaning.

## Supplementary information

## Detecting hallucinations in large language models using semantic entropy

In the format provided by the authors and unedited

Nature | www.nature.com/nature

1887

1888

1889

1890

1891

1892

1893

1894

1895

1896

1897

1898

1899

1900

1901

1902

1903

1904

1905

1906

1907

1908

1909

1910

1911

1912

1913

1914

1915

1916

1917

## Supplementary Material

## Note 1: Worked Example of Semantic Entropy Calculation

This note provides a worked example of the calculation of semantic entropy. As a worked example, suppose that we have asked "Where is the Eiffel Tower?". The model generates five answers with the length-normalised sequence log-probabilities 1N ∏Ni p(si | si) (given in the first column). In this hypothetical example, we happened to sample the literal string "Paris." twice, because we are just randomly sampling from the language model which assigns the string high probability. But we also found a different string that was equivalent to it, as well as some wrong answers. Note that in the case of model APIs which do not report the log-probabilities (such as GPT-4 at time of writing) we will not have the final number, just the text. To compute the semantic entropy, we cluster these generations into clusters that can be considered to mean the same thing. We also add up the probabilities associated

| Generation    |    p |   Naive entropy - p(si) |   Naive entropy - log[p(si)] |   Naive entropy - p(si) log[p(si)] | Semantic entropy - ∑si∈Cj p(si)   | Semantic entropy - p(Cj)   | Semantic entropy - log[p(Cj)]   |   Semantic entropy - p(Cj) log[p(Cj)] |
|---------------|------|-------------------------|------------------------------|------------------------------------|-----------------------------------|----------------------------|---------------------------------|---------------------------------------|
| "Paris."      | 0.20 |                    0.33 |                        -0.48 |                              -0.16 | 0.55                              | 0.90                       | -0.04                           |                                 -0.04 |
| "Paris."      | 0.20 |                    0.33 |                        -0.48 |                              -0.16 | -                                 | -                          | -                               |                                       |
| "It's Paris." | 0.15 |                    0.25 |                        -0.61 |                              -0.15 | -                                 | -                          | -                               |                                       |
| "Rome."       | 0.05 |                    0.08 |                        -1.09 |                              -0.09 | 0.05                              | 0.08                       | -1.09                           |                                 -0.09 |
| "New York."   | 0.01 |                    0.02 |                        -1.79 |                              -0.03 | 0.01                              | 0.02                       | -1.79                           |                                 -0.03 |
| Sum           | 0.61 |                    1.00 |                        -4.45 |                              -0.59 | 0.61                              | 1.00                       | -2.92                           |                                 -0.16 |

1918 1919 1920 1921 1922 1923 1924 1925 1926 1927 1928 1929 1930 1931 1932 Supplementary Table 1: Worked example of Semantic Entropy Calculation. The raw token sequence probabilities for each generation, p, are in the first column. Note that they do not sum to one because they are the probabilities associated with each actually sampled outcome, and if we sample many generations their sum will exceed one. To calculate the naive entropy of the output distribution, in the second column we compute an estimator of the normalised probability for each generated sequence, p(si), by dividing each probability by the sum of the first column. These now do sum to one (up to a rounding error). One way to estimate the naive entropy would then be to multiply each log-probability by the probability, sum them (and multiply by -1, not shown). For the semantic entropy, we instead look at the probabilities summed up within each meaning-cluster. We compute log-probabilities in the same way, and then compute the entropy of the resulting distribution. The resulting entropy is much lower, because several generations meant the same thing as each other (final column). All values to two decimal places.

with each one. This value is reported in the fifth column (the first under the heading "Semantic entropy"). To compute the semantic entropy we compute the negative sum of the expectation of the log-probabilities (Eq. (5)). That is, we get the result 0.16 = -0.9 log(0.9) - 0.08 log(0.08) - 0.02 log(0.02).

For the "discrete" variant of semantic entropy we effectively treat the probability of sampling each of the generations as uniform, by using it as an empirical distribution that approximates the underlying distribution. This means that for the "Paris." cluster we get a weight of 0.6=0.2+0.2+0.2 and a weight of 0.2 for the other two clusters. That is, the discrete semantic entropy here is 0.41 = -0.6 log(0.6)-0.2 log(0.2)-0.2 log(0.2).

Although these two methods produce different absolute results, we find that in practice they tend to agree fairly well on relative ordering, which is what is used in practice to classify confabulations. As a result, the cluster approximation of semantic entropy is a fairly good alternative in cases where the log-probabilities are not disclosed.

## Note 2: Choosing an Entailment Estimator

## Sentence-length Generations

We confirm that the bi-directional entailment classifier works as expected. Prior work has show that in some settings NLI methods can systematically fail 78 , so we seek to ascertain whether these failures substantially affect typical question-answering. Two raters manually labeled 100 pairs of sentence-length generations from LLaMA 2 Chat 70B for three of our datasets for entailment, recording whether they believed that sentence A entailed sentence B. They rated each entailment as: entailment, neutral, contradiction. For the purpose of measuring agreement we combine the neutral and contradiction ratings, because our method is searching for positive entailment. We found that the human raters agreed with each other (87%) at roughly the same rate that they on average agreed with GPT-4 (87%) while they agreed with GPT-3.5 only

1933

1934

1935

1936

1937

1938

1939

1940

1941

1942

1943

1944

1945

1946

1947

1948

1949

1950

1951

1952

1953

1954

1955

1956

1957

1958

1959

1960

1961

1962

1963

1964

1965

1966

1967

1968

1969

1970

1971

1972

1973

1974

1975

1976

1977

1978

|   1979 |               |   DeBERTa |   LLaMA 2 Chat 70B |   GPT-3.5 |   GPT-4 | Human A   | Human B   |
|--------|---------------|-----------|--------------------|-----------|---------|-----------|-----------|
|   1980 | Human A       |      0.81 |               0.78 |      0.83 |    0.89 | -         | 0.87      |
|   1981 | Human B       |      0.78 |               0.80 |      0.84 |    0.85 | 0.87      | -         |
|   1982 | Human Average |      0.80 |               0.79 |      0.83 |    0.87 | -         | -         |

1983

1984

1985

1986

1987

1988

1989

1990

1991 1992 1993 1994 1995 1996 1997 1998 1999 2000 slightly less on average (83%). As a result, because GPT-3.5 is more than an order of magnitude cheaper, we use GPT-3.5 for all entailment calculations for sentence-length generations on SQuAD, TriviaQA, BioASQ, SVAMP, and NQ Open. Presumably our method would perform better with a more expensive entailment estimator. Supplementary table 2 shows the detailed agreement results between the human raters and the entailment estimation.

2001

2002

2003

2004

2005

2006

2007

2008

2009

2010

2011

2012

2013

2014

2015

2016

2017

2018

2019

2020

2021

2022

2023

2024

In addition to validating human agreement with the entailment models, we also

investigate the performance of semantic entropy with different entailment strategies.

In supplementary table 3, we report AUROC values of semantic entropy with various

entailment models for predictions from a LLaMA 2 Chat 70B model on TriviaQA,

SQuAD, and BioASQ. The LLaMA 2 Chat 70B model performs worst, followed by the

purpose-built DeBERTa model and GPT models, where this time version 3.5 slightly

outperforms version 4 on average. For these experiments, unlike our main results, we

used only 8 generations (normally 10) to estimate the entropy and measured accuracy

relative to the reference answer using LLaMA 2 Chat 70B (normally GPT-4, see section

on 'Assessing Accuracy').

Supplementary Table 2: Manual entailment evaluation. Inter-rater agreement on entailment classification for pairs of sentence-length answers produced by LLaMA 2 Chat 70B to 100 questions from each of SQuAD, TriviaQA, and BioASQ (600 answers in total). On average, the human raters agreed with each other to approximately the same extent that they agreed with GPT-4, while GPT-3.5 was only slightly less predictive of human-assessed entailment.

Supplementary Table 3: Entailment Method Ablation. AUROC values for semantic entropy when using different models to compute entailment for sentence-length generations from LLaMA 2 Chat 70B. Semantic entropy performs better when prompted GPT models predict entailment rather than a purpose-built DeBERTa model.

|          |   DeBERTa |   LLaMA 2 Chat 70B |   GPT-3.5 |   GPT-4 |
|----------|-----------|--------------------|-----------|---------|
| TriviaQA |      0.83 |               0.70 |      0.85 |    0.83 |
| SQuAD    |      0.76 |               0.71 |      0.77 |    0.80 |
| BioASQ   |      0.75 |               0.73 |      0.87 |    0.79 |
| Average  |      0.78 |               0.71 |      0.83 |    0.80 |

## Paragraph-length Generations

In supplementary figure 1, we report our experiments for several entailment prediction variants for paragraph-length generations, in addition to our default non-defating bidirectional DeBERTa method. We also experimented with several entailment variants: "GPT-4 two-way" asks GPT-4 to evaluate whether the sentences mean the same thing directly ("Do the following two possible answers to the subquestion mean the same thing?" instead of "Does Possible Answer 1 semantically entail. . . "); "GPT-4 'equivalent"' instead asks "Are the following two possible answers to the subquestion semantically equivalent?"; while "GPT-4 simultaneous 'equivalent' " provides all of the possible answers and asks "Are the following answers equivalent?". All of these methods were substantially worse.

## Note 3: Limitations to Clustering by Entailment

In idealized examples, it is clear when two sentences do or do not mean the same thing as each other. In practice, it can sometimes be that sentence A seems to mean the same as B, and B the same as C, but A and C don't seem to mean the same thing. That is, because semantic equivalence is fuzzy it does not always intuitively behave transitively, meaning that the assumptions behind our equivalence classes do not hold in practice.

<!-- image -->

2089

2090

2091

2092

2093

2094

Supplementary Figure 1: Entailment method choice for paragraph biographies. Implementing the non-defeating bi-directional entailment with DeBERTa provided the best empirical results for paragraph biography confabulation detection.

| 2095           | Similarly, there are cases where bi-directional entailment does not mean that two                                                                                       |
|----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2096 2097      | sentences mean the same thing. For example, "John drove his car to the store." and                                                                                      |
| 2098 2099      | "John went to the store in his car." generally imply each other and would be marked                                                                                     |
| 2100 2101 2102 | as "entailment" by most classifiers, and this reflects the fact that they mean more- or-less the same thing. But, for example, this depends somewhat on the context and |
| 2103 2104      | various aspects of implicature 76 . For example, if we have other reasons to think that                                                                                 |
| 2105 2106      | John might have been the owner of the car but a passenger, rather than the driver,                                                                                      |
| 2107           | then we might judge the two sentences to not mean the same thing as each other.                                                                                         |
| 2108 2109      | As an alternative example of a failure of bi-directional entailment to correspond with                                                                                  |
| 2110           | semantic equivalence, sentences with scalar adverbs such as "Paris might be in France"                                                                                  |
| 2111 2112      | and "Paris might not be in France" can entail each other while meaning something                                                                                        |
| 2113 2114      | quite different 77 .                                                                                                                                                    |
| 2115           |                                                                                                                                                                         |
| 2116           |                                                                                                                                                                         |

For questions whose answers are straightforward, relatively objective, factual, and not vague these problems may not be significant. In particular, we did not observe any of these problems arising in manual inspection of outputs during any of our experiments. Nevertheless, for subtle situations and applications we would encourage practitioners to check these assumptions.

## Note 4: Computational Cost and Choosing the Number of Generations

The bi-directional equivalence algorithm is combinatorially complex in M, the number of samples generated, as it requires (M2 )-many comparisons in the worst-case. In practice, however, the computational cost is small compared to the cost of generating sequences.

First, M does not necessarily need to be very large. We show how the confabulationdetection performance (measured by AUROC) changes with M for sentence-length generations in supplementary figure 2 and for FactualBio paragraphs in supplementary figure 3. For sentence-length generations, after roughly M = 5 there are diminishing returns, although going up to M = 10 can still help. In this paper, we use M = 10 for sentence-length generations as well as short-phrase generations. For this ablation, we produce generations using LLaMA 2 Chat 70B but several experimental characteristics differ from those of our main results. We check entailment using GPT-4 (standardly GPT-3.5), measure accuracy using LLaMA 2 Chat 70B (standardly GPT-4), and use 8 generations to estimate entropy (standardly 10). For paragraph-length biographies, we find that four total factoids (three new generations plus the original factoid) seems optimal (see supplementary figure 3). Unlike the standard setting, more generations is not strictly better, because it decreases the relative weight on the original factoid which increases the risk of a badly posed question that generates irrelevant answers.

<!-- image -->

2194

2195

2196

2197

2198

2199

2200

2201

2202

2203

2204

2205

2206

2207

2208

Supplementary Figure 2: Number of sentence-length generations used for entropy. We find diminishing returns to increasing the number of generations sampled for the semantic entropy estimation, but select 10 as a reasonable number for results in this paper. The numbers annotating p(True) illustrate the number of few-shot examples we were able to include without exceeding the maximal input size for each dataset and number of generations.

Second, when using the DeBERTa-large model, it is so much smaller than the main language model, each pair comparison is much faster than generating even one token from the main model. Using GPT-3.5 to do clustering is considerably more expensive than DeBERTa.

Supplementary Figure 3: Number of factoid generations used in paragraphlength biographies. We find that confabulation-detection performance is not very sensitive to the number of generations, but that four total factoids per question (including the original one) results in competitive performance.

<!-- image -->

Third, because semantic equivalence is transitive we only need to compare one member of each equivalence class to the remaining sequences (see algorithm in Extended Data Figure 1). The number of semantic clusters in our tasks is empirically often quite low which means that far fewer than the worst-case number of comparisons are actually needed in practice. In supplementary figure 4, we show some empirical numbers of clusters for several key datasets.

Fourth, because the LLM often generates identical sequences in practice, we can cache entailments. For example, if the LLM's three generations in response to a question are "Paris.", "It's in Paris.", and "Paris." we can do a (very computationally cheap) string level comparison of the final "Paris." to the previous generations and, on finding that it is the identical text to the earlier string, we can use the previously calculated entailments. We find that in practice this reduces the computational costs

<!-- image -->

2269

2270

2271

2272

2273

2274

2275

2276

2277

2278

2279

2280

2281

2282

2283

2284

2285

2286

2287

2288

2289

2290

2291

2292

2293

2294

2295

2296

2297

2298

2299

2300

Supplementary Figure 4: In many cases, relatively few clusters are found, which can improve computational efficiency. The easiest dataset (TriviaQA) generally has fewest clusters because the answers are confident. In our results for the paragraphlength task, we use 4-factoids per question as shown in (supplementary figure 4e), but increasing the number of generations does not greatly increase the number of clusters (supplementary figure 4f). All sentence-length-generation plots are for LLaMA 2 Chat 70B while the paragraph-generation plots are GPT-4.

by 51.4% for TriviaQA, 12.3% for BioASQ, and 18.0% for SQuAD (with the size of the improvement caused by the proportion of identical answers produced by the model for those datasets).

## Note 5: Further Details for Sentence-Length Generations.

Here, we provide an unaggregated view of the sentence-length AUROCs which form Figure 2. Individual datasets and models follow a very similar pattern to the average, as shown in supplementary figure 5

We also provide a more detailed view of the rejection accuracies at proportions of answers retained for sentence-length generations in supplementary figure 6.

Supplementary Figure 5: Sentence-length confabulation detection-full AUROC. An unaggregated view of the AUROCs shown in Figure 2.

<!-- image -->

## Note 6: Assessing Model Accuracy

We check the quality of our automated ground-truth evaluation (using GPT-4 to compare the model generation with the reference answer) against human judgement by hand on sentence-length answers produced by LLaMA 2 Chat 70B responding to 100 questions from TriviaQA, SQuAD, and BioASQ. In each case, we check whether a generated answer matches the reference answer. Even if doing this reveals that the reference answer is wrong, which sometimes happens, we are interested in knowing whether humans and the automatic methods agree on the match, not on whether they know the actual correct answer. Supplementary table 4 shows the two human raters

2301

2302

2303

2304

2305

2306

2307

2308

2309

2310

2311

2312

2313

2314

2315

2316

2317

2318

2319

2320

2321

2322

2323

2324

2325

2326

2327

2328

2329

2330

2331

2332

2333

2334

2335

2336

2337

2338

2339

2340

2341

2342

2343

2344

2345

2346

<!-- image -->

2372

2373

2374

2375

2376

2377

2378

2379

2380

2381

2382

2383

2384

2385

2386

2387

2388

2389

2390

2391

2392

Supplementary Figure 6: Sentence-length confabulation detectionrejection accuracy. A more detailed view of the rejection accuracies of the figures provides further elaboration of the findings in Figure 2.

agreed with each other at roughly the same rate (92%) as they agreed with GPT-4 on average (93%). While GPT-3.5 is only slightly worse, in order to get the best groundtruth estimation feasible, we use GPT-4 to compare the generated answer with the reference answers provided in the dataset for results in this paper.

## Note 7: Results for Short-Phrase Generation

In the main text, we provide results for sentence-length and paragraph-length generation. Here, we show results for a "short-phrase" scenario where we prompt the model to "Answer the following question as briefly as possible". Additionally, we here

Supplementary Table 4: Ground truth evaluation. We evaluate different automatic accuracy measures against human evaluation on sentence-length answers produced by LLaMA 2 Chat 70B on 100 randomly chosen questions from TriviaQA, SQuAD, and BioASQ. We find that GPT-4 agrees with both human raters at roughly the same level as they agree with each other.

|               |   F1 |   LLaMA 2 Chat 70B |   GPT-3.5 |   GPT-4 | Human A   | Human B   |
|---------------|------|--------------------|-----------|---------|-----------|-----------|
| Human A       | 0.48 |               0.92 |      0.88 |    0.92 | -         | 0.92      |
| Human B       | 0.47 |               0.93 |      0.90 |    0.93 | 0.92      | -         |
| Human Average | 0.47 |               0.92 |      0.89 |    0.93 | -         | -         |

Supplementary Figure 7: Short-Phrase confabulation detection. With a prompt that encourages short generations, we achieve a lower average answer length (15.9±21.8 characters compared to 95.6±69.6 for sentence-length generations). Semantic entropy still works well compared to p(True) and embedding regression, although its advantage over naive entropy is smaller to due to the lower syntactic variability of the shorter generations.

<!-- image -->

2393

2394

2395

2396

2397

2398

2399

2400

2401

2402

2403

2404

2405

2406

2407

2408

2409

2410

2411

2412

2413

2414

2415

2416

2417

2418

2419

2420

2421

2422

2423

2424

2425

2426

2427

2428

2429

2430

2431

2432

2433

2434

2435

2436

2437

2438

<!-- image -->

2464

2465

2466

2467

2468

2469

2470

2471

2472

2473

2474

2475

2476

2477

2478

2479

Supplementary Figure 8: Short-Phrase confabulation detection-Noninstruction-tuned models. Models that have not been instruction-tuned have slightly different output-distribution characteristics to instruction-tuned models. However, we find that both classes of models show broadly similar results and that semantic entropy continues to outperform baselines in this setting.

employ five few-shot QA demonstrations before the main question, all following the template introduced above, which further encourages the LLM to predict with brevity as the reference answers are usually very short for our selection of datasets. The shortphrase scenario is less practically relevant, as users commonly interact with longer

LLM generations, although some settings value brevity and directness.

2480 2481 2482 2483 2484 For short-phrase generations we use the DeBERTa entailment classifier method to check for strict bi-directional entailment, because this is cheaper and well-suited to short phrases. In addition to the instruction-tuned LLaMA, Falcon, and Mistral models we use in the sentence-length experiments, we additionally report results on the non-instruction-tuned LLaMA, Falcon, and Mistral models (which are not effective when applied to the sentence-length generation setting).

Supplementary Figure 9: Short-Phrase confabulation detection-rejection accuracy. A more detailed view of the rejection accuracies of the figures provides further elaboration of the findings in supplementary figure 7.

<!-- image -->

In supplementary figure 7, we show that results in this setting are broadly similar to those in the longer setting, with semantic entropy improving over p(True), embedding regression baseline, and naive entropy. In supplementary figure 8 we show this also holds for non-instruction-tuned models. Although non-instruction-tuned models have

2510

2511

2512

2513

2514

2515

2516

2517

2518

2519

2520

2521

2522

2523

2524

2525

2526

2527

2528

2529

2530

<!-- image -->

2556

2557

2558

2559

2560

2561

2562

2563

2564

2565

2566

2567

2568

2569

2570

2571

2572

2573

2574

2575

2576

Supplementary Figure 10: Short-Phrase confabulation detection-rejection accuracy for non-instruction tuned models. A more detailed view of the rejection accuracies of the figures provides further elaboration of the findings in supplementary figure 7.

slightly different distributional characteristics-tending to have better-calibrated output probabilities-we find that semantic entropy continues to outperform the baselines in this setting.

Averaged across the 60 combinations of tasks and models we study for the shortphrase setting, semantic entropy and discrete semantic entropy achieve the best mean AUROC (see below) values of 0.792 and 0.790 while naive entropy 0.760, p(True) 0.683, and the embedding regression baseline 0.708 lag behind it. Notably, semantic entropy continues to improve over p(True) and the embedding regression baseline by about 0.10 AUROC. However, naive entropy performs better than for longer generations, although semantic entropy does still improve over it by 0.03 on average (and by significantly more for individual datasets and models). This is because longer answers exhibit more of the syntactic variation that causes naive entropy to fail, and requiring answers to be as short as possible reduces the opportunity for variation.

In supplementary figure 9 we provide a more detailed view of the rejection accuracies at different proportions of answers retained. Lastly, supplementary figure 10 shows rejection accuracies for non-instruction tuned models.

## References

- [76] Herbert Paul Grice. Studies in the Way of Words. Harvard University Press, Cambridge, 1989.
- [77] Isabelle Lorge and Janet B. Pierrehumbert. Not wacky vs. definitely wacky: A study of scalar adverbs in pretrained language models. BlackBoxNLP Workshop at EMNLP, 2023.
- [78] Nick McKenna, Tianyi Li, Liang Cheng, Mohammad Javad Hosseini, Mark Johnson, and Mark Steedman. Sources of hallucination by large language models on inference tasks. In Findings of EMNLP, 2023.