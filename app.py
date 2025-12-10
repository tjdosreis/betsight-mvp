import streamlit as st
import pandas as pd
from io import StringIO
from src.data_loader import DataLoader
from src.model import BetModel
from src.finance import RiskManager
from src.backtest import Backtester

# --- CONFIG ---
st.set_page_config(page_title="BetSight v2", layout="wide", page_icon="🦅")

st.markdown("""
<style>
    .traffic-card { padding: 15px; border-radius: 8px; text-align: center; color: white; font-weight: bold; margin-bottom: 10px; }
    .green { background-color: #28a745; }
    .yellow { background-color: #ffc107; color: black; }
    .red { background-color: #dc3545; }
</style>
""", unsafe_allow_html=True)

# --- LOADERS ---
@st.cache_resource
def init_system():
    df = DataLoader.load_data()
    ai = BetModel()
    if not df.empty:
        acc, base, season = ai.train_model(df)
        return df, ai, acc, season
    return df, ai, 0, ""

df_hist, ai_engine, model_acc, test_season = init_system()

# --- SIDEBAR ---
st.sidebar.title("🦅 BetSight Ops")
st.sidebar.info("Modo: Sprint 2 (Truth)")

# 1. PLANO B (CSV MANUAL)
st.sidebar.header("📝 Injeção de Jogos (CSV)")
csv_template = """HomeTeam,AwayTeam,B365H,B365D,B365A
Arsenal,Liverpool,2.10,3.50,3.20
Man City,Chelsea,1.50,4.50,6.00
Fulham,Wolves,2.40,3.30,2.90"""

input_csv = st.sidebar.text_area("Cole os dados aqui:", value=csv_template, height=150, help="Formato: HomeTeam,AwayTeam,OddsC,OddsE,OddsF")

st.sidebar.markdown("---")
st.sidebar.header("💰 Risk Parameters")
bankroll = st.sidebar.number_input("Banca ($)", 1000.0, step=100.0)
kelly_frac = st.sidebar.slider("Kelly Fraction", 0.1, 0.5, 0.25)
max_cap = st.sidebar.slider("Hard Cap", 0.01, 0.10, 0.05)

# --- MAIN PAGE ---
st.title("🦅 BetSight Intelligence")
st.caption(f"Modelo Calibrado na Temporada {test_season} | Acurácia Histórica: {model_acc:.1%}")

# TABS
tab1, tab2 = st.tabs(["🚦 Radar de Oportunidades (Live)", "📉 Auditoria & Backtest"])

# --- TAB 1: LIVE ACTION ---
with tab1:
    if st.button("🔍 PROCESSAR JOGOS (CSV)", type="primary"):
        try:
            # Lê CSV manual
            live_data = pd.read_csv(StringIO(input_csv))
            
            st.subheader("Análise Tática da Semana")
            cols = st.columns(len(live_data))
            
            for idx, row in live_data.iterrows():
                # IA Predict
                probs = ai_engine.predict_match(row['HomeTeam'], row['AwayTeam'], row['B365H'], row['B365A'])
                p_home = probs['H']
                
                # Finance
                decision = RiskManager.calculate_stake(p_home, row['B365H'], bankroll, kelly_frac, max_cap)
                ev = decision['ev']
                
                # Semáforo Logic
                status_color = "red"
                status_text = "NÃO APOSTAR"
                
                if ev > 0.05 and p_home > 0.55:
                    status_color = "green"
                    status_text = "APOSTAR"
                elif ev > 0:
                    status_color = "yellow"
                    status_text = "OBSERVAR"
                
                # Explicação
                reasons = ai_engine.explain_prediction(probs, probs['Mkt_Diff'])
                
                # Render Card
                with cols[idx]:
                    st.markdown(f'<div class="traffic-card {status_color}">{status_text}<br><small>{row["HomeTeam"]}</small></div>', unsafe_allow_html=True)
                    st.metric("Prob. Real", f"{p_home:.1%}")
                    st.metric("EV", f"{ev:.2f}")
                    
                    with st.expander("Por quê?"):
                        for r in reasons:
                            st.write(f"- {r}")
                        st.markdown("---")
                        if decision['stake_val'] > 0:
                            st.success(f"Stake: ${decision['stake_val']:.2f}")
                        else:
                            st.error("Stake: $0.00")

        except Exception as e:
            st.error(f"Erro ao ler CSV. Verifique o formato. Detalhes: {e}")

# --- TAB 2: A VERDADE (BACKTEST) ---
with tab2:
    if df_hist.empty:
        st.warning("Sem dados históricos para backtest.")
    else:
        st.subheader("Auditoria Financeira (CFO Spec)")
        
        # Roda a simulação pesada (Risk Engine)
        with st.spinner("Simulando últimos 100 jogos com Hard Cap e Quarter Kelly..."):
            audit_df, equity_curve = Backtester.run_cfo_audit(df_hist, ai_engine, bankroll)
            
        # Gráficos
        fig_eq, fig_dd = Backtester.plot_dashboard(equity_curve)
        
        st.plotly_chart(fig_eq, use_container_width=True)
        st.plotly_chart(fig_dd, use_container_width=True)
        
        # KPIs
        total_pnl = equity_curve.iloc[-1]['Bankroll'] - equity_curve.iloc[0]['Bankroll']
        max_dd = equity_curve['Drawdown_Pct'].max()
        
        k1, k2, k3 = st.columns(3)
        k1.metric("Lucro/Prejuízo Total", f"${total_pnl:.2f}", delta_color="normal")
        k2.metric("Risco Máximo (Max Drawdown)", f"{max_dd:.1%}", delta_color="inverse")
        k3.metric("Banca Final", f"${equity_curve.iloc[-1]['Bankroll']:.2f}")
        
        st.divider()
        st.markdown("### 💀 Cemitério de Apostas (Audit Log)")
        st.dataframe(audit_df[['Date', 'Match', 'Model_Prob', 'Odds', 'Stake_Pct', 'Outcome', 'PnL', 'Drawdown']], use_container_width=True)