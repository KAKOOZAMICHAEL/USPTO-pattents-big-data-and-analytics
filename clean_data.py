import pandas as pd
import os

def clean_and_save(df, output_path, primary_key):
    if os.path.exists(output_path):
        os.remove(output_path)
    
    count_before = len(df)
    
    # Drop rows where primary key is null or empty
    if isinstance(primary_key, list):
        for pk in primary_key:
            df = df[df[pk].notna() & (df[pk] != '')]
        df = df.drop_duplicates(subset=primary_key)
    else:
        df = df[df[primary_key].notna() & (df[primary_key] != '')]
        df = df.drop_duplicates(subset=[primary_key])
        
    count_after = len(df)
    print(f"File {output_path}: {count_before} rows before deduplication, {count_after} rows after.")
    
    df.to_csv(output_path, index=False)

def main():
    print("Starting data cleaning...")
    
    # 1. Patents
    print("Cleaning patents...")
    df_patents = pd.read_csv("extracted/ext_patents.csv", dtype=str)
    # Read CPC to merge with patents
    df_cpc = pd.read_csv("extracted/ext_cpc.csv", dtype=str)
    # Deduplicate CPC just in case, taking the first CPC section per patent
    df_cpc = df_cpc.drop_duplicates(subset=["patent_id"])
    
    df_patents = pd.merge(df_patents, df_cpc, on="patent_id", how="left")
    clean_and_save(df_patents, "patents.csv", "patent_id")
    
    # 2. Inventors
    print("Cleaning inventors...")
    df_ext_inv = pd.read_csv("extracted/ext_inventors.csv", dtype=str)
    # Inventors table
    df_inventors = df_ext_inv[["inventor_id", "disambig_inventor_id", "disambig_country"]].copy()
    df_inventors.rename(columns={"disambig_inventor_id": "full_name", "disambig_country": "country"}, inplace=True)
    clean_and_save(df_inventors, "inventors.csv", "inventor_id")
    
    # Patent-Inventors table
    df_pat_inv = df_ext_inv[["patent_id", "inventor_id"]].copy()
    clean_and_save(df_pat_inv, "patent_inventors.csv", ["patent_id", "inventor_id"])
    
    # 3. Companies (Assignees)
    print("Cleaning companies...")
    df_ext_assig = pd.read_csv("extracted/ext_assignees.csv", dtype=str)
    # Companies table
    df_companies = df_ext_assig[["assignee_id", "disambig_assignee_organization"]].copy()
    df_companies.rename(columns={"assignee_id": "company_id", "disambig_assignee_organization": "company_name"}, inplace=True)
    clean_and_save(df_companies, "companies.csv", "company_id")
    
    # Patent-Companies table
    df_pat_comp = df_ext_assig[["patent_id", "assignee_id"]].copy()
    df_pat_comp.rename(columns={"assignee_id": "company_id"}, inplace=True)
    clean_and_save(df_pat_comp, "patent_companies.csv", ["patent_id", "company_id"])
    
    # 4. Abstracts
    print("Cleaning abstracts...")
    df_abstracts = pd.read_csv("extracted/ext_abstracts.csv", dtype=str)
    df_abstracts.rename(columns={"patent_abstract": "abstract"}, inplace=True)
    clean_and_save(df_abstracts, "g_abstract.csv", "patent_id")
    
    print("Data cleaning complete.")

if __name__ == "__main__":
    main()
