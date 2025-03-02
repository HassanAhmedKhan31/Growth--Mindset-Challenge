import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Set up the Streamlit app
st.set_page_config(page_title="Data Sweeper", layout="wide")

# Title of the app
st.title("Data Sweeper")
st.write("Transform your files between CSV and Excel formats with built-in data cleansing and visualization!")

# File uploader
uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        # Process each file
        file_extension = os.path.splitext(uploaded_file.name)[-1].lower()
        try:
            if file_extension == ".csv":
                df = pd.read_csv(uploaded_file)
            elif file_extension == ".xlsx":
                df = pd.read_excel(uploaded_file)
            else:
                st.error(f"Unsupported file type: {file_extension}")
                continue
        except Exception as e:
            st.error(f"Error reading file {uploaded_file.name}: {e}")
            continue
        
        # Display file information
        st.write(f"File name: {uploaded_file.name}")
        st.write(f"File size: {uploaded_file.size / 1024:.2f} KB")
        st.write("Preview of the uploaded data:")
        st.write(df.head())

        # Data cleaning options
        st.subheader("Data Cleaning Options")
        col3, col2 = st.columns(2)  # Define columns outside the if block
        if st.checkbox(f"Clean data for {uploaded_file.name}"):
            with col3:
                if st.checkbox("Remove duplicates", key=f"remove_duplicates_{uploaded_file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("Duplicates removed")
            with col2:
                if st.checkbox("Fill missing values with average", key=f"fill_missing_{uploaded_file.name}"):
                    numeric_cols = df.select_dtypes(include='number').columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("Missing values filled with average")
        
        # Choose Specific Columns to keep or convert
        st.subheader("Select Column to Convert")
        columns = st.multiselect(f"Choose Columns for {uploaded_file.name}", df.columns, default=df.columns)
        df = df[columns]

        # Visualize data
        st.subheader("Data Visualization")
        if st.checkbox("Show visualization", key=f"visualize_{uploaded_file.name}"):
            numeric_cols = df.select_dtypes(include='number').columns
            if len(numeric_cols) > 0:
                st.bar_chart(df[numeric_cols].head())
            else:
                st.warning("No numeric columns available for visualization.")

        # File conversion section
        st.subheader("File Conversion")
        conversion_type = st.radio("Choose conversion type:", options=["CSV", "Excel"], key=f"conversion_{uploaded_file.name}")
        
        if st.button("Convert and Download", key=f"convert_{uploaded_file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                buffer.seek(0)
                st.download_button(
                    label="Download CSV",
                    data=buffer,
                    file_name=f"{uploaded_file.name.replace(file_extension, '.csv')}",
                    mime="text/csv"
                )
            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False)
                buffer.seek(0)
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                file_name = f"{uploaded_file.name.replace(file_extension, '.xlsx')}"
                
                st.download_button(
                    label=f"Download {uploaded_file.name} as {conversion_type}",
                    data=buffer,
                    file_name=file_name,
                    mime=mime_type
                )

st.success("All files processed successfully!")