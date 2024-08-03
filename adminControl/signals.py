from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User
from Employee.models import EmployeeDeposit
from home.models import Deposit
from .models import AdminDeposit

@receiver(post_save, sender=EmployeeDeposit)
def update_admin_deposit(sender, instance, **kwargs):
    print("Deposit post_save signal triggered.")  # Debugging statement
    admin_users = User.objects.filter(is_admin=True)
    print(f"Admin users found: {admin_users.count()}")  # Debugging statement
    if admin_users.exists():
        admin_user = admin_users.first()
        print(f"Admin user: {admin_user.username}")  # Debugging statement
        admin_deposit, created = AdminDeposit.objects.get_or_create(admin=admin_user)
        admin_deposit.update_admin_deposit()
    else:
        print("No admin user found.")
