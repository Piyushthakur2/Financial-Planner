document.getElementById('financeForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
     

    const income = parseFloat(document.getElementById('income').value);
    const expensesText = document.getElementById('expenses').value;
    
    // Calculate total expenses from input
    let totalExpenses = 0;
    if (expensesText) {
        expensesText.split(',').forEach(pair => {
            if (pair.includes(':')) {
                const parts = pair.split(':');
                if (parts.length === 2) {
                    const value = parseFloat(parts[1].trim());
                    if (!isNaN(value)) {
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
            return; // Stop the form submission
        }
    }
    
    const analyzeBtn = document.getElementById('analyzeBtn');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    
    // Show loading, hide results
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
    loading.classList.remove('hidden');
    results.classList.add('hidden');
    
    try {
        const formData = new FormData(this);
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data.results);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Failed to analyze finances: ' + error.message);
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<i class="fas fa-chart-pie"></i> Analyze My Finances';
        loading.classList.add('hidden');
    }
});

function displayResults(results) {
    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = '<h2><i class="fas fa-file-alt"></i> Your Financial Analysis</h2>';
    
    // Budget Plan
    if (results.budget_plan) {
        resultsContainer.innerHTML += createBudgetPlanCard(results.budget_plan);
    }
    
    // Investment Plan
    if (results.investment_plan) {
        resultsContainer.innerHTML += createInvestmentPlanCard(results.investment_plan);
    }
    
    // Expense Optimizations
    if (results.expense_optimizations) {
        resultsContainer.innerHTML += createExpenseOptimizationsCard(results.expense_optimizations);
    }
    
    // Debt Plan
    if (results.debt_plan) {
        resultsContainer.innerHTML += createDebtPlanCard(results.debt_plan);
    }
    
    // Health Score
    if (results.financial_health_score !== undefined) {
        resultsContainer.innerHTML += createHealthScoreCard(results.financial_health_score);
    }
    
    resultsContainer.classList.remove('hidden');
}

function createBudgetPlanCard(budgetPlan) {
    // Format percentages to avoid long decimals
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
                        ${budgetPlan.current_allocation ? `
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
                        ` : '<p>No allocation data</p>'}
                    </div>
                    <div class="grid-item">
                        <h4>Recommended (50/30/20)</h4>
                        ${budgetPlan.recommended_allocation_50_30_20 ? `
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
                        ` : '<p>No recommended data</p>'}
                    </div>
                </div>
                
                <div class="savings-box">
                    <strong>Recommended Monthly Savings:</strong> 
                    <span style="font-size: 1.8rem; font-weight: 700; margin-left: 10px;">
                        ₹${budgetPlan.recommended_monthly_savings?.toLocaleString() || 0}
                    </span>
                </div>
                
                <div style="background: #e8f4f8; padding: 20px; border-radius: 10px; border-left: 4px solid #3498db;">
                    <h4><i class="fas fa-lightbulb"></i> Financial Tips</h4>
                    <ul>
                        ${(budgetPlan.tips || ['No tips available']).map(tip => `<li>${tip}</li>`).join('')}
                    </ul>
                </div>
            </div>
        </div>
    `;
}

function createInvestmentPlanCard(investmentPlan) {
    return `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title"><i class="fas fa-chart-line"></i> Investment Plan</h3>
            </div>
            <div class="card-content">
                <h4>Portfolio Allocation</h4>
                <div class="portfolio-grid">
                    ${(investmentPlan.portfolio || []).map(item => `
                        <div class="portfolio-item">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                <span style="font-weight: 600;">${item.asset}</span>
                                <span style="background: #3498db; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.9rem;">
                                    ${item['allocation%']}%
                                </span>
                            </div>
                            <div style="font-size: 1.3rem; font-weight: 700; color: #27ae60; margin-bottom: 8px;">
                                ₹${(item.amount || 0).toLocaleString()}
                            </div>
                            <div style="color: #7f8c8d; font-size: 0.9rem;">
                                ${item.notes || 'No description'}
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
    if (!optimizations || optimizations.length === 0) {
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
                ${optimizations.map(opt => `
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
    if (!debtPlan) {
        return '';
    }
    
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
    // Ensure score is a number and within bounds
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