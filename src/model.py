import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
import streamlit as st

class BetModel:
    """
    Motor de IA com Baseline Comparativo.
    """

    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
        self.le_home = LabelEncoder()
        self.le_away = LabelEncoder()
        self.features = ['Prob_H', 'Prob_D', 'Prob_A', 'HomeTeam_Code', 'AwayTeam_Code']

    def calculate_baseline(self, df: pd.DataFrame):
        """
        Calcula a acurácia da estratégia 'Sempre Mandante'.
        """
        if df.empty: return 0.0
        home_wins = len(df[df['FTR'] == 'H'])
        return home_wins / len(df)

    def create_features(self, df: pd.DataFrame):
        """
        Transforma dados brutos em inteligência (Odds -> Probabilidades).
        """
        df_feat = df.copy()
        
        # 1. Feature Engineering: Odds Implícitas (Sabedoria do Mercado)
        df_feat['Prob_H'] = 1 / df_feat['B365H']
        df_feat['Prob_D'] = 1 / df_feat['B365D']
        df_feat['Prob_A'] = 1 / df_feat['B365A']
        
        # 2. Encoding de Times (Texto -> Números)
        # Concatenamos tudo para garantir que o Encoder conheça todos os times
        all_teams = pd.concat([df_feat['HomeTeam'], df_feat['AwayTeam']]).unique()
        self.le_home.fit(all_teams) # Treina o dicionário de times
        
        df_feat['HomeTeam_Code'] = self.le_home.transform(df_feat['HomeTeam'])
        df_feat['AwayTeam_Code'] = self.le_home.transform(df_feat['AwayTeam'])
        
        # Target Numérico
        target_map = {'H': 0, 'D': 1, 'A': 2}
        df_feat['Target'] = df_feat['FTR'].map(target_map)
        
        return df_feat

    @st.cache_resource
    def train_model(_self, df: pd.DataFrame):
        """
        Treina o modelo respeitando o tempo (Split Cronológico).
        """
        # Feature Engineering
        df_processed = _self.create_features(df)
        
        # SPLIT CRONOLÓGICO (Regra do Data Master)
        # Treino: Histórico (até 23/24)
        # Teste: Temporada Atual (24/25) ou a mais recente disponível
        last_season = df_processed['Season'].max()
        
        train = df_processed[df_processed['Season'] != last_season]
        test = df_processed[df_processed['Season'] == last_season]
        
        # Fallback se a temporada nova tiver poucos jogos
        if len(test) < 10:
            seasons = sorted(df_processed['Season'].unique())
            if len(seasons) > 1:
                last_season = seasons[-1] # Garante a ultima
                train = df_processed[df_processed['Season'] != last_season]
                test = df_processed[df_processed['Season'] == last_season]

        # Definição X e y
        X_train = train[_self.features]
        y_train = train['Target']
        X_test = test[_self.features]
        y_test = test['Target']

        # Treinamento
        _self.model.fit(X_train, y_train)
        
        # Métricas
        preds = _self.model.predict(X_test)
        model_acc = accuracy_score(y_test, preds)
        
        # Calcula Baseline no mesmo conjunto de teste
        baseline_acc = len(test[test['FTR'] == 'H']) / len(test)
        
        return model_acc, baseline_acc, last_season

    def predict_match(self, home_team, away_team, odds_h, odds_d, odds_a):
        """
        Faz a previsão para um jogo inputado manualmente.
        """
        try:
            # Prepara o input único
            h_code = self.le_home.transform([home_team])[0]
            a_code = self.le_home.transform([away_team])[0]
            
            input_data = pd.DataFrame([{
                'Prob_H': 1/odds_h,
                'Prob_D': 1/odds_d,
                'Prob_A': 1/odds_a,
                'HomeTeam_Code': h_code,
                'AwayTeam_Code': a_code
            }])
            
            probs = self.model.predict_proba(input_data)[0]
            
            # Mapeamento reverso classes -> H, D, A
            classes = self.model.classes_ # 0, 1, 2
            return {
                'H': probs[0], # 0 é H
                'D': probs[1], # 1 é D
                'A': probs[2]  # 2 é A
            }
        except Exception as e:
            # Se o time for desconhecido, usa média simples baseada nas odds
            st.warning(f"Time novo detectado. Usando probabilidade implícita das odds.")
            total_prob = (1/odds_h) + (1/odds_d) + (1/odds_a)
            return {
                'H': (1/odds_h) / total_prob,
                'D': (1/odds_d) / total_prob,
                'A': (1/odds_a) / total_prob
            }