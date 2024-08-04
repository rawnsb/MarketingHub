from django.contrib import admin
from django.conf.urls import handler404
from django.urls import path
from .views import home,service,grab_order,custom_404_view,order_management,menu,mine,withdrawal_records,settings_page,wallet_management,check_withdrawal_status,withdraw,wallet_verification,deposite,deposite_records
urlpatterns = [
   path('index/',home,name='home'),
   path('mine/',mine,name='mine'),
   path('wallet_management/',wallet_management,name='wallet'),
   path('wallet-verification/',wallet_verification,name='verification'),
   path('deposite/',deposite,name='deposite'),
   path('deposit-records/',deposite_records,name='deposite_records'),
   path('withdraw/', withdraw, name='withdraw'),
   path('withdraw/check-status/<str:withdrawal_id>/', check_withdrawal_status, name='check_withdrawal_status'),
   path('withdraw-records/',withdrawal_records,name='withdraw_records'),
   path('settings/',settings_page,name='settings'),
   path('order-menu/',menu,name='menu'),
   path('order-management/',order_management,name='order_management'),
   path('services/',service,name='service'),
   path('grab-order/',grab_order,name='grab_order'),
]

handler404 = custom_404_view
