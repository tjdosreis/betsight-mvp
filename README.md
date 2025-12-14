# 🦅 BetSight Intelligence (v2.1)

> **Sistema de Apoio à Decisão Esportiva com Gestão de Risco Financeiro (Kelly Criterion)**

![Status](https://img.shields.io/badge/Status-Production-success)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Stack](https://img.shields.io/badge/Stack-Streamlit%20|%20ScikitLearn%20|%20Plotly-orange)

O **BetSight** não é apenas mais um modelo preditivo. É um framework completo de **Inteligência Artificial + Engenharia Financeira** projetado para identificar ineficiências no mercado de apostas da Premier League (Inglaterra).

Diferente de preditores comuns que focam apenas em "Quem vai ganhar", o BetSight responde à pergunta mais importante: **"Vale a pena arriscar meu capital?"**

---

## 🚀 Funcionalidades Principais

### 1. 🧠 Motor de IA Híbrido (Frozen Model)
- Utiliza um algoritmo **Random Forest** treinado em 5 temporadas históricas (>1.500 jogos).
- **Entrada:** Odds do Mercado (Bet365) + Histórico de Times.
- **Saída:** Probabilidade Real Estatística.
- **Diferencial:** *Explainable AI (XAI)* que traduz os números em narrativas ("Consenso de Mercado" vs "Sinal Forte da IA").

### 2. 💰 Gestão de Risco (Venture CFO Spec)
- Implementação rigorosa do **Critério de Kelly Fracionário**.
- O sistema calcula o **Valor Esperado (EV)** de cada aposta.
- **Logic Gate:** Se o EV for negativo, o sistema exibe um 🔴 **Bloqueio de Segurança**, impedindo o usuário de operar, mesmo que o time seja favorito.

### 3. 📊 Auditoria Transparente (Audit Log)
Nada de "Caixa Preta".
- **Curva de Equidade:** Simulação *Walk-Forward* mostrando como R$ 1.000,00 teriam performado na temporada atual.
- **Drawdown Control:** Monitoramento de queda máxima de capital.
- **Cemitério de Apostas:** Lista completa de onde a IA errou, garantindo transparência total.

---

## 🛠️ Stack Tecnológica

- **Engenharia de Dados:** Python, Pandas, Requests (Pipeline ETL Automatizado).
- **Machine Learning:** Scikit-Learn (Random Forest, Label Encoding), Joblib (Model Serialization).
- **Visualização:** Plotly (Gráficos Financeiros Interativos).
- **Frontend:** Streamlit (UI/UX focado em tomada de decisão rápida).
- **Arquitetura:** Separação entre Treino (`train_model.py`) e Inferência (`app.py`) para latência zero.

---

## 🚦 Como Usar

1. Acesse o Dashboard Online.
2. Na aba **Radar (Live)**, insira os jogos da semana (ou use o exemplo pré-carregado).
3. Ajuste sua **Banca Inicial** e **Agressividade (Kelly)** na barra lateral.
4. Siga o Semáforo:
   - 🟢 **APOSTAR:** Oportunidade Matemática Clara.
   - 🟡 **OBSERVAR:** Risco moderado.
   - 🔴 **NÃO APOSTAR:** Risco excede o prêmio matemático.

---

## ⚖️ Disclaimer (Aviso Legal)

*Este projeto é um portfólio de Data Science e Engenharia de Software. Não é uma recomendação de investimento. Apostas esportivas envolvem alto risco financeiro. O autor não se responsabiliza por perdas financeiras.*