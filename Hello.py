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

# It's recommended to use Streamlit secrets for storing credentials
# For demonstration, they are hardcoded here.
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

# --- Spirulina/Water Lentils Image Functions (UPDATED) ---
def validate_image_name(filename):
    # New format: SPYYMMDD(C/T)N-YYMMDD-N-(P/C)
    # Example: SP250303C2-250401-1-P.jpg
    pattern = r'^(SP|WL)\d{6}[CT]\d{1,2}-\d{6}-\d{1,2}-[PC]\.[a-zA-Z]+$'
    return bool(re.match(pattern, filename))

def parse_image_name(filename):
    # New parsing for SP250303C2-250401-1-P
    name = os.path.splitext(filename)[0]
    try:
        culture_tank_id, image_date, image_counter, purity = name.split('-')
        strain = culture_tank_id[:2]
        return {
            'strain': strain,
            'culture_tank_id': culture_tank_id,
            'image_date': image_date,
            'image_counter': image_counter,
            'purity': purity
        }
    except:
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
                "Invalid filename format. Expected: SPYYMMDD(C/T)N-YYMMDD-N-(P/C)\n"
                "Example: SP250303C2-250401-1-P"
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

# --- Tanks Image Functions (Original - Unchanged) ---
def validate_tank_image_name(filename):
    # Example: SP-2314-20250518-Right.jpg
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
    """)
    
    st.markdown("""
    ### Naming Convention Guide:

    **Format:** `SPYYMMDD(C/T)N-YYMMDD-N-(P/C)`

    **Components:**
    1.  **Culture/Tank ID:**
        * **Strain (2 letters):** `SP` (Spirulina) or `WL` (Water Lentils)
        * **Start Date (YYMMDD):** Date the culture or tank was started.
        * **Type (1 letter):** `C` for Culture or `T` for Tank.
        * **Number (1 or 2 digits):** The index number of the culture or tank.

    2.  **Image Date (YYMMDD):**
        * The date the image was acquired.

    3.  **Image Counter (1 or 2 digits):**
        * The sequence number of the image taken on that day.

    4.  **Purity (1 letter):**
        * `P`: Pure culture
        * `C`: Contaminated culture

    **Examples:**
    * `SP250303C2-250401-1-P`
    * `SP250303T2-250401-1-C`
    """)

    st.markdown("### Upload Images 📸")
    uploaded_files = st.file_uploader("Choose image files", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
    if uploaded_files:
        if st.button("Upload Images to S3"):
            success_count = 0
            for uploaded_file in uploaded_files:
                success, error_message = upload_to_s3(uploaded_file, uploaded_file.name)
                if success:
                    success_count += 1
                    folder = get_folder_path(uploaded_file.name)
                    components = parse_image_name(uploaded_file.name)
                    st.success(f"""
                        Successfully uploaded image:
                        - **File:** {uploaded_file.name}
                        - **Culture/Tank ID:** {components['culture_tank_id']}
                        - **Image Date:** {components['image_date']}
                        - **Image Counter:** {components['image_counter']}
                        - **Purity:** {'Pure' if components['purity'] == 'P' else 'Contaminated'}
                        - **Folder:** {folder}
                    """)
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
        - Unique culture identifier
        - Example: 2314, 1441

    3. **Date (YYYYMMDD):**
        - Format: Year-Month-Day
        - Example: 20250518

    4. **Position:**
        - Right
        - Left
        - Center

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



# import streamlit as st
# from streamlit.logger import get_logger
# import pandas as pd
# import psycopg2
# from datetime import datetime
# import boto3
# import os
# import re

# LOGGER = get_logger(__name__)

# # --- AWS S3 Configuration ---
# S3_BUCKET_NAME = "microscope-imgs"  # For Spirulina/Water Lentils images
# TANKS_S3_BUCKET_NAME = "tanks-imgs"  # For Tanks images

# AWS_ACCESS_KEY = "AKIA6F35EAK7J4KOAUO2"
# AWS_SECRET_KEY = "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"
# AWS_REGION = "us-east-1"

# # Initialize S3 client
# s3_client = boto3.client(
#     "s3",
#     aws_access_key_id=AWS_ACCESS_KEY,
#     aws_secret_access_key=AWS_SECRET_KEY,
#     region_name=AWS_REGION
# )

# # --- Database Functions ---
# def create_connection():
#     conn = psycopg2.connect(
#         database="research",
#         user="alpro",
#         password="PVtgs8mtGsThUEl2NjR0",
#         host="research.c2bcka4zvdxd.us-east-1.rds.amazonaws.com",
#         port="5432"
#     )
#     return conn

# def create_table(conn):
#     cursor = conn.cursor()
#     cursor.execute('''CREATE TABLE IF NOT EXISTS research_data
#                     (id SERIAL PRIMARY KEY,
#                      datetime TIMESTAMP,
#                      dry_weight FLOAT,
#                      ph FLOAT);''')
#     cursor.execute('''ALTER TABLE research_data
#                     ADD COLUMN IF NOT EXISTS ph FLOAT;''')
#     conn.commit()

# def insert_data(conn, datetime, dry_weight, ph):
#     cursor = conn.cursor()
#     cursor.execute('''INSERT INTO research_data (datetime, dry_weight, ph)
#                       VALUES (%s, %s, %s);''', (datetime, dry_weight, ph))
#     conn.commit()
#     st.success("Data inserted successfully!")

# def fetch_data(conn):
#     cursor = conn.cursor()
#     cursor.execute('SELECT * FROM research_data;')
#     data = cursor.fetchall()
#     return data

# # --- Spirulina/Water Lentils Image Functions ---
# def validate_image_name(filename):
#     pattern = r'^(SP|WL)-\d{4}-\d{8}-[PC]\.[a-zA-Z]+$'
#     return bool(re.match(pattern, filename))

# def parse_image_name(filename):
#     name = os.path.splitext(filename)[0]
#     try:
#         strain, culture_num, date, purity = name.split('-')
#         return {
#             'strain': strain,
#             'culture_number': culture_num,
#             'date': date,
#             'purity': purity
#         }
#     except:
#         return None

# def get_folder_path(filename):
#     components = parse_image_name(filename)
#     if not components:
#         return None
#     if components['strain'] == 'SP':
#         return 'Spirulina'
#     elif components['strain'] == 'WL':
#         return 'Water Lentils'
#     return None

# def upload_to_s3(file, filename):
#     try:
#         if not validate_image_name(filename):
#             raise ValueError(
#                 "Invalid filename format. Expected format: 'STRAIN-CULTURENUMBER-YYYYMMDD-PURITY'\n"
#                 "Example: SP-2314-20250327-P or WL-1441-20250223-C"
#             )
#         components = parse_image_name(filename)
#         if not components:
#             raise ValueError("Unable to parse filename components")
#         folder = get_folder_path(filename)
#         if not folder:
#             raise ValueError("Invalid strain prefix. Must be 'SP' or 'WL'")
#         s3_path = f"images/{folder}/{filename}"
#         s3_client.upload_fileobj(file, S3_BUCKET_NAME, s3_path)
#         return True, None
#     except Exception as e:
#         return False, str(e)

# # --- Tanks Image Functions (Updated Naming Convention) ---
# def validate_tank_image_name(filename):
#     # Example: SP-2314-20250518-Right.jpg
#     pattern = r'^(SP|WL)-\d{4}-\d{8}-(Right|Left|Center)\.[a-zA-Z]+$'
#     return bool(re.match(pattern, filename))

# def parse_tank_image_name(filename):
#     name = os.path.splitext(filename)[0]
#     try:
#         strain, culture_num, date, position = name.split('-')
#         return {
#             'culture_name': f"{strain}-{culture_num}",
#             'date': date,
#             'position': position
#         }
#     except:
#         return None

# def upload_tank_image_to_s3(file, filename):
#     try:
#         if not validate_tank_image_name(filename):
#             raise ValueError(
#                 "Invalid filename format. Expected: STRAIN-CULTURENUMBER-YYYYMMDD-POSITION.jpg\n"
#                 "Example: SP-2314-20250518-Right.jpg"
#             )
#         components = parse_tank_image_name(filename)
#         if not components:
#             raise ValueError("Unable to parse filename components")
#         s3_path = f"tanks/{filename}"
#         s3_client.upload_fileobj(file, TANKS_S3_BUCKET_NAME, s3_path)
#         return True, None
#     except Exception as e:
#         return False, str(e)

# # --- UI Functions ---
# def show_header():
#     st.image("public-logo.png", width=150)
#     st.markdown("""
#     <div style="text-align: center;">
#         <h1 style="margin-bottom: 0; color: green;">AlProtein Data Entry 👨🏻‍💻</h1>
#         <hr style="margin-top: 0;">
#     </div>
#     """, unsafe_allow_html=True)

