import os
import streamlit as st
import pandas as pd
from io import BytesIO  # Allows files to be stored temporarily in memory

# Set page configuration
st.set_page_config(page_title="💿 Data Sweeper", layout='wide')

# Page title and description
st.title("💿 Data Sweeper")
st.write(
    "Transform your files between CSV and Excel formats with built-in "
    "data-cleaning and visualization methods!"
)

# File uploader
upload_files = st.file_uploader(
    "Upload your files (CSV or Excel)", type=["csv", "xlsx"], accept_multiple_files=True
)

# Function to format file sizes dynamically
def format_file_size(size_in_bytes):
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024**2:
        return f"{size_in_bytes / 1024:.2f} KB"
    elif size_in_bytes < 1024**3:
        return f"{size_in_bytes / 1024**2:.2f} MB"
    else:
        return f"{size_in_bytes / 1024**3:.2f} GB"

if upload_files:
    for file in upload_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        # Read file based on its extension
        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue

        # Display file info
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {format_file_size(file.size)}")

        # Show dataframe preview
        st.write("🔎 **Preview the Head of the DataFrame**")
        st.dataframe(df.head())

        # Data cleaning options
        st.subheader("🛠 Data Cleaning Options")
        if st.checkbox(f"Clean data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("✅ Duplicates removed")

            with col2:
                if st.button(f"Fill missing values for {file.name}"):
                    numeric_columns = df.select_dtypes(include=["number"]).columns
                    df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].mean())
                    st.write("✅ Missing values have been filled")

        # Column selection
        st.subheader("✨ Select Columns to Convert")
        selected_columns = st.multiselect(
            f"Choose columns for {file.name}", df.columns, default=df.columns
        )
        df = df[selected_columns]

        # Data visualization
        st.subheader("📊 Data Visualization")
        if st.checkbox(f"Show visualization for {file.name}"):
            if df.select_dtypes(include="number").shape[1] >= 2:
                st.bar_chart(df.select_dtypes(include="number").iloc[:, :2])
            else:
                st.warning("⚠️ Not enough numeric columns to create a bar chart.")

        # File conversion options
        st.subheader("♻️ Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)

        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"

            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False, engine="xlsxwriter")
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            buffer.seek(0)

            # Download Button
            if st.download_button(
                label=f"⬇️ Download {file.name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type,
            ):
                st.success("🎉 Successfully downloaded the updated file.")
