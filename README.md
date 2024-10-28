# TKGT
This is the official code and data repository for the paper TKGT.

# Prepare
Before starting, make sure that you have :
- Installed vllm in a v-env called vllm and download below interface for fast and parallel inference, 
```bash
cd /TKGT/Hybird_RAG/predict
git clone git@github.com:jiangpw41/LLMInferenceServer.git
```
- Installed llama-factory in a v-env called llama_factory for fine-tuning.
- Installed nltk toolkit in a v-env called tkgt for first-stage and download nltk package under root dir
- Installed env2.txt in a v-env called tkgt2 for second stage.
- Downloaded a LLM (like chatglm3/4-6b) for Q&A
- Downloaded embedding models for embedding and retreving
  - "roberta-large" under TKGT/Hybird_RAG/evaluation for bert-score evaluation.
  - "sentence-transformers/all-MiniLM-L6-v2" and "cross-encoder/ms-marco-MiniLM-L-6-v2" under TKGT/Hybird_RAG/retriever 


# Dataset
Our project refers to a total of five datasets, four of which are from previous text-to-table tasks (Rotowire, e2e, wikibio, wikitabletext) and the rest one is proposed by us (the CPL). In addition, the data will be stored in two folders, "raw" and "data", respectively, under the root directory of the project. The former contains four copies of the original data (Rotowire, e2e, wikibio, wikitabletext), the latter includes three processed datasets (CPL, Rotowire, e2e) that can be directly used in this project.
## "Raw"
We use the processed four datasets by https://github.com/shirley-wu/text_to_table , which can be download at https://drive.google.com/file/d/1zTfDFCl1nf_giX7IniY5WbXi9tAuEHDn/view. You need to download this .zip file, unzip it under project root, and rename it as "raw".

As for the CPL dataset, as the original data involves privacy, we only provide processed dataset in "data".

## "Data"
There are three datasets in table form stored in the "data" directory from total five, and the remaining two (wikibio, wikitabletext) have no limited table fields. For details, please refer to the readme file in the "data" directory.

# Mixed_IE
The method of TKGT's first stage, which include paradigms of regulation, statistics, and DL.

# KGs
The semi-automatically constructed Knowledge Graph of datasets by human experts with the help of Mixed_IE. Based on KGs schema, prepare prompt list and ft data in batch.

# Hybird-RAG
Using
- rule-based (prior structural knowledge and regular matching) method and 
- statistics-based (word frequency)
- semantic-based (similarity)