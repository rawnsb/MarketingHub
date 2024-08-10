import decimal
from django.urls import reverse
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.conf import settings
from accounts.models import User,User_Wallet_Address
from django.contrib.auth.decorators import login_required
@login_required
def home(request):

    return render(request,'home/index.html')
@login_required
def mine(request):
    return render(request,"profile/mine.html")
# Create your views here.


from .models import KYC,Withdraw,GapAmount

@login_required
def wallet_management(request):
    if request.method == 'POST':
        # Check if a KYC object already exists for the user
        kyc_instance, created = KYC.objects.get_or_create(user=request.user)

        # Update the existing KYC instance with the posted data and files
        kyc_instance.id_card_front = request.FILES['idCardFront']
        kyc_instance.id_card_back = request.FILES['idCardBack']
        kyc_instance.face_video = request.FILES['faceVideo']
        kyc_instance.wallet_type = request.POST['walletType']
        kyc_instance.wallet_address = request.POST['walletAddress']
        kyc_instance.save()

        # Optionally, redirect to a new URL after saving
        messages.success(request, "Your KYC documents have been uploaded successfully. Wait for verification.")
        return redirect('verification')

    return render(request, "home/wallet-management.html")

@login_required
def wallet_verification(request):
    return render(request,"home/verify.html")

from adminControl.models import WalletAddress
from .models import Deposit
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import logging
logger = logging.getLogger(__name__)
@login_required
@csrf_exempt
@require_http_methods(["POST", "GET"])
def deposite(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        deposit_method = data.get('method')
        deposit_amount = data.get('amount')

        existing_deposit = Deposit.objects.filter(
            user=request.user,
            deposit_method=deposit_method,
            is_amount_received=False,

        ).order_by('-created_at').first()
        print("here 2")
        if existing_deposit:
            existing_deposit.deposited_amount = deposit_amount
            existing_deposit.save()
            desp_obj = existing_deposit
        else:
            desp_obj = Deposit.objects.create(
                user=request.user,
                deposited_amount=deposit_amount,
                deposit_method=deposit_method
            )

        # Retrieve a random wallet address
        wallet_address = User_Wallet_Address.objects.get(user=request.user)
        walletAddress=wallet_address.address
        wallet_address.label=deposit_method
        wallet_address.save()



        if wallet_address is not None:
          desp_obj.wallet_address=walletAddress
          desp_obj.save()
        else:
            desp_obj.delete()
        # Prepare response data
        response_data = {'walletAddress': walletAddress}
        return JsonResponse(response_data)
    return render(request, "home/deposit.html")

@login_required
def deposite_records(request):
    obj=Deposit.objects.filter(user=request.user).order_by('-created_at')
    return render(request,"home/deposite_record.html",{"Deposite_records":obj})
# from django.db import transaction
#
# @login_required
# @csrf_exempt
# def withdraw(request):
#     if request.method == 'POST':
#         existing_withdrawal = Withdraw.objects.filter(user=request.user, processed=False).exists()
#         if existing_withdrawal:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': 'You already have a pending withdrawal. Please wait until it is processed.'
#             }, status=400)
#         amount = request.POST.get('withdrawalAmount')
#         password = request.POST.get('withdrawalPassword')
#     #     if request.user.check_password(password):
#     #         obj=Withdraw.objects.create(user=request.user, amount=amount, password=password)
#     #         return JsonResponse({'status': 'processing','withdrawal_id':obj.uid, 'message': 'Withdrawal is processing.'}, status=200)
#     #     else:
#     #         return JsonResponse({'status': 'error', 'message': 'Incorrect password.'}, status=400)
#     # return render(request, 'home/withdraw.html')
#         if not request.user.check_password(password):
#             return JsonResponse({'status': 'error', 'message': 'Incorrect password.'}, status=400)
#
#             # Transaction to ensure atomicity
#         with transaction.atomic():
#             try:
#                 balance = AccountBalance.objects.select_for_update().get(user=request.user)
#                 if balance.account_balance >= amount:
#                     balance.update_balance_on_withdrawal(amount)
#                     withdraw_obj = Withdraw.objects.create(user=request.user, amount=amount, password=password)
#                     return JsonResponse({'status': 'processing', 'withdrawal_id': withdraw_obj.uid,
#                                          'message': 'Withdrawal is processing.'}, status=200)
#                 else:
#                     return JsonResponse({'status': 'error', 'message': 'Insufficient funds for withdrawal.'},
#                                         status=400)
#             except AccountBalance.DoesNotExist:
#                 return JsonResponse({'status': 'error', 'message': 'Account balance not found.'}, status=400)
#
#     return render(request, 'home/withdraw.html')

from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Withdraw, AccountBalance
from accounts.models import PaymentPassword
from adminControl.models import SimpleOrder

@login_required
@csrf_exempt
def withdraw(request):
    if request.method == 'POST':
        kyc_verified = KYC.objects.filter(user=request.user)
        if not kyc_verified or not kyc_verified[0].is_verified:
            return JsonResponse({
                'status': 'error',
                'url': reverse('wallet'),
                'message': 'KYC not verified. Please complete your KYC verification to proceed.'
            }, status=403)
        # Check if there is an existing withdrawal that hasn't been processed
        existing_withdrawal = Withdraw.objects.filter(user=request.user, processed=False).exists()
        if existing_withdrawal:
            return JsonResponse({
                'status': 'error',
                'message': 'You already have a pending withdrawal. Please wait until it is processed.'
            }, status=400)

        amount = decimal.Decimal(request.POST.get('withdrawalAmount'))
        password = request.POST.get('withdrawalPassword')
        try:
            ob = PaymentPassword.objects.get(user=request.user, payment_password=password)
        except PaymentPassword.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Incorrect password.'}, status=400)

        # Start transaction to ensure atomicity
        with transaction.atomic():
            try:
                # Lock the account balance row for update
                balance = AccountBalance.objects.select_for_update().get(user=request.user)
                if balance.account_balance >= amount:
                    withdraw_obj = Withdraw.objects.create(user=request.user, amount=amount, password=password)
                    return JsonResponse({
                        'status': 'processing',
                        'withdrawal_id': withdraw_obj.uid,
                        'message': 'Withdrawal is processing.'
                    }, status=200)
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Insufficient funds for withdrawal.'
                    }, status=400)
            except AccountBalance.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Account balance not found.'
                }, status=400)

    # Render the withdrawal page if GET request
    return render(request, 'home/withdraw.html')


