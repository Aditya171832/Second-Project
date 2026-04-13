from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Sum
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth import update_session_auth_hash
import re
from .forms import FarmerRegistrationForm, DealerRegistrationForm, ProductForm, CheckoutForm
from .models import Profile, Product, Category, Cart, CartItem, Order, OrderItem

def farmer_required(function=None):
    actual_decorator = user_passes_test(
        lambda u: hasattr(u, 'profile') and u.profile.user_type == 'farmer',
        login_url='/',
        redirect_field_name=None
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def dealer_required(function=None):
    actual_decorator = user_passes_test(
        lambda u: hasattr(u, 'profile') and u.profile.user_type == 'dealer',
        login_url='/',
        redirect_field_name=None
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def validate_phone(phone):
    pattern = r'^[6-9]\d{9}$'
    return bool(re.match(pattern, phone))

def validate_gst(gst_number):
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
    return bool(re.match(pattern, gst_number))

def validate_pincode(pincode):
    pattern = r'^\d{6}$'
    return bool(re.match(pattern, pincode))

def landing(request):
    return render(request, 'core/landing.html')

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    return render(request, 'core/contact.html')

def farmer_register(request):
    if request.method == 'POST':
        form = FarmerRegistrationForm(request.POST)
        if form.is_valid():
            # Validate phone
            phone = form.cleaned_data['phone']
            if not validate_phone(phone):
                messages.error(request, 'Enter valid 10-digit Indian phone number starting with 6-9.')
                return render(request, 'core/farmer_register_standalone.html', {'form': form})
            
            # Validate pincode
            pincode = form.cleaned_data['pincode']
            if not validate_pincode(pincode):
                messages.error(request, 'Enter valid 6-digit pincode.')
                return render(request, 'core/farmer_register_standalone.html', {'form': form})
            
            # Check email uniqueness
            from django.contrib.auth.models import User
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                messages.error(request, 'This email is already registered.')
                return render(request, 'core/farmer_register_standalone.html', {'form': form})
            
            # Check username uniqueness
            username = form.cleaned_data['username']
            if User.objects.filter(username=username).exists():
                messages.error(request, 'This username is already taken.')
                return render(request, 'core/farmer_register_standalone.html', {'form': form})
            
            # Save user and login
            user = form.save()
            login(request, user)
            messages.success(request, 'Farmer registration successful!')
            return redirect('core:farmer_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FarmerRegistrationForm()
    
    return render(request, 'core/farmer_register_standalone.html', {'form': form})

def dealer_register(request):
    if request.method == 'POST':
        form = DealerRegistrationForm(request.POST)
        if form.is_valid():
            # Validate phone
            phone = form.cleaned_data['phone']
            if not validate_phone(phone):
                messages.error(request, 'Enter valid 10-digit Indian phone number starting with 6-9.')
                return render(request, 'core/dealer_register_standalone.html', {'form': form})
            
            # Validate pincode
            pincode = form.cleaned_data['pincode']
            if not validate_pincode(pincode):
                messages.error(request, 'Enter valid 6-digit pincode.')
                return render(request, 'core/dealer_register_standalone.html', {'form': form})
            
            # Validate GST
            gst_number = form.cleaned_data['gst_number']
            if not validate_gst(gst_number):
                messages.error(request, 'Enter valid 15-character GST number.')
                return render(request, 'core/dealer_register_standalone.html', {'form': form})
            
            # Check email uniqueness
            from django.contrib.auth.models import User
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                messages.error(request, 'This email is already registered.')
                return render(request, 'core/dealer_register_standalone.html', {'form': form})
            
            # Check username uniqueness
            username = form.cleaned_data['username']
            if User.objects.filter(username=username).exists():
                messages.error(request, 'This username is already taken.')
                return render(request, 'core/dealer_register_standalone.html', {'form': form})
            
            # Check GST uniqueness
            if Profile.objects.filter(gst_number=gst_number).exists():
                messages.error(request, 'This GST number is already registered.')
                return render(request, 'core/dealer_register_standalone.html', {'form': form})
            
            # Save user and login
            user = form.save()
            login(request, user)
            messages.success(request, 'Dealer registration successful!')
            return redirect('core:dealer_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DealerRegistrationForm()
    
    return render(request, 'core/dealer_register_standalone.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                
                try:
                    profile = user.profile
                    if profile.user_type == 'farmer':
                        return redirect('core:farmer_dashboard')
                    elif profile.user_type == 'dealer':
                        return redirect('core:dealer_dashboard')
                    else:
                        messages.error(request, 'Invalid user type.')
                        return redirect('core:landing')
                except Profile.DoesNotExist:
                    messages.error(request, 'Profile not found.')
                    return redirect('core:landing')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'core/login_standalone.html', {'form': form})

# REST OF YOUR CODE REMAINS EXACTLY THE SAME FROM user_logout() TO handler500()
# ... [All your existing code below this line remains unchanged] ...

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('core:landing')

@login_required
def edit_profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(
            user=request.user,
            user_type='farmer',
            phone='',
            address='',
            city='',
            state='',
            pincode=''
        )
        messages.info(request, 'Please update your profile information.')
    
    recent_orders = []
    if profile.user_type == 'farmer':
        recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    elif profile.user_type == 'dealer':
        recent_orders = Order.objects.filter(
            orderitem__dealer=request.user
        ).distinct().order_by('-created_at')[:5]
    
    context = {
        'user': request.user,
        'profile': profile,
        'recent_orders': recent_orders,
    }
    return render(request, 'core/edit_profile.html', context)

@login_required
def update_profile(request):
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('core:edit_profile')
    
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('core:edit_profile')
    
    user = request.user
    
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    pincode = request.POST.get('pincode', '').strip()
    
    if not first_name:
        messages.error(request, 'First name is required.')
        return redirect('core:edit_profile')
    
    if not last_name:
        messages.error(request, 'Last name is required.')
        return redirect('core:edit_profile')
    
    if not email:
        messages.error(request, 'Email is required.')
        return redirect('core:edit_profile')
    
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email(email)
    except ValidationError:
        messages.error(request, 'Please enter a valid email address.')
        return redirect('core:edit_profile')
    
    from django.contrib.auth.models import User
    if User.objects.filter(email=email).exclude(id=user.id).exists():
        messages.error(request, 'This email is already registered by another user.')
        return redirect('core:edit_profile')
    
    if phone and not validate_phone(phone):
        messages.error(request, 'Please enter a valid 10-digit Indian phone number.')
        return redirect('core:edit_profile')
    
    if pincode and not validate_pincode(pincode):
        messages.error(request, 'Please enter a valid 6-digit pincode.')
        return redirect('core:edit_profile')
    
    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    user.save()
    
    profile.phone = phone
    profile.address = request.POST.get('address', profile.address)
    profile.city = request.POST.get('city', profile.city).strip()
    profile.state = request.POST.get('state', profile.state).strip()
    profile.pincode = pincode
    
    if profile.user_type == 'farmer':
        farm_size = request.POST.get('farm_size', '')
        if farm_size:
            try:
                profile.farm_size = float(farm_size)
                if profile.farm_size <= 0:
                    messages.error(request, 'Farm size must be greater than 0.')
                    return redirect('core:edit_profile')
            except ValueError:
                messages.error(request, 'Invalid farm size.')
                return redirect('core:edit_profile')
        profile.farm_location = request.POST.get('farm_location', profile.farm_location).strip()
    
    elif profile.user_type == 'dealer':
        gst_number = request.POST.get('gst_number', '').strip()
        if gst_number:
            if not validate_gst(gst_number):
                messages.error(request, 'Please enter a valid GST number.')
                return redirect('core:edit_profile')
            if Profile.objects.filter(gst_number=gst_number).exclude(user=user).exists():
                messages.error(request, 'This GST number is already registered by another dealer.')
                return redirect('core:edit_profile')
            profile.gst_number = gst_number
        
        profile.company_name = request.POST.get('company_name', profile.company_name).strip()
        profile.business_address = request.POST.get('business_address', profile.business_address)
    
    profile.save()
    
    messages.success(request, 'Profile updated successfully!')
    return redirect('core:edit_profile')

@login_required
def change_password(request):
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('core:edit_profile')
    
    old_password = request.POST.get('old_password')
    new_password1 = request.POST.get('new_password1')
    new_password2 = request.POST.get('new_password2')
    
    if not request.user.check_password(old_password):
        messages.error(request, 'Your current password was entered incorrectly.')
        return redirect('core:edit_profile')
    
    if new_password1 != new_password2:
        messages.error(request, 'The new password fields did not match.')
        return redirect('core:edit_profile')
    
    if len(new_password1) < 8:
        messages.error(request, 'Password must be at least 8 characters long.')
        return redirect('core:edit_profile')
    
    if not re.search(r'[A-Z]', new_password1):
        messages.error(request, 'Password must contain at least one uppercase letter.')
        return redirect('core:edit_profile')
    
    if not re.search(r'[a-z]', new_password1):
        messages.error(request, 'Password must contain at least one lowercase letter.')
        return redirect('core:edit_profile')
    
    if not re.search(r'[0-9]', new_password1):
        messages.error(request, 'Password must contain at least one digit.')
        return redirect('core:edit_profile')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password1):
        messages.error(request, 'Password must contain at least one special character.')
        return redirect('core:edit_profile')
    
    if old_password == new_password1:
        messages.error(request, 'New password must be different from old password.')
        return redirect('core:edit_profile')
    
    request.user.set_password(new_password1)
    request.user.save()
    
    update_session_auth_hash(request, request.user)
    
    messages.success(request, 'Your password has been changed successfully!')
    return redirect('core:edit_profile')

@login_required
@farmer_required
def farmer_dashboard(request):
    featured_products = Product.objects.filter(is_available=True, stock_quantity__gt=0)[:6]
    
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        cart = Cart.objects.create(user=request.user)
    
    cart_items = CartItem.objects.filter(cart=cart)
    cart_count = cart_items.count()
    
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    order_count = Order.objects.filter(user=request.user).count()
    
    return render(request, 'core/farmer_dashboard.html', {
        'featured_products': featured_products,
        'cart': cart,
        'cart_items': cart_items,
        'cart_count': cart_count,
        'recent_orders': recent_orders,
        'order_count': order_count
    })

@login_required
@dealer_required
def dealer_dashboard(request):
    dealer_products = Product.objects.filter(dealer=request.user)
    
    total_products = dealer_products.count()
    
    dealer_order_items = OrderItem.objects.filter(dealer=request.user)
    
    unique_order_ids = dealer_order_items.values_list('order_id', flat=True).distinct()
    total_orders = len(unique_order_ids)
    
    total_revenue = 0
    if dealer_order_items.exists():
        total_revenue = dealer_order_items.aggregate(
            total=Sum('item_total')
        )['total'] or 0
    
    unique_customers = Order.objects.filter(
        orderitem__dealer=request.user
    ).values_list('user_id', flat=True).distinct().count()
    
    recent_orders = Order.objects.filter(
        id__in=unique_order_ids
    ).order_by('-created_at')[:5]
    
    low_stock_products = dealer_products.filter(stock_quantity__lt=10, stock_quantity__gt=0)
    out_of_stock_products = dealer_products.filter(stock_quantity=0)
    
    top_products = dealer_order_items.values(
        'product__name', 'product__id'
    ).annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('item_total')
    ).order_by('-total_sold')[:5]
    
    return render(request, 'core/dealer_dashboard.html', {
        'dealer_products': dealer_products,
        'recent_orders': recent_orders,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_customers': unique_customers,
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'top_products': top_products,
    })

def product_list(request):
    products = Product.objects.filter(is_available=True, stock_quantity__gt=0)
    
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    category_filter = request.GET.get('category', '')
    if category_filter:
        products = products.filter(category__name=category_filter)
    
    categories = Category.objects.all()
    
    cart = None
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            if profile.user_type == 'farmer':
                cart = Cart.objects.filter(user=request.user).first()
                if not cart:
                    cart = Cart.objects.create(user=request.user)
        except Profile.DoesNotExist:
            pass
    
    return render(request, 'core/product_list.html', {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_filter,
        'cart': cart
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_available=True)
    
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True,
        stock_quantity__gt=0
    ).exclude(id=product_id)[:4]
    
    return render(request, 'core/product_detail.html', {
        'product': product,
        'related_products': related_products
    })

@login_required
@farmer_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_available=True)
    
    if product.stock_quantity <= 0:
        messages.error(request, f'Sorry, {product.name} is out of stock.')
        return redirect('core:product_list')
    
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        cart = Cart.objects.create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        if cart_item.quantity + 1 > product.stock_quantity:
            messages.warning(request, f'Cannot add more {product.name}. Only {product.stock_quantity} available in stock.')
        else:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f'{product.name} added to cart!')
    else:
        messages.success(request, f'{product.name} added to cart!')
    
    return redirect('core:product_list')

