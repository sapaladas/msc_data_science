"""
Large Scale Data Management

Task 4:
Using Spark SQL write code to answer the following queries (Q1-Q5) using the csv files you created and uploaded on HDFS.
"""

from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, IntegerType, FloatType, StringType, TimestampType

spark = SparkSession.builder.appName("Task 4: CSV").getOrCreate()

Movies_schema = StructType([ 
    StructField("Id", IntegerType()), 
    StructField("Movie_Name", StringType()),
    StructField("Movie_Desc", StringType()),
    StructField("Rel_Year", IntegerType()),
    StructField("Duration", IntegerType()),
    StructField("ProductionCost", IntegerType()),
    StructField("Revenue", IntegerType()),
    StructField("Popularity", FloatType()),
    StructField("Dep_id", IntegerType())])

Ratings_schema = StructType([ 
    StructField("User_Id", IntegerType()), 
    StructField("Movie_Id", IntegerType()),
    StructField("Rating", FloatType()),
    StructField("Timestamp", TimestampType())])

MovieGenres_schema = StructType([ 
    StructField("Movie_Id", IntegerType()), 
    StructField("Genre", StringType())])

Movies_df_CSV = spark.read.format('csv').options(header='false').schema(Movies_schema).load("hdfs://master:9000/lsdm_files/movies.csv")
Ratings_df_CSV = spark.read.format('csv').options(header='false').schema(Ratings_schema).load("hdfs://master:9000/lsdm_files/ratings.csv")
MovieGenres_df_CSV = spark.read.format('csv').options(header='false').schema(MovieGenres_schema).load("hdfs://master:9000/lsdm_files/movie_genres.csv")

# ----------------------------------------------------------------------------------------------------------------------------------------------
# Task 4 - Q1
# For every year after 1995 print the difference between the money spent to create the movie and the revenue of the movie.
# ----------------------------------------------------------------------------------------------------------------------------------------------

Q1_QueryCSV = "SELECT \
                   Id \
                 , Movie_Name AS Movie \
                 , cast(Revenue AS int) - ProductionCost AS Return \
               FROM MoviesCSV \
               WHERE Rel_Year > 1995 \
                 AND Revenue <> 0 \
                 AND ProductionCost <> 0 \
                 AND Rel_Year <> 0"

Q1_Query_ResCSV = spark.sql(Q1_QueryCSV)
Q1_Query_ResCSV.show(n = 100000, truncate = False)

# ----------------------------------------------------------------------------------------------------------------------------------------------
# Task 4 - Q2
# For the movie "Cesare deve morire" find and print the movie id and then search how many users rated the movie and what the average rating was.
# ----------------------------------------------------------------------------------------------------------------------------------------------

Q2_QueryCSV = "SELECT \
                   MoviesCSV.Id \
                 , MoviesCSV.Movie_Name AS Movie \
                 , COUNT(*) AS UserCount \
                 , AVG(RatingsCSV.Rating) AS AvgRating \
               FROM MoviesCSV \
               INNER JOIN RatingsCSV \
                  ON RatingsCSV.Movie_Id == MoviesCSV.Id \
               WHERE MoviesCSV.Movie_Name = 'Cesare deve morire' \
                 AND Rel_Year <> 0 \
               GROUP BY 1,2"

Q2_Query_ResCSV = spark.sql(Q2_QueryCSV)
Q2_Query_ResCSV.show()

# ----------------------------------------------------------------------------------------------------------------------------------------------
# Task 4 - Q3
# What was the best in term of revenue Animation movie of 1995?
# ----------------------------------------------------------------------------------------------------------------------------------------------

Q3_QueryCSV = "SELECT \
                   MoviesCSV.Id \
                 , MoviesCSV.Movie_Name AS Movie \
                 , MAX(MoviesCSV.Revenue) AS HighestRevenue \
               FROM MoviesCSV \
               INNER JOIN MovieGenresCSV \
                  ON MovieGenresCSV.Movie_Id == MoviesCSV.Id \
               WHERE MovieGenresCSV.Genre = 'Animation' \
                 AND MoviesCSV.Rel_Year = 1995 \
                 AND MoviesCSV.Revenue <> 0 \
                 AND MoviesCSV.Rel_Year <> 0 \
               GROUP BY 1,2 \
               ORDER BY 3 DESC \
               LIMIT 1"

Q3_Query_ResCSV = spark.sql(Q3_QueryCSV)
Q3_Query_ResCSV.show()

# ----------------------------------------------------------------------------------------------------------------------------------------------
# Task 4 - Q4
# Find and print the most popular Comedy movies for every year after 1995.
# ----------------------------------------------------------------------------------------------------------------------------------------------

Q4_QueryCSV = "SELECT \
                   MoviesCSV.Rel_Year \
                 , MAX(MoviesCSV.Popularity) AS MaxPopularity \
               FROM MoviesCSV \
               INNER JOIN MovieGenresCSV \
                  ON MovieGenresCSV.Movie_Id = MoviesCSV.Id \
               WHERE MovieGenresCSV.Genre = 'Comedy' \
                 AND MoviesCSV.Rel_Year > 1995 \
                 AND MoviesCSV.Rel_Year <> 0 \
               GROUP BY 1 \
               ORDER BY 1 DESC"

Q4_Query_ResCSV = spark.sql(Q4_QueryCSV)
Q4_Query_ResCSV.createOrReplaceTempView("TempQ4CSV")

Q4_QueryFCSV = "SELECT \
                    MoviesCSV.Id \
                  , MoviesCSV.Movie_Name \
                  , TempQ4CSV.Rel_Year \
                  , TempQ4CSV.MaxPopularity \
                FROM TempQ4CSV \
                INNER JOIN MoviesCSV \
                   ON MoviesCSV.Popularity = TempQ4CSV.MaxPopularity \
                  AND MoviesCSV.Rel_Year = TempQ4CSV.Rel_Year \
                ORDER BY 3 DESC"

Q4_QueryF_ResCSV = spark.sql(Q4_QueryFCSV)
Q4_QueryF_ResCSV.show(n = 25, truncate = False)

# ----------------------------------------------------------------------------------------------------------------------------------------------
# Task 4 - Q5
# For every year, print the average movie revenue.
# ----------------------------------------------------------------------------------------------------------------------------------------------

Q5_Query = "SELECT \
                Rel_Year \
              , CAST(AVG(Revenue) AS decimal(18,3)) AS AverageRevenue \
            FROM MoviesCSV \
            WHERE Rel_Year <> 0 \
              AND Revenue <> 0 \
            GROUP BY 1 \
            ORDER BY 1 DESC"

Q5_Query_Res = spark.sql(Q5_Query)
Q5_Query_Res.show(n = 100, truncate = False)