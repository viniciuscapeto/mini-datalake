import s3fs

fs = s3fs.S3FileSystem(
    key="admin",
    secret="admin12345",
    client_kwargs={"endpoint_url": "http://localhost:9000"}
)

print("Arquivos em datalake/cdc_vendas/:")
files = fs.ls("datalake/cdc_vendas/")
for f in files:
    print(f" - {f}")
