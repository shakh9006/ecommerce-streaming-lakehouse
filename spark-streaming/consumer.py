import os
import dotenv
import json
import logging

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_date, current_timestamp, to_json
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, MapType

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AWS_REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")
S3_BUCKET = os.getenv("S3_BUCKET")

logger.info(f"AWS_REGION: {AWS_REGION}")
logger.info(f"AWS_ACCESS_KEY_ID: {AWS_ACCESS_KEY_ID}")
logger.info(f"AWS_SECRET_ACCESS_KEY: {AWS_SECRET_ACCESS_KEY}")
logger.info(f"S3_BUCKET: {S3_BUCKET}")
logger.info(f"KAFKA_BOOTSTRAP_SERVERS: {KAFKA_BOOTSTRAP_SERVERS}")
logger.info(f"KAFKA_TOPIC: {KAFKA_TOPIC}")

logger.info("Starting Spark Session...")

spark = (
    SparkSession
    .builder
    .appName("Ecommerce Analytics")
    .config("spark.master", "local[2]")
    .config("spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions,"
            "org.projectnessie.spark.extensions.NessieSparkSessionExtensions")
    .config("spark.sql.defaultCatalog", "nessie")
    .config("spark.sql.catalog.nessie", "org.apache.iceberg.spark.SparkCatalog")
    .config("spark.sql.catalog.nessie.catalog-impl", "org.apache.iceberg.nessie.NessieCatalog")
    .config("spark.sql.catalog.nessie.uri", "http://nessie:19120/api/v2")
    .config("spark.sql.catalog.nessie.ref", "main")
    .config("spark.sql.catalog.nessie.warehouse", f"s3a://ecommerce-warehouse")
    .config("spark.sql.catalog.nessie.authentication.type", "NONE")
    .config("spark.sql.catalog.nessie.io-impl", "org.apache.iceberg.aws.s3.S3FileIO")
    .config("spark.sql.catalog.nessie.s3.endpoint", "http://minio:9000")
    .config("spark.sql.catalog.nessie.s3.path-style-access", "true")
    .config("spark.sql.catalog.nessie.s3.region", AWS_REGION)
    .config("spark.sql.catalog.nessie.s3.access-key-id", AWS_ACCESS_KEY_ID)
    .config("spark.sql.catalog.nessie.s3.secret-access-key", AWS_SECRET_ACCESS_KEY)
    .getOrCreate()
)

location_schema = StructType([
    StructField("city", StringType(), False),
    StructField("state", StringType(), False),
    StructField("country", StringType(), False),
])

event_data_schema = MapType(StringType(), StringType())

event_schema = StructType([
    StructField("event_id", StringType(), False),
    StructField("event_type", StringType(), False),
    StructField("event_timestamp", StringType(), False),
    StructField("user_id", StringType(), False),
    StructField("username", StringType(), False),
    StructField("session_id", StringType(), False),
    StructField("device", StringType(), False),
    StructField("location", location_schema, False),
    StructField("event_data", event_data_schema, False),
])

raw_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
    .option("subscribe", KAFKA_TOPIC)
    .option("startingOffsets", "earliest")
    .option("failOnDataLoss", "false")
    .load()
)

parsed_df = (
    raw_df.selectExpr("CAST(value AS STRING) as json_str")
    .select(from_json(col("json_str"), event_schema).alias("data"))
    .select(
        col("data.event_id"),
        col("data.event_type"),
        col("data.event_timestamp").cast(TimestampType()).alias("event_timestamp"),
        to_date(col("data.event_timestamp")).alias("event_date"),
        col("data.user_id"),
        col("data.username"),
        col("data.session_id"),
        col("data.device"),
        col("data.location"),
        to_json(col("data.event_data")).alias("event_data"),
        current_timestamp().alias("ingestion_timestamp")

    )
)

spark.sql("CREATE NAMESPACE IF NOT EXISTS nessie.raw")

spark.sql("""
    CREATE TABLE IF NOT EXISTS nessie.raw.events (
        event_id STRING,
        event_type STRING,
        event_timestamp TIMESTAMP,
        event_date DATE,
        user_id STRING,
        username STRING,
        session_id STRING,
        device STRING,
        location STRUCT<
            city: STRING,
            state: STRING,
            country: STRING
        >,
        event_data STRING,
        ingestion_timestamp TIMESTAMP
    )
    USING iceberg
    PARTITIONED BY (event_date, event_type)
    TBLPROPERTIES (
        'format-version'='2',
        'write.metadata.delete-after-commit.enabled'='true',
        'write.metadata.previous-versions-max'='3',
        'history.expire.max-snapshot-age-ms'='1800000',
        'history.expire.min-snapshots-to-keep'='3',
        'write.metadata.metrics.default'='4'
    )
""")

checkpoint = "/opt/checkpoints/raw.events"

logger.info("Starting streaming write to Iceberg table...")
query = (
    parsed_df.writeStream
    .format("iceberg")
    .outputMode("append")
    .option("checkpointLocation", checkpoint)
    .option("fanout-enabled", "true")
    .trigger(processingTime="10 seconds")
    .toTable("nessie.raw.events")
)

logger.info("Streaming started successfully!")
logger.info(f"Writing to: nessie.raw.events")
logger.info(f"Checkpoint: {checkpoint}")
query.awaitTermination()
