# Data Dictionary

## Fact Tables

### fact_sales
Sales transactions with profit calculations.

| Column | Type | Description |
|--------|------|-------------|
| transaction_id | string | Unique identifier |
| order_id | string | Order grouping |
| customer_id | string | FK to dim_customer |
| product_id | string | FK to dim_product |
| quantity | int | Units sold |
| total_amount | decimal | Revenue |
| line_profit | decimal | Calculated profit |

## Dimension Tables

### dim_product
Product master data.

| Column | Type | Description |
|--------|------|-------------|
| product_id | string | Primary key |
| category | string | Department |
| brand | string | Manufacturer |
| unit_price | decimal | Retail price |
| margin_pct | decimal | Profit margin % |