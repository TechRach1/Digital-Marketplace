from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .models import Product
from .forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth import logout 
from django.contrib.auth.decorators import login_required
from .forms import ProductForm
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


def product_list(request):
    """
    Retrieve all products from the database and render the product list page.
    """
    products = Product.objects.all()
    return render(request, 'shop/product_list.html', {'products': products})

def first_page(request):
    """
    Render the first page of the shop.
    """
    return render(request, 'shop/first_page.html')

def product_details(request, product_id):
    """
    Retrieve the product object based on the product_id and render the product details page.
    """
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'shop/product_details.html', {'product': product})


def sell_item(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, 'Your product has been listed successfully!')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'shop/sell_item.html', {'form': form})




def register(request):
    """
    Handle user registration. If the request is a POST request, validate and save the form,
    authenticate the user, and log them in. If the form is invalid or the request is GET,
    render the registration form.
    """
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('product_list')
    else:
        form = UserRegisterForm()
    return render(request, 'shop/register.html', {'form': form})

def user_login(request):
    """
    Handle user login. If the request is a POST request, validate the authentication form,
    authenticate the user, and log them in. If the form is invalid or the request is GET,
    render the login form.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('product_list')
    else:
        form = AuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})

def add_to_cart(request):
    """
    Add a product to the cart. If the request is a POST request, retrieve the product_id from
    the POST data, validate it, and add the product to the cart in the session. If the cart
    doesn't exist in the session, create it. Redirect to the product list page.
    """
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        if not product_id:
            return redirect('product_list')  # Redirect if no product_id is provided

        # Check if the product_id is valid
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return redirect('product_list')  # Redirect if product does not exist

        # Implement logic to add product to the cart
        if 'cart' not in request.session:
            request.session['cart'] = {}
        
        cart = request.session['cart']
        
        if product_id in cart:
            cart[product_id] += 1
        else:
            cart[product_id] = 1

        request.session['cart'] = cart
        request.session.modified = True  # Ensure the session is marked as modified
        # Add success message
        messages.success(request, 'Product successfully added to cart. Click on My Cart to view your cart.')
    return redirect('product_list')  # Redirect to product list or any other page

def my_cart(request):
    """
    Retrieve the cart from the session, fetch the product details for each item in the cart,
    and render the cart page with the list of cart items, total quantity, and total price.
    """
    cart = request.session.get('cart', {})
    cart_items = []
    total_quantity = 0
    total_price = 0.0  # Initialize total_price as float

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(pk=product_id)
            item_total_price = product.price * quantity  # Calculate total price for each item
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total_price': item_total_price
            })
            total_quantity += quantity
            total_price += float(item_total_price)  # Add item total price to total_price
        except Product.DoesNotExist:
            continue

    return render(request, 'shop/my_cart.html', {
        'cart_items': cart_items,
        'total_quantity': total_quantity,
        'total_price': total_price
    })


def remove_from_cart(request, product_id):
    """
    Remove a product from the cart. If the request is a POST request, check if the cart exists
    in the session and if the product_id exists in the cart. If so, remove the product from the
    cart and update the session. Redirect to the cart page.
    """
    if request.method == 'POST':
        if 'cart' in request.session:
            cart = request.session['cart']
            product_id_str = str(product_id)  # Convert product_id to string
            if product_id_str in cart:
                product = Product.objects.get(pk=product_id)  # Retrieve the product object
                del cart[product_id_str]
                request.session['cart'] = cart
                request.session.modified = True  # Ensure the session is marked as modified
                messages.success(request, f'{product.name} removed from your cart.')
    return redirect('my_cart')


    
def logout_view(request):
    """
    Handle user logout. If the request is a POST request, log the user out and redirect to the login page.
    If the request is a GET request, render the logout confirmation page.
    """
    if request.method == 'POST':
        logout(request)
        response = redirect('login')  # Redirect to login page after logout
        return response
    return render(request, 'shop/logout.html')



def dashboard(request):
    """
    Display the dashboard page with products created by the logged-in user.
    """
    if request.user.is_authenticated:
        user_products = Product.objects.filter(seller=request.user)
        total_products = user_products.count()
        username = request.user.username

        return render(request, 'shop/dashboard.html', {
            'user_products': user_products,
            'total_products': total_products,
            'username': username
        })
    else:
        return redirect('login')
    
def profile_page(request):
    return render(request,'shop/profile_page.html')



def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Redirect to dashboard or any other page after saving
    else:
        form = ProductForm(instance=product)

    return render(request, 'shop/edit_product.html', {'form': form, 'product': product})

def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')  # Redirect to the product list or any other appropriate page
    return redirect('edit_product', product_id=product.id)


def profile_page(request):
    if request.method == 'POST':
        user = request.user
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()
        messages.success(request, 'Your profile was successfully updated!')
        return redirect('profile_page')
    
    return render(request, 'shop/profile_page.html')


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile_page')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'shop/change_password.html', {'form': form})