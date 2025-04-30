import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import StringIO

st.set_page_config(page_title="Web Table Extractor", page_icon="📊")
st.title("📊 Web Table to CSV Extractor")
st.markdown("Enter a webpage URL that contains HTML tables. Select one and download as a CSV.")

# Input: URL from user
url = st.text_input("🔗 Enter Website URL", placeholder="https://en.wikipedia.org/wiki/List_of_largest_companies_in_India")

# Only run extraction if URL is provided
if url:
    try:
        # Fetch and parse the page
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')

        # No tables found
        if not tables:
            st.warning("⚠️ No tables found on the page.")
        else:
            # Table selection (count starts from 1)
            st.markdown(f"✅ Found **{len(tables)}** tables.")
            table_index = st.selectbox("📋 Select Table Number", options=list(range(len(tables))), format_func=lambda x: f"Table {x + 1}")

            # Load selected table into DataFrame
            df = pd.read_html(StringIO(str(tables[table_index])))[0]
            st.dataframe(df)

            # Download as CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Download CSV", data=csv, file_name=f"table_{table_index + 1}.csv", mime='text/csv')

    except Exception as e:
        st.error(f"❌ Error: {e}")
