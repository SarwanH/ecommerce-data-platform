#!/usr/bin/env python3
"""
Generate realistic e-commerce data for the Home Depot Data Platform.

Usage:
    python src/ingestion/generate_data.py
    python src/ingestion/generate_data.py --days 90 --output data/sample
"""

import os
import random
import uuid
import argparse
from datetime import datetime, timedelta, date
from pathlib import Path

import pandas as pd
import numpy as np
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)

# Configuration
NUM_PRODUCTS = 500
NUM_STORES = 50
NUM_CUSTOMERS = 10000
TRANSACTIONS_PER_DAY = 5000

# Categories and brands (Home Depot style)
CATEGORIES = {
    "Lumber & Building Materials": ["Dimensional Lumber", "Plywood", "Studs"],
    "Electrical": ["Wiring", "Outlets", "Switches", "Lighting"],
    "Plumbing": ["Pipes", "Fittings", "Faucets"],
    "Paint": ["Interior Paint", "Exterior Paint", "Stains"],
    "Tools": ["Power Tools", "Hand Tools", "Tool Storage"],
    "Appliances": ["Refrigerators", "Washers", "Dryers"],
}

BRANDS = {
    "Lumber & Building Materials": ["Pine Co", "Oakwood", "TimberMax"],
    "Electrical": ["Leviton", "Lutron", "Eaton"],
    "Plumbing": ["Moen", "Delta", "Kohler"],
    "Paint": ["Behr", "Glidden", "PPG"],
    "Tools": ["Milwaukee", "DeWalt", "Ryobi", "Makita"],
    "Appliances": ["Samsung", "LG", "Whirlpool", "GE"],
}

REGIONS = {
    "Northeast": ["NY", "NJ", "PA", "MA"],
    "Southeast": ["FL", "GA", "NC", "VA"],
    "Midwest": ["IL", "OH", "MI", "IN"],
    "Southwest": ["TX", "AZ", "CO"],
    "West": ["CA", "WA", "OR"],
}


def generate_products(n=NUM_PRODUCTS):
    """Generate product master data."""
    products = []
    for i in range(n):
        category = random.choice(list(CATEGORIES.keys()))
        subcategory = random.choice(CATEGORIES[category])
        brand = random.choice(BRANDS[category])
        base_price = random.uniform(5, 2000)
        
        products.append({
            "product_id": f"PRD-{i+1:06d}",
            "sku": f"{category[:3].upper()}-{random.randint(100000, 999999)}",
            "product_name": f"{brand} {subcategory} {fake.word().title()}",
            "category": category,
            "subcategory": subcategory,
            "brand": brand,
            "unit_price": round(base_price, 2),
            "unit_cost": round(base_price * random.uniform(0.4, 0.7), 2),
            "weight_lbs": round(random.uniform(0.1, 200), 2),
            "is_active": random.random() > 0.05,
            "created_at": fake.date_time_between("-3y", "-6m"),
            "updated_at": fake.date_time_between("-6m", "now"),
        })
    return pd.DataFrame(products)


def generate_stores(n=NUM_STORES):
    """Generate store data."""
    stores = []
    for i in range(n):
        region = random.choice(list(REGIONS.keys()))
        state = random.choice(REGIONS[region])
        store_type = random.choices(
            ["retail", "distribution_center", "fulfillment_center"],
            weights=[80, 15, 5]
        )[0]
        
        stores.append({
            "store_id": f"STR-{i+1:04d}",
            "store_name": f"Store #{i+1:04d} - {fake.city()}",
            "store_type": store_type,
            "address": fake.street_address(),
            "city": fake.city(),
            "state": state,
            "zip_code": fake.zipcode(),
            "region": region,
            "latitude": float(fake.latitude()),
            "longitude": float(fake.longitude()),
            "opened_date": fake.date_between("-20y", "-1y"),
            "square_footage": random.randint(80000, 150000),
            "is_active": True,
        })
    return pd.DataFrame(stores)


