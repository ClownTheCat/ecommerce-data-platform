import sys
import os
import pandas as pd
from pathlib import Path
from psycopg import sql


DATA_SILVER_DIRECTORY = Path(__file__).resolve().parent.parent /'data'/'silver'
DATA_SILVER_DIRECTORY.mkdir(parents=True,exist_ok=True)

DATA_GOLD_DIRECTORY = Path(__file__).resolve().parent.parent /'data'/'gold'
DATA_GOLD_DIRECTORY.mkdir(parents=True,exist_ok=True)


def build_gold():
    files=sorted(DATA_SILVER_DIRECTORY.glob('*.parquet'))
    if not files:
        print(f'[GOLD BUILDER] Файлов parquet в {DATA_SILVER_DIRECTORY} не обнаружено')
        return
    
    orders=pd.read_parquet(DATA_SILVER_DIRECTORY/'orders.parquet')
    valid_statuses=['paid','shipped','delivered']
    orders=orders[orders['status'].isin(valid_statuses)]
    orders['date']= pd.to_datetime(orders['created_at']).dt.date
    daily = orders.groupby('date').agg(
        revenue=('total_amount','sum'),
        orders_count=('order_id','count')
    ).reset_index()
    daily.to_parquet(DATA_GOLD_DIRECTORY/'daily_sales.parquet',index=False)
    print("[GOLD BUILDER] daily_sales готов! ( •̀ ω •́ )✧")



    products=pd.read_parquet(DATA_SILVER_DIRECTORY/'products.parquet')
    order_items=pd.read_parquet(DATA_SILVER_DIRECTORY/'order_items.parquet')

    orders_merged=pd.merge(order_items,orders,on='order_id',how='left')
    orders_merged=orders_merged[orders_merged['status'].isin(valid_statuses)]
    merged_tables=pd.merge(products,orders_merged,on='product_id',how='inner')
    merged_tables['item_revenue']=merged_tables['quantity']*merged_tables['unit_price']


    top_products = merged_tables.groupby('product_name').agg(
        item_revenue=('item_revenue','sum'),
        quantity_sold = ('quantity','sum')
    ).reset_index()
    top_products=top_products.sort_values(by='item_revenue',ascending=False).head(10)
    top_products.to_parquet(DATA_GOLD_DIRECTORY/'top_products.parquet',index=False)
    print("[GOLD BUILDER] top_products готов! ( •̀ ω •́ )✧")







def main():
    print('[GOLD BUILDER]ᓚᘏᗢ Начинаю создание витрин..')
    try:
        build_gold()
        print(f'[GOLD BUILDER]( •̀ ω •́ )✧ Все витрины созданы!')
    except Exception as err:
        print(f'[GOLD BUILDER][ОШИБКА] Скрипт упау: {err} (┬┬﹏┬┬)')



if __name__=='__main__':
    main()