<!-- source: 2025-Nature-Joint speech and text machine translation for up to 100 languages_SEAMLESSM4T.pdf -->
<!-- source_pdf: D:\2026-AI4S\2025-Nature-Joint speech and text machine translation for up to 100 languages_SEAMLESSM4T.pdf -->
<!-- pages: 75 ; extracted_by: docling 2.140.0 -->

## Joint speech and text machine translation for up to 100 languages

[https://doi.org/10.1038/s41586-024-08359-z](https://doi.org/10.1038/s41586-024-08359-z)

Received: 22 November 2023

Accepted: 6 November 2024

Published online: 15 January 2025

Open access

<!-- image -->

Check for updates SEAMLESS Communication Team*

Creating the Babel Fish, a tool that helps individuals translate speech between any two languages, requires advanced technological innovation and linguistic expertise. Although conventional speech-to-speech translation systems composed of multiple subsystems performing translation in a cascaded fashion exist 1-3 , scalable and high-performing unified systems 4,5 remain underexplored. To address this gap, here we introduce SEAMLESSM4T-Massively Multilingual and Multimodal Machine Translation-a single model that supports speech-to-speech translation (101 to 36 languages), speech-to-text translation (from 101 to 96 languages), text-to-speech translation (from 96 to 36 languages), text-to-text translation (96 languages) and automatic speech recognition (96 languages). Built using a new multimodal corpus of automatically aligned speech translations and other publicly available data, SEAMLESSM4T is one of the first multilingual systems that can translate from and into English for both speech and text. Moreover, it outperforms the existing state-of-the-art cascaded systems, achieving up to 8% and 23% higher BLEU (Bilingual Evaluation Understudy) scores in speech-to-text and speech-to-speech tasks, respectively. Beyond quality, when tested for robustness, our system is, on average, approximately 50% more resilient against background noise and speaker variations in speech-to-text tasks than the previous state-of-the-art systems. We evaluated SEAMLESSM4T on added toxicity and gender bias to assess translation safety. For the former, we included two strategies for added toxicity mitigation working at either training or inference time. Finally, all contributions in this work are publicly available for noncommercial use to propel further research on inclusive speech translation technologies.

The Babel Fish from The Hitchhiker's Guide to the Galaxy is a fictional tool that translates between two languages. In the contemporary global landscape, characterized by increasing interconnectivity and mobile sociality, the social imperative to actualize these technologies and facilitate on-demand speech-to-speech translation (S2ST) both in the digital and in the physical worlds has never been greater. Despite the centrality of speech in everyday communication, machine translation (MT) systems today remain text-oriented. See Supplementary Information section I.1 for more details on why speech should be prioritized in MT. Although single, unimodal models such as No Language Left Behind (NLLB) 6 pushed text-to-text translation (T2TT) coverage to more than 200 languages, unified S2ST models are far from achieving similar scope or performance. This disparity could be attributed to many causes, but audio data scarcity and modelling constraints remain key obstacles.

Existing S2ST systems have three main shortcomings. First, these systems tend to focus on high-resource languages, leaving many low-resource languages behind. Second, these systems mostly service translation from a source language into English (X-eng), not the reverse (eng-X). Third, most S2ST systems rely heavily on the cascading of several subsystems; for example, automatic speech recognition (ASR) + T2TT + text-to-speech (TTS). Although direct systems exist 1,4,5 , they do not match the performance of their cascaded counterparts 7 .

See Supplementary Information section I.2 for more details on the current technical landscape.

To address these limitations, we introduce SEAMLESSM4T (Massively Multilingual and Multimodal Machine Translation), a unified system that supports ASR, T2TT, speech-to-text translation (S2TT), text-to-speech translation (T2ST) and S2ST. To build this, we created a corpus of more than 470,000 h of automatically aligned speech translations (SEAMLESSALIGN) using a new sentence embedding space (Sentence-level Multimodal and Language-Agnostic Representations, or SONAR) 8 . We then combined a filtered subset of this corpus with human-labelled and pseudo-labelled data to develop the first multitasking system that performs S2ST from more than 100 languages into 36 languages, S2TT and ASR into 96 languages, zero-shot T2ST into 36 languages, as well as T2TT for 96 languages (see Table 1 for a comparative overview of language coverage and Supplementary Information section II for more details). Because of the unified architecture of SEAMLESSM4T (Fig. 1), the model can perform T2TT, S2TT or S2ST for non-English directions (X-X) in a zero-shot manner. It can also perform T2ST without being trained explicitly for this task. As a result of pretraining the speech encoder of SEAMLESSM4T on large amounts of unlabelled speech data (see section 'Unsupervised speech pretraining'), it can handle utterances mixing two or more languages.

## Article

## Table 1 | State-of-the-art task and language coverage

| Model                   | Task language coverage - S2TT   | Task language coverage - S2ST   | Task language coverage - ASR   | Task language coverage - T2TT   | Task language coverage - T2ST   |
|-------------------------|---------------------------------|---------------------------------|--------------------------------|---------------------------------|---------------------------------|
| AudioPaLM-8B-S2ST a,21  | 113-eng                         | 113-eng                         | 98                             | -                               | -                               |
| NLLB Team et al. 6      | -                               | -                               | -                              | 202-202                         | -                               |
| WHISPER-LARGE-V2 20     | 96-eng                          | -                               | 97                             | -                               | -                               |
| MMS-L1107-CCLM-LSAH 23  | -                               | -                               | 1107                           | -                               | -                               |
| This work (SEAMLESSM4T) | 101-96                          | 101-36                          | 96                             | 96-96                           | 96-36                           |

For each of our core tasks, we provide the language coverage of SEAMLESSM4T and existing state-of-the-art models.

a Although other models in this table are open-sourced, AudioPaLM is a proprietary model.

To evaluate the quality of outputs of our model, we used several existing metrics spanning across tasks and modalities, as well as four main evaluation datasets. For example, we used chrF2++ 9 for T2TT, BLEU 10 for S2TT, ASR-BLEU 5 for S2ST and WER for ASR. See Supplementary Table 2 for details. We also tested our models for resilience against background noise or speaker variation, as well as other fronts for responsible deployment, such as gender bias, using the MULTILINGUAL HOLISTICBIAS datasets, or added toxicity, using new speech-based metrics (ASR-ETOX and MuTox). We mitigate added toxicity with a filtering strategy at training time and a beam filtering strategy at inference time 11 .

Apart from building SEAMLESSM4T, we also discuss the social implications of our work and how it may contribute to greater degrees of world-readiness 12 in the long run (see section 'Social impact and conclusion'). To spur future research, we make the data tools, code and two sizes of SEAMLESSM4T models publicly available for non-commercial use.

In the subsequent sections, we trace the key results in developing our SEAMLESSM4T models. First, we outline our efforts to mine aligned speech and text data, starting with speech language identification to the mining of aligned speech and text segments using modality-agnostic encoders. Next, we report the main results of our direct translation systems trained in part with the aforementioned automatically aligned speech data. These results highlight the task versatility of SEAMLESSM4T models achieving multilingual state-of-the-art performance in ASR, T2TT, S2TT and S2ST. Then, we support the reported results with human evaluation analysis. Finally, we delineate our efforts to mitigate added toxicity and evaluate the robustness of our models to gender variations.

## Data

Training speech translation systems requires labelled data; that is, speech-to-text and speech-to-speech aligned data. However, those resources are very limited for low-resource languages. We build on the multilingual and multimodal embedding space of SONAR 8 and a large collection of raw speech and texts, as described in the Methods, to automatically mine aligned resources, complementing existing human-labelled and pseudo-labelled data.

## Speech language identification

Processing raw speech from the web involves segmenting utterances into shorter chunks, followed by language identification. Building on an open-source model trained on VoxLingua107 with the ECAPA-TDNN architecture 13,14 , we developed a new speech-based language identification (LID) model covering all 100 languages featured in this work (see Methods, 'Audio processing and speech LID' for more details).

To measure the precision and recall of LID models, we report F1 scores on the test data in Extended Data Table 1. The results are given for the 100 SEAMLESSM4T languages (Overall) and the 79 common languages between SEAMLESSM4T and VoxLingua107 (Intersection). Note that the macro-F1 on all languages for VL107HF is low because 21 languages are not covered by this model. We find that training on the additional languages slightly decreases the overall performance for the common set of languages, which is a direct consequence of a higher number of close languages. For example, Zulu (zul) is very often confused with Nyanja (nya), Igbo (ibo) with Yoruba (yor), and Modern Standard Arabic (arb) with Moroccan Arabic (ary) and Egyptian Arabic (arz). Our model improves classification accuracy (F1 difference greater than 5%) on 17 languages with an average gain of 14.6% without counting newly covered languages, while decreasing classification accuracy for 12 (with an average loss of 9.8%). We further filtered the data by applying a threshold on the LID score (likelihood). Language-specific thresholds have been tuned to maximize F1 score on the development data. By filtering out 8% of the data, we were able to further increase the F1 score by almost 3%.

Fig. 1 | Schematic of the SEAMLESSM4T-V2 model. The three main blocks of UNITY2 (S2ST fine-tuning) with its non-autoregressive (NAR) T2U are shown on the top left. Multitask-UNITY2 with its additional text encoder are shown on the

<!-- image -->

bottom left. Break down of the components of SEAMLESSM4T-V2 (a multitaskUNITY2 model) are shown on the right with the side panel showing the teacher T2U model used for pseudo-labelling (M4).

Table 2 | Comparison of similarity search error rates on all 200 FLORES languages and limited to the intersection of 98 languages on which each model has been trained

| Model   |   Overall - ↓xsim (n = 200) |   Intersection - ↓xsim++ (n = 200) |   Intersection - ↓xsim (n = 98) |   Intersection - ↓xsim++ (n = 98) |
|---------|-----------------------------|------------------------------------|---------------------------------|-----------------------------------|
| SONAR   |                         1.4 |                               15.2 |                             0.1 |                               9.3 |
| LASER3  |                         5.1 |                               36.4 |                             1.1 |                              27.5 |
| LaBSE   |                        10.7 |                               36.1 |                             1.5 |                              15.4 |

The best results are in bold.

## SONAR text embedding space

To mine automatically aligned translation data from language-identified segments, we rely on language- and modality-agnostic encoders. To this end, we build on the SONAR embedding space developed in ref. 8. Currently, we provide a single text encoder and decoder for 200 languages and speech encoders for 37 languages. The list of 200 languages is identical to the language list of the NLLB project 6 . In multilingual similarity search, xsim and xsim++ 15 are two well-known proxy metrics evaluating multilingual embedding spaces for the purpose of mining. As shown in Table 2, SONAR substantially outperforms other popular approaches such as LASER3 16 or LaBSE 17 with lower xsim and xsim++.

Furthermore, we evaluated the SONAR text encoders and decoders on T2TT tasks. The average performance over 200 languages is competitive compared with the medium-sized NLLB dense model, despite the replacement of encoder-decoder attention in SONAR with a bottleneck fixed-size embedding (see the T2TT columns of Extended Data Table 2). This result proves that the use of attention is not a requisite for reasonable translation accuracy. For more details on SONAR, see D2.

## Training speech encoders

The speech encoders were trained with a teacher-student approach on speech transcriptions only (see Methods, 'SONAR'). Evaluating iterations of each speech encoder in an end-to-end loop, that is, mining and training S2TT or S2ST translation systems, would be compute-intensive. Instead, we connected the speech encoder with the SONAR text decoder and evaluated this zero-shot S2TT system as a proxy for the quality of the encoder. As shown in the S2TT columns of Extended Data Table 2, the SONAR speech encoders compare favourably to a model such as WHISPER-LARGE-V2 on FLORES 6 and FLEURS 18 datasets, which was trained on massive amounts of supervised data. Gaps in accuracy can be observed in some high-resource languages such as German, Russian or Portuguese, but SONAR outperforms WHISPER-LARGE-V2 in several low-resource languages such as Swahili or Bengali (see Supplementary Table 8).

## SEAMLESSALIGN

The SONAR text and speech encoders were used to mine for three types of aligned data: (1) English speech to non-English texts (Sen2Txx); (2) non-English speech to English texts (Sxx2Ten); and (3) non-English speech to English speech (Sxx2Sen). SEAMLESSALIGN provides 202,796 h of audio in Sen2Txx, 239,767 h of audio in Sxx2Ten and 29,161 h of audio in Sxx2En. These aligned data were mined from a total of 2.5M h of raw audio (of which English is nearly 40%). SONAR speech encoders were trained on 43,772 h of supervised ASR data. For statistics per language, see Supplementary Table 8.

For the text domain, we use the same data consolidated by the NLLB project 6 . The amount varies from 33 million or 55 million sentences for low-resource languages such as Maltese or Swahili, respectively, to 22,000 million English sentences.

Except for Maltese, for which we only had access to a small amount of raw audio, we were able to mine more than 100 h of speech alignments with English speech for all languages. The alignments with English texts reached a thousand hours for most languages and exceeded 10,000 h for high-resource languages. Overall, SEAMLESSALIGN covers 37 languages for a total of 470,000 h.

Adding such large amounts of data to train a multilingual translation system is a substantial computational challenge. As described in the Methods, 'Modelling', not all of these data were used for modelling, but only a subset with the highest SONAR alignment scores. As our mined data can help support many different use cases, we open-sourced the meta-data needed to guide its recreation (up to a SONAR threshold of 1.15; see Methods, 'SpeechAlign') to allow the community to rebuild SEAMLESSALIGN and use it for their own purposes. The optimal threshold can thus be tuned based on the task, balancing dataset size and alignment quality. Our mining code is also open-sourced in the STOPES library.

## Modelling multitask translation systems

Combining modelling techniques outlined in the Methods, 'Modelling', with additional data from SEAMLESSALIGN (see Methods, 'Data'), we trained SEAMLESSM4T models in two sizes: large with 2.3B parameters and medium with 1.2B parameters. SEAMLESSM4T-MEDIUM is intended to be an accessible test bed to either fine-tune, improve on or engage in analysis with. We further trained an improved version of the large SEAMLESSM4T, dubbed SEAMLESSM4T-V2, with a better speech encoder (see Methods, 'Unsupervised speech pretraining') and a more powerful unit decoder (see section 'S2ST fine-tuning'). All SEAMLESSM4T models support 96 source languages in the text modality and more than 100 source languages in the speech modality. On the target side, the models can output 96 languages in text form and 35 in speech form. The amount of supervised data per direction and per source (for example, M4 or SEAMLESSALIGN) is detailed in Supplementary Tables 12 and 13. This shows that, for some translation directions and given the lack of supervised data, our models will be evaluated zero-shot.

We evaluated our models on all four supervised tasks (T2TT, ASR, S2TT and S2ST) as well as the zero-shot task of text-to-speech translation (T2ST, also referred to as cross-lingual text-to-speech synthesis 19 ). To generate text hypotheses, we decoded with beam-search. We scored with chrF2++ for T2TT and BLEU for S2TT. We measure BLEU scores with SacreBLEU and provide the signatures in Supplementary Table 2. For ASR, we scored with WER (word error rate) on normalized transcriptions and references following ref. 20.

During S2ST and T2ST inference, we performed two-pass beam-search decoding; the best hypothesis out of the first-pass decoding is embedded with the text decoder and is sent to a text-to-unit module (T2U; see section 'S2ST fine-tuning') to search for the best unit sequence hypothesis. We used a beam width of 5 for both searches. We evaluated S2ST and T2ST accuracy with ASR-BLEU using WHISPER models. We set the decoding temperature of WHISPER at zero and used greedy decoding to ensure a deterministic behaviour of the ASR model. The transcribed hypotheses, as well as the references, are normalized following ref. 20 before computing BLEU scores.

## Comparison with cascaded approaches for speech translation

On the set of languages supported by both SEAMLESSM4T and WHISPER, we compare in Table 3 (S2TT columns) the performance of our direct S2TT model to that of cascaded models, namely, combinations of WHISPER ASR models and NLLB T2TT models. SEAMLESSM4T-V2 surpasses the cascaded models with less than 3B parameters in X-eng directions by 4.6 BLEU points (from 22.0 to 26.6) and in eng-X directions by 1 BLEU point (from 21.1 to 22.2). We also added to the comparison in Table 3 cascaded models with the large NLLB-3.3B T2TT model. These models exceed 4B parameters and are largely surpassed by SEAMLESSM4T-V2 in X-eng (+3.9); they only marginally outperform SEAMLESSM4T-V2 in eng-X directions by 0.2 BLEU points.

## Article

| Model                       |                            | S2TT FLEURS (↑BLEU) - X-eng (n = 81)   | S2TT FLEURS (↑BLEU) - eng-X (n = 88)   | S2ST FLEURS (↑ASR-BLEU) - X-eng (n = 81)   | S2ST FLEURS (↑ASR-BLEU) - eng-X (n = 26)   |   S2ST CVSS (↑ASR-BLEU) X-eng (n = 21) |
|-----------------------------|----------------------------|----------------------------------------|----------------------------------------|--------------------------------------------|--------------------------------------------|----------------------------------------|
| Table 3 &#124; WL-V2 (S2TT) | State-of-the-art Size 1.5B | 17.9                                   | S2TT/S2ST -                            | models 17.8                                | -                                          |                                   29.6 |
| WL-V3 (S2TT)                | 1.5B                       | 16.9 a                                 | -                                      |                                            |                                            |                                        |
| A8B (S2TT)                  | 8B                         | 19.7                                   | -                                      |                                            |                                            |                                        |
| WM (ASR) + NLLB-1.3B        | 2B                         | 19.7                                   | 20.7                                   | 20.7                                       | 21.5                                       |                                        |
| WM (ASR) + NLLB-3.3B        | 4B                         | 20.4                                   | 22.0                                   | 21.4                                       | 22.4                                       |                                        |
| WL-V2 (ASR) + NLLB-1.3B     | 2.8B                       | 22.0                                   | 21.2                                   | 22.9                                       | 21.8                                       |                                        |
| WL-V2 (ASR) + NLLB-3.3B     | 4.8B                       | 22.7                                   | 22.4                                   | 23.7                                       | 22.7                                       |                                        |
| SEAMLESSM4T-MEDIUM          | 1.2B                       | 20.9                                   | 19.4                                   | 20.2                                       | 15.8                                       |                                   30.6 |
| SEAMLESSM4T-LARGE           | 2.3B                       | 24.1                                   | 21.8                                   | 25.8                                       | 20.9                                       |                                   35.7 |
| SEAMLESSM4T-V2              | 2.3B                       | 26.6                                   | 22.2                                   | 29.7                                       | 26.1                                       |                                   39.2 |

Comparison with cascaded ASR + T2TT models on FLEURS S2TT, and with two-stage and three-stage cascaded models on FLEURS and CVSS S2ST X-eng. S2ST cascaded systems rely on a TTS model as the last subsystem, for this we use YOURTTS 22 to synthesize English speech and MMS 23 to synthesize non-English speech (these models are not factored into the system size and are omitted from the nomenclature of the models). We abbreviate WHISPER-LARGE as WL, WHISPER-MEDIUM as WM and AUDIOPALM-2-8B-AST as A8B. The results of the cascaded models are shown in italic and the best score for each task is shown in bold.

a We evaluated WHISPER-LARGE-V3 on S2TT FLEURS X-eng using https://github.com/openai/ whisper/. For WHISPER-LARGE-V2, we used the results from ref. 20.

Compared with previous direct S2TT SOTA models that lagged behind cascaded systems (for example, AUDIOPALM-2-8B-AST. ref. 21), SEAMLESSM4T-V2 improves on FLEURS X-eng S2TT BLEU score by 6.9 points (from 19.7 to 26.6; that is, an improvement of 35%).

Table 3 (S2ST columns) also compares S2ST between SEAMLESSM4T models and cascaded models. For S2ST, we explore two options for cascading: (1) three-stage with ASR, T2TT and TTS and (2) two-stage with S2TT and TTS. Both types of cascaded systems rely on a TTS model to synthesize translated speech, and for this we use YOURTTS 22 when synthesizing English speech and MMS 23 when synthesizing speech in the 26 non-English languages of comparison (overlap between the support of SEAMLESSM4T and the support of TTS systems of MMS). Our SEAMLESSM4T-LARGE outperforms the two-stage cascaded models on FLEURS X-eng directions by 8 ASR-BLEU points (17.8-25.8). It also outperforms stronger three-stage cascaded models (WHISPER-LARGE-V2 + NLLB-3.3B + YOURTTS) by 2.1 ASR-BLEU points (23.7-25.8). The improved SEAMLESSM4T-V2 further strengthen this lead on S2ST FLEURS X-eng with an additional +3.9 ASR-BLEU points (25.8-29.7). On CVSS, SEAMLESSM4T-V2 outperforms the two-stage cascaded model (WHISPER-LARGE-V2 + YOURTTS) by a large margin of 9.6 ASR-BLEU points (29.6-39.2). On FLEURS S2ST eng-X directions, we reduce the evaluation set to the 26 languages supported by both TTS of MMS and SEAMLESSM4T. The medium-size model (SEAMLESSM4T-MEDIUM) scores an average ASR-BLEU of 15.8. SEAMLESSM4T-LARGE achieves an average ASR-BLEU of 20.9 and with its improved speech encoder and non-autoregressive T2U model, SEAMLESSM4T-V2 further gains +5.2 ASR-BLEU points (20.926.1). By contrast, the best three-stage cascaded system with MMS (WHISPER-LARGE-V2 + NLLB-3.3B + MMS) scores an average 22.7 ASR-BLEU, that is, SEAMLESSM4T-V2 surpasses state-of-the-art cascaded models by 15% (22.7-26.1).

We share in Supplementary Information section IV.1 evaluation results for the tasks of S2TT and S2ST with additional metrics, including our modality-agnostic BLASER 2.0.

## Multitasking results

We report in Table 4 results on the FLEURS benchmark for the tasks of ASR and zero-shot T2ST (X-eng and eng-X), and the related FLORES

## Table 4 | Multitasking results

| Model                   | Size   | ASR (↓WER) - FLEURS (n = 77)   | T2TT (↑chrF2++) - FLORES X-eng (n = 95)   | T2TT (↑chrF2++) - FLORES eng-X (n = 95)   |   T2ST (↑ASR-BLEU) - FLEURS X-eng (n = 88) |   T2ST (↑ASR-BLEU) - FLEURS eng-X (n = 26) |
|-------------------------|--------|--------------------------------|-------------------------------------------|-------------------------------------------|--------------------------------------------|--------------------------------------------|
| NLLB-3.3B               | 3.3B   | -                              | 60.7                                      | 49.6                                      |                                            |                                            |
| NLLB-3.3B + YOURTTS/MMS | 3.4B   | -                              | -                                         | -                                         |                                       36.4 |                                       23.7 |
| WHISPER-LARGE-V2        | 1.5B   | 41.7                           |                                           |                                           |                                            |                                            |
| SEAMLESSM4T- MEDIUM     | 1.2B   | 21.9                           | 55.4                                      | 48.4                                      |                                       26.3 |                                       18.4 |
| SEAMLESSM4T- LARGE      | 2.3B   | 22.6                           | 60.8                                      | 50.9                                      |                                       34.1 |                                       21.8 |
| SEAMLESSM4T- LARGE V2   | 2.3B   | 18.5                           | 59.2                                      | 49.3                                      |                                       35.9 |                                       27.6 |

Performance of SEAMLESSM4T-LARGE on the auxiliary tasks of ASR and T2TT and the zero-shot task of T2ST compared with SOTA single-task models. The results of cascaded models are shown in italics and the best result in each task is shown in bold. Scoring WHISPER-LARGE-V2, using https://github.com/openai/whisper with the recommended decoding options, results in BLEU scores lower by 0.3 BLEU points on average than what is reported in ref. 20.

benchmark for T2TT (X-eng and eng-X). In ASR, SEAMLESSM4T-LARGE outperforms WHISPER-LARGE-V2 20 on the overlapping 77 supported languages with a WER reduction of 46% (from 41.7 to 22.6), whereas SEAMLESSM4T-V2 improves over WHISPER-LARGE-V2 by 56% (from 41.7 to 18.5). We also compared in Supplementary Table 9 against MMS 23 on FLEURS-54, a subset of FLEURS languages that MMS and WHISPER both support. SEAMLESSM4T-V2 outperforms the MMS variants evaluated with CTC by more than 38% WER (from 31.0 to 19.1), but it is surpassed by the variants that leverage monolingual n-gram language models (5% better WER with 18.6).

In the T2TT support task, results in Table 4 show that our SEAMLESSM4T models are on par with NLLB-3.3B (ref. 6) in both X-eng and eng-X directions.

We next evaluated SEAMLESSM4T models on the task of T2ST in a zero-shot way. Given that FLEURS collected three recordings by three different native speakers for each sample, we randomly selected one for the task of T2ST (the input being text). We report in Table 4 (the T2ST columns) a comparison between SEAMLESSM4T models and cascaded models with NLLB and either YOURTTS (English TTS) or MMS (non-English TTS) for synthesizing translated text. We averaged ASR-BLEU scores over 88 X-eng directions (the overlap between FLEURS and the languages supported by SEAMLESSM4T). We also averaged ASR-BLEU over 26 eng-X directions (overlap of SEAMLESSM4T with TTS models of MMS). Compared with cascaded models, the zero-shot capability of SEAMLESSM4T-LARGE V2 is on par with NLLB-3.3B + YOURTTS in X-eng and outperforms NLLB-3.3B + MMS by more than +3.9 ASR-BLEU points in eng-X (from 23.7 to 27.6). This result demonstrates that (1) the quality of SEAMLESSM4T on zero-shot T2ST is on par with the supervised tasks and (2) non-English speech source is the most challenging input to translate with our model.

To further understand where the improvements in FLEURS S2TT Xeng directions were coming from, we bucketed languages by resource level (see the exact list of languages in Supplementary Table 12) and report average BLEU scores per resource level in Table 5. The results show that SEAMLESSM4T strongly improves the quality of translating from low-resource languages with an improvement of +10.2 BLEU (from 18.0 to 28.2, that is, 57% improvement over AUDIOPALM-2-8B-AST). We also average in column Low* over low-resource directions that are supervised in AUDIOPALM-2-8B-AST. The gain of +7.8 BLEU in that subset of directions suggests that this improvement goes beyond sheer In each resource level (that is, high, medium and low), we averaged over languages that are covered by all three models. In low * , we excluded low-resource languages that are evaluated as zero-shot by AUDIOPALM-2-8B-AST. In each subset, the highest BLEU score is shown in bold.

Table 5 | FLEURS S2TT X-eng by resource level

| Model                |   FLEURS S2TT X-eng (↑BLEU) - High (n = 15) |   FLEURS S2TT X-eng (↑BLEU) - Medium (n = 25) |   FLEURS S2TT X-eng (↑BLEU) - Low (n = 34) |   FLEURS S2TT X-eng (↑BLEU) - Low* (n = 23) |
|----------------------|---------------------------------------------|-----------------------------------------------|--------------------------------------------|---------------------------------------------|
| WHISPER-LARGE-V2     |                                        24.2 |                                          19.4 |                                       16.1 |                                        18.1 |
| AUDIOPALM-2-8B-AST   |                                        27.9 |                                          20.9 |                                       18.0 |                                        22.0 |
| SEAMLESSM4T-MEDIUM   |                                        23.9 |                                          21.8 |                                       22.2 |                                        23.5 |
| SEAMLESSM4T-LARGE    |                                        27.0 |                                          25.3 |                                       25.6 |                                        27.1 |
| SEAMLESSM4T-LARGE V2 |                                        28.8 |                                          28.3 |                                       28.2 |                                        29.8 |

supervision but instead should be attributed to the quality of supervised data and the training recipes.

## Automatic and human evaluation

Semantic accuracy in speech translation is generally evaluated with the automatic metric BLEU 10 for S2TT or its extension ASR-BLEU for S2ST. Moreover, we use BLASER 2.0 (ref. 24), an extension of BLASER 25 , which now enables modality-agnostic evaluation and quality estimation for both speech and text.

To complement the utility of automatic metrics, we also relied on extensive human evaluation of our models. In the following, we provide human evaluation for S2TT and S2ST tasks with the XSTS (cross-lingual semantic textual similarity) protocol 26 and MOS (mean opinion score) protocol for speech outputs (see Methods, 'Human evaluation') on the FLEURS test set. However, we cover a limited number of models (SEAMLESSM4T-LARGE, SEAMLESSM4T-LARGE V2 and a cascaded baseline composed of WHISPER-LARGE-V2 for ASR, NLLB 3.3B for translation and YOURTTS or MMS for TTS for the S2ST task) and translation directions (23 languages from and into English, 10 languages X-eng for MOS) because of resource restrictions.

XSTS scores show that SEAMLESSM4T-LARGE V2 outperforms both the cascaded baseline systems and SEAMLESSM4T-LARGE in terms of both average language-level XSTS score and win rate (the fraction of evaluated languages for which XSTS performance is superior), for all tasks and language directions with high confidence. For the S2ST task, where relative performance of SEAMLESSM4T-V2 was the strongest, win rate of SEAMLESSM4T-V2 approaches 100% compared with both cascaded baseline and SEAMLESSM4T-LARGE for both X-eng and eng-X directions, with average language XSTS scores about 0.5 points higher than the cascaded baseline and 0.36-0.51 points higher compared with SEAMLESSM4T-LARGE for eng-X and X-eng, respectively. See Supplementary Tables 22 and 24 for full language-level and summarized XSTS results, respectively.

We also measure the quality of speech output for the S2ST using a Mean Opinion Score protocol that assesses (1) sound quality, (2) clarity of speech and (3) naturalness. We find that generally, across all MOS aspects, SEAMLESSM4T-LARGE V2 tends to be preferred to SEAMLESSM4T-LARGE, which tends to be preferred to the cascaded model baselines, with the exception of X-eng, for which SEAMLESSM4T-LARGE generations are strongly preferred (+1 point average difference between SEAMLESSM4T-LARGE and SEAMLESSM4T-LARGE V2 generations), an unexpected result that may be a consequence of differences in model architectures that otherwise have improved generation quality. See Supplementary Tables 23 and 24 for full language-level and summarized MOS results, respectively.

Using the XSTS evaluations of the S2ST task, BLASER 2.0 (averaged over all evaluation items in a given language direction) achieves superior Spearman correlations with calibrated language-level XSTS scores in both X-eng direction (0.845 for BLASER 2.0 compared with 0.74 for ETOX is ASR-ETOX in the case of speech outputs. The baseline corresponds to WHISPER-LARGE-V2 for S2TT X-eng; WHISPER-LARGE-V2 + NLLB-3.3B for S2TT X-eng; WHISPER-LARGE-V2 + YOURTTS for S2ST X-eng.

Table 6 | Results for S2TT and S2ST averaged across 28 directions that add toxicity

| Model                   |   FLEURS X-eng - ETOX% (↓) |   FLEURS X-eng - MuTox (↓) |   FLEURS eng-X - ETOX% (↓) |   FLEURS eng-X - Mutox (↓) |   HOLISTICBIAS - ETOX% (↓) |   HOLISTICBIAS - MuTox (↓) |
|-------------------------|----------------------------|----------------------------|----------------------------|----------------------------|----------------------------|----------------------------|
| S2TT                    |                            |                            |                            |                            |                            |                            |
| Baseline                |                       0.21 |                       0.05 |                       0.23 |                       0.08 |                       0.32 |                       0.39 |
| SEAMLESSM4T- LARGE      |                       0.20 |                       0.02 |                       0.24 |                       0.07 |                       0.32 |                       0.37 |
| SEAMLESSM4T-V2          |                       0.22 |                       0.01 |                       0.16 |                       0.08 |                       0.15 |                       0.39 |
| SEAMLESSM4T-V2 + MinTox |                       0.22 |                       0.01 |                       0.07 |                       0.01 |                       0.03 |                       0.37 |
| S2ST                    |                            |                            |                            |                            |                            |                            |
| Baseline                |                       0.05 |                       0.05 |                       0.30 |                       0.02 |                       0.32 |                       0.32 |
| SEAMLESSM4T- LARGE      |                       0.05 |                       0.01 |                       0.15 |                       0.04 |                       0.26 |                       0.29 |
| SEAMLESSM4T-V2          |                       0.04 |                       0.01 |                       0.11 |                       0.02 |                       0.15 |                       0.26 |
| SEAMLESSM4T-V2 + MinTox |                       0.04 |                       0.01 |                       0.05 |                       0.02 |                       0.03 |                       0.25 |

ASR-BLEU) and in particular for the eng-X direction (0.81 for BLASER 2.0 compared with 0.246 for ASR-BLEU). Similar results hold for the S2TT task (see Supplementary Table 21 for full results).

Finally, we tested our models for robustness in terms of noise and speaker variations by creating open robustness benchmarks based on FLEURS (see Methods, 'Robustness'). To that end, we find that SEAMLESSM4T-V2 is, on average, approximately 42% and 66% more resilient against background noise and speaker variation, respectively, when compared with WHISPER-LARGE-V2 (see full results in Supplementary Information section V.2).

## Responsible AI

## Toxicity

Toxicity can be defined as instances of profanity or language that may incite hate, violence or abuse against an individual or a group (such as a religion, race or gender). When it comes to massively multilingual toxicity classifiers for text, the ETOX toolkit seems to be the only openly accessible option with the largest language coverage 27 . In the context of speech translation, we were primarily worried about added toxicitythe introduction in translations of toxic elements not present in source utterances. Speech toxicity has been evaluated for English in ref. 28 and, recently, for tens of languages with MuTox 29 .

Therefore, for speech and text multilingual toxicity detection, we used ETOX (or ASR-ETOX for S2ST) and MuTox (both for speech and text) as metrics to detect and evaluate added toxicity. For toxicity mitigation, we implemented two techniques to deal with added toxicity. Before training, we filtered out training pairs with imbalanced toxicity. Moreover, we used Mintox 11 at inference time (see Methods, 'Toxicity detection').

We computed added toxicity in two datasets (FLEURS and HOLISTICBIAS 27 ) across 24 translation directions with English (arb, ben, cat, ces, dan, deu, est, fin, fra, hin, ind, ita, nld, pes, pol, por, rus, slk, spa, swh, tgl, tur, urd, vie), using the languages at the intersection of the coverage of systems and MuTox having been benchmarked (note that MuTox has wider language coverage, similar to SONAR, but it has only been benchmarked in 30 languages 29 ). See results with more translation directions evaluated with ETOX in Supplementary Information section VI.1. Table 6 shows that although levels and types of added toxicity vary significantly as a function of language and dataset, the added

## Article

toxicity in our systems has a relatively low prevalence consistent across our two toxicity detection metrics (&lt;0.4%). Table 6 shows that MinTox is capable of mitigating added toxicity consistently. The lowest toxicity for all modalities, directions and datasets is consistently obtained with SEAMLESSM4T-V2 + MinTox, achieving reductions of toxicity up to 5% in terms of MuTox (and up to 80% in terms of ETOX) when comparing with the same model without using MinTox, and up to 20% in terms of MuTox (up to 90% in terms of ETOX) when comparing with the baseline (see complete results in Supplementary Information section VI.1).

## Gender bias

Gender bias in the context of MT can be defined as errors in grammatical gender determination. This bias may manifest explicitly as an overgeneralization to one gender when translating non-gendered to gendered forms (for example, outputs favouring masculine representations) or as a lack of robustness when varying the quality of the translation for sentences that differ only in gender inflection.

Previous work on this matter is mostly in the text modality 30-32 and tends to be English-centric, with few demographic axes and multilingual references. Similar efforts for the speech modality remain sparse 33,34 .

We used MULTILINGUAL HOLISTICBIAS 35 and its speech extension to compare the performance of S2TT and S2ST. The eng-X direction enables comparing performance in the presence of masculine or feminine references, and the X-eng direction enables robustness comparisons in translations when we alter gender inflection. A typical example of the English-Spanish language pair would be 'I'm a homemaker' and the corresponding translations 'Soy amo de casa' and 'Soy ama de casa' in Spanish. When translating from English to Spanish, we can measure if the system overgeneralizes to one gender, whereas in the other direction, we can evaluate the robustness of the translation to gender inflection (see Methods, 'Speech extension of MULTILINGUAL HOLISTICBIAS').

We conducted a set of comprehensive evaluations on translation biases for S2TT and S2ST (see Extended Data Table 3 for average results and Supplementary Information section VI.2 for detailed results). SEAMLESSM4T-V2 consistently improves robustness in gender variations across metrics and tasks. When compared with the previous model, SEAMLESSM4T-V2 improves over SEAMLESSM4T-LARGE by 0.4% in S2TT and by 0.1% BLASER 2.0 in S2ST, and it beats the external baseline system of WHISPER-LARGE-V2 (+YOURTTS) by 0.1% in S2TT and by 0.9% BLASER 2.0 for S2ST. However, SEAMLESSM4T-V2 is not able to consistently improve in terms of gender overgeneralization compared with the previous model. SEAMLESSM4T-V2 is comparable in terms of BLASER 2.0 to SEAMLESSM4T-LARGE, but it lags far behind in terms of ASRchrf (by 2.2%), and overgeneralization is increased by 0.2% when it comes to S2TT. Although we can increase bias robustness by improving the overall quality of the model, it seems that we need specific techniques to counteract the overgeneralization of the model towards a specific gender.

## Social impact and conclusion

The world we live in has never been more interconnected-the global proliferation of the internet, mobile devices, communicative platforms and social media exposes individuals to more multilingual content than ever before 36 . The current social order places a demand on the world-readiness of a person 12 , a measure of how competent a person is to take on the polyglot world. Initially developed in the context of language learning, world-readiness underscores the importance of being able to communicate in languages beyond our mother tongue for both instrumental (that is, employment or schooling) and cultural reasons (that is, to become a global citizen). That said, although we believe that language acquisition should remain a key mechanism for boosting our world-readiness, we acknowledge that doing so requires resources many people may not possess.

The downstream applications that SEAMLESSM4T supports could allow on-demand access to world-readiness by streamlining multilingual exchange across various contexts. SEAMLESSM4T-supported applications could act as a co-piloting mechanism that supports users in multilingual conversations and boosts their confidence in speech-heavy interactions. As speech-based interfaces (for example, audio assistants, voice memos and live transcriptions) and auditory content (for example, podcasts, audiobooks and short-form videos) become ever more present, SEAMLESSM4T-enabled downstream applications could unlock a greater variety of multilingual experiences.

From an inclusion standpoint, the focus of SEAMLESSM4T on multimodality could make a meaningful difference in augmenting the world-readiness of those with accessibility needs and those whose languages can be transcribed with multiple writing systems. For many who lack reading or writing skills, or cannot rely on sight (that is, people who are blind or with visual impairment), voice-assisted technologies are essential to how they communicate and stay connected 37 . The ability to translate speech gives these groups more comprehensive access to information not only beyond their native languages but also in a manner that is better suited for their communicative needs.

As with most technologies, the distribution of benefits varies based on user demographics and social situation 38 . Although we make the case that SEAMLESSM4T could augment world-readiness by lowering the barriers in cross-lingual communication, some users may experience more difficulties using our work than others. For instance, similar to many other speech technologies, the ASR performance of SEAMLESSM4T may vary based on gender, race, accent or language 39,40 . Moreover, the performance of our system in translating slang or proper nouns may also be inconsistent across high and low-resource languages.

Another challenge for S2ST is that speech tends to hinge on immediate reception and feedback more than written language does. In other words, speakers are limited in their ability to ascertain the quality of an output or make edits in a live conversation. Without the ability to plan and revise with the help of back-translation or a native speaker, S2ST may carry higher degrees of interactional risk when it comes to mistranslations or toxicity. We urge researchers and developers who fine-tune or build artefacts using SEAMLESSM4T to think critically about design features that could help users circumvent these potential obstacles. Importantly, we believe that SEAMLESSM4T-fueled applications should best be viewed as an augmentation device that assists in translation rather than a tool that replaces the need for language learning or reliable human interpreters. This reminder is especially pertinent in high-stakes situations involving legal or medical decision-making.

Finally, speech is not spoken text-it encompasses a suite of prosodic (for example, rhythm, stress, intonation or tone) and emotional components that deserve further research 41 . To create S2ST systems that feel organic and natural, more research should be directed at output generation that preserves expressivity 42 . Moreover, the consummate realization of the Babel Fish requires deeper investments into research on low-latency speech translation. Developing systems that enable streaming (that is, incrementally translating an input sentence as it is being presented) may increase the adoption of these systems across institutional contexts 43,44 . We hope that SEAMLESSM4T opens up new possibilities for both these research areas.

## Online content

Any methods, additional references, Nature Portfolio reporting summaries, source data, extended data, supplementary information, acknowledgements, peer review information; details of author contributions and competing interests; and statements of data and code availability are available at https://doi.org/10.1038/s41586-024-08359-z.

1. Lavie, A. et al. Janus-III: speech-to-speech translation in multiple languages. In Proc. 1997 IEEE International Conference on Acoustics, Speech, and Signal Processing Vol. 1, 99-102 (IEEE, 1997).

2. Wahlster, W. (ed.) Verbmobil: Foundations of Speech-to-Speech Translation (Springer, 2000).

3. Nakamura, S. et al. The atr multilingual speech-to-speech translation system. IEEE Trans. Audio Speech Lang. Process. 14, 365-376 (2006).
4. Jia, Y. et al. Direct speech-to-speech translation with a sequence-to-sequence model. In Proc. Interspeech 2019, 1123-1127 (ISCA, 2019).
5. Lee, A. et al. Direct speech-to-speech translation with discrete units. In Proc. 60th Annual Meeting of the Association for Computational Linguistics (eds Muresan, S. et al.) Vol. 1, 3327-3339 (Association for Computational Linguistics, 2022).
6. NLLB Team Scaling neural machine translation to 200 languages. Nature 630, 841-846 (2024).
7. Agarwal, M. et al. Findings of the IWSLT 2023 evaluation campaign. In Proc. 20th International Conference on Spoken Language Translation (IWSLT 2023) (eds Salesky, E. et al.) 1-61 (Association for Computational Linguistics, 2023).
8. Duquenne, P.-A., Schwenk, H. &amp; Sagot, B. SONAR: sentence-level multimodal and languageagnostic representations. Preprint at https://arxiv.org/abs/2308.11466 (2023).
9. Popović, M. chrF: character n-gram F-score for automatic MT evaluation. In Proc. Tenth Workshop on Statistical Machine Translation (eds Bojar, O. et al.) 392-395 (Association for Computational Linguistics, 2015).
10. Papineni, K., Roukos, S., Ward, T. &amp; Zhu, W.-J. Bleu: a method for automatic evaluation of machine translation. In Proc. 40th Annual Meeting of the Association for Computational Linguistics (eds Isabelle, P. et al.) 311-318 (Association for Computational Linguistics, 2002).
11. Costa-jussà, M. R., Dale, D., Elbayad, M. &amp; Yu, B. Added toxicity mitigation at inference time for multimodal and massively multilingual translation. In Proc. 25th Annual Conference of the European Association for Machine Translation (eds Scarton, C. et al.) Vol. 1, 360-372 (European Association for Machine Translation, 2024).
12. [ACTFL. World-readiness standards for learning languages. https://www.actfl.org/educatorresources/world-readiness-standards-for-learning-languages (2023).](https://www.actfl.org/educator-resources/world-readiness-standards-for-learning-languages)
13. Desplanques, B., Thienpondt, J. &amp; Demuynck, K. ECAPA-TDNN: emphasized channel attention, propagation and aggregation in TDNN based speaker verification. In Proc. Interspeech 2020, 21st Annual Conference of the International Speech Communication Association, Virtual Event (eds Meng, H. et al.) 3830-3834 (ISCA, 2020).
14. Valk, J. &amp; Alumäe, T. VOXLINGUA107: a dataset for spoken language recognition. In Proc. 2021 IEEE Spoken Language Technology Workshop, 652-658 (IEEE, 2021).
15. Chen, M., Heffernan, K., Çelebi, O., Mourachko, A. &amp; Schwenk, H. xSIM++: An improved proxy to bitext mining performance for low-resource languages. In Proc. 61st Annual Meeting of the Association for Computational Linguistics (eds Rogers, A. et al.) Vol. 2, 101-109 (Association for Computational Linguistics, 2023).
16. Heffernan, K., Çelebi, O. &amp; Schwenk, H. Bitext mining using distilled sentence representations for low-resource languages. In Findings of the Association for Computational Linguistics: EMNLP 2022, 2101-2112 (eds Goldberg, Y. et al.) (Association for Computational Linguistics, 2022).
17. Feng, F., Yang, Y., Cer, D., Arivazhagan, N. &amp; Wang, W. Language-agnostic BERT sentence embedding. In Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (eds Muresan, S. et al.) Vol. 1, 878-891 (Association for Computational Linguistics, 2022).
18. Conneau, A. et al. FLEURS: FEW-Shot Learning Evaluation of Universal Representations of Speech. In 2022 IEEE Spoken Language Technology Workshop (SLT), 798-805 (IEEE, 2023).
19. Zhang, Z.-H. et al. Speak foreign languages with your own voice: cross-lingual neural codec language modeling. Preprint at https://arxiv.org/abs/2303.03926 (2023).
20. Radford, A. et al. Robust speech recognition via large-scale weak supervision. In Proceedings of the 40th International Conference on Machine Learning, article no. 1182, 28492-28518 (ACM, 2023).
21. Rubenstein, P. K. et al. AudioPaLM: a large language model that can speak and listen. Preprint at https://arxiv.org/abs/2306.12925 (2023).
22. Casanova, E. et al. YourTTS: towards zero-shot multi-speaker tts and zero-shot voice conversion for everyone. In Proc. 39th International Conference on Machine Learning, Vol. 162, 2709-2720 (PMLR, 2022).
23. Pratap, V. et al. Scaling speech technology to 1,000+ languages. J. Mach. Learn. Res. 25, 1-52 (2024).
24. Dale, D. &amp; Costa-jussà, M. R. Blaser 2.0: a metric for evaluation and quality estimation of massively multilingual speech and text translation. In Findings of the Association for Computational Linguistics: EMNLP 2024 (eds Al-Onaizan, Y. et al.) 16075-16085 (Association for Computational Linguistics, 2024).
25. Chen, P.-J. et al. Speech-to-speech translation for a real-world unwritten language. In Findings of the Association for Computational Linguistics: ACL 2023 (eds Rogers, A. et al.) 4969-4983 (Association for Computational Linguistics, 2023).
26. Licht, D. et al. Consistent human evaluation of machine translation across language pairs. In Proc. 15th Biennial Conference of the Association for Machine Translation in the Americas (eds Duh, K. &amp; Guzmán, F.) Vol. 1, 309-321 (Association for Machine Translation in the Americas, 2022).
27. Costa-jussà, M. et al. Toxicity in multilingual machine translation at scale. In Findings of the Association for Computational Linguistics: EMNLP 2023, 9570-9586 (Association for Computational Linguistics, 2023).
28. Ghosh, S., Lepcha, S., Sakshi, S., Shah, R. R. &amp; Umesh, S. DeToxy: a large-scale multimodal dataset for toxicity classification in spoken utterances. In Proc. Interspeech 2022, 5185-5189 (2022); https://api.semanticscholar.org/CorpusID:247940269.
29. Costa-jussà, M. R. et al. MuTox: universal multilingual audio-based toxicity dataset and zero-shot detector. In Findings of the Association for Computational Linguistics: ACL 2024 (eds Ku, L.-W. et al.) 5725-5734 (Association for Computational Linguistics, 2024).
30. Stanovsky, G., Smith, N. A. &amp; Zettlemoyer, L. Evaluating gender bias in machine translation. In Proc. 57th Annual Meeting of the Association for Computational Linguistics (eds Korhonen, A. et al.) 1679-1684 (Association for Computational Linguistics, 2019).
31. Levy, S., Lazar, K. &amp; Stanovsky, G. Collecting a large-scale gender bias dataset for coreference resolution and machine translation. In Findings of the Association for Computational Linguistics: EMNLP 2021 (eds Moens, M. F. et al.) 2470-2480 (Association for Computational Linguistics, 2021).
32. Costa-jussà, M. R. et al. Interpreting gender bias in neural machine translation: Multilingual architecture matters. Proc. AAAI Conf. Artif. Intell. 36, 11855-11863 (2022).
33. Costa-jussà, M. R., Basta, C. &amp; Gállego, G. I. Evaluating gender bias in speech translation. In Proceedings of the Thirteenth Language Resources and Evaluation Conference (eds Calzolari, N. et al.) 2141-2147 (European Language Resources Association, 2022).
34. Bentivogli, L. et al. Gender in danger? Evaluating speech translation technology on the MuST-SHE corpus. In Proc. 58th Annual Meeting of the Association for Computational Linguistics (eds Jurafsky, D. et al.) 6923-6933 (Association for Computational Linguistics, 2020).
35. Costa-jussà, M. et al. Multilingual holistic bias: Extending descriptors and patterns to unveil demographic biases in languages at scale. In Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing, 14141-14156 (Association for Computational Linguistics, 2023).
36. Zuckerman, E. The polyglot internet. https://ethanzuckerman.com/the-polyglot-internet/ (2008).
37. Belekar, A., Sunka, S., Bhawar, N. &amp; Bagade, S. Voice based e-mail for the visually impaired. Int. J. Comput. Appl. 175, 8-12 (2020).
38. Wang, S., Cooper, N. &amp; Eby, M. From human-centered to social-centered artificial intelligence: Assessing ChatGPT's impact through disruptive events. Big Data Soc. https://doi.org/10.1177/20539517241290220 (2024).
39. Koenecke, A. et al. Racial disparities in automated speech recognition. Proc. Natl Acad. Sci. USA 117, 7684-7689 (2020).
40. Ngueajio, M. K. &amp; Washington, G. Hey ASR system! Why aren't you more inclusive? Automatic speech recognition systems' bias and proposed bias mitigation techniques. A literature review. In Proc. International Conference on Human-Computer Interaction (eds Chen, J. Y. C. et al.) Vol. 13518, 421-440 (Springer, 2022).
41. Elbow, P. The shifting relationships between speech and writing. Coll. Compos. Commun. 36, 283-303 (1985).
42. Trilla, A. &amp; Alias, F. Sentence-based sentiment analysis for expressive text-to-speech. IEEE Trans. Audio Speech Lang. Process. 21, 223-233 (2013).
43. Iranzo-Sánchez, J., Civera, J. &amp; Juan, A. From simultaneous to streaming machine translation by leveraging streaming history. In Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics, 6972-6985 (Association for Computational Linguistics, 2022).
44. Rybakov, O. et al. Streaming Parrotron for on-device speech-to-speech conversion. Preprint at https://arxiv.org/abs/2210.13761 (2022).

Publisher's note Springer Nature remains neutral with regard to jurisdictional claims in published maps and institutional affiliations.

<!-- image -->

Open Access This article is licensed under a Creative Commons AttributionNonCommercial-NoDerivatives 4.0 International License, which permits any non-commercial use, sharing, distribution and reproduction in any medium or

format, as long as you give appropriate credit to the original author(s) and the source, provide a link to the Creative Commons licence, and indicate if you modified the licensed material. You do not have permission under this licence to share adapted material derived from this article or parts of it. The images or other third party material in this article are included in the article's Creative Commons licence, unless indicated otherwise in a credit line to the material. If material is not included in the article's Creative Commons licence and your intended use is not permitted by statutory regulation or exceeds the permitted use, you will need to obtain permission directly from the copyright holder. To view a copy of this licence, visit http:// creativecommons.org/licenses/by-nc-nd/4.0/.

© Meta 2025

## SEAMLESS Communication Team

Loïc Barrault 1,4 , Yu-An Chung 1,4 , Mariano Coria Meglioli 1,4 , David Dale 1,4 , Ning Dong 1,4 , Paul-Ambroise Duquenne 1,2,4 , Hady Elsahar 1,4 , Hongyu Gong 1,4 , Kevin Heffernan 1,4 , John Hoffman 1,4 , Christopher Klaiber 1,4 , Pengwei Li 1,4 , Daniel Licht 1,4 , Jean Maillard 1,4 , Alice Rakotoarison 1,4 , Kaushik Ram Sadagopan 1,4 , Guillaume Wenzek 1,4 , Ethan Ye 1,4 , Bapi Akula 1 , Peng-Jen Chen 1 , Naji El Hachem 1 , Brian Ellis 1 , Gabriel Mejia Gonzalez 1 , Justin Haaheim 1 , Prangthip Hansanti 1 , Russ Howes 1 , Bernie Huang 1 , Min-Jae Hwang 1 , Hirofumi Inaguma 1 , Somya Jain 1 , Elahe Kalbassi 1 , Amanda Kallet 1 , Ilia Kulikov 1 , Janice Lam 1 , Daniel Li 1 , Xutai Ma 1 , Ruslan Mavlyutov 1 , Benjamin Peloquin 1 , Mohamed Ramadan 1 , Abinesh Ramakrishnan 1 , Anna Sun 1 , Kevin Tran 1 , Tuan Tran 1 , Igor Tufanov 1 , Vish Vogeti 1 , Carleigh Wood 1 , Yilin Yang 1 , Bokai Yu 1 , Pierre Andrews 1,5 , Can Balioglu 1,5 , Marta R. Costa-jussà 1,5 ✉ , Onur Çelebi 1,5 , Maha Elbayad 1,5 , Cynthia Gao 1,5 , Francisco Guzmán 1,5 , Justine Kao 1,5 , Ann Lee 1,5 , Alexandre Mourachko 1,5 , Juan Pino 1,5 , Sravya Popuri 1,5 , Christophe Ropers 1,5 , Safiyyah Saleem 1,5 , Holger Schwenk 1,5 , Paden Tomasello 1,5 , Changhan Wang 1,5 , Jeff Wang 1,5 &amp; Skyler Wang 1,3,5

1 Foundational AI Research, (FAIR) Meta, Menlo Park CA, USA. 2 INRIA, Meta, Paris, France. 3 UC Berkeley, Berkeley, CA, USA. 4 These authors contributed equally: Loïc Barrault, Yu-An Chung, Mariano Coria Meglioli, David Dale, Ning Dong, Paul-Ambroise Duquenne, Hady Elsahar, Hongyu Gong, Kevin Heffernan, John Hoffman, Christopher Klaiber, Pengwei Li, Daniel Licht, Jean Maillard, Alice Rakotoarison, Kaushik Ram Sadagopan, Guillaume Wenzek, Ethan Ye. 5 These authors jointly supervised this work: Pierre Andrews, Can Balioglu, Marta R. Costa-jussà, Onur Çelebi, Maha Elbayad, Cynthia Gao, Francisco Guzmán, Justine Kao, Ann Lee, Alexandre Mourachko, Juan Pino, Sravya Popuri, Christophe Ropers, Safiyyah Saleem, Holger Schwenk, Paden Tomasello, Changhan Wang, Jeff Wang, Skyler Wang. ✉e-mail: costajussa@meta.com

## Methods

## Data

Developing an effective multilingual and multimodal translation system such as SEAMLESSM4T requires sizeable resources across languages and modalities. Some human-labelled resources for translation are freely available, but often limited to a small set of languages or in very specific domains. Well-known examples are parallel text collections such as Europarl 45 and the United Nations Corpus 46 . A few human-created collections also involve the speech modality, such as CoVoST 47,48 and mTEDx 49 . Yet no open dataset currently matches the size of those used in initiatives such as WHISPER 20 or USM 50 , which proved to unlock unprecedented performance.

Parallel data mining emerges as an alternative to using closed data, in terms of both language coverage and corpus size. The dominant approach today is to encode sentences from various languages and modalities into a joint fixed-size embedding space and find parallel instances based on a similarity metric. Mining is then performed by pairwise comparison over massive monolingual corpora, in which sentences with similarity above a certain threshold are considered mutual translations 51,52 . This approach was first introduced using the multilingual LASER space 53 . Teacher-student training was then used to scale this approach to 200 languages 6,16 and, subsequently, the speech modality 54,55 .

Audio processing and speech LID. We started with 4 million hours of raw audio originating from a publicly available repository of crawled web data on which we applied several cleaning and filtering operations. To maximize the recall of mining, it is important that all segments have a similar granularity. For the text domain, a sentence is generally well-defined. This is less obvious for raw speech because pauses are not necessarily used at sentence boundaries. First, we used an open Voice Activity Detection model 56 to split audio files into shorter segments. Second, a newly developed speech LID model was applied to each segment. Our model follows the ECAPA-TDNN architecture 13 and extends the open-source model trained on VoxLingua107 14 by 15 new languages. Finally, we applied an over-segmentation approach that simultaneously proposed multiple, potentially overlapping speech segmentations. We relied on the mining approach to align the most likely ones. Supplementary Fig. 1 shows this pipeline.

SONAR. The SONAR text and speech encoders were developed in ref. 8 using a two-step approach (Supplementary Fig. 2). First, a massively multilingual representation was learnt for the text modality only. Then, teacher-student training was used to extend the embedding space to the speech modality. The text embedding space was trained with an encoder-decoder approach using a combination of multiple objectives: translation, denoising auto-encoding and mean squared error (MSE) loss objective in the sentence embedding space. The training data were identical to those used to train the NLLB model 6 , that is, parallel data to translation from 200 to 200 languages. Speech encoders were trained only on ASR data and by grouping languages into linguistic genealogical groups following ref. 16, for example, Italic, Common Turkic or Indo-Iranian languages. To obtain optimal performance, we determined the optimal convergence separately for each language (that is, when to stop training). This yielded a separate speech encoder for each language. The amount of available ASR data for each language is provided in Supplementary Table 8. The speech encoders were initialized with w3v-best 2.0 speech front end. Preceding work performed max pooling or mean pooling of the output states of the speech front end to obtain a fixed-size embedding of the speech signal 54,57 . An ablation study has shown that better results can be obtained by using a three-layer transformer decoder 8 . Teacher-student training consisted of minimizing the MSE loss with respect to the embedding of the ASR text transcriptions. These embeddings were obtained by the SONAR text encoder, which was kept constant. No translations (into English) were used.

SpeechAlign. We first calculated the embeddings of all over-segmented speech segments. For the text domain, we used exactly the same texts as the NLLB project 6 and embedded them with the SONAR encoder. Exhaustive pairwise comparison can be efficiently performed with the FAISS toolkit 58 . Similarity is measured with a margin criterium as first introduced in ref. 52:

x y score( , ) =margin

<!-- formula-not-decoded -->

where x and y are the source and target sentences, and NNk(x) denotes the k nearest neighbours of x in the other language. We set k to 16.

As an example, this amounts to comparing a hundred thousand hours of speech with more than 20,000 million English sentences, which yielded about eight thousand hours of aligned Arabic speech.

## Modelling

The SEAMLESSM4T models rely on our multitask UNITY architecture. Our proposed unified translation model builds on vanilla UNITY 59 , a two-pass decoding framework that first generates text and subsequently generates speech by predicting discrete acoustic units (see section 'Multilingual discrete acoustic units'). Compared with the vanilla UNITY model 59 , (1) the core S2TT model, initialized from scratch in UNITY, is replaced with an X2T model that supports text as input and is pretrained to jointly optimize the tasks of ASR, S2TT and T2TT (see section 'X2T fine-tuning'), and (2) the shallow T2U model (referred to as T2U unit encoder and second-pass unit decoder in ref. 59) is replaced with a deeper transformer-based encoder-decoder model with six transformer layers that are pretrained on ASR data (see section 'S2ST fine-tuning'). An improved version of UNITY, dubbed UNITY2, replaces the autoregressive T2U with a new non-autoregressive (NAR) T2U decoder. This NAR T2U model delivers stronger accuracy because of its hierarchical upsampling from subwords to characters and then to units.

The pretraining of X2T yielded a stronger speech encoder and a higher quality first-pass text decoder, whereas the scaling and pretraining of the T2U model allowed us to better handle multilingual unit generation without interference. Furthermore, the switch to non-autoregressive T2U decoding improved S2ST inference speed by three times.

Multilingual discrete acoustic units. Recent works have achieved state-of-the-art translation performance by using self-supervised discrete acoustic units as targets for building direct speech translation models 5,60 . This consists of decomposing the S2ST problem into a speech-to-unit translation step and a unit-to-speech conversion step. We extracted continuous speech representations using XLS-R 61 and mapped these representations to discrete tokens. The set of discrete tokens (also referred to as unit vocabulary) is learnt by applying a k-means algorithm to a set of multilingual audio samples. The k-means centroids resemble a codebook that is used to map a sequence of XLS-R speech representations into a sequence of centroid indices or acoustic units. We used a unit vocabulary size K = 10,000 with features from the 35th layer of XLS-R-1B to represent the 35 supported target languages.

For the unit-to-speech conversion step, we followed ref. 62 and built a multilingual vocoder for speech synthesis from the learnt multilingual units. This model is responsible for synthesizing audios from a sequence of units that SEAMLESSM4T models will predict.

Unsupervised speech pretraining. Self-supervised pretraining with unlabelled speech audio data is a practical approach for leveraging unlabelled data. With pretraining, we can bootstrap the quality of translation models and make the most out of our supervised paired data. We pretrained a speech encoder following our improved W2V-BERT 2.0. It follows w2v-BERT 63 in combining contrastive learning with masked prediction learning. W2V-BERT 2.0 uses more codebooks and an additional masked prediction task using random projection quantizers 64 (RPQ). Our W2V-BERT 2.0 model is first trained on 1 million hours of open speech audio data that covers over 143 languages. It follows the w2v-BERT XL architecture 63 , which has 24 Conformer layers 65 and approximately 600 million model parameters. For the v2 version, we scaled up the amount of unlabelled data from 1 million to 4.5 million hours of audio. The most recent and publicly available multilingual speech pretrained model is MMS 23 . It is trained on only 0.5 million hours, spanning over 1,400 languages. The largest model in scale is USM 50 . It is a proprietary multilingual speech pretrained model with 12 million hours of data and more than 300 languages in coverage.

Text-to-text translation models. The text processing components of our SEAMLESSM4T models were pretrained on the task of text-to-text translation, a much more resourced task than speech translation. Consider, for instance, the English-Italian direction, one of the highly resourced pairs in T2TT with more than 128 million parallel sentencesonly 2 million pairs of English text paired with Italian audio are available for S2TT.

A key step in training multilingual text-to-text translation models is learning a shared vocabulary with a text tokenizer. Following ref. 6, we used SentencePiece 66 with the BPE algorithm 67 for this purpose. The tokenizer used in NLLB-200 6 suffers from missing key Chinese characters because of artefacts of sampling. This sampling does not favour logo-graphic writing systems with a large number of unique symbols. To fix this issue, we forced the inclusion of these characters. Our new tokenizer improves the coverage of the MTSU top 5K Chinese characters from 54% to 84%.

To train our multilingual text-to-text model, we followed the same data preparation and training pipelines in ref. 6 using STOPES 68 . Having a smaller language coverage allowed us to significantly decrease the size of the model to 1.3B parameters and only use NLLB-200 training data in the 95 SEAMLESSM4T languages.

Data augmentation with pseudo-labelling. As with any sequenceto-sequence task, speech translation performance is dependent on the availability of high-quality training data. However, the amount of human-labelled data is scarce compared with its T2TT or ASR counterparts. To address this shortage of labelled data, we resort to pseudo-labelling 69,70 the ASR data with a multilingual T2TT model (for example, NLLB models) to generate pseudo-labelled S2TT data.

To augment S2ST data, it is common practice to use TTS models to convert text from speech-to-text data sets into synthetic speech 4,5 . This synthetic speech is, in turn, converted into discrete units for training. This two-step unit extraction process is a slow process and is harder to scale given the dependencies on TTS models. We circumvented the need for synthesizing speech and trained multilingual text-to-unit (T2U) models on all 36 target speech languages. These models can directly convert the text into target discrete units and can be trained on ASR data sets that are readily available.

X2T fine-tuning. The first key part of our multitask UNITY framework is the X2T model, a multi-encoder sequence-to-sequence model with a conformer-based encoder 65 for speech input and another transformer-based encoder 71 for text input. Both encoders were joined with the same text decoder and fine-tuned jointly to optimize the tasks of ASR, S2TT and T2TT.

Our X2T model consists of joining the speech encoder, W2V-BERT 2.0 from M2, post-fixed with a length adapter to downsample long audio sequences, with the text encoder-decoder from M3 (Supplementary Fig. 4). For the length adapter, we used a modified version of M-adapter 72 , in which we replaced the three independent pooling modules for Q, K and V with a shared pooling module to improve efficiency.

X2T was fine-tuned on S2TT data triplets with speech audio (x speech ) in a source language ⟨ℓs⟩, paired with its transcription (x text ) and text translation (y text ) in a target language ⟨ℓt⟩. To enable meaning transfer across modalities, X2T model was fine-tuned to jointly optimize the following objective functions:

<!-- formula-not-decoded -->

We additionally optimized an auxiliary objective function in the form of token-level knowledge distillation ( KD L ) to further transfer knowledge from the strong MT model to the student speech translation task (S2TT).

<!-- formula-not-decoded -->

The final loss is a weighted sum of all three losses: L L α = + S2TT L L β γ + , T2TT KD where α, β and γ are scalar hyper-parameters tuned on the development data.

S2ST fine-tuning. In the last stage of fine-tuning multitask UNITY, we initialized the model with the pretrained X2T model (see section 'X2T fine-tuning') and a pretrained T2U model, similar to the one used for pseudo-labelling S2ST data in M4. The T2U model used for pseudo-labelling is referred to as the teacher T2U model with 12 transformer layers encoder-decoder. For initialization, we used a smaller student T2U model with only six layers to optimize inference and distill the labels of the stronger T2U. In the second version of SEAMLESSM4T, UNITY2 replaces the second-pass autoregressive unit decoder in UNITY with a NAR unit decoder. We adopted the decoder architecture of FastSpeech2 73 and extended it to discrete unit generation. UNITY2 starts with hierarchically upsampling the T2U encoder output from subword length to character length and then to unit length. The unit duration predictor, the key to the hierarchical upsampling, is supervised during training by a multilingual aligner based on RAD-TTS 74 . The architecture is shown in detail in Supplementary Information section IV.8.

We fine-tuned the S2ST task with a combination of X-eng and eng-X S2ST translation data totalling 121,000 h. We froze the model weights corresponding to the X2T model and only fine-tuned the T2U component. This is to ensure that the performance of the model on tasks from the previous stages of fine-tuning remains unchanged.

## Automatic and human evaluation

BLASER 2.0. BLASER 2.0 (ref. 24) is the new version of BLASER 75 , which works with both speech and text modalities, and hence being modality-agnostic. Like the first version, our approach leverages the similarity between input and output sentence embeddings. The new version uses SONAR embeddings Supplementary Information section III.3.1, supports 57 languages in speech and 202 in text (coverage of languages by SONAR at the moment of submission of this paper) and is extendable to future encoders for new languages or modalities that share the same embedding spaces. For the purposes of evaluating speech outputs (and unlike ASR-based metrics), BLASER 2.0 offers the advantage of being text-free.

More specifically, in BLASER 2.0, we take the source input, the translated output from any S2ST, S2TT or T2TT model, and the reference speech segment or text, and convert them into SONAR embedding vectors. For the supervised version of BLASER 2.0, these embeddings are combined and fed into a small, dense neural network that predicts an XSTS score for each translation output.

Human evaluation. Apart from automatic metrics such as (ASR) BLEU and BLASER 2.0, we used human metrics such as XSTS 26 , which measures semantic similarity between a source and target translation, and a standard Mean Opinion Score (as standardized in Recommendation ITU-T P.800, henceforth MOS), which measures (1) naturalness, (2) sound quality and (3) clarity of audio generations to evaluate our models. To obtain more robust language-level scores, we also incorporate a calibration set and calibration methodology, the same used to evaluate the NLLB models 6 . Apart from XSTS, we also obtained MOS evaluations to understand other aspects of audio quality in the target speech. For additional information about human evaluation protocols and analysis, see Supplementary Information section V.1.

Robustness. We built a replicable noise-robustness evaluation benchmark based on FLEURS (noisy FLEURS), which covers 102 languages, two speech tasks (S2TT and ASR), and various noise types (natural noises and music). To create simulated noisy audios, we sampled audio clips from MUSAN 76 on the 'noise' and 'music' categories and mixed them with the original FLEURS speech audios under different signal-to-noise ratio (SNR): 10, 5, 0, -5, -10, -15 and -20. We compared models by BLEU-SNR curves (for S2TT) or WER-SNR curves (for ASR), which illustrate the degree of model performance degradation when the noise level of speech inputs increases (that is, when SNR decreases). For low-resource languages, the clean speech setup is already challenging, let alone a noisy one. Thus, we focused on four high-resource languages (French, Spanish, Modern Standard Arabic and Russian) belonging to three different language families for our noise-robustness analysis.

We followed ref. 47 to evaluate model robustness against speaker variations by calculating the average by-group mean score and by-group coefficient of variation using an utterance-level quality metric. Instead of using BLEU as the quality metric, we used chrF, which has better stability at the utterance level. The calculation of both robustness metrics does not require explicit speaker subgroup labels. We grouped evaluation samples and corresponding utterance-level chrF scores by content (transcript) and then calculated the average by-group mean score chrFMS and average by-group coefficient of variation CoefVarMS, defined as follows:

<!-- formula-not-decoded -->

where G is the set of sentence-level chrF scores grouped by content (transcript) and ∣ ∣ ∣ G g g G g g ′= { ∈ , &gt; 1,Mean( ) &gt;0}. The two metrics are complementary: chrFMS provides a normalized quality metric that, unlike conventional corpus-level metrics, takes speaker variations into consideration, whereas CoefVarMS provides a standardized measure of quality variance under speaker variations. For robustness analysis, we conducted an out-of-domain evaluation on FLEURS on all languages that have at least 40 content groups in the test sets.

## Responsible AI

Toxicity detection. Inspired by ASR-BLEU, this work proposes using ASR-ETOX as a new metric to detect added toxicity in speech and evaluate added toxicity for S2ST ability of SEAMLESSM4T. Essentially, this metric follows a cascaded framework by first deploying a standard ASR module (that is, the same that is used for ASR-BLEU as defined in Supplementary Table 2), then the toxicity detection module, ETOX 27 , which uses the Toxicity-200 word lists 6 . For S2TT, the translated output can be directly evaluated with ETOX. In both cases (S2ST and S2TT), we measured added toxicity at the utterance or sentence level. We first computed toxicity detection for each input in the evaluation dataset and the corresponding output. Then, we compared them and counted a case as containing added toxicity only when the output value exceeds that of the input. Moreover, we used the recently proposed MuTox metric that can be applied to text or speech output with no need for ASR. This classifier has been trained on both speech and text toxicity labelled data for 30 languages. As MuTox relies on SONAR embeddings 29 , MuTox the same number of languages by the zero-shot property. However, accounting for validated quality, we report MuTox only the languages that have been benchmarked 29 . Again in both cases (S2ST and S2TT), we measured added toxicity at the utterance or sentence level. In this case, a sentence contains added toxicity if MuTox scores is &gt;0.9 in the output and &lt;0.5 in the input. We have experimentally validated these thresholds for several languages with human bilingual speakers for several pairs of languages. For S2TT, we computed MuTox in transcribed speech and target text. For S2ST, we computed MuTox in source and target speech.

For toxicity mitigation, we implement two techniques for the mitigation of added toxicity. Before training, we filter out training pairs with imbalanced toxicity. Furthermore, we use Mintox 11 at inference time. In particular, the main workflow generates a translation hypothesis with an unconstrained search. Then, the toxicity classifier is run on this hypothesis. If no toxicity is detected, we provide the translation hypothesis as it is. However, if toxicity is detected in the output, we run the classifier on the input. If the toxicity is unbalanced (that is, no toxicity is detected in the input), we re-run the translation with mitigation, which is the BEAMFILTERING step. This BEAMFILTERING consists of taking as input the multi-token expressions that should not appear in the output and excluding them from the beam-search hypotheses. Note that we do not apply mitigation in cases in which there is toxicity in the input (in other words, we do not deal with cases in which there is toxicity in the input but more toxicity in the output).

We used two datasets to analyse added toxicity. First, we deployed FLEURS to better align with our human evaluation effort and other evaluative components of this work. Furthermore, we used the English-only HOLISTICBIAS framework 77 , which has been shown to trigger true added toxicity in previous studies 27 . In this work, we extend HOLISTICBIAS to speech by applying the default English TTS model from MMS 23 .

Speech extension of MULTILINGUAL HOLISTICBIAS. To compare the performances across modalities (S2ST and S2TT), we extended MULTILINGUAL HOLISTICBIAS to speech 23 (https://github.com/ facebookresearch/fairseq/tree/main/examples/mms#tts-1). We used this generated TTS data as input for S2TT and S2ST and as a reference for S2ST. We conducted the translations in two directions: eng-X and X-eng. Concretely, in X-eng, we translated both masculine and feminine versions of the speech. It is worth noting that some target languages are not available in the SEAMLESSM4T S2ST model, so we performed translations on only 17 languages for the S2ST task in the eng-X direction. For S2TT in eng-X, we have all languages included in the MULTILINGUAL HOLISTICBIAS dataset (n = 25). For reference, the complete language list used in our experiments can be found in Supplementary Table 26.

In terms of evaluation metrics for S2TT, we used chrF. For S2ST, we used ASRchrf (the transcription is done by WHISPER-LARGE and WHISPER-MEDIUM 20 for eng-X and X-eng, respectively, and chrF has been calculated the same way as S2TT except that in S2ST, the text from both prediction and reference were normalized) and BLASER 2.0. It is worth noting that when evaluating on BLASER 2.0, we only included 14 languages (arb, cat, deu, eng, fra, nld, por, ron, rus, spa, swe, tha, ukr and urd) for the eng-X direction (overlapping languages from the generated TTS data and the languages available in our S2ST model).

## Data availability

To make our work available to the community, we provide open source of the following data sets, models and code at GitHub (https://github. com/facebookresearch/seamless\_communication): (1) SEAMLESSM4T models, including model weights for SEAMLESSM4T-LARGE (2.3B parameters) and SEAMLESSM4T-MEDIUM (1.2B parameters), as well as their inference code and fine-tuning recipes powered by our new modelling toolkit FAIRSEQ2 (https://github.com/facebookresearch/ fairseq2); (2) tools for creating aligned speech data, including metadata to recreate the unfiltered 470,000 h of SEAMLESSALIGN, STOPES-based pipelines (https://github.com/facebookresearch/stopes) to create alignments similar to SEAMLESSALIGN and SONAR for speech encoders in 37 languages and text encoders in 200 languages (https://github. com/facebookresearch/SONAR) and (3) a text-free S2ST automatic evaluation model, BLASER 2.0, inclusive of model weights and inference scripts.

45. Koehn, P. Europarl: A parallel corpus for statistical machine translation. In Proceedings of Machine Translation Summit X: Papers, 79-86 (2005).
46. Ziemski, M., Junczys-Dowmunt, M. &amp; Pouliquen, B. The United Nations Parallel Corpus v1.0. In Proceedings of the Tenth International Conference on Language Resources and Evaluation (LREC'16) (eds Calzolari, N. et al.) 3530-3534 (European Language Resources Association, 2016).
47. Wang, C., Pino, J., Wu, A. &amp; Gu, J. CoVoST: a diverse multilingual speech-to-text translation corpus. In Proceedings of the Twelfth Language Resources and Evaluation Conference (eds Calzolari, N. et al.) 4197-4203 (European Language Resources Association, 2020).
48. Wang, C., Wu, A., Gu, J. &amp; Pino, J. CoVoST 2 and Massively Multilingual Speech Translation. In Proc. Interspeech 2021, 2247-2251 (ISCA, 2021).
49. Salesky, E. et al. The multilingual TEDx corpus for speech recognition and translation. In Proc. Interspeech 2021, 3655-3659 (ISCA, 2021).
50. Zhang, Y. et al. Google USM: scaling automatic speech recognition beyond 100 languages. Preprint at https://arxiv.org/abs/2303.01037 (2023).
51. Schwenk, H. Filtering and mining parallel data in a joint multilingual space. In Proc. 56th Annual Meeting of the Association for Computational Linguistics (eds Gurevych, I. &amp; Miyao, Y.) Vol. 2, 228-234 (Association for Computational Linguistics, 2018).
52. Artetxe, M. &amp; Schwenk, H. Margin-based parallel corpus mining with multilingual sentence embeddings. In Proc. 57th Annual Meeting of the Association for Computational Linguistics (eds Korhonen, A. et al.) 3197-3203 (Association for Computational Linguistics, 2019).
53. Artetxe, M. &amp; Schwenk, H. Massively multilingual sentence embeddings for zero-shot cross-lingual transfer and beyond. Trans. Assoc. Comput. Linguist. 7, 597-610 (2019).
54. Duquenne, P.-A., Gong, H. &amp; Schwenk, H. Multimodal and multilingual embeddings for large-scale speech mining. In Advances in Neural Information Processing Systems (eds Ranzato, M. et al.) Vol. 34, 15748-15761 (Curran Associates, 2021).
55. Duquenne, P.-A. et al. SpeechMatrix: a large-scale mined corpus of multilingual speechto-speech translations. In Proc. 61st Annual Meeting of the Association for Computational Linguistics (eds Rogers, A. et al.) Vol. 1, 16251-16269 (2023).
56. Silero. Silero VAD: pre-trained enterprise-grade voice activity detector (VAD), number detector and language classifier. GitHub https://github.com/snakers4/silero-vad (2021).
57. Khurana, S., Laurent, A. &amp; Glass, J. SAMU-XLSR: Semantically-Aligned Multimodal Utterance-Level Cross-Lingual Speech Representation. IEEE J. Sel. Top. Signal Process. 16, 1493-1504 (2022).
58. Douze, M. et al. The Faiss library. Preprint at https://arxiv.org/abs/2401.08281 (2024).
59. Inaguma, H. et al. UnitY: two-pass direct speech-to-speech translation with discrete units. In Proc. 61st Annual Meeting of the Association for Computational Linguistics (eds Rogers, A. et al.) Vol. 1, 15655-15680 (Association for Computational Linguistics, 2023).
60. Tjandra, A., Sakti, S. &amp; Nakamura, S. Speech-to-speech translation between untranscribed unknown languages. In 2019 IEEE Automatic Speech Recognition and Understanding Workshop (ASRU), 593-600 (IEEE, 2019).
61. Babu, A. et al. XLS-R: self-supervised Cross-lingual Speech Representation Learning at Scale. In Proc. Interspeech 2022, 2278-2282 (ISCA, 2022).
62. Gong, H. et al. Multilingual speech-to-speech translation into multiple target languages. Preprint at https://arxiv.org/abs/2307.08655 (2023).
63. Chung, Y.-A. et al. w2v-BERT: combining contrastive learning and masked language modeling for self-supervised speech pre-training. In 2021 IEEE Automatic Speech Recognition and Understanding Workshop (ASRU), 244-250 (IEEE, 2021).
64. Chiu, C.-C., Qin, J., Zhang, Y., Yu, J. &amp; Wu, Y. Self-supervised learning with random-projection quantizer for speech recognition. In Proc. 39th International Conference on Machine Learning, 3915-3924 (PMLR, 2022).
65. Gulati, A. et al. Conformer: convolution-augmented transformer for speech recognition. In Proc. Interspeech 2020, 5036-5040 (ISCA, 2020).
66. Kudo, T. &amp; Richardson, J. SentencePiece: a simple and language independent subword tokenizer and detokenizer for neural text processing. In Proc. 2018 Conference on Empirical Methods in Natural Language Processing: System Demonstrations (eds Blanco, E. &amp; Lu, W.) 66-71 (Association for Computational Linguistics, 2018).
67. Sennrich, R., Haddow, B. &amp; Birch, A. Neural machine translation of rare words with subword units. In Proceedings of the 54th Annual Meeting of the Association for Computational Linguistics (eds Erk, K. &amp; Smith, N. A.) Vol. 1, 1715-1725 (Association for Computational Linguistics, 2016).
68. Andrews, P. et al. stopes - modular machine translation pipelines. In Proc. 2022 Conference on Empirical Methods in Natural Language Processing: System Demonstrations (eds Che, W. &amp; Shutova, E.) 258-265 (Association for Computational Linguistics, 2022).
69. Jia, Y. et al. Leveraging weakly supervised data to improve end-to-end speech-to-text translation. In 2019 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP), 7180-7184 (IEEE, 2019).
70. Pino, J., Xu, Q., Ma, X., Dousti, M. J. &amp; Tang, Y. Self-training for end-to-end speech translation. In Proc. Interspeech 2020, 1476-1480 (2020).
71. Vaswani, A. et al. Attention is all you need. In Advances in Neural Information Processing Systems (eds Guyon, I. et al.) Vol. 30 (Curran Associates, 2017).
72. Zhao, J., Yang, H., Haffari, G. &amp; Shareghi, E. M-Adapter: modality adaptation for end-to-end speech-to-text translation. In Proc. Interspeech 2022, 111-115 (ISCA, 2022).
73. Ren, Y. et al. FastSpeech 2: fast and high-quality end-to-end text to speech. In Proc. 2021 International Conference on Learning Representations (2021).
74. Shih, K. J. et al. RAD-TTS: parallel flow-based tts with robust alignment learning and diverse synthesis. In ICML Workshop on Invertible Neural Networks, Normalizing Flows, and Explicit Likelihood Models (2021).
75. Chen, M. et al. BLASER: A text-free speech-to-speech translation evaluation metric. In Proc. 61st Annual Meeting of the Association for Computational Linguistics (eds Rogers, A. et al.) Vol. 1, 9064-9079 (Association for Computational Linguistics, 2023).
76. Snyder, D., Chen, G. &amp; Povey, D. MUSAN: a music, speech, and noise corpus. Preprint at https://arxiv.org/abs/1510.08484 (2015).
77. Smith, E. M., Hall, M., Kambadur, M., Presani, E. &amp; Williams, A. "I'm sorry to hear that": finding new biases in language models with a holistic descriptor dataset. In Proc. 2022 Conference on Empirical Methods in Natural Language Processing (eds Goldberg, Y. et al.) 9180-9211 (Association for Computational Linguistics, 2022).

Acknowledgements We want to extend our gratitude to those who made this work possible. We thank S. Edunov and A. Fan for helping shape the earlier stages of the project; S. Bhosale, V. Goswami, F. Hernandez and Y. Tang for their help in building stronger models; M. Chen for his contributions to BLASER 1.0; K. Klyushkin for his help in building better experiences; A. Kozhevnikov for his contributions to FAIRSEQ2 and SONAR inference; Z. Ni and X. Zhang for benchmarking audio denoising models; N. Seejoor and M. Duppenthaler for their help in setting up the demo; V. Goswami, S. Hsia, B. Acun-Uyan, and C.-J. Wu for helping with efficiency optimizations; B. Alastruey, M. Anwar, H.-J. Chang, H. Han, C.-W. Huang, H. Lu, S. Ouyang, Y. Peng, P. Rust, J. Shi, N. Verma, S.-L. Yeh and all of our interns and residents for the generative discussions they brought to the team; M. Clark, L. Cohen, J. Pak and H. Rudolph for their advice and guidance; E. Astbury, L. Baillergeau, D. Beaty, J. Bennett, J. Carvill, A. Davidson, A. Farooq, A. Gabriel, G. Jhala, C. Johnson, S. Miles, A. P. K. Mofarrej, R. Nayani, A. Newcomb, T. Piksa, M. Restrepo, N. Rizk and A. Tharinger for helping our research reach new audiences; G. Chauhan, A. Gunapal, C. Ho, D. Kannappan, A. Kokolis, T. Li, M. Reso, S. Sengupta, H. Shojanazeri and X. Zhang for assisting us with compute resources and infrastructure; E. Dupoux and E. M. Smith for their feedback on the paper; C. Moghbel, M. Paluri, J. Pineau, L. van der Maaten and M. Williamson for their continued support of the project.

Author contributions Core contributors to SEAMLESSM4T and their areas of contribution are specified as follows: L.B., P.-A.D., H.E., K.H., G.W., P.A., O.Ç., C.G., J.K. and H.S. contributed to the data workstream of the project, which includes data acquisition and developing tools to facilitate data mining, cleaning and consolidation. P.A., M.R.C., D.D., J. Hoffman and D.L. contributed to the evaluation workstream, which assessed automatic and human quality. P.A., N.D., M.E., C.K., A. Rakotoarison, E.Y., C.B. and J.W. contributed to externalization, including fairseq2 development and demo experiences. P.L., K.R.S., M.E., A.L., S.P., P.T., C. Wang, Y.-A.C., N.D., H.G. and J.M. contributed to the modelling workstream. P.A., M.R.C., M.C.M., H.E., M.E., H.G., C.R. and S.W. contributed to Responsible AI, which includes toxicity, bias, linguistics and social impact evaluations. F.G., J.K., A.M., J.P., H.S., S.S. and P.T. provided leadership for the project. Contributors to SEAMLESSM4T are B.A., P.-J.C., N.E.H., B.E., G.M.G., J. Haaheim, P.H., R.H., B.H., M.-J.H., H.I., S.J., E.K., A.K., I.K., J.L., D.L., X.M., R.M., B.P., M.R., A.R., A.S., K.T., T.T., I.T., V.V., C.W., Y.Y. and B.Y.; M.R.C., C.R., M.E. and S.W. constitute the editorial team and prepared the paper for publication.

Competing interests The authors declare no competing interests.

## Additional information

Supplementary information The online version contains supplementary material available at https://doi.org/10.1038/s41586-024-08359-z.

Correspondence and requests for materials should be addressed to Marta R. Costa-jussà. Peer review information Nature thanks Tanel Alumäe, Allison Koenecke and the other, anonymous, reviewer(s) for their contribution to the peer review of this work. Peer reviewer reports are available.

Reprints and permissions information is available at http://www.nature.com/reprints.

## Article

Extended Data Table 1 | F1 micro and macro averages over all SEAMLESSM4T languages and the intersection of supported languages across models Extended Data Table 2 | Average T2TT and S2TT performance on FLORES devtest and FLEURS's test set

## Article

Extended Data Table 3 | The averaged points across modalities and genders for assessing the overgeneralization (eng-X) and the robustness (X-eng)

Δ represents the relative difference between masculine and feminine (Δ = ω(M - F)/ω(min(M, F)), ω ∈ {chrF, ASRchrf, BLASER 2.0}). Baseline corresponds to WHISPER-LARGE-V2 for S2TT X-eng; WHISPER-LARGE-V2 + NLLB-3.3B for S2TT X-eng; WHISPER-LARGE-V2 + YOURTTS for S2ST X-eng.

Supplementary information

## Joint speech and text machine translation for up to 100 languages

In the format provided by the authors and unedited

Nature | www.nature.com/nature

## Supplementary Information I The Sociotechnical Dimensions of Multimodal Translation

## Supplementary Information I.1 Why Prioritize Speech in Machine Translation?

As is the case with most technologies within natural language processing (NLP) and other language-based research enterprises, MT reached greater maturity in the modality that affords easier record-keeping, data storage, and dispersion: text. By extension, the abundance of digital text makes it a prime candidate for NLP research. In contrast, the relative paucity of speech data relegates research in this area to secondary importance. More specifically, speech is not just spoken text-the two modalities can differ in grammar, registers, and morphology [78]. In most situations, speech may also appear to be a richer modality, possessing prosodic and expressive parameters unmatchable by text [79]. Distinctive in their level of interactivity and sociality, speech directs focus at the speaker or audience, while text spotlights the content of a message [79].

## Speech &amp; social bonding

Research suggests that compared to text-based exchange, communication through speech creates stronger social bonds between interlocutors. For example, in one study, researchers found that interactions including speech (phone, video call, and voice chat) spurred deeper connections between conversation partners compared to those who communicated via text-based media [80, p. 595]. Juxtaposed against speech, which comes with paralinguistic cues such as volume, intonation, and pace, text-based communication is perceived as more impersonal. Interestingly, seeing another person did not make individuals feel more connected than if they had just spoken with their partners. In another study, hearing an outgroup member explain their views out loud made study participants consider them more thoughtful and emotionally warm than reading an explanation of their views [81]. Across a variety of settings, research demonstrates that speech appears to be unique in its ability to convey one's human traits and, consequentially, strengthen the connection between those sharing an exchange.

## Inclusion &amp; accessibility

Speech is not only key to communication from a relational standpoint but is also often the most practical and accessible option. For one, UNESCO estimates that 773 million adults (12.5 percent of all adults) worldwide have not received the education necessary to read or write, thus precluding them from using text to communicate or acquire information [82]. Another group more reliant on speech than text in their everyday lives is those who are blind or with visual impairments. Globally, approximately 43 million people belong to this former category, and 295 million others have moderate to severe visual impairment [83]. Even though voice assistants, text-to-speech systems, and voice-activated technologies today play an important role in supporting these individuals to accomplish everyday tasks, their access to multilingual speech-based Supplementary table 1: Options for 2-stage and 3-stage cascaded systems for S2TT and S2ST. These cascades pair Whisper ASR models [20] with NLLB's T2TT models [6].

| Cascaded models for S2TT                                                 |                                   |
|--------------------------------------------------------------------------|-----------------------------------|
| Whisper-Medium + NLLB-600M-Distilled Whisper-Large-v2 + NLLB-1.3B        | 2-stage cascaded 2-stage cascaded |
| Cascaded models for S2ST                                                 |                                   |
| Whisper-Large-v2 + NLLB-1.3B + YourTTS Whisper-Large-v2 (S2TT) + YourTTS | 3-stage cascaded 2-stage cascaded |
| SeamlessM4T (this work)                                                  | unified                           |

translation or communicative tools remains limited. In a world where the volume of auditory content (i.e., podcasts, audiobooks, short-form videos, etc.) is on the rise, the prohibitive nature of this sociotechnical gap may deprive them of experiences or exchanges that could be meaningful and enriching.

## Script variance

Beyond these factors, text-based communication or translation is further complicated by script variance. For instance, some languages are written in different scripts on either side of a geopolitical border. Urdu, for example, could be written either in the Arabic or Devanagari script depending on where one lives (i.e., Pakistan or India). In such a context, T2TT outputs into Urdu may be illegible to those shown in a script they are unfamiliar with. S2ST, which produces speech outputs, circumvents this multiscript conundrum. In a few other cases, political instabilities around a language's writing system may also motivate the need for speech-based translation. For example, in the last 1,000 years, Uzbek has changed its writing system five times. Despite the fact that-as of February 2021-Uzbekistan announced Uzbek's official transition from the Cyrillic script to a Latin-based alphabet, the former continues to be widely deployed in the country [84]. For languages where writing systems are actively negotiated, speech-based technologies and translation systems may provide stabilized access to information as transitions unfold.

## Supplementary Information I.2 Speech Translation Today

## Cascaded systems

Before the emergence of unified speech translation models in recent years, much attention in speech-based research has been directed at cascaded approaches by chaining subsystems that perform disparate tasks such as ASR, T2TT, and TTS [1-3]. For example, in a 3-stage S2ST cascaded scenario, speech input is first transcribed into text through an ASR system, followed by T2TT, and finally synthesized into speech using TTS (see Supplementary table 1). The main benefit of cascaded systems is that they can take advantage of advancements made in areas associated with each subsystem, such as recently released large-scale multilingual T2TT models [6, 85, 86] and weakly-supervised ASR models [20, 23, 50].

That said, cascaded systems have their limitations. For one, the output of a 2stage cascaded S2TT system involving ASR and T2TT does not match the quality achievable by a single large-scale T2TT model. This drop in performance underscores the challenge of transferring and translating meaning across modalities and can be attributed to many factors, including: (1) poor transcriptions by ASR models for nonEnglish languages, particularly for low-resourced ones, (2) an increased likelihood of error propagation from the ASR model to the T2TT model and other subsequent models in the cascade (the accumulation of errors exacerbates performance), and (3) domain mismatches between these separately trained subsystems (for example, if an ASR model trained on Wikipedia is used in conjunction with a T2TT model optimized for conversational data, this formation may lead to a distribution mismatch at the T2TT stage). Beyond these reasons, the overemphasis on text in cascaded systems omits paralinguistic features and may not adequately handle elements such as proper names and nouns [21].

## Direct S2TT models

Early research into end-to-end speech translation started with producing text as output [87-89]. Since the emergence of multilingual end-to-end S2TT models in 2019 [90, 91], S2TT has become an increasingly popular research area, and many existing models today are powered by the emergence of open multilingual speech corpora like MuST-C [92], EuroParl-ST [93], CoVoST 2 [48] and VoxPopuli [94]. End-to-end models today have made significant progress and achieved parity with cascaded models on academic benchmarks in several contexts (e.g., constrained data, in-domain settings, specific language pairs, etc.) [95, 96]

While recent state-of-the-art pre-trained models have seen rapid improvements in language coverage, going from 128 in [61] to more than 1,400 in [23], they only translate into English and not the other way around. Another prominent model, Google's Universal Speech Model [50], is pre-trained in more than 300 languages and can perform ASR on more than 100 languages. Technically, USM can also be adapted to perform ASR and S2TT tasks in any of the 300+ covered languages once given supervised data (but the model was fine-tuned and evaluated on CoVoST 2, which only covers translations from 21 languages into English).

OpenAI's Whisper [20] is another large-scale model that serves translations into English, not vice versa. As a multitasking model, Whisper demonstrates that scaling weakly supervised pre-training is sufficient for achieving state-of-the-art ASR and S2TT results sans self-supervision and self-training techniques. Trained on 680,000 hours of data, Whisper has achieved state-of-the-art translation quality in 82 Fleurs languages into English.

Combining a text-based [97] and speech-based language model [98], the most recently released AudioPaLM [21] is a large language model designed for joint text and speech processing and generation. Akin to USM, AudioPaLM only evaluates text translation outputs from 101 Fleurs languages into English. Upon the publication of this paper, AudioPaLM is the current state-of-the-art model, outperforming Whisper [20] in both ASR and S2TT tasks.

Supplementary table 2: The list of automatic and human evaluation metrics used in this work.

| Task   | Metric      | Type                  | Area                    | Citation   | Implementation                                                                                                                                                                                                                                                         |
|--------|-------------|-----------------------|-------------------------|------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ASR    | WER         | Automatic             | Quality Robustness      | Automatic  | Text normalization follows Whisper [20]                                                                                                                                                                                                                                |
| T2TT   | BLEU        | Automatic             | Quality                 | [10]       | SacreBLEU signature: nrefs:1&#124;case:mixed&#124;eff:no&#124;tok:13a&#124;smooth:exp&#124;version:2.3.1 Except for cmn, jpn, tha, lao and mya with character-level tokenization: nrefs:1&#124;case:mixed&#124;eff:no&#124;tok:char&#124;smooth:exp&#124;version:2.3.1 |
| T2TT   | chrF2++     | Automatic             | Quality                 | [9]        | SacreBLEU signature: nrefs:1&#124;case:mixed&#124;eff:yes&#124;nc:6&#124;nw:2&#124;space:no&#124;version:2.3.1                                                                                                                                                         |
| S2TT   | Blaser 2.0  | Automatic Model-based | Quality Bias            | [24]       | blaser_2_0_ref model                                                                                                                                                                                                                                                   |
| S2TT   | BLEU        | Automatic             | Quality Robustness Bias | [10]       | Similar to T2TT                                                                                                                                                                                                                                                        |
| S2TT   | chrFMS/chrF | Automatic             | Robustness Bias         | [9]        | Following [47], replaced BLEU with chrF for the quality metric. SacreBLEU signature: nrefs:1&#124;case:mixed&#124;eff:yes&#124;nc:6&#124;nw:0&#124;space:no&#124;version:2.3.1                                                                                         |
| S2TT   | CoefVarMS   | Automatic             | Robustness              | [99]       |                                                                                                                                                                                                                                                                        |
| S2TT   | XSTS        | Human                 | Quality                 | [26]       |                                                                                                                                                                                                                                                                        |
| S2TT   | ETOX        | Automatic             | Toxicity                | [27]       |                                                                                                                                                                                                                                                                        |
| S2TT   | MuTox       | Automatic             | Toxicity                | [29]       |                                                                                                                                                                                                                                                                        |
| S2ST   | ASR-BLEU    | Automatic             | Quality                 |            | Transcribing with Whisper-Large BLEU on normalized transcriptions following [20]                                                                                                                                                                                       |
| S2ST   | ASR-chrF    | Automatic             | Bias                    |            | Transcribing with Whisper-Large on normalized transcriptions following [20]                                                                                                                                                                                            |
| S2ST   | Blaser 2.0  | Automatic Model-based | Quality Bias            | [24]       | Similar to S2TT                                                                                                                                                                                                                                                        |
| S2ST   | XSTS MOS    | Human Human           | Quality Naturalness     | [26] [100] |                                                                                                                                                                                                                                                                        |
| S2ST   | ASR-ETOX    | Automatic             | Toxicity                | [99]       | Transcribing with Whisper-Large. ETOX on normalized transcriptions following [20]                                                                                                                                                                                      |
| S2ST   | MuTox       | Automatic             | Toxicity                | [29]       | Directly on speech                                                                                                                                                                                                                                                     |
| T2ST   | ASR-BLEU    | Automatic             | Quality                 |            | Similar to S2ST                                                                                                                                                                                                                                                        |

## Direct S2ST models

Beyond text outputs, recent speech translation research has focused on building models that directly produce target speech representations (i.e., spectrograms, discrete units, etc.). In this area, Translatotron [4] emerged as the first direct S2ST model. When it comes to quality, however, the model lagged behind 2-stage cascaded systems by a large margin. Translatotron-2 [101] significantly improved its predecessor's performance and bridged the gap with cascaded systems by incorporating a two-pass decoding approach. Although Translatotron relied on S2TT as an auxiliary task during training, the target spectrograms were directly generated at inference time. Translatotron-2, on the other hand, relies on the intermediate decoding outputs of phonemes.

Concurrently with Translatotron, [60] proposed S2ST models based on discrete speech representations that do not require text transcriptions in training. These discrete representations or units are learned through unsupervised term discovery and a sequence-to-sequence model trained to translate units from one language to another. Relatedly, [5] uses HuBERT [102], a pre-trained speech representation model, to encode speech and learn target-side discrete units. S2ST is, thus, decomposed into speech-to-unit (S2U) and subsequently unit-to-speech with a speech re-synthesizer [103].

## On coverage and evaluation of S2ST systems

To date, the aforementioned AudioPaLM [21], which supports both text and speech as input and output, is the current state-of-the-art for S2TT and S2ST. Although the model design suggests that it can support multilingual translation on both source and target sides, its performance is only reported for translating into English. Similarly, although Whisper can transcribe non-English languages, it only supports S2TT into English. To consolidate the current landscape of language coverage and related tasks in speech translation systems, we provide in Table 1 a list of state-of-the-art models in text and speech translation. This language coverage is estimated based on supervised labeled data or evaluated zero-shot languages and directions. We also provide the list of ASR, T2TT, S2TT and S2ST evaluation metrics used by this work in Supplementary table 2. For S2ST, our evaluation focuses on the semantic content of the translation. Throughout this paper, we primarily evaluated our models on the following datasets:

- Flores-200 [6]: a many-to-many multilingual translation benchmark dataset for 200 languages (we evaluated on devtest).
- Fleurs [18]: an n-way parallel speech and text dataset in 102 languages built on the text translation Flores-101 benchmark [104]. Fleurs is well suited for several downstream tasks involving speech and text. We evaluated on the test set, except in ablation experiments where we evaluated on the dev set.
- CoVoST 2 [48]: a large-scale multilingual S2TT corpus covering translations from 21 languages into English and from English into 15 languages. We evaluated on the test set.
- CVSS [105]: a multilingual-to-English speech-to-speech translation (S2ST) corpus, covering sentence-level parallel S2ST pairs from 21 languages into English. We evaluated text-based semantic accuracy on CVSS-C for the tasks of S2ST and T2ST. We note that some samples from the evaluation data were missing (in

8 out of 21 languages: Catalan, German, Estonian, French, Italian, Mongolian, Persian, and Portuguese).

## Supplementary Information II Languages

We summarize information about each of our supported languages in Supplementary table 3. Further details on the table headers are provided below.

## Code

We represent each language with a three-letter ISO 639-3 code.

## Language

There may be multiple ways to refer to the same language; due to formatting limitations, only one of the versions is displayed. The language names have been crossreferenced with major linguistic information platforms such as Ethnologue [106] and Glottolog [107].

## Family and subgrouping

We provide Language family information for each language based on the Glottolog database [107].

## Script

We provide script information in ISO 15924 codes for writing systems.

## Resource level

We categorize the speech resource level as high, medium, or low depending on the volume of available primary data for S2TT into English (with x the amount of primary data in hours, high if x &gt; 1000, medium if x ∈]500, 1000] and low if x ∈ [0, 500]).

Primary data is defined as open-source S2TT and pseudo-labeled ASR data. Absent such data, we report the language as zero-shot (when evaluating S2TT into English).

## Source

We indicate whether a source language is in the speech (Sp) or text (Tx) modality, or both.

## Target

We indicate whether a target language is in the speech (Sp) or text (Tx) modality, or both.

| Code    | Language name          | Family                     | Script     | Resource      | Source        | Target    |
|---------|------------------------|----------------------------|------------|---------------|---------------|-----------|
| afr     | Afrikaans              | Indo-European              | Latn       | low           | Sp, Tx        | Tx        |
| amh     | Amharic                | Afro-Asiatic               | Ethi       | low           | Sp, Tx        | Tx        |
| arb     | Modern Standard Arabic | Afro-Asiatic               | Arab       | high          | Sp, Tx        | Sp, Tx    |
| ary     | Moroccan Arabic        | Afro-Asiatic               | Arab       | low           | Sp, Tx        | Tx        |
| arz     | Egyptian Arabic        | Afro-Asiatic               | Arab       | low           | Sp, Tx        | Tx        |
| asm     | Assamese               | Indo-European              | Beng       | low           | Sp, Tx        | Tx        |
| ast     | Asturian               | Indo-European              | Latn       | zero-shot     | Sp            | -         |
| azj     | North Azerbaijani      | Turkic                     | Latn       | low           | Sp, Tx        | Tx        |
| bel     | Belarusian             | Indo-European              | Cyrl       | high          | Sp, Tx        | Tx        |
| ben     | Bengali                | Indo-European              | Beng       | high          | Sp, Tx        | Sp, Tx    |
| bos     | Bosnian                | Indo-European              | Latn       | low           | Sp, Tx        | Tx        |
| bul     | Bulgarian              | Indo-European              | Cyrl       | low           | Sp, Tx        | Tx        |
| cat     | Catalan                | Indo-European              | Latn       | high          | Sp, Tx        | Sp, Tx    |
| ceb     | Cebuano                | Austronesian               | Latn       | zero-shot     | Sp, Tx        | Tx        |
| ces     | Czech                  | Indo-European              | Latn       | high          | Sp, Tx        | Sp, Tx    |
| ckb     | Central Kurdish        | Indo-European              | Arab       | low           | Sp, Tx        | Tx        |
| cmn     | Mandarin Chinese       | Sino-Tibetan               | Hans, Hant | high          | Sp, Tx        | Sp, Tx    |
| cym     | Welsh                  | Indo-European              | Latn       | medium        | Sp, Tx        | Sp, Tx    |
| dan     | Danish                 | Indo-European              | Latn       | medium        | Sp, Tx        | Sp, Tx    |
| deu     | German                 | Indo-European              | Latn       | high          | Sp, Tx        | Sp, Tx    |
| ell     | Greek                  | Indo-European              | Grek       | medium        | Sp, Tx        | Tx        |
| eng     | English                | Indo-European              | Latn       | high          | Sp, Tx        | Sp, Tx    |
| est     | Estonian               | Uralic                     | Latn       | medium        | Sp, Tx        | Sp, Tx    |
| eus     | Basque                 | Basque                     | Latn       | medium        | Sp, Tx        | Tx        |
| fin     | Finnish                | Uralic                     | Latn       | high          | Sp, Tx        | Sp, Tx    |
| fra     | French                 | Indo-European              | Latn       | high          | Sp, Tx        | Sp, Tx    |
| gaz     | West Central Oromo     | Afro-Asiatic               | Latn       | zero-shot     | Sp, Tx        | Tx        |
| gle     | Irish                  | Indo-European              | Latn       | low           | Sp, Tx        | Tx        |
| glg     | Galician               | Indo-European              | Latn       | low           | Sp, Tx        | Tx        |
| guj     | Gujarati               | Indo-European              | Gujr       | low           | Sp, Tx        | Tx        |
| heb     | Hebrew                 | Afro-Asiatic               | Hebr       | low           | Sp, Tx        | Tx        |
| hin     | Hindi                  | Indo-European              | Deva       | medium        | Sp, Tx        | Sp,       |
| hrv     | Croatian               |                            | Latn       | medium        | Sp, Tx        | Tx Tx     |
| hun     | Hungarian              | Indo-European Uralic       | Latn       | medium        | Sp, Tx        | Tx        |
|         | Armenian               | Indo-European              | Armn       | low           | Sp, Tx        | Tx        |
| hye     |                        |                            |            |               |               |           |
| ibo ind | Igbo                   | Atlantic-Congo             | Latn       | low medium    | Sp, Tx Sp, Tx | Tx Sp,    |
| isl     | Indonesian Icelandic   | Austronesian Indo-European | Latn Latn  | low           | Sp, Tx        | Tx Tx     |
| ita     | Italian                | Indo-European              | Latn       | high          | Sp, Tx        | Sp, Tx Tx |
| jav jpn | Javanese Japanese      | Austronesian Japonic       | Latn       | medium high   | Sp, Tx Sp, Tx | Sp, Tx    |
| kam     | Kamba                  | Atlantic-Congo             | Jpan Latn  | zero-shot     | Sp            | -         |
|         |                        |                            |            |               | Sp, Tx        | Tx        |
| kan     | Kannada                | Dravidian                  | Knda       | low           |               |           |
| kat     | Georgian               | Kartvelian                 | Geor       | low medium    | Sp, Tx        | Tx        |
| kaz kea | Kazakh Kabuverdianu    | Turkic Indo-European       | Cyrl Latn  | zero-shot     | Sp, Tx Sp     | Tx -      |
| khk     | Halh Mongolian         | Mongolic-Khitan            | Cyrl       | low           | Sp, Tx        | Tx        |
| khm     | Khmer                  | Austroasiatic              | Khmr       | low           | Sp, Tx        | Tx        |
| kir     | Kyrgyz                 | Turkic                     | Cyrl       | low           | Sp, Tx        | Tx        |
| kor     | Korean                 | Koreanic                   | Kore       | medium        | Sp, Tx        | Sp,       |
| lao     | Lao                    | Tai-Kadai                  | Laoo       | low           | Sp, Tx        | Tx Tx     |
| lit     | Lithuanian             | Indo-European              | Latn       | low           | Sp, Tx        | Tx        |
| ltz     | Luxembourgish          | Indo-European              | Latn       | zero-shot     | Sp            | -         |
| lug     | Ganda                  | Atlantic-Congo             | Latn       | medium        | Sp, Tx        | Tx        |
| luo     | Luo                    | Nilotic                    | Latn       | zero-shot     | Sp, Tx        | Tx        |
| lvs     | Standard Latvian       | Indo-European              | Latn       | low           | Sp, Tx        | Tx        |
| mai     | Maithili               | Indo-European              | Deva       | zero-shot low | Sp, Tx Sp, Tx | Tx        |
| mal     | Malayalam              | Dravidian                  | Mlym       |               | Sp, Tx        | Tx        |
| mar     | Marathi                | Indo-European              | Deva       | low           |               | Tx        |
| mkd     | Macedonian             | Indo-European              | Cyrl       | low           | Sp, Tx        | Tx        |
| mlt     | Maltese                | Afro-Asiatic               | Latn       | low           | Sp, Tx        | Sp, Tx    |
| mni     | Meitei                 | Sino-Tibetan 39            | Beng       | zero-shot     | Sp, Tx        | Tx        |
| mya     |                        | Sino-Tibetan               | Mymr       | low           | Sp,           | Tx        |
|         | Burmese                |                            |            |               | Tx            |           |

Supplementary table 3: SeamlessM4T languages. We display the language code, name, family, subgroup, and script, as well as the speech resource level and whether the language is supported as a source or a target in the speech and/or text modalities. Zero-shot here refers to S2TT or S2ST tasks with the language in question as source.

| Code   | Language name     | Family         | Script   | Resource   | Source   | Target   |
|--------|-------------------|----------------|----------|------------|----------|----------|
| nld    | Dutch             | Indo-European  | Latn     | high       | Sp, Tx   | Sp, Tx   |
| nno    | Norwegian Nynorsk | Indo-European  | Latn     | low        | Sp, Tx   | Tx       |
| nob    | Norwegian Bokmål  | Indo-European  | Latn     | low        | Sp, Tx   | Tx       |
| npi    | Nepali            | Indo-European  | Deva     | low        | Sp, Tx   | Tx       |
| nya    | Nyanja            | Atlantic-Congo | Latn     | low        | Sp, Tx   | Tx       |
| oci    | Occitan           | Indo-European  | Latn     | zero-shot  | Sp       | -        |
| ory    | Odia              | Indo-European  | Orya     | low        | Sp, Tx   | Tx       |
| pan    | Punjabi           | Indo-European  | Guru     | low        | Sp, Tx   | Tx       |
| pbt    | Southern Pashto   | Indo-European  | Arab     | medium     | Sp, Tx   | Tx       |
| pes    | Western Persian   | Indo-European  | Arab     | low        | Sp, Tx   | Sp, Tx   |
| pol    | Polish            | Indo-European  | Latn     | high       | Sp, Tx   | Sp, Tx   |
| por    | Portuguese        | Indo-European  | Latn     | medium     | Sp, Tx   | Sp, Tx   |
| ron    | Romanian          | Indo-European  | Latn     | high       | Sp, Tx   | Sp, Tx   |
| rus    | Russian           | Indo-European  | Cyrl     | medium     | Sp, Tx   | Sp, Tx   |
| slk    | Slovak            | Indo-European  | Latn     | medium     | Sp, Tx   | Sp, Tx   |
| slv    | Slovenian         | Indo-European  | Latn     | low        | Sp, Tx   | Tx       |
| sna    | Shona             | Atlantic-Congo | Latn     | zero-shot  | Sp, Tx   | Tx       |
| snd    | Sindhi            | Indo-European  | Arab     | zero-shot  | Sp, Tx   | Tx       |
| som    | Somali            | Afro-Asiatic   | Latn     | low        | Sp, Tx   | Tx       |
| spa    | Spanish           | Indo-European  | Latn     | high       | Sp, Tx   | Sp, Tx   |
| srp    | Serbian           | Indo-European  | Cyrl     | low        | Sp, Tx   | Tx       |
| swe    | Swedish           | Indo-European  | Latn     | low        | Sp, Tx   | Sp, Tx   |
| swh    | Swahili           | Atlantic-Congo | Latn     | medium     | Sp, Tx   | Sp, Tx   |
| tam    | Tamil             | Dravidian      | Taml     | medium     | Sp, Tx   | Tx       |
| tel    | Telugu            | Dravidian      | Telu     | medium     | Sp, Tx   | Sp, Tx   |
| tgk    | Tajik             | Indo-European  | Cyrl     | low        | Sp, Tx   | Tx       |
| tgl    | Tagalog           | Austronesian   | Latn     | medium     | Sp, Tx   | Sp, Tx   |
| tha    | Thai              | Tai-Kadai      | Thai     | medium     | Sp, Tx   | Sp, Tx   |
| tur    | Turkish           | Turkic         | Latn     | medium     | Sp, Tx   | Sp, Tx   |
| ukr    | Ukrainian         | Indo-European  | Cyrl     | medium     | Sp, Tx   | Sp, Tx   |
| urd    | Urdu              | Indo-European  | Arab     | medium     | Sp, Tx   | Sp, Tx   |
| uzn    | Northern Uzbek    | Turkic         | Latn     | medium     | Sp, Tx   | Sp, Tx   |
| vie    | Vietnamese        | Austroasiatic  | Latn     | medium     | Sp, Tx   | Sp, Tx   |
| xho    | Xhosa             | Atlantic-Congo | Latn     | zero-shot  | Sp       | -        |
| yor    | Yoruba            | Atlantic-Congo | Latn     | low        | Sp, Tx   | Tx       |
| yue    | Cantonese         | Sino-Tibetan   | Hant     | low        | Sp, Tx   | Tx       |
| zlm    | Colloquial Malay  | Austronesian   | Latn     | low        | Sp       | -        |
| zsm    | Standard Malay    | Austronesian   | Latn     | low        | Tx       | Tx       |
| zul    | Zulu              | Atlantic-Congo | Latn     | low        | Sp, Tx   | Tx       |

## Supplementary Information III SeamlessAlign: Automatically Creating Aligned Data for Speech

Developing an effective multilingual and multimodal translation system like SeamlessM4T requires sizable resources across many languages and modalities. Some human-labeled resources for translation are freely available, albeit often limited to a small set of languages or in very specific domains. Well-known examples are parallel text collections such as Europarl [45] and the United Nations Corpus [46]. A few human-created collections also involve the speech modality, like CoVoST [47, 48] and mTEDx [49]. Yet no open dataset currently matches the size of those used in initiatives like Whisper [20] or USM [50], which proved to unlock unprecedented performance.

Parallel data mining emerges as an alternative to using closed data, both in terms of language coverage and corpus size. The dominant approach today is to encode sentences from various languages and modalities into a joint fixed-size embedding space and to find parallel instances based on a similarity metric. Mining is then performed by pairwise comparison over massive monolingual corpora, where sentences with similarity above a certain threshold are considered mutual translations [51, 52]. This approach was first introduced using the multilingual Laser space [53]. Teacher-student training was then used to scale this approach to 200 languages [6, 16] and subsequently, the speech modality [54, 55].

In this section, we describe how we employed parallel data mining to create SeamlessAlign: the largest open dataset for multimodal translation to date, totaling 470,000 hours. The overall workflow is summarized in Extended data figure 1, and builds on the approach deployed in SpeechMatrix [55]. Starting with a large collection of raw audio, we chunked files into overlapping segments and applied speech Language Identification (LID). On the text side, we used the same sentence-segmented dataset drawn from NLLB [6]. Speech and text corpora were then projected into a common embedding space, in which mining was performed to identify translation pairs with optimal segmentation.

Several improvements over the original SpeechMatrix pipeline are introduced:

- an improved and extended speech language identification (LID) model,
- a novel multimodal embedding space,
- increased coverage from 17 to 37 languages,
- increased raw audio amount, totaling 4 million hours.

In the current version, mining was focused on 37 target languages of the SeamlessM4T system. Scaling to all 100 languages will be explored in future iterations of our work.

## Supplementary Information III.1 Speech-language identification

Language identification (LID) of raw audio data is a critical component of our workflow. Incorrectly labeling speech at this stage can prevent high-quality audio segments from being aligned or, worse, add noise to the resulting paired sets. This can adversely affect the performance of the downstream translation system.

While numerous off-the-shelf LID models exist, none could cover our target list of 100 languages. 2 Therefore, we trained our own model, following the ECAPA-TDNN architecture introduced in [13], for which an open-source model trained on VoxLingua107 [14] is available. The new model adds support for several new languages, including Moroccan Arabic, Egyptian Arabic, Central Kurdish, West Central Oromo, Irish, Igbo, Kyrgyz, Ganda, Maithili, Meitei, Nyanja, Odia, Cantonese, and Zulu.

## Supplementary Information III.1.1 Training

## Baseline

We first retrained a system from scratch on VoxLingua107 data to reproduce a baseline. This system, dubbed VL107 baseline, achieved a classification error rate of 5.25% on the development set of VoxLingua107 at epoch 30. Comparatively, the open-sourced model available on HuggingFace, 3 referred to as VL107 HF, yields an error rate of 7%.

## Experimental setup

With our training pipeline validated, we finally trained our own model for 40 epochs. This required about 172 hours on 8 GPUs. A total of 17k hours of speech were used, with an average of 171 hours per language, ranging from 1 to 600 hours. The test corpus covers our 100 languages of interest and is composed of the FLEURS test set, the VoxLingua107 development set, and extra test data extracted from VAANI, 4 IIITH [108] and KENCORPUS 5 [109].

|                | Overall - ↑F1-micro (n=100)   | Overall - ↑F1-macro (n=100)   | Intersection - ↑F1-micro (n=79)   | Intersection - ↑F1-macro (n=79)   |
|----------------|-------------------------------|-------------------------------|-----------------------------------|-----------------------------------|
| VL107 HF       | 82.3%                         | -                             | 94.1%                             | 92.6%                             |
| VL107 baseline | 82.5%                         | -                             | 94.4%                             | 93.0%                             |
| LID100         | 86.0%                         | 81.9%                         | 92.9%                             | 91.1%                             |

Supplementary table 4: F1 micro and macro average for the considered LID systems over all SeamlessM4T languages and the intersection of supported languages across models. Dashes are used for models that do not support the full 100 scope.

2 MMS [23] has recently been released and covers them all, but it was not available when this project started

[3 https://huggingface.co/TalTechNLP/voxlingua107-epaca-tdnn](https://huggingface.co/TalTechNLP/voxlingua107-epaca-tdnn)

[4 http://vaani.iisc.ac.in](http://vaani.iisc.ac.in/)

[5 https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/6N5V1K](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/6N5V1K)

## Results

The F1 scores on the test data for all models are presented in Table 4. The results are given for the 100 SeamlessM4T languages, and the 79 languages in common with VoxLingua107. We can see that training on the additional languages slightly decreases the overall performance for the common set of languages, which is a direct consequence of the presence of a higher number of close languages. For example, Zulu (zul) is very often confused with Nyanja (nya), Igbo (ibo) with Yoruba (yor), and Modern Standard Arabic (arb) with Moroccan Arabic (ary) and Egyptian Arabic (arz). Our model improves classification (F1 difference greater than 5%) on 17 languages with an average gain of 14.6%, not counting the newly covered languages, while decreasing classification for 12 (with an average loss of 9.8%).

## Supplementary Information III.1.2 Filtering

While it is important to retrieve the maximum amount of data for mining, we must also ensure high quality in LID labeling. Depending on the quantity of data available for a particular language, it may be useful to filter it to retain higher-quality data. We thus estimated the Gaussian distribution of the LID scores per language for correct and incorrect classifications on the development corpus. We selected a threshold per language such that p(correct|score) &gt; p(incorrect|score). By rejecting 8% of the data, we were able to further increase the F1 measure by almost 3%.

|            | ↑F1 micro   | ↑Coverage   |
|------------|-------------|-------------|
| LID100     | 86.0%       | 100%        |
| +filtering | 89.5%       | 92.1%       |

Supplementary table 5: F1 micro average and coverage across 100 languages for the LID100 system with and without filtering.

## Supplementary Information III.2 Gathering raw audio and text data at scale

## Text pre-processing

On the text side, we rely entirely on the same dataset deployed in NLLB [6]. The same data sources, cleaning, and filtering steps are used and run at scale with our Stopes library.

## Audio pre-processing

We start with 4 million hours of raw audio originating from a publicly available repository of crawled web data. Table 8 provides statistics on the amount of raw audio for each language. Approximately 1 million hours in this collection are in English. We then applied a series of pre-processing steps to curate and improve the overall speech quality. Firstly, we deduplicated the audio file URLs found in the repository, downloaded the audio files, and resampled at 16KHz. Subsequently, we filtered out the non-speech data with a bespoke audio event detection (AED) model.

## Audio segmentation

To perform S2TT or S2ST mining, it is desirable to split audio files into smaller chunks that map as closely as possible to self-contained sentences, equivalent to sentences in a text corpus. However, genuine semantic segmentation in speech is an open-ended problem-pauses can be an integral part of a message and can naturally occur differently across languages. For mining purposes, it is impossible to prejudge what specific segments can maximize the overall quality of the mined pairs.

We thus followed the over-segmentation approach drawn from [54] (as depicted in Extended data figure 1).

First, we used an open Voice Activity Detection (VAD) model [56] to split audio files into shorter segments. Subsequently, our speech LID model was used on each file. Finally, we created several possible overlapping splits of each segment and left the choice of the optimal split to the mining algorithm described in the next section. This over-segmentation strategy roughly octuples the number of potential segments considered.

## Supplementary Information III.3 Speech mining

The overall workflow of our mining process is shown in Supplementary figure 2.

️

<!-- image -->

️

Supplementary figure 1: SONAR architecture.

️

️

️

Supplementary figure 2: Workflow of the Sonar encoding and mining processes.

<!-- image -->

Supplementary figure 3: Overview of SeamlessM4T. (1) shows the pre-trained models used when fine-tuning multitasking UnitY. (2) outlines multitasking UnitY with its two encoders, text decoder, T2U encoder-decoder, and the supporting vocoders for synthesizing output speech in S2ST.

<!-- image -->

First, we trained encoders for text (Supplementary Information III.3.1) and speech (Supplementary Information III.3.2). These are then used to project both modalities into a joint embedding space. We then mined speech segments against text sentences or speech segments in other languages to create large amounts of S2TT and S2ST pairs. These corpora are subsequently combined with other resources to train the SeamlessM4T model.

| Model                  |   ↑spBLEU - X-eng (n=200) |   ↑spBLEU - eng-X (n=200) |   ↑COMET - X-eng (n=89) |   ↑COMET - eng-X (n=89) |
|------------------------|---------------------------|---------------------------|-------------------------|-------------------------|
| Sonar                  |                      32.7 |                      21.6 |                    85.9 |                    84.2 |
| NLLB-1.3B (MT topline) |                      35.2 |                      24.9 |                    86.5 |                    85.2 |

Supplementary table 6: Average performance on Flores devtest set over the 200 NLLB languages and 89 languages supported by COMET: translation spBLEU and COMET scores, auto-encoding spBLEU.

## Supplementary Information III.3.1 Sonar text embedding space

## Architecture and training setup

We use a novel sentence embedding space developed by Duquenne et al. [8], named Sentence-level multimOdal and laNguage-Agnostic Representations-in short, Sonar. Sonar substantially outperforms the previous Laser space. It follows the same two-step approach: we first trained a text embedding space and then relied on a teacher-student training strategy to extend it to the speech modality. Similarly to Laser, the initial text Sonar space uses an encoder-decoder architecture, but is based on the NLLB-1.3B model, capable of translating across 200 languages [6]. The intermediate representation was replaced with a fixed-size vector using mean-pooling (i.e., the decoder thus attends to a single vector). This architecture is fine-tuned using all of NLLB's T2TT training data, and several training objectives were explored. A detailed ablation study can be found in Duquenne et al. [8]. This yields a powerful, massively multilingual sentence representation that can be decoded into all 200 languages of the NLLB project. Figure 1 provides an illustration of the Sonar architecture and Table 6 summarizes the translation evaluation of the Sonar framework.

## Evaluation for mining

On pure translation performance, we observe that the fixed-size representation bottleneck leads to a 7% and 13% decrease in BLEU score when translating into English (35.2→32.7) and out of English, respectively (24.9→21.6). This is a rather interesting result, given that the use of attention is commonly considered mandatory to achieve reasonable performance.

On mining performance, we rely on the multilingual similarity search xsim metric, which measures the percentage of sentences in the Flores dataset which are not correctly aligned when searching for the closest vector in the embedding space. The improved version xsim++ [15] added challenging English sentences on the target side. Both of these metrics are a good proxy to the actual T2TT mining task while being much faster to compute.

As summarized in Table 7, Sonar substantially outperforms other popular multilingual sentence representations like Laser3 [16] or LaBSE [17].

|        |   Overall - ↓xsim (n=200) |   Overall - ↓xsim++ (n=200) |   Intersection - ↓xsim (n=98) |   Intersection - ↓xsim++ (n=98) |
|--------|---------------------------|-----------------------------|-------------------------------|---------------------------------|
| Sonar  |                       1.4 |                        15.2 |                           0.1 |                             9.3 |
| Laser3 |                       5.1 |                        36.4 |                           1.1 |                            27.5 |
| LaBSE  |                      10.7 |                        36.1 |                           1.5 |                            15.4 |

Supplementary table 7: Comparison of similarity search results (error rates) on all 200 Flores languages, and limited to the intersection of 98 languages on which each model has been trained on.

## Supplementary Information III.3.2 Training speech encoders

## Architecture and training setup

As a second step and following [54], the new Sonar text embedding space is extended to the speech modality through teacher-student training. In that work, a fixed-size speech representation was obtained by taking the BOS output of a pretrained XLS-R model [61]. This model was then fine-tuned to maximize the cosine loss between this pooled speech representation and sentence embeddings in the same languages (ASR transcriptions) or in English (speech translations). We improved this initial recipe by doing the following:

- MSE loss instead of a cosine loss was used. This enables us to use the Sonar text decoder on speech input,
- w2v-BERT 2.0 speech front-end instead of XLS-R. w2v-BERT 2.0 was optimized on 143 languages (see Appendix Supplementary Information IV.3 for details),
- Attention-pooling. Instead of the usual pooling methods (i.e., mean or maxpooling), we implemented a 3-layer sequence-to-sequence model to convert the variable length sequence of w2v-BERT 2.0 to a fixed size vector,
- Training on human-performed ASR transcriptions only. We collected at least 100 hours of ASR transcriptions for most of the languages (see Table 8 column "train") and trained the speech encoders exclusively on them,
- Following [6, 16], we grouped languages by linguistic families (i.e., Germanic or Indian languages) and trained them together in one speech encoder. Alternative language groupings, which might consider the acoustic characteristics of each language, are left open for future research.

## Evaluation of speech encoders

The trained speech encoders are to be used in S2TT and S2ST mining, and the resulting paired data is to be fed into the SeamlessM4T system (see section Supplementary Information IV). Consequently, an ideal evaluation would consist of testing various iterations of each speech encoder by using them in an end-to-end loop: performing mining, then training a S2TT or S2ST translation system on the mined data, and potentially comparing different thresholds of the Sonar score. Unfortunately, this is a very compute-intensive recipe.

Supplementary table 8: Statistics on speech encoders and amount of mined data. Sen2Txx, Sxx2Ten, and SxxSen correspond to English speech paired with foreign text, foreign speech paired with English Text, and foreign Speech paired with English speech, respectively. Dashes are unmined directions. We provide the amount of raw audio data for mining and the amount of human-provided ASR transcripts to train the speech encoders. The speech encoders are evaluated for S2TT using BLEU on the Fleurs test set. Our model performs zero-shot S2TT. Finally, the last three columns provide the amount of mined data.

| ISO       |   Raw - audio [h] |   Train - ASR [h] |   X-eng (↑BLEU) - Ours |   X-eng (↑BLEU) - Whisper | Mined audio [h] - Sen2Txx   |   Mined audio [h] - Sxx2Ten |   Mined audio [h] - Sxx2Sen |
|-----------|-------------------|-------------------|------------------------|---------------------------|-----------------------------|-----------------------------|-----------------------------|
| arb       |            106755 |               822 |                   28.7 |                      25.5 | 1568                        |                        8072 |                         776 |
| ben       |              7012 |               335 |                   18.9 |                      13.2 | 606                         |                        1345 |                         263 |
| cat       |             43531 |              1738 |                   35.1 |                      34.2 | 1570                        |                        4411 |                         354 |
| ces       |             41318 |               181 |                   29.2 |                      27.8 | 1454                        |                        6905 |                         602 |
| cmn       |             79772 |              9320 |                   16.2 |                      18.4 | 5440                        |                       18760 |                        1570 |
| cym       |             24161 |                99 |                   14.5 |                      13.0 | -                           |                        4411 |                         278 |
| dan       |             34300 |               115 |                   31.9 |                      32.7 | 2499                        |                        6041 |                         583 |
| deu       |            490604 |              3329 |                   32.7 |                      34.6 | 91715                       |                       17634 |                        1921 |
| est       |             12691 |               131 |                   23.8 |                      18.7 | 1022                        |                        3346 |                         607 |
| fin       |             32858 |               184 |                   22.2 |                      22.1 | 651                         |                        6086 |                         526 |
| fra       |            282179 |              2057 |                   31.2 |                      32.2 | 21523                       |                       17380 |                        3337 |
| hin       |             15118 |               150 |                   19.2 |                      22.0 | 1041                        |                        2977 |                         530 |
| ind       |             11559 |               269 |                   26.5 |                      29.1 | 1938                        |                        2658 |                         510 |
| ita       |             79480 |               588 |                   25.3 |                      23.6 | 4378                        |                        6508 |                         817 |
| jpn       |             75863 |             17319 |                   17.4 |                      18.9 | 1973                        |                       21287 |                        1141 |
| kan       |              1451 |               114 |                   20.0 |                      11.6 | -                           |                         232 |                         198 |
| kor       |             37854 |               316 |                   15.0 |                      21.3 | -                           |                        8657 |                         640 |
| mlt       |              2122 |               106 |                   23.2 |                      13.5 | 131                         |                         130 |                          60 |
| nld       |             93933 |              1723 |                   25.5 |                      24.0 | 3720                        |                        6859 |                        1210 |
| pes       |             43788 |               386 |                   22.2 |                      19.6 | -                           |                        7122 |                         693 |
| pol       |             53662 |               304 |                   21.1 |                      22.3 | 1324                        |                        9389 |                         757 |
| por       |            141931 |               269 |                   35.4 |                      38.1 | 4853                        |                        8696 |                         928 |
| ron       |             18719 |               135 |                   32.1 |                      31.5 | 2770                        |                        2878 |                         716 |
| rus       |            103906 |               259 |                   25.4 |                      27.8 | 11296                       |                       13509 |                        1252 |
| slk       |             16954 |               102 |                   29.5 |                      26.1 | 1267                        |                        3785 |                         491 |
| spa       |            324086 |              1511 |                   24.3 |                      23.3 | 27778                       |                       17388 |                        2727 |
| swe       |            125195 |               144 |                   33.4 |                     37.02 | 3438                        |                        2620 |                         484 |
| swh       |             18393 |               361 |                   22.6 |                       7.2 | 690                         |                        2620 |                         484 |
| tam       |            100331 |               245 |                   14.3 |                       9.2 | -                           |                        1664 |                         867 |
| tel       |              3303 |                84 |                   15.8 |                      12.5 | -                           |                         985 |                         536 |
| tgl       |              4497 |               108 |                   13.3 |                      24.4 | -                           |                         633 |                         266 |
| tha       |             13421 |               195 |                   15.3 |                      16.1 | 2577                        |                        3563 |                         542 |
| tur       |             23275 |               174 |                   21.0 |                      26.6 | 1417                        |                        6545 |                         426 |
| ukr       |              6396 |               105 |                   27.9 |                      29.4 | 1220                        |                        1717 |                         392 |
| urd       |             16882 |               185 |                   17.6 |                      17.2 | 773                         |                        3416 |                         652 |
| uzn       |              8105 |               115 |                   17.9 |                       6.0 | 475                         |                        1846 |                         157 |
| vie       |             34336 |               194 |                   17.8 |                      20.4 | 1689                        |                        7692 |                         868 |
| Total/avr |           2529741 |             43772 |                   23.3 |                      22.5 | 202796                      |                      239767 |                       29161 |

Instead, given that the Sonar embedding space comes with a text decoder, we chose to evaluate the individual speech encoders on a S2TT task. That is, following [110, 111], we decoded foreign speech embeddings into English texts. Results are summarized in Table 8, column "X-eng BLEU". For comparison, we also provide the performance of Whisper-Large-v2 [20]. It is important to emphasize that the Sonar speech encoders were trained on ASR transcriptions only and the Sonar text decoder has never been exposed to any speech input. Therefore, the reported results correspond to fully zero-shot speech translation.

Despite the zero-shot scenario, the Sonar speech encoders compare favorably to a model like Whisper-Large-v2, which was trained on a massive amount of translated audio. Gaps in BLEU points can be observed in some high resource languages such as German, Russian or Portuguese, However, zero-shot speech translation with our speech encoders outperforms Whisper-Large-v2 on several low-resource languages - particularly for Swahili and several South Asian languages like Bengali, Kannada, Telugu, and Tamil.

## Supplementary Information III.3.3 Speech mining

## Margin setting

Mining was performed using a margin criterion with our Stopes data processing library 6 [68]. The overall processing is identical to that developed for T2TT mining in NLLB [6]. We performed so-called global mining, where all speech segments in one language are compared to all speech segments in another language. Local mining, on the contrary, would try to leverage knowledge on longer speech chunks that are likely to contain many parallel segments. A typical example would be documentation on an international event in multiple languages. Such high-level information is very difficult to obtain at scale.

First, the embeddings for all speech segments and text sentences are calculated. These are then indexed with the FAISS library [112], enabling efficient large-scale similarity search on GPUs. Finally, nearest neighbors to all elements in both directions are retrieved, and margin scores are computed following the formula introduced in [52]:

<!-- formula-not-decoded -->

where x and y are the source and target sentences, and NNk(x) denotes the k nearest neighbors of x in the other language. We set k to 16.

In past work, a threshold of 1.06 on the margin score was used for bitext mining based on Laser embeddings [6, 113]. The Sonar space, however, displayed different dynamics and the optimal threshold was adapted accordingly. Since full end-to-end evaluation with S2TT or S2ST training is too compute-intensive, we set the new threshold at 1.15 after some human inspection. The statistics reported in Table 8 are based on this threshold.

[6 https://github.com/facebookresearch/stopes](https://github.com/facebookresearch/stopes)

## Mined dataset

We performed mining of speech in foreign languages against English texts (column Sxx2Ten in Table 8) and English speech (column Sxx2Sen in Table 8). Given the sheer size of our raw English speech (1 million hours) and foreign text collections (often more than 1 billion sentences), we carried out this operation only for some languages (column Sen2Txx in Table 8). Other directions are left for future work.

Except for Maltese, for which we had access only to a small amount of raw audio, we were able to mine more than 100 hours of speech alignments with English speech for all languages. The alignments with English texts reached a thousand hours for most languages and exceeded ten thousand hours for six (i.e., German, French, Spanish, Japanese, Russian, and Mandarin Chinese). Overall, SeamlessAlign covers 37 languages and a total of 470,000 hours:

- English speech to non-English text (Sen2Txx)-approximately 200,000 hours
- Non-English speech to English text (Sxx2Ten)-approximately 240,000 hours
- Non-English speech to English speech (Sxx2Sen)-approximately 29,000 hours

Adding such huge amounts of data to train a massively multilingual S2ST translation system represents a substantial computational challenge. As described in Section Supplementary Information IV, not all of this data was used for modeling, but only a subset with the highest Sonar alignment scores. Since our mined data can help support many different use cases, we are open-sourcing the meta-data for the full amount 7 (i.e., up to a Sonar threshold of 1.15), to allow the community to rebuild SeamlessAlign and use it for their own purposes. The optimal threshold can thus be tuned based on the task, balancing dataset size and alignment quality. Our mining code is also open-sourced in the Stopes library.

## Supplementary Information III.4 Related work Supplementary Information III.4.1 Speech LID

Spoken language identification has been traditionally approached in a two-stage workflow: a classifier is trained on top of conventional representations like the i-vector or x-vector, extracted from the raw audio signal [114, 115]. The same idea has been revisited in end-to-end, integrated neural architectures [116-118]. These approaches typically fall short as the input audio goes shorter, which can be an issue with speech recordings involving multiple speakers talking to each other in turn. New methods were developed to tackle this very problem. Lopez-Moreno et al. [119] show that a simple feed-forward network can outperform i-vectors on this task. More complex architectures such as convolutional neural networks or Bi-LSTMs prove to be more efficient in capturing information from the speech input [120, 121]. Some other approaches try to bridge the gap with models focused on longer segments through teacher-student training [122, 123].

[7 available at https://github.com/facebookresearch/seamless\_communication](https://github.com/facebookresearch/seamless_communication)

Recent initiatives aimed at increasing language coverage to go beyond a handful of conventionally very high-resource languages. The ECAPA-TDNN architecture introduced in [13] has proven effective to distinguish between the 107 languages of Voxlingua107 [14]. The XLS-R pretrained model [61] is also fine-tuned on a language identification task using the same dataset. Whisper-Large-v2 is another popular model that can perform this task for 99 languages [20]. Very recently, the MMS project further broadened language support to 4,000 spoken languages [23].

## Supplementary Information III.4.2 Speech segmentation

To achieve sentence-like speech segments, a commonly employed method is pausebased segmentation using Voice Activity Detection (VAD). This approach is widely utilized in various applications, including speech mining, ASR, and speech translation. In this work, we adopted the over-segmentation strategy proposed by Duquenne et al. [54] on top of the segments obtained through VAD segmentation. While this oversegmentation significantly improves the recall of the mining process, it does come with certain drawbacks. Specifically, it leads to a substantial increase (8x) in the number of segments, introducing noise in the embedding space, and raising the computational demand for the mining process. Pause-based segments may not align with semantically coherent sentences; in fact, they tend to be too short because speaker pauses can extend beyond sentence boundaries. Consequently, for speech translation, researchers have put forward more sophisticated segmentation strategies with the potential to deliver higher-quality speech translation results. Gállego et al. [124] used a pretrained wav2vec 2.0 instead of VAD to detect speech segments. Potapczyk &amp; Przybysz [125] proposed a divide-and-conquer (DAC) algorithm that iteratively operates on top of VAD longest detected pauses until all segments become below a max-segment length parameter. Gaido et al. [126] further builds upon this through a hybrid approach. SHAS [127] train a classifier on top of wav2vec 2.0 using optimal segmentation from a manually segmented corpus. Similar to Potapczyk &amp; Przybysz [125], it then applies a DAC algorithm on the splitting probabilities of the network to obtain final segmentation decisions. This approach demonstrated significant gains over simple pause-based segmentation and other baselines in speech-to-text translation tasks. These segmentation methods could be promising for speech mining, suggesting exciting avenues for future research.

## Supplementary Information III.4.3 Multilingual and multimodal representations

Several works have studied how to learn multilingual sentence representations. Well known approaches are Laser [53], LaBSE [17], or [128, 129]. While Laser was trained with an MT translation objective, a decoder compatible with the Laser embedding space is not freely available. To the best of our knowledge, Sonar is the first sentence embedding space for which an efficient and multilingual decoder is available. Another direction of research is to first train an English sentence representation (e.g., sentenceBERT [130]) and in a second step, extend it to more languages using teacher-student training [131]. The same approach was used to extend Laser to 200 languages, named Laser3 [16].

Learning unsupervised representations of speech is the focus of several works, whether involving monolingual [132] or multilingual speech [61, 63, 102]. Examples of joint text and speech pre-trained models are mSLAM [133] and Mu2SLAM [134]. Duquenne et al. [54] were the first to introduce fixed-size text and speech representations that can be used to perform multimodal mining, followed by [57]

## Supplementary Information III.4.4 Speech mining

The proof of concept of a joint text/speech representation that can be used to perform text/speech or speech/speech mining was presented by Duquenne et al. [54]. In followup work, this approach was used to align speech in 17 languages in the VoxPopuli corpus to give rise to the SpeechMatrix corpus [55]. The authors mined for parallel speech segments in all 136 possible combinations of languages, yielding a total of 418 thousand hours of speech-to-speech alignments, out of which about 46 thousand hours are aligned with English. SpeechMatrix is a large corpus, but the domain is rather limited since the raw audio of the VoxPopuli corpus is derived from European Parliament speeches. The corpus SpeechMatrix is freely available. Khurana et al. [57] use a joint text/speech embedding space, dubbed Samu-Xlsr, to evaluate the recall of text and speech retrieval in the corpora CoVoST 2, MUST-C, and MTEDx.

There are several works that indirectly create speech-to-speech corpora. One direction of research is to perform speech synthesis on corpora aligned at the text level, (e.g., the CVSS corpus [105] which is based on the CoVoST 2 speech-to-text translation corpus).

| Model                |   CoVoST 2 (↑BLEU) - X-eng (n=21) | CoVoST 2 (↑BLEU) - eng-X (n=15)   |
|----------------------|-----------------------------------|-----------------------------------|
| Whisper-Large-v2     |                              29.1 | x                                 |
| AudioPaLM-2-8B-AST   |                              37.8 | x                                 |
| SeamlessM4T-Medium   |                              29.8 | 26.6                              |
| SeamlessM4T-Large    |                              34.1 | 30.6                              |
| SeamlessM4T-Large v2 |                              36.6 | 31.7                              |

|                      | ASR (↓WER) - Fleurs-77 (n=77)   | ASR (↓WER) - Fleurs-60 (n=60)   |   ASR (↓WER) - Fleurs-54 (n=54) |   ASR (↓WER) - Fleurs-41 (n=41) |
|----------------------|---------------------------------|---------------------------------|---------------------------------|---------------------------------|
| Whisper-Large-v2     | 41.7                            | 24.0                            |                            43.7 |                            25.0 |
| Whisper-Large-v3     | 34.9                            | 17.2                            |                            35.6 |                            17.0 |
| MMS-L61-noLM-LSAH    | -                               | -                               |                            31.0 |                            29.0 |
| MMS-L1107-CCLM-LSAH  | -                               | -                               |                            18.6 |                            16.5 |
| SeamlessM4T-Medium   | 21.9                            | 16.4                            |                            22.0 |                            16.4 |
| SeamlessM4T-Large    | 22.6                            | 16.6                            |                            23.2 |                            16.9 |
| SeamlessM4T-Large v2 | 18.5                            | 12.8                            |                            19.1 |                            13.1 |

Supplementary table 9: Multitasking X2T results. Performance of SeamlessM4TLarge on CoVoST 2 S2TT and Fleurs ASR compared to SOTA direct translation models. For Fleurs ASR, we report the average normalized WER over languages supported by both SeamlessM4T and Whisper Large (WL) (Fleurs-77). For MMS, we report the results of the MMS-L1107-CCLM-LSAH model (CTC-based with an n-gram language model for each language) on Fleurs-54. For a direct comparison with Whisper-Large-v3, we average over whisper's reported WER scores on Fleurs-60. To compare all ASR models on a common benchmark, we included averages over Fleurs-41.

## Supplementary Information IV Modeling

## Supplementary Information IV.1 Additional results

## Evaluation with spBLEU and Blaser 2.0.

To avoid expanding the set of special case languages evaluated with character-level tokenization, we evaluated with spBLEU using the Flores-200 sentence piece tokenizer. Supplementary table 10 reports spBLEU scores on Fleurs S2TT X-eng and eng-X. We also report in the same table the average Blaser 2.0 scores. Since Blaser Supplementary table 10: S2TT results with spBLEU and Blaser 2.0 we report here the performance of Whisper-Large-v2 and SeamlessM4T-Large measured with spBLEU &amp; Blaser 2.0. Note that unlike BLEU scores copied from [20], the spBLEU and Blaser 2.0 scores are based on our evaluation using https: //github.com/openai/whisper with the recommended decoding options.

| Model              | size   |   Fleurs X-eng(n=81) - ↑BLEU |   Fleurs X-eng(n=81) - ↑spBLEU |   Fleurs X-eng(n=81) - ↑Blaser 2.0 | Fleurs eng-X(n=88) - ↑BLEU   | Fleurs eng-X(n=88) - ↑spBLEU   | Fleurs eng-X(n=88) - ↑Blaser 2.0   |
|--------------------|--------|------------------------------|--------------------------------|------------------------------------|------------------------------|--------------------------------|------------------------------------|
| Whisper-Large-v2   | 1.5B   |                         17.9 |                           19.9 |                               3.29 | x                            | x                              | x                                  |
| SeamlessM4T-Medium | 1.2B   |                         20.9 |                           23.1 |                               3.56 | 19.2                         | 26.0                           | 3.68                               |
| SeamlessM4T-Large  | 2.3B   |                         24.0 |                           26.4 |                               3.66 | 21.5                         | 28.9                           | 3.71                               |

| Model              |   S2ST (↑ASR-BLEU) - Fleurs X-eng (n=101) |   S2ST (↑ASR-BLEU) - Fleurs X-eng (n=82) |   S2ST (↑ASR-BLEU) - Fleurs eng-X (n=35) |   S2ST (↑ASR-BLEU) - Fleurs eng-X (n=32) |   S2ST (↑Blaser - Fleurs X-eng (n=82) |   S2ST (↑Blaser - Fleurs eng-X (n=35) |   2.0) - Fleurs eng-X (n=32) |
|--------------------|-------------------------------------------|------------------------------------------|------------------------------------------|------------------------------------------|---------------------------------------|---------------------------------------|------------------------------|
| SeamlessM4T-Medium |                                      17.9 |                                     20.8 |                                     14.3 |                                     15.4 |                                  3.62 |                                  3.63 |                         3.63 |
| SeamlessM4T-Large  |                                      22.7 |                                     26.3 |                                     19.8 |                                     21.5 |                                  3.85 |                                  3.94 |                         3.95 |

Supplementary table 11: S2ST results with ASR-BLEU and Blaser 2.0 we report here the performance of SeamlessM4T-Large and SeamlessM4T-Medium measured with ASR-BLEU &amp; Blaser 2.0.

2.0 is modality-agnostic, we can also score the task of S2ST with Blaser 2.0. Supplementary table 11 provides the average Blaser 2.0 scores of SeamlessM4T-Large and SeamlessM4T-Medium on S2ST X-eng and eng-X directions. Since Blaser 2.0 supports 83 languages (including English), we average over 82 X-eng directions. For eng-X, we show averages of 35 languages, then averages excluding 3 languages with a WER exceeding 100%. Since Blaser 2.0 supports all 35 target languages the scores are more reliable and less affected by the noisiness of the ASR model underlying ASR-BLEU (a difference of -1.7ASR-BLEU points with the addition of 3 directions). The full results and metrics per evaluation direction can be found at https://github.com/facebookresearch/seamless \_ communication.

## Evaluation of X-X directions with spBLEU.

Since SeamlessM4T models support multiple languages on both the source and target sides, we can evaluate non-English centric directions (labeled X-X) in a zero-shot manner.

Supplementary figure 4: S2TT Fleurs X-X results. We evaluate X-X directions from Fleurs and average spBLEU scores. For a given target text language, we average scores over 100 source languages.

<!-- image -->

Supplementary figure 5: Statistics of ASR and X-eng S2TT data used to train our SeamlessM4T model. We show the data size in hours of speech (log-scale) between ASR, S2TT primary and mined. Languages are sorted in ascending resource-level. For numerical statistics see Supplementary table 12

<!-- image -->

## Supplementary Information IV.2 Preparing training data

## Processing human-labeled data

When using human-labeled data, we removed special tokens such as &lt;silence&gt; and &lt;no-speech&gt; from the verbatim transcriptions. We additionally perform length filtering to remove examples exceeding a maximum text length of 100 sub-word tokens (based on the text tokenizer described below) and pairs with a skewed text-to-audio length ratio that exceeds 5 sub-words per second. Doing so improves the batching efficiency when training and eliminates pairs that are likely to be noisy or misaligned.

## Filtering

We perform additional filtering on the combined pool of primary and mined data. Following [6], we implemented a toxicity filter. This removes pairs that have toxicity imbalance, (i.e., when the difference in the number of toxic items detected in the source and target is above a certain threshold). For S2TT data, transcriptions are used as a proxy for the speech input when counting toxic items. We set the imbalance threshold at 1. In addition, we also applied a length filter. We removed pairs in which the utterance is shorter than 0.1 seconds or longer than 50 seconds. We also removed pairs in which the text is longer than 250 sub-words (based on the tokenizer described below). Lastly, we removed pairs in which the text contains more than 20% of emojis, more than 50% of punctuations, or more than 50% of spaces.

Supplementary figure 6: Statistics of S2ST data used in Stage3 of training SeamlessM4T model. We show the data size in hours of speech between primary and mined. Languages are sorted in ascending resource-level. For numerical statistics see Supplementary table 13

<!-- image -->

Supplementary figure 5 shows the distribution of filtered X-eng S2TT data used to train SeamlessM4T models. Based on the total amount of speech audio hours in each language, we assessed its resource level: high-resource are languages with more than 1000 hours of supervision, mid-resource are those between 500 and 1000 hours, and low-resource are those with less than 500 hours.

## Processing S2ST data from SeamlessAlign

We added up to 2,500 hours of mined speech-to-speech data from SeamlessAlign per language direction depending on its availability. We used the XLSR-based unit extraction pipeline for extracting discrete acoustic units for target speech from the mined data. An in-house ASR model is then deployed to generate text transcriptions for the first pass decoder based on the target speech.

Supplementary figure 6 shows the distribution of all S2ST data used to train SeamlessM4T models between the primary and mined data.

| language code   | ASR             | S2TT X-eng Resource   | S2TT X-eng Resource   | S2TT    | eng-X   | eng-X   | language code   |         | S2TT X-eng   | S2TT X-eng   | Resource S2TT   |         |
|-----------------|-----------------|-----------------------|-----------------------|---------|---------|---------|-----------------|---------|--------------|--------------|-----------------|---------|
| language code   | ASR             | P M                   |                       | S2TT    | P M     |         | language code   | ASR     | P M          |              | P               | eng-X M |
| Total           | 40,012          | 50,596 12,682         |                       | 17,6827 | 5,701   |         |                 |         |              |              |                 |         |
| afr             | 106             | 101                   | low                   | 2069    |         | lit     | 40              | 283     |              | low          | 1920            |         |
| amh             | 54              | 49                    | low                   | 1921    |         | ltz     | 0               | 0       |              | zero-shot    | 0               |         |
| arb             | 934             | 942 400               | high                  | 1959    | 200     | lug     | 369             | 368     |              | medium       | 1890            |         |
| ary             | 97              |                       | low                   | 1776    |         | luo     | 0               | 0       |              | zero-shot    | 1975            |         |
| arz             | 95 93 92        |                       | low                   | 2014    |         | lvs     | 100             | 98      |              | low          | 1779            |         |
| asm             | 77 68           |                       | low                   | 1698    |         | mai     | 0               | 0       |              | zero-shot    | 2004            |         |
| ast             | 0 0             |                       | zero-shot             | 0       |         | mal     | 110             | 57      |              | low          | 1754            |         |
| azj             | 95 94           |                       | low                   | 1901    |         | mar     | 112             | 108     |              | low          | 1848            |         |
| bel             | 1160 1157       |                       | high                  | 1641    |         | mkd     | 145             | 143     |              | low          | 1918            |         |
| ben             | 320             | 400                   | high                  | 1987    | 200     | mlt     | 157             | 151     | 74           | low          | 1699            | 200     |
| bos             | 338 99          | 99                    | low                   | 2113    |         | mni     | 0               | 0       |              | zero-shot    | 1257            |         |
| bul             | 103             | 102                   | low                   | 1881    |         | mri     | 0               | 0       |              | zero-shot    | 0               |         |
| cat             | 1767            | 1758 400              | high                  | 1781    | 200     | mya     | 137             | 125     |              | low          | 1860            |         |
| ceb             | 0               | 0                     | zero-shot             | 2020    |         | nld     | 1734            | 1780    | 400          | high         | 2249            | 200     |
| ces             | 189             | 400                   | high                  | 2066    | 200     | nor     | 214             | 193     |              | low          | 2134            |         |
| ckb             | 442 93 92       |                       | low                   | 2001    |         | npi     | 153             | 129     |              | low          | 1714            |         |
| cmn             | 9027            | 400                   | high                  | 1947    |         | nso     | 0               | 0       |              | zero-shot    | 0               |         |
| cym             | 9784 100        | 96 400                | medium                | 1676    |         | nya     | 103             | 99      |              | low          | 2058            |         |
| dan             | 161             | 371 400               | medium                | 1954    | 200     | oci     | 0               | 0       |              | zero-shot    | 0               |         |
| deu             | 3354            | 3490                  | high                  | 2043    | 200     | ory     | 89              | 86      |              | low          | 1721            |         |
| ell             | 345             | 339                   | medium                | 1725    |         | pan     | 196             | 193     |              | low          | 1641            |         |
| eng             | 3845            | 0                     | high                  | 0       |         | pbt     | 131             | 121     | 400          | medium       | 1847            |         |
| est             | 133             | 130 400               | medium                | 1803    | 200     | pes     | 386             | 68      |              | low          | 1980            |         |
| eus             | 276             | 265                   | medium                | 1998    |         | pol     | 341             | 446     | 400          | high         | 1914            | 200     |
| fin             | 182             | 449 400               | high                  | 1933    | 200     | por     | 269             | 246     | 400          | medium       | 2250            | 200     |
| fra             | 2123 2247       |                       | high                  | 2304    | 200     | ron     | 182             | 443     | 400          | high         | 2131            | 200     |
| fuv             | 0               |                       | zero-shot             | 0       |         | rus     | 264             | 144     | 400          | medium       | 2161            | 200     |
| gaz             | 0 0 0           |                       | zero-shot             | 1766    |         | sat     | 0               |         |              | zero-shot    | 0               |         |
| gle             | 56 55           |                       | low                   | 1973    |         | slk     | 142             | 0 390   | 400          | medium       | 1931            | 200     |
| glg             | 123 121         |                       | low                   | 2116    |         | slv     | 107             | 370     |              | low          | 1800            |         |
| guj             | 143 138         |                       | low                   | 1990    |         | sna     | 0               | 0       |              | zero-shot    | 2067            |         |
| hau             | 0 0             |                       | zero-shot             | 0       |         | snd     | 0               | 0       |              | zero-shot    | 1958            |         |
| heb             | 96 96           |                       | low                   | 2092    |         | som     | 143             | 140     |              | low          | 1851            |         |
| hin             | 148 143         | 400                   | medium                | 2066    | 200     | spa     | 1514            | 1285    |              | high         | 2505            | 200     |
| hrv             | 308 219         |                       | medium                | 2119    |         | srp     | 101             | 98      |              | low          | 1910            |         |
| hun             | 260 474         |                       | medium                | 1900    |         | swe     | 129             | 91      |              | low          | 1810            | 200     |
| hye             | 148 146         |                       | low                   | 1696    |         | swh     | 361             | 50      | 400          | medium       | 1930            | 200     |
| ibo             | 35 28           |                       | low                   | 1738    |         | tam     | 256             | 64      | 400          | medium       | 1569            |         |
| ind             | 250 254         | 400                   | medium                | 1818    | 200     | tel     | 89              | 80      | 400          | medium       | 1934            |         |
|                 | 132 130         |                       | low                   | 2059    |         | tgk     | 99              | 98      |              | low          | 1820            |         |
| isl ita         | 591 910         | 400                   | high                  | 2278    | 200     | tgl     | 99              | 93      | 400          | medium       | 2015            |         |
|                 | 302 301         |                       | medium                | 2122    |         |         | tha             | 59      |              | 400          | medium 1941     |         |
| jav jpn         | 381 15141       |                       | high                  | 1798    | 200     | tur     | 189 169         | 100     | 400          | medium       | 2135            | 101     |
|                 | 0               | 400                   |                       |         |         |         |                 |         |              |              | 0               | 200     |
| kam             | 0               |                       | zero-shot             | 0       |         | umb     |                 | 0 0     |              | zero-shot    |                 |         |
| kan             | 121 185         | 208                   | low                   | 1954    |         | ukr     |                 | 132     | 75           | 400          | medium 2052     | 200     |
| kat             | 124 195         |                       | low                   | 1639    |         | urd     | 185             | 145     | 400          |              | medium 1844     | 200     |
| kaz             | 330 327         |                       | medium                | 1895    |         | uzn     |                 | 166 96  |              | 400          | medium          | 200     |
| kea             | 0 0             |                       | zero-shot             | 0       |         | vie     |                 | 151     |              |              | 1801 2396       |         |
|                 | 148             |                       |                       |         |         |         | 194             |         |              | 400          | medium          | 200     |
| khk             | 152             |                       | low                   | 1657    |         | wol     |                 |         |              |              | zero-shot       |         |
| khm             | 191             |                       | low                   | 1661    |         | xho     |                 | 0       | 0            |              | zero-shot 0     |         |
| kir             | 187 129 123 387 |                       | low medium            | 1839    |         | yor     | yue             | 132 130 | 124          | low          | 1384 low 1931   |         |
| kor lao         |                 | 400                   |                       | 2125    |         |         |                 |         |              |              |                 |         |
|                 | 201 200 190     |                       | low                   | 1959    |         | zlm     |                 | 167 155 | 161          | low          | 0               |         |
| lin             | 0 0             |                       | zero-shot             | 0       |         |         | zul             | 62 55   |              | low          | 2063            |         |

Supplementary table 12: Statistics of ASR and S2TT data used to train our SeamlessM4T model. We list the data size in hours of speech between primary (P) i.e., open-source S2TT and pseudo-labeled ASR data, and mined (M). For each language we distinguish between eng-X for translating from English into that language, and X-eng for translating into English. We qualify as high-resource, languages with more than 1000 hours of supervision. Languages with between 500 and 1000 hours are dubbed medium-resource, and languages with less than 500 hours are low-resource. If a language is not supervised during the 1+2 stages of finetuning then it is evaluated as zero-shot.

Supplementary table 13: Statistics of S2ST data used to train our SeamlessM4T model. We list the data size in hours of speech. For each language we distinguish between Eng-X for translating from English into that language, and X-Eng for translating into English.

| Language   | S2ST - X-eng - Primary   | S2ST - X-eng - Mined   | S2ST - eng-X - Primary   | S2ST - eng-X - Mined   | Language   |   S2ST - X-eng - Primary |   S2ST - X-eng - Mined |   S2ST - eng-X - Primary | S2ST - eng-X - Mined   |
|------------|--------------------------|------------------------|--------------------------|------------------------|------------|--------------------------|------------------------|--------------------------|------------------------|
| Total      | 26,254 100               | 23,171 0               | 49,425 0                 | 21,983 0               | lin        |                       52 |                      0 |                        0 | 0                      |
| afr amh    | 46                       | 0                      | 0                        | 0                      | lit        |                      279 |                      0 |                        0 | 0                      |
| arb        | 898                      | 736                    | 895                      | 681                    | ltz        |                        2 |                      0 |                        0 | 0                      |
| ary        | 94                       | 0                      | 0                        | 0                      | lug        |                      362 |                      0 |                        0 | 0                      |
| arz        | 91                       | 0                      | 0                        | 0                      | lvs        |                       95 |                      0 |                        0 | 0                      |
| asm        | 62                       | 0                      | 0                        | 0                      | mal        |                      103 |                      0 |                        0 | 0                      |
| ast        | 0                        | 0                      | 0                        | 0                      | mar        |                      106 |                      0 |                        0 | 0                      |
| azj        | 92                       | 0                      | 0                        | 0                      | mkd        |                      141 |                      0 |                        0 | 0                      |
| bel        | 285                      | 0                      | 0                        | 0                      | mlt        |                      149 |                     46 |                      688 | 39                     |
| ben        | 292                      | 246                    | 652                      | 221                    | mya        |                      123 |                      0 |                        0 | 0                      |
| bos        | 99                       | 0                      | 0                        | 0                      | nld        |                    1,777 |                  1,061 |                    1,003 | 962                    |
| bul        | 101                      | 0                      | 0                        | 0                      | nor        |                      189 |                      0 |                        0 | 0                      |
| cat        | 276                      | 278                    | 692                      | 293                    | npi        |                      114 |                      0 |                        0 | 0                      |
| ces        | 437                      | 522                    | 832                      | 528                    | nya        |                       99 |                      0 |                        0 | 0                      |
| ckb        | 89                       | 0                      | 0                        | 0                      | oci        |                        0 |                      0 |                        0 | 0                      |
| cmn        | 350                      | 1,318                  | 857                      | 1,388                  | ory        |                       84 |                      0 |                        0 | 0                      |
| cym        | 93                       | 197                    | 700                      | 185                    | pan        |                      188 |                      0 |                        0 | 0                      |
| dan        | 368                      | 420                    | 684                      | 450                    | pbt        |                      114 |                      0 |                        0 | 0                      |
| deu        | 2,570                    | 1,661                  | 962                      | 1,618                  | pes        |                      366 |                      0 |                      881 | 0                      |
| ell        | 330                      | 0                      | 0                        | 0                      | pol        |                      591 |                    667 |                      726 | 657                    |
| est        | 128                      | 502                    | 691                      | 477                    | por        |                      355 |                    606 |                      983 | 508                    |
| eus        | 263                      | 0                      | 0                        | 0                      | ron        |                      469 |                    588 |                      951 | 521                    |
| fin        | 446                      | 442                    | 684                      | 414                    | rus        |                      290 |                  1,093 |                      959 | 1,075                  |
| fra        | 2,255                    | 2,438                  | 937                      | 2,303                  | slk        |                      402 |                    427 |                      686 | 426                    |
| gle        | 55                       | 0                      | 0                        | 0                      | slv        |                      377 |                      0 |                        0 | 0                      |
| glg        | 120                      | 0                      | 0                        | 0                      | som        |                      138 |                      0 |                        0 | 0                      |
| guj        | 135                      | 0                      | 0                        | 0                      | spa        |                    1,694 |                  2,335 |                    1,035 | 2,209                  |
| hau        | 78                       | 0                      | 0                        | 0                      | srp        |                       99 |                      0 |                        0 | 0                      |
| heb        | 96                       | 0                      | 0                        | 0                      | swe        |                      124 |                      0 |                      688 | 0                      |
| hin        | 138                      | 466                    | 656                      | 430                    | swh        |                      342 |                    411 |                      682 | 392                    |
| hrv        | 218                      | 0                      | 0                        | 0                      | tam        |                      241 |                    664 |                      654 | 685                    |
| hun        | 468                      | 0                      | 0                        | 0                      | tel        |                       76 |                    426 |                      655 | 403                    |
| hye        | 141                      | 0                      | 0                        | 0                      | tgk        |                       98 |                      0 |                        0 | 0                      |
| ibo        | 24                       | 0                      | 0                        | 0                      | tgl        |                       82 |                    213 |                      661 | 169                    |
| ind        | 248                      | 443                    | 684                      | 375                    | tha        |                      183 |                    462 |                      641 | 408                    |
| isl        | 127                      | 0                      | 0                        | 0                      | tur        |                      156 |                    375 |                      998 | 411                    |
| ita        | 930                      | 716                    | 1,020                    | 636                    | ukr        |                      129 |                    349 |                      662 | 329                    |
| jav        | 291                      | 0                      | 681                      | 779                    | urd        |                      179 |                    139 |                      695 | 502                    |
| jpn        | 624                      | 993                    | 0                        | 0                      | uzn        |                      162 |                    555 |                      682 | 147                    |
| kan        | 119                      | 170                    | 703                      | 135                    | vie        |                      176 |                    666 |                      954 | 684                    |
| kat        | 180                      | 0                      | 0                        | 0                      | wol        |                       13 |                        |                        0 | 0                      |
| kaz        | 319                      |                        | 0                        | 0                      | xho        |                        6 |                      0 |                        0 | 0                      |
| khk        | 143                      | 0                      | 0                        | 0                      | yor        |                      128 |                      0 |                        0 | 0                      |
| khm        | 184                      | 0 0                    | 0                        | 0                      | yue        |                      136 |                      0 |                        0 | 0 0                    |
| kir        | 120                      | 0                      | 0                        | 0                      | zlm        |                      157 |                      0 |                        0 |                        |
| kor        | 350                      | 541                    | 666                      | 541                    | zul        |                       48 |                      0 |                        0 | 0                      |
| lao        | 183                      | 0                      | 0                        | 0                      |            |                          |                        |                          |                        |

| Model             | Languages   | Hours   | Model type        | Open model   |
|-------------------|-------------|---------|-------------------|--------------|
| XLS-R-2B-S2T      | 128         | 0.4M    | wav2vec 2.0 [135] | ✓            |
| USM               | over 300†   | 12M     | BEST-RQ [64]      |              |
| MMS               | 1406        | 0.5M    | wav2vec 2.0 [135] | ✓            |
| SeamlessM4T-Large | over 143†   | 1M      | w2v-BERT 2.0      | ✓            |

Supplementary table 14: A comparison of multilingual speech pre-training in stateof-the-art ASR and S2TT models. †Estimated from the part of data that has language information.

## Supplementary Information IV.3 Unsupervised Speech Pre-training

Labels for speech recognition and translation tasks are scarce and expensive, especially for low-resource languages. It is challenging to train speech translation models with only limited access to supervision. Self-supervised pre-training with unlabeled speech audio data is, thus, a practical approach for reducing the need for supervision in model training. This method helps achieve the same recognition and translation quality with much less labeled data than models without pre-training. It also helps push the limits of model performance with the same amount of labeled data. The most recent and publicly available state-of-the-art multilingual speech pre-trained model is MMS [23]. It extends its predecessor, XLS-R [61], with additional 55K hours of training data and covers more than 1,300 new languages (see Supplementary table 14). Besides MMS, USM [50] is a proprietary state-of-the-art multilingual speech pre-trained model that leverages the latest model architecture (BEST-RQ [64] instead of wav2vec 2.0 [135]), has the largest scale of training data (12M hours), and covers more than 300 languages.

w2v-BERT 2.0 follows w2v-BERT [63] to combine contrastive learning and masked prediction learning, and improves w2v-BERT with additional codebooks in both learning objectives. The contrastive learning module is used to learn Gumbel vector quantization (GVQ) codebooks and contextualized representations that are fed into the subsequent masked prediction learning module. The latter refines the contextualized representations by a different learning task of predicting the GVQ codes directly instead of polarizing the prediction probability of correct and incorrect codes at the masked positions. Instead of using a single GVQ codebook, w2v-BERT 2.0 follows [135] to use product quantization with two GVQ codebooks. Its contrastive learning loss Lc is the same as that in w2v-BERT, including a codebook diversity loss to encourage the uniform usage of codes. Following w2v-BERT, we use GVQ codebooks for masked prediction learning and denote the corresponding loss as LmGVQ . We also created an additional masked prediction task using random projection quantizers [64] (RPQ), for which we denote the corresponding loss as LmRPQ . The overall w2v-BERT 2.0 training loss L is defined as follows:

<!-- formula-not-decoded -->

where loss weights wc, wmGVQ and wmRPQ are set to 1.0, 0.5, and 0.5, respectively.

| ID   | Configuration                                                   |   Fleurs X-eng (↑BLEU) |
|------|-----------------------------------------------------------------|------------------------|
| A    | w2v-BERT baseline with updated XLS-R data (400K hrs, 143 langs) |                   12.4 |
| B    | A + product quantization with 2 GVQ codebooks                   |                   12.5 |
| C    | B + increased open training data from 400K hours to 1M hours    |                   12.7 |
| D    | C + 2 RPQ codebooks for masked prediction objective             |                   12.8 |

Supplementary table 15: Ablation on w2v-BERT variants and training data scaling.

We follow the w2v-BERT XL architecture [63] for the w2v-BERT 2.0 pre-trained speech encoder in SeamlessM4T-Large, which has 24 Conformer layers [65] and approximately 600M model parameters. The w2v-BERT 2.0 model is trained on 1 million hours of open speech audio data that covers over 143 languages.

## Ablations

We explored various techniques to enhance the quality of our encoders' representations, including algorithm-wise improvements and pre-training data scaling. In our ablation, we aimed to evaluate the w2v-BERT variants by their performance on the downstream S2TT task. All pre-trained w2v-BERT speech encoders are composed of 24 Conformer layers [65] with approximately 600M of parameters. Each speech encoder was used to initialize an S2TT model. The text decoder was initialized with the decoder from NLLB-1.3B, a large multilingual machine translation model covering 200 languages [6] with 1.3B parameters. We fine-tuned the S2TT models on the task of speech translation into English (X-eng S2TT) on 67 languages. We fine-tuned all the speech encoder parameters and only fine-tuned LayerNorms and Self-attention in the text decoder (LNA-D [136]). Our learning rate increased up to 3e-4 through 4000 warm-up updates and subsequently followed the inverse square root learning rate schedule. We trained on 32 GPUs with a batch size of 960K frames in each for 100K updates. We report BLEU scores (SacreBLEU 8 [137]) evaluated on the test set of all 101 X-eng directions from Fleurs [18]. Given the coverage of our training data, this means that 34 of the directions were evaluated as zero-shot.

## Results

We summarize our ablation results in Supplementary table 15. We see that product quantization with 2 GVQ codebooks outperforms normal quantization with a single GVQ codebook (A vs. B). Scaling training data leads to performance gains (B vs. C). Adding additional masked prediction learning objectives with 2 RPQ codebooks helps improve performance (C vs. D).

8 see Supplementary table 2

## Supplementary Information IV.4 Multitasking ablations for X2T

## Ablation dataset

To iterate on different multitasking recipes, we constructed a smaller multilingual speech translation benchmark with 14 languages paired with English. The supervised S2TT data comes from two sources: primary (open-source or licensed) and mined, whereas the ASR data is either from open-sourced or licensed datasets. The T2TT data we used in our multitasking fine-tuning is limited to bitexts produced in the pseudolabeling process, i.e., translated transcriptions in the ASR datasets. For a breakdown of the ablation dataset, see Supplementary table 16.

## Experimental setup

We fine-tuned multilingual translation models on our ablation dataset with different mixes of tasks. As a baseline, we only trained on primary S2TT data (eng-X + Xeng), optimizing L1: LS2TT exclusively. With the data fixed, we experimented with two other objectives to optimize: (L2) with joint optimization of T2TT and S2TT (LS2TT +LT2TT) and (L3) with the additional knowledge distillation objective with T2TT as the teacher and S2TT as the student. We then added more data, namely ASR data and mined data respectively, and compared the performance of models trained with different objectives in the three data setups.

We initialized X2T models with our w2v-BERT 2.0 speech encoder and SeamlessM4T-NLLBT2TT model. We fine-tuned all parameters in the speech encoder and text encoder, while only fine-tuning LayerNorms and Self-attentions in

| Language (code)   |   ASR - Primary | S2TT - X-eng - Primary   | S2TT - X-eng - Mined   | S2TT - eng-X - Primary   | S2TT - eng-X - Mined   | S2ST - X-eng - Primary   | S2ST - X-eng - Mined   | S2ST - eng-X - Primary   | S2ST - eng-X - Mined   |
|-------------------|-----------------|--------------------------|------------------------|--------------------------|------------------------|--------------------------|------------------------|--------------------------|------------------------|
| arb               |             934 | 942                      | 600                    | 1,959                    | 600                    | 899                      | 736                    | 895                      | 681                    |
| ben               |             338 | 320                      | 600                    | 1,987                    | 499                    | 292                      | 246                    | 652                      | 221                    |
| eng               |           3,845 | -                        | -                      | -                        | -                      | -                        | -                      | -                        | -                      |
| hin               |             148 | 143                      | 600                    | 2,066                    | 600                    | 138                      | 466                    | 656                      | 430                    |
| ind               |             250 | 254                      | 600                    | 1,818                    | 596                    | 248                      | 443                    | 684                      | 375                    |
| ita               |             591 | 910                      | 600                    | 2,279                    | 600                    | 930                      | 716                    | 1,020                    | 636                    |
| jpn               |             381 | 15,141                   | 600                    | 1,798                    | 259                    | 624                      | 993                    | 681                      | 779                    |
| por               |             269 | 246                      | 600                    | 2,250                    | 600                    | 355                      | 606                    | 983                      | 508                    |
| rus               |             264 | 144                      | 600                    | 2,161                    | 600                    | 290                      | 1,093                  | 959                      | 1,075                  |
| spa               |           1,515 | 1,285                    | -                      | 2,505                    | 574                    | 1,694                    | 2,335                  | 1,035                    | 2,209                  |
| swh               |             361 | 50                       | 600                    | 1,930                    | 596                    | 342                      | 411                    | 682                      | 392                    |
| tha               |             190 | 59                       | 600                    | 1,941                    | 101                    | 184                      | 462                    | 641                      | 408                    |
| tur               |             169 | 100                      | 600                    | 2,135                    | 600                    | 156                      | 375                    | 998                      | 411                    |
| urd               |             185 | 145                      | 600                    | 1,844                    | 507                    | 179                      | 555                    | 682                      | 502                    |
| vie               |             194 | 151                      | 600                    | 2,396                    | 600                    | 176                      | 666                    | 954                      | 684                    |
| Total             |           9,633 | 19,890                   | 7,800                  | 29,068                   | 2,701                  | 6,508                    | 10,103                 | 11,523                   | 9,312                  |

Supplementary table 16: Hours of data in the ablation dataset for the tasks of ASR, S2TT and S2ST, split between eng-X and X-eng when relevant. For each task, we report hours of training data between primary and mined. By default, S2TT mined data is capped at 400 hours in X-eng and at 200 hours in eng-X.

Supplementary table 17: Ablations on multitasking objectives in three different data setups. Results are reported on Fleurs dev.

| Data - Task              |   D1: S2TT data - S2TT (n=28) ↑BLEU |   D1: S2TT data - ASR∗ (n=15) ↓WER |   D1: S2TT data - T2TT (n=28) ↑BLEU |   D2: D1+ASR data - S2TT (n=28) ↑ BLEU |   D2: D1+ASR data - ASR (n=15) ↓WER |   D2: D1+ASR data - T2TT (n=28) ↑BLEU |   D3: D2+Mined data - S2TT (n=28) ↑BLEU |   D3: D2+Mined data - ASR (n=15) ↓WER |   D3: D2+Mined data - T2TT (n=28) ↑BLEU |
|--------------------------|-------------------------------------|------------------------------------|-------------------------------------|----------------------------------------|-------------------------------------|---------------------------------------|-----------------------------------------|---------------------------------------|-----------------------------------------|
| Metric                   |                                26.5 |                               36.5 |                                34.1 |                                   26.7 |                                16.4 |                                       |                                    27.6 |                                  15.8 |                                    34.7 |
| L1: LS2TT L2: L1 + LT2TT |                                     |                                    |                                     |                                        |                                     |                                  34.2 |                                         |                                       |                                         |
|                          |                                26.6 |                               36.4 |                                36.8 |                                   26.7 |                                16.8 |                                  36.1 |                                    27.6 |                                  16.3 |                                    35.4 |
| L3: L2 + LKD             |                                27.1 |                               35.9 |                                36.7 |                                   27.2 |                                16.2 |                                  36.1 |                                    28.3 |                                  15.8 |                                    35.3 |

the text encoder (LNA [138]). We trained all models for 100K updates (corresponding to 5-7 epochs). To regularize our models, we applied LayerDrop (p=0.1) to the speech encoder with masking (p=0.1). For the text encoder-decoder, we applied regular dropouts (p = 0.1). We evaluated the last checkpoint on development data and evaluated BLEU scores on Fleurs dev for translation tasks (including T2TT) and Whisper-style normalized WER for ASR.

## Results

Within each data setup (D1, D2 or D3), we see in Supplementary table 17 that adding T2TT to the multitasking loss, as expected, helps the performance on T2TT (+1.8 BLEU on average D1,2,3). Without adding this loss, fine-tuning exclusively on S2TT leads to catastrophic forgetting of the pre-training T2TT task (comparing L1 to L2). However, the accuracy of S2TT is seldom affected by this joint training with T2TT. Knowledge distillation is proving to be a necessary ingredient to leverage joint fine-tuning with T2TT. After adding knowledge distillation (L1 to L3), S2TT's performance improves by 0.6 BLEU points on average (D1,2,3).

If we compare the three different data setups, adding ASR data is crucial to supporting the ASR task as evaluating it as zero-shot leads to 3× higher error rates. Joint fine-tuning with T2TT and the auxiliary knowledge distillation loss has no negative effect on ASR given that for ASR data, the teacher task is auto-encoding. Adding mined S2TT data for which the source text is not available for T2TT to teach S2TT, still helps S2TT in the M3 task mix. We note, however, that the accuracy of T2TT drops as we add more speech-text only data (ASR and mined S2TT) without the aligned text-text data.

## Supplementary Information IV.5 Leveraging Mined Speech-Text Data

## Experimental setup

We fine-tuned S2TT models on increasing amounts of mined data from SeamlessAlign. On top of the primary S2TT data, in the first model, we add 200 hours of mined data in each direction, 400 hours in the second and 600 hours in the last. SeamlessAlign is ranked based on Sonar scores and we selected the top ranking pairs up to the desired amount of additional data.

## Results

Supplementary table 18 reports the results of models trained with increasing amounts of mined data. The model trained with at most 400 hours in each direction achieves the best average BLEU score. This signals that some filtering of SeamlessAlign -e.g., based on Sonar similarity scores-can improve the quality of the model's translations without inflating the computational cost of training.

| Data setting   |   X-eng (n=14) - ↑BLEU |   X-eng (n=14) - ∆ |   eng-X (n=14) - ↑BLEU |   eng-X (n=14) - ∆ |
|----------------|------------------------|--------------------|------------------------|--------------------|
| Baseline       |                   23.9 |                    |                   29.0 |                    |
| + 200H mined   |                   25.9 |               +2.0 |                   29.4 |               +0.4 |
| + 400H mined   |                   26.6 |               +2.7 |                   29.8 |               +0.8 |
| + 600H mined   |                   26.0 |               +2.1 |                   29.5 |               +0.5 |

Supplementary table 18: Ablations on the use of mined data. Results are reported on Fleurs dev.

## Supplementary Information IV.6 Leveraging mined speech-to-speech data

To measure the impact of adding mined S2ST data to Stage3 of UnitY fine-tuning, we compared model M2 from Appendix Supplementary Information IV.7 to a model trained following the same training procedure, but with more mined data from SeamlessAlign (see amounts of additional data per direction in Supplementary table 16.

## Results

The results in Supplementary table 19 show that adding mined data improves eng-X translation accuracy by 0.5 ASR-BLEU points, but it decreases that of X-eng by 0.2. However, we do notice slight improvements in the quality of the speech generated and hence add SeamlessAlign for the final model training.

## Supplementary Information IV.7 T2U pre-training in UnitY

## Experimental setup

Similar to the ablation dataset described in Appendix Supplementary Information IV.4, we built an S2ST ablation dataset with pseudo-labeled S2ST data (eng-X + Xeng) to fine-tune multilingual UnitY models. With the data fixed, we compare two options for using pre-trained components when fine-tuning UnitY. In the first (M1), we initialized the speech encoder with its adaptor and the first pass decoder with a pre-trained X2T model. In the second (M2), we additionally initialized the T2U of UnitY with a pre-trained T2U model. In both setups, we only fine-tuned the weights of the T2U model on S2ST data.

## Results

We evaluated our models on Fleurs dev for S2ST and report ASR-BLEU scores in Supplementary table 19. We note that T2U pre-training is beneficial for the fine-tuning of UnitY as it converges faster (comparing ASR-BLEU scores after 10K updates) and is, therefore, more computationally efficient.

## Supplementary Information IV.8 Predicting units with UnitY2

In SeamlessM4T models, the task of speech-to-speech translation is broken down into speech-to-text translation (S2TT) and then text-to-unit conversion (T2U). While UnitY relaxes the training difficulty of direct S2ST, the T2U model often hallucinates or truncates the output. This issue can be attributed to the length mismatch between the speech sequence in units and the text sequence in subwords, the former being on average 25 times longer. To reduce errors in the unit generation, we propose a new direct two-pass S2ST architecture, UnitY2, which enhances the unit generation of UnitY by a non-autoregressive (NAR) decoder that does not rely on any external aligner.

UnitY2 replaces the second-pass autoregressive unit decoder in UnitY with a NAR unit decoder. We adopted the decoder architecture of FastSpeech2 [73] and extended it to discrete unit generation. The original FastSpeech2 decoder, designed for generating Mel-filterbank features in TTS, relies on a variance adaptor to add different variance information such as duration, pitch, and energy as conditional inputs before decoding. Given that UnitY2 is designed to model discrete units, we only added duration information with a duration predictor; other information like pitch or prosody are not well-preserved by discrete units [103]. The NAR unit decoder needs to expand the text input sequence to match the length of the unit output sequence, as such, a text-to-unit alignment is necessary. Unlike UnitY, UnitY2 predicts a duplicated (or non-reduced) unit sequence that preserves repetitive units. Although the non-reduced

|    | Model                        | updates      | Fleurs S2ST (↑ASR-BLEU) - X-eng   | Fleurs S2ST (↑ASR-BLEU) - eng-X   |
|----|------------------------------|--------------|-----------------------------------|-----------------------------------|
| M1 | T2U from scratch             | 10K 20K      | 6.9 23.3                          | 1.8 12.4                          |
| M2 | pre-trained T2U              | 10K 20K 50K† | 18.1 24.2 26.5                    | 8.8 15.2 18.6                     |
| M3 | pre-trained T2U + Mined data | 80K†         | 26.3                              | 19.1                              |

Supplementary table 19: Ablations on pre-training UnitY's T2U and use of S2ST mined data. Results are reported on Fleurs dev. † 80K and 50K correspond to 2 epoches in the two different data settings.

unit sequence is longer, fast inference with NAR unit generation can compensate for the computational overhead.

UnitY2 starts with hierarchically upsampling of the T2U encoder output from subword-length, to character-length then to unit-length. The unit duration predictor, key to the hierarchical upsampling, is supervised during training by a multilingual aligner based on RAD-TTS [74]. To address the multimodality problem in the NAR generation of large-vocabulary non-reduced discrete units, we propose an efficient single-pass span-based glancing training.

## Hierarchical subword-to-unit upsampling

The T2U encoder in UnitY2 receives coarse subword-length representations from the X2T text decoder. 9 As a first-pass decoder in UnitY2, its features are not suitable for describing acoustic details necessary for subsequent unit prediction. To leverage fine-grained textual information without hindering translation quality or the efficiency of the X2T decoder, we propose hierarchical subword-to-unit upsampling, where we upsample the subword-length T2U encoder representations to character-length then to unit-length.

Specifically, a subword-to-character upsampler Sub2Char repeats each subwordlength representation hi according to the number of characters in the subword ytext i and adds character-level embeddings. With ytext-char , the character-length sequence corresponding to ytext , we compute the character-length representations hchar as follows:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

where f char dur is a function returning the number of characters (dchar i ) in the i-th subword, E char is a character embedding lookup table, Pos char is a character-level positional embedding layer, and dmodel is the model dimension.

Then, a character-to-unit upsampler Char2Unit further upsamples hchar to unitlength representations hunit as:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

9 Subword vocabulary size of 256K in SeamlessM4T

where f unit dur is a duration predictor (parameterized by θdur) that returns the number of duplicated units (dunit j ) aligned with the j-th character, Ahard is a hard characterto-unit alignment matrix, α is a learnable scale parameter, and Pos unit is a unit-level positional embedding layer. hunit is used as input to the NAR unit decoder. The duration predictor f unit dur in equation (9) is trained to optimize Ldur(θdur), a mean square error (MSE) loss taking the duration predicted by the aligner as training target in the logarithmic domain.

## Unsupervised multilingual character-to-unit alignment learning

For upsampling, the NAR unit decoder requires alignment (Ahard ) between characters and units to train the unit duration predictor f unit dur . The original FastSpeech2 used a forced alignment tool (e.g., Montreal Forced Aligner [139]) to supervise the duration predictor. For our massively multilingual efforts, forced aligners are unavailable for many low-resource languages. To circumvent the need for external aligners, we propose an unsupervised multilingual character-to-unit aligner. We adapted the aligner architecture in RAD-TTS [74] to our use case. Namely, the SeamlessM4T-v2 multilingual char-to-unit aligner is (1) modified to take discrete units and characters as inputs, (2) trained in a multilingual fashion on 35 languages, and (3) trained with curriculum learning for the alignment prior.

For a character-length sequence ytext-char and the associated unit sequence udup , let schar and sunit be the outputs of the aligner's two encoders (one for characters and one for units). A soft alignment Asoft is calculated as follows:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

where Pprior is the Beta-binomial alignment prior to encourage near-diagonal paths [74]. We disabled this alignment prior after 8k training steps to let the aligner learn a more accurate alignment later in the training. To extract a hard alignment Ahard from Asoft , the monotonic alignment search (MAS) algorithm [140] is applied.

To optimize the aligner parameters θalign, we maximized the log-likelihood of all possible monotonic alignment paths S(ytext-char ), based on the forward algorithm. The forward sum loss Lfwd is formulated as:

<!-- formula-not-decoded -->

where the marginalization is efficiently implemented using a CTC loss. To enforce that Asoft matches Ahard , a binarization loss Lbin = Ahard ⊙log Asoft with ⊙ the Hadamard product. This term is simply the KL divergence between the two alignments. Lbin is added after Kbin training steps.

## Efficient span-based glancing training for NAR unit generation

Non-autoregressive sequence generation suffers from the multimodality problem. 10 Previous works have addressed this problem by using iterative decoding [142], powerful generative models like normalizing flows [143], or diffusion-based models [144, 145]. In this work, we used a single-step NAR decoder to maintain inference efficiency. Particularly, UnitY2's NAR T2U decoder is a Glancing Transformer (GLAT) [146] that relaxes NAR token prediction by glancing at the ground-truth tokens. When the naive GLAT based on random masking is used for unit prediction, the task becomes trivial since adjacent units are locally correlated. To adapt GLAT to unit prediction, we propose an efficient span-based GLAT that operates on the character length before glancing at the units.

Given a unit prediction accuracy α, we sampled character positions to mask with a probability 1 - α. With I char the set of the sampled positions to be masked in ytext-char , we obtained the corresponding unit positions I unit following the aligner's Ahard . We then replaced the decoder input in the I unit positions with ground-truth unit embeddings. We demonstrate that the proposed span-based masking is more effective than random masking at the unit level. Furthermore, we propose an efficient training based on a single forward pass where α is estimated from the previous Kglat steps, instead of introducing a duplicate forward pass at each training step.

## Training UnitY2's NAR T2U and aligner

The second-pass NAR unit decoder and aligner are jointly trained with the following objective:

<!-- formula-not-decoded -->

where Linterctc is a character-level CTC loss at an intermediate unit decoder layer, added to accelerate training convergence [147].

## Supplementary Information V Automatic and Human Evaluation

## Supplementary Information V.1 Human Evaluation

We present additional supporting figures and tables for human evaluation in this section. Table 21 compare correlations between a human measure of translation performance (XSTS) and various automated metrics (ASR-BLEU, BLEU, and Blaser 2.0) for both the S2TT and S2ST tasks. We find Blaser 2.0 provides superior correlation with human judgment for both S2TT and S2ST tasks over both BLEU and ASR-BLEU (respectively), in particular in the eng-X direction where BLEU

10 Each token's distribution depends only on the source sentence; this conditional independence assumption prevents a model from properly capturing the highly multimodal distribution of target translations [141].

and ASR-BLEU correlate poorly with human judgment, regardless of the choice of correlation coefficient.

Table 22 shows XSTS performance for SeamlessM4T-Large, SeamlessM4TLarge v2 a human reference (i.e. FLEURS [18] translations themselves), and a Cascaded baseline on the S2TT and S2ST tasks. In particular, we find that SeamlessM4T-Large v2 provides far superior performance over both the SeamlessM4T-Large and Cascaded baseline models, with the strongest performance on S2ST task.

Table 23 shows MOS performance for the models listed above, showing a general preference for SeamlessM4T-Large v2 over SeamlessM4T-Large and Cascaded baselines in the eng-X direction (for all measured aspects: naturalness, sound quality and clarity of speech) but a strong preference for SeamlessM4T-Large over both baselines in the X-eng direction.

Table 24 shows mean language-level XSTS and MOS scores for all evaluated models over all evaluated languages.

## Supplementary Information V.1.1 Human Evaluation Protocols

For S2TT evaluation, we used the XSTS protocol to assess translation quality. For the S2ST task, we evaluate using two protocols: XSTS for translation quality, and MOS to assess naturalness.

## XSTS.

XSTS [26] evaluates translation quality in terms of semantic meaning preservation, and has previously been used to evaluate the NLLB models [6]. While XSTS was originally designed to evaluate text, the protocol is effectively modality agnostic, and we required only small adaptations in order to support S2ST and S2TT tasks. For instance, the S2ST and S2TT versions of the protocol required additional instructions for annotators regarding the treatment of non-speech tags (e.g. &lt;laugh&gt;), which the annotators were instructed to ignore, and how they should consider pauses and non-speech noises (they are instructed to ignore these as well).

On the execution logistics side, conversations with vendors used for our evaluation work indicated that the evaluation of S2ST translations seemed to require a higher cognitive load for the annotators than T2TT (as a result of not being able to experience the source and target simultaneously), and thus was slower to conduct.

## XSTS annotation and calibration process.

During annotation, 3 annotators examined each source-target audio pair (or audio-text pair) and evaluated the item for semantic similarity using the XSTS protocol. Prior to annotating, all annotators went through a set of monolingual English 'practice' evaluations with score justifications. To expedite evaluation, more than 3 (up to 30 in our case) annotators were used per language pair; each evaluated sentence pair was shown to 3 annotators, assigned essentially randomly, and with calibration set items intermixed in the evaluation. In cases where the 3 annotators had a disagreement of score values of 2 or more, 2 additional annotators evaluated the same item again, bringing the total to 5 evaluator scores for those items. The median score over annotators of the same audio pair was then taken for each evaluation sentence pair; the median is used for robustness. The process was the same for both S2ST and S2TT evaluations. For overall direction scores, we report the mean of this median score (or some aggregate, such as the fraction of sentences with a median XSTS score above a given threshold) across all evaluated items in the dataset generated by a particular system in a language direction. Calibration set items received the exact same treatment, resulting in 1 score per sentence pair per annotator pool, and language-level scores were calibrated using the mean score on the calibration set for the crew of annotators evaluating a given language direction; the calibration set and methodology is described below.

To enable interlanguage comparison of model quality, a mono-lingual "cross-lingual calibration set" [26] was generated and included in the evaluation, and scores were calibrated using the 'moderated calibration' methodology established previously [6, 26]. The calibration process was found to reduce language-level annotator biases and has been shown to improve correlation with automatic metrics as a result. Running a calibration set or 'gold set' of items with a known score, even one much-reduced in size (e.g., 50-100 items instead of the 500 here) is useful as a diagnostic tool for ensuring annotation quality, even if one is not intending on doing interlanguage calibration.

## MOS.

To evaluate and compare generated speech quality for the S2ST task, we used a standard Mean Opinion Score (MOS) protocol to evaluate naturalness, quality of sound, and clarity of speech of our generated audio. MOS methodology has been in use in the telecommunications industry for decades and it was standardized in Recommendation ITU-T P.800. In particular, the adapted guidelines that we used for the MOS evaluation include the following instructions:

1. How clear is the speech? Recordings with clear speech and no mumbling and unclear phrases should be given a high score. Recordings with a large amount of mumbling and unclear phrases should be given a low score.
2. How good is the sound quality? Recordings with clean audio and no noise and static in the background should be given a high score. Recordings with a large amount of noise and static in the background should be given a low score.
3. How natural is the speech? Recordings that sound human-like, with naturalsounding pauses, stress, and intonation, should be given a high score. Recordings that sound robotic, flat, or otherwise unnatural should be given a low score.

For each of these questions, annotators are instructed to provide a Likert score (15). The MOS evaluations were conducted on the same generations as those evaluated with the XSTS protocol, with the exclusion of the cross-lingual calibration set items, and we elected to only evaluate a more limited sample of language directions into English (as MOS characteristics were not expected to be strongly dependent on the input language). Similar to XSTS, 3 annotators scored each generation. The median of annotator scores is collected for each item, and aggregate scores are presented in the paper. Unlike XSTS, additional annotators were not consulted when scores disagreed and calibration was not performed.

## Supplementary Information V.1.2 Evaluation Framework

## Dataset

Human evaluations were conducted utilizing the 'test' partition of the Fleurs dataset [18]. The Fleurs 'test' partition provides up to 350 sentences sourced from the FLORES-101 dataset [104] for each supported language (Fleurs supports 102 languages). Each sentence has up to 3 recorded audios spoken by different speakers (depending on which recordings passed quality review), along with the associated FLORES-101 text. The quality review requirement means that each language may not have a recording for all 350 sentences and that for those sentences that do have recordings, not all three speaker recordings may be present.

When conducting an evaluation of a translation system for a particular language direction, we filtered down the Fleurs data to a subset of sentences that have recordings in both languages in order to have a common, bidirectional evaluation set per-language pair. We do this to ensure S2TT and S2ST evaluations both use an identical set of sentences. Because the coverage of Fleurs varies per language, the subset of items present in the evaluation set varies per language and thus also per language pair; though there is a majority of items common across languages, and we believe the scores to be largely comparable as they were drawn from the same domain.

When preparing Fleurs to be used as a human reference set, pairings had to be made between distinct readers in the source language and readers of the equivalent Fleurs item in the target language. When possible, these pairings were made to match user gender (53% of the time over the entirety of the Fleurs test partition, varying significantly between languages paired with English), and mixed-gender matches had to be made for the remaining 47% of items. We elected to limit human evaluation to 2 unique readings per Fleurs sentence at most.

## Language directions, modalities, and systems evaluated

We list the languages and modalities evaluated with each protocol in Table 20. Language selections were made by balancing a mix of resource availability for human annotations. The final language sample captures a large human population while also representing a mix of high and mid-resource languages.

For the S2TT and S2ST tasks, we have XSTS evaluations of 23 languages in both X-eng and eng-X directions for all three evaluated models and a human reference (i.e. the Fleurs data itself).

For the S2ST task, we used the MOS protocol to evaluate for all 23 in the engX direction. Since we do not expect MOS scores to be strongly sensitive to input language when evaluating English output speech, we evaluated a smaller language set in the X-eng direction (only 10 languages).

Supplementary table 20: Summary of evaluations: languages, modalities, models, and protocols used in human evaluations. Modalities and protocols in parentheses are not presented in this paper but will be shared in a later update. The 23 non-English languages evaluated are: Bengali, Catalan, Dutch, Finnish, French, German, Hindi, Indonesian, Italian, Japanese, Korean, Mandarin Chinese, Modern Standard Arabic, Portuguese, Romanian, Russian, Spanish, Swahili, Telugu, Thai, Turkish, Urdu, and Vietnamese.

| Modality   | Protocol   | Direction   | Systems                                                                      | Languages                                             |
|------------|------------|-------------|------------------------------------------------------------------------------|-------------------------------------------------------|
| S2TT       | XSTS       | X-eng       | Whisper-Large-v2 + NLLB 3.3B SeamlessM4T-Large SeamlessM4T-Large v2          | 23 1                                                  |
| S2TT       | XSTS       | eng-X       | Whisper-Large-v2 + NLLB 3.3B SeamlessM4T-Large SeamlessM4T-Large v2          | 23                                                    |
| S2ST       | XSTS       | X-eng       | Whisper-Large-v2 +NLLB 3.3B + YourTTS SeamlessM4T-Large SeamlessM4T-Large v2 | 23                                                    |
| S2ST       | XSTS       | eng-X       | Whisper-Large-v2 + NLLB 3.3B + MMS SeamlessM4T-Large SeamlessM4T-Large v2    | 23                                                    |
| S2ST       | MOS        | X-eng       | Whisper-Large-v2 +NLLB 3.3B + YourTTS SeamlessM4T-Large SeamlessM4T-Large v2 | 10 (rus, tel, cmn, arb, fra, tur, deu, ita, hin, spa) |
| S2ST       | MOS        | eng-X       | Whisper-Large-v2 +NLLB 3.3B + MMS SeamlessM4T-Large SeamlessM4T-Large v2     | 23                                                    |

| Modality   | Direction   | Metric              | Spearmans ρ (95% CI)                      |
|------------|-------------|---------------------|-------------------------------------------|
| S2ST       | eng-X       | ASR-BLEU Blaser 2.0 | 0.246 (-0.037 - 0.49) 0.81 (0.71 - 0.88)  |
| S2ST       | X-eng       | ASR-BLEU Blaser 2.0 | 0.74 (0.61 - 0.85) 0.845 (0.75 - 0.915)   |
| S2TT       | eng-X       | BLEU Blaser 2.0     | 0.155 (-0.094 - 0.41) 0.590 (0.38 - 0.76) |
| S2TT       | X-eng       | BLEU Blaser 2.0     | 0.64 (0.46 - 0.79) 0.716 (0.54 - 0.85)    |

Supplementary table 21: Spearmans ρ correlation coefficients of different automated metrics compared to XSTS at the language level, using bootstrap resamplings to obtain 95% CIs.

Supplementary table 22: Language-direction level aggregate XSTS scores for both S2TT and S2ST tasks. The models are abbreviated for space considerations: "C" denotes the Cascaded models, "R" is a human reference, "S1" refers to SeamlessM4T-Large and "S2" refers to SeamlessM4T-Large v2. Bold scores denote the highest score, underlines denote the highest score ignoring human reference.

| Dir   | Language   | C    |   XSTS R |   (S2ST) S1 | S2        | C         | XSTS R    | (S2TT) S1   |   S2 |
|-------|------------|------|----------|-------------|-----------|-----------|-----------|-------------|------|
|       | arb        | 3.71 |     4.81 |        3.45 | 4.33      | 4.53      | 4.84      | 4.50        | 4.57 |
|       | ben        | 4.08 |     4.89 |        4.31 | 4.69      | 4.73      | 4.84      | 4.75        | 4.74 |
|       | cat        | 4.19 |     4.85 |        4.34 | 4.60      | 4.65      | 4.73      | 4.71        | 4.73 |
|       | cmn        | -    |     4.90 |        3.14 | 3.69      | 3.51      | 4.73      | 4.04        | 3.77 |
|       | deu        | 4.34 |     4.88 |        4.27 | 4.74      | 4.57      | 4.85      | 4.55        | 4.68 |
|       | fin        | 3.60 |     4.74 |        3.23 | 3.83      | 4.15      | 4.76      | 4.07        | 4.15 |
|       | fra        | 4.11 |     4.82 |        3.95 | 4.43      | 4.56      | 4.64      | 4.49        | 4.61 |
|       | hin        | 4.61 |     4.64 |        4.29 | 4.68      | 4.88      | 4.91      | 4.88        | 4.90 |
|       | ind        | 4.08 |     4.91 |        3.62 | 4.58      | 4.68      | 4.80      | 4.73        | 4.80 |
|       | ita        | -    |     4.76 |        4.32 | 4.62      | 4.72      | 4.70      | 4.84        | 4.83 |
|       | jpn        | -    |     4.30 |        2.55 | 2.74      | 4.07      | 4.54      | 3.91        | 3.96 |
| eng-X | kor        | 3.78 |     4.11 |        3.56 | 3.92      | 4.30      | 4.57      | 3.95        | 4.06 |
|       | nld        | 3.56 |     4.22 |        3.64 | 4.17      | 4.61      | 4.54      | 4.70        | 4.78 |
|       | por        | 4.49 |     4.93 |        4.20 | 4.75      | 4.75      | 4.85      | 4.82        | 4.86 |
|       | ron        | 3.98 |     4.92 |        4.04 | 4.41      | 4.45      | 4.74      | 4.45        | 4.60 |
|       | rus        | 4.07 |     4.86 |        3.73 | 4.34      | 4.55      | 4.80      | 4.60        | 4.68 |
|       | spa        | 4.17 |     4.64 |        3.90 | 4.50      | 4.71      | 4.66      | 4.63        | 4.75 |
|       | swh        | 4.30 |     4.76 |        4.23 | 4.69      | 4.77      | 4.89      | 4.75        | 4.80 |
|       | tel        | 4.14 |     4.58 |        3.73 | 4.46      | 4.69      | 4.78      | 4.69        | 4.69 |
|       | tha        | 3.84 |     4.94 |        3.87 | 4.26      | 4.07      | 4.70      | 4.06        | 4.24 |
|       | tur        | 3.82 |     4.87 |        3.67 | 4.20      | 4.42      | 4.93      | 4.44        | 4.55 |
|       | urd        | 4.04 |     4.67 |        4.13 | 4.49      | 4.45      | 4.76      | 4.52        | 4.63 |
|       | vie        | 3.81 |     4.77 |        3.59 | 4.23      | 4.74      | 4.90      | 4.70        | 4.76 |
|       | arb        | 4.14 |     4.51 |        4.00 | 4.53      | 4.28      | 4.75      | 4.24        | 4.48 |
|       | ben        | 1.68 |     4.90 |        4.32 | 4.76      | 1.75      | 4.86      | 4.55        | 4.69 |
|       | cat        | 4.53 |     4.64 |        4.39 | 4.80      | 4.81      | 4.90      | 4.86        | 4.84 |
|       | cmn        | 4.31 |     4.47 |        4.03 | 4.65      | 4.29      | 4.63      | 3.98        | 4.34 |
|       | deu        | 4.66 |     4.78 |        4.41 | 4.78      | 4.70      | 4.85      | 4.60        | 4.59 |
|       | fin        | 4.09 |     4.57 |        3.51 | 4.25      | 4.26      | 4.75      | 3.89        | 4.20 |
|       | fra        | 4.38 |     4.73 |        4.18 | 4.72      | 4.58      | 4.63      | 4.44        | 4.62 |
|       | hin        | 4.63 |     3.97 |        4.65 | 4.76      | 4.73      | 4.89      | 4.79        | 4.80 |
|       | ind        | 4.26 |     4.81 |        3.88 | 4.64      | 4.44      | 4.77      | 4.36        | 4.55 |
|       | ita        | 4.52 |     4.46 |        4.42 | 4.85      | 4.78      | 4.67      | 4.78        | 4.83 |
|       | jpn        | 3.41 |     4.23 |        2.84 | 3.49      | 3.96      | 4.56      | 3.11        | 3.61 |
| X-eng | kor        | 3.95 |     3.82 |        3.38 | 3.95      | 4.30      | 4.58      | 3.46        | 3.99 |
|       | nld        | 4.12 |     4.14 |        4.00 | 4.38      | 4.54      | 4.61      | 4.45        | 4.60 |
|       | por        | 4.73 |     4.38 |        4.40 | 4.83      | 4.83      | 4.77      | 4.69        | 4.68 |
|       | ron        | 4.14 |     4.82 |        3.97 | 4.60      | 4.17      | 4.64      | 4.11        | 4.33 |
|       | rus        | 4.47 |     4.74 |        4.22 | 4.73      | 4.69      | 4.81      | 4.56        | 4.67 |
|       | spa        | 4.39 |     4.20 |        4.05 | 4.69      | 4.77      | 4.65      | 4.65        | 4.68 |
|       | swh        | 3.63 |     4.84 |        3.96 | 4.54      | 4.01      | 4.96      | 4.54        | 4.74 |
|       | tel        | 1.53 |     3.72 |        4.13 | 4.44      | 2.09      | 4.83      | 4.26        | 4.52 |
|       | tha        | 4.09 |     4.88 |        4.10 | 4.62      | 3.18      | 4.54      | 3.33        | 3.79 |
|       | tur        | 4.14 |     4.85 |        3.56 |           |           |           |             | 4.34 |
|       | urd        | 4.07 |     4.50 |        3.95 | 4.33 4.38 | 4.47 3.77 | 4.83 4.77 | 3.86 3.95   | 4.17 |
|       | vie        | 3.74 |     4.73 |        3.36 | 4.07      | 4.06      | 4.83      | 3.74        | 4.16 |

Supplementary table 23: Language-direction level aggregate MOS scores for each MOS aspect and model evaluated. The models are abbreviated for space considerations: "C" denotes the Cascaded models, "R" is a human reference, "S1" refers to SeamlessM4T-Large and "S2" refers to SeamlessM4T-Large v2. Bold scores denote the highest score, underlines denote the highest score ignoring human reference.

|       |     | C    |   Clarity - R | Clarity - S1   | Clarity - S2   | Naturalness - C   | Naturalness - R   | Naturalness - S1   | Quality - S2 C   |   Quality - R |   Quality - S1 |   Quality - S2 |
|-------|-----|------|---------------|----------------|----------------|-------------------|-------------------|--------------------|------------------|---------------|----------------|----------------|
|       | arb | 2.51 |          4.88 | 3.08           | 3.47           | 1.65 4.87         | 2.17              | 2.06               | 4.22             |          4.48 |           4.16 |           4.34 |
|       | ben | 4.66 |          4.45 | 4.67           | 4.85           | 4.49              | 4.41              | 4.44               | 4.76 4.88        |          3.64 |           4.85 |           4.97 |
|       | cat | 2.94 |          4.39 | 3.73           | 4.05           | 2.24              | 4.50              | 3.50 3.85          | 3.30             |          3.40 |           3.79 |           4.14 |
|       | cmn | -    |          3.96 | 3.47           | 3.72           | -                 | 4.12              | 2.44 2.51          | -                |          3.70 |           3.38 |           3.77 |
|       | deu | 3.20 |          4.31 | 3.91           | 4.09           | 1.71              | 4.33 2.89         | 2.35               | 3.50             |          3.55 |           3.51 |           3.72 |
|       | fin | 4.33 |          4.35 | 4.04           | 4.55           | 2.78              | 4.60 2.68         | 3.07               | 4.42             |          3.71 |           4.85 |           4.92 |
|       | fra | 3.70 |          3.62 | 3.78           | 3.84           | 3.37              | 3.69              | 3.51 3.56          | 3.93             |          3.48 |           3.95 |           3.90 |
|       | hin | 4.25 |          3.74 | 3.97           | 4.30           | 4.14              | 4.06 3.90         | 4.06               | 4.26             |          3.72 |           4.09 |           4.32 |
|       | ind | 3.74 |          3.98 | 3.79           | 4.47           | 3.59              | 4.04              | 3.78               | 4.28 4.27        |          3.14 |           4.41 |           4.67 |
|       | ita | -    |          4.86 | 4.45           | 4.62           | -                 | 4.40              | 4.01 4.16          | -                |          4.64 |           4.35 |           4.55 |
|       | jpn | -    |          3.69 | 2.54           | 2.37           | -                 | 3.89              | 2.39 2.29          | -                |          2.05 |           3.23 |           3.24 |
| eng-X | kor | 2.61 |          4.32 | 2.56           | 2.96           | 2.38              | 4.41              | 2.46 2.71          | 4.07             |          2.55 |           3.08 |           3.13 |
|       | nld | 2.58 |          4.37 | 3.79           | 3.58           | 2.28              | 4.63              | 3.53 2.95          | 3.34             |          3.23 |           3.55 |           3.87 |
|       | por | 4.70 |          4.98 | 4.20           | 4.62           | 4.02              | 4.99 3.46         | 3.75               | 4.93             |          4.06 |           4.56 |           4.77 |
|       | ron | 4.16 |          4.87 | 4.48           | 4.72           | 3.94              | 4.94              | 3.83 4.42          | 4.86             |          3.93 |           4.94 |           4.99 |
|       | rus | 2.88 |          4.83 | 3.52           | 3.42           | 1.95              | 4.82 3.01         | 2.56               | 3.87             |          4.23 |           3.93 |           3.93 |
|       | spa | 3.79 |          4.60 | 4.30           | 4.28           | 2.93              | 4.79              | 4.11 3.57          | 3.63             |          4.07 |           4.30 |           4.25 |
|       | swh | 4.46 |          2.96 | 4.62           | 4.76           | 4.59              | 3.05 4.63         | 4.79               | 4.56             |          2.55 |           4.55 |           4.68 |
|       | tel | 4.61 |          3.70 | 3.65           | 4.33           | 3.79              | 3.75              | 3.43               | 4.25 4.79        |          3.13 |           3.77 |           4.42 |
|       | tha | 3.08 |          4.65 | 3.10           | 3.64           | 3.36 4.63         | 3.09              | 3.73               | 4.39             |          4.41 |           3.42 |           3.94 |
|       | tur | 3.51 |          3.89 | 3.30           | 3.65           | 3.30              | 4.47 2.71         | 3.09               | 4.08             |          3.13 |           3.97 |           4.04 |
|       | urd | 3.08 |          4.57 | 4.04           | 4.31           | 3.18              | 4.67              | 4.12 4.27          | 4.55             |          4.16 |           4.86 |           4.90 |
|       | vie | 4.23 |          3.55 | 3.25           | 3.78           | 4.40              | 3.78              | 2.86 3.11          | 4.84             |          3.31 |           4.45 |           4.89 |
|       | arb | 3.25 |          2.66 | 4.36           | 3.86           | 2.70              | 3.01              | 4.21 3.59          | 2.55             |          2.29 |           3.87 |           3.46 |
|       | cmn | 3.88 |          2.68 | 4.38           | 4.26           | 3.33              | 2.97              | 4.09 3.90          | 3.55             |          2.31 |           4.12 |           4.00 |
|       | deu | 3.67 |          2.68 | 4.46           | 4.18           | 2.90              | 3.01 2.95         | 4.09 3.69 3.88     | 2.99             |          2.28 |           3.89 |           3.81 |
|       | fra | 3.75 |          2.68 | 4.33 4.25      | 4.11 4.13      | 3.24 3.11         | 2.97              | 4.13 4.10          | 3.41 3.36        |          2.32 |           4.01 |           3.87 |
|       | hin | 3.63 |          2.64 |                |                |                   |                   | 3.91               |                  |          2.29 |           4.01 |           3.93 |
| X-eng | ita | 3.75 |          2.68 | 4.31           | 4.12           | 3.20              | 2.99              | 4.13 3.93          | 3.42             |          2.31 |           4.04 |           3.89 |
|       | rus | 3.67 |          2.69 | 4.30           | 4.11           | 3.13              | 3.01              | 4.09 3.92          | 3.38             |          2.29 |           4.00 |           3.87 |
|       | spa | 3.69 |          2.65 | 4.30           | 4.13           | 3.11              | 2.98              | 4.14               | 3.37             |          2.29 |           4.05 |           3.92 |
|       | tel | 3.23 |          2.63 | 4.24           | 4.10           | 2.84              | 2.93              | 3.93 3.88          | 3.15             |          2.31 |           4.01 |           3.90 |
|       | tur | 3.70 |          2.69 | 4.32           | 4.13           | 3.16              | 2.95              | 4.04 4.15 3.96     | 3.37             |          2.29 |           4.02 |           3.86 |

## Supplementary Information V.2 Automatic Robustness Evaluation

## Supplementary Information V.2.1 Robustness Against Background Noises

## Results

Figure 7 shows the average test BLEU and test WER over the 4 languages for X-eng S2TT and ASR on Fleurs with low-to-high input noise level (high-tolow SNR).Both BLEU-SNR curves for our new model, SeamlessM4T-Large v2 are consistently above those for Whisper-Large-v2 and SeamlessM4T-Large. Similarly, SeamlessM4T-Large v2's WER-SNR curves are consistently below the ones for Whisper-Large-v2 and SeamlessM4T-Large. These indicate the superior robustness of SeamlessM4T-Large v2 in noisy speaking environments. SeamlessM4T-Large v2 outperforms Whisper-Large-v2 by an average of 53.2% and 50.5% over various noise types and levels for X-eng S2TT and ASR, respectively.

Supplementary table 24: Summary of XSTS and MOS performance for each evaluated model. Bold scores denote the highest aggregate score observed in its category, underlined scores denote the highest aggregate score observed in its category that is not a human reference.

| Modality   | Dir.   | Model                |   XSTS | MOS:N   | MOS:C     | MOS:Q          |
|------------|--------|----------------------|--------|---------|-----------|----------------|
| S2ST       | eng-X  | Cascaded             |   4.02 | 3.20    | 3.65 4.24 | 4.23 3.58 4.08 |
| S2ST       |        | Human Reference      |   4.66 | 4.34    |           |                |
| S2ST       |        | SeamlessM4T-Large    |   3.81 | 3.35    | 3.75      |                |
| S2ST       |        | SeamlessM4T-Large v2 |   4.29 | 3.48    | 4.02      | 4.28           |
| S2ST       | X-eng  | Cascaded             |   3.97 | 3.07    | 3.62      | 3.25           |
| S2ST       | X-eng  | Human Reference      |   4.46 | 2.98    | 2.67      | 2.30           |
| S2ST       | X-eng  | SeamlessM4T-Large    |   3.97 | 4.12    | 4.32      | 4.00           |
| S2ST       | X-eng  | SeamlessM4T-Large v2 |   4.47 | 3.86    | 4.11      | 3.85           |
| S2TT       | eng-X  | Cascaded             |   4.49 | -       | -         | -              |
| S2TT       | eng-X  | Human Reference      |   4.75 | -       | -         | -              |
| S2TT       | eng-X  | SeamlessM4T-Large    |   4.50 | -       | -         | -              |
| S2TT       | eng-X  | SeamlessM4T-Large v2 |   4.56 | -       | -         | -              |
|            | X-eng  | Cascaded             |   4.15 | -       | -         | -              |
|            | X-eng  | Human Reference      |   4.73 | -       | -         | -              |
|            | X-eng  | SeamlessM4T-Large    |   4.22 | -       | -         | -              |
|            | X-eng  | SeamlessM4T-Large v2 |   4.44 | -       | -         | -              |

It also outperforms our earlier model, SeamlessM4T-Large by an average of 14.9% and 14.5% for X-eng S2TT and ASR, respectively.

## Supplementary Information V.2.2 Robustness Against Speaker Variations

| Model                |   Fleurs X-eng S2TT - chrFMS↑ |   Fleurs X-eng S2TT - CoefVarMS↓ |   Fleurs ASR - chrFMS↑ |   Fleurs ASR - CoefVarMS↓ |
|----------------------|-------------------------------|----------------------------------|------------------------|---------------------------|
| Whisper-Large-v2     |                          40.8 |                             13.7 |                   58.7 |                      17.0 |
| SeamlessM4T-Large    |                          45.3 |                              9.1 |                   72.5 |                       6.4 |
| SeamlessM4T-Large v2 |                          51.6 |                              6.3 |                   79.2 |                       4.0 |

Supplementary table 25: Evaluation results of model robustness against vocal style variations. We report test average by-group mean chrF (chrFMS) and test average by-group coefficient of variation on chrF (CoefVarMS) for X-eng S2TT and ASR on Fleurs (77 and 78 source languages respectively which have at least 40 content groups).

WHISPER-LARGE-V2 SEAMLESSM4T-LARGE SEAMLESSM4T-LARGE V2

<!-- image -->

Supplementary figure 7: Evaluation results of model robustness against background noise. We report average test BLEU and test WER over four languages (three language families) for X-eng S2TT and ASR on Fleurs with low-to-high input noise level (high-to-low SNR). Simulated noises are sampled from MUSAN [76] on the "noise" and "music" categories.

## Supplementary Information VI Appendix: Responsible AI

|      | X-eng                                                                    | eng-X                                                                                                 |
|------|--------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| S2ST | arb,bul,cat,deu,ell,fra,lvs,mar,nld, por,ron,rus,spa,swe,tam,tha,ukr,urd | arb,cat,ces,dan,deu,fra,ita,nld,por,ron, rus,slk,spa,swe,tha,ukr,urd                                  |
| S2TT |                                                                          | arb,bel,bul,cat,ces,dan,deu,ell,fra,ita, lit,lvs,mar,nld,por,ron,rus,slk,slv,spa, swe,tam,tha,ukr,urd |

Supplementary table 26: List of language codes in the bias evaluation experiments, organized by task and language direction.

## Supplementary Information VI.1 Toxicity

In this appendix section, we report further details on toxicity detection results. Supplementary figures 8 and 9 show results of added toxicity with ETOX and ASR-ETOX for Fleurs and HolisticBias detailed by language. While in the figures we show the languages reported in section 2.4, Table 27 reports the averages on languages at the intersection of systems available (across speech translation models and ASR-ETOX, in parentheses: 94 11 , 74 12 , 39 13 ). With this larger set of languages, mitigation due to MinTox is lower in the case of S2ST (consistent with previous results).

|                        | Fleurs X-eng ETOX (74) % (↓)   | Fleurs eng-X ETOX (74) % (↓)   | HolisticBias ETOX (90) % (↓)   |
|------------------------|--------------------------------|--------------------------------|--------------------------------|
| S2TT                   |                                |                                |                                |
| Baseline               | 0.11                           | 0.26                           | 0.29                           |
| SeamlessM4T-Large      | 0.09                           | 0.28                           | 0.20                           |
| SeamlessM4T-v2         | 0.09                           | 0.23                           | 0.09                           |
| SeamlessM4T-v2 +MinTox | 0.09                           | 0.10                           | 0.02                           |
|                        | ETOX (39) % (↓)                | ETOX (39) % (↓)                | ETOX (39) % (↓)                |
| S2ST                   |                                |                                |                                |
| Baseline               | 0.33                           | 0.07                           | 0.25                           |
| SeamlessM4T-Large      | 0.14                           | 0.04                           | 0.14                           |
| SeamlessM4T-v2         | 0.13                           | 0.03                           | 0.13                           |
| SeamlessM4T-v2 +MinTox | 0.05                           | 0.03                           | 0.06                           |

Supplementary table 27: Results for S2TT and S2ST averaged across several directions at the intersection of systems available (in parentheses) that add toxicity. ETOX is ASR-ETOX in the case of speech outputs. Baseline corresponds to WhisperLarge-v2 for S2TT X-eng; Whisper-Large-v2 + NLLB-3.3B for S2TT X-eng; Whisper-Large-v2 + YourTTS for S2ST X-eng.

Supplementary figures 10 and 11 show results of added toxicity with MuTox for Fleurs and HolisticBias detailed by language. More details on toxicity per demographic axes can be found in [148].

## Supplementary Information VI.2 Bias

This section reports full results when analyzing gendered translations when using neutral inputs (eng-X) and the gap in translation performance between inputs that only differ in gender (X-eng).

11 afr, amh, arb, ary, arz, asm, azj, bel, ben, bos, bul, cat, ceb, ces, ckb, cym, dan, deu, ell, eng, est, eus, fin, fra, gaz, gle, glg, guj, heb, hin, hrv, hun, hye, ibo, ind, isl, ita, jav, jpn, kan, kat, kaz, khk, khm, kir, kor, lao, lit, lug, luo, lvs, mai, mal, mar, mkd, mlt, mni, mya, nld, nno, nob, npi, nya, ory, pan, pbt, pes, pol, por, ron, rus, sat, slk, slv, sna, snd, som, spa, srp, swe, swh, tam, tel, tgk, tgl, tha, tur, ukr, urd, uzn, vie, yor, yue, zsm, zul

12 amh, arb, asm, azj, bel, ben, bos, bul, cat, ces, cmn, cym, dan, deu, ell, est, fin, fra, glg, guj, heb, hin, hrv, hun, hye, ind, isl, ita, jav, jpn, kan, kat, kaz, khk, khm, kor, lao, lit, lvs, mal, mar, mkd, mlt, mya, nld, nob, npi, pan, pbt, pes, pol, por, ron, rus, slk, slv, sna, snd, som, spa, srp, swe, swh, tam, tel, tgl, tha, tur, ukr, urd, uzn, vie, yor

13 arb, ben, bul, cat, ces, cmn, cym, dan, deu, ell, est, fin, fra, heb, hin, hun, ind, ita, jpn, kor, mlt, nld, pes, pol, por, ron, rus, slk, spa, swe, swh, tel, tgl, tha, tur, ukr, urd, uzn, vie

Supplementary figure 8: Added toxicity for X-eng and eng-X in Fleurs with ETOX and ASR-ETOX. The figure shows the outputs with added toxicity per language for Baseline, SeamlessM4T-Large, SeamlessM4T-Large v2 and SeamlessM4T-Large v2 + MinTox. Baseline corresponds to Whisper-Large-v2 for S2TT X-eng; Whisper-Largev2 + NLLB-3.3B for S2TT X-eng; Whisper-Large-v2 + YourTTS for S2ST X-eng.

<!-- image -->

Supplementary figure 9: Added toxicity for eng-X for S2TT (top) and S2ST (bottom) in HolisticBias with ETOX and ASR-ETOX. The figure shows the number of outputs with added toxicity (above 0.05%) per language for baseline, SeamlessM4T-Large, SeamlessM4T-Large v2 and SeamlessM4T-Large v2 + MinTox systems. Baseline corresponds to Whisper-Large-v2 for S2TT X-eng; Whisper-Large-v2 + NLLB-3.3B for S2TT X-eng; Whisper-Large-v2 + YourTTS for S2ST X-eng.

<!-- image -->

Supplementary figure 10: Added toxicity for X-eng and eng-X in Fleurs S2TT and S2ST with MuTox. The figure shows the number of outputs with added toxicity per language for baseline, SeamlessM4T-Large, SeamlessM4T-Large v2 and SeamlessM4T-Large v2 + MinTox systems. Baseline corresponds to Whisper-Large-v2 for S2TT X-eng; Whisper-Large-v2 + NLLB-3.3B for S2TT X-eng; Whisper-Large-v2 + YourTTS for S2ST X-eng.

<!-- image -->

Supplementary figure 11: Added toxicity for eng-X for S2TT and S2ST in HolisticBias with MuTox. The figure shows the number of outputs with added toxicity per language for baseline, SeamlessM4T-Large v2, SeamlessM4T-Large v2 + MinTox systems. Baseline corresponds to Whisper-Large-v2 for S2TT X-eng; Whisper-Large-v2 + NLLB-3.3B for S2TT X-eng; Whisper-Large-v2 + YourTTS for S2ST X-eng.

<!-- image -->

<!-- image -->

WHISPER-LARGE-V2 (ASR)+ NLLB-3.3B SEAMLESSM4T-LARGE

Supplementary figure 12: Left: The chrF points difference between masculine and feminine forms for eng-X S2TT using English speech as source and X text translation (masculine or feminine) as reference. Right: The ASR-chrF points difference between masculine and feminine forms for eng-X S2ST using English speech as source and X text translation (masculine or feminine) as reference.

WHISPER-LARGE-V2 SEAMLESSM4T-LARGE WHISPER-LARGE-V2 + YOURTTS

<!-- image -->

Supplementary figure 13: (left) The chrF points difference between masculine and feminine for X-eng S2TT using X speech synthesized by the masculine or feminine version of the text and English text as a reference. (right) The ASR-chrF points difference between masculine and feminine forms for X-eng S2ST using X speech synthesized by the masculine or feminine version of text and English text as reference.

## eng-X.

In our analysis, we utilize the masculine or the feminine human translations of the non-English languageas references. The source for this analysis is the English (eng) Multilingual HolisticBias dataset, comprising a collection of unique sentences with ambiguous gender. Figure 12 shows the results per target language, evincing the following patterns:

WHISPER-LARGE-V2 + YOURTTS SEAMLESSM4T-LARGE

<!-- image -->

Supplementary figure 14: (left) The supervised Blaser 2.0 points difference between masculine and feminine forms for eng-X S2ST using English speech as the source and X text translation (masculine and feminine) as reference. The results are averaged from three experiments. (right) The supervised Blaser 2.0 points difference for X-eng S2ST using X speech synthesized by the masculine or feminine version of text and English text as reference.

- In SeamlessM4T-LargeS2TT, the translation quality deteriorates for all the languages except Thai when using the feminine reference, and is especially noticeable in languages like Catalan (with a significant 10.3 chrF points difference), Slovak (10.1), and Spanish (10.0). For the Whisper-Large-v2 + NLLB-3.3B combination, a decline in translation quality is observed across all languages. The highest differences are found in Catalan (10.7), Spanish (10.3), and Arabic (10.2). It's worth mentioning that the biases' distribution over languages is similar between SeamlessM4T-Large and the Whisper-Large-v2 + NLLB-3.3B combination, with Thai being the only exception.
- In S2ST, we noticed similar trends in relation to S2TT, where translation quality is lowered in all languages (except Thai) when assessing with the feminine reference. The highest differences are with Catalan (10.7 ASR-chrF points difference), Spanish (10.0), and Slovak (9.3).

The left panel of Figure 14 shows the results for automatic speech evaluation by way of Blaser 2.0. We observe similar trends in the ASR-chrF metric. The translation quality deteriorates by an average of 0.02 supervised Blaser 2.0 points across languages when evaluating with the feminine reference for all languages except Thai. Interestingly, the evaluation for French reveals a negligible difference. The highest differences are found in Spanish (0.07), followed by German (0.03).

These differences show that when no gender information is available in the source sentence, the model will prefer to translate to the masculine form in the target language. Note that for some languages (like Spanish or French), the plural masculine form is indistinguishable from the plural generic form.

## X-eng.

Our main objective is to assess the translation quality when starting from a gendered sentence and translating it into English. As such, we aim to measure the model's robustness with regard to gender bias and its ability to handle translations between languages that mark grammatical gender towards English. Figure 13 shows the results per source language for SeamlessM4T-Large and Whisper-Large-v2 or Whisper-Large-v2 + YourTTS. We observe that:

- In S2TT, the performance is better when translating from the masculine reference for most languages (15 out of 18 for SeamlessM4T-Large and 16 out of 18 for the Whisper-Large-v2). However, they have different biases towards different languages. The highest differences between the masculine and feminine forms in SeamlessM4T-Large are with Tamil (6.4 chrF points difference) and Urdu (5.0). 14 On the other hand, the highest differences in Whisper-Large-v2 are with Spanish (5.3), Urdu (3.8), and Russian (3.4).
- In S2ST, we observe similar outcomes to those in S2TT. The model quality is mostly better when translating from masculine cases, as evident in 14 out of 18 languages for SeamlessM4T-Large and 17 out of 18 for the Whisper-Largev2 + YourTTS combination. The most significant differences between masculine and feminine sources in SeamlessM4T-Large are found in Tamil (with an ASR-chrF point difference of 6.3) and Spanish (4.5). The highest differences in Whisper-Large-v2 are in Spanish (4.9), Urdu (3.7), and Ukrainian (3.5).

The right panel of Figure 14 demonstrates the performance comparison using Blaser 2.0. Like the findings in ASR-chrF, the translation quality generally improves when translating from masculine cases, which is observed in 16 out of 18 languages and 15 out of 18 languages for SeamlessM4T-Large and Whisper-Largev2 + YourTTS respectively. The highest differences for SeamlessM4T-Large are with Tamil (0.21 supervised Blaser 2.0 points), Spanish (0.12), and Swedish (0.11). For Whisper-Large-v2 + YourTTS, the highest differences are found in Arabic (0.14), Spanish (0.075), and Tamil (0.05).

## Robustness against vocal style variations.

Supplementary table 25 shows the chrFMS and CoefVarMS scores of SeamlessM4TLarge v2, SeamlessM4T-Large and Whisper-Large-v2 on Fleurs X-eng S2TT and ASR test sets. We see that SeamlessM4T-Large v2 outperforms WhisperLarge-v2 on CoefVarMS by an average of 66.4% over X-eng S2TT and ASR tasks. Moreover, SeamlessM4T-Large v2 outperforms Whisper-Large-v2 on chrFMS by an average of 31.5%. Note that SeamlessM4T-v2 also outperforms SeamlessM4T-Large on both tasks and metrics. These suggest the superior robustness of SeamlessM4T-Large v2 when it comes to vocal style variations.

## References

78. Plag, I., Dalton-Puffer, C. &amp; Baayen, H. Morphological productivity across speech and writing. English Language &amp; Linguistics 3, 209-228 (1999).

14 We find that in our experiment, Arabic shows the bias toward the cases when translated from feminine version, which contrasts with the findings in the Multilingual HolisticBias [35] where Arabic exhibited significantly higher performance when translating from the masculine version. We hypothesize that this difference is attributed to our use of a different language code "ara" instead of "arb" when applying the MMS-TTS.

79. Kraut, R., Galegher, J., Fish, R. &amp; Chalfonte, B. Task requirements and media choice in collaborative writing. Human-Computer Interaction 7, 375-407 (1992).
80. Kumar, A. &amp; Epley, N. It's surprisingly nice to hear you: Misunderstanding the impact of communication media can lead to suboptimal choices of how to connect with others. Journal of Experimental Psychology: General 150, 595 (2021).
81. Schroeder, J., Kardas, M. &amp; Epley, N. The humanizing voice: Speech reveals, and text conceals, a more thoughtful mind in the midst of disagreement. Psychological science 28, 1745-1762 (2017).
82. Markelova, K. Illiteracy: "another form of slavery" 2021. https://en.unesco.org/ courier/2021-5/illiteracy-another-form-slavery.
83. GBD 2019 Blindness and Vision Impairment Collaborators. Trends in prevalence of blindness and distance and near vision impairment over 30 years: an analysis for the Global Burden of Disease Study. The Lancet global health 9, e130-e143 (2021).
84. Jung, Y. &amp; Kim, B. Coexistence of multiple writing systems: Classifying digraphia in post-socialist countries. Journal of Eurasian Studies, 18793665231188380 (2023).
85. Siddhant, A. et al. Towards the Next 1000 Languages in Multilingual Machine Translation: Exploring the Synergy Between Supervised and Self-Supervised Learning. CoRR abs/2201.03110. arXiv: 2201.03110. https://arxiv.org/abs/ 2201.03110 (2022).
86. Fan, A. et al. Beyond English-Centric Multilingual Machine Translation. The Journal of Machine Learning Research (2020).
87. Chan, W., Jaitly, N., Le, Q. &amp; Vinyals, O. Listen, attend and spell: A neural network for large vocabulary conversational speech recognition in 2016 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP) (2016), 4960-4964.
88. Berard, A., Pietquin, O., Servan, C. &amp;Besacier, L. Listen and Translate: A Proof of Concept for End-to-End Speech-to-Text Translation in NeurIPS Workshop on End-to-end Learning for Speech and Audio Processing. (2016).
89. Bérard, A., Besacier, L., Kocabiyikoglu, A. C. &amp; Pietquin, O. End-to-end automatic speech translation of audiobooks in 2018 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP) (2018), 6224-6228.
90. Gangi, M. A. D., Negri, M. &amp;Turchi, M. One-to-ManyMultilingual End-to-End Speech Translation. 2019 IEEE Automatic Speech Recognition and Understanding Workshop (ASRU), 585-592. https://api.semanticscholar.org/CorpusID: 203905407 (2019).
91. Inaguma, H., Duh, K., Kawahara, T. &amp; Watanabe, S. Multilingual endto-end speech translation in 2019 IEEE Automatic Speech Recognition and Understanding Workshop (ASRU) (2019), 570-577.
92. Di Gangi, M. A., Cattoni, R., Bentivogli, L., Negri, M. &amp;Turchi, M. MuST-C: a Multilingual Speech Translation Corpus in Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics:

- Human Language Technologies, Volume 1 (Long and Short Papers) (Association for Computational Linguistics, Minneapolis, Minnesota, June 2019), 2012-2017. https://aclanthology.org/N19-1202.
93. Iranzo-Sánchez, J. et al. Europarl-st: Amultilingual corpus for speech translation of parliamentary debates in ICASSP 2020-2020 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP) (2020), 8229-8233.
94. Wang, C. et al. VoxPopuli: A Large-Scale Multilingual Speech Corpus for Representation Learning, Semi-Supervised Learning and Interpretation in Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics and the 11th International Joint Conference on Natural Language Processing (Volume 1: Long Papers) (Association for Computational Linguistics, Online, Aug. 2021), 993-1003. https://aclanthology.org/2021.acl-long.80.
95. Ansari, E. et al. FINDINGS OF THE IWSLT 2020 EVALUATION CAMPAIGN in Proceedings of the 17th International Conference on Spoken Language Translation (Association for Computational Linguistics, Online, July 2020), 134. https://aclanthology.org/2020.iwslt-1.1.
96. Potapczyk, T. &amp;Przybysz, P. SRPOL's System for the IWSLT 2020 End-to-End Speech Translation Task in Proceedings of the 17th International Conference on Spoken Language Translation (Association for Computational Linguistics, Online, July 2020), 89-94. https://aclanthology.org/2020.iwslt-1.9.
97. Anil, R. et al. PaLM 2 Technical Report 2023. arXiv: 2305.10403 [cs.CL].
98. Borsos, Z. et al. AudioLM: A Language Modeling Approach to Audio Generation. IEEE/ACM Transactions on Audio, Speech, and Language Processing 31, 2523-2533 (2023).
99. Seamless Communication et al. SeamlessM4T-Massively Multilingual &amp; Multimodal Machine Translation 2023. https://arxiv.org/abs/2308.11596.
100. ITU-T Recommendation P.808. Subjective evaluation of speech quality with a crowdsourcing approach Geneva, 2018.
101. Jia, Y., Ramanovich, M. T., Remez, T. &amp; Pomerantz, R. Translatotron 2: Highquality direct speech-to-speech translation with voice preservation in Proceedings of the 39th International Conference on Machine Learning (eds Chaudhuri, K. et al.) 162 (PMLR, 2022), 10120-10134. https://proceedings.mlr.press/v162/ jia22b.html.
102. Hsu, W. -N. et al. Hubert: Self-supervised speech representation learning by masked prediction of hidden units. IEEE/ACM Transactions on Audio, Speech, and Language Processing 29, 3451-3460 (2021).
103. Polyak, A. et al. Speech Resynthesis from Discrete Disentangled Self-Supervised Representations in Proc. Interspeech 2021 (2021).
104. Goyal, N. et al. The Flores-101 Evaluation Benchmark for Low-Resource and Multilingual Machine Translation. Transactions of the Association for Computational Linguistics 10, 522-538. https://aclanthology.org/2022.tacl-1.30 (2022).
105. Jia, Y., Tadmor Ramanovich, M., Wang, Q. &amp; Zen, H. CVSS Corpus and Massively Multilingual Speech-to-Speech Translation in Proceedings of the Thirteenth Language Resources and Evaluation Conference (European Language Resources

- Association, Marseille, France, June 2022), 6691-6703. https://aclanthology. org/2022.lrec-1.720.
106. Ethnologue: Languages of the World Sixteenth (ed Lewis, M. P.) (SIL International, Dallas, TX, USA, 2009).
107. Hammarström, H., Forkel, R., Haspelmath, M. &amp; Bank, S. Glottolog database 4.6 2022.
108. Kumar Vuddagiri, R., Gurugubelli, K., Jain, P., Vydana, H. K. &amp; Kumar Vuppala, A. IIITH-ILSC Speech Database for Indain Language Identification in Proc. 6th Workshop on Spoken Language Technologies for Under-Resourced Languages (SLTU 2018) (2018), 56-60.
109. Wanjawa, B. et al. Kencorpus: A Kenyan Language Corpus of Swahili, Dholuo and Luhya for Natural Language Processing Tasks. arXiv preprint arXiv:2208.12081 (2022).
110. Duquenne, P. -A., Gong, H., Sagot, B. &amp; Schwenk, H. T-Modules: Translation Modules for Zero-Shot Cross-Modal Machine Translation in Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing (Association for Computational Linguistics, Abu Dhabi, United Arab Emirates, Dec. 2022), 5794-5806. https://aclanthology.org/2022.emnlp-main.391.
111. Duquenne, P. -A., Schwenk, H. &amp; Sagot, B. Modular Speech-to-Text Translation for Zero-Shot Cross-Modal Transfer in Interspeech (2023).
112. Johnson, J., Douze, M. &amp; Jégou, H. Billion-scale similarity search with GPUs. IEEE Transactions on Big Data 7, 535-547 (2019).
113. Schwenk, H. et al. CCMatrix: Mining Billions of High-Quality Parallel Sentences on the Web in Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics and the 11th International Joint Conference on Natural Language Processing (Volume 1: Long Papers) (Association for Computational Linguistics, Online, Aug. 2021), 6490-6500. https://aclanthology. org/2021.acl-long.507.
114. Dehak, N., Torres-Carrasquillo, P. A., Reynolds, D. &amp; Dehak, R. Language recognition via i-vectors and dimensionality reduction in Twelfth annual conference of the international speech communication association (2011).
115. Snyder, D. et al. Spoken language recognition using x-vectors. in Odyssey 2018 (2018), 105-111.
116. Cai, W., Cai, D., Huang, S. &amp; Li, M. Utterance-level end-to-end language identification using attention-based CNN-BLSTM in ICASSP 2019-2019 IEEE international conference on acoustics, speech and signal processing (ICASSP) (2019), 5991-5995.
117. Miao, X., McLoughlin, I. &amp; Yan, Y. A New Time-Frequency Attention Mechanism for TDNN and CNN-LSTM-TDNN, with Application to Language Identification. in Interspeech (2019), 4080-4084.
118. Wan, L., Sridhar, P., Yu, Y., Wang, Q. &amp; Moreno, I. L. Tuplemax loss for language identification in ICASSP 2019-2019 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP) (2019), 5976-5980.

119. Lopez-Moreno, I. et al. Automatic language identification using deep neural networks in 2014 IEEE international conference on acoustics, speech and signal processing (ICASSP) (2014), 5337-5341.
120. Lozano-Diez, A., Zazo-Candil, R., Gonzalez-Dominguez, J., Toledano, D. T. &amp; Gonzalez-Rodriguez, J. An end-to-end approach to language identification in short utterances using convolutional neural networks in Sixteenth Annual Conference of the International Speech Communication Association (2015).
121. Fernando, S., Sethu, V., Ambikairajah, E. &amp; Epps, J. Bidirectional Modelling for Short Duration Language Identification. in Interspeech (2017), 2809-2813.
122. Shen, P., Lu, X., Li, S. &amp; Kawai, H. Feature Representation of Short Utterances Based on Knowledge Distillation for Spoken Language Identification. in Interspeech (2018), 1813-1817.
123. Shen, P., Lu, X., Li, S. &amp;Kawai, H. Interactive learning of teacher-student model for short utterance spoken language identification in ICASSP 2019-2019 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP) (2019), 5981-5985.
124. Gállego, G. I., Tsiamas, I., Escolano, C., Fonollosa, J. A. R. &amp;Costa-jussà, M. R. End-to-End Speech Translation with Pre-trained Models and Adapters: UPC at IWSLT 2021 in Proceedings of the 18th International Conference on Spoken Language Translation, IWSLT 2021, Bangkok, Thailand (online), August 5-6, 2021 (eds Federico, M. et al.) (Association for Computational Linguistics, 2021), 110-119. https://doi.org/10.18653/v1/2021.iwslt-1.11.
125. Potapczyk, T. &amp;Przybysz, P. SRPOL's System for the IWSLT 2020 End-to-End Speech Translation Task in Proceedings of the 17th International Conference on Spoken Language Translation, IWSLT 2020, Online, July 9 - 10, 2020 (eds Federico, M. et al.) (Association for Computational Linguistics, 2020), 89-94. https://doi.org/10.18653/v1/2020.iwslt-1.9.
126. Gaido, M., Negri, M., Cettolo, M. &amp;Turchi, M. Beyond Voice Activity Detection: Hybrid Audio Segmentation for Direct Speech Translation in 4th International Conference on Natural Language and Speech Processing, Trento, Italy, November 12-13, 2021 (eds Abbas, M. &amp; Freihat, A. A.) (Association for Computational Linguistics, 2021), 87-94. https ://aclanthology.org/2021. icnlsp1.7.
127. Tsiamas, I., Gállego, G. I., Fonollosa, J. A. R. &amp; Costa-jussà, M. R. SHAS: Approaching optimal Segmentation for End-to-End Speech Translation in Proc. Interspeech 2022 (2022), 106-110.
128. Yang, Y. et al. Improving Multilingual Sentence Embedding using Bi-directional Dual Encoder with Additive Margin Softmax in Proceedings of the TwentyEighth International Joint Conference on Artificial Intelligence, IJCAI-19 (International Joint Conferences on Artificial Intelligence Organization, July 2019), 5370-5378. https://doi.org/10.24963/ijcai.2019/746.
129. Ramesh, G. et al. Samanantar: The Largest Publicly Available Parallel Corpora Collection for 11 Indic Languages. TACL 10, 145-162 (2022).
130. Reimers, N. &amp; Gurevych, I. Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks in Proceedings of the 2019 Conference on Empirical

- Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP) (Association for Computational Linguistics, Hong Kong, China, Nov. 2019), 3982-3992. https: //aclanthology.org/D19-1410.
131. Reimers, N. &amp; Gurevych, I. Making Monolingual Sentence Embeddings Multilingual using Knowledge Distillation in Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP) (Association for Computational Linguistics, Online, Nov. 2020), 4512-4525. https:// aclanthology.org/2020.emnlp-main.365.
132. Baevski, A. et al. data2vec: A General Framework for Self-supervised Learning in Speech, Vision and Language 2022. https://arxiv.org/abs/2202.03555.
133. Bapna, A. et al. mslam: Massively multilingual joint pre-training for speech and text. arXiv preprint arXiv:2202.01374 (2022).
134. Cheng, Y., Zhang, Y., Johnson, M., Macherey, W. &amp; Bapna, A. Mu2SLAM: Multitask, Multilingual Speech and Language Models in Proceedings of the 40th International Conference on Machine Learning (eds Krause, A. et al.) 202 (PMLR, 2023), 5504-5520. https://proceedings.mlr.press/v202/cheng23e.html.
135. Baevski, A., Zhou, Y., Mohamed, A. &amp; Auli, M. wav2vec 2.0: A Framework for Self-Supervised Learning of Speech Representations in Advances in Neural Information Processing Systems (eds Larochelle, H., Ranzato, M., Hadsell, R., Balcan, M. &amp; Lin, H.) 33 (Curran Associates, Inc., 2020), 1244912460. https : / / proceedings . neurips . cc / paper \_ files / paper / 2020 / file / 92d1e1eb1cd6f9fba3227870bb6d7f07-Paper.pdf .
136. Li, X. et al. Multilingual Speech Translation from Efficient Finetuning of Pretrained Models in Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics and the 11th International Joint Conference on Natural Language Processing (Volume 1: Long Papers) (Association for Computational Linguistics, Online, Aug. 2021), 827-838. https://aclanthology.org/ 2021.acl-long.68.
137. Post, M. A Call for Clarity in Reporting BLEU Scores in Proceedings of the Third Conference on Machine Translation: Research Papers (Association for Computational Linguistics, Belgium, Brussels, Oct. 2018), 186-191. https:// www.aclweb.org/anthology/W18-6319.
138. Li, X. et al. Multilingual Speech Translation from Efficient Finetuning of Pretrained Models in Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics and the 11th International Joint Conference on Natural Language Processing (Volume 1: Long Papers) (Association for Computational Linguistics, Online, Aug. 2021), 827-838. https://aclanthology.org/ 2021.acl-long.68.
139. McAuliffe, M., Socolof, M., Mihuc, S., Wagner, M. &amp; Sonderegger, M. Montreal forced aligner: Trainable text-speech alignment using kaldi. in Interspeech 2017 (2017), 498-502.
140. Kim, J., Kim, S., Kong, J. &amp; Yoon, S. Glow-TTS: A generative flow for textto-speech via monotonic alignment search. Advances in Neural Information Processing Systems 33, 8067-8077 (2020).

141. Gu, J., Bradbury, J., Xiong, C., Li, V. O. &amp; Socher, R. Non-autoregressive neural machine translation. arXiv preprint arXiv:1711.02281 (2017).
142. Lee, J., Mansimov, E. &amp; Cho, K. Deterministic Non-Autoregressive Neural Sequence Modeling by Iterative Refinement in Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing (eds Riloff, E., Chiang, D., Hockenmaier, J. &amp; Tsujii, J.) (Association for Computational Linguistics, Brussels, Belgium, 2018), 1173-1182. https://aclanthology.org/D181149.
143. Ma, X., Zhou, C., Li, X., Neubig, G. &amp; Hovy, E. FlowSeq: Non-Autoregressive Conditional Sequence Generation with Generative Flow in Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLPIJCNLP) (eds Inui, K., Jiang, J., Ng, V. &amp; Wan, X.) (Association for Computational Linguistics, Hong Kong, China, Nov. 2019), 4282-4292. https: //aclanthology.org/D19-1437.
144. Gong, S., Li, M., Feng, J., Wu, Z. &amp; Kong, L. DiffuSeq: Sequence to Sequence Text Generation with Diffusion Models in International Conference on Learning Representations, ICLR (2023).
145. Reid, M., Hellendoorn, V. J. &amp; Neubig, G. Diffuser: Discrete diffusion via editbased reconstruction. arXiv preprint arXiv:2210.16886 (2022).
146. Qian, L. et al. Glancing Transformer for Non-Autoregressive Neural Machine Translation in Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics and the 11th International Joint Conference on Natural Language Processing (Volume 1: Long Papers) (eds Zong, C., Xia, F., Li, W. &amp; Navigli, R.) (Association for Computational Linguistics, Online, Aug. 2021), 1993-2003. https://aclanthology.org/2021.acl-long.155.
147. Lee, J. &amp; Watanabe, S. Intermediate loss regularization for CTC-based speech recognition in ICASSP 2021-2021 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP) (2021), 6224-6228.
148. Seamless Communication et al. SeamlessM4T-Massively Multilingual &amp; Multimodal Machine Translation. arXiv 2308.11596. https://arxiv.org/abs/2308. 11596 (2023).

