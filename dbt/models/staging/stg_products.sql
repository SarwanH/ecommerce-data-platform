with source as (
    select * from {{ source('raw', 'products') }}
),

renamed as (
    select
        product_id,
        sku,
        product_name,
        category,
        subcategory,
        brand,
        unit_price,
        unit_cost,
        weight_lbs,
        is_active,
        created_at,
        updated_at,
        round(unit_price - unit_cost, 2) as gross_margin,
        round((unit_price - unit_cost) / nullif(unit_price, 0) * 100, 2) as margin_pct
    from source
)

select * from renamed