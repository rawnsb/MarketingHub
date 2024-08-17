from django.db import models
from django.conf import settings
from Base.models import BaseModel

from django.db import models
from django.contrib.auth.models import AbstractUser
import string
import random

class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    invitation_code = models.CharField(max_length=100, blank=True,null=True, editable=False)

    def save(self, *args, **kwargs):
        if self.is_employee:
            if not self.invitation_code:
                self.invitation_code = self.generate_unique_code()
                print("Generated invite code:", self.invitation_code)  # For debugging, can be removed in production
        elif self.is_admin:
            self.invitation_code = None  # Ensure only employees have invitation codes

        super().save(*args, **kwargs)

    def generate_unique_code(self, length=6):
        """Generate a unique code."""
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        while User.objects.filter(invitation_code=code).exists():
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        return code


class Telegram(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='telegram_account')
    telegram_link = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"Telegram Account for {self.user.username}"

class UserIp(BaseModel):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='user_ip')
    ip_address=models.CharField(max_length=100)
    login_ip=models.CharField(max_length=100,blank=True)

    def __str__(self):
        return f"{self.user.username}'s Ip {self.ip_address}"

class Invite_Code(BaseModel):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='invitecode')
    invite_code = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.user.username}'s invite code{self.invite_code}"

class Profile(BaseModel):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    def __str__(self):
        return f"{self.user.username}'s image"
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
class PaymentPassword(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='payment_password')
    payment_password = models.CharField(
        max_length=10,  # You can define the required length
        validators=[
            RegexValidator(
                regex='^\d{1,10}$',  # This regex ensures the field is numeric and between 1 and 10 digits
                message='Payment password must be numeric and contain between 1 to 10 digits',  # Optional error message
            )
        ]
    )

    def __str__(self):
        return f"{self.user.username}'s payment password"

    def change_password(self, new_password):
        """
        Changes the payment password for the user, with validation.
        """
        # Validate the new password
        if not new_password.isdigit() or not 1 <= len(new_password) <= 8:
            raise ValidationError('Payment password must be numeric and contain between 1 to 10 digits')
        self.payment_password = new_password
        self.save()
        return True

class User_Wallet_Address(BaseModel):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    address = models.CharField(max_length=255, unique=False,null=True)
    label = models.CharField(max_length=100, blank=True,null=True)
    def __str__(self):
        return f"{self.user.username}'s wallet address :- {self.address}"