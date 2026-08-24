-- 1. Criar o banco de teste
CREATE DATABASE MiniDataLakeDB;
GO

USE MiniDataLakeDB;
GO

-- 2. Criar a tabela fictícia de vendas
CREATE TABLE vendas (
    id INT IDENTITY(1,1) PRIMARY KEY,
    produto VARCHAR(100) NOT NULL,
    preco DECIMAL(10,2) NOT NULL,
    quantidade INT NOT NULL,
    data_venda DATETIME DEFAULT GETDATE()
);
GO

-- 3. Inserir dados fictícios
INSERT INTO vendas (produto, preco, quantidade) VALUES
('Notebook', 3500.00, 10),
('Mouse', 89.90, 50),
('Teclado', 199.90, 30),
('Monitor', 1200.00, 15),
('Headset', 350.00, 20);
GO

-- 4. Conferir os dados
SELECT * FROM vendas;
GO
