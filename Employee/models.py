from Base.models import BaseModel
from django.db import models
from django.conf import settings
from accounts.models import User
class EmployeeDeposit(BaseModel):
    employee = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employee_deposit")
    total_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_withdrawal=models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    last_updated = models.DateTimeField(auto_now=True)
    def update_deposits(self):
        referred_customers = User.objects.filter(invitation_code=self.employee.invitation_code, is_customer=True)
        total_deposit = sum(customer.balance.total_deposit for customer in referred_customers if hasattr(customer, 'balance'))
        total_withdrawal = sum(customer.balance.total_withdrawal for customer in referred_customers if hasattr(customer, 'balance'))
        self.total_deposit = total_deposit
        self.total_withdrawal=total_withdrawal
        self.net_deposit = total_deposit - total_withdrawal
        self.save()

    def __str__(self):
        return f"{self.employee.username}'s Deposit info"