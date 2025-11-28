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
    
    # Calculate total expenses and ACTUAL SAVINGS
    total_expenses = sum(expenses_dict.values()) if expenses_dict else 0
    actual_savings = income - total_expenses
    savings_rate = (actual_savings / income) * 100 if income > 0 else 0
    
    print(f"🔍 TRANSFORM DEBUG - Income: ₹{income}, Expenses: ₹{total_expenses}, Savings: ₹{actual_savings} ({savings_rate:.1f}%)")
    
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
    
    # 🎯 KEY FIX: Use ACTUAL savings, not 20% rule
    recommended_savings = backend_data.get('recommended_monthly_savings', actual_savings)
    
    # Smart tips based on actual savings rate
    if savings_rate > 50:
        backend_tips = [
            f"Exceptional! You're saving {savings_rate:.1f}% of your income (₹{actual_savings:,.0f})",
            "Consider investing your substantial savings for better returns",
            "You're saving much more than the typical 20% target"
        ]
    elif savings_rate >= 20:
        backend_tips = [
            f"Good job! You're saving {savings_rate:.1f}% of your income",
            "You're meeting or exceeding savings goals",
            "Consider automating your investments"
        ]
    else:
        backend_tips = [
            f"Current savings: {savings_rate:.1f}% (₹{actual_savings:,.0f})",
            "Aim to increase savings gradually",
            "Review expenses for optimization opportunities"
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
            "recommended_monthly_savings": recommended_savings,  # 🎯 This will be correct now
            "tips": backend_tips
        },
        "investment_plan": {
            "portfolio": backend_data.get('portfolio', [
                {
                    "asset": "Emergency Fund",
                    "allocation%": 20,
                    "amount": total_expenses * 4,  # 4 months expenses
                    "notes": "Liquid cash for emergencies"
                },
                {
                    "asset": "Index Funds",
                    "allocation%": 40,
                    "amount": recommended_savings * 0.4,  # Based on ACTUAL savings
                    "notes": "Diversified stock market investment"
                },
                {
                    "asset": "Bonds",
                    "allocation%": 30,
                    "amount": recommended_savings * 0.3,  # Based on ACTUAL savings
                    "notes": "Fixed income for stability"
                },
                {
                    "asset": "Real Estate",
                    "allocation%": 10,
                    "amount": recommended_savings * 0.1,  # Based on ACTUAL savings
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
            "status": backend_data.get('debt_plan', {}).get('status', 'Excellent - Debt Free!' if debt == 0 else 'Manageable Debt'),
            "estimated_months_to_clear": backend_data.get('debt_plan', {}).get('estimated_months_to_clear', 0 if debt == 0 else max(6, int(debt / (income * 0.15)))),
            "recommended_strategy": backend_data.get('debt_plan', {}).get('recommended_strategy', 'Maintain your debt-free financial health!' if debt == 0 else 'Focus on high-interest debt first')
        },
        "financial_health_score": backend_data.get('financial_health_score', min(100, max(40, 70 + (savings_rate * 0.3))))
    }
    
    print(f"✅ TRANSFORM COMPLETE - Final savings: ₹{results['budget_plan']['recommended_monthly_savings']}")
    
    return results

    
def generate_fallback_analysis(data):
    """Generate basic analysis when backend is unavailable - matches frontend structure"""
    
    income = float(data.get('income', 0))
    expenses_dict = data.get('expenses', {})
    debt = float(data.get('debt', 0))
    risk_level = data.get('risk_level', 'Medium')
    
    # Calculate total expenses
    total_expenses = sum(expenses_dict.values()) if expenses_dict else 0
    actual_savings = income - total_expenses
    savings_rate = (actual_savings / income) * 100 if income > 0 else 0
    
    print(f"🚨 FALLBACK ACTIVATED - Income: ₹{income}, Expenses: ₹{total_expenses}, Savings: ₹{actual_savings}")
    
    # Risk-based portfolio adjustment
    risk_multiplier = 1.0
    if risk_level == 'High':
        risk_multiplier = 1.3
    elif risk_level == 'Low':
        risk_multiplier = 0.7

    # Smart tips based on actual situation
    if savings_rate > 50:
        tips = [
            f"Exceptional! You're saving {savings_rate:.1f}% of your income (₹{actual_savings:,.0f})",
            "Consider investing your substantial savings",
            "You're saving much more than typical targets"
        ]
    elif savings_rate >= 20:
        tips = [
            f"Good job! You're saving {savings_rate:.1f}% of your income",
            "You're meeting savings goals",
            "Consider automating investments"
        ]
    else:
        tips = [
            f"Current savings: {savings_rate:.1f}% (₹{actual_savings:,.0f})",
            "Aim to increase savings gradually",
            "Review expenses for optimization"
        ]

    return {
        "budget_plan": {
            "current_allocation": {
                "needs_percentage": (total_expenses / income) * 100 if income > 0 else 60,
                "wants_percentage": 0,
                "savings_percentage": savings_rate
            },
            "recommended_allocation_50_30_20": {
                "needs": 50,
                "wants": 30,
                "savings": 20
            },
            "recommended_monthly_savings": actual_savings,  # 🎯 Just actual savings
            "tips": tips
        },
        "investment_plan": {
            "portfolio": [
                {
                    "asset": "Emergency Fund",
                    "allocation%": 20,
                    "amount": total_expenses * 4,  # 4 months expenses
                    "notes": "Priority: 3-6 months living expenses"
                },
                {
                    "asset": "Stock Index Funds",
                    "allocation%": int(40 * risk_multiplier),
                    "amount": actual_savings * 0.4 * risk_multiplier,  # Based on ACTUAL savings
                    "notes": "Diversified equities based on your risk level"
                },
                {
                    "asset": "Bonds / Fixed Income",
                    "allocation%": int(30 / risk_multiplier),
                    "amount": actual_savings * 0.3 / risk_multiplier,  # Based on ACTUAL savings
                    "notes": "Stable investments for balance"
                },
                {
                    "asset": "Real Estate / Other",
                    "allocation%": 10,
                    "amount": actual_savings * 0.1,  # Based on ACTUAL savings
                    "notes": "Diversification assets"
                }
            ],
            "important_considerations": [
                "Fallback analysis - AI service unavailable",
                f"Risk level: {risk_level}",
                "Rebalance portfolio annually"
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
            }
        ],
        "debt_plan": {
            "status": "Excellent - Debt Free!" if debt == 0 else "Manageable Debt",
            "estimated_months_to_clear": 0,
            "recommended_strategy": "Maintain your debt-free financial health!" if debt == 0 else "Focus on high-interest debt first"
        },
        "financial_health_score": min(100, max(40, 70 + (savings_rate * 0.3)))
    }

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "flask-frontend"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)