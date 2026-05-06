from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Product, Cart, CartItem, Wishlist, WishlistItem, Order, OrderItem, Notification
from .forms import ProductForm
from accounts.models import CustomUser

def home(request):
    return render(request, 'store/home.html')

def shop(request):
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(name__icontains=query).order_by('-created_at')
    else:
        products = Product.objects.all().order_by('-created_at')
        
    wishlist_product_ids = []
    if request.user.is_authenticated:
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        wishlist_product_ids = wishlist.items.values_list('product_id', flat=True)
        
    return render(request, 'store/shop.html', {
        'products': products, 
        'query': query,
        'wishlist_product_ids': wishlist_product_ids
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

@login_required
def add_to_cart(request, pk):
    if not request.user.is_customer():
        messages.error(request, 'Only customers can buy products.')
        return redirect('home')
        
    product = get_object_or_404(Product, pk=pk)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    # Increment quantity if already in cart
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        
    messages.success(request, f'{product.name} has been added to your cart.')
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': f'{product.name} added to cart.'})
        
    return redirect('cart')

@login_required
def buy_now(request, pk):
    if not request.user.is_customer():
        messages.error(request, 'Only customers can buy products.')
        return redirect('home')
        
    product = get_object_or_404(Product, pk=pk)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        
    return redirect('checkout')

@login_required
def remove_from_cart(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    cart_item.delete()
    
    messages.info(request, 'Item removed from your cart.')
    return redirect('cart')

@login_required
def update_cart_quantity(request, pk, action):
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    
    if action == 'increment':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrement':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            # Remove if quantity becomes 0
            cart_item.delete()
            messages.info(request, f'{cart_item.product.name} removed from cart.')
            
    return redirect('cart')

@login_required
def cart_view(request):
    if not request.user.is_customer():
        return redirect('home')
        
    cart, _ = Cart.objects.get_or_create(user=request.user)
    
    total = sum(item.total_price() for item in cart.items.all())
    
    return render(request, 'store/cart.html', {
        'cart': cart, 
        'total': total
    })

@login_required
def checkout(request):
    if not request.user.is_customer():
        return redirect('home')
        
    cart = get_object_or_404(Cart, user=request.user)
    
    if cart.items.count() == 0:
        messages.warning(request, 'Your cart is empty. Add some products first.')
        return redirect('home')

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address_text = request.POST.get('address', '').strip()

        if not address_text or not full_name or not phone:
            messages.error(request, 'Please provide all shipping details.')
            return redirect('checkout')

        total = sum(item.total_price() for item in cart.items.all())

        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            phone_number=phone,
            address=address_text,
            total_amount=total
        )

        # Move all cart items over to the new order
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                seller=item.product.seller,
                # Lock in the price at checkout
                price=item.product.discount_price if item.product.discount_price else item.product.price,
                quantity=item.quantity
            )

        # Empty the cart after successful checkout
        cart.items.all().delete()
        messages.success(request, 'Your order has been placed successfully!')
        return redirect('orders')

    total = sum(item.total_price() for item in cart.items.all())
    return render(request, 'store/checkout.html', {'cart': cart, 'total': total})

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/orders.html', {'orders': orders})

@login_required
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if order.status == 'Pending':
        order.status = 'Cancelled'
        order.save()
        messages.success(request, f'Order #{order.id} has been cancelled.')
    else:
        messages.error(request, 'You can only cancel pending orders.')
    return redirect('orders')

@login_required
def mark_notification_as_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def wishlist_view(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    return render(request, 'store/wishlist.html', {'wishlist': wishlist})

@login_required
def add_to_wishlist(request, pk):
    product = get_object_or_404(Product, pk=pk)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    
    WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)
    messages.success(request, f'{product.name} added to your wishlist.')
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': f'{product.name} added to wishlist.'})
        
    return redirect('wishlist')

@login_required
def remove_from_wishlist(request, pk):
    wishlist_item = get_object_or_404(WishlistItem, pk=pk, wishlist__user=request.user)
    wishlist_item.delete()
    
    messages.info(request, 'Item removed from wishlist.')
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'info', 'message': 'Item removed from wishlist.'})
        
    return redirect('wishlist')

