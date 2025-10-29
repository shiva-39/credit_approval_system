from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Customer
from .serializers import (
    CustomerRegistrationSerializer,
    CustomerRegistrationResponseSerializer
)


@api_view(['POST'])
def register_customer(request):
    """
    Register a new customer.
    
    Request body:
    - first_name: First Name of customer (string)
    - last_name: Last Name of customer (string)
    - age: Age of customer (int)
    - monthly_income: Monthly income of individual (int)
    - phone_number: Phone number (int)
    
    Response body:
    - customer_id: Id of customer (int)
    - name: Name of customer (string)
    - age: Age of customer (int)
    - monthly_income: Monthly income of individual (int)
    - approved_limit: Approved credit limit (int)
    - phone_number: Phone number (int)
    """
    serializer = CustomerRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        customer = serializer.save()
        
        response_data = {
            'customer_id': customer.customer_id,
            'name': customer.full_name,
            'age': customer.age,
            'monthly_income': int(customer.monthly_salary),
            'approved_limit': int(customer.approved_limit),
            'phone_number': customer.phone_number
        }
        
        response_serializer = CustomerRegistrationResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
