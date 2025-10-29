from rest_framework import serializers
from .models import Loan
from customers.serializers import CustomerDetailSerializer


class LoanSerializer(serializers.ModelSerializer):
    """Serializer for Loan model."""
    
    class Meta:
        model = Loan
        fields = '__all__'


class CheckEligibilityRequestSerializer(serializers.Serializer):
    """Serializer for check eligibility request."""
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField()


class CheckEligibilityResponseSerializer(serializers.Serializer):
    """Serializer for check eligibility response."""
    customer_id = serializers.IntegerField()
    approval = serializers.BooleanField()
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    corrected_interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField()
    monthly_installment = serializers.DecimalField(max_digits=12, decimal_places=2)


class CreateLoanRequestSerializer(serializers.Serializer):
    """Serializer for create loan request."""
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField()


class CreateLoanResponseSerializer(serializers.Serializer):
    """Serializer for create loan response."""
    loan_id = serializers.IntegerField(allow_null=True)
    customer_id = serializers.IntegerField()
    loan_approved = serializers.BooleanField()
    message = serializers.CharField()
    monthly_installment = serializers.DecimalField(max_digits=12, decimal_places=2)


class LoanDetailSerializer(serializers.ModelSerializer):
    """Serializer for loan detail view."""
    customer = CustomerDetailSerializer()
    
    class Meta:
        model = Loan
        fields = ['loan_id', 'customer', 'loan_amount', 'interest_rate', 
                  'monthly_repayment', 'tenure']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['monthly_installment'] = representation.pop('monthly_repayment')
        return representation


class CustomerLoansSerializer(serializers.ModelSerializer):
    """Serializer for customer loans list."""
    repayments_left = serializers.IntegerField()
    
    class Meta:
        model = Loan
        fields = ['loan_id', 'loan_amount', 'interest_rate', 'monthly_repayment', 'repayments_left']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['monthly_installment'] = representation.pop('monthly_repayment')
        return representation