# ==========================================
# Seller Views
# ==========================================

@login_required
def seller_dashboard(request):
    if not request.user.is_seller():
        return redirect('home')
        
    if not request.user.is_approved:
        messages.warning(request, 'Your account is pending admin approval.')
        return redirect('home')
        
    products = Product.objects.filter(seller=request.user)
    # Get all order items that belong to products sold by this user
    orders = OrderItem.objects.filter(seller=request.user).order_by('-order__created_at')
    
    return render(request, 'store/seller_dashboard.html', {
        'products': products, 
        'orders': orders
    })

@login_required
def add_product(request):
    if not request.user.is_seller():
        return redirect('home')
        
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            
            messages.success(request, 'Product added successfully.')
            return redirect('seller_dashboard')
    else:
        form = ProductForm()
        
    return render(request, 'store/add_product.html', {'form': form})

@login_required
def edit_product(request, pk):
    if not request.user.is_seller():
        return redirect('home')
        
    # Ensure they can only edit their own products
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('seller_dashboard')
    else:
        form = ProductForm(instance=product)
        
    return render(request, 'store/add_product.html', {'form': form, 'edit': True})

@login_required
def delete_product(request, pk):
    if not request.user.is_seller():
        return redirect('home')
        
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        
    return redirect('seller_dashboard')

@login_required
def update_order_status(request, pk):
    if not request.user.is_seller():
        return redirect('home')
        
    if request.method == 'POST':
        # Now pk refers to OrderItem pk
        order_item = get_object_or_404(OrderItem, pk=pk, seller=request.user)
        status = request.POST.get('status')
        
        valid_statuses = dict(Order.STATUS_CHOICES).keys()
        if status in valid_statuses:
            order_item.status = status
            order_item.save()
            
            # Create notification for the customer
            Notification.objects.create(
                user=order_item.order.user,
                message=f"Your item '{order_item.product.name}' in order #{order_item.order.id} status has been updated to '{status}'."
            )
            
            messages.success(request, f"Item '{order_item.product.name}' status updated to {status}.")
            
    return redirect('seller_dashboard')

@login_required
def update_stock(request, pk):
    if not request.user.is_seller():
        return redirect('home')
        
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    if request.method == 'POST':
        stock = request.POST.get('stock')
        if stock is not None:
            product.stock = int(stock)
            product.save()
            messages.success(request, f'Stock for {product.name} updated.')
            
    return redirect('seller_dashboard')

# ==========================================
# Admin Views
# ==========================================

@login_required
def admin_dashboard(request):
    if not (request.user.is_superuser or request.user.user_type == 'admin'):
        return redirect('home')
        
    users_list = CustomUser.objects.exclude(id=request.user.id).order_by('-date_joined')
    products_count = Product.objects.count()
    orders_count = Order.objects.count()
    recent_orders = Order.objects.all().order_by('-created_at')[:5]
    
    return render(request, 'store/admin_dashboard.html', {
        'users_list': users_list,
        'products_count': products_count,
        'orders_count': orders_count,
        'recent_orders': recent_orders
    })

@login_required
def toggle_user_status(request, pk):
    if not (request.user.is_superuser or request.user.user_type == 'admin'):
        return redirect('home')
        
    if request.method == 'POST':
        target_user = get_object_or_404(CustomUser, pk=pk)
        target_user.is_active = not target_user.is_active
        target_user.save()
        status_msg = "unblocked" if target_user.is_active else "blocked"
        messages.success(request, f'User {target_user.username} has been {status_msg}.')
        
    return redirect('admin_dashboard')

@login_required
def approve_seller(request, pk):
    if not (request.user.is_superuser or request.user.user_type == 'admin'):
        return redirect('home')
        
    if request.method == 'POST':
        target_user = get_object_or_404(CustomUser, pk=pk)
        if target_user.user_type == 'seller':
            target_user.is_approved = True
            target_user.save()
            messages.success(request, f'Seller {target_user.username} has been approved.')
            
            # Notify the seller
            Notification.objects.create(
                user=target_user,
                message="Your seller account has been approved! You can now access your dashboard and add products."
            )
            
    return redirect('admin_dashboard')
