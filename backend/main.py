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
        
        # 🚨 ADD DEBUG CALCULATIONS
        total_expenses = sum(expenses.values())
        actual_savings = fin.income - total_expenses
        logger.info(f"🔍 DEBUG CALCULATIONS:")
        logger.info(f"🔍 Income: ₹{fin.income}")
        logger.info(f"🔍 Expenses: ₹{total_expenses}")
        logger.info(f"🔍 Actual Savings: ₹{actual_savings}")
        logger.info(f"🔍 20% Rule: ₹{fin.income * 0.2}")
        logger.info(f"🔍 Should Recommend: ₹{max(actual_savings, fin.income * 0.2)}")

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
        
        # 🚨 CHECK FINAL RESULTS
        if 'budget_plan' in results and 'recommended_monthly_savings' in results['budget_plan']:
            logger.info(f"🎯 FINAL - Recommended Savings: ₹{results['budget_plan']['recommended_monthly_savings']}")
        
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
# FALLBACK - Only used if CrewAI fails
async def fallback_analysis(fin: FinanceInput):
    """Fallback using direct agent calls if CrewAI fails"""
    logger.info("🔄 CrewAI failed, using fallback analysis...")
    
    try:
        from agents.budget_agent import analyze_budget
        from agents.expenses_agent import optimize_expenses
        from agents.investment_agent import suggest_investments
        from agents.debt_agent import plan_debt_repayment
        from agents.health_agent import financial_health_score
        
        expenses = dict(fin.expenses or {})
        total_expenses = sum(expenses.values())
        actual_savings = fin.income - total_expenses
        
        # 🚨 DEBUG: Check what's happening
        logger.info(f"🔍 FALLBACK DEBUG:")
        logger.info(f"🔍 Income: ₹{fin.income}")
        logger.info(f"🔍 Expenses: ₹{total_expenses}")
        logger.info(f"🔍 Actual Savings: ₹{actual_savings}")
        
        # Call all agents
        budget = analyze_budget(fin.income, expenses, fin.savings_goal)
        expense_opts = optimize_expenses(expenses)  # ✅ Fixed variable name
        invest = suggest_investments(fin.risk_level, actual_savings)  # ✅ Fixed variable name
        debt_plan = plan_debt_repayment(fin.debt, fin.income)  # ✅ Fixed variable name
        health = financial_health_score(fin.income, expenses, fin.debt, fin.savings_goal)
        
        # 🚨 DEBUG: Check what the budget agent returned
        logger.info(f"🔍 Budget Agent Returned: ₹{budget.get('recommended_monthly_savings')}")
        
        # 🚨 FORCE THE CORRECT VALUE
        budget["recommended_monthly_savings"] = float(actual_savings)
        logger.info(f"🚨 FORCED CORRECTION: ₹{actual_savings}")
        
        # Ensure health is between 0-100
        health = max(0, min(int(health) if isinstance(health, (int, float)) else 70, 100))
        
        return {
            "budget_plan": budget,
            "expense_optimizations": expense_opts,  # ✅ Now defined
            "investment_plan": invest,  # ✅ Now defined
            "debt_plan": debt_plan,  # ✅ Now defined
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