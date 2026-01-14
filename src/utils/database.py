"""Database connection utilities using DuckDB."""

import os
from pathlib import Path
from contextlib import contextmanager
import duckdb
import pandas as pd

DATABASE_PATH = os.getenv("DATABASE_PATH", "data/warehouse.duckdb")


def get_connection(db_path=None):
    """Get DuckDB connection."""
    path = db_path or DATABASE_PATH
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(path)


@contextmanager
def db_connection(db_path=None):
    """Context manager for connections."""
    conn = get_connection(db_path)
    try:
        yield conn
    finally:
        conn.close()


def load_parquet_to_table(table_name, parquet_path, schema="raw", db_path=None):
    """Load parquet file to DuckDB table."""
    with db_connection(db_path) as conn:
        conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        conn.execute(f"""
            CREATE OR REPLACE TABLE {schema}.{table_name} AS
            SELECT * FROM read_parquet('{parquet_path}')
        """)
        result = conn.execute(f"SELECT COUNT(*) FROM {schema}.{table_name}").fetchone()
        return result[0]


def initialize_warehouse(data_dir="data/sample", db_path=None):
    """Initialize warehouse with sample data."""
    data_path = Path(data_dir)
    
    tables = [
        ("products", "products.parquet"),
        ("stores", "stores.parquet"),
        ("customers", "customers.parquet"),
        ("transactions", "transactions.parquet"),
        ("inventory_snapshots", "inventory_snapshots.parquet"),
        ("page_views", "page_views.parquet"),
    ]
    
    print("Initializing warehouse...")
    for table, filename in tables:
        path = data_path / filename
        if path.exists():
            rows = load_parquet_to_table(table, str(path), db_path=db_path)
            print(f"  ✓ {table}: {rows:,} rows")
    print("✅ Done!")


if __name__ == "__main__":
    initialize_warehouse()