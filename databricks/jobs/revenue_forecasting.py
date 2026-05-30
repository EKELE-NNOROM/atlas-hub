# Databricks — Revenue Forecasting (Prophet-style via Spark ML)
# Writes forecast to MART_FINANCE.REVENUE_FORECAST

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--env", default="prod")
parser.add_argument("--horizon_months", type=int, default=12)
args = parser.parse_args()

spark = SparkSession.builder.appName("atlas-revenue-forecast").getOrCreate()

sf = {"sfDatabase": f"ANALYTICS_{args.env.upper()}", "sfSchema": "MART_FINANCE"}

history = spark.read.format("snowflake").options(**sf).option(
    "query", """
        SELECT revenue_month, SUM(arr_usd) AS total_arr
        FROM MART_FINANCE__MONTHLY_REVENUE
        GROUP BY revenue_month
        ORDER BY revenue_month
    """
).load()

# Simple exponential smoothing forecast (production: swap for Prophet/ARIMA via pandas UDF)
window = Window.orderBy("revenue_month")
with_growth = history.withColumn(
    "mom_growth",
    (F.col("total_arr") - F.lag("total_arr").over(window)) / F.lag("total_arr").over(window),
)
avg_growth = with_growth.agg(F.avg("mom_growth").alias("g")).collect()[0]["g"] or 0.02
last_arr = history.orderBy(F.desc("revenue_month")).first()["total_arr"]

forecasts = []
for i in range(1, args.horizon_months + 1):
    projected = last_arr * ((1 + avg_growth) ** i)
    forecasts.append((i, projected))

forecast_df = spark.createDataFrame(forecasts, ["months_ahead", "forecast_arr_usd"]).withColumn(
    "forecast_method", F.lit("exp_smoothing")
).withColumn("generated_at", F.current_timestamp())

forecast_df.write.format("snowflake").options(**sf).option(
    "dbtable", "REVENUE_FORECAST"
).mode("overwrite").save()
