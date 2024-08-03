from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from accounts.models import User,Telegram,User_Wallet_Address
from home.models import Deposit,Withdraw,KYC
from . models import SimpleOrder,SubmittedOrder
from decimal import Decimal
import uuid
@login_required
def update_deposit(request,id):
    user = get_object_or_404(User, id=id, is_customer=True)

    try:
        # Fetch the deposit record associated with this user
        deposit = Deposit.objects.get(user=user, is_amount_received=False)
    except Deposit.DoesNotExist:
        messages.error(request, f"No pending deposit found for { user.username }.")
        return redirect('Admin_dashboard')

    if request.method == 'POST':
        deposited_amount = request.POST.get('deposited_amount')
        deposit_method = deposit.deposit_method  # This field is disabled, so use the existing value
        wallet_address = deposit.wallet_address  # This field is disabled, so use the existing value
        is_amount_received = True  # As the checkbox is removed, we assume the amount is received
        d=Decimal(deposited_amount)
        deposit.deposited_amount = d
        deposit.deposit_method = deposit_method
        deposit.wallet_address = wallet_address
        deposit.is_amount_received = is_amount_received
        deposit.save()

        messages.success(request, f"{ user.username }'s Deposit approved successfully!")
        return redirect('Admin_dashboard')

    context = {
        'deposit': deposit
    }
    return render(request, 'admin/update_deposit.html', context)
# Create your views here.
@login_required
def approve_withdraw(request, id):
    user = get_object_or_404(User, id=id, is_customer=True)

    try:
        # Fetch the withdrawal record associated with this user
        withdrawal = Withdraw.objects.get(user=user, processed=False)
        kyc = get_object_or_404(KYC, user=user, is_verified=True)
    except Withdraw.DoesNotExist:
        messages.error(request, f"No pending withdrawal found for { user.username }.")
        return redirect('Admin_dashboard')

    if request.method == 'POST':
        approved_amount = request.POST.get('approved_amount')
        is_approved = True  # Assuming approval is being done through this form
        withdrawal.amount = approved_amount
        withdrawal.processed = is_approved
        withdrawal.save()
        messages.success(request, f"{ user.username }'sWithdrawal approved successfully!")
        return redirect('Admin_dashboard')

    context = {
        'withdrawal': withdrawal,
        'kyc':kyc
    }
    return render(request, 'admin/approve_withdraw.html', context)

@login_required
def verify_kyc(request, id):
    user = get_object_or_404(User, id=id, is_customer=True)

    try:
        kyc_record = KYC.objects.get(user=user)
    except KYC.DoesNotExist:
        messages.error(request, f"No KYC record found for { user.username }.")
        return redirect('Admin_dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'verify':
            kyc_record.is_verified = True
            kyc_record.save()
            messages.success(request, f"{ user.username }'s KYC verified successfully!")
            return redirect('Admin_dashboard')

        elif action == 'delete':
            kyc_record.delete()
            messages.success(request, f"{ user.username }'s KYC record deleted successfully!")
            return redirect('Admin_dashboard')

    context = {
        'kyc_record': kyc_record
    }
    return render(request, 'admin/kyc_approval.html', context)




@login_required
def update_telegram(request, id):
    user = get_object_or_404(User, id=id)
    telegram_account, created = Telegram.objects.get_or_create(user=user)

    if request.method == 'POST':
        new_link = request.POST.get('newLink')
        if new_link:
            telegram_account.telegram_link = new_link
            telegram_account.save()
            messages.success(request, f"{ user.username }'s Telegram Account is replaced sucessfully!")
            return redirect('Admin_dashboard')  # Replace 'dashboard' with your dashboard URL name

    return render(request, 'admin/update_telegram.html', {'telegram_account': telegram_account, 'user': user})

def update_wallet(request,id):
    user = get_object_or_404(User, id=id)
    wallet_address, created = User_Wallet_Address.objects.get_or_create(user=user)
    kyc = get_object_or_404(KYC, user=user)
    if request.method == 'POST':
        new_address = request.POST.get('newAddress')
        if new_address:
            wallet_address.address = new_address
            wallet_address.save()
            messages.success(request,f'wallet address for { user.username } is updated')
            return redirect('Admin_dashboard')  # Replace 'dashboard' with your dashboard URL name

    return render(request, 'admin/update_wallet_address.html', {
        'wallet_address': wallet_address,
        'user': user,
        'withdrawal_address': kyc.wallet_address
    })
from django.contrib.contenttypes.models import ContentType
@login_required
def list_and_create_orders(request):
    if request.method == 'POST':
        product_name = request.POST['product_name']
        product_price = request.POST['product_price']
        product_commission = request.POST['product_commission']
        product_img = request.FILES.get('product_img')
        label = request.POST.get('label')
        order = SimpleOrder(user=request.user, product_name=product_name, product_price=product_price,
                            product_commission=product_commission,product_img=product_img,label=label)
        order.save()


        return redirect('list_and_create_orders')

    simple_order_content_type = ContentType.objects.get_for_model(SimpleOrder)
    orders = SimpleOrder.objects.filter(content_type=simple_order_content_type)
    return render(request, 'admin/create_simple_orders.html', {'orders': orders})

def update_order(request, order_id):
    order = get_object_or_404(SimpleOrder, id=order_id)
    if request.method == 'POST':
        order.product_name = request.POST.get('product_name')
        order.product_price = request.POST.get('product_price')
        order.product_commission = request.POST.get('product_commission')
        if 'product_img' in request.FILES:
            order.product_img = request.FILES['product_img']
        order.save()
        return redirect('list_and_create_orders')
    return render(request, 'admin/create_simple_orders.html', {'order': order})

def delete_order(request, order_id):
    order = get_object_or_404(SimpleOrder, id=order_id)
    order.delete()
    return redirect('list_and_create_orders')

def order_grant(request,id):
    user = get_object_or_404(User, id=id)
    orders = SimpleOrder.objects.all()
    created_orders = SubmittedOrder.objects.filter(submitted_by=user)

    if created_orders.count() != orders.count():
        for order in orders:
            try:
                submitted_order, created = SubmittedOrder.objects.get_or_create(
                    user=order.user,
                    product_name=order.product_name,
                    product_price=order.product_price,
                    product_commission=order.product_commission,
                    product_img=order.product_img,
                    submitted_by=user,
                    order_id=order.order_id,
                    label=order.label
                )
            except SubmittedOrder.MultipleObjectsReturned:
                pass  # Handle the case where multiple objects might be returned (if needed)

        created_orders = SubmittedOrder.objects.filter(submitted_by=user)
    if request.method == 'POST':
        order_ids = request.POST.getlist('order_ids')
        for created_order in created_orders:
            print("x")
            if str(created_order.id) in order_ids:
                created_order.check_box = True
            else:
                created_order.check_box = False
            index_value = request.POST.get(f'index_{created_order.id}', None)
            print(index_value)
            if index_value is not None:
                try:
                    created_order.index = int(index_value)
                except ValueError:
                    pass  # handle invalid index input gracefully

            created_order.save()
        messages.success(request,f"you have granted Some orders For {user.username}")
        return redirect("Admin_dashboard")
    print(created_orders)
    return render(request,"admin/order_granted.html",{"orders":created_orders})