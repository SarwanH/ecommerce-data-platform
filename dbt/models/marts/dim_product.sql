select
    product_id,
    sku,
    product_name,
    category,
    subcategory,
    brand,
    unit_price,
    unit_cost,
    gross_margin,
    margin_pct,
    weight_lbs,
    is_active,
    created_at,
    updated_at
from {{ ref('stg_products') }}