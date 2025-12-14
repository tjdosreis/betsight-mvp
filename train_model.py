# train_model.py
# Script de Automação de Treino (Data Master Pipeline)

import pandas as pd
import requests
import io
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# Configuração
SEASONS = ['2021', '2122', '2223', '2324', '2425']
BASE_URL = "https://www.football-data.co.uk/mmz4281/{}/E0.csv"
MODEL_FILENAME = "betsight_model_v1.pkl"
ENCODER_FILENAME = "team_encoder_v1.pkl"
DATA_FILENAME = "betsight_history.csv"

def run_pipeline():
    print("🚀 [1/4] Baixando dados da Inglaterra...")
    dfs = []
    for season in SEASONS:
        url = BASE_URL.format(season)
        try:
            s = requests.get(url).content
            df = pd.read_csv(io.StringIO(s.decode('unicode_escape')))
            df['Season_ID'] = season
            dfs.append(df)
            print(f"   -> Temporada {season}: OK")
        except Exception as e:
            print(f"   -> Erro {season}: {e}")
            
    full_df = pd.concat(dfs, ignore_index=True)
    
    # Limpeza
    cols = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'B365H', 'B365D', 'B365A', 'Season_ID']
    # Garante que só pega colunas que existem
    cols_exist = [c for c in cols if c in full_df.columns]
    full_df = full_df[cols_exist].dropna()
    
    full_df['Date'] = pd.to_datetime(full_df['Date'], dayfirst=True, errors='coerce')
    full_df = full_df.sort_values('Date').reset_index(drop=True)
    
    print(f"📊 [2/4] Dataset Bruto: {len(full_df)} jogos.")

    # Feature Engineering
    df_feat = full_df.copy()
    df_feat['Implied_Prob_H'] = 1 / df_feat['B365H']
    df_feat['Implied_Prob_A'] = 1 / df_feat['B365A']
    df_feat['Market_Diff'] = df_feat['Implied_Prob_H'] - df_feat['Implied_Prob_A']
    target_map = {'H': 0, 'D': 1, 'A': 2}
    df_feat['Target'] = df_feat['FTR'].map(target_map)

    # Encoder
    le = LabelEncoder()
    all_teams = pd.concat([df_feat['HomeTeam'], df_feat['AwayTeam']]).astype(str).unique()
    le.fit(all_teams)
    
    df_feat['HomeTeam_Code'] = le.transform(df_feat['HomeTeam'].astype(str))
    df_feat['AwayTeam_Code'] = le.transform(df_feat['AwayTeam'].astype(str))

    # Treino (Split)
    train_df = df_feat[df_feat['Season_ID'] != '2425']
    test_df = df_feat[df_feat['Season_ID'] == '2425']
    
    features = ['Implied_Prob_H', 'Implied_Prob_A', 'Market_Diff', 'HomeTeam_Code', 'AwayTeam_Code']
    X_train = train_df[features]
    y_train = train_df['Target']
    
    print(f"🤖 [3/4] Treinando Random Forest ({len(train_df)} amostras)...")
    model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X_train, y_train)
    
    # Validação
    if not test_df.empty:
        acc = model.score(test_df[features], test_df['Target'])
        print(f"🏆 Acurácia Temporada Atual: {acc:.2%}")

    # Exportação
    print("💾 [4/4] Salvando Artefatos (.pkl e .csv)...")
    joblib.dump(model, MODEL_FILENAME)
    joblib.dump(le, ENCODER_FILENAME)
    df_feat.to_csv(DATA_FILENAME, index=False)
    
    print("✅ PIPELINE CONCLUÍDO. PRONTO PARA DEPLOY.")

if __name__ == "__main__":
    run_pipeline()