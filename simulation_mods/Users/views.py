from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .forms import ModUserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.http import require_POST
# Create your views here.
def user_signup(request):
    if request.method == "POST":
        frm = ModUserCreationForm(request.POST)
        if frm.is_valid():
            frm.save()
            messages.success(request,"You have Successfully Registered!! Please Log In")
            return redirect('user_login')
        else:
            pass
    else:
        frm = ModUserCreationForm()
    return render(request,"users/signup.html",{"frm":frm})

def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username,password=password)
        if user is None:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(username=user_obj.username,password=password)
            except User.DoesNotExist:
                pass
        if user is not None:
            login(request,user)
            return redirect('create')
        else:
            messages.error(request,"Invalid username/email or password")
            return redirect('user_login')
    return render(request,'users/login.html')

@require_POST
def user_logout(request):
    logout(request)
    return redirect('home_page')

def forgot_password(request):
    pass