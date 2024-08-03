
from django.conf import settings

from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from .models import User,PaymentPassword,Invite_Code,UserIp,Telegram,User_Wallet_Address,Profile
from home.models import AccountBalance,OrderCount,GapAmount
from Employee.models import EmployeeDeposit
from adminControl.models import AdminTelegram,WalletAddress
from django.contrib.auth.decorators import login_required
def loginn(request):
    if request.user.is_authenticated and request.user.is_customer:
        return redirect('/home/index/')
    elif request.user.is_authenticated and request.user.is_employee:
        return redirect('Employee_dashboard')
    elif request.user.is_authenticated and request.user.is_admin:
        return redirect('Admin_dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        role = int(request.POST.get('role', 1))


        remember_me = request.POST.get('rememberMe', False)
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_customer and role==1:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)  # Session expires when the browser is closed
            messages.success(request, f'Welcome back, {username}!')
            return redirect('/home/index/')  # Redirect to home page or dashboard
        else:
            messages.error(request, 'Invalid username or password')
    return render(request,"accounts/login.html")

def Employee_login(request):
    if request.user.is_authenticated and request.user.is_customer:
        return redirect('/home/index/')
    elif request.user.is_authenticated and request.user.is_employee:
        return redirect('Employee_dashboard')
    elif request.user.is_authenticated and request.user.is_admin:
        return redirect('Admin_dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = int(request.POST.get('role', 2))

        remember_me = request.POST.get('rememberMe', False)
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_employee and role==2:
            login(request,user)
            if not remember_me:
                request.session.set_expiry(0)  # Session expires when the browser is closed
            messages.success(request, f'Welcome back, {username}!')
            return redirect('Employee_dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, "accounts/Employee_login.html")
@login_required
def Employee_dashboard(request):
    if not request.user.is_employee:
        return render(request, "errors/not_authorized.html")  # Assume you have a not authorized page
    referred_users = User.objects.filter(invitation_code=request.user.invitation_code, is_customer=True)
    context = {
        'referred_users': referred_users
    }
    print(context)

    return render(request, "home/Employee_dashboard.html", context)

def Admin_login(request):
    if request.user.is_authenticated and request.user.is_customer:
        return redirect('/home/index/')
    elif request.user.is_authenticated and request.user.is_employee:
        return redirect('Employee_dashboard')
    elif request.user.is_authenticated and request.user.is_admin:
        return redirect('Admin_dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = int(request.POST.get('role', 3))

        remember_me = request.POST.get('rememberMe', False)
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_admin and role == 3:
           login(request, user)
           if not remember_me:
               request.session.set_expiry(0)

           messages.success(request, f'Welcome back, {username}!')
           return redirect('Admin_dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, "accounts/Admin_login.html")

from django.views.decorators.http import require_http_methods


@login_required
@require_http_methods(["GET", "POST"])
def Admin_dasboard(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')


        # Validate if the username and password are provided
        if not username or not password:
            messages.error(request, "Username and password are required.")
            return redirect('Admin_dashboard')
        print("here",username,password)

        # Create a new employee
        try:
            print("hello created s")
            emp=User.objects.create_user(username=username, password=password,is_employee=True)
            EmployeeDeposit.objects.create(employee=emp)
            print("hello created")
            messages.success(request, f'Employee {username} added successfully.')
            return redirect('Admin_dashboard')
        except Exception as e:
            messages.error(request, f'Error adding employee: {str(e)}')
            return redirect('Admin_dashboard')
    Emp=User.objects.filter(is_employee=True)
    total_emplyee=Emp.count()
    Cus = User.objects.filter(is_customer=True)
    total_customer = Cus.count()
    employees = User.objects.filter(is_employee=True)
    employees_data = []
    for employee in employees:
        invited_customers = User.objects.filter(invitation_code=employee.invitation_code, is_customer=True)
        plain_password = request.session.pop(f'employee_password_{employee.id}', '******')
        employees_data.append({
            'employee': employee,
            'plain_password': plain_password,
            'invited_customers': invited_customers,

        })

    context={"Total_Employees":total_emplyee,"Total_Customer":total_customer,
             'employees_data': employees_data}
    return render(request, 'home/Admin_dashboard.html',context)


# def register(request):
#     if request.method == 'POST':
#         first_name = request.POST['firstName']
#         last_name = request.POST['lastName']
#         username = request.POST['username']
#         email = request.POST['email']
#         invite_code = request.POST['inviteCode']
#         password = request.POST['password']
#         confirm_password = request.POST['confirmPassword']
#         payment_password = request.POST['payment_password']
#
#         if password == confirm_password:
#             if User.objects.filter(username=username).exists():
#                 messages.error(request, 'Username already exists')
#             elif User.objects.filter(email=email).exists():
#                 messages.error(request, 'Email already exists')
#             else:
#
#                 user = User.objects.create_user(
#                     username=username,
#                     password=password,
#                     email=email,
#                     first_name=first_name,
#                     last_name=last_name
#                 )
#
#                 user.save()
#                 if payment_password.isdigit() and 1 <= len(payment_password) <= 6:
#                     PaymentPassword.objects.create(
#                         user=user,
#                         payment_password=payment_password
#                     )
#                 else:
#                     messages.error(request,
#                                    "Invalid payment password. It must be numeric and between 1 to 6 digits long.")
#                     return render(request, "accounts/signup.html")
#
#
#                 invite_code_entry = InviteCode(user=user, invite_code=invite_code)
#                 balance_created= AccountBalance.objects.create(user=user)
#                 balance_created.save()
#                 invite_code_entry.save()
#                 messages.success(request, 'Your account has been created successfully')
#                 # new_user = authenticate(username=username, password=password)
#                 # login(request, new_user)
#                 return redirect('/')
#         else:
#             messages.error(request, 'Passwords do not match')
#     return render(request,"accounts/signup.html")
from django.db import transaction
def register(request):
    # if User.is_authenticated:
    #     messages.info(request, 'You have already logged in. Please logout first to register a new account.')
    #     return redirect("/home/settings/")
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        invite_code = request.POST.get('inviteCode')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')
        payment_password = request.POST.get('payment_password')


        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            user_ip = x_forwarded_for.split(',')[0]
        else:
            user_ip = request.META.get('REMOTE_ADDR', '')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
        elif len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long')
            return redirect('register')

        if not payment_password.isdigit() or not 4 <= len(payment_password) <= 6:
            messages.error(request, "Invalid payment password. It must be numeric and between 4 to 6 digits long.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('register')

        if not invite_code:
            messages.error(request, "No invitation code provided.")
            return redirect('register')

        try:
            employee = User.objects.get(invitation_code=invite_code,is_employee=True)  # Checking Employee invite code validity
        except User.DoesNotExist:
            messages.error(request, "Invalid invitation code.")
            return redirect('register')

        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_customer = True,
                invitation_code=invite_code
            )
            ip=UserIp.objects.create(user=user,ip_address=user_ip)
            Invite_Code.objects.create(user=user,invite_code=invite_code)

            PaymentPassword.objects.create(
                user=user,
                payment_password=payment_password
            )
            tele=Telegram.objects.create(user=user)
            tele.telegram_link=AdminTelegram.get_random_telegram_link()
            tele.save()
            OrderCount.objects.create(user=user)
            wd=WalletAddress.get_random_wallet_address()
            wallet=User_Wallet_Address.objects.create(user=user)
            wallet.address=wd
            wallet.label='USDT'
            wallet.save()

            obj=AccountBalance.objects.create(user=user)
            obj.save()
            obj1=GapAmount.objects.create(user=user)
            obj1.save()

            messages.success(request, 'Your account has been created successfully')
            return redirect('/')

    return render(request, "accounts/signup.html")
@login_required
def logout_user(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("login")
@login_required
def change_payment_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        try:
            payment_password_instance = PaymentPassword.objects.get(user=request.user)
            payment_password_instance.change_password(new_password)
            messages.success(request, 'Your payment password has been updated successfully.')
            return redirect('/home/mine/')  # Redirect to profile or another appropriate page
        except PaymentPassword.DoesNotExist:
            messages.error(request, 'Payment password setup not found.')
        except ValidationError as ve:
            messages.error(request, str(ve))


    return render(request,"home/change_payment_password.html")

from django.contrib.auth import update_session_auth_hash
@login_required
def change_account_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(current_password):
            messages.error(request, 'Your current password was entered incorrectly. Please try again.')
            return redirect('/change_account_password/')

        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('/change_account_password/')

        if len(new_password) < 8:
            messages.error(request, 'Your new password must contain at least 8 characters.')
            return redirect('/change_account_password/')

        # Updating the password
        user = request.user
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)  # Important to keep the user logged in after changing the password
        messages.success(request, 'Your password has been updated successfully.')
        return redirect('/home/mine/')  # Redirect to a profile or a similar page

    return render(request, 'accounts/change_account_password.html')

@login_required
def upload_photo(request):
    if request.method == 'POST':
        # Get the uploaded file
        uploaded_file = request.FILES['profile_photo']

        # Optional: Check file size or file type if needed
        if uploaded_file.size > 1024 * 1024:
            messages.error(request, 'File size exceeds the limit of 1 MB.')
            return redirect('settings')
        if not uploaded_file.content_type.startswith('image/'):
            messages.error(request, 'Invalid file type. Please upload an image.')
            return redirect('settings')
        obj=Profile.objects.create(user=request.user,profile_image=uploaded_file)
        obj.save()
        # Display success message
        messages.success(request, 'Your profile photo has been updated.')
        return redirect('settings')  # Redirect to settings or profile page
    else:
        # GET method is not allowed for this view
        messages.error(request, 'Invalid request.')
        return redirect('settings')

from django.utils.translation import activate
from django.conf import settings
def select_language(request):
    if request.method == 'POST':
        language_code = request.POST.get('language_code')
        print(language_code)
        if language_code and language_code in dict(settings.LANGUAGES):
            activate(language_code)
            request.session[settings.LANGUAGE_SESSION_KEY] = language_code
            print(settings.LANGUAGE_SESSION_KEY)

            request.session.save()
            messages.success(request, 'Language updated successfully.')
        else:
            messages.error(request, 'Invalid language selection.')
        return redirect('settings')
    else:
        return HttpResponse("Method not allowed", status=405)
