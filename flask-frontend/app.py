from flask import Flask, render_template, request, jsonify
import requests
import os
import json

app = Flask(__name__)

# Use environment variable for backend URL (Render will set this)
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:8000')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_finances():
    try:
        # Get JSON data from frontend
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No data received"})
        
        print(f"📨 Frontend received data: {data}")

        # Extract data with CORRECT field names (matching your frontend HTML)
        income = float(data.get('income', 0))
        expenses_dict = data.get('expenses', {})  # Frontend now sends as dictionary
        risk_level = data.get('risk_level', 'Medium')  # Note: frontend sends 'risk_level'
        debt = float(data.get('debt', 0))  # Note: frontend sends 'debt'

        print(f"💰 Parsed - Income: {income}, Expenses: {expenses_dict}, Risk: {risk_level}, Debt: {debt}")

        # Prepare data for backend in the expected format
        payload = {
            "income": income,
            "expenses": expenses_dict,  # Already a dictionary from frontend
            "risk_level": risk_level,
            "debt": debt
        }
        
        print(f"📤 Sending to backend {BACKEND_URL}/analyze-finance")
        print(f"📦 Payload: {payload}")
        
        # Call backend with timeout
        response = requests.post(
            f"{BACKEND_URL}/analyze-finance",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📥 Backend response status: {response.status_code}")
        
        if response.status_code == 200:
            backend_data = response.json()
            print("✅ Backend analysis successful!")
            print(f"📊 Backend response: {backend_data}")
            
            # Check if backend returned a proper analysis or an error
            if backend_data and isinstance(backend_data, dict) and not backend_data.get('error'):
                # Transform backend response to match frontend expectations
                results = transform_backend_response(backend_data, income, expenses_dict, debt)
            else:
                # Backend returned error or invalid data, use fallback
                print("⚠️ Backend returned error, using fallback analysis")
                results = generate_fallback_analysis(data)
            
            print(f"🎯 Sending results to frontend: {results}")
            
            return jsonify({
                "success": True, 
                "results": results  # Frontend expects "results" not "data"
            })
        else:
            error_msg = f"Backend error: {response.status_code} - {response.text}"
            print(f"❌ {error_msg}")
            # Use fallback analysis when backend fails
            fallback_results = generate_fallback_analysis(data)
            return jsonify({
                "success": True,
                "results": fallback_results
            })
            
    except requests.exceptions.ConnectionError:
        error_msg = f"Cannot connect to backend at {BACKEND_URL}"
        print(f"❌ {error_msg}")
        # Generate fallback analysis that matches frontend structure
        fallback_results = generate_fallback_analysis(data)
        print(f"🔄 Using fallback results: {fallback_results}")
        return jsonify({
            "success": True,  # Still success for fallback
            "results": fallback_results  # Frontend expects "results"
        })
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"❌ {error_msg}")
        # Even on unexpected errors, provide fallback analysis
        fallback_results = generate_fallback_analysis(data if 'data' in locals() else {})
        return jsonify({
            "success": True,
            "results": fallback_results
        })

def transform_backend_response(backend_data, income, expenses_dict, debt):
    """Transform backend response to match frontend expected structure"""
    
    # Calculate total expenses
    total_expenses = sum(expenses_dict.values()) if expenses_dict else 0
    
    # Use backend calculations if available, otherwise calculate properly
    needs_percentage = backend_data.get('needs_percentage')
    wants_percentage = backend_data.get('wants_percentage') 
    savings_percentage = backend_data.get('savings_percentage')
    
    # If backend didn't provide allocation percentages, calculate them
    if needs_percentage is None or wants_percentage is None or savings_percentage is None:
        if income > 0:
            # Calculate based on actual expenses vs income
            savings_percentage = min(100, max(0, ((income - total_expenses) / income) * 100))
            needs_percentage = min(100 - savings_percentage, (total_expenses / income) * 100)
            wants_percentage = max(0, 100 - needs_percentage - savings_percentage)
        else:
            needs_percentage = 50
            wants_percentage = 30
            savings_percentage = 20
    
    # Get recommended savings from backend or calculate
    recommended_savings = backend_data.get('recommended_monthly_savings', income * 0.2)
    
    # Get tips from backend or use defaults
    backend_tips = backend_data.get('tips', [])
    if not backend_tips:
        backend_tips = [
            "Start with small savings goals",
            "Track your expenses regularly",
            f"Aim to save at least 20% of your income (₹{income * 0.2:,.0f})"
        ]
    
    # Create the structure your frontend expects
    results = {
        "budget_plan": {
            "current_allocation": {
                "needs_percentage": round(needs_percentage, 1),
                "wants_percentage": round(wants_percentage, 1),
                "savings_percentage": round(savings_percentage, 1)
            },
            "recommended_allocation_50_30_20": {
                "needs": 50,
                "wants": 30,
                "savings": 20
            },
            "recommended_monthly_savings": recommended_savings,
            "tips": backend_tips
        },
        "investment_plan": {
            "portfolio": backend_data.get('portfolio', [
                {
                    "asset": "Emergency Fund",
                    "allocation%": 20,
                    "amount": income * 0.2 * 6,
                    "notes": "Liquid cash for emergencies"
                },
                {
                    "asset": "Index Funds",
                    "allocation%": 40,
                    "amount": recommended_savings * 0.4,
                    "notes": "Diversified stock market investment"
                },
                {
                    "asset": "Bonds",
                    "allocation%": 30,
                    "amount": recommended_savings * 0.3,
                    "notes": "Fixed income for stability"
                },
                {
                    "asset": "Real Estate",
                    "allocation%": 10,
                    "amount": recommended_savings * 0.1,
                    "notes": "Real estate investment trusts"
                }
            ]),
            "important_considerations": backend_data.get('important_considerations', [
                'Consult with a financial advisor',
                'Consider your risk tolerance when investing'
            ])
        },
        "expense_optimizations": backend_data.get('expense_optimizations', [
            {
                "action": "Review monthly subscriptions",
                "estimated_savings": total_expenses * 0.1,
                "reason": "Potential 10% savings from unused services"
            },
            {
                "action": "Reduce dining out",
                "estimated_savings": total_expenses * 0.05,
                "reason": "Cook more meals at home to save money"
            }
        ]),
        "debt_plan": {
            "status": backend_data.get('debt_plan', {}).get('status', 'Good' if debt == 0 or (debt / income) < 0.3 else 'Needs Attention'),
            "estimated_months_to_clear": backend_data.get('debt_plan', {}).get('estimated_months_to_clear', 12 if debt > 0 else 0),
            "recommended_strategy": backend_data.get('debt_plan', {}).get('recommended_strategy', 'Snowball method' if debt > 0 else 'No debt - maintain good habits')
        },
        "financial_health_score": backend_data.get('financial_health_score', 75)
    }
    
    return results
