import os
import zipfile
import urllib.request
import pandas as pd
import time

def download_file(url, filename):
    print(f"Downloading {filename}...")
    urllib.request.urlretrieve(url, filename)
    print(f"Downloaded {filename}.")

def process_data():
    os.makedirs('sample_data', exist_ok=True)
    os.makedirs('temp_data', exist_ok=True)
    
    urls = {
        'g_patent': "https://s3.amazonaws.com/data.patentsview.org/download/g_patent.tsv.zip",
        'g_inventor': "https://s3.amazonaws.com/data.patentsview.org/download/g_inventor_disambiguated.tsv.zip",
        'g_assignee': "https://s3.amazonaws.com/data.patentsview.org/download/g_assignee_disambiguated.tsv.zip",
        'g_abstract': "https://s3.amazonaws.com/data.patentsview.org/download/g_patent_abstract.tsv.zip",
        'g_cpc': "https://s3.amazonaws.com/data.patentsview.org/download/g_cpc_current.tsv.zip"
    }

    # 1. Process g_patent to get 200k patent IDs
    patent_zip = 'temp_data/g_patent.zip'
    download_file(urls['g_patent'], patent_zip)
    
    print("Extracting and slicing g_patent...")
    valid_patent_ids = set()
    
    # We read chunk by chunk to limit memory
    chunk_size = 50000
    rows_collected = 0
    target_rows = 200000
    
    with zipfile.ZipFile(patent_zip, 'r') as z:
        # Get the tsv filename inside the zip
        tsv_name = [n for n in z.namelist() if n.endswith('.tsv')][0]
        with z.open(tsv_name) as f:
            for i, chunk in enumerate(pd.read_csv(f, sep='\t', chunksize=chunk_size, dtype=str)):
                # Filter out null patent_ids
                chunk = chunk.dropna(subset=['patent_id'])
                
                needed = target_rows - rows_collected
                if needed <= 0:
                    break
                    
                if len(chunk) > needed:
                    chunk = chunk.head(needed)
                    
                valid_patent_ids.update(chunk['patent_id'].tolist())
                
                # Write to the 200k file
                mode = 'w' if rows_collected == 0 else 'a'
                header = True if rows_collected == 0 else False
                chunk.to_csv('sample_data/g_patent_200k.tsv', sep='\t', index=False, mode=mode, header=header)
                
                rows_collected += len(chunk)
                print(f"Collected {rows_collected}/{target_rows} patents...")
                
    # Free up disk space immediately
    os.remove(patent_zip)
    print(f"Collected {len(valid_patent_ids)} unique patent IDs.")

    # 2. Function to process dependent files
    def process_dependent(key, zip_url, out_name):
        zip_path = f'temp_data/{key}.zip'
        download_file(zip_url, zip_path)
        
        print(f"Filtering {key}...")
        rows_kept = 0
        with zipfile.ZipFile(zip_path, 'r') as z:
            tsv_name = [n for n in z.namelist() if n.endswith('.tsv')][0]
            with z.open(tsv_name) as f:
                first_chunk = True
                for chunk in pd.read_csv(f, sep='\t', chunksize=100000, dtype=str):
                    if 'patent_id' not in chunk.columns:
                        print(f"Warning: patent_id not found in {key}, skipping filtering...")
                        break
                        
                    # Filter by valid patent IDs
                    filtered = chunk[chunk['patent_id'].isin(valid_patent_ids)]
                    
                    if not filtered.empty:
                        mode = 'w' if first_chunk else 'a'
                        header = True if first_chunk else False
                        filtered.to_csv(f'sample_data/{out_name}', sep='\t', index=False, mode=mode, header=header)
                        first_chunk = False
                        rows_kept += len(filtered)
                        
        print(f"Finished {key}, kept {rows_kept} rows.")
        os.remove(zip_path)

    # Process the remaining 4 files
    process_dependent('g_inventor', urls['g_inventor'], 'g_inventor_200k.tsv')
    process_dependent('g_assignee', urls['g_assignee'], 'g_assignee_200k.tsv')
    process_dependent('g_abstract', urls['g_abstract'], 'g_abstract_200k.tsv')
    process_dependent('g_cpc', urls['g_cpc'], 'g_cpc_200k.tsv')
    
    # Cleanup
    os.rmdir('temp_data')
    print("Successfully downloaded, sliced, and cleaned up real USPTO data!")

if __name__ == "__main__":
    start = time.time()
    try:
        process_data()
    except Exception as e:
        print(f"An error occurred: {e}")
    print(f"Total time: {time.time() - start:.2f} seconds")
