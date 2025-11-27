from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# Use environment variable for backend URL (Render will set this)
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:8000')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_finances():
    try:
        # Get JSON data from frontend (your JavaScript sends JSON)
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No data received"})
        
        income = data.get('income', 0)
        expenses_obj = data.get('expenses', {})
        risk_level = data.get('risk_level', 'medium')
        debt = data.get('debt', 0)
        
        print(f"📨 Frontend received - Income: {income}, Expenses: {expenses_obj}")

        # Prepare data for backend
        payload = {
            "income": income,
            "expenses": expenses_obj,
            "risk_level": risk_level,
            "debt": debt,
            "savings_goal": 0
        }
        
        print(f"📤 Sending to backend: {BACKEND_URL}")
        
        # Call backend with timeout
        response = requests.post(
            f"{BACKEND_URL}/analyze-finance",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30  # Add timeout
        )
        
        print(f"📥 Backend response status: {response.status_code}")
        
        if response.status_code == 200:
            results = response.json()
            print("✅ Backend analysis successful!")
            return jsonify({
                "success": True, 
                "data": results
            })
        else:
            error_msg = f"Backend error: {response.status_code} - {response.text}"
            print(f"❌ {error_msg}")
            return jsonify({
                "success": False, 
                "error": error_msg
            })
            
    except requests.exceptions.ConnectionError:
        error_msg = f"Cannot connect to backend at {BACKEND_URL}"
        print(f"❌ {error_msg}")
        return jsonify({
            "success": False, 
            "error": error_msg,
            "data": generate_fallback_analysis(data)
        })
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"❌ {error_msg}")
        return jsonify({
            "success": False, 
            "error": error_msg
        })

def generate_fallback_analysis(data):
    """Generate basic analysis when backend is unavailable"""
    income = data.get('income', 0)
    expenses = data.get('expenses', {})
    
    total_expenses = sum(expenses.values())
    savings = income - total_expenses
    savings_rate = (savings / income) * 100 if income > 0 else 0
    
    return {
        "financial_metrics": {
            "total_income": income,
            "total_expenses": total_expenses,
            "monthly_savings": savings,
            "savings_rate": round(savings_rate, 1)
        },
        "analysis": {
            "recommendations": [
                "Using fallback analysis - backend unavailable",
                f"Monthly savings: ₹{savings:,.2f}",
                f"Savings rate: {savings_rate:.1f}%"
            ],
            "health_score": 70,
            "health_level": "needs_improvement"
        },
        "provider": "fallback"
    }

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "flask-frontend"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)  # debug=False for production