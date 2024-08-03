from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import  EmployeeDeposit
from home.models import AccountBalance
from accounts.models import User

@receiver(post_save, sender=AccountBalance)
def update_employee_deposit(sender, instance, **kwargs):
    user = instance.user
    if user.is_customer and user.invitation_code:
        try:
            employee = User.objects.get(invitation_code=user.invitation_code, is_employee=True)
            employee_deposit, created = EmployeeDeposit.objects.get_or_create(employee=employee)
            employee_deposit.update_deposits()
        except User.DoesNotExist:
            pass