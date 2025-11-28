from crewai import Agent, Task, Crew, Process
from langchain_core.tools import Tool
import json
import os
import sys

# Get the absolute path to the backend directory
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)  # This goes up to backend folder
sys.path.insert(0, backend_dir)

# ✅ ABSOLUTE IMPORTS with full path
try:
    # Import gemini_client from backend folder
    from gemini_client import gemini_generate
    print("✅ Successfully imported gemini_client")
except ImportError as e:
    print(f"❌ Failed to import gemini_client: {e}")
    # Fallback function
    def gemini_generate(prompt): 
        return f"Simulated response for: {prompt}"

# Other agents use relative imports (they're in the same directory)
from .budget_agent import analyze_budget
from .investment_agent import suggest_investments
from .debt_agent import plan_debt_repayment
from .expenses_agent import optimize_expenses
from .health_agent import financial_health_score

class FinancialCrewAI:
    def __init__(self):
        self.agents = self._create_agents()
    
    def _create_agents(self):
        """Define your specialized agents"""
        
        # Budget Analyst Agent
        budget_analyst = Agent(
            role='Senior Budget Analyst',
            goal='Analyze income and expenses to create optimal budget plans using 50/30/20 rule',
            backstory="""You are an expert financial analyst with 15 years experience in 
            personal finance. You specialize in budget optimization and savings strategies. 
            You're known for creating practical, actionable budget plans.""",
            tools=[self._budget_analysis_tool],
            verbose=True,
            allow_delegation=False
        )
        
        # Investment Advisor Agent
        investment_advisor = Agent(
            role='Chief Investment Officer',
            goal='Create personalized investment portfolios based on risk profile and financial goals',
            backstory="""You are a seasoned investment advisor with expertise in portfolio 
            management. You've helped thousands of clients build wealth through smart 
            asset allocation and risk management strategies.""",
            tools=[self._investment_analysis_tool],
            verbose=True,
            allow_delegation=False
        )
        
        # Debt Management Agent
        debt_specialist = Agent(
            role='Debt Management Expert',
            goal='Develop effective debt repayment strategies and financial recovery plans',
            backstory="""You specialize in debt management and financial recovery. 
            You've helped people get out of debt faster while maintaining financial 
            stability and building emergency funds.""",
            tools=[self._debt_analysis_tool],
            verbose=True,
            allow_delegation=False
        )
        
        # Expense Optimization Agent
        expense_optimizer = Agent(
            role='Expense Optimization Specialist', 
            goal='Identify cost-saving opportunities and optimize spending habits',
            backstory="""You are an expert in expense analysis and cost optimization. 
            You have a keen eye for identifying wasteful spending and finding creative 
            ways to reduce expenses without sacrificing quality of life.""",
            tools=[self._expense_analysis_tool],
            verbose=True,
            allow_delegation=False
        )
        
        # Financial Health Agent
        health_analyst = Agent(
            role='Financial Health Assessor',
            goal='Evaluate overall financial health and provide improvement recommendations',
            backstory="""You are a certified financial health expert who assesses 
            complete financial pictures and provides actionable improvement plans.""",
            tools=[self._health_analysis_tool],
            verbose=True,
            allow_delegation=False
        )
        
        return {
            'budget_analyst': budget_analyst,
            'investment_advisor': investment_advisor,
            'debt_specialist': debt_specialist,
            'expense_optimizer': expense_optimizer,
            'health_analyst': health_analyst
        }
    
    # Tool definitions (wrap your existing functions)
    def _budget_analysis_tool(self, income: str, expenses: str) -> str:
        """Tool for budget analysis"""
        try:
            expenses_dict = json.loads(expenses) if isinstance(expenses, str) else expenses
            result = analyze_budget(float(income), expenses_dict)
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return f"Error in budget analysis: {str(e)}"
    
    def _investment_analysis_tool(self, risk_level: str, investable_amount: str) -> str:
        """Tool for investment analysis"""
        try:
            result = suggest_investments(risk_level, float(investable_amount))
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return f"Error in investment analysis: {str(e)}"
    
    def _debt_analysis_tool(self, debt: str, income: str) -> str:
        """Tool for debt analysis"""
        try:
            result = plan_debt_repayment(float(debt), float(income))
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return f"Error in debt analysis: {str(e)}"
    
    def _expense_analysis_tool(self, expenses: str) -> str:
        """Tool for expense optimization"""
        try:
            expenses_dict = json.loads(expenses) if isinstance(expenses, str) else expenses
            result = optimize_expenses(expenses_dict)
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return f"Error in expense analysis: {str(e)}"
    
    def _health_analysis_tool(self, income: str, expenses: str, debt: str) -> str:
        """Tool for health analysis"""
        try:
            expenses_dict = json.loads(expenses) if isinstance(expenses, str) else expenses
            result = financial_health_score(float(income), expenses_dict, float(debt))
            return json.dumps({"score": result}, ensure_ascii=False)
        except Exception as e:
            return f"Error in health analysis: {str(e)}"