@login_required
@farmer_required
def view_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        cart = Cart.objects.create(user=request.user)
    
    cart_items = CartItem.objects.filter(cart=cart)
    
    subtotal = sum(item.total_price() for item in cart_items)
    tax = subtotal * Decimal('0.18')
    total_amount = subtotal + tax
    
    return render(request, 'core/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'total_amount': total_amount
    })

@login_required
@farmer_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    action = request.POST.get('action')
    
    if action == 'increase':
        if cart_item.quantity + 1 > cart_item.product.stock_quantity:
            messages.warning(request, f'Cannot add more {cart_item.product.name}. Only {cart_item.product.stock_quantity} available in stock.')
        else:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f'Increased {cart_item.product.name} quantity')
    elif action == 'decrease' and cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        messages.success(request, f'Decreased {cart_item.product.name} quantity')
    
    return redirect('core:view_cart')

@login_required
@farmer_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    
    messages.success(request, f'{product_name} removed from cart')
    return redirect('core:view_cart')

@login_required
@dealer_required
def dealer_add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.dealer = request.user
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('core:dealer_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm()
    
    categories = Category.objects.all()
    
    return render(request, 'core/dealer_add_product.html', {
        'form': form,
        'categories': categories
    })

@login_required
@dealer_required
def dealer_edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, dealer=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('core:dealer_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm(instance=product)
    
    categories = Category.objects.all()
    
    return render(request, 'core/dealer_edit_product.html', {
        'form': form,
        'categories': categories,
        'product': product
    })

@login_required
@farmer_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        cart = Cart.objects.create(user=request.user)
    
    cart_items = CartItem.objects.filter(cart=cart)
    
    if not cart_items:
        messages.error(request, 'Your cart is empty!')
        return redirect('core:product_list')
    
    out_of_stock_items = []
    for item in cart_items:
        if item.quantity > item.product.stock_quantity:
            out_of_stock_items.append(item.product.name)
    
    if out_of_stock_items:
        messages.error(request, f'Some items are out of stock: {", ".join(out_of_stock_items)}')
        return redirect('core:view_cart')
    
    subtotal = sum(item.total_price() for item in cart_items)
    tax = subtotal * Decimal('0.18')
    total_amount = subtotal + tax
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            pincode = form.cleaned_data['pincode']
            
            if not validate_phone(phone):
                form.add_error('phone', 'Please enter a valid 10-digit Indian phone number.')
                return render(request, 'core/checkout.html', {
                    'cart': cart,
                    'cart_items': cart_items,
                    'subtotal': subtotal,
                    'tax': tax,
                    'total_amount': total_amount,
                    'form': form
                })
            
            if not validate_pincode(pincode):
                form.add_error('pincode', 'Please enter a valid 6-digit pincode.')
                return render(request, 'core/checkout.html', {
                    'cart': cart,
                    'cart_items': cart_items,
                    'subtotal': subtotal,
                    'tax': tax,
                    'total_amount': total_amount,
                    'form': form
                })
            
            order = Order.objects.create(
                user=request.user,
                total_amount=total_amount,
                shipping_full_name=form.cleaned_data['full_name'],
                shipping_address=form.cleaned_data['address'],
                shipping_city=form.cleaned_data['city'],
                shipping_state=form.cleaned_data['state'],
                shipping_pincode=pincode,
                shipping_phone=phone,
                payment_status='completed'
            )
            
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    dealer=cart_item.product.dealer,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price,
                    item_total=cart_item.total_price()
                )
                
                cart_item.product.stock_quantity -= cart_item.quantity
                cart_item.product.save()
            
            cart_items.delete()
            
            messages.success(request, f'Order #{order.order_number} placed successfully!')
            return redirect('core:order_confirmation', order_id=order.id)
    else:
        initial_data = {}
        try:
            profile = request.user.profile
            initial_data = {
                'full_name': f"{request.user.first_name} {request.user.last_name}",
                'address': profile.address,
                'city': profile.city,
                'state': profile.state,
                'pincode': profile.pincode,
                'phone': profile.phone
            }
        except Profile.DoesNotExist:
            pass
        
        form = CheckoutForm(initial=initial_data)
    
    return render(request, 'core/checkout.html', {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'total_amount': total_amount,
        'form': form
    })

@login_required
@farmer_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    
    return render(request, 'core/order_confirmation.html', {
        'order': order,
        'order_items': order_items
    })

@login_required
@farmer_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    total_orders = orders.count()
    total_spent = sum(order.total_amount for order in orders)
    pending_orders = orders.filter(status='pending').count()
    
    return render(request, 'core/order_history.html', {
        'orders': orders,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'pending_orders': pending_orders
    })

@login_required
@farmer_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    
    return render(request, 'core/order_detail.html', {
        'order': order,
        'order_items': order_items
    })

@login_required
@dealer_required
def dealer_orders(request):
    orders = Order.objects.filter(
        orderitem__dealer=request.user
    ).distinct().order_by('-created_at')
    
    total_orders = orders.count()
    total_revenue = 0
    for order in orders:
        order_items = OrderItem.objects.filter(order=order, dealer=request.user)
        for item in order_items:
            total_revenue += item.quantity * item.price
    
    pending_orders = orders.filter(status='pending').count()
    
    return render(request, 'core/dealer_orders.html', {
        'orders': orders,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders
    })

@login_required
@dealer_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if not OrderItem.objects.filter(order=order, dealer=request.user).exists():
        messages.error(request, 'You are not authorized to update this order.')
        return redirect('core:dealer_orders')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        tracking_number = request.POST.get('tracking_number', '')
        
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            
            if new_status == 'shipped':
                order.tracking_number = tracking_number
                order.shipped_at = timezone.now()
            elif new_status == 'delivered':
                order.delivered_at = timezone.now()
            
            order.save()
            messages.success(request, f'Order #{order.order_number} status updated to {new_status}.')
    
    return redirect('core:dealer_orders')

def handler404(request, exception):
    return render(request, 'core/404.html', status=404)

def handler500(request):
    return render(request, 'core/500.html', status=500)