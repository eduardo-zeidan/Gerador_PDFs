import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import datetime
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_pdf import PdfPages
import warnings

warnings.filterwarnings('ignore')

def gerar_pdf_analise_dispersao(output_file="Variação_Dispersão.pdf"):
    # Carteira de Moedas, Bolsas e Commodities
    moedas = ['USDBRL=X', 'THB=X', 'USDAUD=X', 'USDMXN=X', 'USDGBP=X',
              'USDEUR=X', 'JPY=X', 'CHF=X', 'CAD=X', 'CNY=X', 'INR=X',
              'CZK=X', 'TRY=X', 'NOK=X', 'SEK=X']

    nomes_amigaveis_moedas = {
        'USDBRL=X': 'Real',
        'THB=X': 'Baht Tailandês',
        'USDAUD=X': 'Dólar Australiano',
        'USDMXN=X': 'Peso Mexicano',
        'USDGBP=X': 'Dólar X Libra',
        'USDEUR=X': 'Dólar X Euro',
        'JPY=X': 'Iene Japonês',
        'CHF=X': 'Franco Suíço',
        'CAD=X': 'Dólar Canadense',
        'CNY=X': 'Yuan Chinês',
        'INR=X': 'Rupia Indiana',
        'CZK=X': 'Coroa Tcheca',
        'TRY=X': 'Lira Turca',
        'NOK=X': 'Coroa Norueguesa',
        'SEK=X': 'Coroa Sueca'
    }

    bolsas = ['^GSPC', '^DJI', '^IXIC', '^FTSE', '^N225', '^GDAXI', '^HSI', '^BSESN', '^BVSP', 
              '^MERV', '^FCHI', '^BFX', '^TWII', '^STOXX50E', '^TA125.TA','000001.SS']

    nomes_amigaveis_bolsas = {
        '^GSPC': 'S&P 500',
        '^DJI': 'Dow Jones',
        '^IXIC': 'Nasdaq',
        '^FTSE': 'FTSE 100',
        '^N225': 'Nikkei 225',
        '^GDAXI': 'DAX',
        '^HSI': 'Hang Seng',
        '^BSESN': 'Sensex (Índia)',
        '^BVSP': 'Bovespa',
        '^MERV': 'Merval (Argentina)',
        '^FCHI': 'CAC 40 (França)',
        '^BFX': 'BEL 20 (Bélgica)',
        '^TWII': 'TSEC (Taiwan)',
        '^STOXX50E': 'Euro Stoxx 50',
        '^TA125.TA': 'TA-125 (Israel)',
        '000001.SS': 'Xangai (China)'
    }

    commodities = ['CL=F', 'GC=F', 'SI=F', 'HG=F', 'NG=F', 'ZC=F', 'ZW=F', 'KC=F', 'CT=F', 'SB=F',
                  'PA=F', 'PL=F', 'HO=F', 'RB=F', 'OJ=F', 'CC=F', 'ZS=F', 'ZM=F', 'LE=F', 'HE=F', 'BZ=F', 'TIO=F']

    nomes_amigaveis_commodities = {
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

    # Função para ajustar timezone e resolver problemas de data
    def ajustar_timezone(index):
        if hasattr(index, 'tz'):
            return index.tz_convert(None)
        return index

    # Função para verificar e limpar dados inconsistentes
    def verificar_dados_inconsistentes(dados):
        if dados.isnull().any().any():
            dados = dados.dropna()
        if (dados == 0).any().any():
            dados = dados[dados != 0]
        return dados

    # Função para pegar o fechamento exato para os dias desejados
    def obter_fechamento_exato(historico, datas):
        preços = {}
        for nome_periodo, data in datas.items():
            if data in historico.index:
                preços[nome_periodo] = historico['Close'].loc[data]
            else:
                preços[nome_periodo] = historico['Close'].asof(data)
        return preços

    # Unindo todas as carteiras
    ativos = moedas + bolsas + commodities
    nomes_amigaveis = {**nomes_amigaveis_moedas, **nomes_amigaveis_bolsas, **nomes_amigaveis_commodities}

    # Definir datas de início e fim
    hoje = datetime.datetime.now().replace(tzinfo=None)
    inicio_ano = datetime.datetime(2025, 1, 1).replace(tzinfo=None)
    periodos = {
        '7d': (hoje - pd.offsets.BDay(7)).replace(tzinfo=None),
        '45d': (hoje - pd.offsets.BDay(45)).replace(tzinfo=None),
        '90d': (hoje - pd.offsets.BDay(90)).replace(tzinfo=None),
        '1y': inicio_ano
    }

    # Dicionário para armazenar as variações dos ativos
    variacoes = {
        'Ativo': [],
        'Nome_Amigavel': [],
        'Classe': [],
        'Variação_Anual': [],
        'Variação_7_Dias': [],
        'Variação_45_Dias': [],
        'Variação_90_Dias': []
    }

    # Alteração na Data Inicial
    inicio_dados = datetime.datetime(2024, 1, 1).replace(tzinfo=None)  # Coletar desde 2024
    inicio_ano = datetime.datetime(2025, 1, 1).replace(tzinfo=None)  # Variação anual começa em 2025

    # Coleta de dados
    for ativo in ativos:
        classe = 'Moeda' if ativo in moedas else 'Bolsa' if ativo in bolsas else 'Commodity'
        nome_amigavel = nomes_amigaveis.get(ativo, ativo)
        ticker = yf.Ticker(ativo)
        historico = ticker.history(start=inicio_dados, end=hoje)  # Coleta desde 2024

        # Ajustar o index para remover timezone
        historico.index = ajustar_timezone(historico.index)

        if not historico.empty:
            # Limpar dados inconsistentes
            historico = verificar_dados_inconsistentes(historico)

            try:
                # Filtrar apenas os dados desde 2025 para calcular variação anual
                historico_2025 = historico[historico.index >= inicio_ano]

                if historico_2025.empty:
                    print(f"Sem dados para {nome_amigavel} desde {inicio_ano}.")
                    continue

                # Preço atual e preço de início de 2025
                preco_atual = historico_2025['Close'][-1]
                preco_inicio_2025 = historico_2025['Close'].iloc[0]

                # Calcular a variação anual
                variacao_anual = ((preco_atual - preco_inicio_2025) / preco_inicio_2025) * 100

                # Obter fechamentos exatos para os períodos desejados
                precos = obter_fechamento_exato(historico, periodos)
                variacao_7_dias = ((preco_atual - precos['7d']) / precos['7d']) * 100
                variacao_45_dias = ((preco_atual - precos['45d']) / precos['45d']) * 100
                variacao_90_dias = ((preco_atual - precos['90d']) / precos['90d']) * 100

                # Armazenar no dicionário
                variacoes['Ativo'].append(ativo)
                variacoes['Nome_Amigavel'].append(nome_amigavel)
                variacoes['Classe'].append(classe)
                variacoes['Variação_Anual'].append(variacao_anual)
                variacoes['Variação_7_Dias'].append(variacao_7_dias)
                variacoes['Variação_45_Dias'].append(variacao_45_dias)
                variacoes['Variação_90_Dias'].append(variacao_90_dias)
            except Exception as e:
                print(f"Erro ao processar {nome_amigavel}: {e}")

    # Convertendo o dicionário para DataFrame e ordenando por Variação Anual
    df_variacoes = pd.DataFrame(variacoes)

    if df_variacoes.empty:
        print("Nenhuma variação calculada. PDF não será gerado.")
        return output_file

    # Exibir o DataFrame no terminal
    print("Variações dos Ativos:")
    print(df_variacoes[['Nome_Amigavel', 'Variação_Anual', 'Variação_7_Dias', 'Variação_45_Dias']])

    # Gerar gráficos de dispersão e salvar em PDF, organizados por setor e período
    with PdfPages(output_file) as pdf:
        classes_ativos = ['Moeda', 'Bolsa', 'Commodity']
        periodos_graficos = {
            '7 Dias': 'Variação_7_Dias',
            '45 Dias': 'Variação_45_Dias',
            '90 Dias': 'Variação_90_Dias',
            'Anual': 'Variação_Anual'
        }

        for classe in classes_ativos:
            df_classe = df_variacoes[df_variacoes['Classe'] == classe].sort_values(by='Variação_Anual', ascending=True)
            
            if df_classe.empty:
                print(f"Sem dados para a classe {classe}.")
                continue

            for titulo, coluna in periodos_graficos.items():
                fig, axs = plt.subplots(figsize=(11, 8))
                fig.suptitle(f'{classe} - Variação ({titulo}) - Ordenado pelo Retorno Anual', fontsize=16)

                scatter = axs.scatter(range(len(df_classe)), df_classe[coluna], c=df_classe[coluna], cmap='RdYlGn', s=150)
                axs.set_xlabel(f'{classe} - Ordenado pelo Retorno Anual', fontsize=12)
                axs.set_ylabel(f'Variação (%) - {titulo}', fontsize=12)
                axs.axhline(y=0, color='black', linestyle='--', linewidth=0.5)

                # Anotação para cada ativo com o nome amigável
                for i, txt in enumerate(df_classe['Nome_Amigavel']):
                    y = df_classe[coluna].iloc[i]
                    axs.annotate(txt, (i, y), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=8)

                fig.colorbar(scatter, ax=axs, label='Variação (%)')
                plt.xticks([])  # Remover rótulos do eixo X
                plt.tight_layout(rect=[0, 0.03, 1, 0.95])
                pdf.savefig(fig)
                plt.close(fig)

    print(f"Gráficos ajustados e salvos no arquivo '{output_file}'.")
    return output_file