@login_required
def check_withdrawal_status(request, withdrawal_id):
        withdrawal = Withdraw.objects.get(uid=withdrawal_id, user=request.user)
        return JsonResponse({'processed': withdrawal.processed,'url': reverse('withdraw_records'),})

@login_required
def withdrawal_records(request):
    records = Withdraw.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'home/withdraw_records.html', {'records': records})



@login_required
def settings_page(request):
    return render(request,"home/settings.html",{
        'languages': settings.LANGUAGES,
        'language_code': request.session.get(settings.LANGUAGE_SESSION_KEY, settings.LANGUAGE_CODE)
    })

@login_required
def menu(request):
    return render(request,"grabOrder/menu.html")

@login_required
def order_management(request):
    bal=request.user.balance.account_balance
    color = '#007bff'
    
    if bal>20 and bal<350:
       color = request.GET.get('color','#007bff')
    if bal >=350 and bal <600:
        
        color=request.GET.get('color',"#ffc107")
    if bal>=600:
        color=request.GET.get('color',"#dc3545")
    print(color)
    return render(request,"grabOrder/order_management.html",{'color': color})


import json
from adminControl.models import SubmittedOrder
import json

@login_required
def grab_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            order_ids = data.get('order_ids').split(',')
            total_order_amount = decimal.Decimal(data.get('total_amount'))
            print(order_ids)

            if request.user.balance.account_balance < total_order_amount:
                gap = total_order_amount - request.user.balance.account_balance
                gap_obj=GapAmount.objects.get(user=request.user)
                gap_obj.gap_amount=gap
                gap_obj.save()
                return JsonResponse(
                    {"success": False, "message": f"Insufficient balance. Please deposit {gap} to claim this order."})

            for order_id in order_ids:
                order = get_object_or_404(SubmittedOrder, id=order_id, submitted_by=request.user)
                order.is_submitted = True
                order.save()

                cm = (decimal.Decimal(order.product_commission) / 100)
                price = order.product_price
                cmr = cm * price

                request.user.balance.account_balance += cmr
                request.user.balance.update_daily_commission(cmr)
            request.user.ordercount.no_of_submitted_order += 1
            request.user.ordercount.save()


            return JsonResponse({"success": True, "message": "Order(s) submitted successfully."})
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON data."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

        # GET request handling
    next_order = SubmittedOrder.objects.filter(is_submitted=False, check_box=True, submitted_by=request.user).order_by(
        'index').first()

    combined_lucky_orders = []
    simple_order = None

    if next_order:
        if next_order.label == 'lucky':
            combined_lucky_orders = list(
                SubmittedOrder.objects.filter(label='lucky', is_submitted=False, check_box=True,
                                              submitted_by=request.user).order_by('index')[:3]
            )
        elif next_order.label == 'simple':
            simple_order = next_order

    if combined_lucky_orders:
        total_amount = sum(order.product_price for order in combined_lucky_orders)
        commission_rate = sum(decimal.Decimal(order.product_commission) for order in combined_lucky_orders) / len(combined_lucky_orders) / 100
        
        commission = total_amount * commission_rate
        commission = round(commission, 2)
        expected_total = total_amount + commission
        expected_total = round(expected_total, 2)
    else:
        total_amount = simple_order.product_price if simple_order else 0
        commission_rate = decimal.Decimal(simple_order.product_commission) / 100 if simple_order else 0
        commission = total_amount * commission_rate
        expected_total = total_amount + commission
    
    no_orders = not combined_lucky_orders and simple_order is None

    return render(request, "grabOrder/simple_order.html", {
        "combined_lucky_orders": combined_lucky_orders,
        "simple_order": simple_order,
        "no_orders": no_orders,
        "total_amount": total_amount,
        "commission": commission,
        "expected_total": expected_total,
    })





@login_required
def service(request):
    return render(request,"home/service.html")

def custom_404_view(request, exception):
    return render(request, 'home/404.html', status=404)