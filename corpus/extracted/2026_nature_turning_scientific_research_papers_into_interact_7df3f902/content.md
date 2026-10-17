<!-- source: 2026-Nature-Turning scientific research papers into interactive AI agents.pdf -->
<!-- source_pdf: D:\2026-AI4S\2026-Nature-Turning scientific research papers into interactive AI agents.pdf -->
<!-- pages: 2 ; extracted_by: docling 2.140.0 -->

## Research briefing

## Turning scientific research papers into interactive AI agents

Scientific knowledge is mostly stored in static papers. An automated framework called Paper2Agent can now transform each paper into an active artificial intelligence agent - a virtual corresponding author that answers questions, applies the paper's methods to new data, and collaborates with other paper agents. This makes research easier to reproduce, reuse and extend.

## This is a summary of:

Miao, J. et al. Reimagining research papers as interactive and reliable AI agents. Nature https://doi.org/10.1038/s41586-026-11044-y (2026).

## Cite this as:

Nature https://doi.org/10.1038/d41586-02602880-z (2026).

## The problem

For centuries, research papers have served as science's durable but static unit of record, preserving methods, findings and interpretations. Using this knowledge, however, requires researchers to decipher methods, reconstruct workflows, run code and generate data, and determine whether the results generalize to different settings. Large language models have made papers easier to navigate - a reader can download a PDF and use a chatbot to ask questions about it - but explaining existing knowledge is not the same as using it to generate fresh knowledge. A conventional chatbot cannot easily apply a paper's methods to new data, or combine the methods of one study with the data from another, limiting the reproducibility and reuse of scientific work. But what if a paper could be transformed into an AI agent that explains the study, executes its methods, applies them to new questions, and helps to generate further findings?

## The solution

We developed Paper2Agent, a framework that creates an agentic representation of each paper as a model context protocol (MCP) server (Fig. 1); MCP is an existing open standard that gives diverse AI systems a common interface to tools, data and workflows 1 . Each paper's server packages three components: executable tools that implement its methods; resources such as its text and data sets; and prompts that specify multistep scientific workflows.

We have automated the creation of paper MCPs. A team of specialized AI agents operates in an iterative build-test-repair loop, reading the paper and its code repository, configuring the software environment, running tutorials, converting useful methods into tools, and validating each tool by reproducing the paper's examples. A large language model can then connect to the MCP to form a paper agent - a virtual corresponding author that explains the work, reproduces its analyses and applies its methods to new data in response to plain-language requests.

When applied to AlphaGenome 2 (an AI model that predicts how DNA variants affect gene regulation), Paper2Agent created an AlphaGenome agent with 22 validated tools, all in under one hour and without human intervention. When asked how a DNA variant might affect a particular gene in a given cell type, the agent selects the appropriate tool, runs the model and explains the result. When faced with scientific questions that required AlphaGenome analysis, it achieved

98.7-100% accuracy and completed tasks two to four times faster than did a generalpurpose coding agent given direct access to the repository, which achieved only 78.7-82.7% accuracy. Paper agents can also collaborate autonomously, combining methods and data across studies. Working together, the AlphaGenome agent and agents built from two gene-perturbation studies 3,4 identified GPR137 as a potential causal gene for psoriasis through an analysis proposed by the agent and not reported previously.

## The implications

Paper2Agent shows that a static paper can acquire an operational layer through which its methods can be inspected, executed and reused. Paper2Agent serves complementary functions: its conversion process audits whether the work is sufficiently documented to be 'agentified', and the resulting agent enables follow-on research by applying its methods to fresh data, integrating resources from other studies and addressing innovative questions. The availability of such an agent could therefore complement existing standards for code and data availability.

When we applied Paper2Agent to 110 papers spanning computational biology, machine learning, econometrics and astrophysics, it successfully converted 84 (76%) into working agents. The remaining 26 papers could not be converted because of practical barriers, including unreleased code, missing data or model files, broken software environments and scripts that depended on unavailable data sets. Agentification can therefore serve as a practical diagnostic of computational reproducibility: success indicates that the materials are explicit and complete enough to reconstruct and test, whereas failure exposes details that were left implicit.

Paper2Agent converts scientific knowledge from static and passive artefacts into dynamic virtual authors. Our next goal is to build a global community of millions of proactive paper agents that collaborate across disciplines, connecting methods, data sets and findings to address questions that no paper, researcher or agent could tackle alone.

Jiacheng Miao and James Zou are at Stanford University, Stanford, California, USA.

## EXPERT OPINION

<!-- image -->

The automated conversion of research papers into interactive MCP servers and conversational agents is a novel systems-level contribution. Although the broader idea of executable or reproducible research has a long history, Paper2Agent's emphasis on automated tool extraction, structured MCP interfaces and agent integration is a meaningful extension.

Paper2Agent could have a high practical impact by reducing barriers to method adoption and enabling agentic workflows in computational sciences." (CC BY 4.0)

Su-In Lee and Soham Gadgil are at the University of Washington, Seattle, Washington, USA.

## FIGURE

<!-- image -->

Enabling scientific discovery through paper agents

Figure 1 | Moving from research paper to interactive AI agent. Paper2Agent analyses a paper and its codebase to build a remote model context protocol (MCP) server (a standardized interface through which artificial-intelligence systems use software). This is done through Paper2MCP, which is the first step of Paper2Agent. The server creates or identifies tools (executable functions that implement the paper's methods, indicated here by Tool 1 and Tool K), resources (the manuscript, data and supplements) and prompts (step-by-step workflows for analysis). Connecting a large language model (LLM) to the MCP, through a platform such as Hugging Face, creates a paper-specific agent that can answer questions, reproduce analyses and apply the methods to fresh data through natural-language requests. Miao, J. et al./Nature (CC BY-NC-ND 4.0).

## BEHIND THE PAPER

For years, we have felt that static research papers are not the best way to represent scientific knowledge. The growing capabilities of agentic AI create an opportunity to reimagine papers as interactive virtual authors. A key challenge is that papers are written for humans: simply giving a PDF to a large language model often causes it to miss important insights about how the methods, code or data actually work. We wanted the virtual author to gain hands-on experience with the paper, rather than simply read it.

Our key insight was to have the AI set up a virtual environment in which it can run the code, test the methods and reproduce results from the paper. Through this iterative process, the system builds the paper MCP, and learns how to robustly reuse and adapt the original methods and results. We hope that paper agents can ultimately reshape how scientific knowledge is shared, used and extended.

J.Z.

## REFERENCES

1. Anthropic. https://www.anthropic.com/ news/model-context-protocol (2024).
2. Avsec, Ž. et al. Nature 649, 1206-1218 (2026).
3. Zhu, R. et al. Preprint at bioRxiv https://doi.org/10.64898/2025.12.23.696273 (2025).
4. Ho, C.-H. et al. Nature Genet. 57, 2536-2545 (2025).