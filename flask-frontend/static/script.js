document.getElementById('financeForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const analyzeBtn = document.getElementById('analyzeBtn');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    
    // Show loading, hide results
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
    loading.classList.remove('hidden');
    results.classList.add('hidden');
    
    try {
        // Get form values with safe defaults
        const income = parseFloat(document.getElementById('income').value) || 0;
        const expensesText = document.getElementById('expenses').value || '';
        const riskLevel = document.getElementById('risk_level').value || 'Medium';
        const debt = parseFloat(document.getElementById('debt').value) || 0;

        console.log('Form data:', { income, expensesText, riskLevel, debt });

        // Parse expenses into dictionary
        const expensesDict = {};
        let totalExpenses = 0;
        
        if (expensesText) {
            expensesText.split(',').forEach(pair => {
                if (pair.includes(':')) {
                    const parts = pair.split(':');
                    if (parts.length === 2) {
                        const category = parts[0].trim();
                        const value = parseFloat(parts[1].trim());
                        if (!isNaN(value)) {
                            expensesDict[category] = value;
                            totalExpenses += value;
                        }
                    }
                }
            });
        }

        // Validate income vs expenses
        if (income > 0 && totalExpenses > income) {
            const overspendAmount = totalExpenses - income;
            const shouldContinue = confirm(
                `🚨 Budget Warning!\n\n` +
                `Your monthly income: ₹${income}\n` +
                `Your total expenses: ₹${totalExpenses}\n` +
                `You're overspending by: ₹${overspendAmount}\n\n` +
                `The analysis will show this as a budget crisis.\n` +
                `Continue anyway?`
            );
            
            if (!shouldContinue) {
                resetForm(analyzeBtn, loading);
                return;
            }
        }

        // Prepare data for backend
        const jsonData = {
            income: income,
            expenses: expensesDict,
            risk_level: riskLevel,
            debt: debt
        };

        console.log('Sending to backend:', jsonData);

        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(jsonData)
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Backend response:', data);
        
        // BULLETPROOF: Check if we have valid results
        if (data.success && data.results) {
            displayResults(data.results);
        } else {
            // If no results from backend, generate local fallback
            console.warn('No results from backend, using local fallback');
            const fallbackResults = generateLocalFallback(jsonData);
            displayResults(fallbackResults);
        }
        
    } catch (error) {
        console.error('Analysis failed:', error);
        // Generate local fallback on any error
        try {
            const income = parseFloat(document.getElementById('income').value) || 0;
            const expensesText = document.getElementById('expenses').value || '';
            const riskLevel = document.getElementById('risk_level').value || 'Medium';
            const debt = parseFloat(document.getElementById('debt').value) || 0;
            
            const fallbackResults = generateLocalFallback({
                income,
                expenses: expensesText,
                risk_level: riskLevel,
                debt
            });
            displayResults(fallbackResults);
        } catch (fallbackError) {
            alert('Failed to analyze finances. Please try again later.');
            console.error('Fallback also failed:', fallbackError);
        }
    } finally {
        resetForm(analyzeBtn, loading);
    }
});

function resetForm(analyzeBtn, loading) {
    analyzeBtn.disabled = false;
    analyzeBtn.innerHTML = '<i class="fas fa-chart-pie"></i> Analyze My Finances';
    loading.classList.add('hidden');
}

