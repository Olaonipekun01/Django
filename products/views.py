import stripe
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import SignUpForm
from django.conf import settings
from .models import Order
from .models import Product, Category
    # views.py
from django.db.models import Q
# views.py
from django.core.mail import send_mail




def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout(request):
    if request.method == 'POST':
        charge = stripe.Charge.create(
            amount=5000,  # amount in cents
            currency='usd',
            description='Example charge',
            source=request.POST['stripeToken']
        )
        order = Order.objects.create(user=request.user, total=50)
        return redirect('order_complete')

    return render(request, 'checkout.html')



def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.all()
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'product_list.html', {'category': category, 'categories': categories, 'products': products})


# views.py
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        rating = request.POST['rating']
        comment = request.POST['comment']
        Review.objects.create(product=product, user=request.user, rating=rating, comment=comment)
        return redirect('product_detail', product_id=product.id)
    




def search(request):
    query = request.GET.get('q')
    products = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    return render(request, 'search_results.html', {'products': products})


# views.py
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist.products.add(product)
    return redirect('wishlist_detail')
def wishlist_detail(request):
    wishlist = Wishlist.objects.get(user=request.user)
    return render(request, 'wishlist_detail.html', {'wishlist': wishlist})



# views.py
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'order_history.html', {'orders': orders})



# views.py
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.stock == 0:
        out_of_stock = True
    else:
        out_of_stock = False
    return render(request, 'product_detail.html', {'product': product, 'out_of_stock': out_of_stock})



def send_order_confirmation(order):
    subject = f"Order #{order.id} Confirmation"
    message = f"Thank you for your order. Your order ID is {order.id}."
    send_mail(subject, message, 'from@example.com', [order.user.email])

