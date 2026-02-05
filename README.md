# E-Commerce Data Platform

[![CI Pipeline](https://github.com/SarwanH/ecommerce-data-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/SarwanH/ecommerce-data-platform/actions/workflows/ci.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![dbt](https://img.shields.io/badge/dbt-1.7.4-FF694B.svg)](https://www.getdbt.com/)
[![DuckDB](https://img.shields.io/badge/DuckDB-0.9.2-FEF000.svg)](https://duckdb.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **An end-to-end data engineering platform powering e-commerce analytics, demand forecasting, and inventory optimization for a home improvement retail environment.**

This project demonstrates production-grade data engineering practices including ETL pipeline development, dimensional modeling, data quality validation, and workflow orchestration—built with the modern data stack.

---

## Business Context

### The Problem

Home improvement retailers face complex data challenges:
- **Inventory Management**: Balancing stock levels across 2,000+ stores with 35,000+ SKUs
- **Demand Forecasting**: Predicting seasonal demand for products (e.g., lawn equipment in spring, heating supplies in winter)
- **Omnichannel Analytics**: Tracking customer journeys across online, in-store, and mobile channels
- **Supply Chain Optimization**: Coordinating between retail stores, distribution centers, and fulfillment centers

### The Solution

This platform provides the data infrastructure to:

| Business Need | Data Solution |
|--------------|---------------|
| Inventory Optimization | Daily inventory snapshots with stock status classification and days-of-supply calculations |
| Demand Forecasting | Aggregated sales data with lag features and rolling averages for ML model input |
| Customer Analytics | RFM (Recency, Frequency, Monetary) segmentation and lifetime value calculations |
| Channel Performance | Cross-channel attribution with fulfillment type analysis (BOPIS, Ship-to-Home, In-Store) |

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Languages** | Python 3.11, SQL | Core development |
| **Data Warehouse** | DuckDB (dev) / BigQuery (prod) | Analytical database |
| **Transformation** | dbt Core 1.7 | SQL-based transformations with testing |
| **Orchestration** | Apache Airflow 2.8 | Pipeline scheduling and monitoring |
| **Data Quality** | Great Expectations | Automated data validation |
| **Data Generation** | Faker, NumPy, Pandas | Realistic test data creation |
| **Storage Format** | Apache Parquet | Columnar storage for analytics |
| **CI/CD** | GitHub Actions | Automated testing and deployment |
| **Containerization** | Docker, Docker Compose | Reproducible environments |

### Why These Technologies?

- **DuckDB**: Embedded analytical database with BigQuery-compatible SQL—perfect for local development that mirrors production
- **dbt**: Industry-standard transformation layer with built-in testing, documentation, and lineage
- **Airflow**: Production-proven orchestrator used by companies like Airbnb, Lyft, and major retailers
- **Parquet**: Columnar format with 10x compression vs CSV, predicate pushdown for fast queries

---

## Getting Started

### Prerequisites

- Python 3.9+ (3.11 recommended)
- Git
- 4GB+ available RAM (for data generation)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/SarwanH/ecommerce-data-platform.git
cd ecommerce-data-platform

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configure dbt profile (one-time setup)
mkdir -p ~/.dbt
cat > ~/.dbt/profiles.yml << 'EOF'
home_depot_analytics:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: './data/warehouse.duckdb'
      schema: analytics
EOF
```

---

## Usage

### Generate Sample Data

```bash
# Generate 30 days of sample data (default)
python src/ingestion/generate_data.py

# Generate custom date range
python src/ingestion/generate_data.py --days 90 --output data/sample

# Output:
# ✓ 500 products
# ✓ 50 stores
# ✓ 10,000 customers
# ✓ ~150,000 transactions
# ✓ ~300,000 inventory records
# ✓ ~1,500,000 page views
```

### Initialize Data Warehouse

```bash
# Load parquet files into DuckDB
python src/utils/database.py

# Verify tables
python -c "
from src.utils.database import execute_query
print(execute_query('SELECT table_name FROM information_schema.tables WHERE table_schema = \'raw\''))
"
```

### Run dbt Transformations

```bash
cd dbt

# Install dbt packages
dbt deps

# Validate connection
dbt debug

# Run all models
dbt run

# Run specific layer
dbt run --select staging
dbt run --select marts

# Run with full refresh (rebuilds incremental models)
dbt run --full-refresh

# Generate documentation
dbt docs generate
dbt docs serve  # Opens browser at localhost:8080
```

### Query the Data

```python
from src.utils.database import execute_query

# Top 10 products by revenue
query = """
SELECT 
    p.product_name,
    p.category,
    SUM(f.total_amount) as revenue,
    SUM(f.line_profit) as profit
FROM marts.fact_sales f
JOIN marts.dim_product p ON f.product_id = p.product_id
WHERE f.order_status = 'delivered'
GROUP BY 1, 2
ORDER BY revenue DESC
LIMIT 10
"""
print(execute_query(query))
```

---

## Data Quality

### Great Expectations Suite

The `transactions_suite.json` validates:

| Expectation | Rule |
|-------------|------|
| `expect_column_to_exist` | Required columns present |
| `expect_column_values_to_be_unique` | `transaction_id` uniqueness |
| `expect_column_values_to_not_be_null` | Critical fields populated |
| `expect_column_values_to_be_between` | `quantity` between 1-1000 |
| `expect_column_values_to_be_in_set` | `channel` in ['online', 'in_store', 'app'] |

### dbt Tests

```yaml
# Example from schema.yml
models:
  - name: fact_sales
    columns:
      - name: transaction_id
        tests:
          - unique
          - not_null
      - name: order_status
        tests:
          - accepted_values:
              values: ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled', 'returned']
```

Run tests:
```bash
cd dbt
dbt test
```

---

## Pipeline Orchestration

### Airflow DAG Overview

```
ecommerce_data_pipeline (Daily @ 6:00 AM UTC)
│
├── ingestion (TaskGroup)
│   ├── extract_transactions
│   ├── extract_inventory
│   └── extract_clickstream
│
├── data_quality (TaskGroup)
│   └── run_quality_checks
│
├── dbt_transformations (TaskGroup)
│   ├── dbt_deps
│   ├── dbt_run_staging
│   ├── dbt_run_intermediate
│   ├── dbt_run_marts
│   └── dbt_test
│
├── analytics (TaskGroup)
│   ├── generate_forecast_features
│   └── update_dashboards
│
└── notify_completion
```

### Running Airflow Locally

```bash
cd docker
docker-compose up -d

# Access UI at http://localhost:8080
# Username: admin
# Password: admin
```

---

## Testing

```bash
# Run all Python tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run dbt tests
cd dbt && dbt test

# Run specific test file
pytest tests/unit/test_data_generation.py -v
```

### Test Coverage

| Module | Coverage |
|--------|----------|
| `src/ingestion` | Data generation functions |
| `src/utils` | Database connectivity |
| `dbt models` | Schema tests, uniqueness, referential integrity |

---

## Future Enhancements

- [ ] **Streaming Ingestion**: Add Kafka/Kinesis for real-time clickstream
- [ ] **ML Pipeline**: Integrate demand forecasting model with Vertex AI
- [ ] **Dashboard**: Build Streamlit/Looker dashboard for KPIs
- [ ] **Data Contracts**: Implement schema registry for producer/consumer contracts
- [ ] **Cost Optimization**: Add BigQuery slot management and query optimization
- [ ] **Alerting**: PagerDuty/Slack integration for pipeline failures
