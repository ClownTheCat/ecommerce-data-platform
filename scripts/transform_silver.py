import sys
import os
import pandas as pd
from pathlib import Path
from psycopg import sql




DATA_SILVER_DIRECTORY = Path(__file__).resolve().parent.parent /'data'/'silver'
DATA_SILVER_DIRECTORY.mkdir(parents=True,exist_ok=True)

DATA_BRONZE_DIRECTORY=Path(__file__).resolve().parent.parent / 'data' / 'bronze'
DATA_BRONZE_DIRECTORY.mkdir(parents=True,exist_ok=True)



def transform_data():
    files=sorted(DATA_BRONZE_DIRECTORY.glob('*.parquet'))
    if not files:
        print(f'[SILVER BUILDER] Файлов parquet в {DATA_BRONZE_DIRECTORY} не обнаружено')
        return
    for bronze_file in files:
        df=pd.read_parquet(bronze_file)
        
        if bronze_file.stem == 'customers':
            df['email']=df['email'].apply(lambda x: str(x).lower().strip())
            df['city']=df['city'].fillna('Unknown')

        if bronze_file.stem == 'user_events':
            df.drop_duplicates(subset='event_id',keep='last',inplace=True)

        if bronze_file.stem == 'orders':
            df.drop(columns=['updated_at'], inplace=True)

        if bronze_file.stem == 'products':
            df=df[df['is_active'] == True]
        
        df.to_parquet(DATA_SILVER_DIRECTORY/bronze_file.name,index=False)
        print(f'[SILVER BUILDER] ✅ Таблица ⟪{bronze_file.name}⟫ очищена и сохранена! ( •̀ ω •́ )✧')
        




def main():
    print('[SILVER BUILDER] ᓚᘏᗢ Начинаю отчистку Silver-слоя')
    try:
        transform_data()
        print(f'[SILVER BUILDER] ( •̀ ω •́ )✧ Все данные очищены!')
    except Exception as err:
        print(f'[SILVER BUILDER][ОШИБКА] Скрипт упау: {err} (┬┬﹏┬┬)')



if __name__=='__main__':
    main()