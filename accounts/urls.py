from django.urls import path
from django.views.generic import RedirectView

from .views import loginn,Admin_login,Admin_dasboard,Employee_dashboard,Employee_login,select_language,upload_photo,register,change_account_password,logout_user,change_payment_password

urlpatterns = [
   path('',loginn,name='login'),
   path('Employee-login/',Employee_login,name='Employee_login'),
   path('employee-login/', RedirectView.as_view(url='/Employee-login/', permanent=False)),
   path('employee-login', RedirectView.as_view(url='/Employee-login/', permanent=False)),
   path('Admin-login/',Admin_login,name='Admin_login'),
   path('admin-login/', RedirectView.as_view(url='/Admin-login/', permanent=False)),
   path('admin-login', RedirectView.as_view(url='/Admin-login/', permanent=False)),
   path('Admin-Dashboard/',Admin_dasboard,name='Admin_dashboard'),
   path('Employee-Dashboard/',Employee_dashboard,name='Employee_dashboard'),
   path('signup/',register,name='register'),
   path('logout/',logout_user,name='logout'),
   path('upload_photo/',upload_photo,name='upload_photo'),
   path('select-language/', select_language, name='select_language'),
   path('change_account_password/',change_account_password,name='change_account_password'),
   path('change-payment-password/', change_payment_password, name='change_payment_password'),

]
