def negotiate(data: dict) -> str:
    """Generate a sales contract based on negotiation data.
    
    Args:
        data: Dictionary containing negotiation parameters
              - price: Base price for the contract (default: 10000)
    
    Returns:
        Formatted contract text
    """
    price = data.get("price", 10000)
    final_price = price * 0.9  # 10% discount applied
    
    contract = f"""CONTRATO DE COMPRA E VENDA

Valor: R$ {final_price:,.2f}
Pagamento via PIX em 5 dias
Multa: 20% por cancelamento
Prazo: 7 dias para conclusão
Foro: São Paulo/SP

As partes acima identificadas têm entre si justo e acertado o presente Contrato de Compra e Venda, 
que se regerá pelas cláusulas seguintes:

1. DO OBJETO: O vendedor compromete-se a transferir a propriedade do bem ao comprador.
2. DO PREÇO: O valor total é de R$ {final_price:,.2f}, com pagamento em 5 dias via PIX.
3. DA ENTREGA: O prazo para conclusão é de 7 dias.
4. DA MULTA: Em caso de cancelamento, multa de 20% sobre o valor total.
5. DO FORO: Fica eleito o foro de São Paulo/SP para resolução de conflitos.
"""
    
    return contract.strip()
