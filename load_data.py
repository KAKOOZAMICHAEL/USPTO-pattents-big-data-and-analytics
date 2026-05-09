import pandas as pd
import sqlalchemy
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
import os

DB_URL = "sqlite:///patents.db"


def _insert_or_ignore(table, conn, keys, data_iter):
    """Custom pandas to_sql method that uses SQLite INSERT OR IGNORE."""
    data = [dict(zip(keys, row)) for row in data_iter]
    if not data:
        return
    stmt = sqlite_insert(table.table).values(data).prefix_with("OR IGNORE")
    conn.execute(stmt)


def load_table(engine, table_name, file_path, pk):
    if not os.path.exists(file_path):
        print(f"Skipping {table_name}: {file_path} not found.")
        return

    print(f"Loading table: {table_name}...")
    chunk_size = 10000
    inserted_rows = 0
    skipped_rows = 0

    for chunk in pd.read_csv(file_path, chunksize=chunk_size, dtype=str):
        # Deduplicate within the chunk on primary key
        chunk_len_before = len(chunk)
        pk_cols = pk if isinstance(pk, list) else [pk]
        chunk = chunk.drop_duplicates(subset=pk_cols)
        skipped_rows += chunk_len_before - len(chunk)

        before_count = _get_count(engine, table_name)
        chunk.to_sql(
            table_name,
            con=engine,
            if_exists="append",
            index=False,
            method=_insert_or_ignore,
            chunksize=500
        )
        after_count = _get_count(engine, table_name)
        batch_inserted = after_count - before_count
        inserted_rows += batch_inserted
        skipped_rows += len(chunk) - batch_inserted

    print(f"Table {table_name}: inserted {inserted_rows} rows, skipped {skipped_rows} duplicates")
    os.remove(file_path)


def _get_count(engine, table_name):
    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text(f'SELECT COUNT(*) FROM "{table_name}"'))
        return result.scalar()


def main():
    engine = sqlalchemy.create_engine(DB_URL)

    with engine.begin() as conn:
        conn.execute(sqlalchemy.text("PRAGMA journal_mode=WAL"))
        conn.execute(sqlalchemy.text("PRAGMA synchronous=NORMAL"))
        conn.execute(sqlalchemy.text("PRAGMA foreign_keys=OFF"))
        conn.execute(sqlalchemy.text("PRAGMA cache_size=-64000"))

    tables_to_load = [
        ("patents",          "patents.csv",          "patent_id"),
        ("inventors",        "inventors.csv",        "inventor_id"),
        ("companies",        "companies.csv",        "company_id"),
        ("patent_inventors", "patent_inventors.csv", ["patent_id", "inventor_id"]),
        ("patent_companies", "patent_companies.csv", ["patent_id", "company_id"]),
        ("g_abstract",       "g_abstract.csv",       "patent_id"),
    ]

    for table_name, file_path, pk in tables_to_load:
        load_table(engine, table_name, file_path, pk)

    with engine.begin() as conn:
        conn.execute(sqlalchemy.text("PRAGMA foreign_keys=ON"))

    print("Data loading complete.")


if __name__ == "__main__":
    main()
