# Databricks — Churn Prediction (batch scoring)
# Weekly batch score; writes to MART_PRODUCT.CHURN_SCORES

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml.classification import GBTClassifier
from pyspark.ml.feature import VectorAssembler
from pyspark.ml import Pipeline
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--env", default="prod")
args = parser.parse_args()

spark = SparkSession.builder.appName("atlas-churn-scoring").getOrCreate()

sf = {
    "sfDatabase": f"ANALYTICS_{args.env.upper()}",
    "sfSchema": "MART_PRODUCT",
    "sfWarehouse": f"WH_ML_{args.env.upper()}",
}

# Feature matrix from Snowflake marts
features_df = spark.read.format("snowflake").options(**sf).option(
    "query", """
        SELECT
            e.account_id,
            AVG(e.dau) AS avg_dau,
            AVG(e.mau) AS avg_mau,
            MAX(r.arr_usd) AS arr_usd,
            DATEDIFF(CURRENT_DATE(), MAX(e.activity_date)) AS days_since_active
        FROM MART_PRODUCT__DAILY_ENGAGEMENT e
        LEFT JOIN MART_FINANCE__MONTHLY_REVENUE r ON e.account_id = r.account_id
        GROUP BY e.account_id
    """
).load()

# Training labels from historical churn (subscription canceled)
labels = spark.read.format("snowflake").options(**sf).option(
    "query", """
        SELECT account_id, CASE WHEN canceled_at IS NOT NULL THEN 1 ELSE 0 END AS churned
        FROM INT_SUBSCRIPTION_MRR
    """
).load()

train = features_df.join(labels, "account_id", "inner").fillna(0)

assembler = VectorAssembler(
    inputCols=["avg_dau", "avg_mau", "arr_usd", "days_since_active"],
    outputCol="features",
)
classifier = GBTClassifier(labelCol="churned", featuresCol="features", maxIter=50)
pipeline = Pipeline(stages=[assembler, classifier])
model = pipeline.fit(train)

scores = model.transform(features_df).select(
    "account_id",
    F.col("prediction").alias("churn_predicted"),
    F.col("probability").getItem(1).alias("churn_probability"),
    F.current_timestamp().alias("scored_at"),
)

scores.write.format("snowflake").options(**sf).option(
    "dbtable", "CHURN_SCORES"
).mode("overwrite").save()
