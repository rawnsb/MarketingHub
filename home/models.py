
from django.db import models
from Base.models import BaseModel
from django.conf import settings
from decimal import Decimal

class KYC(BaseModel):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="kyc")
    id_card_front = models.FileField(upload_to='kyc_documents/')
    id_card_back = models.FileField(upload_to='kyc_documents/')
    face_video = models.FileField(upload_to='kyc_videos/')
    wallet_type = models.CharField(max_length=100)
    wallet_address = models.CharField(max_length=255)
    is_verified=models.BooleanField(default=False)

    def __str__(self):
        return f"KYC for {self.wallet_address}"

# Create your models here.
from django.utils import timezone

class AccountBalance(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="balance")
    account_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    today_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_withdrawal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_transaction_date = models.DateField(default=timezone.now)

    @property
    def net_deposit(self):
        return self.total_deposit - self.total_withdrawal

    def __str__(self):
        return f"{self.user.username}'s Balance info"

    def update_daily_commission(self, amount):
        """ Update daily commission and check if it's a new day to reset. """
        if self.last_transaction_date < timezone.now().date():
            self.today_commission = 0
            self.last_transaction_date = timezone.now().date()
        self.today_commission += amount
        self.total_commission += amount
        self.save()

    def update_balance_on_deposit(self, amount):
        """ Update account balance and total deposits on deposit. """
        # Convert the amount to Decimal before adding to ensure type compatibility
        decimal_amount = Decimal(amount)
        self.account_balance += decimal_amount
        self.total_deposit += decimal_amount
        print(self.total_deposit, self.account_balance)
        self.save()

    def update_balance_on_withdrawal(self, amount):
        """ Update account balance and total withdrawals on withdrawal. """
        amount = Decimal(amount)
        if self.account_balance >=amount:
            amount=Decimal(amount)
            self.account_balance -= amount
            self.total_withdrawal += amount
            self.save()
        else:
            raise ValueError("Insufficient funds for withdrawal")



class Deposit(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='deposits',
        verbose_name="User"
    )
    deposited_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Deposited Amount"
    )
    deposit_method = models.CharField(
        max_length=70,
        verbose_name="Deposit Method"
    )
    wallet_address = models.CharField(max_length=100, verbose_name='Wallet Address')
    is_amount_received = models.BooleanField(
        default=False,
        verbose_name="Is Amount Received"
    )


    def __str__(self):
        return f"{self.user.username} deposited {self.deposited_amount}"


from django.db import models

from django.utils.translation import gettext_lazy as _

class Withdraw(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("User")
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Withdrawal Amount")
    )
    password = models.CharField(
        max_length=128,
        verbose_name=_("Password")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At")
    )
    processed = models.BooleanField(
        default=False,
        verbose_name=_("Processed (Verification)")
    )

    def __str__(self):
        """
        Returns a string representation of the withdrawal request,
        showing the user and the requested amount.
        """
        return f"{self.user.username} requested a withdrawal of ${self.amount}"

class OrderCount(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ordercount")
    no_of_submitted_order = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    def __str__(self):
        return f"{self.user.username} has submitted {self.no_of_submitted_order} orders"

class GapAmount(BaseModel):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="gapamount")
    gap_amount=models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return F"Amount ${self.gap_amount} needs to be submitted by {self.user.username}"