from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

app=FastAPI(title="E-commerce Data Platform API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

conn_info = {
    'host': os.getenv('POSTGRES_HOST'),
    'port':  os.getenv('POSTGRES_PORT',int(5433)),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'dbname':os.getenv('POSTGRES_DB')
}


@app.get('/api/sales')
def get_daily_sales():
    try:
        with psycopg.connect(**conn_info) as conn:
            with conn.cursor() as cur:
                cur.execute("select date, revenue, orders_count from dbt_dev.daily_sales order by date asc")

                rows=cur.fetchall()

                result=[]
                for row in rows:
                    result.append({
                        'date': str(row[0]),
                        'revenue': float(row[1]),
                        'orders_count':int(row[2])
                    })
                return result
    except Exception as e:
        return {"error":str(e)}

@app.get("/api/status")
def get_status():
    return {'status': 'ok','message':'API работает!'}



@app.get('/api/events')
def get_event_analytics():
    try:
        with psycopg.connect(**conn_info) as conn:
            with conn.cursor() as cur:
                cur.execute("select event_type, event_count from dbt_dev.event_analytics")
                
                rows=cur.fetchall()

                result=[]
                for row in rows:
                    result.append({
                        'event_type':row[0],
                        'event_count':int(row[1])
                    })
                return result
    except Exception as e:
        return {"error":str(e)}


if __name__ == '__main__':
    import uvicorn
    print('🚀 Запускаю API сервер на http://localhost:8000')
    uvicorn.run(app,host='0.0.0.0',port=8000)