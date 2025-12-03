import streamlit as st
import pandas as pd
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="BetSight MVP",
    page_icon="🎯",
    layout="wide"
)

def main():
    st.title("🎯 BetSight MVP - Sprint 1")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("✅ DEPLOY REALIZADO COM SUCESSO")
        st.write("O pipeline de CI/CD via GitHub Web funcionou.")
        
    with col2:
        st.info("📊 Status do Ambiente")
        st.write(f"Pandas Version: {pd.__version__}")
        st.write(f"Numpy Version: {np.__version__}")

    st.warning("⚠️ Próximo passo: Sincronizar seu VS Code local (git pull).")

if __name__ == "__main__":
    main()
