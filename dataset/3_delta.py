from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_replace

if __name__ == '__main__':
    s = SparkSession.builder.appName("test").master('local[4]').getOrCreate()
    it = 0
    new_translated_folder = 'translated'
    all_records_folder = 'clean_ds'

    new_translated = s.read \
        .json(new_translated_folder) \
        .select(
            col('id').alias('new_t_id'), 'translated'
        )

    all_records = s.read \
        .json(all_records_folder) \
        .select('id', 'product', 'issue', 'narrative') \
        .where(col('narrative').isNotNull()) \
        .withColumn('narrative', regexp_replace('narrative', '"', '')) \

    joined = new_translated.join(all_records, col('id') == col('new_t_id'), 'inner') \
        .select('id', 'product', 'issue', 'narrative', 'translated')

    joined.repartition(1).write.mode('append').json('./translated_bulk')
