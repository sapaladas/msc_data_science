"""
Large Scale Data Management

Task 4:
Using Spark SQL write code to answer the following queries (Q1-Q5) using the parquet files you created and uploaded on HDFS.
"""

from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Task 4: Parquet").getOrCreate()

Movies_df = spark.read.parquet("hdfs://master:9000/lsdm_files/movies.parquet")
Ratings_df = spark.read.parquet("hdfs://master:9000/lsdm_files/ratings.parquet")
MovieGenres_df = spark.read.parquet("hdfs://master:9000/lsdm_files/movie_genres.parquet")

Movies_df.createOrReplaceTempView("Movies")
Ratings_df.createOrReplaceTempView("Ratings")
MovieGenres_df.createOrReplaceTempView("MovieGenres")

# ----------------------------------------------------------------------------------------------------------------------------------------------
# Task 4 - Q1
# For every year after 1995 print the difference between the money spent to create the movie and the revenue of the movie.
# ----------------------------------------------------------------------------------------------------------------------------------------------

Q1_QueryP = "SELECT \
                 movie_id \
               , name AS Movie \
               , revenue - cost AS Return \
             FROM Movies \
             WHERE release_year > 1995 \
               AND revenue <> 0 \
               AND cost <> 0 \
               AND release_year <> 0"

Q1_Query_ResP = spark.sql(Q1_QueryP)
Q1_Query_ResP.show(n = 100000, truncate = False)

# ----------------------------------------------------------------------------------------------------------------------------------------------
# Task 4 - Q2
# For the movie "Cesare deve morire" find and print the movie id and then search how many users rated the movie and what the average rating was.
# ----------------------------------------------------------------------------------------------------------------------------------------------

Q2_QueryP = "SELECT \
                 Movies.movie_id \
               , Movies.name AS Movie \
               , COUNT(*) AS UserCount \
               , AVG(Ratings.rating) AS AvgRating \
             FROM Movies \
             INNER JOIN Ratings \
                ON Ratings.movie_id == Movies.movie_id \
             WHERE Movies.name = 'Cesare deve morire' \
               AND release_year <> 0 \
             GROUP BY 1,2"

Q2_Query_ResP = spark.sql(Q2_QueryP)
Q2_Query_ResP.show()

# ----------------------------------------------------------------------------------------------------------------------------------------------
# Task 4 - Q3
# What was the best in term of revenue Animation movie of 1995?
# ----------------------------------------------------------------------------------------------------------------------------------------------

Q3_QueryP = "SELECT \
                 Movies.movie_id \
               , Movies.name AS Movie \
               , MAX(Movies.revenue) AS HighestRevenue \
             FROM Movies \
             INNER JOIN MovieGenres \
                ON MovieGenres.movie_id == Movies.movie_id \
             WHERE MovieGenres.genre = 'Animation' \
               AND Movies.release_year = 1995 \
               AND Movies.revenue <> 0 \
               AND Movies.release_year <> 0 \
             GROUP BY 1,2 \
             ORDER BY 3 DESC \
             LIMIT 1"

Q3_Query_ResP = spark.sql(Q3_QueryP)
Q3_Query_ResP.show()

# ----------------------------------------------------------------------------------------------------------------------------------------------
# Task 4 - Q4
# Find and print the most popular Comedy movies for every year after 1995.
# ----------------------------------------------------------------------------------------------------------------------------------------------

Q4_QueryP = "SELECT \
                 Movies.release_year \
               , MAX(Movies.popularity) AS MaxPopularity \
             FROM Movies \
             INNER JOIN MovieGenres \
                ON MovieGenres.movie_id = Movies.movie_id \
             WHERE MovieGenres.genre = 'Comedy' \
               AND Movies.release_year > 1995 \
               AND Movies.release_year <> 0 \
             GROUP BY 1 \
             ORDER BY 1 DESC"

Q4_Query_ResP = spark.sql(Q4_QueryP)
Q4_Query_ResP.createOrReplaceTempView("TempQ4")

Q4_QueryFP = "SELECT \
                  Movies.movie_id \
                , Movies.name \
                , TempQ4.release_year \
                , TempQ4.MaxPopularity \
              FROM TempQ4 \
              INNER JOIN Movies \
                 ON Movies.popularity = TempQ4.MaxPopularity \
                AND Movies.release_year = TempQ4.release_year \
              ORDER BY 3 DESC"

Q4_QueryF_ResP = spark.sql(Q4_QueryFP)
Q4_QueryF_ResP.show(n = 25, truncate = False)

# ----------------------------------------------------------------------------------------------------------------------------------------------
# Task 4 - Q5
# For every year, print the average movie revenue.
# ----------------------------------------------------------------------------------------------------------------------------------------------

Q5_QueryP = "SELECT \
                 release_year \
               , CAST(AVG(revenue) AS decimal(18,3)) AS AverageRevenue \
             FROM Movies \
             WHERE Movies.release_year <> 0 \
               AND Movies.revenue <> 0 \
             GROUP BY 1 \
             ORDER BY 1 DESC"

Q5_Query_ResP = spark.sql(Q5_QueryP)
Q5_Query_ResP.show(n = 100, truncate = False)