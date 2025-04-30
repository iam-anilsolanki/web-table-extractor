import gradio as gr
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import StringIO
import tempfile

# Function to fetch tables and provide previews
def get_tables_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')
        previews = []

        # Loop through each table and get a preview of the first 3 rows
        for i, table in enumerate(tables):
            df = pd.read_html(str(table))[0]
            preview = df.head(3).to_markdown(index=False)  # Preview first 3 rows
            previews.append(f"**Table {i} Preview:**\n{preview}")

        return "\n\n".join(previews), gr.update(choices=[str(i) for i in range(len(tables))], interactive=True), gr.update(visible=True)
    except Exception as e:
        return [f"Error: {e}"], gr.update(choices=[], interactive=False), gr.update(visible=False)

# Function to download the selected table as CSV
def download_table_as_csv(url, table_index):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')

        # Ensure the table exists and the index is valid
        if int(table_index) < len(tables):
            table_html = str(tables[int(table_index)])
            df = pd.read_html(StringIO(table_html))[0]  # Wrap HTML in StringIO to avoid deprecation warning

            # Create a temporary CSV file
            with tempfile.NamedTemporaryFile(delete=False, mode='w', newline='', suffix='.csv') as tmp_file:
                df.to_csv(tmp_file, index=False)
                tmp_file_path = tmp_file.name

            return df, tmp_file_path

        else:
            return pd.DataFrame(), "Error: Invalid table index."

    except Exception as e:
        return pd.DataFrame(), f"Error: {e}"

# Create Gradio interface
with gr.Blocks() as app:
    gr.Markdown("## 🕸️ Web Table Extractor to CSV")

    # URL input and button to fetch tables
    with gr.Row():
        url_input = gr.Textbox(label="Enter Website URL", placeholder="https://...")
        fetch_button = gr.Button("Fetch Tables")

    # Display table previews and dropdown for selecting the table
    table_previews = gr.Markdown()
    table_dropdown = gr.Dropdown(label="Select Table Number", interactive=False)
    proceed_button = gr.Button("Download as CSV", visible=False)

    # Output DataFrame and CSV download link
    output_df = gr.Dataframe()
    csv_file = gr.File(label="Download CSV", file_types=[".csv"])

    # Fetch tables and update preview and dropdown options
    fetch_button.click(fn=get_tables_from_url, inputs=[url_input],
                       outputs=[table_previews, table_dropdown, proceed_button])

    # Download the selected table as CSV
    proceed_button.click(fn=download_table_as_csv,
                         inputs=[url_input, table_dropdown],
                         outputs=[output_df, csv_file])

# Launch the Gradio app
app.launch()
