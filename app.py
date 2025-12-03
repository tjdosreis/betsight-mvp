import streamlit as st
import pandas as pd
from src.data_loader import DataLoader
from src.model import BetModel
from src.finance import RiskManager

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="BetSight Intelligence", 
    layout="wide", 
    page_icon="🎯",
    initial_sidebar_state="expanded"
)

# --- ESTILIZAÇÃO (CSS) ---
st.markdown("""
<style>
    .reportview-container { background: #fdfdfd; }
    .sidebar .sidebar-content { background: #f0f2f6; }
    .metric-container { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .legal-text { font-size: 12px; color: #666; text-align: justify; }
    .big-money { font-size: 26px; font-weight: bold; color: #2e7bcf; }
</style>
""", unsafe_allow_html=True)

# --- CARGA DE DADOS & IA (BACKGROUND) ---
# O usuário não vê isso, mas garante que o sistema esteja vivo
with st.spinner("🔄 Conectando ao Neural Core..."):
    df = DataLoader.load_data()
    ai_engine = BetModel()
    if not df.empty:
        model_acc, baseline_acc, test_season = ai_engine.train_model(df)
    else:
        st.error("Falha crítica na conexão de dados.")
        st.stop()

# --- SIDEBAR: PAINEL DE CONTROLE ---
st.sidebar.header("⚙️ Parâmetros do Confronto")

# 1. Seleção de Times
teams = sorted(df['HomeTeam'].unique())
home_team = st.sidebar.selectbox("Mandante (Casa)", teams, index=0, placeholder="Escolha o time...")
away_team = st.sidebar.selectbox("Visitante (Fora)", teams, index=1, placeholder="Escolha o time...")

# 2. Odds (Mercado)
st.sidebar.markdown("### Odds do Mercado")
c1, c2, c3 = st.sidebar.columns(3)
odds_h = c1.number_input("Casa", 1.01, 50.0, 2.00)
odds_d = c2.number_input("Empate", 1.01, 50.0, 3.40)
odds_a = c3.number_input("Fora", 1.01, 50.0, 4.00)

st.sidebar.markdown("---")

# 3. Gestão de Banca (CFO)
st.sidebar.header("💰 Gestão de Risco")
bankroll = st.sidebar.number_input("Banca Disponível ($)", value=1000.0, step=50.0)
kelly_fraction = st.sidebar.slider("Agressividade (Kelly)", 0.1, 0.5, 0.25)
max_cap = st.sidebar.slider("Trava de Segurança (Cap)", 0.01, 0.10, 0.05, format="%.2f")

# 4. BOTÃO DE AÇÃO (CTA)
run_analysis = st.sidebar.button("Analisar Probabilidades", type="primary", use_container_width=True)

# --- INTERFACE PRINCIPAL ---

# H1 & H2 & Intro
st.title("BetSight Intelligence")
st.subheader("Análise Preditiva da Premier League")
st.write("Transformando dados históricos em vantagem estatística. Configure o confronto no menu lateral para iniciar a varredura.")

# Métricas de Validação (Prova Social Técnica)
with st.container():
    st.markdown(f"#### 🛡️ Status do Modelo (Temporada {test_season})")
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Precisão do Algoritmo", f"{model_acc:.1%}")
    col_m2.metric("Baseline de Mercado", f"{baseline_acc:.1%}")
    diff = model_acc - baseline_acc
    col_m3.metric("Alpha (Vantagem)", f"{diff:+.1%}", delta_color="normal")

st.divider()

# --- LÓGICA DE EXECUÇÃO ---
if run_analysis:
    # Validação de Lógica (NeuroCopy Req)
    if home_team == away_team:
        st.error("⚠️ Erro de Lógica: O time Mandante e Visitante não podem ser o mesmo.")
    else:
        # Feedback de Carregamento
        with st.spinner("🔄 Processando 5 anos de dados históricos..."):
            
            # 1. Inteligência (Model)
            probs = ai_engine.predict_match(home_team, away_team, odds_h, odds_d, odds_a)
            p_home = probs['H']
            
            # 2. Finanças (CFO Risk Manager)
            decision = RiskManager.calculate_stake(
                probability=p_home,
                odds=odds_h,
                bankroll=bankroll,
                fraction=kelly_fraction,
                max_cap=max_cap
            )
            
            # 3. Exibição do Relatório
            st.success("✅ Análise concluída. Relatório gerado.")
            
            res_col1, res_col2 = st.columns([1, 1])
            
            with res_col1:
                st.markdown("### 🧠 Inteligência Artificial")
                st.write(f"Confronto: **{home_team}** vs **{away_team}**")
                
                # Gráfico de barras simples para probabilidades
                chart_data = pd.DataFrame({
                    "Resultado": ["Casa", "Empate", "Visitante"],
                    "Probabilidade": [probs['H'], probs['D'], probs['A']]
                })
                st.bar_chart(chart_data, x="Resultado", y="Probabilidade", color="#2e7bcf")
                
                st.info(f"Probabilidade Real Calculada: **{p_home:.1%}**")

            with res_col2:
                st.markdown("### 💸 Diretriz Financeira")
                st.metric("Valor Esperado (EV)", f"{decision['ev']:.2f}")
                
                if decision['stake_val'] > 0:
                    st.markdown(f"""
                    <div style="padding: 15px; border: 1px solid #4CAF50; border-radius: 5px; background-color: #e8f5e9;">
                        <span style="color: #2E7D32; font-weight: bold;">💎 OPORTUNIDADE DETECTADA</span><br>
                        Aporte Sugerido: <span class="big-money">${decision['stake_val']:.2f}</span><br>
                        <small>({decision['stake_pct']}% da Banca)</small>
                    </div>
                    """, unsafe_allow_html=True)
                    st.caption(f"Motivo: {decision['reason']}")
                else:
                    st.markdown(f"""
                    <div style="padding: 15px; border: 1px solid #ef5350; border-radius: 5px; background-color: #ffebee;">
                        <span style="color: #c62828; font-weight: bold;">⛔ ABORTAR OPERAÇÃO</span><br>
                        Risco matemático superior ao benefício.
                    </div>
                    """, unsafe_allow_html=True)
                    st.caption(f"Diagnóstico: {decision['reason']}")

# --- HISTÓRICO RECENTE (Prova de Integridade) ---
st.markdown("---")
with st.expander("📋 Ver Dados Brutos (Auditoria)"):
    st.dataframe(df.tail(10), use_container_width=True)

# --- RODAPÉ DE COMPLIANCE (NeuroCopy Req) ---
st.markdown("---")
st.markdown("""
<div class="legal-text">
    <strong>⚖️ Aviso Legal & Responsabilidade</strong><br>
    O BetSight é uma ferramenta estatística desenvolvida estritamente para fins informativos e de entretenimento. 
    O desempenho passado não garante resultados futuros. Apostas esportivas envolvem alto risco financeiro e a possibilidade de perda total do capital.
    Jogue com responsabilidade e apenas com valores que pode perder.<br><br>
    🔞 <strong>Proibido para menores de 18 anos.</strong>
</div>
""", unsafe_allow_html=True)