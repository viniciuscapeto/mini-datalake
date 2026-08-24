import pandas as pd
import pyodbc
import s3fs
from datetime import datetime

# --- 1. Conectar no SQL Server ---
conn_str = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=MiniDataLakeDB;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

try:
    conn = pyodbc.connect(conn_str)
    print("✓ Conectado ao SQL Server com sucesso.")
except Exception as e:
    print(f"✗ Erro ao conectar no SQL Server: {e}")
    exit()

# --- 2. Ler os LSNs ---
try:
    query_lsn = """
    SELECT sys.fn_cdc_get_min_lsn('dbo_vendas') AS min_lsn,
           sys.fn_cdc_get_max_lsn() AS max_lsn
    """
    lsn_df = pd.read_sql(query_lsn, conn)
    min_lsn = lsn_df.loc[0, "min_lsn"]
    max_lsn = lsn_df.loc[0, "max_lsn"]
    print(f"✓ LSNs obtidos - min: {min_lsn}, max: {max_lsn}")
except Exception as e:
    print(f"✗ Erro ao ler LSNs: {e}")
    conn.close()
    exit()

if min_lsn is None or max_lsn is None:
    print("✗ LSNs são NULL - nenhuma mudança capturada.")
    conn.close()
    exit()

# --- 3. Buscar as mudanças ---
try:
    query_changes = f"""
    SELECT * FROM cdc.fn_cdc_get_all_changes_dbo_vendas(
        0x{min_lsn.hex()}, 0x{max_lsn.hex()}, 'all'
    )
    """
    print(f"✓ Query executada no SQL Server")
    changes_df = pd.read_sql(query_changes, conn)
    print(f"✓ DataFrame criado com {len(changes_df)} mudança(s)")
    print(f"✓ Colunas: {list(changes_df.columns)}")
except Exception as e:
    print(f"✗ Erro ao ler mudanças: {e}")
    conn.close()
    exit()

conn.close()

if changes_df.empty:
    print("✗ DataFrame vazio - nada para gravar.")
    exit()

print(f"\nDados a gravar:")
print(changes_df)

# --- 4. Conectar no MinIO ---
try:
    fs = s3fs.S3FileSystem(
        key="admin",
        secret="admin12345",
        client_kwargs={"endpoint_url": "http://localhost:9000"}
    )
    print("✓ Conectado ao MinIO com sucesso.")
except Exception as e:
    print(f"✗ Erro ao conectar no MinIO: {e}")
    exit()

# --- 5. Criar a pasta se não existir ---
try:
    # Verifica se a pasta existe
    try:
        fs.ls("datalake/cdc_vendas/")
        print("✓ Pasta datalake/cdc_vendas/ já existe")
    except:
        # Se não existir, tenta criar
        fs.makedirs("datalake/cdc_vendas/", exist_ok=True)
        print("✓ Pasta datalake/cdc_vendas/ criada")
except Exception as e:
    print(f"✗ Erro ao criar pasta: {e}")
    exit()

# --- 6. Gravar no MinIO ---
try:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho = f"datalake/cdc_vendas/vendas_changes_{timestamp}.parquet"
    
    print(f"→ Gravando em: {caminho}")
    with fs.open(caminho, "wb") as f:
        changes_df.to_parquet(f, engine="pyarrow", index=False)
    print(f"✓ Arquivo gravado com sucesso!")
    
    # Conferir que o arquivo está lá
    files = fs.ls("datalake/cdc_vendas/")
    print(f"✓ Arquivos na pasta agora: {files}")
except Exception as e:
    print(f"✗ Erro ao gravar: {e}")
    import traceback
    traceback.print_exc()
    exit()