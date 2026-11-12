import sys
import os
import pandas as pd
from pathlib import Path
from psycopg import sql


DATA_GOLD_DIRECTORY = Path(__file__).resolve().parent.parent /'data'/'gold'
files=sorted(DATA_GOLD_DIRECTORY.glob('*.parquet'))
for file in files:
    print(file.name)
    print('-'*60)
    df=pd.read_parquet(DATA_GOLD_DIRECTORY/file)
    print(df)
    print('-'*60)