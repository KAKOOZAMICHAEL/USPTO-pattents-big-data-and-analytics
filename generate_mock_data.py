import os
import pandas as pd
import numpy as np

def generate_mock_data():
    os.makedirs('sample_data', exist_ok=True)
    
    num_records = 500
    
    # 1. g_patent_200k.tsv
    patent_ids = [f"P{str(i).zfill(6)}" for i in range(1, num_records + 1)]
    patents = pd.DataFrame({
        "patent_id": patent_ids,
        "title": [f"Patent Title {i}" for i in range(1, num_records + 1)],
        "filing_date": pd.date_range(start='2015-01-01', periods=num_records, freq='D').strftime('%Y-%m-%d'),
        "publication_date": pd.date_range(start='2016-01-01', periods=num_records, freq='D').strftime('%Y-%m-%d'),
        "main_classification": [np.random.choice(['G06F', 'H04L', 'A61K', 'B60R']) for _ in range(num_records)]
    })
    patents.to_csv('sample_data/g_patent_200k.tsv', sep='\t', index=False)
    
    # 2. g_inventor_200k.tsv
    inventors = pd.DataFrame({
        "patent_id": patent_ids,
        "inventor_id": [f"I{str(i).zfill(5)}" for i in range(1, num_records + 1)],
        "disambig_inventor_id": [f"Inventor Name {i}" for i in range(1, num_records + 1)],
        "disambig_country": [np.random.choice(['US', 'JP', 'CN', 'DE', 'KR']) for _ in range(num_records)]
    })
    inventors.to_csv('sample_data/g_inventor_200k.tsv', sep='\t', index=False)
    
    # 3. g_assignee_200k.tsv
    companies = pd.DataFrame({
        "patent_id": patent_ids,
        "assignee_id": [f"C{str(i % 50).zfill(3)}" for i in range(1, num_records + 1)],
        "disambig_assignee_organization": [np.random.choice([
            'Tech Corp', 'Global Solutions', 'Innovate LLC', 'State University', 'Institute of Tech', 
            'Acme Corp', 'National College'
        ]) for _ in range(num_records)]
    })
    companies.to_csv('sample_data/g_assignee_200k.tsv', sep='\t', index=False)
    
    # 4. g_abstract_200k.tsv
    abstracts = pd.DataFrame({
        "patent_id": patent_ids,
        "patent_abstract": [
            "This invention provides a method for processing data using neural networks and distributed systems. The system improves performance and reduces latency."
            if i % 2 == 0 else 
            "A mechanical device comprising a lever, a gear system, and an actuator designed to improve industrial manufacturing efficiency." 
            for i in range(num_records)
        ]
    })
    abstracts.to_csv('sample_data/g_abstract_200k.tsv', sep='\t', index=False)
    
    # 5. g_cpc_200k.tsv
    cpcs = pd.DataFrame({
        "patent_id": patent_ids,
        "cpc_section": [np.random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']) for _ in range(num_records)]
    })
    cpcs.to_csv('sample_data/g_cpc_200k.tsv', sep='\t', index=False)
    
    print("Mock data generated successfully in sample_data/ directory.")

if __name__ == "__main__":
    generate_mock_data()
