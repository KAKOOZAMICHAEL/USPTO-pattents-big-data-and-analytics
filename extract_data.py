import pandas as pd
import sqlite3
import os

def process_patents():
    print("Extracting patents...")
    chunk_size = 50000
    file_path = "sample_data/g_patent_200k.tsv"
    out_path = "extracted/ext_patents.csv"
    
    if os.path.exists("temp_valid_ids.db"):
        os.remove("temp_valid_ids.db")
    conn = sqlite3.connect("temp_valid_ids.db")
    conn.execute("CREATE TABLE valid_ids (patent_id TEXT PRIMARY KEY)")
    
    # Real USPTO column names
    cols = ["patent_id", "patent_title", "patent_date"]
    
    total_rows = 0
    first_chunk = True
    mode = 'w'
    
    for chunk in pd.read_csv(file_path, sep="\t", chunksize=chunk_size, usecols=lambda c: c in cols, dtype=str):
        chunk = chunk.reindex(columns=cols)
        # Rename to what the pipeline expects
        chunk.rename(columns={"patent_title": "title", "patent_date": "filing_date"}, inplace=True)
        # Add publication_date and main_classification as placeholders if missing
        chunk["publication_date"] = chunk["filing_date"]
        chunk["main_classification"] = "Unknown"
        
        chunk.to_csv(out_path, mode=mode, header=first_chunk, index=False)
        mode = 'a'
        first_chunk = False
        
        valid_ids = chunk[["patent_id"]].dropna()
        valid_ids.to_sql("valid_ids", conn, if_exists="append", index=False)
        
        total_rows += len(chunk)
        print(f"Patents: processed {total_rows} rows")
        
    conn.execute("CREATE INDEX idx_patent_id ON valid_ids(patent_id)")
    conn.close()

def process_file(name, file_path, out_path, cols, rename_map=None):
    print(f"Extracting {name}...")
    chunk_size = 50000
    total_rows = 0
    first_chunk = True
    mode = 'w'
    
    try:
        for chunk in pd.read_csv(file_path, sep="\t", chunksize=chunk_size, usecols=lambda c: c in cols, dtype=str):
            chunk = chunk.reindex(columns=cols)
            if rename_map:
                chunk.rename(columns=rename_map, inplace=True)
            
            # Special case for inventors: combine names
            if name == "inventors":
                chunk["disambig_inventor_id"] = chunk["disambig_inventor_name_first"].fillna("") + " " + chunk["disambig_inventor_name_last"].fillna("")
                # If country is missing, set as Unknown
                if "disambig_country" not in chunk.columns:
                    chunk["disambig_country"] = "Unknown"
            
            chunk.to_csv(out_path, mode=mode, header=first_chunk, index=False)
            mode = 'a'
            first_chunk = False
            
            total_rows += len(chunk)
            print(f"{name}: processed {total_rows} rows")
    except Exception as e:
        print(f"Error processing {name}: {e}")

def main():
    if not os.path.exists("extracted"):
        os.makedirs("extracted")
        
    process_patents()
    
    # Update to actual headers found in TSV
    process_file("inventors", "sample_data/g_inventor_200k.tsv", "extracted/ext_inventors.csv", 
                 ["patent_id", "inventor_id", "disambig_inventor_name_first", "disambig_inventor_name_last"])
    
    process_file("assignees", "sample_data/g_assignee_200k.tsv", "extracted/ext_assignees.csv", 
                 ["patent_id", "assignee_id", "disambig_assignee_organization"])
                 
    process_file("abstracts", "sample_data/g_abstract_200k.tsv", "extracted/ext_abstracts.csv", 
                 ["patent_id", "patent_abstract"])
                 
    process_file("cpc", "sample_data/g_cpc_200k.tsv", "extracted/ext_cpc.csv", 
                 ["patent_id", "cpc_section"])
                 
    print("Extraction complete.")

if __name__ == "__main__":
    main()
