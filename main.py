from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any

from negotiation import negotiate
from legal_ai import summarize_contract, extract_clauses
from risk_service import calculate_risk
from database import save_contract, init_db

app = FastAPI(
    title="Hack Cognition - API Gateway",
    description="Sistema de análise de contratos com IA Jurídica",
    version="1.0.0"
)


class DealRequest(BaseModel):
    """Request model for deal processing."""
    price: float = 10000
    
    class Config:
        json_schema_extra = {
            "example": {
                "price": 20000
            }
        }


class DealResponse(BaseModel):
    """Response model for deal processing."""
    contract_id: int
    contract: str
    summary: str
    clauses: list
    risk: Dict[str, Any]


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    print("✅ Database initialized")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Hack Cognition API Gateway",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "services": {
            "api_gateway": "up",
            "database": "up",
            "legal_ai": "up (regex mode)",
            "risk_service": "up"
        }
    }


@app.post("/deal", response_model=DealResponse)
async def process_deal(data: DealRequest):
    """Process a new deal: generate contract, analyze with AI, calculate risk.
    
    Flow:
        1. Negotiation: Generate contract with 10% discount
        2. Persistence: Save to SQLite database
        3. Legal AI: Summarize and extract clauses
        4. Risk: Calculate risk score based on clauses
        5. Return: Complete analysis
    
    Args:
        data: DealRequest with price
        
    Returns:
        DealResponse with contract, summary, clauses and risk assessment
    """
    # 1. Negotiation - Generate contract
    contract = negotiate(data.model_dump())
    
    # 2. Persistence - Save to database
    contract_id = save_contract(contract)
    
    # 3. Legal AI Analysis
    summary = summarize_contract(contract)
    clauses = extract_clauses(contract)
    
    # 4. Risk Calculation
    risk = calculate_risk(clauses)
    
    # 5. Return complete response
    return DealResponse(
        contract_id=contract_id,
        contract=contract,
        summary=summary,
        clauses=clauses,
        risk=risk
    )


@app.get("/contracts/{contract_id}")
async def get_contract(contract_id: int):
    """Retrieve a saved contract by ID."""
    from database import get_contract as db_get_contract
    
    contract = db_get_contract(contract_id)
    if contract:
        return contract
    return {"error": "Contract not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
