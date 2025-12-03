import pandas as pd
import streamlit as st

class DataLoader:
    BASE_URL = "https://www.football-data.co.uk/mmz4281/{season}/E0.csv"
    SEASONS = ["2324", "2223", "2122"]

    @staticmethod
    @st.cache_data(ttl=3600)
    def load_data():
        all_data = []
        cols = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'B365H', 'B365D', 'B365A']

        for season in DataLoader.SEASONS:
            url = DataLoader.BASE_URL.format(season=season)
            try:
                df = pd.read_csv(url, usecols=lambda c: c in cols)
                df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
                df['Season_ID'] = season
                all_data.append(df)
            except Exception:
                continue

        if not all_data:
            return pd.DataFrame()

        return pd.concat(all_data, ignore_index=True).dropna().sort_values(by='Date', ascending=False)