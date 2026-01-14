with transactions as (
    select * from {{ ref('stg_transactions') }}
),

products as (
    select product_id, unit_cost from {{ ref('stg_products') }}
)

select
    t.transaction_id,
    t.order_id,
    t.customer_id,
    t.store_id,
    t.product_id,
    t.transaction_date,
    t.transaction_day,
    t.transaction_month,
    t.day_of_week,
    t.is_weekend,
    t.quantity,
    t.unit_price,
    t.discount_amount,
    t.total_amount,
    t.order_status,
    t.channel,
    t.fulfillment_type,
    p.unit_cost,
    t.quantity * p.unit_cost as line_cost,
    t.total_amount - (t.quantity * p.unit_cost) as line_profit
from transactions t
left join products p on t.product_id = p.product_id