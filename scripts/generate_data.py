import os
import sys
import psycopg
import time
import uuid
from psycopg.types.json import Jsonb
from dotenv import load_dotenv
from faker import Faker
import random


load_dotenv()
fake=Faker('ru_RU')

conn_info={
    'host':os.getenv('POSTGRES_HOST'),
    'port':int(os.getenv('POSTGRES_PORT',5433)),
    'user':os.getenv('POSTGRES_USER'),
    'password':os.getenv('POSTGRES_PASSWORD'),
    'dbname':os.getenv('POSTGRES_DB'),
}

def insert_many_customers(cur, count=100):
    data=[]
    timestamp=int(time.time())
    for i in range(count):
        unique_email=f"{timestamp}_{i}_{fake.email()}"
        data.append((
            fake.first_name(),
            unique_email,
            fake.city()
        ))
    cur.executemany("""
        insert into customers(first_name,email,city) values
        (%s,%s,%s) on conflict (email) do nothing;
""", data)
    print(f'[DATA GENERATOR] В базу добавлено {count} клиентов! :-) ')

    
def insert_categories(cur, count=1):
    data=[]
    for _ in range(count):
        unique_cat = f"{fake.unique.word().capitalize()}_{uuid.uuid4().hex[:3]}"
        data.append((
            unique_cat,
        ))
    cur.executemany("insert into categories (name) values (%s)",data)
    print(f'[DATA GENERATOR] В базу добавлено {count} категорий! :-) ')
    
def get_category_ids(cur):
    cur.execute("select category_id from categories;")
    return [row[0] for row in cur.fetchall()]

def insert_products(cur,count=1000):
    cat_ids=get_category_ids(cur)
    data=[]
    for _ in range(count):
        data.append((random.choice(cat_ids),fake.catch_phrase(),fake.random_int(min=10,max=100000)))
    cur.executemany("insert into products(category_id,product_name,price) values (%s,%s,%s)",data)
    print(f'[DATA GENERATOR] В базу добавлено {count} продуктов! :-) ')

    # return [row[0] for row in cur.fetchall()]
def insert_orders(cur, count=1000):
    cur.execute("select customer_id from customers;")
    customer_ids=[row[0] for row in cur.fetchall()]

    cur.execute("select product_id,price from products;")
    products=cur.fetchall()

    statuses = ['created', 'paid', 'shipped', 'delivered', 'cancelled']

    for _ in range(count):
        customer_id=random.choice(customer_ids)
        status=random.choice(statuses)    
        currency='RUB'

        items_count = random.randint(1,3)
        chosen_products = random.sample(products, k=items_count)

        total_amount=0.0
        order_items_data=[]

        for prod_id,price in chosen_products:
            quantity=random.randint(1,3)
            item_price=float(price)

            total_amount+=quantity*item_price

            order_items_data.append([prod_id,quantity,item_price])

        cur.execute("""
            insert into orders (customer_id,status,total_amount,currency) values(%s,%s,%s,%s) returning order_id
        """, (customer_id,status,round(total_amount,2),currency))
        order_id=cur.fetchone()[0]

        final_items=[]
        for item in order_items_data:
            final_items.append((order_id,item[0],item[1],item[2]))
        cur.executemany("""
            insert into order_items(order_id,product_id,quantity,unit_price) values
            (%s,%s,%s,%s)
        """,final_items)
    print(f'[GENERATOR] Успешно создано {count} заказов и их позиций! :-)')

def insert_warehouses(cur,count=5):
    data=[]
    for i in range(count):
        unique_name = f"Склад {i}_{uuid.uuid4().hex[:4]}" 
        data.append((
            unique_name,
            fake.city()
        ))
    cur.executemany("""
        insert into warehouses(name,city) values(%s,%s)
    """,data)
    print(f'[DATA GENERATOR] В базу добавлено {count} новых складов! :-) ')

def insert_inventory(cur):
    cur.execute("""
        select product_id from products
    """)
    product_ids=[row[0] for row in cur.fetchall()]

    cur.execute("""
        select warehouse_id from warehouses
    """)
    warehouse_ids=[row[0] for row in cur.fetchall()]

    data=[]
    for p_id in product_ids:
        for w_id in warehouse_ids:
            qty=random.randint(0,500)
            data.append((p_id,w_id,qty))
    
    cur.executemany("""
        insert into inventory(product_id,warehouse_id,quantity) values(%s,%s,%s)
    """,data)
    print(f'[DATA GENERATOR] продукты зарегестрированы на складе!')
    
def insert_marketing_campaigns(cur,count=20):
    channel=['vk', 'google', 'yandex', 'email']
    data=[]
    for i in range(count):
        spend=fake.random_int(1000,50000)
        impressions=fake.random_int(10000,1000000)
        clicks=fake.random_int(100 ,50000)
        date=fake.date_this_year()
        data.append((
            fake.random_element(channel),
            f'campaign {i}',
            spend,impressions,clicks,date


        ))
    cur.executemany("""
        insert into marketing_campaigns(channel,name,spend,impressions,clicks,date) values
        (%s,%s,%s,%s,%s,%s)
    """,data)
    print(f'[DATA GENERATOR] В базу добавлены новые маркетинговые партнеры!')

