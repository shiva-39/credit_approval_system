from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from customers.models import Customer
from .models import Loan
from .serializers import (
    CheckEligibilityRequestSerializer,
    CheckEligibilityResponseSerializer,
    CreateLoanRequestSerializer,
    CreateLoanResponseSerializer,
    LoanDetailSerializer,
    CustomerLoansSerializer
)
from .credit_score import (
    check_loan_eligibility,
    calculate_monthly_installment,
    calculate_credit_score
)


@api_view(['POST'])
def check_eligibility(request):
    """
    Check loan eligibility for a customer.
    
    Request body:
    - customer_id: Id of customer (int)
    - loan_amount: Requested loan amount (float)
    - interest_rate: Interest rate on loan (float)
    - tenure: Tenure of loan in months (int)
    
    Response body:
    - customer_id: Id of customer (int)
    - approval: Can loan be approved (bool)
    - interest_rate: Interest rate on loan (float)
    - corrected_interest_rate: Corrected interest rate (float)
    - tenure: Tenure of loan (int)
    - monthly_installment: Monthly installment to be paid (float)
    """
    serializer = CheckEligibilityRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    customer_id = data['customer_id']
    loan_amount = data['loan_amount']
    interest_rate = data['interest_rate']
    tenure = data['tenure']
    
    # Get customer
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response(
            {'error': 'Customer not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check eligibility
    eligibility_result = check_loan_eligibility(
        customer, loan_amount, interest_rate, tenure
    )
    
    response_data = {
        'customer_id': customer_id,
        'approval': eligibility_result['approval'],
        'interest_rate': float(interest_rate),
        'corrected_interest_rate': float(eligibility_result['corrected_interest_rate']),
        'tenure': tenure,
        'monthly_installment': float(eligibility_result['monthly_installment'])
    }
    
    response_serializer = CheckEligibilityResponseSerializer(data=response_data)
    if response_serializer.is_valid():
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_loan(request):
    """
    Process a new loan based on eligibility.
    
    Request body:
    - customer_id: Id of customer (int)
    - loan_amount: Requested loan amount (float)
    - interest_rate: Interest rate on loan (float)
    - tenure: Tenure of loan in months (int)
    
    Response body:
    - loan_id: Id of approved loan, null otherwise (int)
    - customer_id: Id of customer (int)
    - loan_approved: Is the loan approved (bool)
    - message: Appropriate message if loan is not approved (string)
    - monthly_installment: Monthly installment to be paid (float)
    """
    serializer = CreateLoanRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    customer_id = data['customer_id']
    loan_amount = data['loan_amount']
    interest_rate = data['interest_rate']
    tenure = data['tenure']
    
    # Get customer
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response(
            {'error': 'Customer not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check eligibility
    eligibility_result = check_loan_eligibility(
        customer, loan_amount, interest_rate, tenure
    )
    
    if not eligibility_result['approval']:
        response_data = {
            'loan_id': None,
            'customer_id': customer_id,
            'loan_approved': False,
            'message': eligibility_result['message'],
            'monthly_installment': float(eligibility_result['monthly_installment'])
        }
        
        response_serializer = CreateLoanResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(response_data, status=status.HTTP_200_OK)
    
    # Create loan
    corrected_interest_rate = eligibility_result['corrected_interest_rate']
    monthly_installment = eligibility_result['monthly_installment']
    
    start_date = timezone.now().date()
    end_date = start_date + timedelta(days=tenure * 30)  # Approximate
    
    loan = Loan.objects.create(
        customer=customer,
        loan_amount=loan_amount,
        tenure=tenure,
        interest_rate=corrected_interest_rate,
        monthly_repayment=Decimal(str(monthly_installment)),
        emis_paid_on_time=0,
        start_date=start_date,
        end_date=end_date
    )
    
    # Update customer's current debt
    customer.current_debt = float(customer.current_debt) + float(loan_amount)
    customer.save()
    
    response_data = {
        'loan_id': loan.loan_id,
        'customer_id': customer_id,
        'loan_approved': True,
        'message': 'Loan approved successfully',
        'monthly_installment': float(monthly_installment)
    }
    
    response_serializer = CreateLoanResponseSerializer(data=response_data)
    if response_serializer.is_valid():
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def view_loan(request, loan_id):
    """
    View loan details and customer details.
    
    Response body:
    - loan_id: Id of approved loan (int)
    - customer: JSON containing id, first_name, last_name, phone_number, age
    - loan_amount: Loan amount (float)
    - interest_rate: Interest rate of the approved loan (float)
    - monthly_installment: Monthly installment to be paid (float)
    - tenure: Tenure of loan (int)
    """
    try:
        loan = Loan.objects.select_related('customer').get(loan_id=loan_id)
    except Loan.DoesNotExist:
        return Response(
            {'error': 'Loan not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = LoanDetailSerializer(loan)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def view_loans_by_customer(request, customer_id):
    """
    View all current loan details by customer id.
    
    Response body: List of loan items, each containing:
    - loan_id: Id of approved loan (int)
    - loan_amount: Loan amount (float)
    - interest_rate: Interest rate of the approved loan (float)
    - monthly_installment: Monthly installment to be paid (float)
    - repayments_left: No of EMIs left (int)
    """
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response(
            {'error': 'Customer not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    loans = Loan.objects.filter(customer=customer)
    
    # Add repayments_left to each loan
    loans_data = []
    for loan in loans:
        loan_serializer = CustomerLoansSerializer(loan)
        loans_data.append(loan_serializer.data)
    
    return Response(loans_data, status=status.HTTP_200_OK)
