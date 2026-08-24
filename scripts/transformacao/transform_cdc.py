import pandas as pd
import s3fs
import sys
import os
from datetime import datetime

# Importa as configurações centralizadas
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from config.settings import (
    MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET
)

# --- 1. Conectar no MinIO ---
fs = s3fs.S3FileSystem(
    key=MINIO_ACCESS_KEY,
    secret=MINIO_SECRET_KEY,
    client_kwargs={"endpoint_url": MINIO_ENDPOINT}
)
print("✓ Conectado ao MinIO.")

# --- 2. Ler todos os Parquets da pasta cdc_vendas ---
caminho_cru = f"{MINIO_BUCKET}/cdc_vendas/"

try:
    arquivos = fs.ls(caminho_cru)
    parquets = [a for a in arquivos if a.endswith(".parquet")]
    print(f"✓ {len(parquets)} arquivo(s) encontrado(s) em {caminho_cru}")
except FileNotFoundError:
    print(f"✗ Pasta {caminho_cru} não encontrada. Rode o cdc_to_minio.py primeiro.")
    exit()

if not parquets:
    print("✗ Nenhum arquivo Parquet encontrado.")
    exit()

# Lê e concatena todos os Parquets numa tabela só
dfs = []
for arquivo in parquets:
    with fs.open(arquivo, "rb") as f:
        dfs.append(pd.read_parquet(f, engine="pyarrow"))

df_cru = pd.concat(dfs, ignore_index=True)
print(f"✓ Total de {len(df_cru)} linha(s) carregada(s).")
print(f"\nDados crus:")
print(df_cru)

# --- 3. Transformação ---

# 3.1 Mapear o código de operação pra texto legível
# 1=DELETE, 2=INSERT, 3=UPDATE (antes), 4=UPDATE (depois)
mapa_operacao = {1: "DELETE", 2: "INSERT", 3: "UPDATE_ANTES", 4: "UPDATE_DEPOIS"}
df_cru["operacao"] = df_cru["__$operation"].map(mapa_operacao)

# 3.2 Remover colunas internas do CDC
colunas_cdc = ["__$start_lsn", "__$seqval", "__$operation", "__$update_mask"]
df_limpo = df_cru.drop(columns=colunas_cdc)

# 3.3 Manter só os estados finais:
# - INSERTs (operacao=2): linha nova
# - UPDATE_DEPOIS (operacao=4): versão mais recente após update
# - Ignorar DELETE_ANTES (3) e registrar DELETEs (1) separadamente
df_atual = df_limpo[df_limpo["operacao"].isin(["INSERT", "UPDATE_DEPOIS"])].copy()
df_deletados = df_limpo[df_limpo["operacao"] == "DELETE"].copy()

# 3.4 Consolidar: pegar a versão mais recente de cada id
# (em caso de múltiplas mudanças no mesmo id, fica a última)
df_consolidado = df_atual.drop_duplicates(subset=["id"], keep="last").reset_index(drop=True)

# 3.5 Adicionar coluna de quando foi processado
df_consolidado["processado_em"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print(f"\nDados transformados ({len(df_consolidado)} linha(s)):")
print(df_consolidado)

if not df_deletados.empty:
    print(f"\nRegistros deletados ({len(df_deletados)} linha(s)):")
    print(df_deletados[["id", "produto", "operacao"]])

# --- 4. Gravar o resultado tratado no MinIO ---
caminho_tratado = f"{MINIO_BUCKET}/vendas_tratado/"

# Garante que a pasta existe
try:
    fs.ls(caminho_tratado)
except FileNotFoundError:
    fs.makedirs(caminho_tratado, exist_ok=True)
    print(f"\n✓ Pasta {caminho_tratado} criada.")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
caminho_saida = f"{caminho_tratado}vendas_tratado_{timestamp}.parquet"

with fs.open(caminho_saida, "wb") as f:
    df_consolidado.to_parquet(f, engine="pyarrow", index=False)

print(f"\n✓ Dados tratados gravados em: s3://{caminho_saida}")
print(f"✓ Transformação concluída com sucesso!")