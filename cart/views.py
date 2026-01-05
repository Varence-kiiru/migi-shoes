from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from models_app.models import ShoeVariant
from models_app.models import CartItem
from models_app.models import Order, OrderItem, Notification
from models_app.models import Address, PaymentMethod
from django.core.exceptions import ValidationError
from .forms import AddressForm, PaymentMethodForm, ContactForm
from django.urls import reverse
from django.http import HttpResponseRedirect
from decimal import Decimal
from Core.models import CompanySettings

def add_to_cart(request):
    """Add a variant to the cart using session for anonymous users or DB for authenticated users.
    """
    variant_id = request.POST.get('variant')
    variant = get_object_or_404(ShoeVariant, variant_id=variant_id)

    if request.user.is_authenticated and hasattr(request.user, 'customer_profile'):
        customer = request.user.customer_profile

        cart_item, created = CartItem.objects.get_or_create(
            customer=customer,
            variant=variant,
            defaults={'quantity': 1}
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()
    else:
        cart = request.session.get('cart', {})
        # store quantities as ints; keys as strings
        cart[str(variant.variant_id)] = int(cart.get(str(variant.variant_id), 0)) + 1
        request.session['cart'] = cart

    return redirect('cart:summary')


def cart_summary(request):
    """Render cart summary for authenticated users (DB cart) or anonymous users (session cart)."""
    company = CompanySettings.objects.first()
    shipping_fee = company.shipping_fee if company else Decimal('150.00')

    if request.user.is_authenticated and hasattr(request.user, 'customer_profile'):
        customer = request.user.customer_profile
        cart_items = CartItem.objects.filter(customer=customer)

        subtotal = sum(item.variant.shoe.price * item.quantity for item in cart_items)
        final_total = subtotal + shipping_fee

        return render(request, 'cart/summary.html', {
            'cart_items': cart_items,
            'total': subtotal,
            'shipping_fee': shipping_fee,
            'final_total': final_total,
        })

    # anonymous/session cart
    session_cart = request.session.get('cart', {})
    cart_items = []
    subtotal = 0

    for variant_id, qty in session_cart.items():
        variant = ShoeVariant.objects.filter(variant_id=variant_id).first()
        if not variant:
            continue
        item_total = (variant.shoe.price) * int(qty)  # discounted price for display
        subtotal += item_total  # discounted prices for subtotal

        cart_item = {
            'id': variant.variant_id,  # used by template for url of shoe
            'variant': variant,
            'quantity': int(qty),
            'total_price': item_total,
        }
        cart_items.append(cart_item)

    final_total = subtotal + shipping_fee

    return render(request, 'cart/summary.html', {
        'cart_items': cart_items,
        'total': subtotal,
        'shipping_fee': shipping_fee,
        'final_total': final_total,
    })

def remove_from_cart(request, item_id):
    #for logged-in customer
    if request.user.is_authenticated and hasattr(request.user, 'customer_profile'):
        item = get_object_or_404(CartItem, id=item_id, customer=request.user.customer_profile)
        item.delete()
    else: #anonymous user
        cart = request.session.get('cart', {})
        # item_id for session mode is the variant_id
        cart.pop(str(item_id), None)
        request.session['cart'] = cart

    return redirect('cart:summary')

def update_quantity(request, item_id):
    # require post
    if request.method != 'POST':
        return redirect('cart:summary')

    #increment or decrement action
    action = request.POST.get('action')

    #logged-in customer
    if request.user.is_authenticated and hasattr(request.user, 'customer_profile'):
        item = get_object_or_404(CartItem, id=item_id, customer=request.user.customer_profile)

        if action == 'increment':
            item.quantity += 1
            item.save()
        elif action == 'decrement' and item.quantity > 1:
            item.quantity -= 1
            item.save()

    else: #anonymous user
        cart = request.session.get('cart', {})
        key = str(item_id)
        if key in cart:
            if action == 'increment':
                cart[key] = int(cart.get(key, 0)) + 1
            elif action == 'decrement':
                if int(cart.get(key, 0)) > 1:
                    cart[key] = int(cart.get(key, 0)) - 1
        request.session['cart'] = cart

    return redirect('cart:summary')

@login_required
def checkout(request):
    company = CompanySettings.objects.first()
    shipping_fee = company.shipping_fee if company else Decimal('150.00')

    customer = request.user.customer_profile
    cart_items = customer.cart_items.all()  # via related name
    addresses = customer.addresses.all()
    payment_methods = customer.payment_methods.all()

    # Prefill contact from the logged-in user
    contact_initial = {
        'full_name': customer.full_name,
        'email': request.user.email,
        'phone': customer.phone or '',
    }
    contact_form = ContactForm(initial=contact_initial)
    shipping_form = AddressForm(prefix='shipping')
    billing_form = AddressForm(prefix='billing')
    payment_form = PaymentMethodForm()
    # defaults for select inputs (used to preserve selection on errors)
    shipping_selected = 'new'
    billing_selected = 'same'
    payment_selected = 'new'

    if request.method == 'POST' and 'place_order' in request.POST:
        # Bind forms only as needed
        contact_form = ContactForm(request.POST)
        shipping_existing = request.POST.get('shipping_existing')
        billing_existing = request.POST.get('billing_existing')
        payment_existing = request.POST.get('payment_existing')

        # preserve what the user selected so we can re-render the selects on error
        shipping_selected = shipping_existing or 'new'
        billing_selected = billing_existing or 'same'
        payment_selected = payment_existing or 'new'

        # Validate contact
        valid = True
        if not contact_form.is_valid():
            valid = False

        # Create correct shipping address instance
        shipping_address_obj = None
        if shipping_existing and shipping_existing != 'new':
            try:
                shipping_address_obj = Address.objects.get(addr_id=shipping_existing, customer=customer)
            except Address.DoesNotExist:
                valid = False
                shipping_form.add_error(None, 'Selected shipping address not found.')
        else:
            shipping_form = AddressForm(request.POST, prefix='shipping')
            if shipping_form.is_valid():
                shipping_address_obj = shipping_form.save(commit=False)
                # Do not attach to customer for order-only address
                shipping_address_obj.customer = None
                shipping_address_obj.save()
            else:
                valid = False

        # Create correct billing address instance
        billing_address_obj = None
        if billing_existing == 'same':
            billing_address_obj = shipping_address_obj
        elif not billing_existing or billing_existing == 'new':
            billing_form = AddressForm(request.POST, prefix='billing')
            if billing_form.is_valid():
                billing_address_obj = billing_form.save(commit=False)
                # Do not attach to customer for order-only address
                billing_address_obj.customer = None
                billing_address_obj.save()
            else:
                billing_form.add_error(None, 'Invalid billing address.')
        else:
            try:
                billing_address_obj = Address.objects.get(addr_id=billing_existing, customer=customer)
            except Address.DoesNotExist:
                valid = False
                billing_form.add_error(None, 'Selected billing address not found.')

        # Validate payment: prefer 'new' payment, then COD, then existing-selection lookup
        payment_method_obj = None

        if payment_existing == 'new':
            payment_form = PaymentMethodForm(request.POST)
            if not payment_form.is_valid():
                valid = False
            else:
                payment_method_obj = payment_form.save(commit=False)
                payment_method_obj.customer = None
                payment_method_obj.save()
        elif payment_existing == 'cod':
            # Cash on delivery: explicitly no payment method object
            payment_method_obj = None
        elif payment_existing:
            try:
                payment_method_obj = PaymentMethod.objects.get(card_id=payment_existing, customer=customer)
            except PaymentMethod.DoesNotExist:
                valid = False
                payment_form.add_error(None, 'Selected payment method not found.')
        else:
            # No payment option picked
            valid = False
            payment_form.add_error(None, 'Please select a payment method.')

        if not valid:
            subtotal = sum(item.variant.shoe.price * item.quantity for item in cart_items)
            final_total = subtotal + shipping_fee
            return render(request, 'cart/checkout.html', {
                'cart_items': cart_items,
                'total': subtotal,
                'shipping_fee': shipping_fee,
                'final_total': final_total,
                'customer': customer,
                'addresses': addresses,
                'payment_methods': payment_methods,
                # forms with errors
                'contact_form': contact_form,
                'shipping_form': shipping_form,
                'billing_form': billing_form,
                'payment_form': payment_form,
                'shipping_selected': shipping_selected,
                'billing_selected': billing_selected,
                'payment_selected': payment_selected,
            })

        # Create order using Address FKs
        total = sum(item.variant.shoe.original_price * item.quantity for item in cart_items)
        discount = sum(item.variant.shoe.discount * item.quantity for item in cart_items)
        final_total = total - discount

        order = Order.objects.create(
            customer=customer,
            total_price=final_total,
            shipping_address=shipping_address_obj,
            billing_address=billing_address_obj,
            payment_method=payment_method_obj,
            status='Pending',
            discount_amount=discount,
            subtotal=total,
            shipping_cost=shipping_fee,
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                variant=item.variant,
                quantity=item.quantity,
                price=item.variant.shoe.price,
            )

        Notification.objects.create(
            customer=customer,
            message=f"Your order #{order.order_id} has been confirmed!",
            related_order=order,
        )

        # Clear cart
        cart_items.delete()

        return redirect('customer:customer_orders')

    # GET: render checkout
    subtotal = sum(item.variant.shoe.price * item.quantity for item in cart_items)
    final_total = subtotal + shipping_fee

    context = {
        'cart_items': cart_items,
        'total': subtotal,
        'shipping_fee': shipping_fee,
        'final_total': final_total,
        'customer': customer,
        'addresses': addresses,
        'payment_methods': payment_methods,
        'contact_form': contact_form,
        'shipping_form': shipping_form,
        'billing_form': billing_form,
        'payment_form': payment_form,
        'shipping_selected': shipping_selected,
        'billing_selected': billing_selected,
        'payment_selected': payment_selected,
    }
    return render(request, 'cart/checkout.html', context)