# def numerical_data_page():
#     st.markdown("## Numerical Data Entry")
#     st.markdown("""
#     🚀 **For R&D Team:**
#     Enter numerical research data including datetime, dry weight, and pH values.
#     """)
#     current_year = datetime.now().year
#     current_month = datetime.now().month
#     default_datetime = f"{current_year}-{current_month:02}-01 00:00:00"
#     st.markdown("### Enter Research Data 👇")
#     datetime_input = st.text_input("Enter Datetime ⏰⏰:", default_datetime)
#     dry_weight_input = st.number_input("Enter Dry Weight ⚖️⚖️:", min_value=0.0)
#     ph_input = st.number_input("Enter pH 🧪🧪:", min_value=0.0, max_value=14.0, step=0.01)
#     if st.button("Submit"):
#         try:
#             if len(datetime_input) == 16:
#                 datetime_input += ":00"
#             pd.to_datetime(datetime_input, format='%Y-%m-%d %H:%M:%S')
#         except ValueError:
#             st.error("Please enter datetime in the format YYYY-MM-DD HH:MM")
#             return
#         if not (0 <= ph_input <= 14):
#             st.error("Please enter a valid pH value between 0 and 14.")
#             return
#         conn = create_connection()
#         create_table(conn)
#         insert_data(conn, datetime_input, dry_weight_input, ph_input)
#         conn.close()
#     if st.button("View Data"):
#         conn = create_connection()
#         data = fetch_data(conn)
#         conn.close()
#         df = pd.DataFrame(data, columns=['ID', 'Datetime', 'Dry Weight', 'pH'])
#         st.dataframe(df)

