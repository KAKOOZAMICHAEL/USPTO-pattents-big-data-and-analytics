# USPTO Patent Analytics Dataset Details

This document explains the structure, context, and contents of the data used in the **Global Patent Intelligence Pipeline**. 

The pipeline is designed to ingest data published by the **United States Patent and Trademark Office (USPTO)**, specifically utilizing bulk data releases provided by PatentsView (a USPTO-supported data initiative).

## What Does This Data Represent?

At a high level, this dataset represents **granted patents**. When an inventor or a company files for a patent and it is officially granted, it contains rich metadata:
- **Who** invented it (Inventors)
- **Who** owns the rights to it (Assignees / Companies)
- **What** it is about (Abstract and Titles)
- **How** it is categorized technologically (CPC - Cooperative Patent Classification)
- **When** it was filed and published (Dates)

For testing purposes, we generated a **mock dataset** of 500 rows that mathematically mimics a subset of the real `200k` row dataset.

---

## File-by-File Breakdown

The data is split across 5 normalized Tab-Separated Value (TSV) files to reduce redundancy. 

### 1. `g_patent_200k.tsv`
This is the core table representing the patent document itself.
- **`patent_id`**: The unique identifier for the granted patent (e.g., `P000001`).
- **`title`**: The official, legal title of the invention.
- **`filing_date`**: The date the patent application was originally submitted to the USPTO.
- **`publication_date`**: The date the patent was officially granted and published.
- **`main_classification`**: The primary technological category assigned to the patent (e.g., `G06F` for Electrical Computers/Data Processing).

### 2. `g_inventor_200k.tsv`
This file links patents to the human beings who actually invented the technology. A single patent can have multiple inventors.
- **`patent_id`**: Foreign key linking to the patent.
- **`inventor_id`**: A unique ID for the specific inventor occurrence.
- **`disambig_inventor_id`**: In real USPTO data, names are often misspelled across different patents. This field represents the "cleaned" or "disambiguated" true name of the inventor.
- **`disambig_country`**: The standardized country code where the inventor resides (e.g., `US`, `JP`, `DE`).

### 3. `g_assignee_200k.tsv`
This file links patents to the entities (corporations, universities, or governments) that legally own the patent rights.
- **`patent_id`**: Foreign key linking to the patent.
- **`assignee_id`**: A unique identifier for the company/assignee.
- **`disambig_assignee_organization`**: The standardized, cleaned name of the organization (e.g., "Tech Corp", "State University"). Our analytics pipeline uses keyword matching on this field to classify patents as either *Academic* or *Corporate*.

### 4. `g_abstract_200k.tsv`
This file contains the raw text summaries of the inventions.
- **`patent_id`**: Foreign key linking to the patent.
- **`patent_abstract`**: A paragraph (typically 100-250 words) describing the technical problem and the proposed solution. *In our pipeline, this text is used to train a Machine Learning model (Logistic Regression over TF-IDF vectors) to automatically predict what category an invention belongs to.*

### 5. `g_cpc_200k.tsv`
This file contains the Cooperative Patent Classification (CPC) codes. CPC is a highly specific hierarchical system used globally to categorize technologies.
- **`patent_id`**: Foreign key linking to the patent.
- **`cpc_section`**: The top-level letter characterizing the broad domain of the invention.
  - `A`: Human Necessities
  - `B`: Performing Operations; Transporting
  - `C`: Chemistry; Metallurgy
  - `D`: Textiles; Paper
  - `E`: Fixed Constructions
  - `F`: Mechanical Engineering; Lighting; Heating; Weapons; Blasting
  - `G`: Physics
  - `H`: Electricity

---

## How The Pipeline Uses This Data

1. **Relational Mapping**: The pipeline uses `patent_id` to join these 5 separate files into a cohesive MySQL database.
2. **Network Analysis**: By looking at `g_inventor_200k.tsv`, we can map out which inventors share the same `patent_id`. We use this to build a **Co-Inventor Network Graph** showing collaboration.
3. **Forecasting**: We aggregate the `filing_date` from `g_patent_200k.tsv` by year and run it through a Linear Regression model to predict future filing volumes.
4. **Natural Language Processing**: We feed the texts from `g_abstract_200k.tsv` alongside the target labels from `g_cpc_200k.tsv` into an ML pipeline to build the Deep Learning abstract classifier.
