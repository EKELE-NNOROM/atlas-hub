# Databricks — Customer Segmentation
# Job: atlas-customer-segmentation
# Reads Snowflake marts, writes segments back to ANALYTICS_PROD.MART_PRODUCT.CUSTOMER_SEGMENTS

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.cluster import KMeans
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--env", default="prod")
parser.add_argument("--run_date", required=True)
args = parser.parse_args()

spark = SparkSession.builder.appName("atlas-customer-segmentation").getOrCreate()

sf_options = {
    "sfURL": spark.conf.get("spark.databricks.secrets.atlas.snowflake.url"),
    "sfUser": spark.conf.get("spark.databricks.secrets.atlas.snowflake.user"),
    "sfPassword": spark.conf.get("spark.databricks.secrets.atlas.snowflake.password"),
    "sfDatabase": f"ANALYTICS_{args.env.upper()}",
    "sfSchema": "MART_PRODUCT",
    "sfWarehouse": f"WH_ML_{args.env.upper()}",
}

engagement = spark.read.format("snowflake").options(**sf_options).option(
    "dbtable", "MART_PRODUCT__DAILY_ENGAGEMENT"
).load()

revenue = spark.read.format("snowflake").options(**sf_options).option(
    "dbtable", "MART_FINANCE__MONTHLY_REVENUE"
).load()

features = (
    engagement.groupBy("account_id")
    .agg(
        F.avg("dau").alias("avg_dau"),
        F.avg("mau").alias("avg_mau"),
        F.max("activity_date").alias("last_active"),
    )
    .join(
        revenue.groupBy("account_id").agg(F.max("arr_usd").alias("arr_usd")),
        "account_id",
        "left",
    )
    .fillna({"avg_dau": 0, "avg_mau": 0, "arr_usd": 0})
    .withColumn("dau_mau_ratio", F.col("avg_dau") / F.greatest(F.col("avg_mau"), F.lit(1)))
)

assembler = VectorAssembler(
    inputCols=["avg_dau", "avg_mau", "arr_usd", "dau_mau_ratio"],
    outputCol="features_raw",
)
scaled = StandardScaler(inputCol="features_raw", outputCol="features").fit(assembler.transform(features))

model = KMeans(k=5, seed=42, featuresCol="features").fit(scaled.transform(assembler.transform(features)))

segments = model.transform(scaled.transform(assembler.transform(features))).select(
    "account_id",
    F.col("prediction").alias("segment_id"),
    F.lit(args.run_date).alias("scored_at"),
)

segment_names = spark.createDataFrame([
    (0, "dormant"), (1, "low_touch"), (2, "growth"), (3, "power_user"), (4, "enterprise")
], ["segment_id", "segment_name"])

output = segments.join(segment_names, "segment_id").drop("segment_id")

output.write.format("snowflake").options(**sf_options).option(
    "dbtable", "CUSTOMER_SEGMENTS"
).mode("overwrite").save()

print(f"Segmentation complete: {output.count()} accounts")
