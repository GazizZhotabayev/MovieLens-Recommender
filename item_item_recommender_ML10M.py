def compute_similarity_scores(folder, output):
    from pyspark import SparkContext
    from pyspark.sql import SparkSession
    import pyspark.sql.functions as F
    import pandas as pd
    from pyspark.sql.types import IntegerType

    sc = SparkContext('local[*]')
    df = SparkSession.builder.getOrCreate().read.option('delimiter', '::').csv(folder + 'ratings.dat')\
         .toDF("User ID", "Movie ID", "Rating", "Timestamp").drop('Timestamp') #read in the file, add column names and drop the timestamp

    df = df.withColumn('User ID', df['User ID'].cast(IntegerType()))\ #for some reason it reads in the IDs and ratings as strings
         .withColumn('Movie ID', df['Movie ID'].cast(IntegerType()))\
         .withColumn('Rating', df['Rating'].cast(IntegerType()))\
         .withColumnRenamed('Movie ID', 'Movie ID_x').withColumnRenamed('Rating', 'Rating_x')\ #rename the columns (preparing for the self-join)
         .join(df.withColumnRenamed('Movie ID', 'Movie ID_y').withColumnRenamed('Rating', 'Rating_y'), on="User ID",how="leftouter")\
         .filter(F.col('Movie ID_x') < F.col('Movie ID_y'))\ #keep just one pair of movies - i.e. just (A, B) instead of (A, B) and (B, A)
         .drop('User ID')\ #no longer need this
         .withColumn("xx", F.col('Rating_x') * F.col('Rating_x'))\ #these 3 columns are needed for the cosine similarity computation
         .withColumn("xy", F.col('Rating_x') * F.col('Rating_y'))\
         .withColumn("yy", F.col('Rating_y') * F.col('Rating_y'))\
         .drop('Rating_x').drop('Rating_y')\ #drop the ratings now that we're done with them
         .groupBy(F.col("Movie ID_x"), F.col("Movie ID_y"))\ #group by every movie pair
         .agg(
             F.sum(F.col('xy')).alias('a'),
             (F.sqrt(F.sum(F.col('xx'))) * F.sqrt(F.sum(F.col('yy')))).alias('b'),
             F.count(F.col('xy')).alias('n_users')
             )\
             .withColumn('cos_similarity', F.when(F.col('b') != 0, F.col('a') / F.col('b')).otherwise(None))\
             .drop('a').drop('b')#calculate the cosine similarity

    columns = df.schema.fieldNames()
    #was really struggling writing this all out to csvs with pysparks built-in functionality
    #found a workaround to split the data into multiple chunks and write those with panda
    chunks = df.repartition(20).rdd.mapPartitions(lambda iterator: [pd.DataFrame(list(iterator), columns=columns)]).toLocalIterator()
    i = 0
    for pandas_df in chunks:
        i += 1
        pandas_df.to_csv(output + str(i) + '.csv', index = False)

    sc.stop()