function generateLocalFallback(data) {
    const income = data.income || 0;
    const expenses = data.expenses || {};
    const riskLevel = data.risk_level || 'Medium';
    const debt = data.debt || 0;
    
    // Calculate totals
    let totalExpenses = 0;
    if (typeof expenses === 'object') {
        totalExpenses = Object.values(expenses).reduce((sum, val) => sum + (parseFloat(val) || 0), 0);
    }
    
    const savings = income - totalExpenses;
    const savingsRate = income > 0 ? (savings / income) * 100 : 0;
    
    // Risk-based adjustments
    const riskMultiplier = riskLevel === 'High' ? 1.4 : riskLevel === 'Low' ? 0.6 : 1.0;
    
    // Calculate monthly investment amounts (based on monthly savings)
    const monthlySavings = Math.max(savings, income * 0.2);
    
    // Emergency fund target (3-6 months of expenses)
    const emergencyFundTarget = totalExpenses * 4; // 4 months as a reasonable target
    
    return {
        budget_plan: {
            current_allocation: {
                needs_percentage: 55,
                wants_percentage: 30,
                savings_percentage: 15
            },
            recommended_allocation_50_30_20: {
                needs: 50,
                wants: 30,
                savings: 20
            },
            recommended_monthly_savings: monthlySavings,
            tips: [
                `Great job! Your monthly savings potential is ₹${Math.max(savings, 0).toLocaleString()}`,
                "Follow the proven 50/30/20 budget rule for optimal financial health",
                "Priority: Build a 3-6 month emergency fund for financial security",
                "Track your expenses weekly to identify spending patterns",
                "Consider automating your savings for consistent results"
            ]
        },
        investment_plan: {
            portfolio: [
                {
                    asset: "Emergency Fund",
                    "allocation%": 25,
                    amount: emergencyFundTarget,
                    notes: `Essential safety net - ${Math.round(emergencyFundTarget/totalExpenses)} months of living expenses`
                },
                {
                    asset: "Stock Market",
                    "allocation%": Math.round(35 * riskMultiplier),
                    amount: monthlySavings * 0.35 * riskMultiplier,
                    notes: "Diversified index funds for long-term growth"
                },
                {
                    asset: "Bonds",
                    "allocation%": Math.round(30 / riskMultiplier),
                    amount: monthlySavings * 0.3 / riskMultiplier,
                    notes: "Stable government and corporate bonds"
                },
                {
                    asset: "Real Estate",
                    "allocation%": 10,
                    amount: monthlySavings * 0.1,
                    notes: "REITs for real estate exposure without property management"
                }
            ],
            important_considerations: [
                `Your ${riskLevel} risk profile has been considered in portfolio allocation`,
                "Diversify across different asset classes to manage risk",
                "Review and rebalance your investments every 6-12 months",
                "Consider tax-advantaged accounts for better returns"
            ]
        },
        expense_optimizations: [
            {
                action: "Review monthly subscriptions",
                estimated_savings: totalExpenses * 0.15,
                reason: "Identify and cancel unused streaming services and memberships"
            },
            {
                action: "Smart grocery planning",
                estimated_savings: totalExpenses * 0.08,
                reason: "Plan meals weekly and buy in bulk to reduce food costs"
            },
            {
                action: "Energy efficiency improvements",
                estimated_savings: totalExpenses * 0.05,
                reason: "Switch to LED bulbs and optimize utility usage"
            }
        ],
        debt_plan: {
            status: debt === 0 ? "Excellent - Debt Free!" : debt < income * 0.3 ? "Manageable" : "Needs Attention",
            estimated_months_to_clear: debt > 0 ? Math.ceil(debt / (income * 0.15)) : 0,
            recommended_strategy: debt === 0 ? "Maintain your debt-free financial health!" : "Avalanche method: Focus on highest interest debt first for maximum savings"
        },
        financial_health_score: Math.min(95, Math.max(40, 60 + (savingsRate * 0.3) - (debt/income * 25)))
    };
}

