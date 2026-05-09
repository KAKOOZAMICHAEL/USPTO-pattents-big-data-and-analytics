import sqlalchemy
import pandas as pd
import os
from analyze_db import train_abstract_classifier

DB_URL = "sqlite:///patents.db"

def main():
    engine = sqlalchemy.create_engine(DB_URL)

    if not os.path.exists("outputs"):
        os.makedirs("outputs")

    # ---------- patent_yearly_summary ----------
    print("Populating patent_yearly_summary...")
    q1 = """
    INSERT INTO patent_yearly_summary (year, cpc_section, country, count)
    SELECT
        CAST(strftime('%Y', p.filing_date) AS INTEGER),
        p.cpc_section,
        i.country,
        COUNT(*)
    FROM patents p
    LEFT JOIN patent_inventors pi ON p.patent_id = pi.patent_id
    LEFT JOIN inventors i ON pi.inventor_id = i.inventor_id
    GROUP BY
        strftime('%Y', p.filing_date),
        p.cpc_section,
        i.country
    """

    # ---------- monthly_volume_summary ----------
    print("Populating monthly_volume_summary...")
    q2 = """
    INSERT INTO monthly_volume_summary (month, count)
    SELECT
        strftime('%Y-%m-01', filing_date),
        COUNT(*)
    FROM patents
    GROUP BY strftime('%Y-%m-01', filing_date)
    """

    # ---------- company_yearly_summary ----------
    print("Populating company_yearly_summary...")
    q3 = """
    INSERT INTO company_yearly_summary (year, company_id, count, type)
    SELECT
        CAST(strftime('%Y', p.filing_date) AS INTEGER),
        c.company_id,
        COUNT(*),
        CASE
            WHEN LOWER(c.company_name) LIKE '%university%'
              OR LOWER(c.company_name) LIKE '%institute%'
              OR LOWER(c.company_name) LIKE '%college%' THEN 'Academic'
            ELSE 'Corporate'
        END
    FROM companies c
    JOIN patent_companies pc ON c.company_id = pc.company_id
    JOIN patents p ON pc.patent_id = p.patent_id
    GROUP BY
        strftime('%Y', p.filing_date),
        c.company_id,
        CASE
            WHEN LOWER(c.company_name) LIKE '%university%'
              OR LOWER(c.company_name) LIKE '%institute%'
              OR LOWER(c.company_name) LIKE '%college%' THEN 'Academic'
            ELSE 'Corporate'
        END
    """

    with engine.begin() as conn:
        conn.execute(sqlalchemy.text("DELETE FROM patent_yearly_summary"))
        conn.execute(sqlalchemy.text(q1))
        print("Success: Populated patent_yearly_summary.")

        conn.execute(sqlalchemy.text("DELETE FROM monthly_volume_summary"))
        conn.execute(sqlalchemy.text(q2))
        print("Success: Populated monthly_volume_summary.")

        conn.execute(sqlalchemy.text("DELETE FROM company_yearly_summary"))
        conn.execute(sqlalchemy.text(q3))
        print("Success: Populated company_yearly_summary.")

    # ---------- Top inventors export ----------
    print("Exporting top_inventors.csv...")
    df_inv = pd.read_sql(sqlalchemy.text("""
        SELECT i.full_name, COUNT(DISTINCT p.patent_id) as count
        FROM inventors i
        JOIN patent_inventors pi ON i.inventor_id = pi.inventor_id
        JOIN patents p ON pi.patent_id = p.patent_id
        GROUP BY i.inventor_id, i.full_name
        ORDER BY count DESC
        LIMIT 100
    """), engine)
    df_inv.to_csv("outputs/top_inventors.csv", index=False)
    print("Success: Exported top_inventors.csv.")

    # ---------- Top companies export ----------
    print("Exporting top_companies.csv...")
    df_comp = pd.read_sql(sqlalchemy.text("""
        SELECT c.company_name, COUNT(DISTINCT p.patent_id) as count
        FROM companies c
        JOIN patent_companies pc ON c.company_id = pc.company_id
        JOIN patents p ON pc.patent_id = p.patent_id
        GROUP BY c.company_id, c.company_name
        ORDER BY count DESC
        LIMIT 100
    """), engine)
    df_comp.to_csv("outputs/top_companies.csv", index=False)
    print("Success: Exported top_companies.csv.")

    # ---------- Abstract classifier ----------
    print("Training abstract classifier...")
    acc, report = train_abstract_classifier(engine)
    print(f"Success: Trained abstract classifier (Accuracy: {acc:.2f}).")
    print(report)


if __name__ == "__main__":
    main()
