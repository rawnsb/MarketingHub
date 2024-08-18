from django.contrib import admin
from django.urls import path
from .views import update_deposit,fetch_custom_orders,change_action,delete_customer,reset_order_numbers,update_customer_order,delete_unused_products,grant_batches_to_customer,remove_granted_batch,grant_batch_to_customer,delete_batch_order,fetch_orders,finalize_batch,add_orders,orders_panel,update_wallet,update_telegram,approve_withdraw,verify_kyc
urlpatterns = [
    path('update_deposit/<int:id>/', update_deposit, name='update_deposit'),
    path('approve-withdraw/<int:id>/', approve_withdraw, name='approve_withdraw'),
    path('kyc-verification/<int:id>/', verify_kyc, name='verify_kyc'),
    path('update-telegram/<int:id>/', update_telegram, name='update_telegram'),
    path('change-action/<int:id>/', change_action, name='change_action'),
    path('delete-customer/<int:id>/', delete_customer, name='delete_customer'),
    path('reset-order-numbers/<int:id>/', reset_order_numbers, name='reset_order_numbers'),
    path('update-wallet/<int:id>/', update_wallet, name='update_wallet'),
    path('orders_panel/', orders_panel, name='orders_panel'),
    path('add-orders/<int:batch_id>/', add_orders, name='add_orders'),
    path('finalize-batch/<int:batch_id>/', finalize_batch, name='finalize_batch'),
    path('batch/<int:batch_id>/', fetch_orders, name='fetch_orders'),
    path('delete-batch-order/<int:order_id>/', delete_batch_order, name='delete_batch_order'),
     # granting new
     path('grant-batches/<int:customer_id>/', grant_batches_to_customer, name='grant_batches_to_customer'),
     path('grant-batch/<int:batch_id>/to-customer/<int:customer_id>/', grant_batch_to_customer, name='grant_batch_to_customer'),
     path('remove-batch/<int:batch_id>/from-customer/<int:customer_id>/', remove_granted_batch, name='remove_granted_batch'),
     path('fetch_custom_orders/<int:batch_id>/from-customer/<int:customer_id>/', fetch_custom_orders, name='fetch_custom_orders'),
     path('update_customer_order/<int:order_id>/<int:customer_id>/', update_customer_order, name='update_customer_order'),

    #  dlete product unused
    path('delete-unused-products/', delete_unused_products, name='delete_unused_products'),
     
]
