from typing import Optional
from gemini_client import gemini_generate
import json
import re

def financial_health_score(income: float, expenses: dict, debt: float, savings_goal: Optional[float] = None) -> int:
    """
    Returns an integer financial health score (0-100).
    """
    prompt = (
        f"Calculate a financial health score (0-100) based on:\n"
        f"Monthly Income: ₹{income}\n"
        f"Expenses: {expenses}\n"
        f"Debt: ₹{debt}\n"
        f"Savings goal: {savings_goal if savings_goal else 'Not specified'}\n\n"
        "Return ONLY this EXACT JSON format:\n"
        "{\n"
        '  "score": 75\n'
        "}\n\n"
        "Scoring guidelines:\n"
        "- 80-100: Excellent (low debt, high savings, good income-to-expense ratio)\n"
        "- 60-79: Good (manageable debt, reasonable savings)\n"
        "- 40-59: Fair (high debt or low savings)\n"
        "- 0-39: Poor (financial stress indicators)\n\n"
        "Return ONLY the JSON object, no other text."
    )

    try:
        response_text = gemini_generate(prompt)
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return calculate_fallback_score(income, expenses, debt)
    
    # Clean the response and extract JSON
    cleaned_response = clean_json_response(response_text)
    
    try:
        data = json.loads(cleaned_response)
        
        # Validate the required structure
        if not validate_health_structure(data):
            return calculate_fallback_score(income, expenses, debt)
            
        score = int(data.get("score", 70))
        # Ensure score is between 0 and 100
        return max(0, min(score, 100))
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Raw response: {response_text}")
        return calculate_fallback_score(income, expenses, debt)

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

def validate_health_structure(data: dict) -> bool:
    """Validate that the response has the expected structure"""
    if not isinstance(data, dict):
        return False
        
    if "score" not in data:
        return False
        
    if not isinstance(data.get("score"), (int, float)):
        return False
        
    return True

def calculate_fallback_score(income: float, expenses: dict, debt: float) -> int:
    """Calculate a fallback financial health score"""
    if income <= 0:
        return 0
    
    total_expenses = sum(expenses.values()) if expenses else 0
    
    # Calculate basic ratios
    savings_ratio = (income - total_expenses) / income
    debt_ratio = debt / income if income > 0 else 1
    
    # Base score components
    savings_score = min(50, savings_ratio * 100)  # Max 50 points for savings
    debt_score = max(0, 30 - (debt_ratio * 30))  # Up to 30 points, reduced by debt
    expense_ratio = total_expenses / income
    expense_score = max(0, 20 - (expense_ratio * 10))  # Up to 20 points for reasonable expenses
    
    total_score = savings_score + debt_score + expense_score
    
    # Ensure score is between 0 and 100
    return max(0, min(int(total_score), 100))