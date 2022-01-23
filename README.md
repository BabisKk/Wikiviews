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
3. Create a Spark Cluster in Google DataProc with Jupyter Notebook enabled. Use the bucket you created earlier for staging
4. Goto the Web Interfaces of your cluster, open Jypter and create a new notebook
5. Paste the contents of spark.py into a cell and adjust the needed variables
6. Run the cell and wait until it finishes
7. You can use Google's BigQuery to load the Parquet file directly
8. You can also use Google's Data Studio for visualization

### Outcome:
I downloaded the data for December 2021 and January 2022 and created this [dashboard](https://datastudio.google.com/reporting/ee1602bb-913d-4625-952c-06dfd45c6512/page/sn7jC) showing the top 20 articles by user views per day.
