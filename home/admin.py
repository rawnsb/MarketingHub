from django.contrib import admin
from .models import KYC,AccountBalance,Deposit,Withdraw,OrderCount,GapAmount
admin.site.register(KYC)
admin.site.register(AccountBalance)
admin.site.register(Deposit)
admin.site.register(Withdraw)
admin.site.register(OrderCount)
admin.site.register(GapAmount)

# Register your models here.
