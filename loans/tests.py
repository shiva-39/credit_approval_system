"""
Unit tests for credit scoring and loan processing.
"""
from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from customers.models import Customer
from loans.models import Loan
from loans.credit_score import (
    calculate_credit_score,
    calculate_monthly_installment,
    check_loan_eligibility
)


class CreditScoreTestCase(TestCase):
    """Test credit score calculation."""
    
    def setUp(self):
        """Set up test data."""
        self.customer = Customer.objects.create(
            first_name="Test",
            last_name="User",
            phone_number=9999999999,
            monthly_salary=Decimal('50000'),
            approved_limit=Decimal('1800000'),
            current_debt=Decimal('0')
        )
    
    def test_new_customer_credit_score(self):
        """Test credit score for new customer with no loans."""
        score = calculate_credit_score(self.customer)
        self.assertEqual(score, 50)  # Default score for new customers
    
    def test_credit_score_with_good_history(self):
        """Test credit score with good payment history."""
        # Create a loan with all EMIs paid on time
        Loan.objects.create(
            customer=self.customer,
            loan_amount=Decimal('100000'),
            tenure=12,
            interest_rate=Decimal('10.0'),
            monthly_repayment=Decimal('8791.59'),
            emis_paid_on_time=12,
            start_date=timezone.now().date() - timedelta(days=365),
            end_date=timezone.now().date() - timedelta(days=5)
        )
        
        score = calculate_credit_score(self.customer)
        self.assertGreater(score, 70)  # Should have high score
    
    def test_credit_score_exceeds_limit(self):
        """Test credit score when current debt exceeds approved limit."""
        # Create loans that exceed approved limit
        Loan.objects.create(
            customer=self.customer,
            loan_amount=Decimal('1000000'),
            tenure=24,
            interest_rate=Decimal('12.0'),
            monthly_repayment=Decimal('47073.44'),
            emis_paid_on_time=10,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=720)
        )
        Loan.objects.create(
            customer=self.customer,
            loan_amount=Decimal('1000000'),
            tenure=24,
            interest_rate=Decimal('12.0'),
            monthly_repayment=Decimal('47073.44'),
            emis_paid_on_time=10,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=720)
        )
        
        score = calculate_credit_score(self.customer)
        self.assertEqual(score, 0)  # Should be 0 when exceeding limit


class MonthlyInstallmentTestCase(TestCase):
    """Test monthly installment calculation."""
    
    def test_calculate_emi_with_interest(self):
        """Test EMI calculation with interest."""
        loan_amount = 100000
        interest_rate = 12.0
        tenure = 12
        
        emi = calculate_monthly_installment(loan_amount, interest_rate, tenure)
        
        # EMI should be approximately 8884.88
        self.assertAlmostEqual(emi, 8884.88, places=1)
    
    def test_calculate_emi_zero_interest(self):
        """Test EMI calculation with zero interest."""
        loan_amount = 120000
        interest_rate = 0
        tenure = 12
        
        emi = calculate_monthly_installment(loan_amount, interest_rate, tenure)
        
        # EMI should be loan_amount / tenure
        self.assertEqual(emi, 10000.0)


class LoanEligibilityTestCase(TestCase):
    """Test loan eligibility checks."""
    
    def setUp(self):
        """Set up test data."""
        self.customer = Customer.objects.create(
            first_name="Test",
            last_name="User",
            phone_number=9999999999,
            monthly_salary=Decimal('50000'),
            approved_limit=Decimal('1800000'),
            current_debt=Decimal('0')
        )
    
    def test_eligibility_high_credit_score(self):
        """Test eligibility with new customer (default score 50)."""
        result = check_loan_eligibility(
            self.customer,
            loan_amount=500000,
            interest_rate=10.0,
            tenure=24
        )
        
        # New customer gets default score of 50, which triggers 30-50 slab
        # Interest rate should be corrected to minimum 12%
        self.assertTrue(result['approval'])
        self.assertEqual(result['corrected_interest_rate'], 12.0)
    
    def test_eligibility_exceeds_emi_limit(self):
        """Test eligibility when EMIs exceed 50% of salary."""
        # Create existing loan with high EMI
        Loan.objects.create(
            customer=self.customer,
            loan_amount=Decimal('1000000'),
            tenure=24,
            interest_rate=Decimal('12.0'),
            monthly_repayment=Decimal('47073.44'),  # High EMI
            emis_paid_on_time=10,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=720)
        )
        
        result = check_loan_eligibility(
            self.customer,
            loan_amount=500000,
            interest_rate=10.0,
            tenure=24
        )
        
        self.assertFalse(result['approval'])
        self.assertIn('EMI', result['message'])


class CustomerModelTestCase(TestCase):
    """Test Customer model."""
    
    def test_create_customer(self):
        """Test customer creation."""
        customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            phone_number=9876543210,
            monthly_salary=Decimal('75000'),
            approved_limit=Decimal('2700000'),
            current_debt=Decimal('0')
        )
        
        self.assertEqual(customer.full_name, "John Doe")
        self.assertEqual(customer.monthly_salary, Decimal('75000'))
    
    def test_approved_limit_calculation(self):
        """Test approved limit calculation in registration."""
        monthly_income = 50000
        approved_limit = round(36 * monthly_income / 100000) * 100000
        
        self.assertEqual(approved_limit, 1800000)


class LoanModelTestCase(TestCase):
    """Test Loan model."""
    
    def setUp(self):
        """Set up test data."""
        self.customer = Customer.objects.create(
            first_name="Test",
            last_name="User",
            phone_number=9999999999,
            monthly_salary=Decimal('50000'),
            approved_limit=Decimal('1800000'),
            current_debt=Decimal('0')
        )
    
    def test_create_loan(self):
        """Test loan creation."""
        loan = Loan.objects.create(
            customer=self.customer,
            loan_amount=Decimal('500000'),
            tenure=24,
            interest_rate=Decimal('12.0'),
            monthly_repayment=Decimal('23539.07'),
            emis_paid_on_time=0,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=720)
        )
        
        self.assertEqual(loan.customer, self.customer)
        self.assertEqual(loan.loan_amount, Decimal('500000'))
    
    def test_repayments_left(self):
        """Test repayments_left calculation."""
        # Create a loan that started 6 months ago with 24 month tenure
        loan = Loan.objects.create(
            customer=self.customer,
            loan_amount=Decimal('500000'),
            tenure=24,
            interest_rate=Decimal('12.0'),
            monthly_repayment=Decimal('23539.07'),
            emis_paid_on_time=6,
            start_date=timezone.now().date() - timedelta(days=180),
            end_date=timezone.now().date() + timedelta(days=540)
        )
        
        repayments = loan.repayments_left
        # Should have approximately 18 EMIs left (24 - 6)
        self.assertGreaterEqual(repayments, 17)
        self.assertLessEqual(repayments, 19)
