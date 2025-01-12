# pdf_gerador2.py

import yfinance as yf
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.colors as mcolors
from matplotlib.backends.backend_pdf import PdfPages
import logging
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

def gerar_pdf(output_file="Análise_Z-Score_Carteiras.pdf"):
    # Configurar o logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # Definir as carteiras com nomes amigáveis em português
    carteira_bolsas = {
        '^GSPC': 'S&P 500 (EUA)',
        '^DJI': 'Dow Jones (EUA)',
        '^IXIC': 'Nasdaq (EUA)',
        '^FTSE': 'FTSE 100 (Reino Unido)',
        '^N225': 'Nikkei 225 (Japão)',
        '^HSI': 'Hang Seng (Hong Kong)',
        '^BVSP': 'Ibovespa (Brasil)',
        '^STOXX50E': 'Euro Stoxx 50 (Zona do Euro)',
        '^GDAXI': 'DAX (Alemanha)',
        '^RUT': 'Russell 2000 (EUA)',
        '^AORD': 'S&P/ASX 200 (Austrália)',
        '^FCHI': 'CAC 40 (França)',
        '^KS11': 'KOSPI (Coreia do Sul)',
        '^BSESN': 'BSE Sensex (Índia)',
        '^BFX': 'BEL 20 (Bélgica)',
        '^MERV': 'Merval (Argentina)',
        '^TWII': 'TSEC (Taiwan)',
        '^TA125.TA': 'TA-125 (Israel)',
        '^MXX': 'IPC (México)',
        '000001.SS': 'Xangai (China)',
    }

    carteira_commodities = {
        'CL=F': 'Petróleo WTI',
        'GC=F': 'Ouro',
        'SI=F': 'Prata',
        'HG=F': 'Cobre',
        'NG=F': 'Gás Natural',
        'ZC=F': 'Milho',
        'ZW=F': 'Trigo',
        'KC=F': 'Café',
        'CT=F': 'Algodão',
        'SB=F': 'Açúcar',
        'PA=F': 'Paládio',
        'PL=F': 'Platina',
        'HO=F': 'Óleo de Aquecimento',
        'RB=F': 'Gasolina',
        'OJ=F': 'Suco de Laranja',
        'CC=F': 'Cacau',
        'ZS=F': 'Soja (CBOT)',
        'ZM=F': 'Farelo de Soja',
        'LE=F': 'Boi Gordo',
        'HE=F': 'Suínos Magros',
        'BZ=F': 'Petróleo Brent',
        'TIO=F': 'Minério de Ferro'
    }

    carteira_moedas = {
        'USDJPY=X': 'Iene Japonês',
        'USDEUR=X': 'USD/Euro',
        'USDGBP=X': 'USD/Libra',
        'USDAUD=X': 'Dólar Australiano',
        'USDCAD=X': 'Dólar Canadense',
        'USDCHF=X': 'Franco Suíço',
        'USDCNY=X': 'Yuan Chinês',
        'USDBRL=X': 'Real Brasileiro',
        'USDINR=X': 'Rupia Indiana',
        'USDRUB=X': 'Rublo Russo',
        'USDMXN=X': 'Peso Mexicano',
        'USDZAR=X': 'Rand Sul-Africano',
        'USDTRY=X': 'Lira Turca',
        'USDKRW=X': 'Won Sul-Coreano',
        'USDIDR=X': 'Rupia Indonésia',
        'USDTHB=X': 'Baht Tailandês',
        'USDSGD=X': 'Dólar de Singapura',
        'USDPLN=X': 'Zloty Polonês',
        'USDNOK=X': 'Coroa Norueguesa'
    }

    # Configurar o estilo dos gráficos
    sns.set_style('whitegrid')
    plt.style.use('default')

    def obter_dados_historicos(ativos, dias_media):
        dados = pd.DataFrame()
        for ativo in ativos:
            try:
                dado_ativo = yf.download(ativo, period='1y', interval='1d')['Close']
                if not dado_ativo.empty:
                    dados[ativo] = dado_ativo
                else:
                    logging.warning(f"Sem dados para o ativo {ativo}.")
            except Exception as e:
                logging.error(f"Erro ao baixar dados para {ativo}: {e}")
        return dados.tail(dias_media).fillna(method='ffill').fillna(method='bfill')

    def calcular_z_score(ativos, dados_recente):
        taxas_atuais = dados_recente.iloc[-1]
        media = dados_recente.mean()
        desvio_padrao = dados_recente.std()
        z_scores = (taxas_atuais - media) / desvio_padrao
        z_scores = z_scores.reindex(ativos, fill_value=0)  # Preencher com zero caso o Z-score não possa ser calculado
        return z_scores

    def plotar_z_scores(z_scores, nome_carteira, dias_media):
        z_scores_ordenados = z_scores.sort_values(ascending=True)  # Ordenar de forma ascendente
        vmin = z_scores_ordenados.min()
        vmax = z_scores_ordenados.max()
        vcenter = 0 if vmin < 0 and vmax > 0 else (vmin + vmax) / 2

        norm = mcolors.TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
        cmap = plt.get_cmap('RdYlGn')
        colors = cmap(norm(z_scores_ordenados.values))

        num_assets = len(z_scores_ordenados)
        plt.figure(figsize=(max(14, num_assets * 0.7), 8))

        ax = sns.barplot(x=z_scores_ordenados.index, y=z_scores_ordenados.values, palette=colors)

        hoje = datetime.today().strftime('%d/%m/%Y')
        plt.xlabel('Ativos', fontsize=14)

        if nome_carteira == 'Pares de Moedas':
            plt.ylabel('Z-score // > 0 = Desvalorização da Moeda & < 0 = Valorização da Moeda', fontsize=10)
        else:
            plt.ylabel('Z-score', fontsize=14)

        plt.title(f'Z-score - {nome_carteira} em {hoje}\n(Últimos {dias_media} dias)', fontsize=18)
        plt.xticks(rotation=45, ha='right', fontsize=12)
        plt.yticks(fontsize=12)

        max_z_score = max(abs(z_scores_ordenados.min()), abs(z_scores_ordenados.max()))
        offset = 0.01 * max_z_score

        for i, valor in enumerate(z_scores_ordenados.values):
            if valor >= 0:
                ax.text(i, valor + offset, f'{valor:.2f}', ha='center', va='bottom', fontsize=12, bbox=dict(facecolor='white', edgecolor='none', pad=1))
            else:
                ax.text(i, valor - offset, f'{valor:.2f}', ha='center', va='top', fontsize=12, bbox=dict(facecolor='white', edgecolor='none', pad=1))

        ax.grid(True, which='both', axis='y', linestyle='--', linewidth=0.7, alpha=0.7)
        ax.set_axisbelow(True)
        plt.tight_layout()

    def gerar_analises(carteira, dias_media, nome_carteira, pdf):
        ativos = list(carteira.keys())
        dados_recente = obter_dados_historicos(ativos, dias_media)

        if dados_recente.empty:
            logging.error(f"Nenhum dado disponível para {nome_carteira}.")
            return

        z_scores = calcular_z_score(ativos, dados_recente)

        if z_scores.empty:
            logging.warning(f"Não há Z-scores calculados para {nome_carteira}.")
            return

        z_scores.index = [carteira[ativo] for ativo in z_scores.index]
        plotar_z_scores(z_scores, nome_carteira, dias_media)
        pdf.savefig()
        plt.close()

    # Função principal para gerar o PDF
    with PdfPages(output_file) as pdf:
        dias_media = 20
        gerar_analises(carteira_moedas, dias_media, 'Pares de Moedas', pdf)
        gerar_analises(carteira_bolsas, dias_media, 'Bolsas de Valores', pdf)
        gerar_analises(carteira_commodities, dias_media, 'Commodities', pdf)

    logging.info(f"Análises exportadas para '{output_file}'.")
    return output_file

