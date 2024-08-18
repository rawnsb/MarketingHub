from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from accounts.models import User,Telegram,User_Wallet_Address
from home.models import Deposit,Withdraw,KYC
from . models import CustomerBatch, CustomerOrder
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
@login_required
def update_wallet(request, id):
    user = get_object_or_404(User, id=id)
    wallet_address, created = User_Wallet_Address.objects.get_or_create(user=user)

    # Try to get the KYC object, handle if it doesn't exist
    try:
        kyc = KYC.objects.get(user=user)
    except KYC.DoesNotExist:
        kyc = None  # Set KYC to None if it doesn't exist

    if request.method == 'POST':
        new_address = request.POST.get('newAddress')
        if new_address:
            wallet_address.address = new_address
            wallet_address.save()
            messages.success(request, f'Wallet address for {user.username} has been updated.')
            return redirect('Admin_dashboard')  # Replace with your dashboard URL name

    return render(request, 'admin/update_wallet_address.html', {
        'wallet_address': wallet_address,
        'user': user,
        'withdrawal_address': kyc.wallet_address if kyc else "KYC Not Verified"  # Handle case where KYC is None
    })
@login_required
def change_action(request, id):
    user = get_object_or_404(User, id=id)
    user.is_active = not user.is_active
    user.save()
    
    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f'The user {user.username} has been successfully {status}.')
    
    return redirect("Admin_dashboard")
@login_required
def reset_order_numbers(request, id):
    user = get_object_or_404(User, id=id)
    user.ordercount.no_of_submitted_order = 0
    user.ordercount.save()

    messages.success(request, f'Order count for {user.username} has been successfully reset to 0.')

    return redirect("Admin_dashboard")
def delete_customer(request,id):
    user = get_object_or_404(User, id=id)
    user.delete()
    messages.success(request, f'Customer {user.username} has been successfully deleted.')
    return redirect("Admin_dashboard")


# new
from .models import Batch,Order,Product
@login_required
def orders_panel(request):
    if request.method == 'POST':
        batch_name = request.POST.get('batch_name')
        if batch_name:
            Batch.objects.create(name=batch_name)
            return redirect('orders_panel')

    # Fetch all batches to display them
    batches = Batch.objects.all()

    return render(request, "admin/batch_creation_and_display_orders.html", {
        'batches': batches,
    })

from django.http import JsonResponse
@login_required
def fetch_orders(request, batch_id):
    # Get the batch based on the provided batch_id
    batch = get_object_or_404(Batch, id=batch_id)

    # Fetch orders related to the batch
    orders = Order.objects.filter(batch=batch).select_related('product').prefetch_related('products')

    orders_data = []
    for order in orders:
        # Handle the ForeignKey relationship (single product)
        products_data = []
        if order.product:
            products_data.append({
                'name': order.product.name,
                'image_url': order.product.image.url,
            })

        # Handle the Many-to-Many relationship (additional products in lucky orders)
        for product in order.products.all():
            products_data.append({
                'name': product.name,
                'image_url': product.image.url,
            })

        # Append order data including products
        orders_data.append({
            'id': order.id,
            'order_type': order.order_type,
            'total_amount': order.total_amount,
            'products': products_data,
        })

    return JsonResponse({'orders': orders_data})




