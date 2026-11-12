select
    event_type,
    count(*) as event_count
from public.user_events
group by event_type
order by event_count desc