import subprocess
import pandas as pd
import streamlit as st
import altair as alt
import s3fs
from sqlalchemy import create_engine, text
from datalake.config import settings, logger

def read_from_database(query_string, params={}):
    engine = create_engine(settings.DB.CONNECTION_STRING.replace(f'@{settings.DB.HOST}:', '@localhost:'))
    query = text(query_string)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params=params)
    logger.info("Done fetching data from database ... ")
    logger.info(f"\n{df}")
    return df

def read_from_storage(storage_path):
    fs = s3fs.S3FileSystem(
        anon=False,
        key=settings.STORAGE.USER,
        secret=settings.STORAGE.PASSWORD,
        client_kwargs={'endpoint_url': settings.STORAGE.ENDPOINT.replace('minio', 'localhost')}
    )
    files = fs.glob(storage_path)
    storage_options = {
        "key": settings.STORAGE.USER,
        "secret": settings.STORAGE.PASSWORD,
        "client_kwargs": {"endpoint_url": settings.STORAGE.ENDPOINT.replace('minio', 'localhost')}
    }
    df_list = [pd.read_parquet(f"s3://{file}", storage_options=storage_options) for file in files]
    combined_df = pd.concat(df_list, ignore_index=True)
    logger.info("Done fetching ... ")
    logger.info(f"\n{combined_df}")
    return combined_df

@st.cache_data
def fetch_all_stats():
    if st.session_state.use_storage == True:
        logger.info("Fetching s3 data ... ")
        all_stats = read_from_storage("s3://datalake/aggregated/yelp_academic_dataset_aggregated/*.parquet")
    else:
        logger.info("Fetching data from database ... ")
        all_stats = read_from_database("SELECT * FROM yelp_agg")
    return all_stats
    
@st.cache_data
def fetch_all_categories():
    if st.session_state.use_storage == True:
        categories = read_from_storage("s3://datalake/aggregated/yelp_academic_dataset_categories/*.parquet")
    else:
        categories = read_from_database("SELECT DISTINCT category FROM yelp_business_categories")
    return categories['category'].tolist()
    
def update_businesses():
    selected_value = st.session_state.category_value
    if selected_value != "":
        businesses = read_from_database("SELECT DISTINCT name FROM yelp_business_name_and_category WHERE category = :category", params={"category":selected_value})
        st.session_state['businesses'] = businesses["name"].tolist()
        # if st.session_state.use_storage == False:
        #     businesses = read_from_storage("s3://datalake/aggregated/yelp_academic_dataset_business_name_and_category/*.parquet")
        #     businesses: pd.DataFrame = businesses[businesses["category"] == selected_value]
        #     st.session_state['businesses'] = businesses["name"].unique().tolist()
        # else:
        #     businesses = read_from_database("SELECT DISTINCT name FROM yelp_business_name_and_category WHERE category = :category", params={"category":selected_value})
        #     st.session_state['businesses'] = businesses["name"].tolist()

def fetch_weekly_stats():
    business_category = st.session_state.category_value
    business_name = st.session_state.business_value
    if st.session_state.use_storage == True:
        all_stats = st.session_state['all_stats']
        filtered_df = all_stats[all_stats['name'] == business_name]
        filtered_df: pd.DataFrame = filtered_df[filtered_df['categories'].apply(lambda x: business_category in x)]
        filtered_df['checkin_count_trend'] = filtered_df['checkin_count'].cumsum()
        st.session_state['stats'] = filtered_df.to_dict(orient='records')
    else:
        stats = read_from_database('SELECT week, checkin_count, average_stars FROM yelp_agg WHERE "name" = :name AND :category = ANY(categories)', params={"name": business_name, "category": business_category})
        stats['checkin_count_trend'] = stats['checkin_count'].cumsum()
        st.session_state['stats'] = stats.to_dict(orient='records')

def main():
    st.set_page_config(
        page_title="NewYorker.com",
        page_icon=":rocket:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.header('Dashboard', divider='red')
    st.subheader('Data Engineering Programming challenge')
    st.sidebar.page_link("http://localhost:8000", label="Documentation", icon="📒", help="Sphinx Documentation - Please run the server separately as mentioned in the README.md file")
    st.sidebar.page_link("http://localhost:9001", label="Storage", icon="🪣", help="Minio Storage Bucket")
    st.sidebar.page_link("http://localhost:5000", label="Database", icon="📦", help="PG Admin")
    st.sidebar.page_link("http://localhost:8080", label="Pipelines", icon="✨", help="Spark streaming pipeline")
    
    if 'use_storage' not in st.session_state:
        st.session_state.use_storage = True
    
    if 'all_stats' not in st.session_state:
        st.write("fetching all stats .... it may take a while (upto 4-5 mins) !")
        st.session_state['all_stats'] = fetch_all_stats()
    
    if 'businesses' not in st.session_state:
        st.session_state['businesses'] = []

    categories = fetch_all_categories()
    col1, col2 = st.columns(2)

    with col1:
        st.selectbox(
            label="Select a category",
            options=[""] + categories,
            on_change=update_businesses,
            key="category_value"
        )

    with col2:
        st.selectbox(
            label="Select a business",
            options=st.session_state['businesses'],
            on_change=fetch_weekly_stats,
            key="business_value"
        )

    if 'stats' in st.session_state:
        df = pd.DataFrame(st.session_state['stats'])
        df['date'] = pd.to_datetime(df['week'].astype(str) + '0', format='%Y%W%w')
        graph_col1, graph_col2 = st.columns(2)

        with graph_col1:
            st.subheader("Total checkin count every week")
            checkin_chart = alt.Chart(df).mark_bar().encode(
                x=alt.X('date:T', axis=alt.Axis(labelAngle=-45, format='%Y-%U')),
                y='checkin_count:Q',
                tooltip=['date', 'checkin_count']
                ).interactive()
            st.altair_chart(checkin_chart, use_container_width=True)
        
        with graph_col2:
            st.subheader("Checkin Trend")
            checkin_chart = alt.Chart(df).mark_line().encode(
                x=alt.X('date:T', axis=alt.Axis(labelAngle=-45, format='%Y-%U')),
                y='checkin_count_trend:Q',
                tooltip=['date', 'checkin_count_trend']
                ).interactive()
            st.altair_chart(checkin_chart, use_container_width=True)

        st.subheader("Average Weekly Star Rating")
        stars_chart = alt.Chart(df).mark_line().encode(
            x=alt.X('date:T', axis=alt.Axis(labelAngle=-45, format='%Y-%U')),
            y='average_stars:Q',
            tooltip=['date', 'average_stars']
        ).interactive()
        st.altair_chart(stars_chart, use_container_width=True)

def cli():
    subprocess.run(["streamlit", "run", "./datalake/dashboard/__main__.py"])

if __name__ == "__main__":
    main()