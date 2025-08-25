from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from .forms import SignUpForm
from orders.models import Order

class UserLoginView(LoginView):
    template_name = "registration/login.html"

class UserLogoutView(LogoutView):
    pass

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            user.refresh_from_db()
            login(request, user)
            return redirect("accounts:profile")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")[:20]
    return render(request, "accounts/profile.html", {"orders": orders})
