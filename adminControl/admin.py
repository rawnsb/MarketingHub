from django.contrib import admin
from .models import WalletAddress,AdminDeposit,ExtraPictures,AdminTelegram,Batch, Product,CustomerOrder,CustomerBatch, Order

admin.site.register(Batch)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(WalletAddress)
admin.site.register(AdminDeposit)
admin.site.register(AdminTelegram)
admin.site.register(CustomerOrder)
admin.site.register(CustomerBatch)
admin.site.register(ExtraPictures)

# Register your models here.
