import os
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine


load_dotenv()

st.set_page_config(page_title="News Pipeline Dashboard", layout="wide")
st.title("News Pipeline Dashboard")

odbc_conn = os.getenv("AZURE_SQL_ODBC_CONNECTION_STRING", "")
table_name = os.getenv("AZURE_SQL_TABLE", "dbo.news_articles")

if not odbc_conn:
    st.error("Missing AZURE_SQL_ODBC_CONNECTION_STRING in environment.")
    st.stop()

engine = create_engine(f"mssql+pyodbc:///?odbc_connect={quote_plus(odbc_conn)}")
query = f"SELECT TOP 1000 * FROM {table_name} ORDER BY ingested_at DESC"
df = pd.read_sql(query, engine)

if df.empty:
    st.warning("No records found in SQL table yet.")
else:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total rows", len(df.index))
    col2.metric("Unique sources", df["source_name"].nunique())
    col3.metric("Unique authors", df["author"].nunique())

    st.subheader("Latest Articles")
    st.dataframe(df[["published_at", "source_name", "title", "keywords", "url"]], use_container_width=True)

    st.subheader("Top Sources")
    top_sources = df["source_name"].value_counts().head(10)
    st.bar_chart(top_sources)
