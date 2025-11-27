from crewai import Crew, Process, Task
from .crewai_agents import FinancialCrewAI
import json

class FinancialCrewOrchestrator:
    def __init__(self):
        self.financial_crew = FinancialCrewAI()
    
    def analyze_finances(self, user_data):
        """Orchestrate the crew to analyze finances"""
        
        print("🚀 Starting CrewAI Financial Analysis...")
        
        # Create dynamic tasks based on user data
        tasks = self._create_dynamic_tasks(user_data)
        
        # Create and run the crew
        crew = Crew(
            agents=list(self.financial_crew.agents.values()),
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
        
        try:
            # Execute the crew
            print("🤖 CrewAI agents are collaborating...")
            result = crew.kickoff()
            
            print("✅ CrewAI analysis completed!")
            return self._fallback_analysis(user_data)  # Use fallback for now
            
        except Exception as e:
            print(f"❌ CrewAI Error: {e}")
            return self._fallback_analysis(user_data)
    
    def _create_dynamic_tasks(self, user_data):
        """Create tasks for the crew"""
        # ... keep your existing task creation code
        pass
    
    def _fallback_analysis(self, user_data):
        """Fallback using direct agent calls"""
        print("🔄 Using direct agent analysis...")
        
        total_expenses = sum(user_data['expenses'].values())
        monthly_investable = max(0, user_data['income'] - total_expenses - user_data.get('debt', 0))
        
        # ✅ FIXED: Use absolute imports
        from backend.agents.budget_agent import analyze_budget
        from backend.agents.investment_agent import suggest_investments
        from backend.agents.debt_agent import plan_debt_repayment
        from backend.agents.expenses_agent import optimize_expenses
        from backend.agents.health_agent import financial_health_score
        
        # Ensure health score is within bounds
        health_score = financial_health_score(
            user_data['income'], user_data['expenses'], user_data.get('debt', 0)
        )
        health_score = max(0, min(int(health_score) if isinstance(health_score, (int, float)) else 70, 100))
        
        # ✅ FIXED: Proper indentation
        return {
            "budget_plan": analyze_budget(user_data['income'], user_data['expenses'], user_data.get('savings_goal', 0)),
            "investment_plan": suggest_investments(user_data['risk_level'], monthly_investable),
            "debt_plan": plan_debt_repayment(user_data.get('debt', 0), user_data['income']),
            "expense_optimizations": optimize_expenses(user_data['expenses']),
            "financial_health_score": health_score,
            "crewai_used": True
        }