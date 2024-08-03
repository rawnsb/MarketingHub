from django.contrib import admin
from .models import WalletAddress,AdminDeposit,AdminTelegram,SimpleOrder,SubmittedOrder
admin.site.register(WalletAddress)
admin.site.register(AdminDeposit)
admin.site.register(AdminTelegram)
admin.site.register(SimpleOrder)
admin.site.register(SubmittedOrder)

# Register your models here.
