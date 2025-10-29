"""
Credit scoring utility for loan eligibility evaluation.
"""
from decimal import Decimal
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Loan


def calculate_monthly_installment(loan_amount, interest_rate, tenure):
    """
    Calculate monthly installment using compound interest formula.
    
    Formula: EMI = P × r × (1 + r)^n / ((1 + r)^n - 1)
    Where:
    - P = Principal loan amount
    - r = Monthly interest rate (annual rate / 12 / 100)
    - n = Tenure in months
    """
    if interest_rate == 0:
        return float(loan_amount) / tenure
    
    P = float(loan_amount)
    r = float(interest_rate) / (12 * 100)  # Monthly interest rate
    n = tenure
    
    # EMI calculation
    emi = P * r * pow(1 + r, n) / (pow(1 + r, n) - 1)
    
    return round(emi, 2)


def calculate_credit_score(customer):
    """
    Calculate credit score for a customer based on historical data.
    
    Components:
    1. Past Loans paid on time (30 points)
    2. Number of loans taken in past (20 points)
    3. Loan activity in current year (20 points)
    4. Loan approved volume (20 points)
    5. If sum of current loans > approved limit, score = 0 (10 points)
    
    Returns: credit_score (0-100)
    """
    loans = Loan.objects.filter(customer=customer)
    
    if not loans.exists():
        return 50  # Default score for new customers
    
    score = 0
    
    # Component 1: Past Loans paid on time (30 points)
    total_loans = loans.count()
    total_emis = loans.aggregate(total=Sum('tenure'))['total'] or 0
    total_paid_on_time = loans.aggregate(total=Sum('emis_paid_on_time'))['total'] or 0
    
    if total_emis > 0:
        on_time_ratio = total_paid_on_time / total_emis
        score += on_time_ratio * 30
    
    # Component 2: Number of loans taken in past (20 points)
    # More loans = lower score (inverse relationship)
    if total_loans == 0:
        score += 20
    elif total_loans <= 2:
        score += 20
    elif total_loans <= 5:
        score += 15
    elif total_loans <= 10:
        score += 10
    else:
        score += 5
    
    # Component 3: Loan activity in current year (20 points)
    current_year = timezone.now().year
    current_year_loans = loans.filter(start_date__year=current_year).count()
    
    if current_year_loans == 0:
        score += 20
    elif current_year_loans == 1:
        score += 15
    elif current_year_loans == 2:
        score += 10
    else:
        score += 5
    
    # Component 4: Loan approved volume (20 points)
    total_loan_amount = loans.aggregate(total=Sum('loan_amount'))['total'] or 0
    approved_limit = float(customer.approved_limit)
    
    if approved_limit > 0:
        volume_ratio = float(total_loan_amount) / approved_limit
        if volume_ratio <= 0.5:
            score += 20
        elif volume_ratio <= 1.0:
            score += 15
        elif volume_ratio <= 1.5:
            score += 10
        else:
            score += 5
    
    # Component 5: Check if sum of current loans > approved limit (10 points)
    today = timezone.now().date()
    current_loans = loans.filter(end_date__gte=today)
    current_debt = current_loans.aggregate(total=Sum('loan_amount'))['total'] or 0
    
    if float(current_debt) > approved_limit:
        return 0  # Override score to 0
    else:
        score += 10
    
    return min(100, max(0, int(score)))


def check_loan_eligibility(customer, loan_amount, interest_rate, tenure):
    """
    Check loan eligibility for a customer.
    
    Returns:
    - approval: bool
    - corrected_interest_rate: float
    - monthly_installment: float
    - message: str
    """
    credit_score = calculate_credit_score(customer)
    
    # Check if sum of current loans > approved limit
    today = timezone.now().date()
    current_loans = Loan.objects.filter(customer=customer, end_date__gte=today)
    current_debt = current_loans.aggregate(total=Sum('loan_amount'))['total'] or 0
    
    if float(current_debt) > float(customer.approved_limit):
        return {
            'approval': False,
            'corrected_interest_rate': interest_rate,
            'monthly_installment': 0,
            'message': 'Current loans exceed approved limit'
        }
    
    # Check if sum of all current EMIs > 50% of monthly salary
    current_emis_sum = current_loans.aggregate(total=Sum('monthly_repayment'))['total'] or 0
    max_emi_allowed = float(customer.monthly_salary) * 0.5
    
    # Calculate what the new EMI would be
    new_emi = calculate_monthly_installment(loan_amount, interest_rate, tenure)
    total_emi_with_new_loan = float(current_emis_sum) + new_emi
    
    if total_emi_with_new_loan > max_emi_allowed:
        return {
            'approval': False,
            'corrected_interest_rate': interest_rate,
            'monthly_installment': new_emi,
            'message': 'Total EMIs exceed 50% of monthly salary'
        }
    
    # Determine approval and corrected interest rate based on credit score
    corrected_interest_rate = interest_rate
    approval = False
    message = ''
    
    if credit_score > 50:
        approval = True
        message = 'Loan approved'
    elif credit_score > 30:
        corrected_interest_rate = max(12.0, interest_rate)
        approval = True
        message = 'Loan approved with corrected interest rate'
    elif credit_score > 10:
        corrected_interest_rate = max(16.0, interest_rate)
        approval = True
        message = 'Loan approved with corrected interest rate'
    else:
        approval = False
        corrected_interest_rate = interest_rate
        message = 'Credit score too low'
    
    # Recalculate EMI with corrected interest rate
    monthly_installment = calculate_monthly_installment(loan_amount, corrected_interest_rate, tenure)
    
    return {
        'approval': approval,
        'corrected_interest_rate': corrected_interest_rate,
        'monthly_installment': monthly_installment,
        'message': message
    }
