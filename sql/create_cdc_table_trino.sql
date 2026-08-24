-- 1. Criar o schema cdc
CREATE SCHEMA IF NOT EXISTS hive.cdc
WITH (location = 's3://datalake/cdc_vendas/');

-- 2. Criar a tabela externa apontando aos arquivos Parquet do CDC
-- Obs: colunas com $ precisam de aspas duplas no Trino
CREATE TABLE IF NOT EXISTS hive.cdc.vendas_changes (
    "__$start_lsn"    VARBINARY,
    "__$seqval"       VARBINARY,
    "__$operation"    INTEGER,
    "__$update_mask"  VARBINARY,
    id                INTEGER,
    produto           VARCHAR,
    preco             DOUBLE,
    quantidade        INTEGER,
    data_venda        TIMESTAMP
)
WITH (
    external_location = 's3://datalake/cdc_vendas/',
    format = 'PARQUET'
);

-- 3. Testar a consulta
SELECT * FROM hive.cdc.vendas_changes;

-- 4. Ver só as colunas relevantes com o tipo de operação legível
SELECT
    id,
    produto,
    preco,
    quantidade,
    data_venda,
    "__$operation" AS operacao  -- 1=DELETE, 2=INSERT, 3=UPDATE antes, 4=UPDATE depois
FROM hive.cdc.vendas_changes
ORDER BY "__$start_lsn";
