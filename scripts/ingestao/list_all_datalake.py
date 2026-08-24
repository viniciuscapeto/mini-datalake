import s3fs

fs = s3fs.S3FileSystem(
    key="admin",
    secret="admin12345",
    client_kwargs={"endpoint_url": "http://localhost:9000"}
)

print("Tudo dentro de datalake/:")
try:
    files = fs.ls("datalake/")
    if files:
        for f in files:
            print(f" - {f}")
    else:
        print("  (vazio)")
except Exception as e:
    print(f"Erro: {e}")