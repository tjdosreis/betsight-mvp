import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
import streamlit as st

class BetModel:
    """
    Motor de IA v2.1: Features de Mercado + Explainability.
    """

    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
        self.le_teams = LabelEncoder()
        # Features usadas para treinamento (Simplicidade Ruthless)
        self.features = ['Implied_Prob_H', 'Implied_Prob_A', 'Market_Diff', 'HomeTeam_Code', 'AwayTeam_Code']

    def create_features(self, df: pd.DataFrame):
        """
        Transforma dados brutos em inteligência (Data Master Spec).
        """
        df_feat = df.copy()
        
        # 1. Features de Mercado (A "Opinião" das Casas)
        df_feat['Implied_Prob_H'] = 1 / df_feat['B365H']
        df_feat['Implied_Prob_A'] = 1 / df_feat['B365A']
        
        # 2. Diferencial (Quem é o favorito?)
        df_feat['Market_Diff'] = df_feat['Implied_Prob_H'] - df_feat['Implied_Prob_A']
        
        # 3. Encoding de Times
        # Fit em todos os times possíveis para garantir consistência
        all_teams = pd.concat([df_feat['HomeTeam'], df_feat['AwayTeam']]).astype(str).unique()
        self.le_teams.fit(all_teams)
        
        df_feat['HomeTeam_Code'] = self.le_teams.transform(df_feat['HomeTeam'].astype(str))
        df_feat['AwayTeam_Code'] = self.le_teams.transform(df_feat['AwayTeam'].astype(str))
        
        # Target
        target_map = {'H': 0, 'D': 1, 'A': 2}
        df_feat['Target'] = df_feat['FTR'].map(target_map)
        
        return df_feat

    @st.cache_resource
    def train_model(_self, df: pd.DataFrame):
        df_processed = _self.create_features(df)
        
        # Split Cronológico
        last_season = df_processed['Season'].max()
        train = df_processed[df_processed['Season'] != last_season]
        test = df_processed[df_processed['Season'] == last_season]
        
        # Fallback de segurança
        if len(test) < 10:
            seasons = sorted(df_processed['Season'].unique())
            last_season = seasons[-1]
            train = df_processed[df_processed['Season'] != last_season]
            test = df_processed[df_processed['Season'] == last_season]

        X_train = train[_self.features]
        y_train = train['Target']
        X_test = test[_self.features]
        y_test = test['Target']

        _self.model.fit(X_train, y_train)
        
        preds = _self.model.predict(X_test)
        model_acc = accuracy_score(y_test, preds)
        baseline_acc = len(test[test['FTR'] == 'H']) / len(test)
        
        return model_acc, baseline_acc, last_season

    def predict_match(self, home, away, odds_h, odds_a):
        """Previsão para inputs manuais ou pipeline."""
        try:
            # Transforma input
            h_code = self.le_teams.transform([str(home)])[0]
            a_code = self.le_teams.transform([str(away)])[0]
            
            imp_h = 1/odds_h
            imp_a = 1/odds_a
            mkt_diff = imp_h - imp_a
            
            input_data = pd.DataFrame([{
                'Implied_Prob_H': imp_h,
                'Implied_Prob_A': imp_a,
                'Market_Diff': mkt_diff,
                'HomeTeam_Code': h_code,
                'AwayTeam_Code': a_code
            }])
            
            probs = self.model.predict_proba(input_data)[0]
            # probs = [Prob_H, Prob_D, Prob_A]
            return {'H': probs[0], 'D': probs[1], 'A': probs[2], 'Mkt_Diff': mkt_diff}
            
        except Exception as e:
            # Fallback se time desconhecido
            return {'H': 1/odds_h, 'D': 0.0, 'A': 1/odds_a, 'Mkt_Diff': 0.0}

    def explain_prediction(self, probs, mkt_diff):
        """
        O Tradutor (NeuroCopy Spec).
        """
        reasons = []
        p_home = probs['H']
        
        # 1. Análise de Mercado
        if mkt_diff > 0.15:
            reasons.append("🏢 **Consenso:** O Mercado vê o Mandante como Grande Favorito.")
        elif mkt_diff < -0.15:
            reasons.append("🦓 **Zebra:** O Mercado aposta contra o Mandante.")
        else:
            reasons.append("⚖️ **Equilíbrio:** Odds indicam um jogo parelho.")
            
        # 2. Confiança da IA
        if p_home > 0.60:
            reasons.append("🤖 **Sinal Forte:** A IA identificou padrões históricos claros de vitória.")
        elif p_home < 0.40:
            reasons.append("⚠️ **Risco:** A IA não confia na vitória do mandante.")
            
        return reasons