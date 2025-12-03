import streamlit as st
import pandas as pd
from src.data_loader import DataLoader
from src.model import BetModel
from src.finance import RiskManager

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="BetSight MVP", layout="wide", page_icon="🎯")

# --- CSS (Estilo Visual) ---
st.markdown("""
<style>
    .metric-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b; }
    .success-msg { color: #00cc00; font-weight: bold; font-size: 18px; }
    .error-msg { color: #ff3333; font-weight: bold; font-size: 18px; }
    .warning-msg { color: #ffa500; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO ---
st.title("🎯 BetSight Intelligence")
st.caption("Sprint 1: System v1.0 | Quarter Kelly Strategy Active")

# --- SIDEBAR (CONTROLES DO CFO) ---
st.sidebar.header("💰 Parâmetros do CFO")
bankroll = st.sidebar.number_input("Banca Total ($)", value=1000.0, step=100.0)
kelly_fraction = st.sidebar.slider("Kelly Fraction", 0.1, 0.5, 0.25, help="Padrão: 0.25 (Quarter Kelly)")
max_cap = st.sidebar.slider("Hard Cap (Teto Máximo)", 0.01, 0.10, 0.05, format="%.2f", help="Máximo por aposta: 5%")

# --- CARGA DE DADOS & TREINO ---
with st.spinner("Inicializando IA e Carregando Dados..."):
    df = DataLoader.load_data()
    ai_engine = BetModel()
    
    if not df.empty:
        model_acc, baseline_acc, test_season = ai_engine.train_model(df)
    else:
        st.error("Erro crítico: Base de dados vazia.")
        st.stop()

# --- PAINEL DE PERFORMANCE ---
st.subheader(f"⚔️ Validação do Modelo (Temporada {test_season})")
c1, c2, c3 = st.columns(3)
c1.metric("Acurácia IA", f"{model_acc:.1%}")
c2.metric("Baseline (Mandante)", f"{baseline_acc:.1%}")
diff = model_acc - baseline_acc
c3.metric("Edge do Modelo", f"{diff:+.1%}", delta_color="normal" if diff > 0 else "inverse")

st.divider()

# --- SIMULADOR DE APOSTAS ---
col_sim, col_data = st.columns([1, 2])

with col_sim:
    st.markdown("### 🤖 Oportunidade de Mercado")
    
    # Inputs
    teams = sorted(df['HomeTeam'].unique())
    home_team = st.selectbox("Mandante", teams, index=0)
    away_team = st.selectbox("Visitante", teams, index=1)
    
    cols_odds = st.columns(3)
    odds_h = cols_odds[0].number_input("Odds Casa", 1.01, 50.0, 2.00)
    odds_d = cols_odds[1].number_input("Odds Empate", 1.01, 50.0, 3.40)
    odds_a = cols_odds[2].number_input("Odds Fora", 1.01, 50.0, 4.00)

    if st.button("CALCULAR INVESTIMENTO", type="primary"):
        # 1. Previsão da IA
        probs = ai_engine.predict_match(home_team, away_team, odds_h, odds_d, odds_a)
        p_home = probs['H']
        
        # 2. Decisão do CFO
        decision = RiskManager.calculate_stake(
            probability=p_home, 
            odds=odds_h, 
            bankroll=bankroll, 
            fraction=kelly_fraction, 
            max_cap=max_cap
        )
        
        # 3. Output Visual
        st.markdown("---")
        
        # Métricas Chave
        k1, k2 = st.columns(2)
        k1.metric("Probabilidade Real (IA)", f"{p_home:.1%}")
        k2.metric("Valor Esperado (EV)", f"{decision['ev']:.2f}")
        
        st.markdown("#### 💸 Decisão Financeira")
        
        if decision['stake_val'] > 0:
            st.markdown(f'<p class="success-msg">💎 APOSTAR: ${decision["stake_val"]:.2f}</p>', unsafe_allow_html=True)
            st.write(f"Representa **{decision['stake_pct']}%** da sua banca.")
            st.caption(f"Motivo: {decision['reason']}")
            
            # Alerta se bateu no teto
            if decision['stake_pct'] == (max_cap * 100):
                st.warning(f"⚠️ Nota: O valor foi limitado pelo Hard Cap de {max_cap*100:.0f}%.")
                
        else:
            st.markdown(f'<p class="error-msg">⛔ {decision["reason"]}</p>', unsafe_allow_html=True)
            st.write(f"Stake Recomendada: $0.00")

with col_data:
    st.markdown("### 📋 Dados Históricos")
    st.dataframe(df[['Date', 'HomeTeam', 'AwayTeam', 'FTR', 'B365H']].tail(15), use_container_width=True, hide_index=True)