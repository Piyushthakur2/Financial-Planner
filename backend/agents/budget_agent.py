from typing import Optional
from gemini_client import gemini_generate  # Correct import for subdirectory
import json
import re

def analyze_budget(income: float, expenses: dict, savings_goal: Optional[float] = None) -> dict:
    """
    Returns structured JSON for budget analysis.
    """
    # Calculate actual savings
    total_expenses = sum(expenses.values()) if expenses else 0
    actual_savings = income - total_expenses
    actual_savings_percentage = (actual_savings / income) * 100 if income > 0 else 0
    
    prompt = (
        f"You are a financial assistant. Analyze this financial situation:\n"
        f"Monthly Income: ₹{income}\n"
        f"Expenses: {expenses}\n"
        f"Total Expenses: ₹{total_expenses}\n"
        f"Actual Monthly Savings: ₹{actual_savings} ({actual_savings_percentage:.1f}% of income)\n"
        f"Savings goal: {savings_goal if savings_goal else 'Not specified'}\n\n"
        f"IMPORTANT: Recommend maintaining their current savings rate of {actual_savings_percentage:.1f}%.\n\n"
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
        f'  "recommended_monthly_savings": {actual_savings},\n'  # 🎯 JUST ACTUAL SAVINGS
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
        
        # 🎯 CORRECT: JUST USE ACTUAL SAVINGS
        data["recommended_monthly_savings"] = float(actual_savings)
        
        # Update tips if user is saving exceptionally well
        if actual_savings_percentage > 50:
            data["tips"] = [
                f"Exceptional! You're saving {actual_savings_percentage:.1f}% of your income (₹{actual_savings})",
                "Consider investing your substantial savings for better returns",
                "You're saving much more than the typical 20% target - excellent discipline!",
                "Focus on investment strategies rather than basic savings advice"
            ]
            
        return data
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Raw response: {response_text}")
        return create_fallback_response(income, expenses)
    """
    Returns structured JSON for budget analysis.
    """
    # 🚨 CALCULATE ACTUAL SAVINGS FIRST
    total_expenses = sum(expenses.values()) if expenses else 0
    actual_savings = income - total_expenses
    actual_savings_percentage = (actual_savings / income) * 100 if income > 0 else 0
    
    prompt = (
        f"You are a financial assistant. Analyze this financial situation:\n"
        f"Monthly Income: ₹{income}\n"
        f"Expenses: {expenses}\n"
        f"Total Expenses: ₹{total_expenses}\n"
        f"Actual Monthly Savings: ₹{actual_savings} ({actual_savings_percentage:.1f}% of income)\n"
        f"Savings goal: {savings_goal if savings_goal else 'Not specified'}\n\n"
        f"IMPORTANT: If the user is saving more than 20% (₹{income * 0.2}), acknowledge this "
        f"and recommend maintaining their excellent savings rate of {actual_savings_percentage:.1f}%.\n\n"
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
        f'  "recommended_monthly_savings": {max(actual_savings, income * 0.2)},\n'  # 🚨 KEY FIX
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
        
        # 🚨 CRITICAL: ENSURE we use actual savings if it's higher
        data["recommended_monthly_savings"] = float(max(
            data.get("recommended_monthly_savings", income * 0.2),
            actual_savings  # This ensures we never recommend LESS than what user already saves
        ))
        
        # 🚨 Update tips if user is saving exceptionally well
        if actual_savings_percentage > 50:
            data["tips"] = [
                f"Exceptional! You're saving {actual_savings_percentage:.1f}% of your income (₹{actual_savings})",
                "Consider investing your substantial savings for better returns",
                "You're saving much more than the typical 20% target - excellent discipline!",
                "Focus on investment strategies rather than basic savings advice"
            ]
            
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
    actual_savings = income - total_expenses
    savings_percentage = (actual_savings / income) * 100 if income > 0 else 0
    
    # Estimate needs vs wants
    needs_categories = ['rent', 'utilities', 'groceries']
    wants_categories = ['entertainment', 'travel', 'dining']
    
    needs_total = sum(expenses.get(cat, 0) for cat in needs_categories) if expenses else 0
    wants_total = sum(expenses.get(cat, 0) for cat in wants_categories) if expenses else 0
    
    needs_percentage = (needs_total / income) * 100 if income > 0 else 0
    wants_percentage = (wants_total / income) * 100 if income > 0 else 0
    
    # 🎯 CORRECT: JUST USE ACTUAL SAVINGS
    recommended_savings = actual_savings
    
    # Smart tips based on actual situation
    if savings_percentage > 50:
        tips = [
            f"Excellent! You're saving {savings_percentage:.1f}% of your income",
            "Consider investing your excess savings for better returns",
            "You're well ahead of the typical 20% savings goal"
        ]
    elif savings_percentage >= 20:
        tips = [
            f"Good job! You're saving {savings_percentage:.1f}% of your income",
            "You're meeting or exceeding the recommended savings rate",
            "Consider automating your savings for consistency"
        ]
    else:
        tips = [
            f"Current savings: {savings_percentage:.1f}% (₹{actual_savings})",
            "Review your expenses to identify savings opportunities",
            "Even small increases in savings can make a big difference over time"
        ]
    
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
        "recommended_monthly_savings": float(recommended_savings),  # 🎯 Just actual savings
        "tips": tips
    }