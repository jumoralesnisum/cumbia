import concurrent.futures
import json
import multiprocessing
import time

from deep_translator import GoogleTranslator
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf
from pyspark.sql.types import StringType, StructType, StructField

lock = multiprocessing.Lock()


def call_service(text):
    translator = GoogleTranslator(source='en', target='es')

    while True:
        try:
            return translator.translate(text) + " "
        except Exception as e:
            print(e)
            time.sleep(1)


def translate(record):
    text = record['narrative']
    text = text.replace('"', '')
    n = 4999
    if not text.strip():
        return ""
    translated = ""
    while len(text) > n:
        chunk = text[:n]
        last_word_index = chunk.rfind(' ')
        actual_chunk = text[:last_word_index]

        translated += call_service(actual_chunk)
        text = text[last_word_index:]
    if len(text) > 0:
        final_chunk = call_service(text)
        if final_chunk:
            translated += final_chunk
    return {'id': record['id'], 'translated': translated}


def translate_batch(batch):
    i, chunk = batch
    with open(f'./translated/part_{i}', 'w', encoding='utf8') as f:
        for record in chunk:
            translated = translate(record)
            f.write((json.dumps(translated, ensure_ascii=False) + "\n"))


def chunks(l, n):
    """Yield n number of sequential chunks from l."""
    d, r = divmod(len(l), n)
    for i in range(n):
        si = (d+1)*(i if i < r else r) + d*(0 if i < r else i - r)
        yield l[si:si+(d+1 if i < r else d)]


def remove_files():
    import os
    import glob

    files = glob.glob('./translated/*')
    for f in files:
        os.remove(f)


if __name__ == '__main__':
    s = SparkSession.builder.appName("test").master('local[4]').getOrCreate()

    udf_translate = udf(lambda r: translate(r), StringType())
    processed_folder = 'translated_bulk'
    all_records_folder = 'clean_ds'

    try:
        processed = s.read \
            .json(processed_folder) \
            .drop('_corrupt_record') \
            .select(
                'id'
            )
    except Exception as e:
        schema = StructType([
            StructField('id', StringType(), True)
        ])
        processed = s.createDataFrame(s.sparkContext.emptyRDD(), schema)
    print(f"Processed Count: {processed.count()}")

    all_records = s.read \
        .json(all_records_folder) \
        .select(col('id').alias('all_id'), col('narrative').alias('base_narrative')) \
        .where(col('base_narrative').isNotNull())
    print(f"All records Count: {all_records.count()}")

    magma = all_records \
        .join(
            processed,
            col("all_id") == col("id"), 'left')\
        .where(col("id").isNull()).\
        select(col('all_id').alias('id'), col('base_narrative').alias('narrative'))

    magma.show(100, truncate=False)
    base = magma.sample(0.5).toJSON().map(lambda j: json.loads(j)).collect()

    chunked = list(chunks(base, 4))
    indexed = list(enumerate(chunked))

    remove_files()

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # map
        list(executor.map(lambda batch: translate_batch(batch), indexed))

