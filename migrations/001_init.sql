create table if not exists categories (
    category_id serial primary key,
    name varchar(100) not null unique
    
);
create table if not exists warehouses (
    warehouse_id serial primary key,
    name varchar(100) not null unique,
    city varchar(100) not null
    
);

create table if not exists customers(
    customer_id serial primary key,
    first_name varchar(100) not null,
    email varchar(255) not null unique,
    city varchar(100),
    created_at timestamp not null default now(),
    updated_at timestamp not null default now()
);


create table if not exists products(
    product_id serial primary key,
    category_id int not null references categories(category_id),
    product_name varchar(100) not null,
    price numeric(10,2) not null check (price >= 0),
    is_active boolean not null default true,
    created_at timestamp not null default now(),
    updated_at timestamp not null default now()
);

create table if not exists orders(
    order_id serial primary key,
    customer_id int not null references customers(customer_id),
    status varchar(50) not null,
    total_amount numeric(10,2) not null,
    currency char(3) not null,
    created_at timestamp not null default now(),
    updated_at timestamp not null default now()

);
create table if not exists order_items(
    order_id int not null references orders(order_id) on delete cascade,
    product_id int not null references products(product_id),
    quantity int not null check (quantity > 0),
    unit_price numeric(10,2) not null check (unit_price >= 0),
    primary key (order_id, product_id)

);

create table if not exists payments(
    payment_id serial primary key,
    order_id int not null references orders(order_id),
    amount numeric(12,2) not null,
    status varchar(50) not null,
    method varchar(50) not null,
    paid_at timestamp,
    provider_transaction_id varchar(100)
);




create table if not exists refunds(
    refund_id serial primary key,
    payment_id int not null references payments(payment_id),
    amount numeric(12,2) not null check (amount > 0),
    reason varchar(255),
    created_at timestamp not null default now()

);


create table if not exists deliveries(
    delivery_id serial primary key,
    order_id int not null references orders(order_id) on delete cascade,
    delivery_service varchar(100) not null,
    tracking_number varchar(100) unique,
    status varchar(20) not null check (status in ('created', 'picked_up', 'in_transit', 'delivered', 'failed')),
    address varchar(500),
    shipped_at timestamp,
    delivered_at timestamp
);


create table if not exists inventory(
    product_id int not null references products(product_id),
    warehouse_id int not null references warehouses(warehouse_id),
    quantity int not null check (quantity >= 0),
    snapshot_at timestamp not null default now(),
    primary key (product_id, warehouse_id, snapshot_at)

);


create table if not exists user_events(
    event_id uuid primary key default gen_random_uuid(),
    user_id int references customers(customer_id),
    session_id uuid default gen_random_uuid() not null,
    event_type varchar(50) not null,
    product_id int references products(product_id),
    event_timestamp timestamp not null,
    properties jsonb
);

create table if not exists marketing_campaigns (
    campaign_id serial primary key,
    channel varchar(50) not null,
    name varchar(255) not null,
    spend numeric(12,2) not null check (spend >= 0),
    impressions int not null default 0,
    clicks int not null default 0,
    date date not null
);


