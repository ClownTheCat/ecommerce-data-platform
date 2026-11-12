import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col,count, sum as _sum
import sys

os.environ["HADOOP_HOME"] = r"C:\hadoop"
os.environ["hadoop.home.dir"] = r"C:\hadoop"

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT","http://localhost:9000")
ACCESS_KEY = "minioadmin"
SECRET_KEY = "minioadmin"


def main():
    print('🚀 Запуск Apache Spark...')

    spark = SparkSession.builder \
        .appName("MinIO_S3_Read") \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262") \
        .config("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT) \
        .config("spark.hadoop.fs.s3a.access.key", ACCESS_KEY) \
        .config("spark.hadoop.fs.s3a.secret.key", SECRET_KEY) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .config("spark.hadoop.fs.s3a.connection.timeout", "60000") \
        .config("spark.hadoop.fs.s3a.connection.establish.timeout", "60000") \
        .config("spark.hadoop.fs.s3a.socket.timeout", "60000") \
        .getOrCreate()

    try:
        print("Читаю orders.parquet из MinIO... ᓚᘏᗢ")
        df=spark.read.parquet("s3a://bronze/orders.parquet")

        print(" Считаю статистику по статусам... ᓚᘏᗢ")
        agg_df = df.groupBy('status').agg(
            count('order_id').alias('total_orders'),
            _sum('total_amount').alias('total_revenue')
        )
        agg_df.show()

        print("Сохраняю результат в silver... ( •̀ ω •́ )✧")
        agg_df.write.mode('overwrite').parquet("s3a://bronze/orders_by_status_spark")


    except Exception as err:
        print(f'❌ Ошибка Spark: {err}     (┬┬﹏┬┬)')
        sys.exit(1)
    finally:
        spark.stop()


if __name__ == '__main__':
    main()