"""
Large Scale Data Management

Task 2:
Using RDDs write code to answer the following queries (Q1-Q5). You can use the csv or parquet files you uploaded on HDFS.
"""

from pyspark.sql import SparkSession

sc = SparkSession.builder.appName("Task 2").getOrCreate().sparkContext()

# ----------------------------------------------------------------------------------------------------------------------------------------------
# Task 2 - Q1
# For every year after 1995 print the difference between the money spent to create the movie and the revenue of the movie.
# ----------------------------------------------------------------------------------------------------------------------------------------------

movies = sc.textFile("hdfs://master:9000/lsdm_files/movies.csv").map(lambda x: (x.split(",")))
movies_len = movies.map(lambda x: x if (len(x[3]) == 4) else None).filter(lambda x: x != None)
movies_a95 = movies_len.filter(lambda x: int(x[3]) > 1995)
movies_nzc = movies_a95.filter(lambda x: int(x[5]) > 0)
movies_nzr = movies_nzc.filter(lambda x: int(x[6]) > 0)
profit = movies_nzr.map(lambda x: [x[1], int(x[6]) - int(x[5])])
print(profit.take(30))

# ----------------------------------------------------------------------------------------------------------------------------------------------
# Task 2 - Q2
# For the movie "Cesare deve morire" find and print the movie id and then search how many users rated the movie and what the average rating was.
# ----------------------------------------------------------------------------------------------------------------------------------------------

movies = sc.textFile("hdfs://master:9000/lsdm_files/movies.csv").map(lambda x: (x.split(",")))
cesare = movies.filter(lambda x: x[1] == "Cesare deve morire")
cesare_formatted = cesare.map(lambda x: [x[0], [x[1]]])

ratings = sc.textFile("hdfs://master:9000/lsdm_files/ratings.csv").map(lambda x: (x.split(",")))
ratings_cesare = ratings.filter(lambda x: x[1] == "96821")
ratings_formatted = ratings_cesare.map(lambda x: [x[1], [x[2]]])

joined_data = cesare_formatted.join(ratings_formatted)

sum_ratings = joined_data.map(lambda x: (x[1][1][0])).map(lambda x: float(x[0:3])).reduce(lambda a,b: a+b)
count_ratings = joined_data.count()
avg_rating = sum_ratings / count_ratings
print(avg_rating)

# ----------------------------------------------------------------------------------------------------------------------------------------------
# Task 2 - Q3
# What was the best in term of revenue Animation movie of 1995?
# ----------------------------------------------------------------------------------------------------------------------------------------------

movies = sc.textFile("hdfs://master:9000/lsdm_files/movies.csv").map(lambda x: (x.split(",")))
movies_e95 = movies.filter(lambda x: x[3] == "1995")
movies_formatted = movies_e95.map(lambda x: [x[0], [x[1],x[6]]])

movie_genres = sc.textFile("hdfs://master:9000/lsdm_files/movie_genres.csv").map(lambda x: (x.split(",")))
movie_genres_animation = movie_genres.filter(lambda x: x[1] == "Animation")
movie_genres_formatted = movie_genres_animation.map(lambda x: [x[0], [x[1]]])

joined_data = movies_formatted.join(movie_genres_formatted)

get_movies = joined_data.map(lambda x: (x[1][0]))
movies_by_revenue = get_movies.map(lambda x: [int(x[1]), [x[0]]]).sortByKey(ascending=False)
print(movies_by_revenue.take(1))

# ----------------------------------------------------------------------------------------------------------------------------------------------
# Task 2 - Q4
# Find and print the most popular Comedy movies for every year after 1995.
# ----------------------------------------------------------------------------------------------------------------------------------------------

movies = sc.textFile("hdfs://master:9000/lsdm_files/movies.csv").map(lambda x: (x.split(",")))
movies_a95 = movies.filter(lambda x: x[3] > "1995")
movies_formatted = movies_a95.map(lambda x: [x[0], [x[1], int(x[3]), float(x[7])]])

movie_genres = sc.textFile("hdfs://master:9000/lsdm_files/movie_genres.csv").map(lambda x: (x.split(",")))
movie_genres_animation = movie_genres.filter(lambda x: x[1] == "Comedy")
movie_genres_formatted = movie_genres_animation.map(lambda x: [x[0], [x[1]]])

joined_data = movies_formatted.join(movie_genres_formatted)

get_movies = joined_data.map(lambda x: (x[1][0])).map(lambda x: [x[1], x[0], x[2]])
most_popular = get_movies.map(lambda x: (x[0], x)).reduceByKey(lambda x1, x2: max(x1, x2, key=lambda x: x[-1])).sortByKey(ascending=False).values()
print(most_popular.collect())

# ----------------------------------------------------------------------------------------------------------------------------------------------
# Task 2 - Q5
# For every year, print the average movie revenue.
# ----------------------------------------------------------------------------------------------------------------------------------------------

movies = sc.textFile("hdfs://master:9000/lsdm_files/movies.csv").map(lambda x: (x.split(",")))
movies_len = movies.map(lambda x: x if (len(x[3]) == 4) else None).filter(lambda x: x != None)
movies_rev = movies_len.filter(lambda x: int(x[6]) > 0)
movies_formatted = movies_rev.map(lambda x: [x[3],int(x[6])])

revenue_per_year = movies_formatted.mapValues(lambda x: (x, 1)).reduceByKey(lambda a,b: (a[0]+b[0], a[1]+b[1])).sortByKey(ascending=False).mapValues(lambda x: x[0]/x[1])
print(revenue_per_year.collect())