def generate_customers(n=NUM_CUSTOMERS):
    """Generate customer data."""
    customers = []
    tiers = ["bronze"] * 50 + ["silver"] * 30 + ["gold"] * 15 + ["pro_xtra"] * 5
    
    for i in range(n):
        region = random.choice(list(REGIONS.keys()))
        state = random.choice(REGIONS[region])
        cust_type = "pro" if random.random() < 0.15 else "consumer"
        
        customers.append({
            "customer_id": f"CUS-{i+1:08d}",
            "customer_type": cust_type,
            "email": fake.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "city": fake.city(),
            "state": state,
            "zip_code": fake.zipcode(),
            "created_at": fake.date_time_between("-5y", "now"),
            "loyalty_tier": random.choice(tiers),
        })
    return pd.DataFrame(customers)


def generate_transactions(products_df, stores_df, customers_df, days=30):
    """Generate sales transactions."""
    transactions = []
    
    product_ids = products_df[products_df["is_active"]]["product_id"].tolist()
    prices = dict(zip(products_df["product_id"], products_df["unit_price"]))
    store_ids = stores_df[stores_df["store_type"] == "retail"]["store_id"].tolist()
    customer_ids = customers_df["customer_id"].tolist()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    order_num = 0
    
    for day in range(days):
        current = start_date + timedelta(days=day)
        is_weekend = current.weekday() >= 5
        daily_count = int(TRANSACTIONS_PER_DAY * (1.3 if is_weekend else 1.0))
        
        for _ in range(daily_count):
            order_num += 1
            order_id = f"ORD-{order_num:010d}"
            num_items = random.choices([1,2,3,4,5], weights=[40,30,15,10,5])[0]
            
            channel = random.choices(
                ["online", "in_store", "app"],
                weights=[35, 55, 10]
            )[0]
            
            for prod_id in random.sample(product_ids, num_items):
                qty = random.choices([1,2,3,5,10], weights=[60,25,10,4,1])[0]
                price = prices.get(prod_id, 50.0)
                discount = round(price * qty * random.choice([0, 0.05, 0.1, 0.15]), 2)
                
                transactions.append({
                    "transaction_id": f"TXN-{uuid.uuid4().hex[:12].upper()}",
                    "order_id": order_id,
                    "customer_id": random.choice(customer_ids),
                    "store_id": random.choice(store_ids),
                    "product_id": prod_id,
                    "transaction_date": current.replace(
                        hour=random.randint(6, 21),
                        minute=random.randint(0, 59)
                    ),
                    "quantity": qty,
                    "unit_price": price,
                    "discount_amount": discount,
                    "total_amount": round(price * qty - discount, 2),
                    "order_status": random.choices(
                        ["pending", "confirmed", "shipped", "delivered", "cancelled", "returned"],
                        weights=[5, 10, 15, 60, 5, 5]
                    )[0],
                    "channel": channel,
                    "fulfillment_type": "in_store" if channel == "in_store" else random.choice(["ship_to_home", "bopis"]),
                })
    
    return pd.DataFrame(transactions)


def generate_inventory(products_df, stores_df, days=30):
    """Generate inventory snapshots."""
    snapshots = []
    product_ids = products_df[products_df["is_active"]]["product_id"].tolist()
    store_ids = stores_df["store_id"].tolist()
    
    # Sample product-store combinations
    combos = [
        (s, p) for s in store_ids
        for p in random.sample(product_ids, min(200, len(product_ids)))
    ]
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    inventory = {c: random.randint(10, 500) for c in combos}
    
    for day in range(days):
        snap_date = start_date + timedelta(days=day)
        for (store_id, product_id), base in inventory.items():
            qty = max(0, base + random.randint(-20, 30))
            inventory[(store_id, product_id)] = qty
            reserved = random.randint(0, min(20, qty))
            
            snapshots.append({
                "snapshot_date": snap_date,
                "store_id": store_id,
                "product_id": product_id,
                "quantity_on_hand": qty,
                "quantity_reserved": reserved,
                "quantity_available": qty - reserved,
                "reorder_point": random.randint(20, 50),
                "safety_stock": random.randint(10, 30),
                "days_of_supply": round(qty / max(1, random.uniform(5, 20)), 1),
            })
    
    return pd.DataFrame(snapshots)


