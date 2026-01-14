import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
import pandas as pd
from src.ingestion.generate_data import generate_products, generate_stores, generate_customers


class TestGenerateProducts:
    """Tests for product generation."""
    
    def test_generate_products_returns_dataframe(self):
        df = generate_products(10)
        assert isinstance(df, pd.DataFrame)
    
    def test_generate_products_correct_count(self):
        df = generate_products(10)
        assert len(df) == 10
    
    def test_generate_products_has_required_columns(self):
        df = generate_products(5)
        required_columns = ['product_id', 'sku', 'product_name', 'category', 
                          'subcategory', 'brand', 'unit_price', 'unit_cost']
        for col in required_columns:
            assert col in df.columns, f"Missing column: {col}"
    
    def test_generate_products_unique_ids(self):
        df = generate_products(100)
        assert df['product_id'].is_unique
    
    def test_generate_products_valid_prices(self):
        df = generate_products(50)
        assert (df['unit_price'] > 0).all()
        assert (df['unit_cost'] > 0).all()


class TestGenerateStores:
    """Tests for store generation."""
    
    def test_generate_stores_returns_dataframe(self):
        df = generate_stores(5)
        assert isinstance(df, pd.DataFrame)
    
    def test_generate_stores_correct_count(self):
        df = generate_stores(5)
        assert len(df) == 5
    
    def test_generate_stores_unique_ids(self):
        df = generate_stores(20)
        assert df['store_id'].is_unique
    
    def test_generate_stores_valid_types(self):
        df = generate_stores(50)
        valid_types = ['retail', 'distribution_center', 'fulfillment_center']
        assert df['store_type'].isin(valid_types).all()


class TestGenerateCustomers:
    """Tests for customer generation."""
    
    def test_generate_customers_returns_dataframe(self):
        df = generate_customers(10)
        assert isinstance(df, pd.DataFrame)
    
    def test_generate_customers_correct_count(self):
        df = generate_customers(10)
        assert len(df) == 10
    
    def test_generate_customers_unique_ids(self):
        df = generate_customers(100)
        assert df['customer_id'].is_unique
    
    def test_generate_customers_valid_types(self):
        df = generate_customers(100)
        valid_types = ['consumer', 'pro']
        assert df['customer_type'].isin(valid_types).all()
