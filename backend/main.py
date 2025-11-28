from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import FinanceInput  # ← CHANGED
from agents.crewai_orchestrator import FinancialCrewOrchestrator  # ← CHANGED
import os
import logging

# Add logging for production
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Personal Finance Advisor - CrewAI")

# Enable CORS - Update for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5000", 
        "http://127.0.0.1:5000",
        "https://your-frontend-url.onrender.com",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze-finance")
async def analyze(fin: FinanceInput):
    try:
        expenses = dict(fin.expenses or {})
        
        logger.info(f"🚀 Processing request with CrewAI Agentic System")
        logger.info(f"   Income: {fin.income}, Expenses: {expenses}, Debt: {fin.debt}")

        # CREWAI AGENTIC AI ORCHESTRATION
        orchestrator = FinancialCrewOrchestrator()
        
        user_data = {
            "income": fin.income,
            "expenses": expenses,
            "risk_level": fin.risk_level,
            "debt": fin.debt or 0,
            "savings_goal": fin.savings_goal or 0
        }
        
        # CrewAI handles ALL agent coordination automatically
        results = orchestrator.analyze_finances(user_data)
        
        logger.info("✅ CrewAI Agentic Analysis Completed!")
        logger.info("   🤖 Budget Analyst → Investment Advisor → Debt Specialist → Expense Optimizer")
        
        return results

    except Exception as e:
        logger.error(f"❌ Error in CrewAI analysis: {e}")
        # Fallback to direct function calls if CrewAI fails
        return await fallback_analysis(fin)

@app.get("/")
async def root():
    return {"message": "Finance AI with CrewAI - Agentic System"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "crewai": "integrated"}

@app.get("/test")
async def test_endpoint():
    return {"message": "Test endpoint working"}

# FALLBACK - Only used if CrewAI fails
async def fallback_analysis(fin: FinanceInput):
    """Fallback using direct agent calls if CrewAI fails"""
    logger.info("🔄 CrewAI failed, using fallback analysis...")
    
    try:
        from agents.budget_agent import analyze_budget  # ← CHANGED
        from agents.expenses_agent import optimize_expenses  # ← CHANGED
        from agents.investment_agent import suggest_investments  # ← CHANGED
        from agents.debt_agent import plan_debt_repayment  # ← CHANGED
        from agents.health_agent import financial_health_score  # ← CHANGED
        
        expenses = dict(fin.expenses or {})
        total_expenses = sum(expenses.values())
        monthly_investable = max(0.0, fin.income - total_expenses - (fin.debt or 0))

        # Direct function calls (old way)
        budget = analyze_budget(fin.income, expenses, fin.savings_goal)
        expense_opts = optimize_expenses(expenses)
        invest = suggest_investments(fin.risk_level, monthly_investable)
        debt_plan = plan_debt_repayment(fin.debt, fin.income)
        health = financial_health_score(fin.income, expenses, fin.debt, fin.savings_goal)
        
        # Ensure health is between 0-100
        health = max(0, min(int(health) if isinstance(health, (int, float)) else 70, 100))
        
        return {
            "budget_plan": budget,
            "expense_optimizations": expense_opts,
            "investment_plan": invest,
            "debt_plan": debt_plan,
            "financial_health_score": health,
            "crewai_used": False
        }
        
    except Exception as e:
        logger.error(f"❌ Fallback also failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add this for production deployment
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)