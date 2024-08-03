from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Deposit, AccountBalance,Withdraw,GapAmount

from django.utils import timezone

@receiver(post_save, sender=Deposit)
def update_account_balance(sender, instance, created, **kwargs):
    if instance.is_amount_received==True and not created:
        # Get or create the AccountBalance associated with the user
        account_balance, _ = AccountBalance.objects.get_or_create(user=instance.user)
        account_balance.update_balance_on_deposit(instance.deposited_amount)
        gap=GapAmount.objects.get(user=instance.user)
        if instance.deposited_amount >gap.gap_amount:
            gap.gap_amount=0
        elif instance.deposited_amount >gap.gap_amount:
            gap.gap_amount-=instance.deposited_amount
        gap.save()


@receiver(post_save, sender=Withdraw)
def update_account_balance(sender, instance, created, **kwargs):
    if instance.processed==True and not created:
        print("Yes Done")
        account_balance, _ = AccountBalance.objects.get_or_create(user=instance.user)
        account_balance.update_balance_on_withdrawal(instance.amount)

        # Optionally, update commissions if applicable
        # if instance.deposit_method == 'SomeSpecificMethodThatAffectsCommissions':
        #     commission_amount = calculate_commission(instance.deposited_amount)  # Define this function as needed
        #     account_balance.update_daily_commission(commission_amount)
