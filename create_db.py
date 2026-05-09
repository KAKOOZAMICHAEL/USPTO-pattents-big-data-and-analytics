import sqlalchemy
import os

DB_URL = "sqlite:///patents.db"
DB_PATH = "patents.db"

def main():
    print("Starting database creation...")
    
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Removed existing patents.db for fresh run.")

    engine = sqlalchemy.create_engine(DB_URL)
    
    with open("schema.sql", "r") as f:
        schema_sql = f.read()
    
    with engine.begin() as conn:
        # Split by semicolon and execute each statement
        for statement in schema_sql.split(";"):
            if statement.strip():
                conn.execute(sqlalchemy.text(statement))
        
        # Add Indexes for Performance
        print("Adding performance indexes...")
        conn.execute(sqlalchemy.text("CREATE INDEX idx_p_filing ON patents(filing_date)"))
        conn.execute(sqlalchemy.text("CREATE INDEX idx_p_cpc ON patents(cpc_section)"))
        conn.execute(sqlalchemy.text("CREATE INDEX idx_i_country ON inventors(country)"))
        conn.execute(sqlalchemy.text("CREATE INDEX idx_pi_patent ON patent_inventors(patent_id)"))
        conn.execute(sqlalchemy.text("CREATE INDEX idx_pi_inventor ON patent_inventors(inventor_id)"))
        
        # Summary table indexes
        conn.execute(sqlalchemy.text("CREATE INDEX idx_pys_year ON patent_yearly_summary(year)"))
        conn.execute(sqlalchemy.text("CREATE INDEX idx_pys_country ON patent_yearly_summary(country)"))
        conn.execute(sqlalchemy.text("CREATE INDEX idx_pys_cpc ON patent_yearly_summary(cpc_section)"))
        conn.execute(sqlalchemy.text("CREATE INDEX idx_mvs_month ON monthly_volume_summary(month)"))
        conn.execute(sqlalchemy.text("CREATE INDEX idx_cys_year ON company_yearly_summary(year)"))

    print(f"Database ready: {os.path.abspath(DB_PATH)}")

if __name__ == "__main__":
    main()
