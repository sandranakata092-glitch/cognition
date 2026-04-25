"""Automated tests for Hack Cognition MVP."""
import sys
import json
import sqlite3

# ============================================================
# 1. Unit Tests - Each module independently
# ============================================================

print("=" * 60)
print("1. TESTANDO negotiation.py")
print("=" * 60)

from negotiation import negotiate

result = negotiate({"price": 20000})
assert "CONTRATO DE COMPRA E VENDA" in result, "❌ Título do contrato não encontrado"
assert "R$ 18,000.00" in result, "❌ Preço com desconto incorreto"
assert "Multa" in result, "❌ Cláusula de multa não encontrada"
assert "Prazo" in result, "❌ Cláusula de prazo não encontrada"
print("✅ negotiate() - Contrato gerado corretamente")
print(f"   Preview: {result[:80]}...")

result_default = negotiate({})
assert "R$ 9,000.00" in result_default, "❌ Preço default incorreto"
print("✅ negotiate() - Default price (10000) funciona")

print()

# ============================================================
print("=" * 60)
print("2. TESTANDO legal_ai.py")
print("=" * 60)

from legal_ai import summarize_contract, extract_clauses

contract_text = negotiate({"price": 20000})

summary = summarize_contract(contract_text)
assert len(summary) > 10, "❌ Resumo muito curto"
assert "Contrato:" in summary, "❌ Formato do resumo incorreto"
print(f"✅ summarize_contract() - Resumo: {summary}")

clauses = extract_clauses(contract_text)
assert len(clauses) > 0, "❌ Nenhuma cláusula extraída"
clause_types = [c["type"] for c in clauses]
print(f"✅ extract_clauses() - {len(clauses)} cláusulas extraídas: {clause_types}")

# Verify specific clause types exist
assert "multa" in clause_types, "❌ Cláusula de multa não detectada"
assert "prazo" in clause_types, "❌ Cláusula de prazo não detectada"
print("✅ Cláusulas de multa e prazo detectadas corretamente")

for clause in clauses:
    assert "type" in clause, "❌ Cláusula sem campo 'type'"
    assert "text" in clause, "❌ Cláusula sem campo 'text'"
    assert len(clause["text"]) > 0, "❌ Texto da cláusula vazio"
print("✅ Todas as cláusulas têm campos válidos")

print()

# ============================================================
print("=" * 60)
print("3. TESTANDO risk_service.py")
print("=" * 60)

from risk_service import calculate_risk

# Test with multa + prazo clauses
risk = calculate_risk(clauses)
assert "score" in risk, "❌ Risco sem campo 'score'"
assert "level" in risk, "❌ Risco sem campo 'level'"
print(f"✅ calculate_risk() - Score: {risk['score']}, Level: {risk['level']}")

# Test specific scenarios
risk_low = calculate_risk([{"type": "prazo", "text": "Prazo: 30 dias"}])
assert risk_low["level"] == "Baixo", f"❌ Esperado Baixo, obtido {risk_low['level']}"
print(f"✅ Risco Baixo - 1 cláusula prazo (score={risk_low['score']})")

risk_med = calculate_risk([
    {"type": "multa", "text": "Multa: 10%"},
    {"type": "prazo", "text": "Prazo: 7 dias"}
])
assert risk_med["level"] == "Médio", f"❌ Esperado Médio, obtido {risk_med['level']}"
print(f"✅ Risco Médio - multa+prazo (score={risk_med['score']})")

risk_high = calculate_risk([
    {"type": "multa", "text": "Multa: 20%"},
    {"type": "multa", "text": "Multa adicional: 5%"},
    {"type": "prazo", "text": "Prazo: 3 dias"}
])
assert risk_high["level"] == "Alto", f"❌ Esperado Alto, obtido {risk_high['level']}"
print(f"✅ Risco Alto - 2 multas+1 prazo (score={risk_high['score']})")

print()

# ============================================================
print("=" * 60)
print("4. TESTANDO database.py")
print("=" * 60)

from database import init_db, save_contract, get_contract

