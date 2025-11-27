from typing import List, Dict
from ..gemini_client import gemini_generate
import json
import re

def optimize_expenses(expenses: Dict[str, float]) -> List[Dict]:
    """
    Returns structured JSON for expense optimization suggestions.
    Each suggestion includes:
        - 'action': What to do
        - 'estimated_savings': Potential savings amount
        - 'reason': Why this action helps
    """
    prompt = (
        f"User monthly expenses: {expenses}.\n"
        "Provide a list of 3-5 actionable suggestions to reduce costs in this EXACT JSON format:\n"
        "[\n"
        "  {\n"
        '    "action": "Reduce spending on category",\n'
        '    "estimated_savings": 1500.0,\n'
        '    "reason": "Category is high relative to total expenses"\n'
        "  },\n"
        "  {\n"
        '    "action": "Another suggestion",\n'
        '    "estimated_savings": 800.0,\n'
        '    "reason": "Reason for this suggestion"\n'
        "  }\n"
        "]\n\n"
        "Focus on categories with highest spending first.\n"
        "Return ONLY the JSON array, no other text."
    )

    try:
        response_text = gemini_generate(prompt)
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return create_fallback_expenses_response(expenses)
    
    # Clean the response and extract JSON
    cleaned_response = clean_json_response(response_text)
    
    try:
        suggestions = json.loads(cleaned_response)
        
        # Validate the required structure
        if not validate_expenses_structure(suggestions):
            return create_fallback_expenses_response(expenses)
            
        return suggestions
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Raw response: {response_text}")
        return create_fallback_expenses_response(expenses)

def clean_json_response(response_text: str) -> str:
    """Clean and extract JSON from response text"""
    if not response_text:
        return "[]"
        
    # Remove markdown code blocks
    cleaned = response_text.replace('```json', '').replace('```', '')
    
    # Extract JSON using regex - look for array format
    json_match = re.search(r'\[.*\]', cleaned, re.DOTALL)
    if json_match:
        return json_match.group()
    
    return cleaned.strip()

def validate_expenses_structure(suggestions: list) -> bool:
    """Validate that the response has the expected structure"""
    if not isinstance(suggestions, list):
        return False
        
    required_keys = ["action", "estimated_savings", "reason"]
    
    for suggestion in suggestions:
        if not isinstance(suggestion, dict):
            return False
        if not all(key in suggestion for key in required_keys):
            return False
            
    return True

def create_fallback_expenses_response(expenses: Dict[str, float]) -> List[Dict]:
    """Create a fallback response when JSON parsing fails"""
    fallback_suggestions = []
    total_expenses = sum(expenses.values()) if expenses else 1
    
    for category, amount in expenses.items():
        if amount > total_expenses * 0.15:  # Categories spending more than 15% of total
            estimated_savings = round(amount * 0.15, 2)  # Suggest 15% reduction
            fallback_suggestions.append({
                "action": f"Reduce spending on {category}",
                "estimated_savings": estimated_savings,
                "reason": f"{category} is high relative to total expenses"
            })
    
    # If no high-spending categories found, provide general advice
    if not fallback_suggestions:
        fallback_suggestions.append({
            "action": "Review all subscriptions and recurring payments",
            "estimated_savings": 1000.0,
            "reason": "Often overlooked expenses can be optimized"
        })
        fallback_suggestions.append({
            "action": "Plan meals and reduce food waste",
            "estimated_savings": 800.0,
            "reason": "Food expenses often have optimization potential"
        })
    
    return fallback_suggestions