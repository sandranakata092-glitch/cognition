from typing import List, Dict


def calculate_risk(clauses: List[Dict[str, str]]) -> Dict[str, any]:
    """Calculate risk score based on extracted contract clauses.
    
    Scoring:
        - Multa clauses: +3 points each
        - Prazo clauses: +2 points each
        - Valor clauses: +1 point each
        - Other clauses: +1 point each
    
    Risk Levels:
        - 0-3: Baixo (Low)
        - 4-6: Médio (Medium)
        - 7+: Alto (High)
    
    Args:
        clauses: List of extracted clauses with 'type' and 'text' keys
        
    Returns:
        Dictionary with risk score and level
    """
    score = 0
    
    for clause in clauses:
        clause_type = clause.get("type", "").lower()
        
        if clause_type == "multa":
            score += 3
        elif clause_type == "prazo":
            score += 2
        elif clause_type == "valor":
            score += 1
        else:
            score += 1  # Default for other clause types
    
    # Determine risk level
    if score <= 3:
        level = "Baixo"
    elif score <= 6:
        level = "Médio"
    else:
        level = "Alto"
    
    return {
        "score": score,
        "level": level,
        "clause_count": len(clauses),
        "details": f"Baseado em {len(clauses)} cláusulas analisadas"
    }