@login_required
def add_orders(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    current_order_count = Order.objects.filter(batch=batch).count()
    
    if request.method == 'POST':
        if current_order_count >= 20:
          messages.error(request, 'This batch already has 20 orders. You cannot add more orders.')
          return redirect('add_orders', batch_id=batch.id)
        order_type = request.POST.get('order_type')

        if order_type == 'Simple':
            product_name = request.POST.get('product_name')
            product_price = request.POST.get('product_price')
            product_commission = request.POST.get('product_commission')
            product_image = request.FILES.get('product_image')

            if product_name and product_price and product_commission and product_image:
                product_price = float(product_price)
                product_commission_rate = float(product_commission)
                commission_amount = product_price * (product_commission_rate / 100)
                total_amount = product_price 

                product = Product.objects.create(
                    name=product_name,
                    price=product_price,
                    commission_rate=product_commission_rate,
                    image=product_image
                )

                order = Order.objects.create(
                    batch=batch,
                    order_type=order_type,
                    product=product,
                    total_amount=total_amount,
                )

                messages.success(request, 'Simple Order created successfully.')
                return redirect('add_orders', batch_id=batch.id)

        elif order_type == 'Lucky':
            lucky_product_count = int(request.POST.get('lucky_product_count'))
            lucky_order_position = request.POST.get('lucky_order_position')
            products = []

            for i in range(lucky_product_count):
                product_name = request.POST.get(f'lucky_product_name_{i}')
                product_price = request.POST.get(f'lucky_product_price_{i}')
                product_image = request.FILES.get(f'lucky_product_image_{i}')

                if product_name and product_price and product_image:
                    product_price = float(product_price)

                    product = Product.objects.create(
                        name=product_name,
                        price=product_price,
                        commission_rate=20,  # Assuming Lucky Orders don't have commissions for individual products
                        image=product_image
                    )
                    products.append(product)
            
            total_amount = sum(product.price for product in products)
            commission_amount = total_amount * 0.2  # Assuming a 20% commission on the total amount
            # total_amount += commission_amount

            order = Order.objects.create(
                batch=batch,
                order_type=order_type,
                total_amount=total_amount,
                lucky_order_position=lucky_order_position
            )
            order.products.add(*products)  # Adding multiple products to the lucky order

            messages.success(request, 'Lucky Order created successfully.')
            return redirect('add_orders', batch_id=batch.id)

    orders = Order.objects.filter(batch=batch).order_by('id')
    return render(request, 'admin/order_panel.html', {
        'batch': batch,
        'orders': orders,
        'remaining_orders': 20 - orders.count()
    })
@login_required
def finalize_batch(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    orders = Order.objects.filter(batch=batch)
    if orders.count() != 20:
        messages.error(request, 'You must add exactly 20 orders to finalize the batch.')
        return redirect('add_orders', batch_id=batch.id)
    
    # Add finalization logic here (if any)
    messages.success(request, f'Batch "{batch.name}" finalized successfully with {orders.count()} orders.')
    return redirect('orders_panel')
@login_required
def delete_batch_order(request,order_id):
    order = get_object_or_404(Order, id=order_id)
    batch_id = order.batch.id
    if order.order_type == 'Lucky':
        # If it's a Lucky order, delete all related products
        order.products.all().delete()
    else:
        # For Simple orders, delete the single associated product
        if order.product:
            order.product.delete()
    order.delete()
    messages.success(request, 'Order deleted successfully.')
    return redirect('add_orders', batch_id=batch_id)


# grant order new
@login_required
def grant_batches_to_customer(request, customer_id):
    customer = get_object_or_404(User, id=customer_id)
    batches = Batch.objects.all()
    return render(request, 'admin/grant_batches.html', {
        'customer': customer,
        'batches': batches
    })

# def grant_batch_to_customer(request, batch_id, customer_id):
#     batch = get_object_or_404(Batch, id=batch_id)
#     customer = get_object_or_404(User, id=customer_id)

#     # Check if the batch has already been granted to the customer
#     if batch in customer.batches.all():
#         messages.warning(request, f"Batch {batch.name} has already been granted to {customer.username}.")
#     else:
#         customer.batches.add(batch)
#         customer.save()
#         messages.success(request, f"Batch {batch.name} granted to {customer.username}.")

#     return redirect('grant_batches_to_customer', customer_id=customer.id)
@login_required
def grant_batch_to_customer(request, batch_id, customer_id):
    batch = get_object_or_404(Batch, id=batch_id)
    customer = get_object_or_404(User, id=customer_id)

    # Check if the batch has already been granted to the customer
    if CustomerBatch.objects.filter(user=customer, original_batch=batch).exists():
        messages.warning(request, f"Batch {batch.name} has already been granted to {customer.username}.")
    else:
        # Clone the batch for the customer
        custom_batch = CustomerBatch.objects.create(
            user=customer,
            original_batch=batch,
            custom_batch_name=f'{batch.name} - {customer.username}'
        )

        # Clone each order in the batch
        for order in batch.orders.all():
            custom_order = CustomerOrder.objects.create(
                customer_batch=custom_batch,
                original_order=order,
                custom_product=order.product,
                custom_lucky_order_position=order.lucky_order_position,
                custom_total_amount=order.total_amount
            )
            custom_order.custom_products.set(order.products.all())
            custom_order.save()

        messages.success(request, f"Batch {batch.name} granted to {customer.username}.")

    return redirect('grant_batches_to_customer', customer_id=customer.id)

# def remove_granted_batch(request, batch_id, customer_id):
#     batch = get_object_or_404(Batch, id=batch_id)
#     customer = get_object_or_404(User, id=customer_id)

#     # Check if the batch is currently granted to the customer
#     if batch in customer.batches.all():
#         customer.batches.remove(batch)
#         messages.success(request, f"Batch {batch.name} removed from {customer.username}'s Batch List.")
#     else:
#         messages.warning(request, f"Batch {batch.name} was not granted to {customer.username}.")

#     return redirect('grant_batches_to_customer', customer_id=customer.id)
@login_required
def remove_granted_batch(request, batch_id, customer_id):
    batch = get_object_or_404(Batch, id=batch_id)
    customer = get_object_or_404(User, id=customer_id)

    # Check if the batch has been granted to the customer
    customer_batch = CustomerBatch.objects.filter(user=customer, original_batch=batch).first()

    if customer_batch:
        # Delete the customer-specific batch and all related orders
        customer_batch.delete()
        messages.success(request, f"Batch {batch.name} and all related orders removed from {customer.username}'s Batch List.")
    else:
        messages.warning(request, f"Batch {batch.name} was not granted to {customer.username}.")

    return redirect('grant_batches_to_customer', customer_id=customer.id)

# fetch orders
@login_required
def fetch_custom_orders(request, batch_id,customer_id):
    
    # Get the batch based on the provided batch_id
    batch = get_object_or_404(Batch, id=batch_id)
    customer = get_object_or_404(User, id=customer_id)

    # Check if there is a custom batch for this customer
    custom_batch = CustomerBatch.objects.filter(user=customer, original_batch=batch).first()

    if custom_batch:
        
        # Fetch custom orders related to the custom batch
        orders = CustomerOrder.objects.filter(customer_batch=custom_batch).select_related('custom_product').prefetch_related('custom_products')
    else:
        # Fetch original orders related to the batch
        
        orders = Order.objects.filter(batch=batch).select_related('product').prefetch_related('products')

    orders_data = []
    for order in orders:
        products_data = []

        if custom_batch:
            # Handle the ForeignKey relationship (single product in custom order)
            if order.custom_product:
                products_data.append({
                    'name': order.custom_product.name,
                    'price':order.custom_product.price,
                    'commission_rate':order.custom_product.commission_rate,
                    'image_url': order.custom_product.image.url,
                    

                })

            # Handle the Many-to-Many relationship (additional products in lucky custom orders)
            for product in order.custom_products.all():
                products_data.append({
                    'name': product.name,
                    'image_url': product.image.url,
                })

            orders_data.append({
                'id': order.id,
                'order_type': order.original_order.order_type,
                'total_amount': order.custom_total_amount,
                'products': products_data,
            })
        else:
            # Handle the ForeignKey relationship (single product in original order)
            if order.product:
                products_data.append({
                    'name': order.product.name,
                    'price':order.product.price,
                    'commission_rate':order.product.commission_rate,
                    'image_url': order.product.image.url,
                    
                })

            # Handle the Many-to-Many relationship (additional products in lucky original orders)
            for product in order.products.all():
                products_data.append({
                    'name': product.name,
                    'price':product.price,
                    'commission_rate':product.commission_rate,
                    'image_url': product.image.url,
                })

            orders_data.append({
                'id': order.id,
                'order_type': order.order_type,
                'total_amount': order.total_amount,
                'products': products_data,
            })

    return JsonResponse({'orders': orders_data})



# update order

# @login_required
# def update_customer_order(request, order_id, customer_id):
#     customer = get_object_or_404(User, id=customer_id)
#     try:
#         customer_order = CustomerOrder.objects.get(id=order_id)
#     except CustomerOrder.DoesNotExist:
#         messages.error(request, f"You have not granted this batch to {customer.username}.")
#         return redirect('grant_batches_to_customer', customer_id=customer_id)

#     if request.method == 'POST':
#         new_total_amount = 0

#         if customer_order.original_order.order_type == 'Simple':
#             product = customer_order.custom_product
#             name_changed = product.name != request.POST.get('product_name')
#             price_changed = product.price != request.POST.get('product_price')
#             commission_rate_changed = product.commission_rate != request.POST.get('commission_rate')
#             image_changed = request.FILES.get('product_image') is not None

#             # Check if any changes have been made
#             if name_changed or price_changed or commission_rate_changed or image_changed:
#                 # Create a new product
#                 new_product = Product.objects.create(
#                     name=request.POST.get('product_name'),
#                     price=request.POST.get('product_price'),
#                     commission_rate=request.POST.get('commission_rate'),
#                     image=request.FILES.get('product_image') if image_changed else product.image
#                 )
#                 # Link the new product to the customer order
#                 customer_order.custom_product = new_product
#                 customer_order.save()

#             # Recalculate the total amount based on the new product
#             new_total_amount =float(new_product.price) + (float(new_product.price) * (float(new_product.commission_rate) * 0.01))

#         else:  # For 'Lucky' orders with multiple products
#             for product in customer_order.custom_products.all():
#                 name_changed = product.name != request.POST.get(f'product_name_{product.id}')
#                 price_changed = product.price != request.POST.get(f'product_price_{product.id}')
#                 commission_rate_changed = product.commission_rate != request.POST.get(f'commission_rate_{product.id}')
#                 image_changed = request.FILES.get(f'product_image_{product.id}') is not None

#                 # Check if any changes have been made
#                 if name_changed or price_changed or commission_rate_changed or image_changed:
#                     # Create a new product
#                     new_product = Product.objects.create(
#                         name=request.POST.get(f'product_name_{product.id}'),
#                         price=request.POST.get(f'product_price_{product.id}'),
#                         commission_rate=request.POST.get(f'commission_rate_{product.id}'),
#                         image=request.FILES.get(f'product_image_{product.id}') if image_changed else product.image
#                     )
#                     # Update the M2M relation to link the new product to the customer order
#                     customer_order.custom_products.remove(product)
#                     customer_order.custom_products.add(new_product)

#                     # Recalculate the total amount for this product
#                     new_total_amount += float(new_product.price) + (float(new_product.price) * (float(new_product.commission_rate) / 100))
#                 else:
#                     # If no changes, keep the current total for the product
#                     new_total_amount +=  float(product.price) + (float(product.price) * (float(product.commission_rate) / 100))

#         # Update the total amount with the new calculated value
#         customer_order.custom_total_amount = new_total_amount
#         customer_order.save()

#         messages.success(request, f"Order with ID: {order_id} was updated successfully.")

#         return redirect('grant_batches_to_customer', customer_id=customer_id)

#     return render(request, 'admin/update_custom_order.html', {'customer_order': customer_order})

@login_required
def update_customer_order(request, order_id, customer_id):
    customer = get_object_or_404(User, id=customer_id)
    try:
        customer_order = CustomerOrder.objects.get(id=order_id)
    except CustomerOrder.DoesNotExist:
        messages.error(request, f"You have not granted this batch to {customer.username}.")
        return redirect('grant_batches_to_customer', customer_id=customer_id)

    if request.method == 'POST':
        new_total_amount = 0
        create_new_product = False

        if customer_order.original_order.order_type == 'Simple':
            product = customer_order.custom_product

            # Ensure consistent type comparison
            name_changed = product.name != request.POST.get('product_name')
            price_changed = float(product.price) != float(request.POST.get('product_price'))
            commission_rate_changed = float(product.commission_rate) != float(request.POST.get('commission_rate'))
            image_changed = request.FILES.get('product_image') is not None

            # If any of these change flags are true, we create a new product
            if name_changed or price_changed or commission_rate_changed or image_changed:
                create_new_product = True

            if create_new_product:
                # Create a new product
                new_product = Product.objects.create(
                    name=request.POST.get('product_name'),
                    price=request.POST.get('product_price'),
                    commission_rate=request.POST.get('commission_rate'),
                    image=request.FILES.get('product_image') if image_changed else product.image
                )
                # Link the new product to the customer order
                customer_order.custom_product = new_product
                customer_order.save()

                # Recalculate the total amount based on the new product
                new_total_amount = float(new_product.price)
            else:
                # No changes, keep the current total amount
                new_total_amount = float(product.price) 

        else:  # For 'Lucky' orders with multiple products
            for product in customer_order.custom_products.all():
                name_changed = product.name != request.POST.get(f'product_name_{product.id}')
                price_changed = float(product.price) != float(request.POST.get(f'product_price_{product.id}'))
                commission_rate_changed = float(product.commission_rate) != float(request.POST.get(f'commission_rate_{product.id}'))
                image_changed = request.FILES.get(f'product_image_{product.id}') is not None

                # If any of these change flags are true, we create a new product
                if name_changed or price_changed or commission_rate_changed or image_changed:
                    create_new_product = True

                    # Create a new product
                    new_product = Product.objects.create(
                        name=request.POST.get(f'product_name_{product.id}'),
                        price=request.POST.get(f'product_price_{product.id}'),
                        commission_rate=request.POST.get(f'commission_rate_{product.id}'),
                        image=request.FILES.get(f'product_image_{product.id}') if image_changed else product.image
                    )
                    # Update the M2M relation to link the new product to the customer order
                    customer_order.custom_products.remove(product)
                    customer_order.custom_products.add(new_product)

                    # Recalculate the total amount for this product
                    new_total_amount += float(new_product.price) 
                else:
                    # No changes, keep the current total amount for this product
                    new_total_amount += float(product.price) 

        # Update the total amount with the new calculated value
        customer_order.custom_total_amount = new_total_amount
        customer_order.save()

        messages.success(request, f"Order with ID: {order_id} was updated successfully.")

        return redirect('grant_batches_to_customer', customer_id=customer_id)

    return render(request, 'admin/update_custom_order.html', {'customer_order': customer_order})



from django.contrib.admin.views.decorators import staff_member_required
@staff_member_required
@login_required
def delete_unused_products(request):
    unused_products = Product.objects.filter(
        orders__isnull=True, 
        lucky_orders__isnull=True,
        custom_orders__isnull=True,  # Adjust based on your actual field names
        custom_lucky_orders__isnull=True,
    )
    deleted_count, _ = unused_products.delete()
    
    messages.success(request, f"Deleted {deleted_count} unused products.")
    return redirect('Admin_dashboard')  # Redirect to the Django admin index or any other desired page
