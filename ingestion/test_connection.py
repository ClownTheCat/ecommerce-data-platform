import os
import psycopg
from dotenv import load_dotenv


def main():
    load_dotenv()
    with psycopg.connect(
   
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv('POSTGRES_PORT', 5432)),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB'),

    ) as conn:


        with conn.cursor() as cur:
            cur.execute("SELECT count(*) from pg_tables where schemaname='public';")
            total=cur.fetchone()
            print(f'Таблиц в public: {total}')



if __name__ == "__main__":
    main()