## List of Supplementary Tables

|   1 | Options for 2-stage and 3-stage cascaded systems for S2TT and S2ST. These cascades pair Whisper ASR models [20] with NLLB's T2TT models [6]. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                                  |   34 |
|-----|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------|
|   2 | The list of automatic and human evaluation metrics used in this work.                                                                                                                                                                                                                                                             |   36 |
|   3 | SeamlessM4T languages. We display the language code, name, subgroup, and script, as well as the speech resource level and the language is supported as a source or a target in the speech text modalities. Zero-shot here refers to S2TT or S2ST tasks with the language in question as source. . . . . . . . . . . . . . . . . . |      |
|     | family, whether and/or                                                                                                                                                                                                                                                                                                            |   40 |

|   4 | F1 micro and macro average for the considered LID systems over all SeamlessM4T languages and the intersection of supported languages across models. Dashes are used for models that do not support the full 100 scope. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                                                                                                                                                                                                                                                                        |   42 |
|-----|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------|
|   5 | F1 micro average and coverage across 100 languages for the LID100 system with and without filtering. . . . . . . . . . . . . . . . . . . . .                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |   43 |
|   6 | Average performance on Flores devtest set over the 200 NLLB lan- guages and 89 languages supported by COMET: translation spBLEU and COMET scores, auto-encoding spBLEU. . . . . . . . . . . . . . .                                                                                                                                                                                                                                                                                                                                                                                                                                               |   46 |
|   7 | Comparison of similarity search results (error rates) on all 200 Flores languages, and limited to the intersection of 98 languages on which each model has been trained on. . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                                                                                                                                                                                                                                                                                                                                       |   47 |
|   8 | Statistics on speech encoders and amount of mined data. Sen2Txx, Sxx2Ten, and SxxSen correspond to English speech paired with for- eign text, foreign speech paired with English Text, and foreign Speech paired with English speech, respectively. Dashes are unmined directions. We provide the amount of raw audio data for mining and the amount of human-provided ASR transcripts to train the speech encoders. The speech encoders are evaluated for S2TT using BLEU on the Fleurs test set. Our model performs zero-shot S2TT. Finally, the last three columns provide the amount of mined data. . . . . . . . . . . . . . . .             |   48 |
|   9 | Multitasking X2T results. Performance of SeamlessM4T-Large on CoVoST 2 S2TT and Fleurs ASR compared to SOTA direct translation models. For Fleurs ASR, we report the average normal- ized WER over languages supported by both SeamlessM4T and Whisper Large (WL) (Fleurs-77). For MMS, we report the results of the MMS-L1107-CCLM-LSAH model (CTC-based with an n-gram language model for each language) on Fleurs-54. For a direct com- parison with Whisper-Large-v3, we average over whisper's reported WER scores on Fleurs-60. To compare all ASR models on a common benchmark, we included averages over Fleurs-41. . . . . . . . . . . . |   53 |
|  10 | S2TT results with spBLEU and Blaser 2.0 we report here the performance of Whisper-Large-v2 and SeamlessM4T-Large measured with spBLEU & Blaser 2.0. Note that unlike BLEU scores copied from [20], the spBLEU and Blaser 2.0 scores are based on our evaluation using https://github.com/openai/whisper with the recommended decoding options. . . . . . . . . . . . . . . . . . . . . .                                                                                                                                                                                                                                                          |   54 |
|  11 | S2ST results with ASR-BLEU and Blaser 2.0 we report here the performance of SeamlessM4T-Large and SeamlessM4T- Medium measured with ASR-BLEU & Blaser 2.0. . . . . . . . . .                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |   54 |

