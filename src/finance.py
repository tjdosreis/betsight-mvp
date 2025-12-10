class RiskManager:
    """
    Gestor de Risco para Apostas Individuais (Live).
    """
    
    @staticmethod
    def calculate_stake(probability: float, odds: float, bankroll: float, fraction: float = 0.25, max_cap: float = 0.05) -> dict:
        if probability <= 0 or odds <= 1:
            return {'stake_val': 0.0, 'stake_pct': 0.0, 'reason': 'Erro nos dados', 'ev': 0.0}

        # EV
        ev = (probability * odds) - 1
        
        if ev <= 0:
            return {
                'stake_val': 0.0, 
                'stake_pct': 0.0, 
                'reason': '⛔ EV Negativo ou Neutro',
                'ev': ev
            }

        # Kelly
        b = odds - 1
        p = probability
        q = 1 - p
        kelly_full = (b * p - q) / b
        
        # Quarter Kelly + Hard Cap
        stake_pct = kelly_full * fraction
        stake_pct = min(stake_pct, max_cap)
        stake_pct = max(0.0, stake_pct)
        
        stake_val = bankroll * stake_pct
        
        return {
            'stake_val': round(stake_val, 2),
            'stake_pct': round(stake_pct * 100, 2),
            'reason': '✅ Aposta Aprovada (Otimizada)',
            'ev': ev
        }