# pdf_gerador3.py

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import logging
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# Configurar o logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def gerar_pdf_variacao_diaria(output_file="Variação_Diária.pdf"):
    ativos_descricao = {
        'USDBRL=X': 'USD/BRL',
        'USDMXN=X': 'USD/MXN',
        '^BVSP': 'Bovespa',
        'VALE3.SA': 'Vale S.A.',
        'PETR4.SA': 'Petrobras (PN)',
        'ITUB4.SA': 'Itaú Unibanco (PN)',
        'BBDC4.SA': 'Bradesco (PN)',
        'ABEV3.SA': 'Ambev (ON)',
        'WEGE3.SA': 'Weg (ON)',
        'SMAL11.SA': 'Índice Small Cap',
        'USDJPY=X': 'USD/JPY',
        '^TNX': 'Treasury - 10 anos',
        '^GSPC': 'S&P 500',
        '^STOXX50E': 'Euro Stoxx 50',
        '^N225': 'Nikkei 225',
        '^GDAXI': 'DAX',
        '^FTSE': 'FTSE 100',
        'USDEUR=X': 'USD/EUR', 
        'USDGBP=X': 'USD/GBP', 
        'USDCAD=X': 'USD/CAD',	
        'USDCNY=X': 'USD/CNY',
        '^HSI': 'Hang Seng Index',
        '^AORD': 'ASX 200',
        '^MXX': 'Índice IPC (México)',
        'GC=F': 'Ouro (Gold)',
        'CL=F': 'Petróleo WTI',
        'SI=F': 'Prata (Silver)',
        'HG=F': 'Cobre (Copper)',
        'ZC=F': 'Milho (Corn)',
        'TIO=F': 'Minério de Ferro'
    }

    tickers = [
        'USDBRL=X', 'USDMXN=X', '^BVSP', 'VALE3.SA', 'PETR4.SA', 'ITUB4.SA', 'BBDC4.SA', 
        'ABEV3.SA', 'WEGE3.SA', 'SMAL11.SA', 'USDJPY=X', '^TNX', '^GSPC', '^STOXX50E', 
        '^N225', '^GDAXI', '^FTSE', 'USDEUR=X', 'USDGBP=X', 'USDAUD=X', 'USDCAD=X', 
        'USDCHF=X', 'USDCNY=X', '^HSI', '^AORD', '^MXX', 'GC=F', 'CL=F', 'SI=F', 
        'HG=F', 'ZC=F', 'TIO=F'
    ]

    # Categorias de ativos
    bolsas = ['^BVSP', '^GSPC', '^STOXX50E', '^N225', '^GDAXI', '^FTSE', '^HSI', '^AORD', '^MXX']
    moedas = ['USDBRL=X', 'USDMXN=X', 'USDJPY=X', 'USDEUR=X', 'USDGBP=X', 'USDCAD=X']
    commodities = ['GC=F', 'CL=F', 'SI=F', 'HG=F', 'ZC=F', 'TIO=F']

    def calcular_variacao(tickers, periodo='5d'):
        try:
            # Baixar os dados
            dados = yf.download(tickers, period=periodo, interval='1d')['Close']
            # Verificar se há pelo menos duas linhas de dados
            if dados.shape[0] < 2:
                logging.warning(f"Não há dados suficientes para os tickers: {tickers}")
                return pd.Series(dtype=float), None
            
            # Calcular variação
            variacao = (dados.iloc[-1] - dados.iloc[-2]) / dados.iloc[-2] * 100
            variacao = variacao.dropna()
    
            # Logar os tickers com dados válidos e os que foram ignorados
            logging.info(f"Tickers com dados válidos: {list(variacao.index)}")
            tickers_ignorados = set(tickers) - set(variacao.index)
            if tickers_ignorados:
                logging.warning(f"Tickers sem dados ou ignorados: {tickers_ignorados}")
    
            # Obter a data da última variação
            data_var = dados.index[-1].strftime('%d/%m/%Y')
    
            return variacao, data_var
        except Exception as e:
            logging.error(f"Erro ao baixar dados para os tickers {tickers}: {e}")
            return pd.Series(dtype=float), None

    def plotar_variacao(variacao, titulo, ax, categoria):
        sns.set(style="whitegrid")
        sns.set_palette("muted")
        
        if variacao.empty:
            ax.text(0.5, 0.5, 'Nenhum dado disponível.', 
                    horizontalalignment='center', verticalalignment='center', 
                    fontsize=14, color='red')
            ax.axis('off')
            return

        descricao = [ativos_descricao.get(ticker, ticker) for ticker in variacao.index]
        valores = variacao.values

        # Definir cores baseadas no sinal da variação
        colors = ['#28a745' if v > 0 else '#dc3545' for v in valores]  # Verde para positivo, Vermelho para negativo

        bars = ax.bar(descricao, valores, color=colors)

        # Adicionar rótulos de valor nas barras
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 pontos de deslocamento para cima
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=10, color='black', fontweight='bold')

        ax.axhline(0, color='black', linewidth=0.8)
        ax.set_title(titulo, fontsize=16, fontweight='bold', color='#333333')
        ax.set_ylabel('Variação (%)', fontsize=14, color='#333333')
        ax.tick_params(axis='x', rotation=45, labelsize=12)
        ax.tick_params(axis='y', labelsize=12)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    # Calcular variação para cada categoria
    variacao_moedas, data_var_moedas = calcular_variacao(moedas, periodo='5d')
    variacao_bolsas, data_var_bolsas = calcular_variacao(bolsas, periodo='5d')
    variacao_commodities, data_var_commodities = calcular_variacao(commodities, periodo='5d')

    # Determinar a data mais recente entre as categorias
    datas = [data for data in [data_var_moedas, data_var_bolsas, data_var_commodities] if data]
    data_geracao = max(datas) if datas else datetime.now().strftime('%d/%m/%Y')

    # Gerar gráficos e salvar no PDF
    with PdfPages(output_file) as pdf:
        # Configuração geral do estilo
        sns.set(style="whitegrid")
        plt.rcParams.update({
            'font.size': 12,
            'font.family': 'sans-serif',
            'axes.titlesize': 16,
            'axes.labelsize': 14,
            'xtick.labelsize': 12,
            'ytick.labelsize': 12,
            'figure.figsize': (12, 8),
            'figure.facecolor': '#ffffff',
            'axes.facecolor': '#f9f9f9'
        })

        fig, axs = plt.subplots(3, 1, figsize=(14, 20))

        plotar_variacao(variacao_moedas, f'Variação Diária - Moedas ({data_geracao})', axs[0], 'Moedas')
        plotar_variacao(variacao_bolsas, f'Variação Diária - Bolsas ({data_geracao})', axs[1], 'Bolsas')
        plotar_variacao(variacao_commodities, f'Variação Diária - Commodities ({data_geracao})', axs[2], 'Commodities')

        plt.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

    logging.info(f'PDF gerado com sucesso: {output_file}')

if __name__ == "__main__":
    gerar_pdf_variacao_diaria()