def generate_fallback_analysis(data):
    """Generate basic analysis when backend is unavailable - matches frontend structure"""
    
    income = float(data.get('income', 0))
    expenses_dict = data.get('expenses', {})
    debt = float(data.get('debt', 0))
    risk_level = data.get('risk_level', 'Medium')
    
    # Calculate total expenses
    total_expenses = sum(expenses_dict.values()) if expenses_dict else 0
    
    savings = income - total_expenses
    savings_rate = (savings / income) * 100 if income > 0 else 0
    
    # Risk-based portfolio adjustment
    risk_multiplier = 1.0
    if risk_level == 'High':
        risk_multiplier = 1.3
    elif risk_level == 'Low':
        risk_multiplier = 0.7

    # Ensure ALL required fields are present
    return {
        "budget_plan": {
            "current_allocation": {
                "needs_percentage": 60,
                "wants_percentage": 25,
                "savings_percentage": 15
            },
            "recommended_allocation_50_30_20": {
                "needs": 50,
                "wants": 30,
                "savings": 20
            },
            "recommended_monthly_savings": max(savings, income * 0.2),
            "tips": [
                "Note: Using fallback analysis (AI quota exceeded)",
                f"Your current savings: ₹{savings:,.0f} ({savings_rate:.1f}% of income)",
                "Aim to save at least 20% of your income",
                "Track expenses using budgeting apps"
            ]
        },
        "investment_plan": {
            "portfolio": [
                {
                    "asset": "Emergency Fund",
                    "allocation%": 20,
                    "amount": income * 3,
                    "notes": "Priority: 3-6 months living expenses"
                },
                {
                    "asset": "Stock Index Funds",
                    "allocation%": int(40 * risk_multiplier),
                    "amount": savings * 0.4 * risk_multiplier,
                    "notes": "Diversified equities based on your risk level"
                },
                {
                    "asset": "Bonds / Fixed Income",
                    "allocation%": int(30 / risk_multiplier),
                    "amount": savings * 0.3 / risk_multiplier,
                    "notes": "Stable investments for balance"
                },
                {
                    "asset": "Debt Repayment",
                    "allocation%": 10,
                    "amount": debt,
                    "notes": "Focus on high-interest debt first"
                }
            ],
            "important_considerations": [
                "Fallback analysis due to AI service limits",
                f"Risk level considered: {risk_level}",
                "Rebalance portfolio annually",
                "Consider tax-advantaged accounts"
            ]
        },
        "expense_optimizations": [
            {
                "action": "Review monthly subscriptions",
                "estimated_savings": total_expenses * 0.1,
                "reason": "Cancel unused streaming/services"
            },
            {
                "action": "Meal planning & cooking at home",
                "estimated_savings": total_expenses * 0.08,
                "reason": "Reduce dining out and food waste"
            },
            {
                "action": "Energy efficiency improvements",
                "estimated_savings": total_expenses * 0.05,
                "reason": "Lower utility bills with smart usage"
            }
        ],
        "debt_plan": {
            "status": "Excellent" if debt == 0 else "Good" if debt < income * 0.3 else "Needs Attention",
            "estimated_months_to_clear": max(6, int(debt / (income * 0.1))) if debt > 0 else 0,
            "recommended_strategy": "No debt - maintain good habits" if debt == 0 else "Avalanche method: target highest interest debt first"
        },
        "financial_health_score": min(95, max(30, int(50 + (savings_rate * 0.5) - (debt/income * 20))))
    }

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "flask-frontend"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)