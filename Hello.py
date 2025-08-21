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
#         password="y13HLddTiOes36FWZoYY",
#         host="research.c2bcka4zvdxd.us-east-1.rds.amazonaws.com",
#         port="5432"
#     )
#     postgres
#     #82TcYIPjshp0b7C6aYhO
#     #alprotein-data-entry.cluster-c2bcka4zvdxd.us-east-1.rds.amazonaws.com

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

# # --- Image Naming Convention Functions ---

# def validate_image_name(filename):
#     # Format: SPYYMMDD(C/T)N-YYMMDD-N-(P/C).<ext>
#     pattern = r'^(SP|WL)\d{6}[CT]\d{1,2}-\d{6}-\d{1,2}-[PC]\.[a-zA-Z]+$'
#     return bool(re.match(pattern, filename))

# def parse_image_name(filename):
#     # Format: SP250303C2-250401-1-P.jpg
#     name = os.path.splitext(filename)[0]
#     try:
#         first, second, image_counter, purity = name.split('-')
#         # first: SP250303C2 or WL250303T2   (strain+date+c/t+N)
#         strain = first[:2]
#         culture_date = first[2:8]
#         c_t = first[8]
#         culture_num = first[9:]
#         image_date = second
#         image_num = image_counter
#         return {
#             'strain': strain,
#             'culture_date': culture_date,
#             'c_t': c_t,
#             'culture_num': culture_num,
#             'image_date': image_date,
#             'image_num': image_num,
#             'purity': purity
#         }
#     except Exception as e:
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
#                 "Invalid filename format. Expected: SPYYMMDD(C/T)N-YYMMDD-N-(P/C).<ext>\n"
#                 "Example: SP250303C2-250401-1-P.jpg"
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

# # --- Tanks Image Functions (No update, as spec unchanged) ---
# def validate_tank_image_name(filename):
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

#     **Format:** SPYYMMDD(C/T)N-YYMMDD-N-(P/C).<ext>

#     **First Block (Culture or Tank code):**
#     - SP: Spirulina
#     - WL: Water Lentils
#     - YYMMDD: Date of culture/tank start (not image date)
#     - C/T: C for Culture, T for Tank
#     - N: Culture or tank number (1 or 2 digits)

#     **Second Block (Image details):**
#     - YYMMDD: Date of image acquisition
#     - N: Image counter for that day (1 or 2 digits)

#     **Purity:**
#     - P: Pure
#     - C: Contaminated

#     **Examples:**
#     - SP250303C2-250401-1-P.jpg (Spirulina, culture 2 started on Mar 3, 2025, image 1 on Apr 1, 2025, Pure)
#     - SP250303T2-250401-1-C.jpg (Spirulina, **tank** 2 started Mar 3, 2025, image 1, Contaminated)
#     """)
#     st.markdown("### Upload Images 📸")
#     uploaded_files = st.file_uploader("Choose image files", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
#     if uploaded_files:
#         if st.button("Upload Images to S3"):
#             success_count = 0
#             for uploaded_file in uploaded_files:
#                 success, error_message = upload_to_s3(uploaded_file, uploaded_file.name)
#                 if success:
#                     folder = get_folder_path(uploaded_file.name)
#                     components = parse_image_name(uploaded_file.name)
#                     ctype = "Culture" if components['c_t'] == 'C' else "Tank"
#                     st.success(f"""
#                         Successfully uploaded image:
#                         - File: {uploaded_file.name}
#                         - Strain: {components['strain']}
#                         - {ctype} Number: {components['culture_num']}
#                         - {ctype} Date (YYMMDD): {components['culture_date']}
#                         - Image Date (YYMMDD): {components['image_date']}
#                         - Image #: {components['image_num']}
#                         - Purity: {'Pure' if components['purity'] == 'P' else 'Contaminated'}
#                         - Folder: {folder}
#                     """)
#                     success_count += 1
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
#         - Example: 2314, 1441
#     3. **Date (YYYYMMDD):**
#         - Example: 20250518
#     4. **Position:**
#         - Right, Left, Center

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




