from typing import Optional
from ..gemini_client import gemini_generate  # Correct import for subdirectory
import json
import re

def analyze_budget(income: float, expenses: dict, savings_goal: Optional[float] = None) -> dict:
    """
    Returns structured JSON for budget analysis.
    """
    prompt = (
        f"You are a financial assistant. Analyze this financial situation:\n"
        f"Monthly Income: ₹{income}\n"
        f"Expenses: {expenses}\n"
        f"Savings goal: {savings_goal if savings_goal else 'Not specified'}\n\n"
        "Provide analysis in this EXACT JSON format:\n"
        "{\n"
        '  "current_allocation": {\n'
        '    "needs_percentage": 54.0,\n'
        '    "wants_percentage": 9.0,\n'
        '    "savings_percentage": 37.0\n'
        "  },\n"
        '  "recommended_allocation_50_30_20": {\n'
        '    "needs_percentage": 50.0,\n'
        '    "wants_percentage": 30.0,\n'
        '    "savings_percentage": 20.0\n'
        "  },\n"
        '  "recommended_monthly_savings": 10000.0,\n'
        '  "tips": [\n'
        '    "You are currently saving significantly more than the recommended 20% of your income!",\n'
        '    "Consider setting specific financial goals for your excess savings.",\n'
        '    "Review your needs category for potential optimizations."\n'
        "  ]\n"
        "}\n\n"
        "Calculate current allocation percentages based on:\n"
        "- Needs: rent, utilities, groceries\n"
        "- Wants: entertainment, travel, dining\n"
        "- Savings: Income - Total Expenses\n\n"
        "Return ONLY the JSON object, no other text."
    )

    try:
        response_text = gemini_generate(prompt)
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return create_fallback_response(income, expenses)
    
    # Clean the response and extract JSON
    cleaned_response = clean_json_response(response_text)
    
    try:
        data = json.loads(cleaned_response)
        
        # Validate the required structure
        if not validate_budget_structure(data):
            return create_fallback_response(income, expenses)
            
        return data
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Raw response: {response_text}")
        return create_fallback_response(income, expenses)

def clean_json_response(response_text: str) -> str:
    """Clean and extract JSON from response text"""
    if not response_text:
        return "{}"
        
    # Remove markdown code blocks
    cleaned = response_text.replace('```json', '').replace('```', '')
    
    # Extract JSON using regex
    json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if json_match:
        return json_match.group()
    
    return cleaned.strip()

def validate_budget_structure(data: dict) -> bool:
    """Validate that the response has the expected structure"""
    required_keys = [
        "current_allocation", 
        "recommended_allocation_50_30_20",
        "recommended_monthly_savings",
        "tips"
    ]
    
    if not all(key in data for key in required_keys):
        return False
        
    if not isinstance(data.get("current_allocation"), dict):
        return False
        
    if not isinstance(data.get("tips"), list):
        return False
        
    return True

def create_fallback_response(income: float, expenses: dict) -> dict:
    """Create a fallback response when JSON parsing fails"""
    total_expenses = sum(expenses.values()) if expenses else 0
    savings = income - total_expenses
    savings_percentage = (savings / income) * 100 if income > 0 else 0
    
    # Estimate needs vs wants
    needs_categories = ['rent', 'utilities', 'groceries']
    wants_categories = ['entertainment', 'travel', 'dining']
    
    needs_total = sum(expenses.get(cat, 0) for cat in needs_categories) if expenses else 0
    wants_total = sum(expenses.get(cat, 0) for cat in wants_categories) if expenses else 0
    
    needs_percentage = (needs_total / income) * 100 if income > 0 else 0
    wants_percentage = (wants_total / income) * 100 if income > 0 else 0
    
    return {
        "current_allocation": {
            "needs_percentage": float(needs_percentage),
            "wants_percentage": float(wants_percentage), 
            "savings_percentage": float(savings_percentage)
        },
        "recommended_allocation_50_30_20": {
            "needs_percentage": 50.0,
            "wants_percentage": 30.0,
            "savings_percentage": 20.0
        },
        "recommended_monthly_savings": income * 0.2,  # 20% of income
        "tips": [
            "Ensure your expenses don't exceed your income",
            "Try to save at least 20% of your monthly income", 
            "Review and categorize your expenses regularly"
        ]
    }