|   12 | Statistics of ASR and S2TT data used to train our SeamlessM4T model. We list the data size in hours of speech between primary (P) i.e., open-source S2TT and pseudo-labeled ASR data, and mined (M). For each language we distinguish between eng-X for translating from English into that language, and X-eng for translating into English. We qualify as high-resource, languages with more than 1000 hours of supervision. Languages with between 500 and 1000 hours are dubbed medium-resource, and languages with less than 500   |    |
|------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----|
|      | hours are low-resource. If a language is not supervised during the 1+2 stages of finetuning then it is evaluated as zero-shot. . . . . . . . . . . . . . . . Statistics of S2ST data used to train our SeamlessM4T model. We list the                                                                                                                                                                                                                                                                                                  | 57 |
|   13 | data size in hours of speech. For each language we distinguish between Eng- X for translating from English into that language, and X-Eng for translating into English. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                                                                                                                                                                                                               | 58 |
|   14 | A comparison of multilingual speech pre-training in state-of-the-art ASR and S2TT models. †Estimated from the part of data that has language information. . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                                                                                                                                                                                                                                        | 59 |
|   15 | Ablation on w2v-BERT variants and training data scaling. . . . . . . .                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 60 |
|   16 | Hours of data in the ablation dataset for the tasks of ASR, S2TT and S2ST, split between eng-X and X-eng when relevant. For each task, we report hours of training data between primary and mined. By default, S2TT mined data is capped at 400 hours in X-eng and at 200 hours in eng-X. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                                                                                        | 61 |
|   17 | Ablations on multitasking objectives in three different data setups. Results are reported on Fleurs dev. . . . . . . . . . . . . . . . . . .                                                                                                                                                                                                                                                                                                                                                                                           | 62 |
|   18 | Ablations on the use of mined data. Results are reported on Fleurs dev. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                                                                                                                                                                                                                                                                                                      | 63 |
|   19 | Ablations on pre-training UnitY's T2U and use of S2ST mined data. Results are reported on Fleurs dev. † 80K and 50K correspond to 2 epoches in the two different data settings. . . . . . . . . . . . . . . . .                                                                                                                                                                                                                                                                                                                        | 64 |
|   20 | Summary of evaluations: languages, modalities, models, and protocols used in human evaluations. Modalities and protocols in parentheses are not presented in this paper but will be shared in a later update. The 23 non-English languages evaluated are: Bengali, Catalan, Dutch, Finnish, French, German, Hindi, Indonesian, Italian, Japanese, Korean, Mandarin Chinese, Modern Standard Arabic, Portuguese, Romanian, Russian, Spanish, Swahili, Telugu, Thai, Turkish, Urdu, and Vietnamese.                                      | 71 |
|   21 | Spearmans ρ correlation coefficients of different automatedmetrics com- pared to XSTS at the language level, using bootstrap resamplings to obtain 95% CIs. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                                                                                                                                                                                                                              | 71 |
|   22 | Language-direction level aggregate XSTS scores for both S2TT and S2ST tasks. The models are abbreviated for space considerations: "C" denotes the Cascaded models, "R" is a human reference, "S1" refers to SeamlessM4T-Large and "S2" refers to SeamlessM4T-Large v2. Bold scores denote the highest score, underlines denote the highest score ignoring human reference. . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                           | 72 |