# import streamlit as st
# from streamlit.logger import get_logger
# import pandas as pd
# import psycopg2
# from datetime import datetime
# import boto3
# import os
# import re
# import numpy as np

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
#     """Establishes a connection to the PostgreSQL database."""
#     conn = psycopg2.connect(
#         database="research",
#         user="alpro",
#         password="y13HLddTiOes36FWZoYY",
#         host="research.c2bcka4zvdxd.us-east-1.rds.amazonaws.com",
#         port="5423"
#     )
#     return conn

# def create_table(conn):
#     """Creates the research_data table if it doesn't exist."""
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
#     """Inserts numerical data into the research_data table."""
#     cursor = conn.cursor()
#     cursor.execute('''INSERT INTO research_data (datetime, dry_weight, ph)
#                       VALUES (%s, %s, %s);''', (datetime, dry_weight, ph))
#     conn.commit()
#     st.success("Data inserted successfully!")

# def fetch_data(conn):
#     """Fetches all data from the research_data table."""
#     cursor = conn.cursor()
#     cursor.execute('SELECT * FROM research_data;')
#     data = cursor.fetchall()
#     return data

# # --- Manual Data Entry Functions ---
# def create_manual_entry_table(conn):
#     """Creates the manual_data_entry table if it doesn't exist."""
#     cursor = conn.cursor()
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS manual_data_entry (
#             id SERIAL PRIMARY KEY,
#             timestamp TIMESTAMP NOT NULL,
#             ph FLOAT,
#             tds FLOAT,
#             do FLOAT,
#             concentration FLOAT,
#             light FLOAT
#         );
#     ''')
#     conn.commit()

# def insert_manual_data(conn, timestamp, ph, tds, do, concentration, light):
#     """Inserts data from the manual entry form into the database."""
#     cursor = conn.cursor()
#     query = '''
#         INSERT INTO manual_data_entry (timestamp, ph, tds, do, concentration, light)
#         VALUES (%s, %s, %s, %s, %s, %s);
#     '''
#     # Use None for np.nan values so psycopg2 converts them to NULL
#     data = (
#         timestamp,
#         ph if not pd.isna(ph) else None,
#         tds if not pd.isna(tds) else None,
#         do if not pd.isna(do) else None,
#         concentration if not pd.isna(concentration) else None,
#         light if not pd.isna(light) else None
#     )
#     cursor.execute(query, data)
#     conn.commit()

# def fetch_last_five_manual_entries(conn):
#     """Fetches the last 5 entries from the manual_data_entry table."""
#     cursor = conn.cursor()
#     cursor.execute('SELECT * FROM manual_data_entry ORDER BY timestamp DESC LIMIT 5;')
#     data = cursor.fetchall()
#     return data


# # --- Image Naming Convention Functions ---

# def validate_image_name(filename):
#     # Format: SPYYMMDD(C/T)N-YYMMDD-N-(P/C).<ext>
#     pattern = r'^(SP|WL)\d{6}[CT]\d{1,2}-\d{6}-\d{1,2}-[PC]\.[a-zA-Z]+$'
#     return bool(re.match(pattern, filename))

# def parse_image_name(filename):
#     # Format: SP250303C2-250401-1-P.jpg
#     name = os.path.splitext(filename)[0]
#     try:
#         first, second, image_counter, purity = name.split('-')
#         # first: SP250303C2 or WL250303T2   (strain+date+c/t+N)
#         strain = first[:2]
#         culture_date = first[2:8]
#         c_t = first[8]
#         culture_num = first[9:]
#         image_date = second
#         image_num = image_counter
#         return {
#             'strain': strain,
#             'culture_date': culture_date,
#             'c_t': c_t,
#             'culture_num': culture_num,
#             'image_date': image_date,
#             'image_num': image_num,
#             'purity': purity
#         }
#     except Exception as e:
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
#                 "Invalid filename format. Expected: SPYYMMDD(C/T)N-YYMMDD-N-(P/C).<ext>\n"
#                 "Example: SP250303C2-250401-1-P.jpg"
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

# # --- Tanks Image Functions (No update, as spec unchanged) ---
# def validate_tank_image_name(filename):
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

# def manual_data_entry_page():
#     """UI for the new manual data entry section."""
#     st.markdown("## Manual Data Entry")
#     st.markdown("📝 **For R&D Team:** Manually input sensor data.")

#     # --- Data Entry Form ---
#     st.markdown("### Enter Sensor Data 👇")
    
#     # Use two columns for a better layout
#     col1, col2 = st.columns(2)

#     with col1:
#         timestamp_date = st.date_input("Date", value=datetime.now().date())
#         timestamp_time = st.time_input("Time", value=datetime.now().time())
#         ph_input = st.number_input("Enter pH", value=None, placeholder="Optional", format="%.2f")
#         tds_input = st.number_input("Enter TDS (ppm)", value=None, placeholder="Optional", format="%.2f")

#     with col2:
#         do_input = st.number_input("Enter DO (mg/L)", value=None, placeholder="Optional", format="%.2f")
#         concentration_input = st.number_input("Enter Concentration (g/L)", value=None, placeholder="Optional", format="%.4f")
#         light_input = st.number_input("Enter Light (lux)", value=None, placeholder="Optional", format="%.2f")

#     if st.button("Submit Manual Entry"):
#         # Combine date and time to create a datetime object
#         timestamp_input = datetime.combine(timestamp_date, timestamp_time)

#         # Collect all optional inputs
#         optional_inputs = [ph_input, tds_input, do_input, concentration_input, light_input]
        
#         # Check if at least one optional input has a value
#         if not any(v is not None for v in optional_inputs):
#             st.error("Please enter a value for at least one variable besides the timestamp.")
#         else:
#             try:
#                 conn = create_connection()
#                 create_manual_entry_table(conn)
                
#                 # Replace None with np.nan for database insertion
#                 ph_val = ph_input if ph_input is not None else np.nan
#                 tds_val = tds_input if tds_input is not None else np.nan
#                 do_val = do_input if do_input is not None else np.nan
#                 concentration_val = concentration_input if concentration_input is not None else np.nan
#                 light_val = light_input if light_input is not None else np.nan

#                 insert_manual_data(conn, timestamp_input, ph_val, tds_val, do_val, concentration_val, light_val)
#                 st.success("Data successfully added!")
#                 conn.close()
#             except Exception as e:
#                 st.error(f"An error occurred: {e}")

#     # --- Query Last 5 Entries ---
#     st.markdown("---")
#     if st.button("Query Last 5 Data Entries"):
#         try:
#             conn = create_connection()
#             data = fetch_last_five_manual_entries(conn)
#             conn.close()
#             if data:
#                 df = pd.DataFrame(data, columns=['ID', 'Timestamp', 'pH', 'TDS', 'DO', 'Concentration', 'Light'])
#                 st.dataframe(df)
#             else:
#                 st.info("No data found in the manual entry table.")
#         except Exception as e:
#             st.error(f"An error occurred while fetching data: {e}")


# def image_data_page():
#     st.markdown("## Image Data Upload")
#     st.markdown("""
#     📸 **For Image Analysis:**
#     Upload research-related images to S3 storage.

#     ### Naming Convention Guide:

#     **Format:** SPYYMMDD(C/T)N-YYMMDD-N-(P/C).<ext>

#     **First Block (Culture or Tank code):**
#     - SP: Spirulina
#     - WL: Water Lentils
#     - YYMMDD: Date of culture/tank start (not image date)
#     - C/T: C for Culture, T for Tank
#     - N: Culture or tank number (1 or 2 digits)

#     **Second Block (Image details):**
#     - YYMMDD: Date of image acquisition
#     - N: Image counter for that day (1 or 2 digits)

#     **Purity:**
#     - P: Pure
#     - C: Contaminated

#     **Examples:**
#     - SP250303C2-250401-1-P.jpg (Spirulina, culture 2 started on Mar 3, 2025, image 1 on Apr 1, 2025, Pure)
#     - SP250303T2-250401-1-C.jpg (Spirulina, **tank** 2 started Mar 3, 2025, image 1, Contaminated)
#     """)
#     st.markdown("### Upload Images 📸")
#     uploaded_files = st.file_uploader("Choose image files", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
#     if uploaded_files:
#         if st.button("Upload Images to S3"):
#             success_count = 0
#             for uploaded_file in uploaded_files:
#                 success, error_message = upload_to_s3(uploaded_file, uploaded_file.name)
#                 if success:
#                     folder = get_folder_path(uploaded_file.name)
#                     components = parse_image_name(uploaded_file.name)
#                     ctype = "Culture" if components['c_t'] == 'C' else "Tank"
#                     st.success(f"""
#                         Successfully uploaded image:
#                         - File: {uploaded_file.name}
#                         - Strain: {components['strain']}
#                         - {ctype} Number: {components['culture_num']}
#                         - {ctype} Date (YYMMDD): {components['culture_date']}
#                         - Image Date (YYMMDD): {components['image_date']}
#                         - Image #: {components['image_num']}
#                         - Purity: {'Pure' if components['purity'] == 'P' else 'Contaminated'}
#                         - Folder: {folder}
#                     """)
#                     success_count += 1
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
#         - Example: 2314, 1441
#     3. **Date (YYYYMMDD):**
#         - Example: 20250518
#     4. **Position:**
#         - Right, Left, Center

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
#         "Manual Data Entry",  # New page added here
#         "Image Data Upload",
#         "Tanks Image Data Upload"
#     ])
#     if page == "Numerical Data Entry":
#         numerical_data_page()
#     elif page == "Manual Data Entry":
#         manual_data_entry_page()
#     elif page == "Image Data Upload":
#         image_data_page()
#     elif page == "Tanks Image Data Upload":
#         tanks_image_data_page()

# if __name__ == "__main__":
#     main()



# import streamlit as st
# from streamlit.logger import get_logger
# import pandas as pd
# import psycopg2
# from datetime import datetime
# import boto3
# import os
# import re
# import numpy as np

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
#     """Establishes a connection to the PostgreSQL database."""
#     conn = psycopg2.connect(
#         database="research",
#         user="alpro",
#         password="y13HLddTiOes36FWZoYY",
#         host="research.c2bcka4zvdxd.us-east-1.rds.amazonaws.com",
#         port="5423"
#     )
#     return conn

# def create_table(conn):
#     """Creates the research_data table if it doesn't exist."""
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
#     """Inserts numerical data into the research_data table."""
#     cursor = conn.cursor()
#     cursor.execute('''INSERT INTO research_data (datetime, dry_weight, ph)
#                       VALUES (%s, %s, %s);''', (datetime, dry_weight, ph))
#     conn.commit()
#     st.success("Data inserted successfully!")

# def fetch_data(conn):
#     """Fetches all data from the research_data table."""
#     cursor = conn.cursor()
#     cursor.execute('SELECT * FROM research_data;')
#     data = cursor.fetchall()
#     return data

# # --- Manual Data Entry Functions ---
# def create_manual_entry_table(conn):
#     """Creates the manual_data_entry table if it doesn't exist."""
#     cursor = conn.cursor()
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS manual_data_entry (
#             id SERIAL PRIMARY KEY,
#             timestamp TIMESTAMP NOT NULL,
#             ph FLOAT,
#             tds FLOAT,
#             do FLOAT,
#             concentration FLOAT,
#             light FLOAT
#         );
#     ''')
#     conn.commit()

# def insert_manual_data(conn, timestamp, ph, tds, do, concentration, light):
#     """Inserts data from the manual entry form into the database."""
#     cursor = conn.cursor()
#     query = '''
#         INSERT INTO manual_data_entry (timestamp, ph, tds, do, concentration, light)
#         VALUES (%s, %s, %s, %s, %s, %s);
#     '''
#     # Use None for np.nan values so psycopg2 converts them to NULL
#     data = (
#         timestamp,
#         ph if not pd.isna(ph) else None,
#         tds if not pd.isna(tds) else None,
#         do if not pd.isna(do) else None,
#         concentration if not pd.isna(concentration) else None,
#         light if not pd.isna(light) else None
#     )
#     cursor.execute(query, data)
#     conn.commit()

# def fetch_last_five_manual_entries(conn):
#     """Fetches the last 5 entries from the manual_data_entry table."""
#     cursor = conn.cursor()
#     cursor.execute('SELECT * FROM manual_data_entry ORDER BY timestamp DESC LIMIT 5;')
#     data = cursor.fetchall()
#     return data


# # --- Image Naming Convention Functions ---

# def validate_image_name(filename):
#     # Format: SPYYMMDD(C/T)N-YYMMDD-N-(P/C).<ext>
#     pattern = r'^(SP|WL)\d{6}[CT]\d{1,2}-\d{6}-\d{1,2}-[PC]\.[a-zA-Z]+$'
#     return bool(re.match(pattern, filename))

# def parse_image_name(filename):
#     # Format: SP250303C2-250401-1-P.jpg
#     name = os.path.splitext(filename)[0]
#     try:
#         first, second, image_counter, purity = name.split('-')
#         # first: SP250303C2 or WL250303T2   (strain+date+c/t+N)
#         strain = first[:2]
#         culture_date = first[2:8]
#         c_t = first[8]
#         culture_num = first[9:]
#         image_date = second
#         image_num = image_counter
#         return {
#             'strain': strain,
#             'culture_date': culture_date,
#             'c_t': c_t,
#             'culture_num': culture_num,
#             'image_date': image_date,
#             'image_num': image_num,
#             'purity': purity
#         }
#     except Exception as e:
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
#                 "Invalid filename format. Expected: SPYYMMDD(C/T)N-YYMMDD-N-(P/C).<ext>\n"
#                 "Example: SP250303C2-250401-1-P.jpg"
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

# # --- Tanks Image Functions (No update, as spec unchanged) ---
# def validate_tank_image_name(filename):
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

# def manual_data_entry_page():
#     """UI for the new manual data entry section."""
#     st.markdown("## Manual Data Entry")
#     st.markdown("📝 **For R&D Team:** Manually input sensor data.")

#     # --- Data Entry Form ---
#     st.markdown("### Enter Sensor Data 👇")
    
#     # Use two columns for a better layout
#     col1, col2 = st.columns(2)

#     with col1:
#         timestamp_date = st.date_input("Date", value=datetime.now().date())
#         timestamp_time = st.time_input("Time", value=datetime.now().time())
#         ph_input = st.number_input("Enter pH", value=None, format="%.2f")
#         tds_input = st.number_input("Enter TDS (ppm)", value=None, format="%.2f")

#     with col2:
#         do_input = st.number_input("Enter DO (mg/L)", value=None, format="%.2f")
#         concentration_input = st.number_input("Enter Concentration (g/L)", value=None, format="%.4f")
#         light_input = st.number_input("Enter Light (lux)", value=None, format="%.2f")

#     if st.button("Submit Manual Entry"):
#         # Combine date and time to create a datetime object
#         timestamp_input = datetime.combine(timestamp_date, timestamp_time)

#         # Collect all optional inputs
#         optional_inputs = [ph_input, tds_input, do_input, concentration_input, light_input]
        
#         # Check if at least one optional input has a value
#         if not any(v is not None for v in optional_inputs):
#             st.error("Please enter a value for at least one variable besides the timestamp.")
#         else:
#             try:
#                 conn = create_connection()
#                 create_manual_entry_table(conn)
                
#                 # Replace None with np.nan for database insertion
#                 ph_val = ph_input if ph_input is not None else np.nan
#                 tds_val = tds_input if tds_input is not None else np.nan
#                 do_val = do_input if do_input is not None else np.nan
#                 concentration_val = concentration_input if concentration_input is not None else np.nan
#                 light_val = light_input if light_input is not None else np.nan

#                 insert_manual_data(conn, timestamp_input, ph_val, tds_val, do_val, concentration_val, light_val)
#                 st.success("Data successfully added!")
#                 conn.close()
#             except Exception as e:
#                 st.error(f"An error occurred: {e}")

#     # --- Query Last 5 Entries ---
#     st.markdown("---")
#     if st.button("Query Last 5 Data Entries"):
#         try:
#             conn = create_connection()
#             data = fetch_last_five_manual_entries(conn)
#             conn.close()
#             if data:
#                 df = pd.DataFrame(data, columns=['ID', 'Timestamp', 'pH', 'TDS', 'DO', 'Concentration', 'Light'])
#                 st.dataframe(df)
#             else:
#                 st.info("No data found in the manual entry table.")
#         except Exception as e:
#             st.error(f"An error occurred while fetching data: {e}")


# def image_data_page():
#     st.markdown("## Image Data Upload")
#     st.markdown("""
#     📸 **For Image Analysis:**
#     Upload research-related images to S3 storage.

#     ### Naming Convention Guide:

#     **Format:** SPYYMMDD(C/T)N-YYMMDD-N-(P/C).<ext>

#     **First Block (Culture or Tank code):**
#     - SP: Spirulina
#     - WL: Water Lentils
#     - YYMMDD: Date of culture/tank start (not image date)
#     - C/T: C for Culture, T for Tank
#     - N: Culture or tank number (1 or 2 digits)

#     **Second Block (Image details):**
#     - YYMMDD: Date of image acquisition
#     - N: Image counter for that day (1 or 2 digits)

#     **Purity:**
#     - P: Pure
#     - C: Contaminated

#     **Examples:**
#     - SP250303C2-250401-1-P.jpg (Spirulina, culture 2 started on Mar 3, 2025, image 1 on Apr 1, 2025, Pure)
#     - SP250303T2-250401-1-C.jpg (Spirulina, **tank** 2 started Mar 3, 2025, image 1, Contaminated)
#     """)
#     st.markdown("### Upload Images 📸")
#     uploaded_files = st.file_uploader("Choose image files", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
#     if uploaded_files:
#         if st.button("Upload Images to S3"):
#             success_count = 0
#             for uploaded_file in uploaded_files:
#                 success, error_message = upload_to_s3(uploaded_file, uploaded_file.name)
#                 if success:
#                     folder = get_folder_path(uploaded_file.name)
#                     components = parse_image_name(uploaded_file.name)
#                     ctype = "Culture" if components['c_t'] == 'C' else "Tank"
#                     st.success(f"""
#                         Successfully uploaded image:
#                         - File: {uploaded_file.name}
#                         - Strain: {components['strain']}
#                         - {ctype} Number: {components['culture_num']}
#                         - {ctype} Date (YYMMDD): {components['culture_date']}
#                         - Image Date (YYMMDD): {components['image_date']}
#                         - Image #: {components['image_num']}
#                         - Purity: {'Pure' if components['purity'] == 'P' else 'Contaminated'}
#                         - Folder: {folder}
#                     """)
#                     success_count += 1
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
#         - Example: 2314, 1441
#     3. **Date (YYYYMMDD):**
#         - Example: 20250518
#     4. **Position:**
#         - Right, Left, Center

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
#         "Manual Data Entry",  # New page added here
#         "Image Data Upload",
#         "Tanks Image Data Upload"
#     ])
#     if page == "Numerical Data Entry":
#         numerical_data_page()
#     elif page == "Manual Data Entry":
#         manual_data_entry_page()
#     elif page == "Image Data Upload":
#         image_data_page()
#     elif page == "Tanks Image Data Upload":
#         tanks_image_data_page()

# if __name__ == "__main__":
#     main()



import streamlit as st
from streamlit.logger import get_logger
import pandas as pd
import psycopg2
from datetime import datetime
import boto3
import os
import re
import numpy as np

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
    """Establishes a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        database="research",
        user="alpro",
        password="y13HLddTiOes36FWZoYY",
        host="research.c2bcka4zvdxd.us-east-1.rds.amazonaws.com",
        port="5423"
    )
    return conn

def create_table(conn):
    """Creates the research_data table if it doesn't exist."""
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
    """Inserts numerical data into the research_data table."""
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO research_data (datetime, dry_weight, ph)
                      VALUES (%s, %s, %s);''', (datetime, dry_weight, ph))
    conn.commit()
    st.success("Data inserted successfully!")

def fetch_data(conn):
    """Fetches all data from the research_data table."""
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM research_data;')
    data = cursor.fetchall()
    return data

# --- Manual Data Entry Functions ---
def create_manual_entry_table(conn):
    """Creates the manual_data_entry table if it doesn't exist."""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS manual_data_entry (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            ph FLOAT,
            tds FLOAT,
            do FLOAT,
            concentration FLOAT,
            light FLOAT
        );
    ''')
    conn.commit()

def insert_manual_data(conn, timestamp, ph, tds, do, concentration, light):
    """Inserts data from the manual entry form into the database."""
    cursor = conn.cursor()
    query = '''
        INSERT INTO manual_data_entry (timestamp, ph, tds, do, concentration, light)
        VALUES (%s, %s, %s, %s, %s, %s);
    '''
    # Use None for np.nan values so psycopg2 converts them to NULL
    data = (
        timestamp,
        ph if not pd.isna(ph) else None,
        tds if not pd.isna(tds) else None,
        do if not pd.isna(do) else None,
        concentration if not pd.isna(concentration) else None,
        light if not pd.isna(light) else None
    )
    cursor.execute(query, data)
    conn.commit()

def fetch_last_five_manual_entries(conn):
    """Fetches the last 5 entries from the manual_data_entry table."""
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM manual_data_entry ORDER BY timestamp DESC LIMIT 5;')
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

def manual_data_entry_page():
    """UI for the new manual data entry section."""
    st.markdown("## Manual Data Entry")
    st.markdown("""
    📝 **For R&D Team:** This section is for manual data entry and serves two main purposes:

    1.  **Data Backup:** Use this form to manually log data if the automated sensor system fails or is offline. This ensures no data is lost during downtime.
    2.  **Comparative Analysis:** Enter manual readings to compare them with data captured by the automated sensors. This helps in validating sensor accuracy and system performance.
 
    **Instructions:** The **Timestamp** (Date and Time) is mandatory. You must enter a value for at least one other field. All other fields are optional. Leave a field as `0.0`to save it as N/A (Not Available).
    """)
    # --- Data Entry Form ---
    st.markdown("### Enter Sensor Data 👇")
    
    # Use two columns for a better layout
    col1, col2 = st.columns(2)

    with col1:
        timestamp_date = st.date_input("Date", value=datetime.now().date())
        timestamp_time = st.time_input("Time", value=datetime.now().time())
        ph_input = st.number_input("Enter pH", value=0.0, format="%.2f")
        tds_input = st.number_input("Enter TDS (ppm)", value=0.0, format="%.2f")

    with col2:
        do_input = st.number_input("Enter DO (mg/L)", value=0.0, format="%.2f")
        concentration_input = st.number_input("Enter Concentration (g/L)", value=0.0, format="%.4f")
        light_input = st.number_input("Enter Light (lux)", value=0.0, format="%.2f")

    if st.button("Submit Manual Entry"):
        # Combine date and time to create a datetime object
        timestamp_input = datetime.combine(timestamp_date, timestamp_time)

        # Collect all optional inputs
        optional_inputs = [ph_input, tds_input, do_input, concentration_input, light_input]
        
        # Check if at least one optional input has a non-zero value
        if not any(v != 0.0 for v in optional_inputs):
            st.error("Please enter a value for at least one variable (a value other than 0.0).")
        else:
            try:
                conn = create_connection()
                create_manual_entry_table(conn)
                
                # Replace 0.0 with np.nan for database insertion
                ph_val = ph_input if ph_input != 0.0 else np.nan
                tds_val = tds_input if tds_input != 0.0 else np.nan
                do_val = do_input if do_input != 0.0 else np.nan
                concentration_val = concentration_input if concentration_input != 0.0 else np.nan
                light_val = light_input if light_input != 0.0 else np.nan

                insert_manual_data(conn, timestamp_input, ph_val, tds_val, do_val, concentration_val, light_val)
                st.success("Data successfully added!")
                conn.close()
            except Exception as e:
                st.error(f"An error occurred: {e}")

    # --- Query Last 5 Entries ---
    st.markdown("---")
    if st.button("Query Last 5 Data Entries"):
        try:
            conn = create_connection()
            data = fetch_last_five_manual_entries(conn)
            conn.close()
            if data:
                df = pd.DataFrame(data, columns=['ID', 'Timestamp', 'pH', 'TDS', 'DO', 'Concentration', 'Light'])
                st.dataframe(df)
            else:
                st.info("No data found in the manual entry table.")
        except Exception as e:
            st.error(f"An error occurred while fetching data: {e}")


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
        "Manual Data Entry",  # New page added here
        "Image Data Upload",
        "Tanks Image Data Upload"
    ])
    if page == "Numerical Data Entry":
        numerical_data_page()
    elif page == "Manual Data Entry":
        manual_data_entry_page()
    elif page == "Image Data Upload":
        image_data_page()
    elif page == "Tanks Image Data Upload":
        tanks_image_data_page()

if __name__ == "__main__":
    main()
