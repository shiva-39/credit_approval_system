from rest_framework import serializers
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model."""
    
    class Meta:
        model = Customer
        fields = ['customer_id', 'first_name', 'last_name', 'age', 
                  'phone_number', 'monthly_salary', 'approved_limit', 'current_debt']
        read_only_fields = ['customer_id', 'approved_limit']


class CustomerRegistrationSerializer(serializers.Serializer):
    """Serializer for customer registration."""
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    age = serializers.IntegerField()
    monthly_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    phone_number = serializers.IntegerField()

    def create(self, validated_data):
        # Calculate approved limit: 36 * monthly_income (rounded to nearest lakh)
        monthly_income = validated_data['monthly_income']
        approved_limit = round(36 * float(monthly_income) / 100000) * 100000
        
        customer = Customer.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            age=validated_data['age'],
            monthly_salary=monthly_income,
            phone_number=validated_data['phone_number'],
            approved_limit=approved_limit,
            current_debt=0
        )
        return customer


class CustomerRegistrationResponseSerializer(serializers.Serializer):
    """Serializer for customer registration response."""
    customer_id = serializers.IntegerField()
    name = serializers.CharField()
    age = serializers.IntegerField()
    monthly_income = serializers.IntegerField()
    approved_limit = serializers.IntegerField()
    phone_number = serializers.IntegerField()


class CustomerDetailSerializer(serializers.ModelSerializer):
    """Serializer for customer details in loan view."""
    id = serializers.IntegerField(source='customer_id')
    
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'age']
