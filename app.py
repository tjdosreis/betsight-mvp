import streamlit as st
import pandas as pd
from io import StringIO
from src.model import BetModel
from src.finance import RiskManager
from src.backtest import Backtester

# --- CONFIG ---
st.set_page_config(page_title="BetSight v2.1", layout="wide", page_icon="🦅")
st.markdown("""<style>.traffic-card { padding: 15px; border-radius: 8px; text-align: center; color: white; font-weight: bold; margin-bottom: 10px; }.green { background-color: #28a745; }.yellow { background-color: #ffc107; color: black; }.red { background-color: #dc3545; }</style>""", unsafe_allow_html=True)

# --- LOADERS (Versão Frozen) ---
@st.cache_resource
def init_system():
    # 1. Carrega IA Congelada
    ai = BetModel()
    
    # 2. Carrega Histórico Processado (CSV Local)
    try:
        df = pd.read_csv("betsight_history.csv")
        # Garante datas
        df['Date'] = pd.to_datetime(df['Date'])
    except FileNotFoundError:
        st.error("⚠️ Histórico não encontrado. Execute o pipeline de treino.")
        df = pd.DataFrame()
        
    return df, ai

df_hist, ai_engine = init_system()

# --- SIDEBAR ---
st.sidebar.title("🦅 BetSight Ops")
st.sidebar.info("Modo: Production (Frozen Model)")

# INPUT MANUAL
st.sidebar.header("📝 Jogos da Semana")
csv_template = """HomeTeam,AwayTeam,B365H,B365D,B365A
Arsenal,Liverpool,2.10,3.50,3.20
Man City,Chelsea,1.50,4.50,6.00
Fulham,Wolves,2.40,3.30,2.90"""
input_csv = st.sidebar.text_area("CSV Input:", value=csv_template, height=150)

st.sidebar.markdown("---")
st.sidebar.header("💰 Gestão de Banca")
bankroll = st.sidebar.number_input("Banca Inicial (R$)", 1000.0, step=100.0)
kelly_frac = st.sidebar.slider("Fração de Kelly", 0.1, 0.5, 0.25)
max_cap = st.sidebar.slider("Teto Máximo", 0.01, 0.10, 0.05)

# --- MAIN ---
st.title("🦅 BetSight Intelligence")
st.caption("Operation Truth | Dados Auditados")

tab1, tab2 = st.tabs(["🚦 Radar (Live)", "📉 Auditoria"])

# --- TAB 1 ---
with tab1:
    if st.button("🔍 PROCESSAR JOGOS", type="primary"):
        try:
            live_data = pd.read_csv(StringIO(input_csv))
            st.subheader("Análise Tática")
            cols = st.columns(len(live_data))
            
            for idx, row in live_data.iterrows():
                probs = ai_engine.predict_match(row['HomeTeam'], row['AwayTeam'], row['B365H'], row['B365A'])
                p_home = probs['H']
                decision = RiskManager.calculate_stake(p_home, row['B365H'], bankroll, kelly_frac, max_cap)
                ev = decision['ev']
                
                status_color = "red"
                status_text = "NÃO APOSTAR"
                if ev > 0.05 and p_home > 0.55:
                    status_color = "green"
                    status_text = "APOSTAR"
                elif ev > 0:
                    status_color = "yellow"
                    status_text = "OBSERVAR"
                
                reasons = ai_engine.explain_prediction(probs, probs['Mkt_Diff'])
                
                with cols[idx]:
                    st.markdown(f'<div class="traffic-card {status_color}">{status_text}<br><small>{row["HomeTeam"]}</small></div>', unsafe_allow_html=True)
                    st.metric("Prob. Real", f"{p_home:.1%}")
                    st.metric("EV", f"{ev:.2f}")
                    with st.expander("Por quê?"):
                        for r in reasons: st.write(f"- {r}")
                        st.markdown("---")
                        if decision['stake_val'] > 0: st.success(f"Aposta: R$ {decision['stake_val']:.2f}")
                        else: st.error("Aposta: R$ 0.00")
        except Exception as e:
            st.error(f"Erro no CSV: {e}")

# --- TAB 2 ---
with tab2:
    if df_hist.empty:
        st.warning("Sem dados.")
    else:
        st.subheader("Auditoria Financeira")
        with st.spinner("Rodando Simulação Walk-Forward..."):
            audit_df, equity_curve = Backtester.run_cfo_audit(df_hist, ai_engine, bankroll)
            
        fig_eq, fig_dd = Backtester.plot_dashboard(equity_curve)
        st.plotly_chart(fig_eq, use_container_width=True)
        st.plotly_chart(fig_dd, use_container_width=True)
        
        # Audit Log
        display_df = audit_df[['Date', 'Match', 'Model_Prob', 'Odds', 'Stake_Pct', 'Outcome', 'PnL', 'Drawdown']].copy()
        display_df.columns = ['Data', 'Jogo', 'Prob. IA', 'Odds', '% Aposta', 'Resultado', 'R$ PnL', 'Queda Max']
        st.dataframe(display_df.sort_values('Data', ascending=False), use_container_width=True)