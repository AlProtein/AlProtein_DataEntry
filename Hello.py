# import streamlit as st
# from streamlit.logger import get_logger
# import pandas as pd
# import psycopg2
# from datetime import datetime


# LOGGER = get_logger(__name__)



# # Function to connect to AWS RDS database
# def create_connection():
#     conn = psycopg2.connect(
#         database="concentration",
#         user="alpro",
#         password="l33hJC7Ys2n4zr6u63zo",
#         host="dataacquisition.cc4idrhev5xz.eu-north-1.rds.amazonaws.com",
#         port="5432")
#     return conn

# # Create table if not exists
# def create_table(conn):
#     cursor = conn.cursor()
#     cursor.execute('''CREATE TABLE IF NOT EXISTS research_data
#                     (id SERIAL PRIMARY KEY,
#                      datetime TIMESTAMP,
#                      dry_weight FLOAT);''')
#     conn.commit()

# # Function to insert data into database
# def insert_data(conn, datetime, dry_weight):
#     cursor = conn.cursor()
#     cursor.execute('''INSERT INTO research_data (datetime, dry_weight)
#                       VALUES (%s, %s);''', (datetime, dry_weight))
#     conn.commit()
#     st.success("Data inserted successfully!")

# # Main function
# def main():
#     # Set page layout
#     st.set_page_config(page_title="Research Data Entry", page_icon=":bar_chart:")

#     # Upload and display company logo at the header
#     st.image("public-logo.png", width=150)
#     # README section with centralized title
#     st.markdown("""
#     <div style="text-align: center;">
#         <h1 style="margin-bottom: 0; color: green;">AlProtein Data Entry 👨🏻‍💻</h1>
#         <hr style="margin-top: 0;">
#     """, unsafe_allow_html=True)


#     # README section
#     st.markdown("""
#     🚀 Welcome to the Research Data Entry App! 🚀

#     This app is your go-to tool for empowering both the R&D and AI teams. Here's how:

#     🔍 **For R&D Team:**
#     Easily enter and manage research data in a structured format. The app securely stores this valuable information in an AWS RDS database, ensuring data integrity and accessibility. Remember to use the datetime format (YYYY/MM/DD HH:mm:ss:) when inputting data.

#     🤖 **For AI Team:**
#     Harness the power of labeled sensor data! With this app, you can effortlessly label sensor data with precise timestamps and dry weight values. These labeled data points are the building blocks for enhancing the AIPredict model, enabling accurate predictions of dry weight based on sensor data.

#     🚀 Ready to get started? Simply enter the required data below and hit the "Submit" button to supercharge your research and AI initiatives!
#     """)



#     # Get current year and month
#     current_year = datetime.now().year
#     current_month = datetime.now().month

#     # Default datetime to current year and month
#     default_datetime = f"{current_year}-{current_month:02}-01 00:00:00"

#     # Input fields for datetime and dry weight
#     st.markdown("### Enter Research Data 👇")
#     datetime_input = st.text_input("Enter Datetime ⏰⏰:", default_datetime)
#     dry_weight_input = st.number_input("Enter Dry Weight ⚖️⚖️:", min_value=0.0)

#     # Button to submit data
#     if st.button("Submit"):
#         try:
#             # Add default seconds if not specified
#             if len(datetime_input) == 16:
#                 datetime_input += ":00"

#             # Validate datetime format
#             pd.to_datetime(datetime_input, format='%Y-%m-%d %H:%M:%S')
#         except ValueError:
#             st.error("Please enter datetime in the format YYYY-MM-DD HH:MM")
#             return

#         # Insert data into database
#         conn = create_connection()
#         create_table(conn)
#         insert_data(conn, datetime_input, dry_weight_input)
#         conn.close()

# # Run the app
# if __name__ == "__main__":
#     main()




# Hello.py
import streamlit as st
from streamlit.logger import get_logger
import pandas as pd
import psycopg2
from datetime import datetime

LOGGER = get_logger(__name__)

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
    Upload and manage research-related images with associated metadata.
    """)

    # Image upload section
    st.markdown("### Upload Images 📸")
    uploaded_files = st.file_uploader("Choose image files", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

    # Image metadata section
    if uploaded_files:
        st.markdown("### Image Metadata")
        for uploaded_file in uploaded_files:
            st.write(f"Processing: {uploaded_file.name}")

            col1, col2 = st.columns(2)

            with col1:
                st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)

            with col2:
                sample_id = st.text_input(f"Sample ID for {uploaded_file.name}", key=f"sample_id_{uploaded_file.name}")
                capture_date = st.date_input(f"Capture Date for {uploaded_file.name}", key=f"date_{uploaded_file.name}")
                notes = st.text_area(f"Notes for {uploaded_file.name}", key=f"notes_{uploaded_file.name}")

                if st.button(f"Save metadata for {uploaded_file.name}", key=f"save_{uploaded_file.name}"):
                    st.success(f"Metadata for {uploaded_file.name} saved successfully!")

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