|   23 | Language-direction level aggregate MOS scores for each MOS aspect and model evaluated. The models are abbreviated for space considera- tions: "C" denotes the Cascaded models, "R" is a human reference, "S1" refers to SeamlessM4T-Large and "S2" refers to SeamlessM4T- Large v2. Bold scores denote the highest score, underlines denote the highest score ignoring human reference. . . . . . . . . . . . . . . . . .   |   73 |
|------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------|
|   24 | Summary of XSTS and MOS performance for each evaluated model. Bold scores denote the highest aggregate score observed in its category, underlined scores denote the highest aggregate score observed in its category that is not a human reference. . . . . . . . . . . . . . . . . .                                                                                                                                       |   74 |
|   25 | Evaluation results of model robustness against vocal style vari- ations. We report test average by-group mean chrF (chrFMS) and test average by-group coefficient of variation on chrF (CoefVarMS) for X- eng S2TT and ASR on Fleurs (77 and 78 source languages respectively which have at least 40 content groups). . . . . . . . . . . . . . . . . . .                                                                   |   74 |
|   26 | List of language codes in the bias evaluation experiments, organized by task and language direction. . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                                                                                                                                                                                        |   75 |
|   27 | Results for S2TT and S2ST averaged across several directions at the intersection of systems available (in parentheses) that add toxicity. ETOX is ASR-ETOX in the case of speech outputs. Baseline corre- sponds to Whisper-Large-v2 for S2TT X-eng; Whisper-Large-v2 + NLLB-3.3B for S2TT X-eng; Whisper-Large-v2 + YourTTS for S2ST X-eng. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                    |   76 |
|      | of Supplementary Figures                                                                                                                                                                                                                                                                                                                                                                                                    |      |
|    1 | SONAR architecture. . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                                                                                                                                                                                                                                                                 |   44 |
|    2 | Workflow of the Sonar encoding and mining processes. . . . . . . . .                                                                                                                                                                                                                                                                                                                                                        |   45 |
|    3 | Overview of SeamlessM4T. (1) shows the pre-trained models used when fine-tuning multitasking UnitY. (2) outlines multitasking UnitY with its two encoders, text decoder, T2U encoder-decoder, and the supporting vocoders for synthesizing output speech in S2ST. . . . . . .                                                                                                                                               |   45 |
|    4 | S2TT Fleurs X-X results. We evaluate X-X directions from Fleurs and average spBLEU scores. For a given target text language, we average scores over 100 source languages. . . . . . . . . . . . . . .                                                                                                                                                                                                                       |   55 |
|    5 | Statistics of ASR and X-eng S2TT data used to train our Seam- lessM4T model. We show the data size in hours of speech (log-scale) between ASR, S2TT primary and mined. Languages are sorted in ascending resource-level. For numerical statistics see Supplementary table 12 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                          |   55 |
|    6 | Statistics of S2ST data used in Stage3 of training SeamlessM4T model. We show the data size in hours of speech between primary and mined. Languages are sorted in ascending resource-level. For numerical statistics see Supplementary table 13 . . . . . . . . . . . . . . . . . . .                                                                                                                                       |   56 |

