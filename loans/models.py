from django.db import models
from customers.models import Customer


class Loan(models.Model):
    """Loan model representing loans taken by customers."""
    loan_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loans')
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tenure = models.IntegerField(help_text="Tenure in months")
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    monthly_repayment = models.DecimalField(max_digits=12, decimal_places=2)
    emis_paid_on_time = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'loans'
        ordering = ['-loan_id']

    def __str__(self):
        return f"Loan {self.loan_id} - Customer {self.customer.customer_id}"

    @property
    def repayments_left(self):
        """Calculate number of EMIs left."""
        from django.utils import timezone
        from dateutil.relativedelta import relativedelta
        
        today = timezone.now().date()
        
        if today >= self.end_date:
            return 0
        
        # Calculate months passed since start
        months_passed = (today.year - self.start_date.year) * 12 + (today.month - self.start_date.month)
        
        # EMIs left = total tenure - months passed
        emis_left = max(0, self.tenure - months_passed)
        return emis_left
