import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

class Backtester:
    """
    Motor de Auditoria Financeira (CFO Spec).
    Simula Juros Compostos, Quarter Kelly e Drawdown.
    """

    @staticmethod
    def run_cfo_audit(df: pd.DataFrame, model_engine, initial_bankroll=1000.0):
        """
        Simulação Walk-Forward rigorosa.
        """
        # Ordenação cronológica vital
        df = df.sort_values('Date').reset_index(drop=True)
        # Pega amostra recente (ex: últimos 100 jogos) para performance recente
        df = df.tail(100).copy()
        
        history = []
        current_bank = initial_bankroll
        high_water_mark = initial_bankroll
        
        # Para gráfico inicial
        equity_curve = [{'Date': df.iloc[0]['Date'], 'Bankroll': initial_bankroll, 'Drawdown_Pct': 0.0}]

        for idx, row in df.iterrows():
            # 1. Dados
            odds_h = row['B365H']
            odds_a = row['B365A']
            
            # 2. Previsão
            probs = model_engine.predict_match(row['HomeTeam'], row['AwayTeam'], odds_h, odds_a)
            prob_h = probs['H']
            
            # 3. Lógica Financeira (CFO Risk Engine)
            # Kelly Criterion Pura
            b = odds_h - 1
            if b <= 0: b = 0.01
            p = prob_h
            q = 1 - p
            
            kelly_raw = ((b * p) - q) / b
            
            # Aplicação das Travas
            stake_pct = 0.0
            if kelly_raw > 0:
                # Quarter Kelly
                stake_pct = kelly_raw * 0.25
                # Hard Cap 5%
                if stake_pct > 0.05: stake_pct = 0.05
            
            # 4. Execução da Aposta
            money_stake = current_bank * stake_pct
            profit_loss = 0.0
            outcome = "Skip"
            
            if money_stake > 0:
                if row['FTR'] == 'H':
                    profit_loss = money_stake * (odds_h - 1)
                    outcome = "Win"
                else:
                    profit_loss = -money_stake
                    outcome = "Loss"
            
            current_bank += profit_loss
            
            # 5. Cálculo de Drawdown
            if current_bank > high_water_mark:
                high_water_mark = current_bank
            
            drawdown_val = high_water_mark - current_bank
            drawdown_pct = 0.0
            if high_water_mark > 0:
                drawdown_pct = drawdown_val / high_water_mark

            # 6. Log
            history.append({
                'Date': row['Date'],
                'Match': f"{row['HomeTeam']} vs {row['AwayTeam']}",
                'Model_Prob': prob_h,
                'Odds': odds_h,
                'Stake_Pct': stake_pct,
                'Stake_Val': money_stake,
                'Result': row['FTR'],
                'Outcome': outcome,
                'PnL': profit_loss,
                'Bankroll': current_bank,
                'Drawdown': drawdown_pct
            })
            
            equity_curve.append({
                'Date': row['Date'], 
                'Bankroll': current_bank, 
                'Drawdown_Pct': drawdown_pct
            })
            
        return pd.DataFrame(history), pd.DataFrame(equity_curve)

    @staticmethod
    def plot_dashboard(equity_df):
        """Gera os gráficos de Equity e Drawdown."""
        # Gráfico 1: Equidade
        fig_eq = px.line(equity_df, x='Date', y='Bankroll', 
                         title='💰 Curva de Equidade (Crescimento do Capital)',
                         color_discrete_sequence=['#00CC96'])
        fig_eq.add_hline(y=equity_df['Bankroll'].iloc[0], line_dash="dash", line_color="gray")
        
        # Gráfico 2: Drawdown (Área Vermelha)
        fig_dd = px.area(equity_df, x='Date', y='Drawdown_Pct', 
                         title='📉 Risco: Drawdown Histórico (Queda do Topo)',
                         color_discrete_sequence=['#EF553B'])
        fig_dd.update_yaxes(autorange="reversed", tickformat=".1%") # Inverte eixo Y para parecer submerso
        
        return fig_eq, fig_dd