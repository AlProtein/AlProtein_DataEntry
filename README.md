# AlProtein Data Entry Platform

![AlProtein Logo](public-logo.png)

## 🚀 Overview

**AlProtein Data Entry** is a Streamlit-based web application designed for the AlProtein research and R&D teams to streamline the entry, management, and upload of experimental data and images. The platform supports both numerical data and image uploads (microscope and tank photos), leveraging AWS S3 for secure image storage and PostgreSQL for structured research data.

---

## 🌟 Features

- **Numerical Data Entry**
  - Input experimental results, including datetime, dry weight, and pH.
  - Data validation for date/time and pH ranges.
  - View and export all submitted research data.

- **Image Data Upload**
  - Upload microscope images with enforced naming conventions for quality assurance.
  - Images are organized and stored in AWS S3 under the correct research folder.
  - Naming conventions ensure traceability of strain, culture, date, and purity.

- **Tank Image Data Upload**
  - Upload tank monitoring images with dedicated naming conventions (including position: Right, Left, Center).
  - Images are stored in a separate S3 bucket for tank images.

- **Secure Cloud Storage**
  - All images are uploaded directly to AWS S3 buckets.
  - Database connectivity for structured numerical data.

- **Simple, Friendly UI**
  - Modern, responsive Streamlit interface.
  - Sidebar navigation between all core features.

---

## 📂 Directory Structure

```
.
├── Hello.py             # Main Streamlit app
├── public-logo.png      # Project logo
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

---

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/AlProtein/AlProtein_DataEntry.git
cd AlProtein_DataEntry
```

### 2. Install Dependencies

We recommend using a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment

> **Note:** Sensitive credentials (database and AWS keys) are currently hardcoded for demo but should be moved to environment variables or a secret manager in production.

- **Database:** PostgreSQL credentials are required.
- **AWS S3:** Access and secret keys for image uploads.

### 4. Run the Application

```bash
streamlit run Hello.py
```

---

## 📝 Usage Guide

### 1. **Numerical Data Entry**

- Navigate to **Numerical Data Entry** in the sidebar.
- Enter your research data (datetime, dry weight, pH).
- Click **Submit** to save to the database.
- Click **View Data** to see all entries.

### 2. **Image Data Upload**

- Go to **Image Data Upload**.
- Review the naming convention:
  ```
  STRAIN-CULTURENUMBER-DATE-PURITY.jpg
  Example: SP-2314-20250327-P
  ```
  - **STRAIN:** `SP` (Spirulina) or `WL` (Water Lentils)
  - **CULTURENUMBER:** 4 digits (e.g., 2314)
  - **DATE:** YYYYMMDD (e.g., 20250327)
  - **PURITY:** `P` (Pure) or `C` (Contaminated)
- Upload images and click **Upload Images to S3**.

### 3. **Tanks Image Data Upload**

- Go to **Tanks Image Data Upload**.
- Naming convention for tank images:
  ```
  STRAIN-CULTURENUMBER-YYYYMMDD-POSITION.jpg
  Example: SP-2314-20250518-Right.jpg
  ```
  - **POSITION:** Right, Left, Center
- Upload images and click **Upload Tank Images to S3**.

---

## 🧑‍💻 Technologies Used

- [Streamlit](https://streamlit.io/) – UI framework
- [PostgreSQL](https://www.postgresql.org/) – Research data storage
- [AWS S3](https://aws.amazon.com/s3/) – Image storage
- [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) – AWS Python SDK
- [pandas](https://pandas.pydata.org/) – Data manipulation

---

## 🔒 Security Notice

- **Credentials are currently hardcoded** in the code for demonstration. 
- **Do NOT use this in production** without moving all secrets to secure environment variables or a secrets manager.
- Ensure your AWS and database credentials are protected.

---

## 🏗️ Project Status & Contribution

This project is under active development. Contributions, issues, and suggestions are welcome! Please open an issue or submit a pull request.

---

## 📄 License

This project is proprietary to AlProtein. Contact the maintainers for licensing details.

---

## 📬 Contact

For support or inquiries, contact the AlProtein R&D team.

---

## 🤝 Acknowledgments

Special thanks to all contributors and the AlProtein R&D team for their efforts in developing and maintaining this platform.
