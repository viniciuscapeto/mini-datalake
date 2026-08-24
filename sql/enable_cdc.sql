USE MiniDataLakeDB;
GO

-- 1. Habilitar CDC no nível do banco de dados
EXEC sys.sp_cdc_enable_db;
GO

-- 2. Conferir se o CDC foi habilitado no banco
SELECT name, is_cdc_enabled FROM sys.databases WHERE name = 'MiniDataLakeDB';
GO

-- 3. Habilitar CDC na tabela vendas
EXEC sys.sp_cdc_enable_table
    @source_schema = N'dbo',
    @source_name   = N'vendas',
    @role_name     = NULL,
    @supports_net_changes = 1;
GO

-- 4. Conferir se a tabela está sendo capturada
SELECT name, is_tracked_by_cdc FROM sys.tables WHERE name = 'vendas';
GO
