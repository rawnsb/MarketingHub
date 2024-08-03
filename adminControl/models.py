from django.db import models
from Base.models import BaseModel
from random import randint
from Employee.models import EmployeeDeposit
from accounts.models import User
import random

class WalletAddress(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallet_addresses')
    address = models.CharField(max_length=255, unique=True)  # Unique if each address can only be used by one user
    label = models.CharField(max_length=100, blank=True)  # Optional label for the address
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.label} - {self.address}"
    @staticmethod
    def get_random_wallet_address(deposit_method='USDT'):
        wallet_addresses = WalletAddress.objects.filter(label__iexact=deposit_method)
        count = wallet_addresses.count()
        if count > 0:
            random_index = randint(0, count - 1)
            return wallet_addresses[random_index].address
        return None


from django.conf import settings

class AdminDeposit(BaseModel):
    admin = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="admin")
    total_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_withdrawal=models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    last_updated = models.DateTimeField(auto_now=True)

    def update_admin_deposit(self):
        print("hello")
        employee_deposits = EmployeeDeposit.objects.all()
        self.total_deposit = sum(employee.total_deposit for employee in employee_deposits)
        self.total_withdrawal = sum(employee.total_withdrawal for employee in employee_deposits)
        self.net_deposit = self.total_deposit - self.total_withdrawal
        self.save()

    def __str__(self):
        return f"{self.admin.username}'s Admin Deposit info"


class AdminTelegram(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='telegram_accounts')
    telegram_link = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"Telegram Account for {self.user.username}"

    @staticmethod
    def get_random_telegram_link():
        telegram_links = AdminTelegram.objects.all()
        count = telegram_links.count()
        if count > 0:
            random_index = random.randint(0, count - 1)
            return telegram_links[random_index].telegram_link
        return None


import random


from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
class SimpleOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="simple_orders")
    product_name = models.CharField(max_length=300)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    product_commission = models.CharField(max_length=300)
    order_id = models.CharField(max_length=7, blank=True,null=True)
    product_img = models.ImageField(upload_to='simple_orders/', null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, editable=False)
    label = models.CharField(max_length=10)
    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = self.generate_unique_order_id()
            while SimpleOrder.objects.filter(order_id=self.order_id).exists():
                self.order_id = self.generate_unique_order_id()
        if not self.content_type:
            self.content_type = ContentType.objects.get_for_model(self.__class__)
        super(SimpleOrder, self).save(*args, **kwargs)

    @staticmethod
    def generate_unique_order_id():
        return str(random.randint(100000, 999999))

    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"


class SubmittedOrder(SimpleOrder):
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name="submitted_orders")
    is_submitted = models.BooleanField(default=False)
    check_box = models.BooleanField(default=False)
    index = models.IntegerField( null=True, blank=True)
    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}, submitted by {self.submitted_by.username if self.submitted_by else 'N/A'}"
