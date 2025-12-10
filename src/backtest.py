import pandas as pd
import plotly.graph_objects as go
from src.finance import RiskManager

class Backtester:
    """
    O Juiz Imparcial.
    Simula o desempenho financeiro do modelo ao longo do tempo (Walk-Forward).
    """

    @staticmethod
    def run_walk_forward_simulation(df: pd.DataFrame, model_engine, initial_bankroll=1000.0):
        """
        Percorre a temporada cronologicamente.
        Para cada jogo, pergunta ao modelo e aplica a gestão do CFO.
        """
        # Garante ordem cronológica
        df = df.sort_values('Date').reset_index(drop=True)
        
        # Filtra apenas a temporada de teste (ex: 24/25) ou as últimas X rodadas
        # Para o MVP, vamos pegar os últimos 50 jogos para ser rápido
        test_slice = df.tail(50).copy()
        
        history = []
        current_bank = initial_bankroll
        
        # Log para o gráfico (Data vs Saldo)
        equity_curve = [{'Date': test_slice.iloc[0]['Date'], 'Balance': current_bank}]

        for index, row in test_slice.iterrows():
            # 1. Extrair dados do jogo
            odds_h = row['B365H']
            odds_d = row['B365D']
            odds_a = row['B365A']
            result = row['FTR'] # H, D, A
            
            # 2. Previsão da IA (Simulando que não sabemos o resultado)
            # Nota: O modelo já deve estar treinado com dados ANTERIORES a este jogo
            probs = model_engine.predict_match(
                row['HomeTeam'], row['AwayTeam'], odds_h, odds_d, odds_a
            )
            p_home = probs['H']
            
            # 3. Decisão do CFO
            decision = RiskManager.calculate_stake(
                probability=p_home,
                odds=odds_h,
                bankroll=current_bank,
                fraction=0.25, # Quarter Kelly fixo
                max_cap=0.05
            )
            
            stake = decision['stake_val']
            
            # 4. Resolução da Aposta (A Verdade)
            profit_loss = 0.0
            outcome = "Skip"
            
            if stake > 0:
                if result == 'H': # Green
                    profit_loss = (stake * odds_h) - stake
                    outcome = "Win"
                else: # Red
                    profit_loss = -stake
                    outcome = "Loss"
                
                # Atualiza Banca
                current_bank += profit_loss
            
            # 5. Registro (Audit Log)
            history.append({
                'Date': row['Date'],
                'Match': f"{row['HomeTeam']} vs {row['AwayTeam']}",
                'Prediction_Prob': p_home,
                'Odds': odds_h,
                'Stake': stake,
                'Result': result,
                'Outcome': outcome,
                'PnL': profit_loss,
                'Bankroll': current_bank
            })
            
            equity_curve.append({'Date': row['Date'], 'Balance': current_bank})

        return pd.DataFrame(history), pd.DataFrame(equity_curve)

    @staticmethod
    def plot_equity_curve(equity_df):
        """Gera o gráfico da Curva de Capital."""
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=equity_df['Date'], 
            y=equity_df['Balance'],
            mode='lines+markers',
            name='Saldo',
            line=dict(color='#00cc00', width=3)
        ))
        fig.update_layout(
            title="Curva de Equidade (Simulação Real)",
            xaxis_title="Tempo",
            yaxis_title="Banca (R$)",
            template="plotly_white",
            height=300
        )
        return fig