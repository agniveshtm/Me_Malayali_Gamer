from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .forms import ModUserCreationForm,ModAuthenticationForm
from django.contrib import messages
from django.contrib.auth import login,logout
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from django.contrib.auth.forms import SetPasswordForm
from django.http import JsonResponse
from .utils import generate_otp,send_otp_email,is_otp_expired,clear_otp_session,send_reset_otp
from datetime import datetime
# Create your views here.
@never_cache
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

def email_verification(request):
    pass

@never_cache
def user_login(request):
    if request.method == "POST":
        frm = ModAuthenticationForm(request,request.POST)
        if frm.is_valid():
            user = frm.get_user()
            login(request,user)
            return redirect('create')
        else:
            messages.error(request,"Invalid username/email or password")
    else:
        frm = ModAuthenticationForm(request)
    return render(request,'users/login.html',{"frm":frm})

@require_POST
def user_logout(request):
    logout(request)
    return redirect('home_page')

@never_cache
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email","")
        if User.objects.filter(email=email).exists():
            request.session['reset_email'] = email
            success = send_reset_otp(request)
            if success:
                return redirect('otp_verify')
            else:
                messages.error(request,"Failed to send OTP. Please try again.")
                return redirect('forgot_password')
        else:
            messages.error(request,"No account found with this email address. Please check and try again.")
            return redirect("forgot_password")
    return render(request,'users/password_reset.html')

@never_cache
def otp_verify(request):
    email = request.session.get('reset_email')
    otp_created_at=request.session.get('otp_created_at')
    if not email or not otp_created_at:
        messages.error(request,"Session expired. Please start the password reset process again.")
        return redirect('forgot_password')
    if is_otp_expired(otp_created_at):
        clear_otp_session(request)
        messages.error(request,"OTP has expired. Please request a new one.")
        return redirect('forgot_password')
    if request.method == "POST":
        entered_otp=request.POST.get('otp')
        stored_otp=request.session.get('reset_otp')
        if entered_otp==stored_otp:
            messages.success(request,"OTP verified successfully!")
            return redirect('reset_password')
        else:
            messages.error(request,"Invalid OTP. Please try again.")
            return redirect('otp_verify')
    return render(request,'users/otp.html',{'email':email})

@require_POST
def resend_otp(request):
    success = send_reset_otp(request)
    if success:
        messages.success(request, 'OTP resent successfully.')
    else:
        messages.error(request, 'Failed to resend OTP. Please try again.')
    return redirect('otp_verify')

def reset_password(request):
    email = request.session.get('reset_email')
    if not email:
        messages.error(request,"Session expired. Please start the password reset process again.")
        return redirect('forgot_password')
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request,"User not found.")
        return redirect('forgot_password')
    if request.method == "POST":
        frm = SetPasswordForm(user,request.POST)
        if frm.is_valid():
            frm.save()
            clear_otp_session(request)
            messages.success(request,"Password reset successfully! Please log in with your new password.")
            return redirect('user_login')
    else:
        frm = SetPasswordForm(user)
    return render(request,'users/reset_password.html',{'frm':frm,'email':email})