# def image_data_page():
#     st.markdown("## Image Data Upload")
#     st.markdown("""
#     📸 **For Image Analysis:**
#     Upload research-related images to S3 storage.

#     ### Naming Convention Guide:

#     **Format:** STRAIN-CULTURENUMBER-DATE-PURITY

#     **Components:**
#     1. **Strain (2 letters):**
#         - SP: Spirulina
#         - WL: Water Lentils

#     2. **Culture Number (4 digits):**
#         - Unique culture identifier
#         - Example: 2314, 1441

#     3. **Date (YYYYMMDD):**
#         - Format: Year-Month-Day
#         - Example: 20250327

#     4. **Purity (1 letter):**
#         - P: Pure culture
#         - C: Contaminated culture

#     **Examples:**
#     - SP-2314-20250327-P (Spirulina, Culture 2314, March 27, 2025, Pure)
#     - WL-1441-20250223-C (Water Lentils, Culture 1441, February 23, 2025, Contaminated)
#     """)
#     st.markdown("### Upload Images 📸")
#     uploaded_files = st.file_uploader("Choose image files", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
#     if uploaded_files:
#         if st.button("Upload Images to S3"):
#             success_count = 0
#             for uploaded_file in uploaded_files:
#                 success, error_message = upload_to_s3(uploaded_file, uploaded_file.name)
#                 if success:
#                     success_count += 1
#                     folder = get_folder_path(uploaded_file.name)
#                     components = parse_image_name(uploaded_file.name)
#                     st.success(f"""
#                         Successfully uploaded image:
#                         - File: {uploaded_file.name}
#                         - Strain: {components['strain']}
#                         - Culture: {components['culture_number']}
#                         - Date: {components['date']}
#                         - Purity: {'Pure' if components['purity'] == 'P' else 'Contaminated'}
#                         - Folder: {folder}
#                     """)
#                 else:
#                     st.error(f"Failed to upload {uploaded_file.name}: {error_message}")
#             st.info(f"Upload complete: {success_count} out of {len(uploaded_files)} files uploaded successfully.")

# def tanks_image_data_page():
#     st.markdown("## Tanks Image Data Upload")
#     st.markdown("""
#     🛢️ **For Tanks Monitoring:**
#     Upload tank images to S3 storage.

#     ### Naming Convention Guide:

#     **Format:** STRAIN-CULTURENUMBER-YYYYMMDD-POSITION

#     **Components:**
#     1. **Strain (2 letters):**
#         - SP: Spirulina
#         - WL: Water Lentils

#     2. **Culture Number (4 digits):**
#         - Unique culture identifier
#         - Example: 2314, 1441

#     3. **Date (YYYYMMDD):**
#         - Format: Year-Month-Day
#         - Example: 20250518

#     4. **Position:**
#         - Right
#         - Left
#         - Center

#     **Example:** SP-2314-20250518-Right.jpg
#     """)
#     uploaded_files = st.file_uploader("Choose tank image files", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
#     if uploaded_files:
#         if st.button("Upload Tank Images to S3"):
#             success_count = 0
#             for uploaded_file in uploaded_files:
#                 success, error_message = upload_tank_image_to_s3(uploaded_file, uploaded_file.name)
#                 if success:
#                     components = parse_tank_image_name(uploaded_file.name)
#                     st.success(f"""
#                         Uploaded: {uploaded_file.name}
#                         - Culture Name: {components['culture_name']}
#                         - Date: {components['date']}
#                         - Position: {components['position']}
#                     """)
#                     success_count += 1
#                 else:
#                     st.error(f"Failed to upload {uploaded_file.name}: {error_message}")
#             st.info(f"Upload complete: {success_count} out of {len(uploaded_files)} files uploaded successfully.")

# def main():
#     st.set_page_config(page_title="Research Data Entry", page_icon=":bar_chart:", layout="wide")
#     show_header()
#     st.sidebar.title("Navigation")
#     page = st.sidebar.radio("Select Page", [
#         "Numerical Data Entry",
#         "Image Data Upload",
#         "Tanks Image Data Upload"
#     ])
#     if page == "Numerical Data Entry":
#         numerical_data_page()
#     elif page == "Image Data Upload":
#         image_data_page()
#     elif page == "Tanks Image Data Upload":
#         tanks_image_data_page()

# if __name__ == "__main__":
#     main()


