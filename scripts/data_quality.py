import sys
import pandas as pd
from pathlib import Path



SILVER_DIR = Path(__file__).resolve().parent.parent / 'data' / 'silver'


def check_customers():
    df=pd.read_parquet(SILVER_DIR/'customers.parquet')

    if df['email'].duplicated().any():
        print('[DATA QUALITY][ОШИБКА] Найдены дупликаты email в ⟪customers⟫!❌❌❌ (ノಠ益ಠ)ノ彡┻━┻')
        sys.exit(1)
    else:
        print('[DATA QUALITY] В ⟪customers⟫ дупликатов нет! ^_^ ✅')


def check_products():
    df=pd.read_parquet(SILVER_DIR/'products.parquet')
    if (df['price']<0).any():
        print('[DATA QUALITY][ОШИБКА] Найдены минусовые цены на продукты в ⟪products⟫!❌❌❌ (ノಠ益ಠ)ノ彡┻━┻')
        sys.exit(1)
    else:
        print('[DATA QUALITY] В ⟪products⟫ минусовых цен нет! ^_^ ✅')


def check_orders():
    df=pd.read_parquet(SILVER_DIR/'orders.parquet')
    if df['total_amount'].isnull().any():
        print('[DATA QUALITY][ОШИБКА] Найдены total_amount NONE в ⟪orders⟫!❌❌❌ (ノಠ益ಠ)ノ彡┻━┻')
        sys.exit(1)
    else:
        print('[DATA QUALITY] В ⟪orders⟫ total_amount NONE нет! ^_^ ✅')

def main():
    print('[DATA QUALITY] ᓚᘏᗢ Запускаю проверки качества данных...')
    check_customers()
    check_products()
    check_orders()
    print("[DATA QUALITY] Все проверки пройдены! Данные чистые, можно строить Gold.🎉( •̀ ω •́ )✧ 🎉")




if __name__=='__main__':
    main()