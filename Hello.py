import streamlit as st
from streamlit.logger import get_logger
import pandas as pd
import psycopg2
from datetime import datetime
import boto3
import os
import re

LOGGER = get_logger(__name__)

# --- AWS S3 Configuration ---
S3_BUCKET_NAME = "microscope-imgs"  # For Spirulina/Water Lentils images
TANKS_S3_BUCKET_NAME = "tanks-imgs"  # For Tanks images

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

# --- Database Functions ---
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

# --- Image Naming Convention Functions ---

def validate_image_name(filename):
    # Format: SPYYMMDD(C/T)N-YYMMDD-N-(P/C).<ext>
    pattern = r'^(SP|WL)\d{6}[CT]\d{1,2}-\d{6}-\d{1,2}-[PC]\.[a-zA-Z]+$'
    return bool(re.match(pattern, filename))

def parse_image_name(filename):
    # Format: SP250303C2-250401-1-P.jpg
    name = os.path.splitext(filename)[0]
    try:
        first, second, image_counter, purity = name.split('-')
        # first: SP250303C2 or WL250303T2   (strain+date+c/t+N)
        strain = first[:2]
        culture_date = first[2:8]
        c_t = first[8]
        culture_num = first[9:]
        image_date = second
        image_num = image_counter
        return {
            'strain': strain,
            'culture_date': culture_date,
            'c_t': c_t,
            'culture_num': culture_num,
            'image_date': image_date,
            'image_num': image_num,
            'purity': purity
        }
    except Exception as e:
        return None

def get_folder_path(filename):
    components = parse_image_name(filename)
    if not components:
        return None
    if components['strain'] == 'SP':
        return 'Spirulina'
    elif components['strain'] == 'WL':
        return 'Water Lentils'
    return None

def upload_to_s3(file, filename):
    try:
        if not validate_image_name(filename):
            raise ValueError(
                "Invalid filename format. Expected: SPYYMMDD(C/T)N-YYMMDD-N-(P/C).<ext>\n"
                "Example: SP250303C2-250401-1-P.jpg"
            )
        components = parse_image_name(filename)
        if not components:
            raise ValueError("Unable to parse filename components")
        folder = get_folder_path(filename)
        if not folder:
            raise ValueError("Invalid strain prefix. Must be 'SP' or 'WL'")
        s3_path = f"images/{folder}/{filename}"
        s3_client.upload_fileobj(file, S3_BUCKET_NAME, s3_path)
        return True, None
    except Exception as e:
        return False, str(e)

# --- Tanks Image Functions (No update, as spec unchanged) ---
def validate_tank_image_name(filename):
    pattern = r'^(SP|WL)-\d{4}-\d{8}-(Right|Left|Center)\.[a-zA-Z]+$'
    return bool(re.match(pattern, filename))

def parse_tank_image_name(filename):
    name = os.path.splitext(filename)[0]
    try:
        strain, culture_num, date, position = name.split('-')
        return {
            'culture_name': f"{strain}-{culture_num}",
            'date': date,
            'position': position
        }
    except:
        return None

def upload_tank_image_to_s3(file, filename):
    try:
        if not validate_tank_image_name(filename):
            raise ValueError(
                "Invalid filename format. Expected: STRAIN-CULTURENUMBER-YYYYMMDD-POSITION.jpg\n"
                "Example: SP-2314-20250518-Right.jpg"
            )
        components = parse_tank_image_name(filename)
        if not components:
            raise ValueError("Unable to parse filename components")
        s3_path = f"tanks/{filename}"
        s3_client.upload_fileobj(file, TANKS_S3_BUCKET_NAME, s3_path)
        return True, None
    except Exception as e:
        return False, str(e)

