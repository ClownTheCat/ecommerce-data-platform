select
    date(created_at) as date,
    sum(total_amount) as revenue,
    count(order_id) as orders_count
from public.orders
where status in ('paid','shipped','delivered')
group by date(created_at)
order by date