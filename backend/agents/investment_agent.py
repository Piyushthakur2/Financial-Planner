from typing import Dict, Any
from ..gemini_client import gemini_generate
import json
import re

def suggest_investments(risk_level: str, monthly_investable: float) -> Dict[str, Any]:
    """
    Returns structured JSON for investment suggestions.
    Keys:
      - 'portfolio': list of dicts with 'asset', 'allocation%', 'amount', 'notes'
      - 'important_considerations': list of strings
    """
    prompt = (
        f"You are a financial advisor.\n"
        f"User risk level: {risk_level}\n"
        f"Monthly investable amount: ₹{monthly_investable}\n\n"
        "Return ONLY this EXACT JSON format:\n"
        "{\n"
        '  "portfolio": [\n'
        "    {\n"
        '      "asset": "Fixed Deposits",\n'
        '      "allocation%": 50,\n'
        '      "amount": 5000.0,\n'
        '      "notes": "Safe and guaranteed returns"\n'
        "    },\n"
        "    {\n"
        '      "asset": "Mutual Funds",\n'
        '      "allocation%": 30,\n'
        '      "amount": 3000.0,\n'
        '      "notes": "Balanced growth potential"\n'
        "    },\n"
        "    {\n"
        '      "asset": "Bonds",\n'
        '      "allocation%": 20,\n'
        '      "amount": 2000.0,\n'
        '      "notes": "Stable income"\n'
        "    }\n"
        "  ],\n"
        '  "important_considerations": [\n'
        '    "Diversify across asset classes",\n'
        '    "Review portfolio every 6 months",\n'
        '    "Adjust based on risk tolerance"\n'
        "  ]\n"
        "}\n\n"
        f"Adjust allocations based on risk level: {risk_level}\n"
        "Return ONLY the JSON object, no other text."
    )

    try:
        response_text = gemini_generate(prompt)
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return create_fallback_investment_response(risk_level, monthly_investable)
    
    # Clean the response and extract JSON
    cleaned_response = clean_json_response(response_text)
    
    try:
        data = json.loads(cleaned_response)
        
        # Validate the required structure
        if not validate_investment_structure(data):
            return create_fallback_investment_response(risk_level, monthly_investable)
            
        return data
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Raw response: {response_text}")
        return create_fallback_investment_response(risk_level, monthly_investable)

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

def validate_investment_structure(data: dict) -> bool:
    """Validate that the response has the expected structure"""
    required_keys = ["portfolio", "important_considerations"]
    
    if not all(key in data for key in required_keys):
        return False
        
    if not isinstance(data.get("portfolio"), list):
        return False
        
    if not isinstance(data.get("important_considerations"), list):
        return False
        
    # Validate portfolio items
    portfolio_required = ["asset", "allocation%", "amount", "notes"]
    for item in data.get("portfolio", []):
        if not all(key in item for key in portfolio_required):
            return False
            
    return True

def create_fallback_investment_response(risk_level: str, monthly_investable: float) -> Dict[str, Any]:
    """Create a fallback response when JSON parsing fails"""
    if risk_level.lower() == "high":
        portfolio = [
            {"asset": "Stocks", "allocation%": 60, "amount": monthly_investable*0.6, "notes": "High growth potential"},
            {"asset": "Mutual Funds", "allocation%": 25, "amount": monthly_investable*0.25, "notes": "Diversified equity"},
            {"asset": "Bonds", "allocation%": 15, "amount": monthly_investable*0.15, "notes": "Some stability"}
        ]
    elif risk_level.lower() == "medium":
        portfolio = [
            {"asset": "Mutual Funds", "allocation%": 50, "amount": monthly_investable*0.5, "notes": "Balanced growth"},
            {"asset": "Bonds", "allocation%": 30, "amount": monthly_investable*0.3, "notes": "Stable income"},
            {"asset": "Fixed Deposits", "allocation%": 20, "amount": monthly_investable*0.2, "notes": "Safety net"}
        ]
    else:  # low risk
        portfolio = [
            {"asset": "Fixed Deposits", "allocation%": 50, "amount": monthly_investable*0.5, "notes": "Safe returns"},
            {"asset": "Bonds", "allocation%": 30, "amount": monthly_investable*0.3, "notes": "Moderate risk"},
            {"asset": "Mutual Funds", "allocation%": 20, "amount": monthly_investable*0.2, "notes": "Balanced growth"}
        ]
    
    return {
        "portfolio": portfolio,
        "important_considerations": [
            "Diversify across asset classes",
            "Review portfolio every 6 months", 
            "Adjust based on risk tolerance",
            "Consider consulting a financial advisor"
        ]
    }