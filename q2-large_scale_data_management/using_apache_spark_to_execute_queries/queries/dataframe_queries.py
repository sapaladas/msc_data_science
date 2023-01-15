"""
Large Scale Data Management

Task 3:
Using DataFrames write code to answer the following queries (Q1-Q5) using the parquet files you created and uploaded on HDFS.
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.appName("Task 3").getOrCreate()

Movies_df = spark.read.parquet("hdfs://master:9000/lsdm_files/movies.parquet")
Ratings_df = spark.read.parquet("hdfs://master:9000/lsdm_files/ratings.parquet")
MovieGenres_df = spark.read.parquet("hdfs://master:9000/lsdm_files/movie_genres.parquet")

# ----------------------------------------------------------------------------------------------------------------------------------------------
# Task 3 - Q1
# For every year after 1995 print the difference between the money spent to create the movie and the revenue of the movie.
# ----------------------------------------------------------------------------------------------------------------------------------------------

Movies_df.filter((Movies_df.release_year > 1995) & (Movies_df.revenue != 0) & (Movies_df.release_year != 0)) \
         .select(Movies_df.movie_id, Movies_df.name, (Movies_df.revenue - Movies_df.cost).alias('Difference')) \
         .collect()

# ----------------------------------------------------------------------------------------------------------------------------------------------
# Task 3 - Q2
# For the movie "Cesare deve morire" find and print the movie id and then search how many users rated the movie and what the average rating was.
# ----------------------------------------------------------------------------------------------------------------------------------------------

Movies_df.filter((Movies_df.name == 'Cesare deve morire') & (Movies_df.release_year != 0)) \
         .join(Ratings_df, Movies_df.movie_id == Ratings_df.movie_id, 'inner') \
         .select(Movies_df.movie_id, Movies_df.name, Ratings_df.user_id, Ratings_df.rating) \
         .groupBy(Movies_df.movie_id, Movies_df.name) \
         .agg(F.count('user_id').alias('count'), F.avg('rating').alias('AvgRating')) \
         .collect()

# ----------------------------------------------------------------------------------------------------------------------------------------------
# Task 3 - Q3
# What was the best in term of revenue Animation movie of 1995?
# ----------------------------------------------------------------------------------------------------------------------------------------------

Movies_df.join(MovieGenres_df, Movies_df.movie_id == MovieGenres_df.movie_id, 'inner') \
         .filter((MovieGenres_df.genre == 'Animation') & (Movies_df.release_year != 0) & (Movies_df.revenue != 0) & (Movies_df.release_year == 1995)) \
         .select(Movies_df.movie_id, Movies_df.name, Movies_df.revenue) \
         .groupBy(Movies_df.movie_id, Movies_df.name) \
         .agg(F.max('revenue').alias('MaxRevenue')) \
         .sort(F.max('revenue').desc()) \
         .limit(1).collect()

# ----------------------------------------------------------------------------------------------------------------------------------------------
# Task 3 - Q4
# Find and print the most popular Comedy movies for every year after 1995.
# ----------------------------------------------------------------------------------------------------------------------------------------------

TempDf = Movies_df.join(MovieGenres_df, Movies_df.movie_id == MovieGenres_df.movie_id, 'inner') \
                  .filter((MovieGenres_df.genre == 'Comedy') & (Movies_df.release_year != 0) & (Movies_df.release_year > 1995)) \
                  .select(Movies_df.release_year, Movies_df.popularity) \
                  .groupBy(Movies_df.release_year) \
                  .agg(F.max('popularity').alias('MaxPopularity')) \
                  .withColumnRenamed('release_year', 'year') \
                  .sort(Movies_df.release_year.desc())
                  
TempDf.join(Movies_df, (Movies_df.popularity == TempDf.MaxPopularity) & (TempDf.year == Movies_df.release_year), 'inner') \
      .select(Movies_df.name, TempDf.year, TempDf.MaxPopularity) \
      .collect()

# ----------------------------------------------------------------------------------------------------------------------------------------------
# Task 3 - Q5
# For every year, print the average movie revenue.
# ----------------------------------------------------------------------------------------------------------------------------------------------

Movies_df.filter((Movies_df.release_year != 0) & (Movies_df.revenue != 0)) \
         .select(Movies_df.release_year, Movies_df.revenue) \
         .groupBy(Movies_df.release_year) \
         .agg(F.avg('revenue').alias('AverageRevenue')) \
         .sort(Movies_df.release_year.desc()) \
         .collect()