from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    mobile = models.CharField(max_length=15, unique=True)

    def _str_(self):
        return self.username

class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)
    image = models.URLField(blank=True)

    def _str_(self):
        return f"{self.name} x{self.quantity}"

class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    item = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    ordered_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.item} x{self.quantity}".....................................forms.pyfrom django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class SignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'mobile', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    pass..............views.py # shoppingapp/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from shoppingapp.forms import SignUpForm, LoginForm
from shoppingapp.models import CustomUser, CartItem, Order
import json
def basic(request):
    return render(request, 'basic.html')

def cloth(request):
    return render(request, 'project.html')

def login_view(request):
    return render(request, 'login.html')


def signup(request):
    form = SignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Account created successfully! Please log in.')
        return redirect('login')
    return render(request, 'signup.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = LoginForm

    def form_invalid(self, form):
        print('Form errors:', form.errors)  # Debug form errors
        print('Submitted data:', self.request.POST)  # Debug submitted data
        return super().form_invalid(form)

# Cart Operations
@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        item.total = item.price * item.quantity  # Dynamic total
    total_price = sum(item.total for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def add_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        price = data.get('price')
        quantity = int(data.get('quantity', 1))
        
        if not name or not price:
            return JsonResponse({'success': False, 'message': 'Invalid item details'}, status=400)
        
        try:
            price = float(price)
            if price <= 0 or quantity <= 0:
                raise ValueError
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid price or quantity'}, status=400)
        
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            name=name,
            defaults={'price': price, 'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return JsonResponse({'success': True, 'message': 'Item added to cart'})
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

@login_required
def delete_item(request, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id, user=request.user)
        cart_item.delete()
        return JsonResponse({'success': True, 'message': 'Item removed'})
    except ObjectDoesNotExist:
        return JsonResponse({'success': False, 'message': 'Item not found'}, status=404)

@login_required
def delete_all_items(request):
    CartItem.objects.filter(user=request.user).delete()
    return JsonResponse({'success': True, 'message': 'All items removed'})

@login_required
def checkout(request):
    CartItem.objects.filter(user=request.user).delete()
    messages.success(request, 'Checkout successful! Your order has been placed.')
    return redirect('cart')

@login_required
def save_cart(request):
    data = json.loads(request.body)
    CartItem.objects.filter(user=request.user).delete()
    for item in data.get('cart', []):
        CartItem.objects.create(
            user=request.user,
            name=item['name'],
            price=int(item['price']),
            quantity=int(item.get('quantity', 1))
        )
    return JsonResponse({'status': 'saved'})

@login_required
def load_cart(request):
    items = CartItem.objects.filter(user=request.user)
    return JsonResponse({
        'cart': [
            {
                'name': item.name,
                'price': item.price,
                'quantity': item.quantity
            }
            for item in items
        ]
    })

@login_required
def place_order(request):
    data = json.loads(request.body)
    for item in data.get('cart', []):
        Order.objects.create(
            user=request.user,
            item=item['name'],
            price=int(item['price']),
            quantity=int(item.get('quantity', 1))
        )
    CartItem.objects.filter(user=request.user).delete()
    return JsonResponse({'status': 'order placed'})

# @login_required
# def delete_account(request):
#     if request.method == 'POST':
#         user = request.user
#         user.delete()  # Deletes user and associated CartItem/Order due to CASCADE
#         logout(request)  # Logs out the user after deletion
#         messages.success(request, 'Your account has been deleted successfully.')
#         return redirect('login')
#     return render(request, 'del.html', {'user': request.user})
