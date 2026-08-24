import pandas as pd
import s3fs

# --- 1. Gerar dado fake ---
df = pd.DataFrame({
    "id": [1, 2, 3, 4, 5],
    "produto": ["Notebook", "Mouse", "Teclado", "Monitor", "Headset"],
    "preco": [3500.00, 89.90, 199.90, 1200.00, 350.00],
    "quantidade": [10, 50, 30, 15, 20]
})

print("Dado gerado:")
print(df)

# --- 2. Conectar no MinIO via s3fs ---
fs = s3fs.S3FileSystem(
    key="admin",
    secret="admin12345",
    client_kwargs={"endpoint_url": "http://localhost:9000"}
)

# --- 3. Gravar como Parquet dentro do bucket ---
caminho = "datalake/vendas/vendas.parquet"

with fs.open(caminho, "wb") as f:
    df.to_parquet(f, engine="pyarrow", index=False)

print(f"\nArquivo gravado com sucesso em: s3://{caminho}")

# --- 4. Conferir que o arquivo está lá ---
print("\nArquivos no bucket datalake/vendas/:")
print(fs.ls("datalake/vendas/"))