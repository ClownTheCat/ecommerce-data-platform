import os
import sys
import psycopg
from dotenv import load_dotenv
from pathlib import Path


load_dotenv()



MIGRATIONS_DIR=Path(__file__).resolve().parent.parent / 'migrations'

conn_info = {
    'host': os.getenv('POSTGRES_HOST'),
    'port': int(os.getenv('POSTGRES_PORT',5433)),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'dbname': os.getenv('POSTGRES_DB')
}

def ensure_migrations_table(cur):
    cur.execute("""
        create table if not exists migrations(
            filename text primary key,
            applied_at timestamp default current_timestamp

        );
""")


def already_applied(cur, filename):
    cur.execute('select 1 from migrations where filename=%s',(filename,))
    return cur.fetchone() is not None

def apply_one(cur, filename, sql):
    cur.execute(sql)
    cur.execute('insert into migrations (filename) values (%s)', (filename,))

def main():
    if not MIGRATIONS_DIR.exists():
        print(f'ОШИБКА: Папка {MIGRATIONS_DIR} не найдена')
        sys.exit(1)

    files = sorted(MIGRATIONS_DIR.glob('*.sql'))
    print("Подключаюсь к базе: ",conn_info['dbname'])

    with psycopg.connect(**conn_info) as conn:
        with conn.cursor() as cur:
            ensure_migrations_table(cur)
            conn.commit()
            for path in files:
                filename=path.stem
                if already_applied(cur,filename):
                    print(f'-> {filename} уже применена, пропускаю')
                    continue
                print(f'-> Применяю {filename}...')
                sql=path.read_text(encoding='utf-8')
                apply_one(cur, filename, sql)
                conn.commit()
                print(f'✅ {filename} применена')
            print('Все миграции применены')





if __name__=='__main__':
    main()
    