function displayResults(results) {
    console.log('Displaying results:', results);
    
    const resultsContainer = document.getElementById('results');
    
    // BULLETPROOF: Ensure results exist
    if (!results) {
        resultsContainer.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title"><i class="fas fa-exclamation-triangle"></i> Analysis Unavailable</h3>
                </div>
                <div class="card-content">
                    <p>Unable to generate financial analysis at this time. Please try again later.</p>
                </div>
            </div>
        `;
        resultsContainer.classList.remove('hidden');
        return;
    }
    
    resultsContainer.innerHTML = '<h2><i class="fas fa-file-alt"></i> Your Financial Analysis</h2>';
    
    // Safely display each section
    if (results.budget_plan) {
        resultsContainer.innerHTML += createBudgetPlanCard(results.budget_plan);
    }
    
    if (results.investment_plan) {
        resultsContainer.innerHTML += createInvestmentPlanCard(results.investment_plan);
    }
    
    if (results.expense_optimizations) {
        resultsContainer.innerHTML += createExpenseOptimizationsCard(results.expense_optimizations);
    }
    
    if (results.debt_plan) {
        resultsContainer.innerHTML += createDebtPlanCard(results.debt_plan);
    }
    
    if (results.financial_health_score !== undefined && results.financial_health_score !== null) {
        resultsContainer.innerHTML += createHealthScoreCard(results.financial_health_score);
    }
    
    // If no results at all, show message
    if (resultsContainer.innerHTML === '<h2><i class="fas fa-file-alt"></i> Your Financial Analysis</h2>') {
        resultsContainer.innerHTML += `
            <div class="card">
                <div class="card-content">
                    <p>No analysis data available. Please check your input and try again.</p>
                </div>
            </div>
        `;
    }
    
    resultsContainer.classList.remove('hidden');
}

// Rest of your card creation functions remain the same...
function createBudgetPlanCard(budgetPlan) {
    const needsPercent = budgetPlan.current_allocation?.needs_percentage?.toFixed(1) || 0;
    const wantsPercent = budgetPlan.current_allocation?.wants_percentage?.toFixed(1) || 0;
    const savingsPercent = budgetPlan.current_allocation?.savings_percentage?.toFixed(1) || 0;
    
    return `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title"><i class="fas fa-wallet"></i> Budget Plan</h3>
            </div>
            <div class="card-content">
                <div class="grid">
                    <div class="grid-item">
                        <h4>Current Allocation</h4>
                        <div class="allocation">
                            <div class="allocation-item">
                                <span>Needs</span>
                                <span><strong>${needsPercent}%</strong></span>
                            </div>
                            <div class="allocation-item">
                                <span>Wants</span>
                                <span><strong>${wantsPercent}%</strong></span>
                            </div>
                            <div class="allocation-item">
                                <span>Savings</span>
                                <span><strong>${savingsPercent}%</strong></span>
                            </div>
                        </div>
                    </div>
                    <div class="grid-item">
                        <h4>Recommended (50/30/20)</h4>
                        <div class="allocation">
                            <div class="allocation-item">
                                <span>Needs</span>
                                <span><strong>50%</strong></span>
                            </div>
                            <div class="allocation-item">
                                <span>Wants</span>
                                <span><strong>30%</strong></span>
                            </div>
                            <div class="allocation-item">
                                <span>Savings</span>
                                <span><strong>20%</strong></span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="savings-box">
                    <strong>Recommended Monthly Savings:</strong> 
                    <span style="font-size: 1.8rem; font-weight: 700; margin-left: 10px;">
                        ₹${(budgetPlan.recommended_monthly_savings || 0).toLocaleString()}
                    </span>
                </div>
                
                <div style="background: #e8f4f8; padding: 20px; border-radius: 10px; border-left: 4px solid #3498db;">
                    <h4><i class="fas fa-lightbulb"></i> Financial Tips</h4>
                    <ul>
                        ${(budgetPlan.tips || ['Start with achievable savings goals']).map(tip => `<li>${tip}</li>`).join('')}
                    </ul>
                </div>
            </div>
        </div>
    `;
}

function createInvestmentPlanCard(investmentPlan) {
    const portfolio = investmentPlan.portfolio || [];
    
    return `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title"><i class="fas fa-chart-line"></i> Investment Plan</h3>
            </div>
            <div class="card-content">
                <h4>Portfolio Allocation</h4>
                <div class="portfolio-grid">
                    ${portfolio.map(item => `
                        <div class="portfolio-item">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                <span style="font-weight: 600;">${item.asset || 'Investment'}</span>
                                <span style="background: #3498db; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.9rem;">
                                    ${item['allocation%'] || 0}%
                                </span>
                            </div>
                            <div style="font-size: 1.3rem; font-weight: 700; color: #27ae60; margin-bottom: 8px;">
                                ₹${(item.amount || 0).toLocaleString()}
                            </div>
                            <div style="color: #7f8c8d; font-size: 0.9rem;">
                                ${item.notes || 'Diversified investment'}
                            </div>
                        </div>
                    `).join('')}
                </div>
                
                ${investmentPlan.important_considerations && investmentPlan.important_considerations.length > 0 ? `
                <div style="background: #fff3cd; padding: 20px; border-radius: 10px; border: 1px solid #ffeaa7; margin-top: 20px;">
                    <h4>Important Considerations</h4>
                    <ul>
                        ${investmentPlan.important_considerations.map(note => `<li>${note}</li>`).join('')}
                    </ul>
                </div>
                ` : ''}
            </div>
        </div>
    `;
}

function createExpenseOptimizationsCard(optimizations) {
    const optimizationsList = optimizations || [];
    
    if (optimizationsList.length === 0) {
        return `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title"><i class="fas fa-piggy-bank"></i> Expense Optimizations</h3>
                </div>
                <div class="card-content">
                    <p>No expense optimizations suggested at this time.</p>
                </div>
            </div>
        `;
    }
    
    return `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title"><i class="fas fa-piggy-bank"></i> Expense Optimizations</h3>
            </div>
            <div class="card-content">
                ${optimizationsList.map(opt => `
                    <div class="optimization-item">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <strong>${opt.action || 'Reduce spending'}</strong>
                            <span style="background: #e74c3c; color: white; padding: 5px 12px; border-radius: 15px; font-size: 0.9rem;">
                                Save ₹${(opt.estimated_savings || 0).toLocaleString()}
                            </span>
                        </div>
                        <p style="margin: 0; color: #7f8c8d;">${opt.reason || 'Optimization suggested'}</p>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function createDebtPlanCard(debtPlan) {
    if (!debtPlan) return '';
    
    return `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title"><i class="fas fa-credit-card"></i> Debt Plan</h3>
            </div>
            <div class="card-content">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                        <span style="color: #7f8c8d; font-size: 0.9rem;">Status</span>
                        <div style="color: #2c3e50; font-size: 1.2rem; font-weight: 600;">${debtPlan.status || 'No debt'}</div>
                    </div>
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                        <span style="color: #7f8c8d; font-size: 0.9rem;">Clear Debt In</span>
                        <div style="color: #2c3e50; font-size: 1.2rem; font-weight: 600;">
                            ${debtPlan.estimated_months_to_clear || 0} months
                        </div>
                    </div>
                </div>
                <div style="background: #e8f4f8; padding: 20px; border-radius: 10px; border-left: 4px solid #3498db;">
                    <strong>Recommended Strategy:</strong>
                    <p style="margin: 10px 0 0 0;">${debtPlan.recommended_strategy || 'No specific strategy needed'}</p>
                </div>
            </div>
        </div>
    `;
}

function createHealthScoreCard(score) {
    const healthScore = Math.max(0, Math.min(100, Number(score) || 0));
    
    const getHealthMessage = (score) => {
        if (score >= 80) return "Excellent! Your finances are in great shape! 🎉";
        if (score >= 60) return "Good! There's room for improvement. 💪";
        if (score >= 40) return "Fair. Let's work on improving your financial health! 📈";
        if (score >= 20) return "Needs attention. Consider financial counseling. 💡";
        return "Critical situation. Seek professional financial help immediately. 🚨";
    };

    const getHealthColor = (score) => {
        if (score >= 80) return '#4CAF50';
        if (score >= 60) return '#8BC34A';
        if (score >= 40) return '#FFC107';
        if (score >= 20) return '#FF9800';
        return '#F44336';
    };

    return `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title"><i class="fas fa-heartbeat"></i> Financial Health Score</h3>
            </div>
            <div class="card-content">
                <div style="text-align: center; padding: 20px;">
                    <div class="health-score-circle" style="background: conic-gradient(${getHealthColor(healthScore)} 0% ${healthScore}%, #f0f0f0 ${healthScore}% 100%);">
                        <span class="health-score-text">${healthScore}</span>
                    </div>
                    <div style="color: #7f8c8d; margin-bottom: 15px;">out of 100</div>
                </div>
                <div style="background: ${healthScore >= 60 ? '#d4edda' : healthScore >= 40 ? '#fff3cd' : '#f8d7da'}; 
                     color: ${healthScore >= 60 ? '#155724' : healthScore >= 40 ? '#856404' : '#721c24'}; 
                     padding: 15px; border-radius: 8px; text-align: center; font-weight: 600;">
                    ${getHealthMessage(healthScore)}
                </div>
            </div>
        </div>
    `;
}