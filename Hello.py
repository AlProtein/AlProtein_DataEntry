


# Hello.py
import streamlit as st
from streamlit.logger import get_logger
import pandas as pd
import psycopg2
from datetime import datetime
import boto3
import os

LOGGER = get_logger(__name__)

# AWS S3 Configuration
S3_BUCKET_NAME = "microscope-imgs"  
AWS_ACCESS_KEY = "AKIA6F35EAK7J4KOAUO2"  
AWS_SECRET_KEY = "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" 
AWS_REGION = "us-east-1"  

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

# Database functions
def create_connection():
    conn = psycopg2.connect(
        database="research",
        user="alpro",
        password="PVtgs8mtGsThUEl2NjR0",
        host="research.c2bcka4zvdxd.us-east-1.rds.amazonaws.com",
        port="5432"
    )
    return conn

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS research_data
                    (id SERIAL PRIMARY KEY,
                     datetime TIMESTAMP,
                     dry_weight FLOAT,
                     ph FLOAT);''')
    cursor.execute('''ALTER TABLE research_data
                    ADD COLUMN IF NOT EXISTS ph FLOAT;''')
    conn.commit()

def insert_data(conn, datetime, dry_weight, ph):
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO research_data (datetime, dry_weight, ph)
                      VALUES (%s, %s, %s);''', (datetime, dry_weight, ph))
    conn.commit()
    st.success("Data inserted successfully!")

def fetch_data(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM research_data;')
    data = cursor.fetchall()
    return data

# S3 functions
def upload_to_s3(file, filename):
    try:
        s3_client.upload_fileobj(file, S3_BUCKET_NAME, f"images/{filename}")
        return True
    except Exception as e:
        st.error(f"Error uploading to S3: {str(e)}")
        return False

# Page functions
def show_header():
    st.image("public-logo.png", width=150)
    st.markdown("""
    <div style="text-align: center;">
        <h1 style="margin-bottom: 0; color: green;">AlProtein Data Entry 👨🏻‍💻</h1>
        <hr style="margin-top: 0;">
    </div>
    """, unsafe_allow_html=True)

def numerical_data_page():
    st.markdown("## Numerical Data Entry")

    st.markdown("""
    🚀 **For R&D Team:**
    Enter numerical research data including datetime, dry weight, and pH values.
    """)

    current_year = datetime.now().year
    current_month = datetime.now().month
    default_datetime = f"{current_year}-{current_month:02}-01 00:00:00"

    st.markdown("### Enter Research Data 👇")
    datetime_input = st.text_input("Enter Datetime ⏰⏰:", default_datetime)
    dry_weight_input = st.number_input("Enter Dry Weight ⚖️⚖️:", min_value=0.0)
    ph_input = st.number_input("Enter pH 🧪🧪:", min_value=0.0, max_value=14.0, step=0.01)

    if st.button("Submit"):
        try:
            if len(datetime_input) == 16:
                datetime_input += ":00"
            pd.to_datetime(datetime_input, format='%Y-%m-%d %H:%M:%S')
        except ValueError:
            st.error("Please enter datetime in the format YYYY-MM-DD HH:MM")
            return

        if not (0 <= ph_input <= 14):
            st.error("Please enter a valid pH value between 0 and 14.")
            return

        conn = create_connection()
        create_table(conn)
        insert_data(conn, datetime_input, dry_weight_input, ph_input)
        conn.close()

    if st.button("View Data"):
        conn = create_connection()
        data = fetch_data(conn)
        conn.close()
        df = pd.DataFrame(data, columns=['ID', 'Datetime', 'Dry Weight', 'pH'])
        st.dataframe(df)

def image_data_page():
    st.markdown("## Image Data Upload")

    st.markdown("""
    📸 **For Image Analysis:**
    Upload research-related images to S3 storage.
    """)

    # Image upload section
    st.markdown("### Upload Images 📸")
    uploaded_files = st.file_uploader("Choose image files", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

    # Upload to S3 button
    if uploaded_files:
        if st.button("Upload Images to S3"):
            success_count = 0
            for uploaded_file in uploaded_files:
                if upload_to_s3(uploaded_file, uploaded_file.name):
                    success_count += 1

            if success_count == len(uploaded_files):
                st.success(f"Successfully uploaded {success_count} images to S3 bucket!")
            else:
                st.warning(f"Uploaded {success_count} out of {len(uploaded_files)} images to S3 bucket.")

def main():
    st.set_page_config(page_title="Research Data Entry", page_icon=":bar_chart:", layout="wide")

    show_header()

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select Page", ["Numerical Data Entry", "Image Data Upload"])

    if page == "Numerical Data Entry":
        numerical_data_page()
    else:
        image_data_page()

if __name__ == "__main__":
    main()