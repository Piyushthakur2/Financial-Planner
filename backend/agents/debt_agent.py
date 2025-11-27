from typing import Dict
from ..gemini_client import gemini_generate
import json
import re

def plan_debt_repayment(debt: float, income: float) -> Dict:
    """
    Returns structured JSON for debt planning.
    """
    prompt = (
        f"User monthly income: ₹{income}, current debt: ₹{debt}.\n"
        "Provide a JSON object with this EXACT structure:\n"
        "{\n"
        '  "status": "Debt-free",\n'
        '  "recommended_strategy": "Strategy description",\n'
        '  "estimated_months_to_clear": 0\n'
        "}\n\n"
        "Rules:\n"
        "- If debt is 0, status should be 'Debt-free' and months_to_clear should be 0\n"
        "- If debt > 0, status should be 'Has debt' and provide realistic months_to_clear\n"
        "- recommended_strategy should be practical advice\n\n"
        "Return ONLY the JSON object, no other text."
    )

    try:
        response_text = gemini_generate(prompt)
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return create_fallback_debt_response(debt, income)
    
    # Clean the response and extract JSON
    cleaned_response = clean_json_response(response_text)
    
    try:
        data = json.loads(cleaned_response)
        
        # Validate the required structure
        if not validate_debt_structure(data):
            return create_fallback_debt_response(debt, income)
            
        return data
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Raw response: {response_text}")
        return create_fallback_debt_response(debt, income)

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

def validate_debt_structure(data: dict) -> bool:
    """Validate that the response has the expected structure"""
    required_keys = [
        "status", 
        "recommended_strategy",
        "estimated_months_to_clear"
    ]
    
    if not all(key in data for key in required_keys):
        return False
        
    if not isinstance(data.get("estimated_months_to_clear"), (int, float)):
        return False
        
    return True

def create_fallback_debt_response(debt: float, income: float) -> Dict:
    """Create a fallback response when JSON parsing fails"""
    if debt == 0:
        return {
            "status": "Debt-free",
            "recommended_strategy": "Maintain your debt-free status and continue saving",
            "estimated_months_to_clear": 0
        }
    else:
        # Calculate realistic months to clear debt (assuming 20% of income for debt repayment)
        monthly_repayment = income * 0.2 if income > 0 else debt / 12
        months_to_clear = max(1, int(debt / monthly_repayment)) if monthly_repayment > 0 else 12
        
        return {
            "status": "Has debt",
            "recommended_strategy": "Pay off high-interest debt first and avoid new debt. Consider allocating 20% of income towards debt repayment.",
            "estimated_months_to_clear": months_to_clear
        }