# Use test database
import database
original_db = database.DB_PATH
test_db = "test_contracts.db"
database.DB_PATH = test_db

init_db()
contract_id = save_contract("Contrato de teste MVP")
assert contract_id > 0, "❌ ID do contrato inválido"
print(f"✅ save_contract() - Salvo com ID={contract_id}")

retrieved = get_contract(contract_id)
assert retrieved is not None, "❌ Contrato não encontrado"
assert retrieved["content"] == "Contrato de teste MVP", "❌ Conteúdo não confere"
print(f"✅ get_contract() - Recuperado: {retrieved['content']}")

retrieved_none = get_contract(9999)
assert retrieved_none is None, "❌ Deveria retornar None para ID inexistente"
print("✅ get_contract() - Retorna None para ID inexistente")

# Cleanup test DB (Windows requires connection to be fully closed)
import os
import time
time.sleep(0.5)
try:
    os.remove(test_db)
except PermissionError:
    pass  # File locked on Windows, not critical
database.DB_PATH = original_db

print()

# ============================================================
print("=" * 60)
print("5. TESTANDO API (via HTTP)")
print("=" * 60)

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Test health endpoint
response = client.get("/health")
assert response.status_code == 200, f"❌ Health retornou {response.status_code}"
data = response.json()
assert data["status"] == "healthy", "❌ Status não é healthy"
print(f"✅ GET /health - Status: {data['status']}")

# Test root endpoint
response = client.get("/")
assert response.status_code == 200, f"❌ Root retornou {response.status_code}"
print(f"✅ GET / - {response.json()['message']}")

# Test POST /deal
response = client.post("/deal", json={"price": 25000})
assert response.status_code == 200, f"❌ Deal retornou {response.status_code}"
data = response.json()

assert "contract_id" in data, "❌ Sem contract_id"
assert "contract" in data, "❌ Sem contract"
assert "summary" in data, "❌ Sem summary"
assert "clauses" in data, "❌ Sem clauses"
assert "risk" in data, "❌ Sem risk"
print(f"✅ POST /deal - contract_id={data['contract_id']}")

assert "CONTRATO DE COMPRA E VENDA" in data["contract"], "❌ Título não encontrado"
assert "22,500" in data["contract"], "❌ Preço incorreto no contrato"
print(f"✅ Contrato gerado com preço R$ 22,500.00")

assert len(data["summary"]) > 10, "❌ Resumo muito curto"
print(f"✅ Summary: {data['summary'][:60]}...")

assert len(data["clauses"]) > 0, "❌ Nenhuma cláusula"
clause_types = [c["type"] for c in data["clauses"]]
print(f"✅ Cláusulas: {clause_types}")

assert data["risk"]["score"] > 0, "❌ Score de risco é zero"
assert data["risk"]["level"] in ["Baixo", "Médio", "Alto"], "❌ Level de risco inválido"
print(f"✅ Risk: score={data['risk']['score']}, level={data['risk']['level']}")

# Test GET /contracts/{id}
contract_id = data["contract_id"]
response = client.get(f"/contracts/{contract_id}")
assert response.status_code == 200, f"❌ GET contract retornou {response.status_code}"
print(f"✅ GET /contracts/{contract_id} - Contrato recuperado")

# Test with default price
response = client.post("/deal", json={})
assert response.status_code == 200, "❌ Deal sem preço falhou"
data_default = response.json()
assert "9,000" in data_default["contract"], "❌ Default price incorreto"
print(f"✅ POST /deal sem preço - Default R$ 9,000.00")

print()

# ============================================================
print("=" * 60)
print("🏆 RESULTADO FINAL")
print("=" * 60)
print()
print("✅ negotiation.py  - PASSOU")
print("✅ legal_ai.py     - PASSOU")
print("✅ risk_service.py  - PASSOU")
print("✅ database.py      - PASSOU")
print("✅ API Endpoints    - PASSOU")
print()
print("🎉 TODOS OS TESTES PASSARAM - MVP FUNCIONAL!")
