'''

Classe responsável pelas operaç~eos de gerenciamento do sistema,
ou seja, a interação com o banco de dados e a manipulação de dados.

'''

from database_manager import DatabaseManager
from datetime import datetime

class SalesProcessor:
    def __init__(self):
        self.db = DatabaseManager()
        
        
    def create_client(self, name, email, cpf, phone):
        """
        Cria um novo cliente no banco de dados.

        Args:
            self.db (DatabaseManager): Instância do gerenciador do banco de dados.
            name (str): Nome do cliente.
            email (str): E-mail do cliente.
            cpf (str): CPF do cliente.
            fone (str): Telefone do cliente.
        """
        self.db.insert_customer(name=name, email=email, cpf=cpf, phone=phone)
        
    def delete_client(self, client_id):
        """
        Deleta um cliente do banco de dados.

        Args:
            self.db (DatabaseManager): Instância do gerenciador do banco de dados.
            client_id (int): ID do cliente a ser deletado.
        """
        self.db.delete_customer(customer_id=client_id)
        
    def create_product(self, name, description, code, purchase_price, sale_price, stock):
        """
        Cria um novo produto no banco de dados.

        Args:
            self.db (DatabaseManager): Instância do gerenciador do banco de dados.
            name (str): Nome do produto.
            description (str): Descrição do produto.
            code (str): Código do produto.
            purchase_price (float): Preço de compra do produto.
            sale_price (float): Preço de venda do produto.
            stock (int): Estoque do produto.
        """
        
        # Verificando se o código do produto já existe
        product = self.search_product(code)
        if product is not None or not product.empty:
            self.db.insert_product(name=name, description=description, code=code, purchase_price=purchase_price, sale_price=sale_price, stock=stock)
            return True
        return False

    def update_product(self, product_id, name, description, code, purchase_price, sale_price, stock):
        """
        Atualiza um produto no banco de dados.

        Args:
            self.db (DatabaseManager): Instância do gerenciador do banco de dados.
            product_id (int): ID do produto a ser atualizado.
            name (str): Nome do produto.
            description (str): Descrição do produto.
            code (str): Código do produto.
            purchase_price (float): Preço de compra do produto.
            sale_price (float): Preço de venda do produto.
            stock (int): Estoque do produto.
        """
        self.db.update_product(product_id=product_id, name=name, description=description, code=code, purchase_price=purchase_price, sale_price=sale_price, stock=stock)

    def check_stock(self, product_code, quantity):
        """
        Verifica se o produto tem estoque suficiente para a venda.
        
        Args:
            product__code (str): Código do produto a ser vendido.
            quantity (int): Quantidade do produto a ser vendida.
        
        Returns:
            bool: True se o estoque for suficiente, False caso contrário.
        """
        product = self.db.fetch_by_id("Product", product_code, "code")
        
        if product.empty:
            return False
        return int(product["stock"].values[0]) >= int(quantity)

    def create_sale(self, client_id, total_price, profit,payment, installment, tax):
        """
        Cria uma nova venda no banco de dados.

        Args:
            self.db (DatabaseManager): Instância do gerenciador do banco de dados.
            client_id (int): ID do cliente que realizou a compra.
            total_price (float): Preço total da compra.
            profit (float): Lucro da compra.
            payment (int): Forma de pagamento da compra.
            installment (int): Número de parcelas da compra.
            tax (float): Taxa de juros da compra.
        """
        sale_date = datetime.now().strftime("%Y-%m-%d")
        sale_id = self.db.insert_sale(customer_id=client_id, total_value=total_price, profit=profit, sale_date=sale_date, payment=payment, installment=installment, tax=tax)
        
        return sale_id

    def process_sale(self, sale_id, product_code, quantity):
        """
        Processa a venda de um produto, atualizando o estoque e registrando a venda.

        Args:
            self.db (DatabaseManager): Instância do gerenciador do banco de dados.
            sale_id (int): ID da venda.
            product_id (int): ID do produto a ser vendido.
            quantity (int): Quantidade do produto a ser vendida.
        """
        # 1. Obtendo as informações do produto
        product = self.db.fetch_by_id("Product", record_id=product_code, column_name="code")
        product_id = product["id"].values[0]
        product_qtd = int(product["stock"].values[0])
        quantity = int(quantity)
        # 2. Verificando se a quantidade de produtos vendidos é menor ou igual ao estoque
        if quantity <= product_qtd:
            # 3. Atualizando o estoque do produto
            new_stock = product_qtd - quantity
            self.db.update_product(product_id=product_id, stock=new_stock)
            # Exibindo dados do produto
            new_product = self.db.fetch_by_id("Product", record_id=product_id)
            # 4. Inserindo o produto vendido na tabela SalesProduct
            self.db.insert_sales_product(sale_id=sale_id, product_id=product_id, quantity=quantity)
            return True
        else:
            return False
     
    def search_sales_product(self, sale_id=None):
        """
        Busca um produto vendido no banco de dados pelo ID da venda.

        Args:
            self.db (DatabaseManager): Instância do gerenciador do banco de dados.
            sale_id (int): ID da venda a ser buscada.
        """
        if sale_id is None:
            sales_product = self.db.fetch_all(table_name = "SalesProduct")
            return sales_product
        sales_product = self.db.fetch_by_id(table_name = "SalesProduct", record_id = sale_id)
        return sales_product
        
    def search_product(self, code):
        """
        Busca um produto no banco de dados pelo código.

        Args:
            self.db (DatabaseManager): Instância do gerenciador do banco de dados.
            code (str): Código do produto a ser buscado.
        """
        product = self.db.fetch_by_id(table_name = "Product", record_id = code, column_name = "code")
        return product
    
    def search_product_id(self, id):
        """
        Busca um produto no banco de dados pelo id.

        Args:
            self.db (DatabaseManager): Instância do gerenciador do banco de dados.
            id (int): Id do produto a ser buscado.
        """
        product = self.db.fetch_by_id(table_name = "Product", record_id = id)
        return product
    
    def filter_product_name(self, name):
        """
        Busca um produto no banco de dados pelo nome.

        Args:
            self.db (DatabaseManager): Instância do gerenciador do banco de dados.
            name (str): Nome do produto a ser buscado.
        """
        product = self.db.filter_by_column(table_name = "Product", column_name = "name", value = name)
        
        return product
    
    def search_client_id(self, id):
        """
        Busca um cliente no banco de dados pelo id.

        Args:
            self.db (DatabaseManager): Instância do gerenciador do banco de dados.
            id (int): Id do cliente a ser buscado.
        """
        client = self.db.fetch_by_id(table_name = "Customer", record_id = id)
        
        return client
    
    def search_client(self, nome=""):
        """
        Busca um cliente no banco de dados pelo nome.

        Args:
            self.db (DatabaseManager): Instância do gerenciador do banco de dados.
            nome (str): Nome do cliente a ser buscado.
        """
        if nome == "":
            client = self.db.fetch_all(table_name = "Customer")
            return client
            
        client = self.db.filter_by_column(table_name = "Customer", column_name = "name", value = nome)
        return client
    
    def update_client(self, client_id, name, email, cpf, phone):
        """
        Atualiza um cliente no banco de dados.

        Args:
            self.db (DatabaseManager): Instância do gerenciador do banco de dados.
            client_id (int): ID do cliente a ser atualizado.
            name (str): Nome do cliente.
            email (str): E-mail do cliente.
            cpf (str): CPF do cliente.
            fone (str): Telefone do cliente.
        """
        self.db.update_customer(customer_id=client_id, name=name, email=email, cpf=cpf, phone=phone)

    def search_sale(self, sale_id=None):
        """
        Busca uma venda no banco de dados pelo ID.

        Args:
            self.db (DatabaseManager): Instância do gerenciador do banco de dados.
            sale_id (int): ID da venda a ser buscada.
        """
        if sale_id is None:
            sale = self.db.fetch_all(table_name = "Sales")
            return sale
        sale = self.db.fetch_by_id(table_name = "Sales", record_id = sale_id)
        return sale