# This makes 'agents' a Python subpackage
# You can import your main classes here for easier access
from .crewai_orchestrator import FinancialCrewOrchestrator
from .budget_agent import analyze_budget
from .expenses_agent import optimize_expenses
from .investment_agent import suggest_investments
from .debt_agent import plan_debt_repayment
from .health_agent import financial_health_score

__all__ = [
    'FinancialCrewOrchestrator',
    'analyze_budget',
    'optimize_expenses',
    'suggest_investments', 
    'plan_debt_repayment',
    'financial_health_score'
]