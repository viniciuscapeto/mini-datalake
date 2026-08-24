from dotenv import load_dotenv
import os

# Carrega o .env da raiz do projeto
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# MinIO
MINIO_ENDPOINT   = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET     = os.getenv("MINIO_BUCKET")

# SQL Server
SQL_SERVER   = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_DRIVER   = os.getenv("SQL_DRIVER")

# String de conexão pronta pra usar com pyodbc
SQL_CONN_STR = (
    f"DRIVER={{{SQL_DRIVER}}};"
    f"SERVER={SQL_SERVER};"
    f"DATABASE={SQL_DATABASE};"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)