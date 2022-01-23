# Wikiviews
Big Data project into Wikipedia pageview statistics processed with PySpark in Google Cloud

### Background and Motivation:
Since the development of the first transistor in 1947 the information age started slowly to emerge. We currently live in a rapidly evolving and interconnected world, with data coming in from all directions and it is hard to distinguish what the public’s concerns are or what humanity is more eager to learn.

### Project objectives:
So, what is the world most fascinated about right now? What were its interests last month, or at the same time last year? How does humanity shift from one point of interest to another throughout time? With this project I aim to answer these interesting questions, that relate to everybody and improve my skills with this data and process-intensive task.

### Data Sources:
To achieve the task, data from the largest free online encyclopedia will be used and that is no other than Wikipedia. The pageview data is dumped daily (*Volume* of > 1GB per day *Velocity*) and made publicly available via the Wikimedia Analytics team [here](https://dumps.wikimedia.org/other/pageview_complete/readme.html).

### Implementation:

1. Open your Google Cloud Console
2. Create a Project and a Google Cloud Storage (GCS) bucket 
3. Create a linux VM in Google Cloud, elable permission to your GCS bucket and download the data you need by using: 
```linux
curl https://dumps.wikimedia.org/other/pageview_complete/2021/2021-12/pageviews-20211201-user.bz2 | gsutil cp - gs://your-bucket/folder/filename.bz2
```
You can also parallelize the downloading, but placing the commands in a text file and run it with the `parallel` package:
```linux
sudo apt-get install parallel
parallel -j 10 < tasks.txt
```
3. Create a Spark Cluster in Google DataProc with Jupyter Notebook enabled. Use the bucket you created earlier for staging.
4. Goto the Web Interfaces of your cluster, open Jypter and create a new notebook. Alternatively you can create a Spark job.
5. Paste the contents of spark.py (shown also below) into a cell and adjust the needed variables. The code loads all csv's from a folder, processes them and dumps a parquet file:
```python
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
```
6. Run the cell and wait until it finishes.
7. Use Google's BigQuery to load the Parquet file directly.
8. Use Google's Data Studio for visualization.

### Outcome:
I downloaded the data for December 2021 and January 2022 and created [this dashboard](https://datastudio.google.com/reporting/ee1602bb-913d-4625-952c-06dfd45c6512/page/sn7jC) showing the top 20 articles by user views per day.
