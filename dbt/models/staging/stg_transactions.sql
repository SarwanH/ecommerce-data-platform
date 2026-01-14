with source as (
    select * from {{ source('raw', 'transactions') }}
)

select
    transaction_id,
    order_id,
    customer_id,
    store_id,
    product_id,
    transaction_date,
    quantity,
    unit_price,
    discount_amount,
    total_amount,
    order_status,
    channel,
    fulfillment_type,
    date_trunc('day', transaction_date) as transaction_day,
    date_trunc('month', transaction_date) as transaction_month,
    extract(dow from transaction_date) as day_of_week,
    case when extract(dow from transaction_date) in (0, 6) then true else false end as is_weekend
from source