# pdf_gerador3.py

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
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
                return pd.Series(dtype=float)
            
            # Calcular variação
            variacao = (dados.iloc[-1] - dados.iloc[-2]) / dados.iloc[-2] * 100
            variacao = variacao.dropna()

            # Logar os tickers com dados válidos e os que foram ignorados
            logging.info(f"Tickers com dados válidos: {list(variacao.index)}")
            tickers_ignorados = set(tickers) - set(variacao.index)
            if tickers_ignorados:
                logging.warning(f"Tickers sem dados ou ignorados: {tickers_ignorados}")

            return variacao
        except Exception as e:
            logging.error(f"Erro ao baixar dados para os tickers {tickers}: {e}")
            return pd.Series(dtype=float)

    def plotar_variacao(variacao, titulo, ax):
        ativos = variacao.index
        valores = variacao.values

        if variacao.empty:
            ax.text(0.5, 0.5, 'Nenhum dado disponível.', 
                    horizontalalignment='center', verticalalignment='center', 
                    fontsize=12, color='red')
            ax.axis('off')
        else:
            descricao = [ativos_descricao.get(ticker, ticker) for ticker in ativos]
            ax.bar(descricao, valores, color=['green' if v > 0 else 'red' for v in valores])
            ax.axhline(0, color='black', linestyle='--', linewidth=0.8)
        
        ax.set_title(titulo, fontsize=14)
        ax.set_ylabel('Variação (%)', fontsize=12)
        ax.tick_params(axis='x', rotation=45, labelsize=10)

    # Calcular variação
    variacao_moedas = calcular_variacao(moedas, periodo='5d')
    variacao_bolsas = calcular_variacao(bolsas, periodo='5d')
    variacao_commodities = calcular_variacao(commodities, periodo='5d')

    # Gerar gráficos e salvar no PDF
    with PdfPages(output_file) as pdf:
        fig, axs = plt.subplots(3, 1, figsize=(12, 18))

        plotar_variacao(variacao_moedas, 'Variação Diária - Moedas', axs[0])
        plotar_variacao(variacao_bolsas, 'Variação Diária - Bolsas', axs[1])
        plotar_variacao(variacao_commodities, 'Variação Diária - Commodities', axs[2])

        plt.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

    logging.info(f'PDF gerado com sucesso: {output_file}')

if __name__ == "__main__":
    gerar_pdf_variacao_diaria()


    # Executar a função principal e retornar o caminho do PDF
    return main()
