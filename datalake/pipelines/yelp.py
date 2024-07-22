from datalake.config import settings, logger
from pyspark.sql.window import Window
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, count, year, weekofyear, mean, round, last, trim, split, explode, array_distinct

# ===========================================================================================================
# cleaning method
# ===========================================================================================================
def clean(spark: SparkSession):
    files = ['business', 'checkin', 'review', 'tip', 'user']
    for file in files:
        raw_file_path = f"s3a://datalake/raw/yelp_academic_dataset_{file}.json"
        clean_file_path = f"s3a://datalake/cleaned/yelp_academic_dataset_{file}"
        logger.info(f"Cleaning {file} dataset ...")
        df = spark.read.json(raw_file_path)
        df.show()
        match file:
            case 'business':
                df = df.withColumn("categories", split(trim(col("categories")), "\\s*,\\s*"))
            case 'checkin':
                df = df.withColumn("date", split(trim(col("date")), "\\s*,\\s*"))
            case 'user':
                df = df.withColumn("friends", split(trim(col("friends")), "\\s*,\\s*"))
            case _:
                logger.info("No modification needed in this dataset")
        df.write.parquet(clean_file_path, mode="overwrite")

# ===========================================================================================================
# aggregation methods 
# ===========================================================================================================
def weekly_checkin_count(spark: SparkSession):
    checkin_datafile = f"s3a://datalake/cleaned/yelp_academic_dataset_checkin/*.parquet"
    checkin_df = spark.read.parquet(checkin_datafile)
    checkin_df = checkin_df.withColumn("date", explode(checkin_df["date"]))
    checkin_df = checkin_df.withColumn("week", year(col('date')) * 100 + weekofyear(col("date")))
    grouped_df = checkin_df.groupBy("business_id", "week").agg(count("week").alias("checkin_count"))
    return grouped_df

def weekly_average_star_ratings(spark: SparkSession):
    review_datafile = f"s3a://datalake/cleaned/yelp_academic_dataset_review/*.parquet"
    review_df = spark.read.parquet(review_datafile)
    review_df = review_df.withColumn("week", year(col('date')) * 100 + weekofyear(col("date")))
    grouped_df = review_df.groupBy("business_id", "week").agg(mean("stars").alias("average_stars"))
    grouped_df = grouped_df.withColumn("average_stars", round('average_stars', 1))
    return grouped_df

def merge_weekly_ratings_and_checkin_count(weekly_checkin_count_df: DataFrame, weekly_average_star_ratings_df: DataFrame):
    # merge data frames using full outer join
    merged_df = weekly_checkin_count_df.join(weekly_average_star_ratings_df, ['business_id', 'week'], 'outer')
    # fill nan values with 0 for checkin_count (since it's count, nan would mean 0)
    merged_df = merged_df.fillna({'checkin_count': 0})
    # fill previous values using window functions
    window_spec = Window.partitionBy('business_id').orderBy('week').rowsBetween(Window.unboundedPreceding, 0)
    merged_df = merged_df.withColumn('average_stars', last('average_stars', True).over(window_spec))
    merged_df = merged_df.fillna({'average_stars': 0.0})
    # order all values by business_id, week
    merged_df = merged_df.orderBy(col('business_id'), col('week').asc(), col('average_stars').desc(), col('checkin_count').desc())
    return merged_df


def aggregate(spark: SparkSession):
    weekly_checkin_count_df = weekly_checkin_count(spark)
    weekly_checkin_count_df.show(truncate=False)

    weekly_average_star_ratings_df = weekly_average_star_ratings(spark)
    weekly_average_star_ratings_df.show(truncate=False)
   
    merged_df = merge_weekly_ratings_and_checkin_count(weekly_checkin_count_df, weekly_average_star_ratings_df)
    
    business_datafile = f"s3a://datalake/cleaned/yelp_academic_dataset_business/*.parquet"
    business_df = spark.read.parquet(business_datafile)
    business_df.show()
    
    merged_df = merged_df.join(business_df.select('business_id', 'name', 'state', 'categories'), ['business_id'], 'left')
    merged_df.show()
    merged_df.write.parquet("s3a://datalake/aggregated/yelp_academic_dataset_aggregated", mode="overwrite")
    # extras - categories file
    categories = merged_df.select(explode(array_distinct(merged_df["categories"])).alias("category")).distinct()
    categories.write.parquet("s3a://datalake/aggregated/yelp_academic_dataset_categories", mode="overwrite")
    # extras - business names and category file
    business_names_and_category = merged_df.withColumn("category", explode(merged_df["categories"]))
    business_names_and_category = business_names_and_category.select(['business_id', 'name', 'category']).distinct()
    business_names_and_category.write.parquet("s3a://datalake/aggregated/yelp_academic_dataset_business_name_and_category", mode="overwrite")
    

# ===========================================================================================================
# load data to postgres instance
# ===========================================================================================================
def load(spark: SparkSession, table_name='yelp_agg'):
    jdbc_url = f"jdbc:postgresql://{settings.DB.HOST}:{settings.DB.PORT}/{settings.DB.NAME}"
    connection_properties = {
        "user": settings.DB.USER,
        "password": settings.DB.PASSWORD,
        "driver": "org.postgresql.Driver"
    }
    # write aggregated data
    agg_datafile = f"s3a://datalake/aggregated/yelp_academic_dataset_aggregated/*.parquet"
    agg_df = spark.read.parquet(agg_datafile)
    agg_df.write.jdbc(url=jdbc_url, table=table_name, mode="overwrite", properties=connection_properties)
    # write business categories table
    category_datafile = "s3a://datalake/aggregated/yelp_academic_dataset_categories/*.parquet"
    category_df = spark.read.parquet(category_datafile)
    category_df.write.jdbc(url=jdbc_url, table='yelp_business_categories', mode="overwrite", properties=connection_properties)
    # write business names and category table
    business_name_and_category_datafile = "s3a://datalake/aggregated/yelp_academic_dataset_business_name_and_category/*.parquet"
    business_name_and_category_df = spark.read.parquet(business_name_and_category_datafile)
    business_name_and_category_df.write.jdbc(url=jdbc_url, table='yelp_business_name_and_category', mode="overwrite", properties=connection_properties)

class PipelineOptionsError(Exception):
    def __init__(self, message):
        super.__init__(message)

def pipeline(option):
    spark = (
        SparkSession
        .builder
        .appName(f"Write to Storage Bucket after {option}")
        .master("spark://spark-master:7077")
        .config("spark.hadoop.fs.s3a.endpoint", settings.STORAGE.ENDPOINT)
        .config("spark.hadoop.fs.s3a.access.key", settings.STORAGE.USER)
        .config("spark.hadoop.fs.s3a.secret.key", settings.STORAGE.PASSWORD)
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .getOrCreate()
    )
    try:
        spark.sparkContext.setLogLevel("INFO")
        # Yelp dataset files:
        # raw/yelp_academic_dataset_{file}
        #  - business
        #  - checkin
        #  - review
        #  - tip
        #  - user
        match option:
            case "clean":
                clean(spark)
            case "aggregate":
                aggregate(spark)
            case "load":
                load(spark, 'yelp_agg')
            case _:
                raise PipelineOptionsError("Pipeline options can either be clean, aggregate or load !!!")
    finally:
        spark.stop()

if __name__ == '__main__':
    pipeline()
