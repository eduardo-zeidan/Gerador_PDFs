# pdf_gerador3.py

import matplotlib
matplotlib.use('Agg')  # Define o backend para 'Agg' antes de importar pyplot

import pandas as pd
import yfinance as yf
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import itertools
from scipy.stats import zscore
from datetime import datetime
import warnings
import matplotlib.colors as mcolors
import logging

# Suprimir avisos desnecessários
warnings.filterwarnings('ignore')

def gerar_pdf(output_file="Regressão_Pares_Ativos.pdf"):
    plt.style.use('ggplot')
    
    # Configurar o logging para facilitar o debug
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # Descrição amigável dos ativos
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
        # '000001.SS' removido anteriormente
    }

    # Definir lista completa de tickers sem '000001.SS'
    tickers = [
        'USDBRL=X', 'USDMXN=X', '^BVSP', 'VALE3.SA', 'PETR4.SA', 'ITUB4.SA', 'BBDC4.SA', 
        'ABEV3.SA', 'WEGE3.SA', 'SMAL11.SA', 'USDJPY=X', '^TNX', '^GSPC', '^STOXX50E', 
        '^N225', '^GDAXI', '^FTSE', 'USDEUR=X', 'USDGBP=X', 'USDAUD=X', 'USDCAD=X', 
        'USDCHF=X', 'USDCNY=X', '^HSI', '^AORD', '^MXX', 'GC=F', 'CL=F', 'SI=F', 
        'HG=F', 'ZC=F', 'TIO=F'
        # '000001.SS' removido
    ]

    bolsas = ['^BVSP', '^GSPC', '^STOXX50E', '^N225', '^GDAXI', '^FTSE', '^HSI', '^AORD', '^MXX']
    moedas = ['USDBRL=X', 'USDMXN=X', 'USDJPY=X', 'USDEUR=X', 'USDGBP=X', 'USDCAD=X']
    commodities = ['GC=F', 'CL=F', 'SI=F', 'HG=F', 'ZC=F', 'TIO=F']
    t10 = '^TNX'
    ibov = '^BVSP'

    # Estrutura os pares para regressão
    regression_pairs = (
        [(moeda, 'USDBRL=X') for moeda in moedas if moeda != 'USDBRL=X'] + 
        [('^BVSP', bolsa) for bolsa in bolsas if bolsa != '^BVSP'] + 
        [(t10, bolsa) for bolsa in bolsas] + 
        [(t10, moeda) for moeda in moedas] + 
        [(commodity1, commodity2) for commodity1, commodity2 in itertools.combinations(commodities, 2)] + 
        [(ibov, commodity) for commodity in commodities] + 
        [('^BVSP', 'USDBRL=X')]  # Incluindo o par específico para USD/BRL e Bovespa
    )

    def load_data(tickers, start_date, end_date):
        logging.info(f"Baixando dados de {len(tickers)} tickers de {start_date} até {end_date}...")
        
        # Baixa todos os tickers de uma vez
        try:
            data = yf.download(tickers, start=start_date, end=end_date, progress=False, group_by='ticker', threads=True)
        except Exception as e:
            logging.error(f"Erro ao baixar dados: {e}")
            return None, tickers  # Retorna todos os tickers como falhos
        
        successful_tickers = []
        failed_tickers = []
        close_data = {}
        
        # Processa os dados retornados
        for ticker in tickers:
            try:
                if len(tickers) == 1:
                    # Caso haja apenas um ticker, a estrutura dos dados é diferente
                    temp_close = data['Close']
                else:
                    temp_close = data[ticker]['Close']
                
                if temp_close.isnull().all():
                    failed_tickers.append(ticker)
                    logging.warning(f"Sem dados válidos para {ticker}.")
                else:
                    close_data[ticker] = temp_close
                    successful_tickers.append(ticker)
                    logging.info(f"Sucesso: {ticker} - {temp_close.count()} registros.")
            except KeyError:
                failed_tickers.append(ticker)
                logging.warning(f"Sem dados para {ticker}.")
        
        if not close_data:
            raise ValueError("Nenhum ativo retornou dados válidos.")
        
        # Cria o DataFrame alinhando os índices
        df = pd.DataFrame(close_data)
        df = df.dropna(how='all')  # Remove linhas onde todos os valores são NaN
        
        logging.info(f"Total de tickers com dados válidos: {len(successful_tickers)}")
        logging.info(f"Tickers sem dados ou com erro: {len(failed_tickers)}")
        logging.info(f"Tickers sem dados: {failed_tickers}\n")
        
        return df, failed_tickers

    # Função para realizar a regressão linear e calcular R²
    def perform_regression(df, x_column, y_column, N=600):
        pair_df = df[[x_column, y_column]].dropna()
        if pair_df.empty:
            logging.warning(f"Sem dados para regressão entre {x_column} e {y_column}.")
            return None, None, None
        
        pair_df = pair_df.sort_index()
        if len(pair_df) > N:
            pair_df = pair_df.iloc[-N:]
        
        X = pair_df[[x_column]].values
        Y = pair_df[y_column].values
        
        linear_model = LinearRegression()
        linear_model.fit(X, Y)
        y_pred = linear_model.predict(X)
        r2 = r2_score(Y, y_pred)
        
        pair_df['residual'] = Y - y_pred
        pair_df['residual_standardized'] = zscore(pair_df['residual'])
        
        return linear_model, r2, pair_df

    # Função para criar gráficos e salvar no PDF
    def plot_results_to_pdf(pdf, df, x_column, y_column, r2):
        residuals_standardized = df['residual_standardized']
        std_residuals = np.std(residuals_standardized)
        
        plt.figure(figsize=(12, 6))
        
        plt.plot(df.index, residuals_standardized, label='Resíduo Padronizado', color='blue', linewidth=1.5)
        plt.fill_between(df.index, -1.5 * std_residuals, 1.5 * std_residuals, 
                        color='lightcoral' if r2 < 0.1 else 'lightgreen', alpha=0.3, label='Intervalo de 1.5dp')
        plt.axhline(0, color='red', linestyle='--', linewidth=1.5)
        
        title_color = 'red' if r2 < 0.1 else 'black'
        plt.title(f'{ativos_descricao.get(y_column, y_column)} vs {ativos_descricao.get(x_column, x_column)}', 
                fontsize=16, weight='bold', color=title_color)
        plt.suptitle(f'Resíduo da Regressão de {ativos_descricao.get(y_column, y_column)} sendo explicado por {ativos_descricao.get(x_column, x_column)}\n'
                f'R² = {r2:.4f}, Amostra = {len(df)} dias, Última Data = {df.index[-1].strftime("%Y-%m-%d")}', 
                fontsize=12)
        
        plt.xlabel('Data')
        plt.ylabel('Resíduo Padronizado (%)')
        plt.legend(loc='upper right', fontsize=8)
        
        y_min, y_max = residuals_standardized.min(), residuals_standardized.max()
        plt.ylim(y_min - 0.5, y_max + 0.5)
        
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        plt.annotate("FIM J&F Disciplina / Mesa Quant - Eduardo Zeidan", 
                    xy=(1, 0), xycoords='axes fraction', fontsize=8, color='gray', ha='right', va='bottom')
        
        pdf.savefig()
        plt.close()

    def add_grid_table_with_gradient_to_pdf(pdf, residuals_table):
        # Ordenar a tabela por 'Resíduo Mais Recente' para melhor visualização
        residuals_table = residuals_table.sort_values('Resíduo Mais Recente')
        
        # Criar a figura e o eixo principal
        fig, ax = plt.subplots(figsize=(12, 8))  # Reduzir o tamanho da figura
        ax.axis('off')
        
        # Definir o gradiente de azul claro para branco e amarelo
        cmap = mcolors.LinearSegmentedColormap.from_list("blue_white_yellow", ["#add8e6", "white", "#ffff00"])
        norm = plt.Normalize(residuals_table['Resíduo Mais Recente'].min(), residuals_table['Resíduo Mais Recente'].max())
        
        # Ajustar o número de colunas e linhas para uma tabela mais compacta
        num_cols = 5
        num_rows = (len(residuals_table) + num_cols - 1) // num_cols
        
        block_width = 0.7  # Reduzir a largura dos blocos
        block_height = 0.7  # Reduzir a altura dos blocos
        
        for idx, (i, j) in enumerate(itertools.product(range(num_rows), range(num_cols))):
            if idx < len(residuals_table):
                pair = residuals_table.iloc[idx]
                pair_name = pair['Comparação']
                pair_residual = pair['Resíduo Mais Recente']
                color = cmap(norm(pair_residual))
                
                y_pos = (num_rows - 1 - i) * block_height  # Posicionar de cima para baixo
                
                # Desenhar o retângulo
                ax.add_patch(plt.Rectangle((j * block_width, y_pos), block_width, block_height, 
                                        color=color, linewidth=1, edgecolor='black'))
                
                # Ajustar a cor do texto para garantir legibilidade
                text_color = 'black' 
                
                # Adicionar o nome do par de ativos
                ax.text(j * block_width + block_width / 2, y_pos + block_height * 0.6, pair_name, 
                        ha='center', va='center', fontsize=6, color=text_color, fontweight='bold', wrap=True)
                
                # Adicionar o valor do resíduo
                ax.text(j * block_width + block_width / 2, y_pos + block_height * 0.3, f"{pair_residual:.2f}", 
                        ha='center', va='center', fontsize=8, color=text_color, fontweight='bold')
        
        # Ajustar os limites do gráfico
        plt.xlim(0, num_cols * block_width)
        plt.ylim(0, num_rows * block_height)
        plt.tight_layout()

        # Adicionar o título fora do gráfico, na parte superior branca, com mais espaço entre o título e a tabela
        fig.text(0.5, 0.98, "Destaques diários | 15 maiores & 15 menores resíduos", 
                ha='center', va='top', fontsize=12, fontweight='bold')

        # Adicionar a assinatura no canto inferior direito
        fig.text(0.99, 0.01, "FIM J&F Disciplina / Mesa Quant - Eduardo Zeidan", 
                ha='right', va='center', fontsize=9, color='gray')

        # Salvar o gráfico e a assinatura no PDF
        pdf.savefig()
        plt.close()

    # Função principal para gerar o PDF
    def main():
        nonlocal tickers  # Permite modificar a variável 'tickers' definida no escopo externo

        # Definir intervalo de datas para regressão
        end_date = datetime.today() - pd.DateOffset(days=1)  # Define end_date para ontem
        start_date = end_date - pd.DateOffset(years=1)

        logging.info(f"Intervalo de datas: {start_date.strftime('%Y-%m-%d')} até {end_date.strftime('%Y-%m-%d')}\n")

        # Carregar os dados
        try:
            df, failed_tickers = load_data(tickers, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        except ValueError as ve:
            logging.error(f"[Erro] {ve}")
            # Opcional: Remova tickers problemáticos ou ajuste a lista conforme necessário
            # Por exemplo, remover 'TIO=F' se persistir o erro
            problematic_tickers = ['TIO=F']  # Adicione outros tickers problemáticos aqui
            for ticker in problematic_tickers:
                if ticker in tickers:
                    tickers.remove(ticker)
                    logging.info(f"Removido ticker problemático: {ticker}")
            # Recarregar os dados com a lista ajustada
            df, failed_tickers = load_data(tickers, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

        # Remover todos os tickers que falharam
        if failed_tickers:
            logging.info("Removendo tickers que falharam no download: %s", failed_tickers)
            tickers = [ticker for ticker in tickers if ticker not in failed_tickers]
            df, _ = load_data(tickers, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

        pdf_filename = output_file

        pair_results = []
        N = 756  # Número máximo de dias para a regressão

        logging.info("\nIniciando regressões...\n")

        for ticker1, ticker2 in regression_pairs:
            if ticker1 not in df.columns or ticker2 not in df.columns:
                logging.warning(f"Pular par ({ticker1}, {ticker2}) pois um dos tickers não possui dados.")
                continue
            
            model, r2, df_res = perform_regression(df, ticker1, ticker2, N=N)
            
            if df_res is None:
                continue

            pair_results.append({
                'ticker1': ticker1,
                'ticker2': ticker2,
                'df_res': df_res,
                'r2': r2
            })

        # Verificar se há resultados de regressão
        if not pair_results:
            raise ValueError("Nenhum par de regressão foi processado com sucesso.")

        # Criar a tabela de resíduos
        residuals_table = pd.DataFrame({
            'Comparação': [
                f"{ativos_descricao.get(result['ticker2'], result['ticker2'])} vs {ativos_descricao.get(result['ticker1'], result['ticker1'])}"
                for result in pair_results
            ],
            'Resíduo Mais Recente': [round(result['df_res']['residual_standardized'].iloc[-1], 2) for result in pair_results]
        })

        # Selecionar os 15 maiores e 15 menores resíduos
        top_maiores = residuals_table.nlargest(15, 'Resíduo Mais Recente')
        top_menores = residuals_table.nsmallest(15, 'Resíduo Mais Recente')
        top_residuos = pd.concat([top_maiores, top_menores])

        # Gerar o PDF
        with PdfPages(pdf_filename) as pdf:
            # Adicionar a tabela de resíduos com gradiente
            add_grid_table_with_gradient_to_pdf(pdf, top_residuos)
            
            # Adicionar os gráficos de resíduos para cada par
            for result in pair_results:
                ticker1 = result['ticker1']
                ticker2 = result['ticker2']
                df_res = result['df_res']
                r2 = result['r2']

                plot_results_to_pdf(pdf, df_res, ticker1, ticker2, r2)

        logging.info(f"\nPDF gerado com sucesso: {pdf_filename}")

        # Retornar o caminho do PDF gerado
        return pdf_filename

    # Executar a função principal e retornar o caminho do PDF
    return main()
