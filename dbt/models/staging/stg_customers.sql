select
    customer_id,
    first_name,
    lower(trim(email)) as email,
    coalesce(city,'Unknown') as city,
    created_at,
    updated_at
from public.customers