# shoppingapp/views.py
# shoppingapp/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from shoppingapp.forms import SignUpForm, LoginForm
from shoppingapp.models import CartItem, Order
import json


# Navigation views
def basic(request):
    return render(request, 'basic.html')

def cloth(request):
    return render(request, 'project.html')

def login_view(request):
    return render(request, 'login.html')


# from django.shortcuts import render, redirect
# from django.contrib.auth import login
# from django.contrib.auth.views import LoginView
# from django.contrib.auth.decorators import login_required
# from django.http import JsonResponse
# from .forms import SignUpForm, LoginForm
# from .models import CartItem, Order
# import json

def signup(request):
    form = SignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect("login")
    return render(request, "signup.html", {"form": form})

class CustomLoginView(LoginView):
    template_name = "login.html"
    authentication_form = LoginForm

@login_required
def save_cart(request):
    data = json.loads(request.body)
    CartItem.objects.filter(user=request.user).delete()
    for item in data.get("cart", []):
        CartItem.objects.create(user=request.user, name=item["name"], price=int(item["price"]))
    return JsonResponse({"status": "saved"})

@login_required
def load_cart(request):
    items = CartItem.objects.filter(user=request.user)
    return JsonResponse({
        "cart": [{"name": item.name, "price": item.price} for item in items]
    })

@login_required
def place_order(request):
    data = json.loads(request.body)
    for item in data.get("cart", []):
        Order.objects.create(user=request.user, item=item["name"], price=int(item["price"]))
    CartItem.objects.filter(user=request.user).delete()
    return JsonResponse({"status": "order placed"})
