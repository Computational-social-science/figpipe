## Project Overview

This repository contains the code and data pipeline for the research paper, "The Growing Concentration of National Influence in Global Science and its Impact on Future Research." The project investigates the dynamics of scientific influence by constructing and analyzing international networks from the [OpenAlex](https://openalex.org/) dataset. The core of this research is to differentiate and measure two forms of scientific influence:

1.  **Attributional Influence**: The conventional measure of influence based on citations. This reflects the acknowledgment and building upon of prior knowledge.
2.  **Discursive Influence**: A more nuanced measure that captures when a scientific paper not only cites a previous work but also incorporates the same key terms or concepts in its title or abstract. This signifies a direct engagement with and shaping of the research conversation.

By analyzing these two types of influence, the project demonstrates that influence is increasingly and disproportionately concentrated within a small group of "core" countries, which shapes the global research agenda and has significant implications for scientific equity and innovation.

## Data Source & Prerequisites

* **Data Source**: The analysis is based on a static snapshot of the OpenAlex database (version dated December 1, 2023), which contains metadata for nearly 240 million scientific works.
* **Platform**: The data pipeline is designed to be executed using **Amazon Web Services (AWS)**. The raw OpenAlex snapshot is assumed to be stored in an S3 bucket and queried using **AWS Athena**.
* **Prerequisite - Step 0 (Initial Data Setup)**: Before running this pipeline, the raw OpenAlex data must be processed into queryable Athena tables. The user is responsible for creating an initial table (referred to as `mag_staging.project_phoenix_text_data` in the scripts) that contains the work ID, title, abstract, year, and author-country affiliations for each publication.

## Analytical Pipeline

The workflow is executed in sequential steps. Each step consists of one or more scripts that process the data, leading to the final network edgelists used in the paper's analysis.

### Step 0: Create Initial Text and Metadata Table

* **Script**: `Step_X0_SQL_Create_Text_Data.txt`
* **Description**: This is the first script to be executed. It runs an SQL query in AWS Athena to process the raw OpenAlex data. It joins multiple tables (`semantic_works`, `works_concepts`, `works_authorships`, etc.) to create a single, unified table containing the necessary text data (title and abstract), publication year, work ID, concept ID, and formatted author-country affiliations for all relevant articles in the dataset.
* **Input**: Raw OpenAlex tables hosted in AWS Athena.
* **Output**: An Athena table named `mag_staging.project_phoenix_text_data` stored in an S3 location, which serves as the primary input for the next step.

### Step 1: Extract Key Terms from Publications

* **Script**: `Step_X1_Python_Extracted_Terms.py`
* **Description**: This script uses an ensemble of four Python-based key phrase extractors (`TextRank`, `Multi-RAKE`, `YAKE!`, and `Textacy`) to identify and extract key terms and phrases from the titles and abstracts of publications. The script is designed to be run in parallel for different scientific fields by passing a concept ID as a command-line argument.
* **Input**: An Athena table (`mag_staging.project_phoenix_text_data`) containing publication text and metadata.
* **Output**: A series of compressed pickle files (`.pbz2`) for each field, containing dictionaries that map terms to the work IDs and publication years in which they appear, and work IDs to their associated author countries.

### Step 2: Extract Wikidata Concepts

* **Script**: `Step_X2_SQL_Extracted_Wikidata_Concept_IDs.txt`
* **Description**: This Athena SQL query identifies scientific concepts in OpenAlex that have an associated Wikidata ID. It gathers all papers associated with these concepts, along with their publication years and origin countries, to supplement the NLP-extracted terms from Step 1.
* **Input**: The standard OpenAlex tables in Athena (e.g., `works_concepts`, `concepts`, `semantic_works`).
* **Output**: A CSV file (`INPUT_SQL_Extracted_Wikidata_Concept_IDs.csv`) containing Wikidata-verified concepts and their associated papers.

### Step 3: Aggregate and Filter Terms

* **Script**: `Step_X3_Python_All_Terms_across_Fields.py`
* **Description**: This script aggregates the outputs from Step 1 and Step 2. It filters the combined list of terms based on criteria outlined in the paper: terms must first appear in or after 1990 and be present in at least ten different papers. The script then generates definitive lists of work IDs that will be used to find citations.
* **Input**:
    * All `.pbz2` dictionaries produced in Step 1.
    * The `INPUT_SQL_Extracted_Wikidata_Concept_IDs.csv` file from Step 2.
* **Output**:
    * `INPUT_Python_OpenAlex_All_Work_IDs_Extracted_and_WikiData_Terms_[date].csv`: A comprehensive list of all work IDs containing the final filtered terms.
    * `INPUT_Python_OpenAlex_Work_IDs_WikiData_Terms_for_Country_Affiliation_[date].csv`: A specific list of work IDs from Wikidata concepts needed for a country lookup.
    * `INPUT_Python_OpenAlex_Extracted_Terms_and_Wikidata_Dictionary_[date].pbz2`: A master dictionary containing the final term-to-paper mappings, used in subsequent analysis steps.

### Step 4: Find Citing Papers via Athena

* **Scripts**:
    * `Step_X4A_Upload_Work_IDs_to_Athena.pdf` (Instructional Guide)
    * `Step_X4B_Upload_Work_IDs_to_Athena.txt` (SQL)
    * `Step_X4C_Upload_Wikidata_Work_IDs_to_Athena.txt` (SQL)
* **Description**: This is a multi-part data retrieval step performed in AWS.
    1.  **Upload**: The two CSV files generated in Step 3 are uploaded to an S3 bucket. The PDF provides a general guide for this process.
    2.  **Create Tables**: The `CREATE EXTERNAL TABLE` commands in `Step_X4B` and `Step_X4C` are run in Athena to make the uploaded CSVs queryable.
    3.  **Query Citations**: The `SELECT` query in `Step_X4B` joins the newly created table of work IDs with OpenAlex's citation data (`works_referenced_works`) to find all papers that *cite* the "term papers". It also fetches the publication year and country data for these citing papers.
    4.  **Query Countries**: The query in `Step_X4C` retrieves country affiliations for the Wikidata-specific work IDs.
* **Input**: The CSV files generated in Step 3, uploaded to S3.
* **Output**:
    * `INPUT_Python_OpenAlex_Citing_IDs_for_Extracted_and_WikiData_Terms_[date].csv`: The primary input for Step 5, containing a mapping of each term paper to all the papers that cite it.
    * `INPUT_Python_OpenAlex_Work_IDs_WikiData_Terms_[date].csv`: A supplementary file containing country information for Wikidata-based papers.

### Step 5: Construct Influence Networks

This is the final analytical stage, where the concepts of discursive and attributional influence are operationalized to build country-to-country network edgelists.

* **Step 5A: Discursive Influence**
    * **Script**: `Step_X5A_Python_Create_Multi-Paper_Discursive_Influence_Edgelists_LATEST.py`
    * **Description**: This script implements the core logic for identifying discursive influence. For each "term paper," it finds all citing papers within a 10-year window that also use the same term in their title or abstract. It then aggregates these connections into a yearly, country-to-country directed network.
    * **Input**: The master dictionary from Step 3 and the citation data CSV from Step 4.
    * **Output**: `OUTPUT_Python_MultiPaper_Discursive_Influence_[date].csv`.

* **Step 5B: Attributional Influence**
    * **Script**: `Step_X5B_Python_Create_Multi-Paper_Attributional_Influence_Edgelists_LATEST.py`
    * **Description**: This script identifies attributional influence. It processes the same citation data as Step 5A but defines attributional links as any citation that is *not* a discursive link, ensuring the two measures are mutually exclusive. It then aggregates these connections into a yearly, country-to-country directed network.
    * **Input**: The master dictionary from Step 3, the citation data from Step 4, and an intermediate file from Step 5A that lists the discursive links to be excluded.
    * **Output**: `OUTPUT_Python_MultiPaper_Attributional_Influence_[date].csv`.

* **Alternative Analysis Script**
    * **Script**: `Step_X5_Python_Create_Diffusion_Citation_and_Origin_Edgelists_LATEST.py`
    * **Description**: This file represents an earlier or alternative version of the analysis. It computes similarity indices (Jaccard, Cosine, Overlap) between citing and diffused paper sets and generates simpler edgelists for diffusion, citation, and origin. This script is not part of the primary pipeline for the paper but is included for context.

### Step 6: Final Analysis and Figure Generation

* **Script**: `Step_X6_R_Relative_Influence_Figures_LATEST.R`
* **Description**: This R script is the final step in the pipeline. It reads the discursive and attributional influence edgelists generated in Step 5 and performs the main statistical analyses for the paper. It calculates the core metric, "Relative Influence," by taking the difference between scaled discursive and attributional influence scores. The script then calculates network statistics like Gini coefficients and country centralities, runs MR-QAP models, and generates all the primary figures and tables presented in the manuscript, including time-series plots, dyad comparisons, and regional arc diagrams.
* **Input**:
    * `OUTPUT_Python_MultiPaper_Discursive_Influence_[date].csv`
    * `OUTPUT_Python_MultiPaper_Attributional_Influence_[date].csv`
    * `OUTPUT_Python_MultiPaper_Number_of_Cites_per_Influencer_Paper_Attributional_Influence_[date].csv`
* **Output**: All figures (as PDF files) and tables used in the research paper.

### Step 7: Analyze National Research Agenda Mimicry
* **Script**: `Step_NHB_RR1_X1_National_Signature_Replacement.py`
* **Description**: This script performs the "mimicry" analysis detailed in the manuscript to test whether the concentration of influence displaces local research agendas. For each country and year, it creates a "national research agenda" represented by a term-frequency vector of all terms published by that country's authors. It then calculates a "mimicry ratio," which compares how similar a country's current research agenda is to an influential country's past (5-year average) agenda, relative to its own past agenda, using cosine similarity. 
* **Input**:
    * The primary citation data from Step 4 (INPUT_Python_OpenAlex_Citing_IDs_for_Extracted_and_WikiData_Terms_[date].csv).
    * The master term and country dictionaries from Step 3. An intermediate file containing discursive influence mappings (INPUT_Python_Discursive_Influence_Dictionary_[date].pkl).
* **Output**: OUTPUT_Python_HNB_RR1_National_Signature_Influence_[date].csv, which contains the final mimicry ratio scores used to generate Figure 7 in the paper. 

## File Manifest

* `Step_X0_SQL_Create_Text_Data.txt`
* `Step_X1_Python_Extracted_Terms.py`
* `Step_X2_SQL_Extracted_Wikidata_Concept_IDs.txt`
* `Step_X3_Python_All_Terms_across_Fields.py`
* `Step_X4A_Upload_Work_IDs_to_Athena.pdf`
* `Step_X4B_Upload_Work_IDs_to_Athena.txt`
* `Step_X4C_Upload_Wikidata_Work_IDs_to_Athena.txt`
* `Step_X5_Python_Create_Diffusion_Citation_and_Origin_Edgelists_LATEST.py`
* `Step_X5A_Python_Create_Multi-Paper_Discursive_Influence_Edgelists_LATEST.py`
* `Step_X5B_Python_Create_Multi-Paper_Attributional_Influence_Edgelists_LATEST.py`
* `Step_X6_R_Relative_Influence_Figures_LATEST.R`
* `Step_NHB_RR1_X1_National_Signature_Replacement.py`

## Citation

If you use this code or methodology in your research, please cite the original paper. All code and metadata constructed for this project are also available on the Harvard Dataverse at: [https://doi.org/10.7910/DVN/ZSZRKK](https://doi.org/10.7910/DVN/ZSZRKK).