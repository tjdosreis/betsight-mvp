import pandas as pd
import streamlit as st

class DataLoader:
    """
    Pipeline ETL conforme especificações do Data Master.
    """
    
    # URL template para a Premier League (E0)
    BASE_URL = "https://www.football-data.co.uk/mmz4281/{season}/E0.csv"
    
    # Temporadas solicitadas: 20/21 até 24/25
    SEASONS = ['2021', '2122', '2223', '2324', '2425']

    @staticmethod
    @st.cache_data(ttl=3600)
    def load_data():
        """
        Baixa, consolida e limpa os dados.
        """
        all_data = []
        
        # Schema Obrigatório do Data Master
        cols_req = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'B365H', 'B365D', 'B365A']

        for season in DataLoader.SEASONS:
            url = DataLoader.BASE_URL.format(season=season)
            try:
                # Baixa apenas colunas que existem no CSV (para evitar erro em anos antigos)
                df = pd.read_csv(url, encoding="ISO-8859-1")
                
                # Filtra colunas de interesse
                cols_found = [c for c in cols_req if c in df.columns]
                df = df[cols_found].copy()
                
                # Adiciona coluna de Temporada para o Split Cronológico
                df['Season'] = season
                
                # Padronização de Data
                df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
                
                all_data.append(df)
            except Exception as e:
                # Silencia erro de temporadas futuras que ainda não existem
                continue

        if not all_data:
            return pd.DataFrame()

        # Consolidação
        df_final = pd.concat(all_data, ignore_index=True)
        
        # Limpeza (Regras do Data Master)
        df_final.dropna(subset=['FTR', 'B365H', 'B365D', 'B365A'], inplace=True)
        df_final.sort_values('Date', inplace=True)
        
        return df_final