def insert_payments(cur):
    method=['card','sbp']
    data=[]
    cur.execute("select order_id,total_amount,status from orders where order_id not in (select order_id from payments)")
    orders=cur.fetchall()
    for order_id,amount,status in orders:
        if status=='cancelled':
            payment_status='failed'
            paid_at=None
        else:
            payment_status='succeeded'
            paid_at=fake.date_time_this_year()
        data.append((
            order_id,
            amount,
            payment_status,
            fake.random_element(method),
            paid_at,
            fake.uuid4()
        ))
    cur.executemany("""insert into payments(order_id,amount,status,method,paid_at,provider_transaction_id) values(%s,%s,%s,%s,%s,%s) 
    """,data)
    print(f'[DATA GENERATOR] В базу добавлены новые платежи!')


def insert_deliveries(cur):
    data=[]

    cur.execute("select order_id from orders;")
    order_ids=[row[0] for row in cur.fetchall()]
    
    delivery_service=['СДЭК','Почта','Boxberrry']
    
    status=['created', 'picked_up', 'in_transit', 'delivered', 'failed']
   
    
    for order_id in order_ids:
        is_deliv=random.random()<0.2
        if is_deliv:
            shipped_at=None
            delivered_at=None
        else:
            shipped_at=fake.date_time_this_year()
            delivered_at=fake.date_time_this_year()
        data.append((
            order_id,
            fake.random_element(delivery_service),
            fake.uuid4(),
            fake.random_element(status),
            fake.address(),
            shipped_at,
            delivered_at
        ))
    cur.executemany("""
        insert into deliveries(order_id,delivery_service,tracking_number,status,address,shipped_at,delivered_at) values(%s,%s,%s,%s,%s,%s,%s)
    """,data)
    print(f'[DATA GENERATOR] В базу добавлены новые доставки!')

def insert_refunds(cur):
    data=[]
    cur.execute("select payment_id,amount from payments where status='succeeded';")
    payments=cur.fetchall()
    sample_size=int(len(payments)*0.1)
    if sample_size>0:
        payments_to_refund = random.sample(payments,sample_size)
        for payment_id,amount in payments_to_refund:
            nums=[0.5,0.3,0.8]
            refund_amount=float(amount)*random.choice(nums)
            data.append((
                payment_id,
                refund_amount,
                fake.sentence()
            ))
        cur.executemany("""
            insert into refunds(payment_id,amount,reason) values(%s,%s,%s)
        """,data)
    print(f'[DATA GENERATOR] В базу добавлены новые возвраты!')
def insert_user_events(cur,count=1000):
    data=[]
    cur.execute("select customer_id from customers;")
    customer_ids=[row[0] for row in cur.fetchall()]
    cur.execute("select product_id from products;")
    product_ids=[row[0] for row in cur.fetchall()]
    properties =Jsonb({"source": "google"})
    event_type=['product_view', 'add_to_cart', 'search', 'purchase']
    if not customer_ids:
        print("ОШИБКА: В базе нет клиентов. Сначала сгенерируйте клиентов.")
        sys.exit(1)
    for _ in range(count):
        is_anonymous=random.random()<0.3
        if is_anonymous:
            customer_id=None
        else:
            customer_id=random.choice(customer_ids)
        data.append((
            customer_id,
            fake.uuid4(),
            fake.random_element(event_type),
            fake.random_element(product_ids),
            fake.date_time_this_year(),
            properties
        ))
    cur.executemany("""
        insert into user_events(user_id,session_id,event_type,product_id,event_timestamp,properties) values
        (%s,%s,%s,%s,%s,%s)
    """,data)
    print(f'[DATA GENERATOR] В базу добавлены новые действия пользователей!')




def main():
    try:
        with psycopg.connect(**conn_info) as conn:
            
            print(f'Подключение {__file__} к базе {conn_info["dbname"]} прошло успешно!')
            with conn.cursor() as cur:
                insert_many_customers(cur,1000)#создаем customer'ов
                insert_categories(cur,10)#создаем категории
                insert_products(cur,1000)
                insert_orders(cur, 500)
                insert_warehouses(cur,5)
                insert_inventory(cur)
                insert_marketing_campaigns(cur,20)
                insert_payments(cur)
                insert_deliveries(cur)
                insert_refunds(cur)
                insert_user_events(cur,1000)
                conn.commit()
    except Exception as err:
        print(f'[ОШИБКА] Скрипт: {__file__} нихуя не подключился к базе: {conn_info["dbname"]}')
        print(err)
        sys.exit(1)



if __name__=='__main__':
    main()