from django.contrib import admin
from django.urls import path
from .views import update_deposit,order_grant,update_order,delete_order,update_wallet,update_telegram,approve_withdraw,verify_kyc,list_and_create_orders
urlpatterns = [
    path('update_deposit/<int:id>/', update_deposit, name='update_deposit'),
    path('approve-withdraw/<int:id>/', approve_withdraw, name='approve_withdraw'),
    path('kyc-verification/<int:id>/', verify_kyc, name='verify_kyc'),
    path('update-telegram/<int:id>/', update_telegram, name='update_telegram'),
    path('update-wallet/<int:id>/', update_wallet, name='update_wallet'),
    path('simple-orders/', list_and_create_orders, name='list_and_create_orders'),
    path('order/update/<int:order_id>/', update_order, name='update_order'),
    path('order/delete/<int:order_id>/', delete_order, name='delete_order'),
    path('order-grant/<int:id>/', order_grant, name='order_grant'),
]
