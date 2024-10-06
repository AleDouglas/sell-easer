'''

Arquivo para configuração do banco de dados
Recerá as informações de conexão com o banco de dados e fará a conexão
com o banco de dados.
Além disso, será responsável por criar as tabelas necessárias, fazer consultas, updates e deletes.


'''


import sqlite3
import pandas as pd
import random


class DatabaseManager:

    # Método construtor da classe
    def __init__(self, db_name="sales_system.db"):
        # Conecta ao banco de dados (cria se não existir)
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    # Método para criar as tabelas no banco de dados
    def create_tables(self):
        # Cria a tabela Customer, se não existir
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Customer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                cpf TEXT,
                email TEXT,
                phone TEXT
            )
        ''')
        # Printando que código da tabela Customer user foi executando com sucesso com um 'Ok' verde no final
        print("Database progress.....\033[92mOk\033[0m")
        
        # Cria a tabela Product, se não existir
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Product (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                code TEXT UNIQUE NOT NULL,
                description TEXT,
                purchase_price REAL NOT NULL,
                sale_price REAL NOT NULL,
                stock INTEGER DEFAULT 0
            )
        ''')
        print("Database progress.....\033[92mOk\033[0m")
        # Cria a tabela Sales, se não existir
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                total_value REAL NOT NULL,
                profit REAL DEFAULT 0.0,
                installment INTEGER DEFAULT 1,
                payment INTEGER DEFAULT 1,
                tax REAL DEFAULT 0.0,
                sale_date TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES Customer(id)
            )
        ''')
        print("Database progress.....\033[92mOk\033[0m")
        # Cria a tabela SalesProduct, se não existir - relaciona Sales com Product
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS SalesProduct (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER,
                product_id INTEGER,
                quantity INTEGER NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES Sales(id),
                FOREIGN KEY (product_id) REFERENCES Product(id)
            )
        ''')
        print("Database progress.....\033[92mOk\033[0m")
        # Salva as alterações no banco de dados
        self.connection.commit()
        print("Commit progress.....\033[92mOk\033[0m")

    # Método para consultar todos os registros de uma tabela e retornar como DataFrame
    def fetch_all(self, table_name):
        """
        Consulta todos os registros da tabela especificada.
        
        Args:
            table_name (str): Nome da tabela a ser consultada.
        
        Returns:
            DataFrame: Resultados da consulta em formato de DataFrame.
        """
        query = f"SELECT * FROM {table_name}"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        # Converte o resultado para DataFrame usando pandas
        columns = [column[0] for column in self.cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        return df

    # Método para consultar um registro específico pelo ID e retornar como DataFrame
    def fetch_by_id(self, table_name, record_id, column_name='id'):
        """
        Consulta um registro específico por ID na tabela especificada.
        
        Args:
            table_name (str): Nome da tabela a ser consultada.
            record_id (int): ID do registro a ser consultado.
            column_name (str, opcional): Nome da coluna de ID (padrão: 'id').
        
        Returns:
            DataFrame: Registro específico em formato de DataFrame.
        """
        query = f"SELECT * FROM {table_name} WHERE {column_name} = ?"
        self.cursor.execute(query, (record_id,))
        row = self.cursor.fetchone()
        # Converte o resultado para DataFrame usando pandas
        columns = [column[0] for column in self.cursor.description]
        df = pd.DataFrame([row], columns=columns) if row else pd.DataFrame(columns=columns)
        
        
        return df

    # Método para consultar registros específicos em uma tabela filtrando pelo valor da coluna
    def filter_by_column(self, table_name, column_name, value):
        """
        Consulta registros específicos em uma tabela filtrando pelo valor da coluna.
        
        Args:
            table_name (str): Nome da tabela a ser consultada.
            column_name (str): Nome da coluna a ser filtrada.
            value (str): Valor a ser filtrado.
        
        Returns:
            DataFrame: Registros filtrados em formato de DataFrame.
        """
        # Ajuste para usar LIKE para busca de strings que contenham o valor
        query = f"SELECT * FROM {table_name} WHERE {column_name} LIKE ?"
        self.cursor.execute(query, (f"%{value}%",))  # Uso de LIKE para encontrar todas as correspondências
        rows = self.cursor.fetchall()  # Busca todas as linhas que correspondem ao critério
        
        # Converte o resultado para DataFrame usando pandas
        columns = [column[0] for column in self.cursor.description]
        df = pd.DataFrame(rows, columns=columns) if rows else pd.DataFrame(columns=columns)
        return df

    # Método para inserir um novo cliente na tabela Customer
    def insert_customer(self, name, cpf, email, phone):
        """
        Insere um novo cliente na tabela Customer.
        
        Args:
            name (str): Nome do cliente.
            cpf (str): CPF do cliente.
            email (str): E-mail do cliente.
            phone (str): Telefone do cliente.
        """
        query = '''
            INSERT INTO Customer (name, cpf, email, phone)
            VALUES (?, ?, ?, ?)
        '''
        self.cursor.execute(query, (name, cpf, email, phone))
        self.connection.commit()

    # Método para inserir um novo produto na tabela Product
    def insert_product(self, name, description, code, purchase_price, sale_price, stock=0):
        """
        Insere um novo produto na tabela Product.
        
        Args:
            name (str): Nome do produto.
            description (str): Descrição do produto.
            code (str): Código do produto.
            purchase_price (float): Valor de compra do produto.
            sale_price (float): Valor de venda do produto.
            stock (int): Estoque do produto.
        """
        query = '''
            INSERT INTO Product (name, description, code, purchase_price, sale_price, stock)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        self.cursor.execute(query, (name, description, code, purchase_price, sale_price, stock))
        self.connection.commit()

    # Método para inserir uma nova venda na tabela Sales
    def insert_sale(self, customer_id, total_value, profit,sale_date, installment=1, payment=1, tax=0.0):
        """
        Insere uma nova venda na tabela Sales.
        
        Args:
            customer_id (int): ID do cliente que realizou a compra.
            total_value (float): Valor total da venda.
            profit (float): Lucro da venda.
            installment (int): Número de parcelas da compra.
            payment (int): Forma de pagamento da compra.
            tax (float): Taxa de juros da compra.
            sale_date (str): Data da venda (formato: 'YYYY-MM-DD').
        
        Returns:
            int: ID da venda inserida, para ser usada na tabela SalesProduct.
        """
        query = '''
            INSERT INTO Sales (customer_id, total_value, profit, sale_date, installment, payment, tax)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        
        if installment < 1:
            installment = 1
        
        self.cursor.execute(query, (customer_id, total_value, profit, sale_date, installment, payment, tax))
        self.connection.commit()
        return self.cursor.lastrowid  # Retorna o ID da venda inserida

    # Método para inserir produtos vendidos na tabela SalesProduct
    def insert_sales_product(self, sale_id, product_id, quantity):
        """
        Insere os produtos vendidos na tabela SalesProduct.
        
        Args:
            sale_id (int): ID da venda (referente à tabela Sales).
            product_id (int): ID do produto vendido (referente à tabela Product).
            quantity (int): Quantidade do produto vendido.
        """
        query = '''
            INSERT INTO SalesProduct (sale_id, product_id, quantity)
            VALUES (?, ?, ?)
        '''
        
        try:
            product_id = int(product_id)
        except ValueError:
            print("ID do produto deve ser um número inteiro.")
            return
        
        self.cursor.execute(query, (sale_id, product_id, quantity))
        self.connection.commit()
    
    # Método para editar um cliente na tabela Customer
    def update_customer(self, customer_id, name=None, cpf=None, email=None, phone=None):
        """
        Edita um cliente existente na tabela Customer.
        
        Args:
            customer_id (int): ID do cliente a ser editado.
            name (str, opcional): Novo nome do cliente.
            cpf (str, opcional): Novo CPF do cliente.
            email (str, opcional): Novo e-mail do cliente.
            phone (str, opcional): Novo telefone do cliente.
        """
        query = '''
            UPDATE Customer
            SET name = COALESCE(?, name),
                cpf = COALESCE(?, cpf),
                email = COALESCE(?, email),
                phone = COALESCE(?, phone)
            WHERE id = ?
        '''
        self.cursor.execute(query, (name, cpf, email, phone, customer_id))
        self.connection.commit()

    # Método para editar um produto na tabela Product
    def update_product(self, product_id, name=None, description=None, code=None, purchase_price=None, sale_price=None, stock=None):
        """
        Edita um produto existente na tabela Product.
        
        Args:
            product_id (int): ID do produto a ser editado.
            name (str, opcional): Novo nome do produto.
            description (str, opcional): Nova descrição do produto.
            code (str, opcional): Novo código do produto.
            purchase_price (float, opcional): Novo valor de compra do produto.
            sale_price (float, opcional): Novo valor de venda do produto.
            stock (int, opcional): Novo estoque do produto.
        """
        query = '''
            UPDATE Product
            SET name = COALESCE(?, name),
                description = COALESCE(?, description),
                code = COALESCE(?, code),
                purchase_price = COALESCE(?, purchase_price),
                sale_price = COALESCE(?, sale_price),
                stock = COALESCE(?, stock)
            WHERE id = ?
        '''
        
        # Ajuste da ordem dos parâmetros
        self.cursor.execute(query, (name, description, code, purchase_price, sale_price, stock, int(product_id)))
        self.connection.commit()

    # Método para editar uma venda na tabela Sales
    def update_sale(self, sale_id, customer_id=None, total_value=None, profit=None,sale_date=None, installment=None, payment=None, tax=None):
        """
        Edita uma venda existente na tabela Sales.
        
        Args:
            sale_id (int): ID da venda a ser editada.
            customer_id (int, opcional): Novo ID do cliente.
            total_value (float, opcional): Novo valor total da venda.
            profit (float, opcional): Novo lucro da venda.
            installment (int, opcional): Novo número de parcelas da compra.
            payment (int, opcional): Nova forma de pagamento da compra.
            tax (float, opcional): Nova taxa de juros da compra
            sale_date (str, opcional): Nova data da venda (formato: 'YYYY-MM-DD').
        """
        query = '''
            UPDATE Sales
            SET customer_id = COALESCE(?, customer_id),
                total_value = COALESCE(?, total_value),
                profit = COALESCE(?, profit),
                sale_date = COALESCE(?, sale_date)
                installment = COALESCE(?, installment),
                payment = COALESCE(?, payment),
                tax = COALESCE(?, tax)
            WHERE id = ?
        '''
        self.cursor.execute(query, (customer_id, total_value, profit, sale_date, sale_id, installment, payment, tax))
        self.connection.commit()

    # Método para editar produtos vendidos na tabela SalesProduct
    def update_sales_product(self, sales_product_id, sale_id=None, product_id=None, quantity=None):
        """
        Edita um registro existente na tabela SalesProduct.
        
        Args:
            sales_product_id (int): ID do registro a ser editado na tabela SalesProduct.
            sale_id (int, opcional): Novo ID da venda.
            product_id (int, opcional): Novo ID do produto.
            quantity (int, opcional): Nova quantidade do produto vendido.
        """
        query = '''
            UPDATE SalesProduct
            SET sale_id = COALESCE(?, sale_id),
                product_id = COALESCE(?, product_id),
                quantity = COALESCE(?, quantity)
            WHERE id = ?
        '''
        self.cursor.execute(query, (sale_id, product_id, quantity, sales_product_id))
        self.connection.commit()

    # Método para deletar um cliente na tabela Customer
    def delete_customer(self, customer_id):
        """
        Deleta um cliente da tabela Customer.
        
        Args:
            customer_id (int): ID do cliente a ser deletado.
        """
        query = '''
            DELETE FROM Customer
            WHERE id = ?
        '''
        self.cursor.execute(query, (customer_id,))
        self.connection.commit()

    # Método para deletar um produto na tabela Product
    def delete_product(self, product_id):
        """
        Deleta um produto da tabela Product.
        
        Args:
            product_id (int): ID do produto a ser deletado.
        """
        query = '''
            DELETE FROM Product
            WHERE id = ?
        '''
        self.cursor.execute(query, (product_id,))
        self.connection.commit()

    # Método para deletar uma venda na tabela Sales
    def delete_sale(self, sale_id):
        """
        Deleta uma venda da tabela Sales.
        
        Args:
            sale_id (int): ID da venda a ser deletada.
        """
        # Primeiro, deleta os produtos associados à venda na tabela SalesProduct
        self.cursor.execute('''
            DELETE FROM SalesProduct
            WHERE sale_id = ?
        ''', (sale_id,))
        
        # Depois, deleta a venda na tabela Sales
        self.cursor.execute('''
            DELETE FROM Sales
            WHERE id = ?
        ''', (sale_id,))
        self.connection.commit()

    # Método para deletar um registro na tabela SalesProduct
    def delete_sales_product(self, sales_product_id):
        """
        Deleta um registro da tabela SalesProduct.
        
        Args:
            sales_product_id (int): ID do registro a ser deletado na tabela SalesProduct.
        """
        query = '''
            DELETE FROM SalesProduct
            WHERE id = ?
        '''
        self.cursor.execute(query, (sales_product_id,))
        self.connection.commit()

    # Método para fechar a conexão com o banco de dados
    def close_connection(self):
        # Fecha a conexão com o banco de dados
        self.connection.close()

from datetime import datetime

''' Criando banco de dados para teste '''
def populate_test_database(db_manager):
    """
    Preenche o banco de dados com dados de teste, incluindo clientes, produtos e vendas.
    
    Args:
        db_manager (DatabaseManager): Instância da classe DatabaseManager para manipulação do banco.
    """
    # Dados de exemplo para clientes
    customers = [
        {"name": "John Doe", "cpf": "12345678900", "email": "john@example.com", "phone": "1111111111"},
        {"name": "Jane Smith", "cpf": "98765432100", "email": "jane@example.com", "phone": "2222222222"},
        {"name": "Alice Johnson", "cpf": "11223344556", "email": "alice@example.com", "phone": "3333333333"},
        {"name": "Bob Brown", "cpf": "66778899000", "email": "bob@example.com", "phone": "4444444444"},
    ]
    
    # Inserindo clientes
    for customer in customers:
        db_manager.insert_customer(customer['name'], customer['cpf'], customer['email'], customer['phone'])

    # Dados de exemplo para produtos
    products = [
        {"name": "Laptop", "description": "15-inch laptop", "code": "P001", "purchase_price": 1000, "sale_price": 1200, "stock": 10},
        {"name": "Mouse", "description": "Wireless mouse", "code": "P002", "purchase_price": 20, "sale_price": 30, "stock": 50},
        {"name": "Keyboard", "description": "Mechanical keyboard", "code": "P003", "purchase_price": 50, "sale_price": 70, "stock": 30},
        {"name": "Monitor", "description": "24-inch monitor", "code": "P004", "purchase_price": 200, "sale_price": 250, "stock": 20},
    ]
    
    # Inserindo produtos
    for product in products:
        db_manager.insert_product(product['name'], product['description'], product['code'], product['purchase_price'], product['sale_price'], product['stock'])

    # Gerando vendas aleatórias
    for _ in range(5):  # Vamos gerar 5 vendas
        customer_id = random.randint(1, len(customers))  # Seleciona um cliente aleatoriamente
        sale_date = datetime.now().strftime("%Y-%m-%d")
        total_value = 0
        profit = 0

        # Seleciona de 1 a 3 produtos para a venda
        product_ids = random.sample(range(1, len(products) + 1), random.randint(1, 3))
        quantities = [random.randint(1, 5) for _ in product_ids]

        # Calcula o valor total da venda e o lucro
        for product_id, quantity in zip(product_ids, quantities):
            product = db_manager.fetch_by_id("Product", product_id).iloc[0]
            total_value += product['sale_price'] * quantity
            profit += (product['sale_price'] - product['purchase_price']) * quantity

        # Insere a venda e associa os produtos
        sale_id = db_manager.insert_sale(customer_id, total_value, profit, sale_date)
        
        for product_id, quantity in zip(product_ids, quantities):
            db_manager.insert_sales_product(sale_id, product_id, quantity)
    
    print("Banco de dados de testes populado com sucesso!")
    


if __name__ == "__main__":
    # Cria uma instância do DatabaseManager
    db = DatabaseManager()
    # Popula o banco de dados com dados de teste
    populate_test_database(db)
    # Fecha a conexão com o banco de dados
    db.close_connection()
