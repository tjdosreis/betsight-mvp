import streamlit as st
import pandas as pd
from src.data_loader import DataLoader
from src.model import BetModel
from src.finance import RiskManager

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="BetSight MVP", layout="wide", page_icon="🎯")

# --- CSS CUSTOM ---
st.markdown("""
<style>
    .metric-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b; }
    .success-text { color: #00cc00; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO ---
st.title("🎯 BetSight Intelligence")
st.caption("Sprint 1: Premier League | Model Validation Protocol")

# --- CARGA DE DADOS & TREINO ---
with st.spinner("Processando ETL e Treinando Modelo (Random Forest)..."):
    df = DataLoader.load_data()
    
    # Instancia e Treina
    ai_engine = BetModel()
    model_acc, baseline_acc, test_season = ai_engine.train_model(df)

# --- DASHBOARD SUPERIOR: VEREDITO ---
st.subheader(f"⚔️ O Veredito: Temporada {test_season}")
col_a, col_b, col_c = st.columns(3)

with col_a:
    st.metric("Acurácia do Modelo (IA)", f"{model_acc:.1%}")

with col_b:
    st.metric("Baseline (Sempre Casa)", f"{baseline_acc:.1%}")

with col_c:
    diff = model_acc - baseline_acc
    if diff > 0:
        st.success(f"✅ SUPERIORIDADE: +{diff:.1%}")
    else:
        st.error(f"⚠️ NECESSÁRIO REFINAR: {diff:.1%}")

st.divider()

# --- SIMULADOR ---
col_sim, col_data = st.columns([1, 2])

with col_sim:
    st.markdown("### 🤖 Simulador de Aposta")
    st.info("O modelo usa as Odds + Histórico dos Times.")
    
    # Seleção de Times (Ordenados)
    teams = sorted(df['HomeTeam'].unique())
    home_team = st.selectbox("Time da Casa", teams, index=0)
    away_team = st.selectbox("Visitante", teams, index=1)
    
    # Inputs de Odds
    c1, c2, c3 = st.columns(3)
    odds_h = c1.number_input("Odds Casa", 1.01, 100.0, 2.00)
    odds_d = c2.number_input("Odds Empate", 1.01, 100.0, 3.50)
    odds_a = c3.number_input("Odds Fora", 1.01, 100.0, 3.80)
    
    # Gestão de Banca
    bankroll = st.number_input("Banca ($)", value=1000.0)
    kelly_frac = st.slider("Kelly Fraction", 0.1, 0.5, 0.2)

    if st.button("CALCULAR PROBABILIDADE", type="primary"):
        # Previsão
        probs = ai_engine.predict_match(home_team, away_team, odds_h, odds_d, odds_a)
        p_home = probs['H']
        
        # Kelly
        stake_pct = RiskManager.kelly_criterion(p_home, odds_h, kelly_frac)
        stake_val = bankroll * stake_pct
        ev = RiskManager.expected_value(p_home, odds_h)
        
        # Output
        st.markdown("---")
        st.write(f"**Probabilidade Real (IA):** {p_home:.1%}")
        st.write(f"**Valor Esperado (EV):** {ev:.2f}")
        
        if ev > 0:
            st.success(f"💰 Aposta Sugerida: ${stake_val:.2f} ({stake_pct*100:.1f}%)")
        else:
            st.warning("⛔ Não há valor nesta aposta (EV Negativo).")

with col_data:
    st.markdown("### 📋 Dados Brutos (ETL)")
    st.write(f"Total de jogos processados: {len(df)}")
    st.dataframe(
        df[['Date', 'Season', 'HomeTeam', 'AwayTeam', 'FTR', 'B365H']].tail(10),
        use_container_width=True,
        hide_index=True
    )
    
    # Botão para baixar CSV (Requisito do Data Master)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "⬇️ Baixar Dataset Processado (CSV)",
        csv,
        "betsight_dataset.csv",
        "text/csv"
    )