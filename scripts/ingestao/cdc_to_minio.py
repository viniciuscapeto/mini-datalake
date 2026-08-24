import pandas as pd
import pyodbc
import s3fs
from datetime import datetime

# --- 1. Conectar no SQL Server ---
conn_str = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=MiniDataLakeDB;"
    "Trusted_Connection=yes;"   # autenticação Windows
    "TrustServerCertificate=yes;"  # evita erro de certificado SSL em ambiente local
)

conn = pyodbc.connect(conn_str)
print("Conectado ao SQL Server com sucesso.")

# --- 2. Ler as mudanças capturadas pelo CDC ---
# cdc.fn_cdc_get_all_changes_dbo_vendas é criada automaticamente pelo sp_cdc_enable_table
# Precisamos do LSN (Log Sequence Number) mínimo e máximo disponíveis
query_lsn = """
SELECT sys.fn_cdc_get_min_lsn('dbo_vendas') AS min_lsn,
       sys.fn_cdc_get_max_lsn() AS max_lsn
"""
lsn_df = pd.read_sql(query_lsn, conn)
min_lsn = lsn_df.loc[0, "min_lsn"]
max_lsn = lsn_df.loc[0, "max_lsn"]

if min_lsn is None:
    print("Nenhuma mudança capturada ainda pelo CDC.")
    conn.close()
    exit()

# --- 3. Buscar as mudanças no intervalo de LSN ---
query_changes = f"""
SELECT * FROM cdc.fn_cdc_get_all_changes_dbo_vendas(
    0x{min_lsn.hex()}, 0x{max_lsn.hex()}, 'all'
)
"""
changes_df = pd.read_sql(query_changes, conn)
conn.close()

print(f"\n{len(changes_df)} mudança(s) capturada(s):")
print(changes_df)

if changes_df.empty:
    print("Nada para gravar.")
    exit()

# --- 4. Gravar no MinIO como Parquet (particionado por data de execução) ---
fs = s3fs.S3FileSystem(
    key="admin",
    secret="admin12345",
    client_kwargs={"endpoint_url": "http://localhost:9000"}
)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
caminho = f"datalake/cdc_vendas/vendas_changes_{timestamp}.parquet"

with fs.open(caminho, "wb") as f:
    changes_df.to_parquet(f, engine="pyarrow", index=False)

print(f"\nMudanças gravadas em: s3://{caminho}")