- 7 Evaluation results of model robustness against background noise. We report average test BLEU and test WER over four languages (three language families) for X-eng S2TT and ASR on Fleurs with low-to-high input noise level (high-to-low SNR). Simulated noises are sampled from MUSAN [76] on the "noise" and "music" categories.

75

- 8 Added toxicity for X-eng and eng-X in Fleurs with ETOX and ASR-ETOX. The figure shows the outputs with added toxicity per language for Baseline, SeamlessM4T-Large, SeamlessM4T-Large v2 and SeamlessM4T-Large v2 + MinTox. Baseline corresponds to Whisper-Large-v2 for S2TT X-eng; Whisper-Large-v2 + NLLB3.3B for S2TT X-eng; Whisper-Large-v2 + YourTTS for S2ST X-eng. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 77
- 9 Added toxicity for eng-X for S2TT (top) and S2ST (bottom) in HolisticBias with ETOX and ASR-ETOX. The figure shows the number of outputs with added toxicity (above 0.05%) per language for baseline, SeamlessM4T-Large, SeamlessM4T-Large v2 and SeamlessM4T-Large v2 + MinTox systems. Baseline corresponds to Whisper-Large-v2 for S2TT X-eng; Whisper-Large-v2 + NLLB3.3B for S2TT X-eng; Whisper-Large-v2 + YourTTS for S2ST X-eng. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 77
- 10 Added toxicity for X-eng and eng-X in Fleurs S2TT and S2ST with MuTox. The figure shows the number of outputs with added toxicity per language for baseline, SeamlessM4T-Large, SeamlessM4T-Large v2 and SeamlessM4T-Large v2 + MinTox systems. Baseline corresponds to Whisper-Large-v2 for S2TT X-eng; Whisper-Large-v2 + NLLB-3.3B for S2TT X-eng; Whisper-Large-v2 + YourTTS for S2ST X-eng. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 78
- 11 Added toxicity for eng-X for S2TT and S2ST in HolisticBias with MuTox. The figure shows the number of outputs with added toxicity per language for baseline, SeamlessM4T-Large v2, SeamlessM4TLarge v2 + MinTox systems. Baseline corresponds to WhisperLarge-v2 for S2TT X-eng; Whisper-Large-v2 + NLLB-3.3B for S2TT X-eng; Whisper-Large-v2 + YourTTS for S2ST X-eng. . . 78
- 12 Left: The chrF points difference between masculine and feminine forms for eng-X S2TT using English speech as source and X text translation (masculine or feminine) as reference. Right: The ASR-chrF points difference between masculine and feminine forms for eng-X S2ST using English speech as source and X text translation (masculine or feminine) as reference. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 79
- 13 (left) The chrF points difference between masculine and feminine for X-eng S2TT using X speech synthesized by the masculine or feminine version of the text and English text as a reference. (right) The ASRchrF points difference between masculine and feminine forms for X-eng S2ST using X speech synthesized by the masculine or feminine version of text and English text as reference. . . . . . . . . . . . . . . . . . . . 79

- 14 (left) The supervised Blaser 2.0 points difference between masculine and feminine forms for eng-X S2ST using English speech as the source and X text translation (masculine and feminine) as reference. The results are averaged from three experiments. (right) The supervised Blaser 2.0 points difference for X-eng S2ST using X speech synthesized by the masculine or feminine version of text and English text as reference. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 80