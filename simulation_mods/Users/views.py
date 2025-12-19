from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .forms import ModUserCreationForm,ModAuthenticationForm
from django.contrib import messages
from django.contrib.auth import login,logout
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from django.contrib.auth.forms import SetPasswordForm
from .utils import (is_otp_expired,clear_otp_session,send_reset_otp,send_verify_email_otp,clear_verify_otp_session)
# Create your views here.
@never_cache
def user_signup(request):
    if request.method == "POST":
        frm = ModUserCreationForm(request.POST)
        if frm.is_valid():
            user = frm.save(commit=False)
            user.is_active = False
            user.save()
            request.session['verify_email']=user.email
            success = send_verify_email_otp(request)
            if success:
                return redirect('email_verification')
            else:
                messages.error(request, "Failed to send verification OTP. Please try again.")
                return redirect('user_signup')
    else:
        frm = ModUserCreationForm()
    return render(request,"users/signup.html",{"frm":frm})

def email_verification(request):
    email = request.session.get('verify_email')
    otp_created_at = request.session.get('verify_otp_created_at')
    if not email or not otp_created_at:
        messages.error(request, "Session expired. Please sign up again.")
        return redirect('user_signup')
    if is_otp_expired(otp_created_at):
        clear_verify_otp_session(request)
        messages.error(request, "OTP has expired. Please sign up again.")
        return redirect('user_signup')
    if request.method == "POST":
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('verify_otp')
        if entered_otp == stored_otp:
            try:
                user = User.objects.get(email=email)
                user.is_active = True
                user.save()
                clear_verify_otp_session(request)
                messages.success(request, 'Your email has been verified successfully! You can now login.')
                return redirect('user_login')
            except User.DoesNotExist:
                messages.error(request, "User not found.")
                return redirect('user_signup')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect('email_verification')
    return render(request,"users/otp.html",{'email':email,'is_verification': True,'resend_url': 'resend_verification_otp'})

@never_cache
def user_login(request):
    if request.method == "POST":
        frm = ModAuthenticationForm(request,request.POST)
        if frm.is_valid():
            user = frm.get_user()
            login(request,user)
            return redirect('create')
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
    return render(request,'users/otp.html',{'email':email, 'resend_url': 'resend_otp'})

@require_POST
def resend_otp(request):
    success = send_reset_otp(request)
    if success:
        messages.success(request, 'OTP resent successfully.')
    else:
        messages.error(request, 'Failed to resend OTP. Please try again.')
    return redirect('otp_verify')

@require_POST
def resend_verification_otp(request):
    success = send_verify_email_otp(request)
    if success:
        messages.success(request, 'Verification OTP resent successfully.')
    else:
        messages.error(request, 'Failed to resend OTP. Please try again.')
    return redirect('email_verification')

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
