import re
from typing import List, Dict


def summarize_contract(text: str) -> str:
    """Generate a summary of the contract using simple NLP (regex-based).
    
    In Option B, this would use transformers pipeline for summarization.
    
    Args:
        text: Full contract text
        
    Returns:
        Executive summary of key points
    """
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    
    # Extract key points (lines containing important keywords)
    keywords = ['valor', 'pagamento', 'multa', 'prazo', 'entrega', 'preço']
    key_points = []
    
    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in keywords):
            # Clean up the line
            clean_line = line.strip()
            if len(clean_line) > 10:  # Avoid very short lines
                key_points.append(clean_line)
    
    # Limit to first 3 key points for brevity
    summary_parts = key_points[:3]
    
    if summary_parts:
        return "Contrato: " + " | ".join(summary_parts)
    
    return "Contrato comercial padrão de compra e venda."


def extract_clauses(text: str) -> List[Dict[str, str]]:
    """Extract specific clauses from contract text using regex patterns.
    
    In Option B, this would use spaCy for NLP-based extraction.
    
    Args:
        text: Full contract text
        
    Returns:
        List of extracted clauses with type and text
    """
    clauses = []
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Check individual lines for explicit clause mentions
    for line in lines:
        line_lower = line.lower()
        
        if 'multa' in line_lower:
            clauses.append({
                "type": "multa",
                "text": line
            })
        elif 'prazo' in line_lower:
            clauses.append({
                "type": "prazo",
                "text": line
            })
    
    # Remove duplicates based on text content
    seen = set()
    unique_clauses = []
    for clause in clauses:
        text_key = clause['text'][:50].lower()
        if text_key not in seen:
            seen.add(text_key)
            unique_clauses.append(clause)
    
    return unique_clauses
