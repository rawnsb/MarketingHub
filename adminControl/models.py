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

class ExtraPictures(models.Model):
    ali_baba_logo=models.ImageField(upload_to="Logo")
    about_ist=models.ImageField(upload_to="about_pics")
    about_2nd=models.ImageField(upload_to="about_pics")
    about_3rd=models.ImageField(upload_to="about_pics")
    about_4th=models.ImageField(upload_to="about_pics")
    about_5th=models.ImageField(upload_to="about_pics")

    def __str__(self):
        return "extra pictures"





class Batch(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return self.name

class Order(models.Model):
    SIMPLE = 'Simple'
    LUCKY = 'Lucky'
    ORDER_TYPES = [
        (SIMPLE, 'Simple'),
        (LUCKY, 'Lucky')
    ]

    batch = models.ForeignKey(Batch, related_name='orders', on_delete=models.CASCADE)
    order_type = models.CharField(max_length=10, choices=ORDER_TYPES)
    product = models.ForeignKey(Product, related_name='orders', on_delete=models.CASCADE, null=True, blank=True)
    lucky_order_position = models.IntegerField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    products = models.ManyToManyField(Product, related_name='lucky_orders', blank=True)

    def __str__(self):
        return f'{self.order_type} Order - {self.product.name if self.product else "Multiple Products"}'

User.add_to_class('batches', models.ManyToManyField(Batch, related_name='users', blank=True))


# clone

class CustomerBatch(models.Model):
    user = models.ForeignKey(User, related_name='customer_batches', on_delete=models.CASCADE)
    original_batch = models.ForeignKey(Batch, related_name='customer_copies', on_delete=models.CASCADE)
    custom_batch_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Custom Batch for {self.user.username} - {self.custom_batch_name}'

class CustomerOrder(models.Model):
    id = models.BigIntegerField(primary_key=True, editable=False)
    customer_batch = models.ForeignKey(CustomerBatch, related_name='customer_orders', on_delete=models.CASCADE)
    original_order = models.ForeignKey(Order, related_name='customer_copies', on_delete=models.CASCADE)
    custom_product = models.ForeignKey(Product, related_name='custom_orders', on_delete=models.CASCADE, null=True, blank=True)
    custom_lucky_order_position = models.IntegerField(null=True, blank=True)
    custom_total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    custom_products = models.ManyToManyField(Product, related_name='custom_lucky_orders', blank=True)
    is_submitted=models.BooleanField(default=False)

    def __str__(self):
        return f'Custom Order for {self.customer_batch.user.username}'
    
    def save(self, *args, **kwargs):
        if not self.id:
            # Generate a 7-digit or 9-digit random ID
            self.id = random.randint(10000, 9999999)  # Adjust the range as needed
            # Ensure the ID is unique
            while CustomerOrder.objects.filter(id=self.id).exists():
                self.id = random.randint(1000000, 999999999)
        super().save(*args, **kwargs)