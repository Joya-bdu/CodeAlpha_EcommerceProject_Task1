from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Product, CartItem, Order, OrderItem
from django.http import JsonResponse
import json
from .models import CartItem
from .models import Category

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'store/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form})

@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')


@login_required
def home_view(request):
    query = request.GET.get('q', '')  # সার্চ কিওয়ার্ড
    category_name = request.GET.get('category', '')  # ক্যাটেগরি নাম

    products = Product.objects.select_related('category').all()

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    if category_name:
        products = products.filter(category__name__iexact=category_name)  # category__name দিয়ে ফিল্টার

    # ক্যাটেগরির ইউনিক লিস্ট (ফিল্টার বক্সের জন্য)
    categories = Category.objects.all()  # Category model থেকে সব ক্যাটেগরি নিয়ে আসা

    context = {
        'products': products,
        'categories': categories,
        'search_query': query,
        'selected_category': category_name,
    }
    return render(request, 'store/home.html', context)

@login_required
def product_detail_view(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'store/product_detail.html', {'product': product})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"{product.name} added to cart.")
    return redirect('home')

@login_required
def update_cart_quantity(request):
    import json
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = data.get('quantity')

        if quantity < 1:
            return JsonResponse({'status': 'error', 'message': 'Quantity must be at least 1'})

        try:
            cart_item = CartItem.objects.get(user=request.user, product_id=product_id)
            cart_item.quantity = quantity
            cart_item.save()

            # নতুন কার্টের মোট টোটাল হিসাব
            cart_items = CartItem.objects.filter(user=request.user)
            total = sum(item.product.price * item.quantity for item in cart_items)

            return JsonResponse({
                'status': 'success',
                'message': 'Quantity updated',
                'item_total': cart_item.total_price(),
                'cart_total': total,
                'product_id': product_id
            })
        except CartItem.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Cart item not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

   
@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items:
        messages.info(request, "Your cart is empty!")
        return redirect('home')

    total = sum(item.total_price() for item in cart_items)

    if request.method == 'POST':
        order = Order.objects.create(user=request.user, total_amount=total)
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )
        cart_items.delete()  # empty cart after order
        messages.success(request, f"Order #{order.id} placed successfully!")
        return redirect('home')

    return render(request, 'store/checkout.html', {'cart_items': cart_items, 'total': total})

@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('view_cart')