# --- UI Functions ---
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

    ### Naming Convention Guide:

    **Format:** SPYYMMDD(C/T)N-YYMMDD-N-(P/C).<ext>

    **First Block (Culture or Tank code):**
    - SP: Spirulina
    - WL: Water Lentils
    - YYMMDD: Date of culture/tank start (not image date)
    - C/T: C for Culture, T for Tank
    - N: Culture or tank number (1 or 2 digits)

    **Second Block (Image details):**
    - YYMMDD: Date of image acquisition
    - N: Image counter for that day (1 or 2 digits)

    **Purity:**
    - P: Pure
    - C: Contaminated

    **Examples:**
    - SP250303C2-250401-1-P.jpg (Spirulina, culture 2 started on Mar 3, 2025, image 1 on Apr 1, 2025, Pure)
    - SP250303T2-250401-1-C.jpg (Spirulina, **tank** 2 started Mar 3, 2025, image 1, Contaminated)
    """)
    st.markdown("### Upload Images 📸")
    uploaded_files = st.file_uploader("Choose image files", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
    if uploaded_files:
        if st.button("Upload Images to S3"):
            success_count = 0
            for uploaded_file in uploaded_files:
                success, error_message = upload_to_s3(uploaded_file, uploaded_file.name)
                if success:
                    folder = get_folder_path(uploaded_file.name)
                    components = parse_image_name(uploaded_file.name)
                    ctype = "Culture" if components['c_t'] == 'C' else "Tank"
                    st.success(f"""
                        Successfully uploaded image:
                        - File: {uploaded_file.name}
                        - Strain: {components['strain']}
                        - {ctype} Number: {components['culture_num']}
                        - {ctype} Date (YYMMDD): {components['culture_date']}
                        - Image Date (YYMMDD): {components['image_date']}
                        - Image #: {components['image_num']}
                        - Purity: {'Pure' if components['purity'] == 'P' else 'Contaminated'}
                        - Folder: {folder}
                    """)
                    success_count += 1
                else:
                    st.error(f"Failed to upload {uploaded_file.name}: {error_message}")
            st.info(f"Upload complete: {success_count} out of {len(uploaded_files)} files uploaded successfully.")

def tanks_image_data_page():
    st.markdown("## Tanks Image Data Upload")
    st.markdown("""
    🛢️ **For Tanks Monitoring:**
    Upload tank images to S3 storage.

    ### Naming Convention Guide:
    **Format:** STRAIN-CULTURENUMBER-YYYYMMDD-POSITION

    **Components:**
    1. **Strain (2 letters):**
        - SP: Spirulina
        - WL: Water Lentils
    2. **Culture Number (4 digits):**
        - Example: 2314, 1441
    3. **Date (YYYYMMDD):**
        - Example: 20250518
    4. **Position:**
        - Right, Left, Center

    **Example:** SP-2314-20250518-Right.jpg
    """)
    uploaded_files = st.file_uploader("Choose tank image files", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
    if uploaded_files:
        if st.button("Upload Tank Images to S3"):
            success_count = 0
            for uploaded_file in uploaded_files:
                success, error_message = upload_tank_image_to_s3(uploaded_file, uploaded_file.name)
                if success:
                    components = parse_tank_image_name(uploaded_file.name)
                    st.success(f"""
                        Uploaded: {uploaded_file.name}
                        - Culture Name: {components['culture_name']}
                        - Date: {components['date']}
                        - Position: {components['position']}
                    """)
                    success_count += 1
                else:
                    st.error(f"Failed to upload {uploaded_file.name}: {error_message}")
            st.info(f"Upload complete: {success_count} out of {len(uploaded_files)} files uploaded successfully.")

def main():
    st.set_page_config(page_title="Research Data Entry", page_icon=":bar_chart:", layout="wide")
    show_header()
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select Page", [
        "Numerical Data Entry",
        "Image Data Upload",
        "Tanks Image Data Upload"
    ])
    if page == "Numerical Data Entry":
        numerical_data_page()
    elif page == "Image Data Upload":
        image_data_page()
    elif page == "Tanks Image Data Upload":
        tanks_image_data_page()

if __name__ == "__main__":
    main()
