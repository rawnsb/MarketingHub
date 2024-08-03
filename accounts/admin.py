# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import User, InviteCode, PaymentPassword, Profile, UserIP  # Import the User model
#
# # Custom UserAdmin to manage custom user fields in the admin
# class CustomUserAdmin(UserAdmin):
#     model = User  # Use the model class directly
#     list_display = ['username','email','referred_by', 'role', 'is_staff']  # Customize what to display
#
#
# admin.site.register(User, CustomUserAdmin)
#
# # Register other models
# admin.site.register(InviteCode)
# admin.site.register(PaymentPassword)
# admin.site.register(Profile)
# admin.site.register(UserIP)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User,PaymentPassword,Profile,Invite_Code,UserIp,Telegram,User_Wallet_Address
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_admin', 'is_employee', 'is_customer', 'invitation_code')
    list_filter = ('is_admin', 'is_employee', 'is_customer')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                   'is_admin', 'is_employee', 'is_customer',
                                   'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Additional Info', {'fields': ('invitation_code',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'is_admin', 'is_employee', 'is_customer')
        }),
        ('Permissions', {
            'classes': ('wide',),
            'fields': ('groups', 'user_permissions')
        }),
        ('Generate Code', {
            'classes': ('wide',),
            'fields': ('invitation_code',)
        })
    )
    search_fields = ('username', 'email', 'invitation_code')
    ordering = ('username',)
    readonly_fields = ('invitation_code',)


admin.site.register(User, UserAdmin)

admin.site.register(PaymentPassword)
admin.site.register(Profile)
admin.site.register(Invite_Code)
admin.site.register(UserIp)
admin.site.register(Telegram)
admin.site.register(User_Wallet_Address)
