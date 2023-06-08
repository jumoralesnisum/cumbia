import re

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, regexp_replace, monotonically_increasing_id
from pyspark.sql.types import StringType


def clean_string(text):
    # Make lower
    # text = text.lower()
    # text = re.sub(r"(@\[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.+?", "", text)

    # Remove line breaks
    text = re.sub(r'\n', '', text)
    return text


if __name__ == '__main__':
    s = SparkSession.builder.appName("test").master('local[4]').getOrCreate()
    udf_clean = udf(lambda r: clean_string(r), StringType())
    df = s.read \
        .option("multiline", "true") \
        .option("quote", '"')\
        .option("header", "true")\
        .option("escape", "\\")\
        .option("escape", '"')\
        .csv('Consumer_Complaints.csv') \
        .select('Product', 'Issue', col('Consumer complaint narrative').alias('narrative')) \
        .withColumn('id', monotonically_increasing_id()) \
        .where(col('narrative').isNotNull())
    print(f"Count: {df.count()}")
    print(f"Partitions: {df.rdd.getNumPartitions()}")

    result_df = df \
        .withColumn('narrative', regexp_replace('narrative', '"', '')) \
        .withColumn('narrative', udf_clean(col('narrative'))) \
        .withColumnRenamed('Product', 'product') \
        .withColumnRenamed('Issue', 'issue')

    result_df.write.mode('overwrite').json("clean_ds")
    #result_df.show(20, truncate=False)
