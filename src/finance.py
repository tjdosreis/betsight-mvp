class RiskManager:
    """
    Cérebro Financeiro (CFO Spec v1.0).
    Implementa Quarter Kelly + Hard Cap de 5%.
    """
    
    @staticmethod
    def calculate_stake(probability: float, odds: float, bankroll: float, fraction: float = 0.25, max_cap: float = 0.05) -> dict:
        """
        Calcula o aporte seguro baseado nas diretrizes do CFO.
        
        Args:
            probability (float): 0.0 a 1.0 (Confiança do Modelo)
            odds (float): Odds decimais (ex: 2.00)
            bankroll (float): Banca total atual
            fraction (float): Kelly Multiplier (Default: 0.25)
            max_cap (float): Trava de segurança máxima (Default: 0.05 = 5%)
            
        Returns:
            dict: {'stake_val': float, 'stake_pct': float, 'reason': str, 'ev': float}
        """
        # 1. Compliance e Validação
        if probability <= 0 or probability >= 1:
            return {'stake_val': 0.0, 'stake_pct': 0.0, 'reason': 'Probabilidade Inválida', 'ev': 0.0}
        if odds <= 1:
            return {'stake_val': 0.0, 'stake_pct': 0.0, 'reason': 'Odds Inválidas', 'ev': 0.0}

        # 2. Cálculo do EV (Expected Value)
        # EV = (Prob * Odds) - 1
        ev = (probability * odds) - 1
        
        if ev <= 0:
            return {
                'stake_val': 0.0, 
                'stake_pct': 0.0, 
                'reason': '⛔ EV Negativo ou Neutro (Risco sem recompensa matemática)',
                'ev': ev
            }

        # 3. Fórmula de Kelly (b*p - q) / b
        b = odds - 1
        p = probability
        q = 1 - p
        
        kelly_full = (b * p - q) / b
        
        # 4. Aplicação do Quarter Kelly (0.25)
        kelly_fractional = kelly_full * fraction
        
        # 5. Hard Cap (Trava de Segurança de 5%)
        # O sistema escolhe o MENOR valor entre o Kelly Fracionado e o Teto.
        final_stake_pct = min(kelly_fractional, max_cap)
        final_stake_pct = max(0.0, final_stake_pct) # Garante que não seja negativo
        
        # 6. Conversão Monetária
        stake_val = bankroll * final_stake_pct
        
        return {
            'stake_val': round(stake_val, 2),
            'stake_pct': round(final_stake_pct * 100, 2),
            'reason': '✅ Aposta Aprovada (Otimizada)',
            'ev': ev
        }