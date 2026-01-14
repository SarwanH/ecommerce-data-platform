"""Tests for data generation."""
import pytest
import pandas as pd
from src.ingestion.generate_data import generate_products, generate_stores

def test_generate_products():
    df = generate_products(10)
    assert len(df) == 10
    assert 'product_id' in df.columns
    assert df['product_id'].is_unique

def test_generate_stores():
    df = generate_stores(5)
    assert len(df) == 5
    assert 'store_id' in df.columns