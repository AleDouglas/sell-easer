from PyQt6.QtWidgets import QMainWindow, QApplication, QTableView, QVBoxLayout, QWidget, QPushButton, QHeaderView, QFrame, QGraphicsScene, QGraphicsPixmapItem
from app import Ui_MainWindow  # Importa a interface gerada pelo Qt Designer
from PyQt6.QtCore import Qt, QAbstractTableModel, QVariant
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPixmap,QImage

from sales_processor import SalesProcessor
from datetime import datetime
# traceback
import traceback

# Imports para gráficos
import sys
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class PandasModel(QAbstractTableModel):
    def __init__(self, dataframe: pd.DataFrame):
        super().__init__()
        self._data = dataframe

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            # Centraliza o conteúdo das células
            return Qt.AlignmentFlag.AlignCenter
        return QVariant()

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._data.columns[section]
            else:
                return str(self._data.index[section])

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        # Inicializa a classe SalesProcessor
        self.sales_processor = SalesProcessor()
        
        # Iniciando variávels de controle
        # dataframe para armazenar os produtos do carrinho
        self.carrinho = pd.DataFrame(columns=["id","name", "code", "sale_price", "stock", "quantity"])
        carrinho_tmp = self.carrinho.copy()
        carrinho_tmp.columns = ["ID", "Nome", "Código", "Preço de Venda", "Estoque", "Quantidade"]
        self.clientes = pd.DataFrame(columns=["id", "name", "cpf"])
        
        self.controle_de_estoque = pd.DataFrame(columns=["id", "name", "code", "stock"])
        self.table_estoque = pd.DataFrame(columns=["id", "name", "code", "description", "purchase_price", "sale_price", "stock"])
        estoque_tmp = self.table_estoque.copy()
        estoque_tmp.columns = ["ID", "Nome", "Código", "Descrição", "Preço de Compra", "Preço de Venda", "Estoque"]
        self.vendas = pd.DataFrame(columns=["id", "client_id", "sale_date", "total_value"])
        self.table_vendas = pd.DataFrame(columns=["id", "client_id", "sale_date", "total_value", "payment", "installment", "tax"])
        self.table_log_pd = pd.DataFrame(columns=["ID", "Operação", "Data"])
        self.cliente = None
        self.produto = None
        self.payment_method = 1
        self.taxa = 0
        self.desconto = 0
        self.profit = 0
        self.installment = 1
        self.value_total = 0
        self.purchase_total = 0
        self.installment_table = pd.DataFrame(columns=["N de Parcelas", "Valor das Parcelas", "Taxa", "Desconto"])
        self.payment_names = {
            0: "Dinheiro",
            1: "Cartão de Crédito",
            2: "Cartão de Débito",
            3: "PIX"
        }

        # Inicializa a interface do Qt Designer
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Vai para a pagina loading_page
        self.go_to_loading_page()
        
        # Busca por todas as vendas e preenche o dataframe vendas
        self.vendas = self.sales_processor.search_sale()
        
        # Testando gráficos #################

        # Gerar o gráfico de crescimento
        self.plot_products()
        self.plot_profit_growth_daily()
        self.plot_sales_growth_daily()
        self.plot_sales_growth()
        self.plot_stock_products()
        
        
        ######################
        # Aplicando estilo na QTableView
        self.ui.carrinho_table.setModel(PandasModel(carrinho_tmp))
        self.ui.table_search_client_carrinho.setModel(PandasModel(self.clientes))
        self.ui.table_clientes.setModel(PandasModel(self.clientes))
        self.ui.table_finalizar_venda.setModel(PandasModel(carrinho_tmp))
        self.ui.table_estoque.setModel(PandasModel(estoque_tmp))
        self.ui.table_ultimas_compras.setModel(PandasModel(self.table_vendas))
        self.ui.table_parcelas.setModel(PandasModel(self.installment_table))
        self.ui.table_log.setModel(PandasModel(self.table_log_pd))
        # Configuração para preencher a largura da QTableView
        header = self.ui.carrinho_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # Faz com que as colunas preencham 100% da largura
        
        header_2 = self.ui.table_search_client_carrinho.horizontalHeader()
        header_2.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        model = self.buscar_cliente('')
        model.columns = ["ID", "Nome", "CPF"]
        self.ui.table_search_client_carrinho.setModel(model)
        
        header_25 = self.ui.table_clientes.horizontalHeader()
        header_25.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        header_3 = self.ui.table_finalizar_venda.horizontalHeader()
        header_3.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        header_4 = self.ui.table_estoque.horizontalHeader()
        header_4.setSectionResizeMode(QHeaderView.ResizeMode.Stretch) 
        
        header_5 = self.ui.table_ultimas_compras.horizontalHeader()
        header_5.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        header_6 = self.ui.table_parcelas.horizontalHeader()
        header_6.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        header_7 = self.ui.table_log.horizontalHeader()
        header_7.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        

        # Inicializando Botões do Menu Principal
        self.ui.btn_menu_inicio.clicked.connect(self.go_to_inicial_page)
        self.ui.btn_menu_ccliente.clicked.connect(self.go_to_cadastrar_cliente)
        self.ui.btn_menu_cproduto.clicked.connect(self.go_to_cadastrar_produto)
        self.ui.btn_menu_venda.clicked.connect(self.go_to_registrar_venda)
        self.ui.btn_menu_estoque.clicked.connect(self.go_to_controle_estoque)
        self.ui.btn_menu_clientes.clicked.connect(self.clientes_table)
        self.ui.btn_menu_relatorio.clicked.connect(self.go_to_relatorios)
        self.ui.btn_menu_log.clicked.connect(self.go_to_log_page)
        
        
        
        # Inicializando Botões das Funcionalidades dentro do Sistema
        self.ui.btn_menu_insert_client.clicked.connect(self.insert_client) # Botão de inserir cliente
        self.ui.btn_menu_insert_produto.clicked.connect(self.insert_produto) # Botão de inserir produto
        self.ui.btn_add_carrinho.clicked.connect(self.add_item_carrinho) # Botão de adicionar item ao carrinho
        self.ui.btn_remover_carrinho.clicked.connect(self.remove_item_carrinho) # Botão de remover item do carrinho
        self.ui.btn_finalizar_venda.clicked.connect(self.go_to_finalizar_venda) # Botão de finalizar venda
        self.ui.btn_buscar_cliente.clicked.connect(self.btn_search_client_sales) # Botão de buscar cliente na página de venda
        self.ui.btn_finalizar_venda_2.clicked.connect(self.finalizar_venda) # Botão de finalizar venda
        self.ui.btn_buscar_estoque.clicked.connect(self.buscar_estoque) # Botão de buscar estoque
        self.ui.btn_menu_editar_produto.clicked.connect(self.go_to_editar_estoque) # Botão de editar estoque
        self.ui.btn_menu_insert_produto_2.clicked.connect(self.editar_estoque) # Botão de editar estoque
        
        self.ui.button_next_payment.clicked.connect(self.go_to_payment_method) # Botão de ir para a página de método de pagamento
        self.ui.money_btn.clicked.connect(self.select_money) # Botão de pagamento em dinheiro
        self.ui.credit_btn.clicked.connect(self.select_credit_card)
        self.ui.debit_btn.clicked.connect(self.select_debit_card)
        self.ui.pix_btn.clicked.connect(self.select_pix)
        self.ui.btn_add_parcela.clicked.connect(self.add_installment)
        self.ui.btn_add_taxa.clicked.connect(self.add_tax)
        self.ui.btn_add_desconto.clicked.connect(self.add_discount)
        self.ui.btn_calc_troco.clicked.connect(self.add_troco)
        
        self.ui.btn_buscar_compra.clicked.connect(self.buscar_compra)
        
        
        self.ui.btn_buscar_cliente_2.clicked.connect(self.go_to_cliente_table) # Botão de buscar cliente na página de clientes
        self.ui.btn_menu_editar_cliente.clicked.connect(self.edit_client) # Botão de editar cliente
        self.ui.btn_menu_insert_client_2.clicked.connect(self.save_cliente_edit) # Botão de salvar edição de cliente
        self.ui.btn_deletar_cliente.clicked.connect(self.delete_client) # Botão de deletar cliente
        
        
        self.ui.btn_filter_plot_products.clicked.connect(self.filter_plot_products)
        self.ui.btn_filter_plot_sales.clicked.connect(self.filtrar_plot_sales)
        self.ui.btn_filter_plot_profit.clicked.connect(self.filtrar_plot_profit)
        
        # Botões para cancelar operações
        self.ui.btn_cancelar_op_cadastrar_produto.clicked.connect(self.cancelar_op_cadastrar_produto) # Botão de cancelar operação de cadastro de produto
        self.ui.btn_menu_cancel_insert_client.clicked.connect(self.cancelar_op_cadasatrar_cliente) # Botão de cancelar operação de cadastro de cliente
        self.ui.btn_cancelar_venda.clicked.connect(self.cancelar_op_registrar_venda) # Botão de cancelar operação de venda
        self.ui.btn_cancelar_venda_2.clicked.connect(self.cancelar_op_registrar_venda) # Botão de cancelar operação de finalizar venda
        self.ui.btn_menu_cancel_insert_produto_2.clicked.connect(self.cancelar_op_editar_produto) # Botão de cancelar operação de edição de produto
        self.ui.btn_finalizar_venda_3.clicked.connect(self.cancelar_op_registrar_venda) # Botão de cancelar operação de edição de produto
        
        
        # LOG PAGE
        self.ui.log_filter_btn.clicked.connect(self.filter_log)
        
        # Iniciando Temas
        self.default_theme(
            title_size="font-size: 30px; font-weight: bold;", 
            font_color="color: #333; border: 0;", 
            background_centralwidget="background: #deebf4;",  # Fundo totalmente branco
            background_lineedit="background: white; color: #333;border: 1px solid grey;border-radius: 3px;"  # Fundo dos campos de texto totalmente branco com texto escuro
        )
        
    def filter_plot_products(self):
        from_date = self.ui.dateEdit_3.text()
        to_date = self.ui.dateEdit_4.text()
        dateEdit = datetime.strptime(from_date, "%d/%m/%Y").strftime("%Y-%m-%d")
        dateEdit_2 = datetime.strptime(to_date, "%d/%m/%Y").strftime("%Y-%m-%d")
        self.plot_products(date_from=dateEdit, date_to=dateEdit_2)
        
    def filtrar_plot_sales(self):
        from_date = self.ui.dateEdit_5.text()
        to_date = self.ui.dateEdit_6.text()
        
        dateEdit = datetime.strptime(from_date, "%d/%m/%Y").strftime("%Y-%m-%d")
        dateEdit_2 = datetime.strptime(to_date, "%d/%m/%Y").strftime("%Y-%m-%d")
        self.plot_sales(date_from=dateEdit, date_to=dateEdit_2)
    
    def plot_sales(self, date_from=None, date_to=None):
        if self.vendas.empty:
            return

        actual_month = datetime.now().month
        sales_copy = self.vendas.copy()
        
        # Converter as datas para o formato mês/ano e agrupar por mês
        sales_copy['sale_month'] = pd.to_datetime(sales_copy['sale_date']).dt.to_period('M')
        
        
        # Filtrar datas
        if date_from is not None and date_to is not None:
            vendas_diarias = sales_copy[(sales_copy['sale_date'] >= date_from) & (sales_copy['sale_date'] <= date_to)]
        
        # Agrupar as vendas por dia
        vendas_diarias = vendas_diarias.groupby('sale_date').sum(numeric_only=True).reset_index()
        
        # Adicionar coluna com a soma acumulada por dia
        vendas_diarias['cumulative_sales'] = vendas_diarias['total_value'].cumsum()

        # Obter o tamanho atual do QWidget que você usou no QtDesigner
        width_px = self.ui.graphicsView_initial_4.width()
        height_px = self.ui.graphicsView_initial_4.height()

        dpi = 100
        fig = Figure(figsize=(width_px / dpi, height_px / dpi), dpi=dpi)
        canvas = FigureCanvas(fig)
        
        ax = fig.add_subplot(111)
        ax.plot(vendas_diarias['sale_date'].astype(str), vendas_diarias['cumulative_sales'], marker='o', linestyle='-', color='b')
        ax.set_title("Crescimento de vendas")
        ax.set_ylabel("Valor de vendas por dia")
        ax.grid(True)
        
        
        # Obter o layout existente do graphicsView_initial_4
        layout = self.ui.graphicsView_initial_4.layout()
        
        # Se não houver layout, criar um novo
        if layout is None:
            layout = QVBoxLayout(self.ui.graphicsView_initial_4)
            self.ui.graphicsView_initial_4.setLayout(layout)
        else:
            # Limpar o layout atual removendo widgets anteriores
            for i in reversed(range(layout.count())): 
                layout.itemAt(i).widget().setParent(None)

        # Adicionar o novo canvas ao layout existente
        layout.addWidget(canvas)
        canvas.draw()
    
    def plot_products(self, date_from=None, date_to=None):
        if self.vendas.empty:
            return

        # Pegando a tabela do DB: SalesProduct
        sales_product = self.sales_processor.search_sales_product()

        # Buscar pelo sale_id e adicionar a coluna sale_date sem agrupar
        sales_product = sales_product.merge(self.vendas[['id', 'sale_date']], left_on='sale_id', right_on='id', how='left')

        if date_from is not None and date_to is not None:
            sales_product = sales_product[(sales_product['sale_date'] >= date_from) & (sales_product['sale_date'] <= date_to)]
        
        # Agrupar e somar a quantidade por produto
        sales_product = sales_product.groupby('product_id').sum(numeric_only=True).reset_index()

        # Separando as 20 maiores quantidades e ordenando
        sales_product = sales_product.nlargest(20, 'quantity').sort_values(by='quantity', ascending=False)

        # Buscar o nome do produto
        sales_product['name'] = sales_product['product_id'].apply(lambda x: self.sales_processor.search_product_id(id=x)['name'].iloc[0])

        # Obter o tamanho atual do QWidget que foi nomeado como graphicsView_initial_3 no QtDesigner
        width_px = self.ui.graphicsView_initial_3.width()
        height_px = self.ui.graphicsView_initial_3.height()

        # Definir tamanho mínimo, se necessário
        width_px = max(width_px, 950)
        height_px = max(height_px, 450)

        dpi = 100  # Densidade de pixels por polegada

        # Criar a figura com o tamanho ajustado
        fig = Figure(figsize=(width_px / dpi, height_px / dpi), dpi=dpi)
        canvas = FigureCanvas(fig)

        fig.patch.set_facecolor('#f0f0f0')

        ax = fig.add_subplot(111)

        # Plotar o gráfico de barras
        ax.bar(sales_product['name'].astype(str), sales_product['quantity'], color='b', alpha=0.7)
        ax.set_title("Quantidade de Produtos Vendidos")
        ax.set_xlabel("Nome do Produto")
        ax.set_ylabel("Quantidade Vendida")
        ax.grid(True, axis='y')

        layout = self.ui.graphicsView_initial_3.layout()
        
        # Se não houver layout, criar um novo
        if layout is None:
            layout = QVBoxLayout(self.ui.graphicsView_initial_3)
            self.ui.graphicsView_initial_3.setLayout(layout)
        else:
            # Limpar o layout atual removendo widgets anteriores
            for i in reversed(range(layout.count())): 
                layout.itemAt(i).widget().setParent(None)

        # Adicionar o novo canvas ao layout existente
        layout.addWidget(canvas)
        canvas.draw()
        
    def plot_profit_growth_daily(self):
        if self.vendas.empty:
            return

        actual_month = datetime.now().month
        sales_copy = self.vendas.copy()
        
        # Converter as datas para o formato mês/ano e agrupar por mês
        sales_copy['sale_month'] = pd.to_datetime(sales_copy['sale_date']).dt.to_period('M')
        
        # Filtrar apenas as vendas do mês atual
        vendas_diarias = sales_copy[sales_copy['sale_month'].dt.month == actual_month]
        
        # Agrupar as vendas por dia
        vendas_diarias = vendas_diarias.groupby('sale_date').sum(numeric_only=True).reset_index()
        
        # Adicionar coluna com a soma acumulada por dia
        vendas_diarias['cumulative_profit'] = vendas_diarias['profit'].cumsum()

        # Obter o tamanho atual do QWidget que você usou no QtDesigner
        width_px = self.ui.widget_2.width()
        height_px = self.ui.widget_2.height()
        
        if width_px > 736:
            width_px = 736
        if height_px > 369:
            height_px = 369

        dpi = 100
        fig = Figure(figsize=(width_px / dpi, height_px / dpi), dpi=dpi)
        canvas = FigureCanvas(fig)
        
        ax = fig.add_subplot(111)
        ax.plot(vendas_diarias['sale_date'].astype(str), vendas_diarias['cumulative_profit'], marker='o', linestyle='-', color='b')
        ax.set_title("Lucro por Dia ( Mês Atual )")
        ax.set_ylabel("Lucro ( R$ )")
        ax.grid(True)
        
        layout = self.ui.widget_2.layout()
        
        # Se não houver layout, criar um novo
        if layout is None:
            layout = QVBoxLayout(self.ui.widget_2)
            self.ui.widget_2.setLayout(layout)
        else:
            # Limpar o layout atual removendo widgets anteriores
            for i in reversed(range(layout.count())): 
                layout.itemAt(i).widget().setParent(None)

        # Adicionar o novo canvas ao layout existente
        layout.addWidget(canvas)
        canvas.draw()
    
    def filtrar_plot_profit(self):
        from_date = self.ui.dateEdit_7.text()
        to_date = self.ui.dateEdit_8.text()
        
        dateEdit = datetime.strptime(from_date, "%d/%m/%Y").strftime("%Y-%m-%d")
        dateEdit_2 = datetime.strptime(to_date, "%d/%m/%Y").strftime("%Y-%m-%d")
        self.plot_profit_growth_custom(date_from=dateEdit, date_to=dateEdit_2)
    
    def plot_profit_growth_custom(self, date_from=None, date_to=None):
        if self.vendas.empty:
            return

        actual_month = datetime.now().month
        sales_copy = self.vendas.copy()
        
        # Converter as datas para o formato mês/ano e agrupar por mês
        sales_copy['sale_month'] = pd.to_datetime(sales_copy['sale_date']).dt.to_period('M')
        
        # Filtrando o mês
        vendas_diarias = sales_copy[(sales_copy['sale_date'] >= date_from) & (sales_copy['sale_date'] <= date_to)]
        # Agrupar as vendas
        sale_month_qtd = len(vendas_diarias['sale_month'].unique())
        if sale_month_qtd > 1:
            vendas_diarias = vendas_diarias.groupby('sale_month').sum(numeric_only=True).reset_index()
        else:
            vendas_diarias = vendas_diarias.groupby('sale_date').sum(numeric_only=True).reset_index()
        
        # Adicionar coluna com a soma acumulada por dia
        vendas_diarias['cumulative_profit'] = vendas_diarias['profit'].cumsum()

        # Obter o tamanho atual do QWidget que você usou no QtDesigner
        width_px = self.ui.graphicsView_initial_5.width()
        height_px = self.ui.graphicsView_initial_5.height()
        
        if width_px > 736:
            width_px = 736
        if height_px > 369:
            height_px = 369

        dpi = 100
        fig = Figure(figsize=(width_px / dpi, height_px / dpi), dpi=dpi)
        canvas = FigureCanvas(fig)
        
        ax = fig.add_subplot(111)
        if sale_month_qtd > 1:
            ax.plot(vendas_diarias['sale_month'].astype(str), vendas_diarias['cumulative_profit'], marker='o', linestyle='-', color='b')
            ax.set_title("Lucro por Mês")
        else:
            ax.plot(vendas_diarias['sale_date'].astype(str), vendas_diarias['cumulative_profit'], marker='o', linestyle='-', color='b')
            ax.set_title("Lucro por Dia ( Mês Atual )")
        ax.set_ylabel("Lucro ( R$ )")
        ax.grid(True)
        
        layout = self.ui.graphicsView_initial_5.layout()
        
        # Se não houver layout, criar um novo
        if layout is None:
            layout = QVBoxLayout(self.ui.graphicsView_initial_5)
            self.ui.graphicsView_initial_5.setLayout(layout)
        else:
            # Limpar o layout atual removendo widgets anteriores
            for i in reversed(range(layout.count())): 
                layout.itemAt(i).widget().setParent(None)

        # Adicionar o novo canvas ao layout existente
        layout.addWidget(canvas)
        canvas.draw()
        
        
    def plot_sales_growth_daily(self):
        if self.vendas.empty:
            return

        actual_month = datetime.now().month
        sales_copy = self.vendas.copy()
        
        # Converter as datas para o formato mês/ano e agrupar por mês
        sales_copy['sale_month'] = pd.to_datetime(sales_copy['sale_date']).dt.to_period('M')
        
        # Filtrar apenas as vendas do mês atual
        vendas_diarias = sales_copy[sales_copy['sale_month'].dt.month == actual_month]
        
        # Agrupar as vendas por dia
        vendas_diarias = vendas_diarias.groupby('sale_date').sum(numeric_only=True).reset_index()
        
        # Adicionar coluna com a soma acumulada por dia
        vendas_diarias['cumulative_sales'] = vendas_diarias['total_value'].cumsum()

        # Obter o tamanho atual do QWidget que você usou no QtDesigner
        width_px = self.ui.graphicsView_initial_2.width()
        height_px = self.ui.graphicsView_initial_2.height()
        
        if width_px > 736:
            width_px = 736
        if height_px > 369:
            height_px = 369

        dpi = 100
        fig = Figure(figsize=(width_px / dpi, height_px / dpi), dpi=dpi)
        canvas = FigureCanvas(fig)
        
        ax = fig.add_subplot(111)
        ax.plot(vendas_diarias['sale_date'].astype(str), vendas_diarias['cumulative_sales'], marker='o', linestyle='-', color='b')
        ax.set_title("Crescimento de vendas por dia no mês atual")
        ax.set_ylabel("Valor de vendas por dia")
        ax.grid(True)
        
        layout = self.ui.graphicsView_initial_2.layout()
        
        # Se não houver layout, criar um novo
        if layout is None:
            layout = QVBoxLayout(self.ui.graphicsView_initial_2)
            self.ui.graphicsView_initial_2.setLayout(layout)
        else:
            # Limpar o layout atual removendo widgets anteriores
            for i in reversed(range(layout.count())): 
                layout.itemAt(i).widget().setParent(None)

        # Adicionar o novo canvas ao layout existente
        layout.addWidget(canvas)
        canvas.draw()
        
    def plot_sales_growth(self):
        if self.vendas.empty:
            return

        # Converter as datas para o formato mês/ano e agrupar por mês
        self.vendas['sale_month'] = pd.to_datetime(self.vendas['sale_date']).dt.to_period('M')

        # Agrupar as vendas por mês
        vendas_mensais = self.vendas.groupby('sale_month').sum(numeric_only=True).reset_index()

        # Calcular a soma acumulada das vendas mensais
        vendas_mensais['cumulative_sales'] = vendas_mensais['total_value'].cumsum()

        # Obter o tamanho atual do QWidget que foi nomeado como graphicsView_initial no QtDesigner
        width_px = self.ui.graphicsView_initial.width()
        height_px = self.ui.graphicsView_initial.height()
        
        if width_px > 736:
            width_px = 736
        if height_px > 369:
            height_px = 369


        dpi = 100  # Densidade de pixels por polegada

        # Criar a figura com o tamanho ajustado
        fig = Figure(figsize=(width_px / dpi, height_px / dpi), dpi=dpi)
        canvas = FigureCanvas(fig)

        # Adicionando borda e cor de fundo
        fig.patch.set_facecolor('#f0f0f0')
        fig.patch.set_linewidth(0)

        ax = fig.add_subplot(111)
        
        # Plotar o gráfico de linha mostrando o crescimento
        ax.plot(vendas_mensais['sale_month'].astype(str), vendas_mensais['cumulative_sales'], marker='o', linestyle='-', color='b')
        ax.set_title("Crescimento de vendas por mês")
        ax.set_ylabel("Valor de vendas por mês")
        ax.grid(True)

        layout = self.ui.graphicsView_initial.layout()
        
        # Se não houver layout, criar um novo
        if layout is None:
            layout = QVBoxLayout(self.ui.graphicsView_initial)
            self.ui.graphicsView_initial.setLayout(layout)
        else:
            # Limpar o layout atual removendo widgets anteriores
            for i in reversed(range(layout.count())): 
                layout.itemAt(i).widget().setParent(None)

        # Adicionar o novo canvas ao layout existente
        layout.addWidget(canvas)
        canvas.draw()

    def plot_stock_products(self):
        
        self.controle_de_estoque = self.sales_processor.filter_product_name("")
        estoque_tmp = self.controle_de_estoque.copy()

        # Ordenando por estoque
        estoque_tmp = estoque_tmp.sort_values(by='stock', ascending=False)
        estoque_tmp = estoque_tmp.head(10)
        
        width_px = self.ui.widget.width()
        height_px = self.ui.widget.height()
        dpi = 100
        fig = Figure(figsize=(width_px / dpi, height_px / dpi), dpi=dpi)
        canvas = FigureCanvas(fig)
        fig.patch.set_facecolor('#f0f0f0')
        fig.patch.set_linewidth(0)
        ax = fig.add_subplot(111)
        ax.bar(estoque_tmp['name'].astype(str), estoque_tmp['stock'], color='b', alpha=0.7)
        ax.set_title("Quantidade de Produtos em Estoque")
        ax.set_ylabel("Quantidade em Estoque")
        ax.grid(True)
        
        layout = self.ui.widget.layout()
        
        # Se não houver layout, criar um novo
        if layout is None:
            layout = QVBoxLayout(self.ui.widget)
            self.ui.widget.setLayout(layout)
        else:
            # Limpar o layout atual removendo widgets anteriores
            for i in reversed(range(layout.count())): 
                layout.itemAt(i).widget().setParent(None)

        # Adicionar o novo canvas ao layout existente
        layout.addWidget(canvas)
        canvas.draw()
 
    def go_to_loading_page(self):
        # Inicia progressBar_loading_page em 0
        self.ui.progressBar_loading_page.setValue(0)
        # Muda para a página `loading_page`
        self.ui.stackedWidget.setCurrentWidget(self.ui.loading_page)
        
        # Define a duração total em milissegundos (5 segundos)
        duration = 750
        # Define o incremento de tempo em milissegundos
        interval = 50
        # Calcula o incremento de valor para a progress bar
        self.step = 100 / (duration / interval)

        # Inicia o QTimer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(interval)

    def update_progress(self):
        # Atualiza o valor da progress bar
        current_value = self.ui.progressBar_loading_page.value()
        # Converte o incremento para inteiro
        next_value = current_value + int(self.step)
        
        # Evita passar de 100 devido a arredondamentos
        if next_value >= 100:
            next_value = 100

        self.ui.progressBar_loading_page.setValue(next_value)

        # Para o timer quando atinge 100%
        if next_value >= 100:
            self.timer.stop()
            # Muda para a página `page_1_inicial`
            self.go_to_inicial_page()

    def go_to_inicial_page(self):
        # Recarregando gráficos
        self.vendas = self.sales_processor.search_sale()
        self.plot_products()
        self.plot_profit_growth_daily()
        self.plot_sales_growth_daily()
        self.plot_sales_growth()
        # Muda para a página `page_1_inicial`
        self.ui.stackedWidget.setCurrentWidget(self.ui.page)
        
    def go_to_cadastrar_cliente(self):
        # Muda para a página `page_2_cadastrar_cliente`
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_2_ccliente)
        
    def go_to_cadastrar_produto(self):
        # Muda para a página `page_3_cadastrar_produto`
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_3_cproduto)
        
    def go_to_registrar_venda(self):
        # Muda para a página `page_4_registrar_venda`
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_4_venda)
    
    def go_to_controle_estoque(self):
        # Faz uma busca pelo estoque e preenche a tabela
        self.controle_de_estoque = self.sales_processor.filter_product_name("")
        estoque_tmp = self.controle_de_estoque.copy()
        estoque_tmp.columns = ["ID", "Nome", "Código", "Descrição", "Preço de Compra", "Preço de Venda", "Estoque"]
        model = PandasModel(estoque_tmp)
        self.ui.table_estoque.setModel(model)
        
        
        # Muda para a página `page_5_controle_estoque`
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_5_estoque)
        
    def go_to_relatorios(self):
        self.buscar_ultimas_compras = self.sales_processor.search_sale()
        ultimas_vendas = self.buscar_ultimas_compras
        # Convertendo valores para payment_names no método de pagamento
        ultimas_vendas["payment"] = ultimas_vendas["payment"].map(self.payment_names)
        # Renomeando as colunas
        ultimas_vendas.columns = ["ID da Venda", "ID Cliente", "Valor Total ( R$ )", "Lucro", "Parcelas", "Método de Pagamento", "Taxa de Juros (%)", "Desconto (%)","Data da Venda"]
        
        
        self.ui.table_ultimas_compras.setModel(PandasModel(ultimas_vendas))
        
        # Muda para a página `page_6_relatorios`
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_6_relatorio)
        
    def go_to_configuracoes(self):
        # Muda para a página `page_7_configuracoes`
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_7_config)
    
    def go_to_finalizar_venda(self):
        # Muda para a página `page_8_finalizar_venda`
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_8_finalizar_venda)
        
    def go_to_editar_estoque(self):
        # Muda para a página `page_9_editar_estoque`
        # Antes verifica se um produto foi selecionado
        product_code = self.ui.lineEdit_buscar_estoque_codigo.text()
        if product_code == "":
            self.ui.error_buscar_estoque.setText("Produto não selecionado")
            return
        # Busca pelo produto
        product = self.sales_processor.search_product(code=product_code)
        if product is None or product.empty:
            self.ui.error_buscar_estoque.setText("Produto não encontrado")
            return
        # Atualiza a variável produto
        self.produto = product["id"].iloc[0]
        # Preenche os campos da página de editar estoque
        self.ui.lineEdit_add_name_produto_2.setText(product["name"].iloc[0])
        self.ui.lineEdit_add_description_2.setText(product["description"].iloc[0])
        self.ui.lineEdit_add_codigo_produto_2.setText(product["code"].iloc[0])
        self.ui.lineEdit_add_valor_compra_2.setText(str(product["purchase_price"].iloc[0]))
        self.ui.lineEdit_add_valor_venda_2.setText(str(product["sale_price"].iloc[0]))
        self.ui.lineEdit_add_estoque_2.setText(str(product["stock"].iloc[0]))
        
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_9_editar_estoque)    
    
    def go_to_cliente_table(self):
        '''
        Método para buscar um cliente na página de cadastro de cliente
        '''
        nome = self.ui.lineEdit_buscar_cliente_nome.text()
        modal = self.buscar_cliente(nome)
        self.ui.table_clientes.setModel(modal)
        
    def go_to_payment_method(self):
        '''
        Método para mudar para a página de método de pagamento
        '''
        # 1. Verificando se o carrinho está vazio
        if self.carrinho.empty:
            self.ui.error_registrar_venda.setText("Carrinho vazio, é necessário adicionar itens para finalizar uma venda")
            return
        cliente = self.ui.table_search_client_carrinho.model().index(self.ui.table_search_client_carrinho.currentIndex().row(), 0).data()

        # 2. Verificando se o cliente foi selecionado
        if cliente is None:
            self.ui.error_registrar_venda.setText("Cliente não selecionado")
            return
        
        self.ui.stackedWidget.setCurrentWidget(self.ui.payment_method)
       
    def go_to_log_page(self):
        '''
        Método para mudar para a página de log
        '''
        
        # Buscando o log
        self.table_log_pd = self.sales_processor.search_log()
        # log
        log = self.table_log_pd.copy()
        # Alterando o nome das colunas
        log.columns = ["ID", "Operação", "Data"]
        # Gerando o modelo
        model = PandasModel(log)
        # Atualizando a tabela
        self.ui.table_log.setModel(model)
        
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_log)
        
    def filter_log(self):
        '''
        Método para filtrar o log
        '''
        date_from = self.ui.dateEdit_9.text()
        date_to = self.ui.dateEdit_10.text()
        
        # Buscando o log no dataframe
        log = self.table_log_pd.copy()
        # Convertendo as datas para o formato datetime
        log["datetime"] = pd.to_datetime(log["datetime"])
        # Filtrando as datas
        log = log[(log["datetime"] >= date_from) & (log["datetime"] <= date_to)]
        # Alterando o nome das colunas
        log.columns = ["ID", "Operação", "Data"]
        # Gerando o modelo
        model = PandasModel(log)
        # Atualizando a tabela
        self.ui.table_log.setModel(model)
        
    def select_money(self):
        '''
        Método para mudar para a página de finalizar pagamento
        '''
        self.payment_method = 0
        self.installment = 1
        self.taxa = 0
        self.desconto = 0
        self.ui.label_metodo_pagamento_2.setText("Dinheiro")
        self.ui.stackedWidget.setCurrentWidget(self.ui.finish_payment)
        
        # Preenchendo a tabela de parcelas, como o pagamento é à vista, só terá uma parcela
        self.installment_table = pd.DataFrame({
            "N de Parcelas": [1],
            "Valor das Parcelas ( R$ )": [self.value_total],
            "Taxa %": [0],
            "Desconto %": [0]
        })

        # Atualizando o modelo e exibindo a tabela na interface
        model = PandasModel(self.installment_table)
        self.ui.table_parcelas.setModel(model)
        
    def select_credit_card(self):
        '''
        Método para mudar para a página de finalizar pagamento
        '''
        self.payment_method = 1
        self.installment = 1
        self.taxa = 0
        self.desconto = 0
        self.ui.label_metodo_pagamento_2.setText("Cartão de Crédito")
        self.ui.stackedWidget.setCurrentWidget(self.ui.finish_payment)
        
        # Preenchendo a tabela de parcelas, como o pagamento é à vista, só terá uma parcela
        self.installment_table = pd.DataFrame({
            "N de Parcelas": [1],
            "Valor das Parcelas ( R$ )": [self.value_total],
            "Taxa %": [0],
            "Desconto %": [0]
        })

        # Atualizando o modelo e exibindo a tabela na interface
        model = PandasModel(self.installment_table)
        self.ui.table_parcelas.setModel(model)
        
    def select_debit_card(self):
        '''
        Método para mudar para a página de finalizar pagamento
        '''
        self.payment_method = 2
        self.installment = 1
        self.taxa = 0
        self.desconto = 0
        self.ui.label_metodo_pagamento_2.setText("Cartão de Débito")
        self.ui.stackedWidget.setCurrentWidget(self.ui.finish_payment)
        
        # Preenchendo a tabela de parcelas, como o pagamento é à vista, só terá uma parcela
        self.installment_table = pd.DataFrame({
            "N de Parcelas": [1],
            "Valor das Parcelas ( R$ )": [self.value_total],
            "Taxa %": [0],
            "Desconto %": [0]
        })

        # Atualizando o modelo e exibindo a tabela na interface
        model = PandasModel(self.installment_table)
        self.ui.table_parcelas.setModel(model)
        
    def select_pix(self):
        '''
        Método para mudar para a página de finalizar pagamento
        '''
        self.payment_method = 3
        self.installment = 1
        self.taxa = 0
        self.desconto = 0
        self.ui.label_metodo_pagamento_2.setText("PIX")
        self.ui.stackedWidget.setCurrentWidget(self.ui.finish_payment)
        
        # Preenchendo a tabela de parcelas, como o pagamento é à vista, só terá uma parcela
        self.installment_table = pd.DataFrame({
            "N de Parcelas": [1],
            "Valor das Parcelas ( R$ )": [self.value_total],
            "Taxa %": [0],
            "Desconto %": [0]
        })

        # Atualizando o modelo e exibindo a tabela na interface
        model = PandasModel(self.installment_table)
        self.ui.table_parcelas.setModel(model)
        
    def add_tax(self):
        value = self.ui.lineEdit_adicionar_taxa.text()
        total = self.value_total
        if value == "":
            value = 0
        try:
            if not value.replace(".", "", 1).isdigit():
                value = 0
        except:
            value = 0
        
        # Removendo a taxa anterior
        
        self.value_total = ( total * 100 ) / ( 100 + self.taxa )
        # Calculando a diferença para reduzir do self.purchase_total
        # Atualizando o valor da taxa
        self.taxa = float(value)
        self.value_total = self.value_total + (self.value_total * (self.taxa / 100))
        # Atualizando os valores na interface
        self.ui.label_valor_total_3.setText(f"R${self.value_total:.2f}")
        # Atualizando a tabela de parcelas
        parcelas = [self.installment]
        valores = [self.value_total / self.installment]
        taxas = [self.taxa]
        desconto = [self.desconto]
        self.installment_table = pd.DataFrame({
            "N de Parcelas": self.installment,
            "Valor das Parcelas ( R$ )": valores,
            "Taxa %": taxas,
            "Desconto %": desconto
        })
        
        # Atualizando a tabela de parcelas
        model = PandasModel(self.installment_table)
        self.ui.table_parcelas.setModel(model)
        
    def add_discount(self):
        value = self.ui.lineEdit_adicionar_desconto.text()
        total = self.value_total
        if value == "":
            value = 0
        try:
            if not value.replace(".", "", 1).isdigit():
                value = 0
        except:
            value = 0
        
        # Removendo o desconto anterior
        self.value_total = ( total * 100 ) / ( 100 - self.desconto )
        # Calculando a diferença para reduzir do self.purchase_total
        # Atualizando o valor do desconto
        self.desconto = float(value)
        self.value_total = self.value_total - (self.value_total * (self.desconto / 100))
        # Atualizando os valores na interface
        self.ui.label_valor_total_3.setText(f"R${self.value_total:.2f}")
        # Atualizando a tabela de parcelas
        parcelas = [self.installment]
        valores = [self.value_total / self.installment]
        taxas = [self.taxa]
        desconto = [self.desconto]
        self.installment_table = pd.DataFrame({
            "N de Parcelas": parcelas,
            "Valor das Parcelas ( R$ )": valores,
            "Taxa %": taxas,
            "Desconto %": desconto
        })
        
        # Atualizando a tabela de parcelas
        model = PandasModel(self.installment_table)
        self.ui.table_parcelas.setModel(model)
        
    def add_installment(self):
        ''' Gerando nova tabela de parcelas '''
        value = self.ui.lineEdit_adicionar_parcelas.text()
        total = self.value_total
        if value == "":
            self.ui.error_adicionar_parcela.setText("Campo obrigatório: Número de parcelas não preenchido")
            return
        if not value.isdigit():
            self.ui.error_adicionar_parcela.setText("Número de parcelas deve ser um número inteiro")
            return
        self.installment = int(value)
        
        parcelas = [self.installment]
        valores = [self.value_total / self.installment]  
        taxas = [self.taxa]
        desconto = [self.desconto]
        self.installment_table = pd.DataFrame({
            "N de Parcelas": parcelas,
            "Valor das Parcelas ( R$ )": valores,
            "Taxa %": taxas,
            "Desconto %": desconto
        })
        
        # Atualizando a tabela de parcelas
        model = PandasModel(self.installment_table)
        self.ui.table_parcelas.setModel(model)
        
    def add_troco(self):
        value = self.ui.lineEdit_valor_recebido.text()
        if value == "":
            return
        try:
            result = f'R${float(value) - self.value_total}'
        except:
            self.ui.label_result_troco.setText('Invalid Value')
            return
            
        self.ui.label_result_troco.setText(result)
    
    def insert_client(self):
        # Captura os valores dos QLineEdit
        nome = self.ui.lineEdit_add_nome_cliente.text()
        email = self.ui.lineEdit_add_email.text()
        cpf = self.ui.lineEdit_add_cpf.text()
        phone = self.ui.lineEdit_add_fone.text()
        
        # Verificando se o único campo obrigatório está preenchido ( Nome do cliente )
        if nome == "":
            # Alterando QLabel: error_cadastrar_client para informar que o campo nome é obrigatório
            self.ui.error_cadastrar_client.setText("Campo obrigatório: Nome do Cliente não preenchido")
            return
        
        # Chamando o método create_client da classe SalesProcessor
        self.sales_processor.create_client(name=nome, email=email, cpf=cpf, phone=phone)
        
        # Alterando QLabel: error_cadastrar_client para informar que o cliente foi cadastrado com sucesso
        self.ui.stackedWidget.setCurrentWidget(self.ui.end_finish_payment)

    def insert_produto(self):
        nome = self.ui.lineEdit_add_name_produto.text() # Obrigatório
        description = self.ui.lineEdit_add_description.text()
        codigo = self.ui.lineEdit_add_codigo_produto.text() # Obrigatório
        valor_compra = self.ui.lineEdit_add_valor_compra.text() # Obrigatório
        valor_venda = self.ui.lineEdit_add_valor_venda.text() # Obrigatório
        estoque = self.ui.lineEdit_add_estoque.text() # Obrigatório
        
        if nome == "" or codigo == "" or valor_compra == "" or valor_venda == "" or estoque == "":
            self.ui.error_cadastrar_produto.setText("Campos obrigatórios não preenchidos")
            return
        
        try:
            valor_venda = float(valor_venda)
            valor_compra = float(valor_compra)
            estoque = int(estoque)
        except:
            self.ui.error_cadastrar_produto.setText("Verifique os valores inseridos!")
            return

        
        # Verifica se já existe um produto com o mesmo código
        product = self.sales_processor.search_product(code=codigo)
        if product is not None and not product.empty:
            self.ui.error_cadastrar_produto.setText("Produto já cadastrado")
            return
        
        new_product = self.sales_processor.create_product(name=nome, description=description, code=codigo, purchase_price=valor_compra, sale_price=valor_venda, stock=estoque)
        
        if not new_product:
            self.ui.error_cadastrar_produto.setText("Produto já cadastrado")
            return
        
        self.ui.stackedWidget.setCurrentWidget(self.ui.end_finish_payment)
        
    def cancelar_op_cadastrar_produto(self):
        '''
        Método para limpar os campos do formulário de cadastro de produto
        '''
        self.ui.lineEdit_add_name_produto.setText("")
        self.ui.lineEdit_add_description.setText("")
        self.ui.lineEdit_add_codigo_produto.setText("")
        self.ui.lineEdit_add_valor_compra.setText("")
        self.ui.lineEdit_add_valor_venda.setText("")
        self.ui.lineEdit_add_estoque.setText("")
        self.ui.error_cadastrar_produto.setText("")
        
    def cancelar_op_cadasatrar_cliente(self):
        '''
        Método para limpar os campos do formulário de cadastro de cliente
        '''
        self.ui.lineEdit_add_nome_cliente.setText("")
        self.ui.lineEdit_add_email.setText("")
        self.ui.lineEdit_add_cpf.setText("")
        self.ui.lineEdit_add_fone.setText("")
        self.ui.error_cadastrar_client.setText("")
        
    def cancelar_op_registrar_venda(self):
        '''
        Método para limpar os campos do formulário de registrar venda
        '''
        self.ui.lineEdit_cod_produto_carrinho.setText("")
        self.ui.lineEdit_qtd_produto_carrinho_2.setText("1")
        self.ui.error_registrar_venda.setText("")
        ''' Limpar o carrinho '''
        self.carrinho = pd.DataFrame(columns=["id","name", "code", "sale_price", "stock", "quantity", "purchase_price"])
        self.clientes = pd.DataFrame(columns=["id", "name", "cpf"])
        self.cliente = None
        # Atualiza a visualização do carrinho na QTableView
        tmp_carrinho = self.carrinho.copy()
        tmp_carrinho.columns = ["ID", "Nome", "Código", "Preço de Venda", "Estoque", "Quantidade", "Preço de Compra Total"]
        model = PandasModel(tmp_carrinho)
        tmp_cliente = self.clientes.copy()
        tmp_cliente.columns = ["ID", "Nome", "CPF"]
        model_client = PandasModel(tmp_cliente)
        self.ui.carrinho_table.setModel(model)
        self.ui.table_search_client_carrinho.setModel(model_client)
        self.ui.table_finalizar_venda.setModel(model)
        # Atualizando os valores na interface
        self.ui.label_qtd_itens_carrinho.setText("0")
        self.ui.label_valor_total_carrinho.setText("R$0.00")
        self.ui.label_qtd_itens_carrinho_2.setText("0")
        self.ui.label_valor_total_carrinho_2.setText("R$0.00")
        self.ui.label_valor_total_3.setText("R$0.00")
        self.value_total = 0
        self.purchase_total = 0
        
        self.go_to_registrar_venda()
        
    def cancelar_op_editar_produto(self):
        '''
        Método para limpar os campos do formulário de editar produto
        '''
        self.ui.lineEdit_add_name_produto_2.setText("")
        self.ui.lineEdit_add_description_2.setText("")
        self.ui.lineEdit_add_codigo_produto_2.setText("")
        self.ui.lineEdit_add_valor_compra_2.setText("")
        self.ui.lineEdit_add_valor_venda_2.setText("")
        self.ui.lineEdit_add_estoque_2.setText("")
        self.ui.error_cadastrar_produto_2.setText("")
        ''' Limpar o produto '''
        self.produto = None
        self.ui.error_buscar_estoque.setText("")
        self.go_to_controle_estoque()
        
    def add_item_carrinho(self):
        codigo = self.ui.lineEdit_cod_produto_carrinho.text()
        quantidade = self.ui.lineEdit_qtd_produto_carrinho_2.text()
        
        # Verificando se o valor é negativo
        if quantidade != "":
            if int(quantidade) < 0:
                self.ui.error_registrar_venda.setText("Quantidade não pode ser negativa")
                return
        
        # Verifica se o campo de código está vazio
        if codigo == "":
            self.ui.error_registrar_venda.setText("Campo obrigatório: Código do Produto não preenchido")
            return
        
        # Busca o produto pelo código
        product = self.sales_processor.search_product(code=codigo)
        # Removendo colunas description e purchase_price
        product = product.drop(columns=["description"])
        
        # Verifica se o produto foi encontrado e se não está vazio
        if product is None or product.empty:
            self.ui.error_registrar_venda.setText("Produto não encontrado")
            return
        
        # Verifica se o produto possui dados válidos antes de concatenar
        if not product.dropna(how='all').empty:
            # Adiciona a quantidade de produtos no DataFrame
            if quantidade == "":
                quantidade = 1  # Se a quantidade não for informada, assume 1
            product["quantity"] = int(quantidade)

            # MUltiplica o preço de venda pelo quantidade
            product["sale_price"] = float(product["sale_price"].iloc[0]) * product["quantity"].iloc[0]
            product["purchase_price"] = float(product["purchase_price"].iloc[0]) * product["quantity"].iloc[0]
            
            self.carrinho = pd.concat([self.carrinho, product], ignore_index=True)
            
        self.carrinho['id'] = range(1, len(self.carrinho) + 1)
        
        # Criando uma variável temporário para self.carrinho e trocar nome das colunastotal_purchase
        tmp_carrinho = self.carrinho.copy()
        
        tmp_carrinho.columns = ["ID", "Nome", "Código", "Preço de Venda  ( R$ )", "Estoque", "Quantidade", "Preço de Compra Total ( R$ )"]

        # Atualiza a visualização do carrinho na QTableView
        model = PandasModel(tmp_carrinho)
        self.ui.carrinho_table.setModel(model)  # Assume que o nome do QTableView é carrinho_table
        # Limpa mensagens de erro anteriores
        self.ui.error_registrar_venda.setText("")
        # Somando a coluna sale_price do carrinho
        total = self.carrinho["sale_price"].sum()
        total_purchase = self.carrinho["purchase_price"].sum()
        
        # Atualizando os valores na interface
        # Quantidade de itens é dado pela soma da coluna quantity
        self.ui.label_qtd_itens_carrinho.setText(str(self.carrinho["quantity"].sum()))
        # label_valor_total_carrinho
        self.ui.label_valor_total_carrinho.setText(f"R${total:.2f}")
        
        # Gerando carrinho na página de finalizar venda
        self.ui.table_finalizar_venda.setModel(model)
        self.ui.label_qtd_itens_carrinho_2.setText(str(self.carrinho["quantity"].sum()))
        self.ui.label_valor_total_carrinho_2.setText(f"R${total:.2f}")
        
        
        self.ui.label_valor_total_3.setText(f"R${total:.2f}")
        self.value_total = total
        self.purchase_total = total_purchase
        
    def remove_item_carrinho(self):
        # Implementar a remoção de um item do carrinho
        id = self.ui.lineEdit_id_remove_carrinho.text()
        # Verifica se o campo de código está vazio
        if id == "":
            self.ui.error_registrar_venda.setText("Campo obrigatório: ID do Produto não preenchido")
            return
        # Verifica se o id é um número
        if not id.isdigit():
            self.ui.error_registrar_venda.setText("ID do Produto deve ser um número")
            return
        # Verifica se o id é um número válido
        if int(id) not in self.carrinho["id"].values:
            self.ui.error_registrar_venda.setText("ID do Produto não encontrado")
            return
        # Remove o item do carrinho
        self.carrinho = self.carrinho[self.carrinho["id"] != int(id)]
        
        tmp_carrinho = self.carrinho.copy()
        tmp_carrinho.columns = ["ID", "Nome", "Código", "Preço de Venda ( R$ )","Estoque", "Quantidade", "Preço de Compra Total ( R$ )"]
        
        model = PandasModel(tmp_carrinho)
        self.ui.carrinho_table.setModel(model)
        self.ui.error_registrar_venda.setText("")
        total = self.carrinho["sale_price"].sum()
        total_purchase = self.carrinho["purchase_price"].sum()
        self.value_total = total
        self.purchase_total = total_purchase
        
        self.ui.label_qtd_itens_carrinho.setText(str(self.carrinho["quantity"].sum()))
        self.ui.label_valor_total_carrinho.setText(f"R${total:.2f}")
        
    def btn_search_client_sales(self):
        name = self.ui.lineEdit_buscar_cliente_carrinho.text()
        model = self.buscar_cliente(name)
        self.ui.table_search_client_carrinho.setModel(model)
        
    def buscar_cliente(self, name=""):
        # Busca um cliente no banco de dados pelo nome
        # Retorna um DataFrame com os dados do cliente
        if name == "":
            cliente = self.sales_processor.search_client()
        else:
            cliente = self.sales_processor.search_client(name)
        # Manter apenas as colunas id, name e cpf
        cliente = cliente[["id", "name", "cpf"]]
        cliente.columns = ["ID", "Nome", "CPF"]
        # Preenchendo tabela table_search_client_carrinho com os resultados
        model = PandasModel(cliente)
        return model
        
    def finalizar_venda(self):
        try:
            # Verificar se o carrinho está vazio
            if self.carrinho.empty:
                self.ui.error_registrar_venda_2.setText("Carrinho vazio, é necessário adicionar itens para finalizar uma venda")
                self.ui.error_registrar_venda_2.setStyleSheet("color: red")
                return

            produtos = self.carrinho[["id", "code", "quantity"]]
            # Pegando cliente a partir do QTableView selecionado
            cliente = self.ui.table_search_client_carrinho.model().index(self.ui.table_search_client_carrinho.currentIndex().row(), 0).data()
            
            # Verifica se o cliente foi selecionado
            if cliente is None:
                self.ui.error_registrar_venda_2.setText("Cliente não selecionado")
                self.ui.error_registrar_venda_2.setStyleSheet("color: red")
                return
            # Verifica se o carrinho está vazio
            if produtos.empty or produtos is None:
                self.ui.error_registrar_venda_2.setText("Carrinho vazio")
                self.ui.error_registrar_venda_2.setStyleSheet("color: red")
                return
            # Verificando se a quantidade de produtos vendidos é menor ou igual ao estoque
            for index, row in produtos.iterrows():
                # Soma a quantidade de um produto no carrinho, serve para evitar que um produto seja vendido em quantidade maior que a disponível
                quantidade_total_do_id = self.carrinho[self.carrinho["code"] == row["code"]]["quantity"].sum() 
                estoque = self.sales_processor.check_stock(row["code"], quantidade_total_do_id)
                if not estoque:
                    self.ui.error_registrar_venda_2.setText(f"Produto {row['code']} sem estoque suficiente, volte para a tela de registro de venda e remova o item")
                    self.ui.error_registrar_venda_2.setStyleSheet("color: red")
                    return
                
            profit = self.value_total - self.purchase_total
            # Processa a venda
            venda = self.sales_processor.create_sale(client_id=cliente, total_price=self.value_total, profit = profit, payment=int(self.payment_method), installment=int(self.installment), tax=float(self.taxa), discount=float(self.desconto))
            # Processa a venda de cada produto
            for index, row in produtos.iterrows():
                quantity = int(row["quantity"])
                self.sales_processor.process_sale(sale_id=venda, product_code=row["code"], quantity=quantity)
            # Mensagem de sucesso
            self.limpar_carrinhos()
            self.ui.stackedWidget.setCurrentWidget(self.ui.end_finish_payment)
        except Exception as e:
            # printando traceback
            traceback_print = traceback.format_exc()
            print(traceback_print)
        
    def buscar_estoque(self):
        nome = self.ui.lineEdit_buscar_estoque_nome.text()
        codigo = self.ui.lineEdit_buscar_estoque_codigo.text()
        produto = None
        # Se tiver código, buscar por ele primeiro
        produto_codigo = self.sales_processor.search_product(code=codigo)
        produto_nome = self.sales_processor.filter_product_name(name=nome)
        # Juntar os dois resultados
        if produto_codigo is not None and not produto_codigo.empty:
            produto = produto_codigo
        if produto_nome is not None and not produto_nome.empty:
            if produto is not None and not produto.empty:
                produto = pd.concat([produto, produto_nome])
            else:
                produto = produto_nome
        # Se não encontrar o produto, exibir mensagem de erro
        if produto is None or produto.empty:
            self.ui.error_buscar_estoque.setText("Produto não encontrado")
            self.ui.error_buscar_estoque.setStyleSheet("color: red")
            # limpar a tabela de estoque
            model = PandasModel(produto)
            self.ui.table_estoque.setModel(model)
            return
        # Renomear as colunas
        produto.columns = ["ID", "Nome", "Código", "Descrição", "Preço de Compra", "Preço de Venda", "Estoque"]
        # Atualiza a tabela de estoque
        model = PandasModel(produto)
        self.ui.table_estoque.setModel(model)
        self.ui.error_buscar_estoque.setText("")
        
    def editar_estoque(self):
        produto = self.produto
        
        nome = self.ui.lineEdit_add_name_produto_2.text()
        codigo = self.ui.lineEdit_add_codigo_produto_2.text()
        estoque = self.ui.lineEdit_add_estoque_2.text()
        descricao = self.ui.lineEdit_add_description_2.text()
        valor_compra = self.ui.lineEdit_add_valor_compra_2.text()
        valor_venda = self.ui.lineEdit_add_valor_venda_2.text()
        
        if nome == "" or codigo == "" or estoque == "" or valor_compra == "" or valor_venda == "":
            self.ui.error_cadastrar_produto_2.setText("Campos obrigatórios não preenchidos")
            return
        
        try:
            valor_venda = float(valor_venda)
            valor_compra = float(valor_compra)
            estoque = int(estoque)
        except:
            self.ui.error_cadastrar_produto_2.setText("Verifique os valores inseridos!")
            return
        
        # Atualiza o estoque do produto
        self.sales_processor.update_product(product_id=produto,name=nome, description=descricao, code=codigo, purchase_price=valor_compra, sale_price=valor_venda, stock=estoque)
        # Mensagem de sucesso
        self.ui.error_cadastrar_produto_2.setText("Produto atualizado com sucesso!")
        
    def limpar_carrinhos(self):
        # Limpa os carrinhos
        self.carrinho = pd.DataFrame(columns=["id","name", "code", "sale_price", "stock", "quantity", "purchase_price"])
        self.clientes = pd.DataFrame(columns=["id", "name", "cpf"])
        self.cliente = None
        self.value_total = 0
        self.payment_method = 0
        self.installment = 1
        self.taxa = 0
        # Atualiza a visualização do carrinho na QTableView
        tmp_carrinho = self.carrinho.copy()
        tmp_carrinho.columns = ["ID", "Nome", "Código", "Preço de Venda", "Estoque", "Quantidade", "Preço de Compra"]
        model = PandasModel(tmp_carrinho)
        self.ui.carrinho_table.setModel(model)
        self.ui.table_search_client_carrinho.setModel(model)
        self.ui.table_finalizar_venda.setModel(model)
        # Atualizando os valores na interface
        self.ui.label_qtd_itens_carrinho.setText("0")
        self.ui.label_valor_total_carrinho.setText("R$0.00")
        self.ui.label_qtd_itens_carrinho_2.setText("0")
        self.ui.label_valor_total_carrinho_2.setText("R$0.00")
        
    def clientes_table(self):
        '''
        Método para preencher a tabela de clientes
        '''
        todos_clientes = self.buscar_cliente(name="")
        # Preenchendo na tabela table_clientes
        self.ui.table_clientes.setModel(todos_clientes)
        # Mudando para página de clientes page_7_clientes
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_7_clientes)
        
    def edit_client(self):
        '''
        Método para editar um cliente
        '''
        # Implementar a edição de um cliente
        id = self.ui.lineEdit_buscar_cliente_id.text()
        # Buscar cliente por ID
        cliente = self.sales_processor.search_client_id(id)
        if cliente is None or cliente.empty:
            self.ui.error_buscar_cliente.setText("Cliente não encontrado")
            return
        # Preencher formulário e trocar de página
        self.ui.lineEdit_add_nome_cliente_2.setText(cliente["name"].iloc[0])
        self.ui.lineEdit_add_email_2.setText(cliente["email"].iloc[0])
        self.ui.lineEdit_add_cpf_2.setText(cliente["cpf"].iloc[0])
        self.ui.lineEdit_add_fone_2.setText(cliente["phone"].iloc[0])
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_10_editar_cliente)
        
    def delete_client(self):
        id = self.ui.lineEdit_buscar_cliente_id.text()
        self.sales_processor.delete_client(client_id=id)
        # Retorna para a página de clientes
        self.clientes_table()
    
    def save_cliente_edit(self):
        '''
        Método para salvar a edição de um cliente
        '''
        # Implementar a edição de um cliente
        id = self.ui.lineEdit_buscar_cliente_id.text()
        nome = self.ui.lineEdit_add_nome_cliente_2.text()
        email = self.ui.lineEdit_add_email_2.text()
        cpf = self.ui.lineEdit_add_cpf_2.text()
        fone = self.ui.lineEdit_add_fone_2.text()
        # Verificar se o nome está preenchido
        if nome == "":
            self.ui.error_cadastrar_client_2.setText("Campo obrigatório: Nome do Cliente não preenchido")
            return
        # Atualizar o cliente
        self.sales_processor.update_client(client_id=id, name=nome, email=email, cpf=cpf, phone=fone)
        # Mensagem de sucesso
        self.ui.error_cadastrar_client_2.setText("Cliente atualizado com sucesso!")
    
    def buscar_compra(self):
        # Carregando filtros
        cliente_id = self.ui.lineEdit_buscar_cliente_carrinho_2.text()
        compra_id = self.ui.lineEdit_buscar_id_compra.text()
        dateEdit = self.ui.dateEdit.text()
        dateEdit_2 = self.ui.dateEdit_2.text()
        
        # Iniciando o DataFrame de resultados como a tabela completa
        df_result = self.buscar_ultimas_compras
        
        # Aplicando o filtro de compra_id se não estiver vazio
        if compra_id != "":
            df_result = df_result[df_result["ID da Venda"] == int(compra_id)]
        
        # Aplicando o filtro de cliente_id se não estiver vazio
        if cliente_id != "":
            df_result = df_result[df_result["ID Cliente"] == int(cliente_id)]
        
        # Aplicando o filtro de dateEdit se não estiver vazio
        if dateEdit != "" and dateEdit_2 != "":
            # Datas no formato DD-MM-YYYY converter para YYYY-MM-DD
            dateEdit = datetime.strptime(dateEdit, "%d/%m/%Y").strftime("%Y-%m-%d")
            dateEdit_2 = datetime.strptime(dateEdit_2, "%d/%m/%Y").strftime("%Y-%m-%d")
            df_result = df_result[(df_result["Data da Venda"] >= dateEdit) & (df_result["Data da Venda"] <= dateEdit_2)]
        
        # Preenchendo a tabela table_compras com os resultados filtrados
        self.ui.table_ultimas_compras.setModel(PandasModel(df_result))
    
    def mostrar_compra(self):
        pass
        
    # Definindo Temas
    def default_theme(self, title_size="font-size: 42px;font-weight: bold;",font_color="color: white;border: 0;", background_centralwidget="background: #182625;", background_lineedit="background: rgba(6, 0, 0, 0.25);color: white;", cancel_button_style="font-weight: bold;background: yellow; color: black; border: 0; padding: 5px 10px; border-radius: 5px;", delete_button_style="font-weight: bold;background: #f44336; color: white; border: 0; padding: 5px 10px; border-radius: 5px;", finish_button_style="QPushButton{font-weight: bold;background: #4CAF50; color: white; border: 0; padding: 5px 10px; border-radius: 5px;}QPushButton:hover{background-color:#91B7D9;color:black;}"):
        
        menu_top_button = '''
        QPushButton
            {
            background: #3D5A73;
                font-weight: bold;
                border-radius: 0px 0px 0px 0px;
                border: 1px solid black;
                padding: 5px;
            }
            QPushButton:hover
            {
            background-color:#91B7D9;
                color: black;
            }
        '''
        
        self.ui.btn_menu_ccliente.setStyleSheet(f"{menu_top_button}")
        self.ui.btn_menu_cproduto.setStyleSheet(f"{menu_top_button}")
        self.ui.btn_menu_venda.setStyleSheet(f"{menu_top_button}")
        self.ui.btn_menu_estoque.setStyleSheet(f"{menu_top_button}")
        self.ui.btn_menu_clientes.setStyleSheet(f"{menu_top_button}")
        self.ui.btn_menu_relatorio.setStyleSheet(f"{menu_top_button}")
        self.ui.btn_menu_log.setStyleSheet(f"{menu_top_button}")
        self.ui.btn_menu_inicio.setStyleSheet(f"{menu_top_button}")
        
        
        # Cor de fundo do centralwidget
        self.ui.centralwidget.setStyleSheet(f"{background_centralwidget}")
        
        # Alterando o estilo dos botões de cancelar
        self.ui.btn_finalizar_venda_3.setStyleSheet(f"{cancel_button_style}")
        self.ui.btn_menu_cancel_insert_client_2.setStyleSheet(f"{cancel_button_style}")
        self.ui.btn_remover_carrinho.setStyleSheet(f"{cancel_button_style}")
        self.ui.btn_cancelar_op_cadastrar_produto.setStyleSheet(f"{cancel_button_style}")
        self.ui.btn_menu_cancel_insert_client.setStyleSheet(f"{cancel_button_style}")
        
        # Alterando o estilo dos botões de deletar
        self.ui.btn_deletar_cliente.setStyleSheet(f"{delete_button_style}")
        self.ui.btn_cancelar_venda.setStyleSheet(f"{delete_button_style}")
        self.ui.btn_cancelar_venda_2.setStyleSheet(f"{delete_button_style}")
        self.ui.btn_menu_cancel_insert_produto_2.setStyleSheet(f"{delete_button_style}")
        
        # Alterando o estilo dos botões de finalizar
        self.ui.btn_menu_insert_client_2.setStyleSheet(f"{finish_button_style}")
        self.ui.btn_finalizar_venda_2.setStyleSheet(f"{finish_button_style}")
        self.ui.btn_buscar_cliente_2.setStyleSheet(f"{finish_button_style}")
        self.ui.btn_menu_editar_produto.setStyleSheet(f"{finish_button_style}")
        self.ui.btn_buscar_estoque.setStyleSheet(f"{finish_button_style}")
        self.ui.btn_add_carrinho.setStyleSheet(f"{finish_button_style}")
        self.ui.btn_finalizar_venda.setStyleSheet(f"{finish_button_style}")
        self.ui.btn_menu_insert_produto.setStyleSheet(f"{finish_button_style}")
        self.ui.btn_menu_insert_client.setStyleSheet(f"{finish_button_style}")
        self.ui.btn_menu_insert_produto_2.setStyleSheet(f"{finish_button_style}")
        self.ui.btn_menu_editar_cliente.setStyleSheet(f"{finish_button_style}")
        
        # Loading Page
        self.ui.label_loading_page.setStyleSheet(f"{font_color}{title_size}")
        
        # Cores da página de cadastrar cliente
        self.ui.label_nome_completo.setStyleSheet(f"{font_color}")
        self.ui.label_email.setStyleSheet(f"{font_color}")
        self.ui.label_cpf.setStyleSheet(f"{font_color}")
        self.ui.label_fone.setStyleSheet(f"{font_color}")
        self.ui.label_title_ccliente.setStyleSheet(f"{font_color}{title_size}")
        self.ui.lineEdit_add_nome_cliente.setStyleSheet(f"{background_lineedit}")
        self.ui.lineEdit_add_email.setStyleSheet(f"{background_lineedit}")
        self.ui.lineEdit_add_cpf.setStyleSheet(f"{background_lineedit}")
        self.ui.lineEdit_add_fone.setStyleSheet(f"{background_lineedit}")
        # Cores da página de cadastrar produto
        self.ui.label_nome_do_produto.setStyleSheet(f"{font_color}")
        self.ui.label_descricao_do_produto.setStyleSheet(f"{font_color}")
        self.ui.label_codigo.setStyleSheet(f"{font_color}")
        self.ui.label_valor_compra.setStyleSheet(f"{font_color}")
        self.ui.label_valor_venda.setStyleSheet(f"{font_color}")
        self.ui.label_estoque_inicial.setStyleSheet(f"{font_color}")
        self.ui.lineEdit_add_name_produto.setStyleSheet(f"{background_lineedit}")
        self.ui.lineEdit_add_description.setStyleSheet(f"{background_lineedit}")
        self.ui.lineEdit_add_codigo_produto.setStyleSheet(f"{background_lineedit}")
        self.ui.lineEdit_add_valor_compra.setStyleSheet(f"{background_lineedit}")
        self.ui.lineEdit_add_valor_venda.setStyleSheet(f"{background_lineedit}")
        self.ui.lineEdit_add_estoque.setStyleSheet(f"{background_lineedit}")
        # Cores da página de registrar venda
        ''' Titulos '''
        self.ui.label_title_pagina_inicial.setStyleSheet(f"{font_color}{title_size}")
        self.ui.label_title_novo_produto_3.setStyleSheet(f"{font_color}{title_size}")
        self.ui.label_title_carrinho.setStyleSheet(f"{font_color}{title_size}")
        self.ui.label_qtd_itens_carrinho.setStyleSheet(f"{font_color}{title_size}")
        self.ui.label_qtd_itens_total.setStyleSheet(f"{font_color}{title_size}")
        self.ui.label_valor_total_carrinho.setStyleSheet(f"{font_color}{title_size}")
        self.ui.label_valor_total.setStyleSheet(f"{font_color}{title_size}")
        
        self.ui.label_cod_produto_carrinho.setStyleSheet(f"{font_color}")
        self.ui.label_qtd_itens.setStyleSheet(f"{font_color}")
        self.ui.lineEdit_cod_produto_carrinho.setStyleSheet(f"{background_lineedit}")
        self.ui.lineEdit_qtd_produto_carrinho_2.setStyleSheet(f"{background_lineedit}")
        self.ui.label_id_produto.setStyleSheet(f"{font_color}")
        self.ui.lineEdit_id_remove_carrinho.setStyleSheet(f"{background_lineedit}")
        
        # Método de Pagamento ( selecionar )
        self.ui.label_payment_method_title.setStyleSheet(f"{font_color}{title_size}")
        self.ui.money_btn.setStyleSheet(f"{finish_button_style}")
        self.ui.credit_btn.setStyleSheet(f"{finish_button_style}")
        self.ui.debit_btn.setStyleSheet(f"{finish_button_style}")
        self.ui.pix_btn.setStyleSheet(f"{finish_button_style}")
        
        
        # Finalizar Pagamento
        self.ui.label_finish_nome_cliente.setStyleSheet(f"{font_color}")
        self.ui.label_adicionar_taxa.setStyleSheet(f"{font_color}")
        self.ui.label_valor_total_compra.setStyleSheet(f"{font_color}")
        self.ui.label_metodo_pagamento.setStyleSheet(f"{font_color}")
        self.ui.label_valor_recebido.setStyleSheet(f"{font_color}")
        self.ui.label_troco.setStyleSheet(f"{font_color}")
        self.ui.label_parcelas.setStyleSheet(f"{font_color}")
        self.ui.label_insert_nome_cliente.setStyleSheet(f"{font_color}")
        self.ui.label_metodo_pagamento_2.setStyleSheet(f"{font_color}")
        self.ui.label_valor_total_3.setStyleSheet(f"{font_color}")
        self.ui.lineEdit_adicionar_parcelas.setStyleSheet(f"{background_lineedit}")
        self.ui.label_result_troco.setStyleSheet(f"{font_color}")
        
        self.ui.title_op_realizada.setStyleSheet(f"{font_color}{title_size}")
        
        self.ui.btn_add_taxa.setStyleSheet(f"{finish_button_style}")
        self.ui.btn_add_desconto.setStyleSheet(f"{finish_button_style}")
        self.ui.btn_add_parcela.setStyleSheet(f"{finish_button_style}")
        
        self.ui.label_adicionar_desconto.setStyleSheet(f"{font_color}")
        
        self.ui.lineEdit_adicionar_desconto.setStyleSheet(f"{background_lineedit}")
        self.ui.lineEdit_adicionar_taxa.setStyleSheet(f"{background_lineedit}")
        self.ui.lineEdit_valor_recebido.setStyleSheet(f"{background_lineedit}")
        
        self.ui.label_6.setStyleSheet(f"{font_color}")
        self.ui.label_7.setStyleSheet(f"{font_color}")
        self.ui.dateEdit_9.setStyleSheet(f"{background_lineedit}")
        self.ui.dateEdit_10.setStyleSheet(f"{background_lineedit}")
        
        table_style = """
            QTableView {
                background-color: white;
                gridline-color: white;
                border: 1px solid black;
                color: black;
                font-weight: bold;
                
            }
            QHeaderView::section {
                color: white;
                padding: 4px;
                font-weight: bold;
                border: 1px solid black;
                background-color: black;
            }
            QTableView::item {
                padding: 4px;
            }
        """
        
        ''' TABELAS '''
        self.ui.table_log.setStyleSheet(table_style)
        self.ui.table_search_client_carrinho.setStyleSheet(table_style)
        self.ui.table_ultimas_compras.setStyleSheet(table_style)
        
        
        self.ui.carrinho_table.setStyleSheet(table_style)
        
        
        self.ui.label_qtd_itens_total_2.setStyleSheet(f"{font_color}{title_size}")
        self.ui.label_qtd_itens_carrinho_2.setStyleSheet(f"{font_color}{title_size}")
        
        self.ui.label_valor_total_2.setStyleSheet(f"{font_color}{title_size}")
        self.ui.label_valor_total_carrinho_2.setStyleSheet(f"{font_color}{title_size}")
        
        self.ui.label_buscar_cliente.setStyleSheet(f"{font_color}")
        self.ui.lineEdit_buscar_cliente_carrinho.setStyleSheet(f"{background_lineedit}")
        
        self.ui.label_title_cliente_2.setStyleSheet(f"{font_color}{title_size}")
        
        self.ui.error_registrar_venda_2.setStyleSheet(f"{font_color}")
        
        self.ui.table_finalizar_venda.setStyleSheet(table_style)
        
        self.ui.table_parcelas.setStyleSheet(table_style)
        
        # Cores da página de controle de estoque
        self.ui.label_title_produto_estoque.setStyleSheet(f"{font_color}{title_size}")
        self.ui.label_nome_produto_estoque.setStyleSheet(f"{font_color}")
        self.ui.lineEdit_buscar_estoque_nome.setStyleSheet(f"{background_lineedit}")
        
        self.ui.label_nome_codigo_estoque.setStyleSheet(f"{font_color}")
        self.ui.lineEdit_buscar_estoque_codigo.setStyleSheet(f"{background_lineedit}")
        
        self.ui.table_estoque.setStyleSheet(table_style)
        
        self.ui.label_id_cliente_busca.setStyleSheet(f"{font_color}")
        self.ui.label_nome_cliente_busca.setStyleSheet(f"{font_color}")
        
        self.ui.lineEdit_buscar_cliente_id.setStyleSheet(f"{background_lineedit}")
        self.ui.lineEdit_buscar_cliente_nome.setStyleSheet(f"{background_lineedit}")
        self.ui.table_clientes.setStyleSheet(table_style)
        self.ui.error_buscar_cliente.setStyleSheet(f"{font_color}")
        
        self.ui.label_nome_completo_2.setStyleSheet(f"{font_color}")
        self.ui.label_email_2.setStyleSheet(f"{font_color}")
        self.ui.label_cpf_2.setStyleSheet(f"{font_color}")
        self.ui.label_fone_2.setStyleSheet(f"{font_color}")
        self.ui.lineEdit_add_nome_cliente_2.setStyleSheet(f"{background_lineedit}")
        self.ui.lineEdit_add_email_2.setStyleSheet(f"{background_lineedit}")
        self.ui.lineEdit_add_cpf_2.setStyleSheet(f"{background_lineedit}")
        self.ui.lineEdit_add_fone_2.setStyleSheet(f"{background_lineedit}")
        self.ui.error_cadastrar_client_2.setStyleSheet(f"{font_color}")
        
        # Página para editar produto
        self.ui.label_title_edit_produto_2.setStyleSheet(f"{font_color}{title_size}")
        self.ui.label_nome_do_produto_2.setStyleSheet(f"{font_color}")
        self.ui.label_descricao_do_produto_2.setStyleSheet(f"{font_color}")
        self.ui.label_codigo_2.setStyleSheet(f"{font_color}")
        self.ui.label_valor_compra_2.setStyleSheet(f"{font_color}")
        self.ui.label_valor_venda_2.setStyleSheet(f"{font_color}")
        self.ui.label_estoque_inicial_2.setStyleSheet(f"{font_color}")
        self.ui.lineEdit_add_name_produto_2.setStyleSheet(f"{background_lineedit}")
        self.ui.lineEdit_add_description_2.setStyleSheet(f"{background_lineedit}")
        self.ui.lineEdit_add_codigo_produto_2.setStyleSheet(f"{background_lineedit}")
        self.ui.lineEdit_add_valor_compra_2.setStyleSheet(f"{background_lineedit}")
        self.ui.lineEdit_add_valor_venda_2.setStyleSheet(f"{background_lineedit}")
        self.ui.lineEdit_add_estoque_2.setStyleSheet(f"{background_lineedit}")
        
        # Filtro do plot
        self.ui.label_filtro_data.setStyleSheet(f"{font_color}")
        self.ui.label_de.setStyleSheet(f"{font_color}")
        self.ui.label_ate.setStyleSheet(f"{font_color}")
        self.ui.dateEdit_3.setStyleSheet(f"{background_lineedit}")
        self.ui.dateEdit_4.setStyleSheet(f"{background_lineedit}")
        self.ui.btn_filter_plot_products.setStyleSheet(f"{finish_button_style}")
        
        
        
        

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()