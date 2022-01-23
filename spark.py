from pyspark.sql.types import StructType, StructField, IntegerType, StringType
import pyspark.sql.functions as F
from pyspark.sql.window import Window
import os

bucket_name = 'your_bucket'
infolder = 'in'
outfolder = 'out'

# List of articles (starting with) to be disregarded
l = ['Special:', 'File:', 'Portal:', 'User:', 'Template:', 'Category:', 'User_talk:', 'Wikipedia', 'Main_' , '-']
reg_str = r"^("+ "|".join(l) + ")"

# Pageview csv dumps schema
schema = StructType([
    StructField("project",StringType()),
    StructField("title",StringType()),
    StructField("pageid",StringType()),
    StructField("agent",StringType()),
    StructField("total",IntegerType()),
    StructField("hourly",StringType())])

# Reading all csv dumps
df = spark.read.schema(schema).option('delimiter', ' ').format("csv") \
    .load(os.path.join('gs://', bucket_name, infolder))

# Filtering, adding date column, grouping and summing views
df = df.filter(df.project == "en.wikipedia") \
    .where(~df.title.rlike(reg_str)) \
    .withColumn('title', F.regexp_replace('title', '_|-', ' ')) \
    .withColumn("date", F.to_date(F.regexp_extract(F.input_file_name(), """(.{10}).bz2$""", 1),"yyyy-MM-dd")) \
    .groupBy("date", "title").agg(F.sum("total").alias('views'))

# Window for ranking pageviews by date 
window = Window.partitionBy("date").orderBy(df['views'].desc())

# Ranking, filtering top-20 per group, repartitioning into one (file) and saving parquet
df.select('*', F.row_number().over(window).alias('rank')) .filter(F.col('rank') <= 20) \
  .repartition(1).write.mode('append').parquet(os.path.join('gs://', bucket_name, outfolder))
