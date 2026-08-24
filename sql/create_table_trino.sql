-- 1. Criar o schema (equivalente a um "banco" dentro do catálogo hive)
CREATE SCHEMA IF NOT EXISTS hive.vendas
WITH (location = 's3://datalake/vendas/');

-- 2. Criar a tabela externa apontando pro Parquet que o Python gravou
CREATE TABLE IF NOT EXISTS hive.vendas.vendas (
    id INTEGER,
    produto VARCHAR,
    preco DOUBLE,
    quantidade INTEGER
)
WITH (
    external_location = 's3://datalake/vendas/',
    format = 'PARQUET'
);

-- 3. Testar a consulta
SELECT * FROM hive.vendas.vendas;
