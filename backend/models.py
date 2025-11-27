from pydantic import BaseModel
from typing import Dict, Optional, Any, List

# Input model
class FinanceInput(BaseModel):
    income: float
    expenses: Dict[str, float]
    savings_goal: Optional[float] = None
    risk_level: str = "medium"
    debt: Optional[float] = 0.0

# Output model
class FinanceOutput(BaseModel):
    budget_plan: Dict[str, Any]
    investment_plan: Dict[str, Any]
    expense_optimizations: List[Dict[str, Any]]
    debt_plan: Dict[str, Any]
    health_score: int
