import pandas as pd
import joblib
import streamlit as st

class BetModel:
    """
    Motor de Inferência v3.0 (Frozen Model).
    Carrega o cérebro pré-treinado do Data Master.
    """

    def __init__(self):
        # Carrega artefatos estáticos
        try:
            self.model = joblib.load("betsight_model_v1.pkl")
            self.le_teams = joblib.load("team_encoder_v1.pkl")
        except FileNotFoundError:
            st.error("⚠️ Artefatos do modelo não encontrados. Rode 'python train_model.py' localmente e suba os arquivos .pkl")
            self.model = None

    def predict_match(self, home, away, odds_h, odds_a):
        """Previsão usando o modelo congelado."""
        if self.model is None: return {'H':0, 'D':0, 'A':0, 'Mkt_Diff':0}

        try:
            # Tratamento de input igual ao do treino
            h_str = str(home)
            a_str = str(away)
            
            # Encoder
            h_code = self.le_teams.transform([h_str])[0]
            a_code = self.le_teams.transform([a_str])[0]
            
            imp_h = 1/odds_h
            imp_a = 1/odds_a
            mkt_diff = imp_h - imp_a
            
            # Features exatas do treino
            input_data = pd.DataFrame([{
                'Implied_Prob_H': imp_h,
                'Implied_Prob_A': imp_a,
                'Market_Diff': mkt_diff,
                'HomeTeam_Code': h_code,
                'AwayTeam_Code': a_code
            }])
            
            probs = self.model.predict_proba(input_data)[0]
            return {'H': probs[0], 'D': probs[1], 'A': probs[2], 'Mkt_Diff': mkt_diff}
            
        except Exception as e:
            # Fallback (Time novo que subiu da segunda divisão)
            return {'H': 1/odds_h, 'D': 0.0, 'A': 1/odds_a, 'Mkt_Diff': 0.0}

    def explain_prediction(self, probs, mkt_diff):
        """Tradutor NeuroCopy."""
        reasons = []
        p_home = probs['H']
        
        if mkt_diff > 0.15:
            reasons.append("🏢 **Consenso:** Mercado vê Mandante como Favorito.")
        elif mkt_diff < -0.15:
            reasons.append("🦓 **Zebra:** Mercado aposta contra.")
        else:
            reasons.append("⚖️ **Equilíbrio:** Odds parelhas.")
            
        if p_home > 0.60:
            reasons.append("🤖 **Sinal Forte:** IA confirma favoritismo.")
        elif p_home < 0.40:
            reasons.append("⚠️ **Risco:** IA cética com o mandante.")
            
        return reasons