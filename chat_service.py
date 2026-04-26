"""Chat service with Groq AI integration."""
import os
from typing import List, Dict

# Initialize Groq client from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("⚠️ GROQ_API_KEY not set. Chat will use fallback responses.")
    groq_client = None
else:
    from groq import Groq
    groq_client = Groq(api_key=GROQ_API_KEY)

# System prompt for Nexa Orion
SYSTEM_PROMPT = """Você é a Nexa Orion, uma assistente jurídica especializada em análise de contratos com IA.

Suas capacidades:
1. Criar contratos de compra e venda com desconto de 10%
2. Analisar riscos jurídicos (multa=3pts, prazo=2pts, valor=1pt)
3. Extrair cláusulas importantes (multa, prazo, pagamento)
4. Resumir contratos automaticamente
5. Calcular scores de risco (Baixo ≤3, Médio 4-6, Alto ≥7)

Quando o usuário quiser criar um contrato:
- Peça o valor da negociação
- Explique que aplicará 10% de desconto
- Mencione que analisará risco automaticamente

Quando analisar risco:
- Explique o sistema de pontuação
- Dê recomendações baseadas no nível de risco
- Sugira melhorias no contrato se necessário

Seja profissional, clara e objetiva. Use linguagem jurídica acessível.
Responda em português do Brasil."""

# Conversation history storage (in-memory, per session)
_conversations: Dict[str, List[Dict]] = {}


def get_chat_response(message: str, session_id: str = "default") -> str:
    """Get AI response from Groq with conversation context.
    
    Args:
        message: User message
        session_id: Session identifier for conversation history
        
    Returns:
        AI response text
    """
    # Fallback if Groq not configured
    if groq_client is None:
        return get_fallback_response(message)
    
    # Initialize conversation if new
    if session_id not in _conversations:
        _conversations[session_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    
    # Add user message
    _conversations[session_id].append({"role": "user", "content": message})
    
    # Keep only last 20 messages to prevent token overflow
    if len(_conversations[session_id]) > 20:
        _conversations[session_id] = [
            _conversations[session_id][0]  # Keep system prompt
        ] + _conversations[session_id][-19:]  # Keep last 19 messages
    
    try:
        # Call Groq API
        chat_completion = groq_client.chat.completions.create(
            messages=_conversations[session_id],
            model="llama3-8b-8192",  # Fast and capable model
            temperature=0.7,
            max_tokens=2048,
            top_p=0.9,
        )
        
        # Extract response
        response = chat_completion.choices[0].message.content
        
        # Add assistant response to history
        _conversations[session_id].append({"role": "assistant", "content": response})
        
        return response
        
    except Exception as e:
        return f"Desculpe, ocorreu um erro ao processar sua mensagem: {str(e)}. Por favor, tente novamente."


def get_fallback_response(message: str) -> str:
    """Fallback responses when Groq is not available."""
    lower = message.lower()
    
    if 'contrato' in lower or 'criar' in lower:
        return "Para criar um contrato, informe o valor da negociação. Exemplo: 'Criar contrato de R$ 50000'. O sistema aplicará 10% de desconto automaticamente."
    
    if 'risco' in lower:
        return "O sistema calcula risco baseado em: Multa (3 pts), Prazo (2 pts), Valor (1 pt). Score ≤3 = Baixo, 4-6 = Médio, ≥7 = Alto."
    
    if 'cláusula' in lower or 'clausula' in lower:
        return "Detectamos automaticamente: cláusulas de multa, prazo, pagamento e valor. Crie um contrato para ver a extração em ação!"
    
    return "Olá! Sou a Nexa Orion. Posso ajudar com: criação de contratos, análise de riscos, extração de cláusulas e resumos. Como posso ajudar?"


def clear_conversation(session_id: str = "default"):
    """Clear conversation history for a session."""
    if session_id in _conversations:
        del _conversations[session_id]


def get_conversation_history(session_id: str = "default") -> List[Dict]:
    """Get conversation history (excluding system prompt)."""
    if session_id not in _conversations:
        return []
    return [msg for msg in _conversations[session_id] if msg["role"] != "system"]