def generate_page_views(products_df, customers_df, days=30):
    """Generate clickstream data."""
    page_views = []
    product_ids = products_df["product_id"].tolist()
    customer_ids = customers_df["customer_id"].tolist() + [None] * 5000
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    for day in range(days):
        current = start_date + timedelta(days=day)
        sessions = random.randint(3000, 7000)
        
        for _ in range(sessions):
            session_id = f"SES-{uuid.uuid4().hex[:16].upper()}"
            customer_id = random.choice(customer_ids)
            device = random.choice(["desktop", "mobile", "tablet"])
            browser = random.choice(["Chrome", "Safari", "Firefox", "Edge"])
            
            for _ in range(random.randint(3, 15)):
                event_type = random.choices(
                    ["page_view", "add_to_cart", "purchase", "search"],
                    weights=[70, 15, 5, 10]
                )[0]
                
                page_views.append({
                    "event_id": f"EVT-{uuid.uuid4().hex[:12].upper()}",
                    "session_id": session_id,
                    "customer_id": customer_id,
                    "product_id": random.choice(product_ids) if random.random() > 0.3 else None,
                    "event_timestamp": current.replace(
                        hour=random.randint(0, 23),
                        minute=random.randint(0, 59)
                    ),
                    "event_type": event_type,
                    "page_url": f"/product/{random.choice(product_ids)}" if random.random() > 0.4 else "/",
                    "referrer_url": random.choice([None, "https://google.com", "direct"]),
                    "device_type": device,
                    "browser": browser,
                })
    
    return pd.DataFrame(page_views)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--output", type=str, default="data/sample")
    args = parser.parse_args()
    
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    
    print("=" * 50)
    print("Home Depot Data Generator")
    print("=" * 50)
    
    print("\nGenerating products...")
    products = generate_products()
    products.to_parquet(output / "products.parquet", index=False)
    products.to_csv(output / "products.csv", index=False)
    print(f"  ✓ {len(products):,} products")
    
    print("\nGenerating stores...")
    stores = generate_stores()
    stores.to_parquet(output / "stores.parquet", index=False)
    stores.to_csv(output / "stores.csv", index=False)
    print(f"  ✓ {len(stores):,} stores")
    
    print("\nGenerating customers...")
    customers = generate_customers()
    customers.to_parquet(output / "customers.parquet", index=False)
    customers.to_csv(output / "customers.csv", index=False)
    print(f"  ✓ {len(customers):,} customers")
    
    print(f"\nGenerating transactions ({args.days} days)...")
    transactions = generate_transactions(products, stores, customers, args.days)
    transactions.to_parquet(output / "transactions.parquet", index=False)
    transactions.to_csv(output / "transactions.csv", index=False)
    print(f"  ✓ {len(transactions):,} transactions")
    
    print(f"\nGenerating inventory ({args.days} days)...")
    inventory = generate_inventory(products, stores, args.days)
    inventory.to_parquet(output / "inventory_snapshots.parquet", index=False)
    inventory.to_csv(output / "inventory_snapshots.csv", index=False)
    print(f"  ✓ {len(inventory):,} inventory records")
    
    print(f"\nGenerating page views ({args.days} days)...")
    views = generate_page_views(products, customers, args.days)
    views.to_parquet(output / "page_views.parquet", index=False)
    views.to_csv(output / "page_views.csv", index=False)
    print(f"  ✓ {len(views):,} page views")
    
    print("\n" + "=" * 50)
    print("✅ Data generation complete!")
    print(f"Output: {output.absolute()}")


if __name__ == "__main__":
    main()