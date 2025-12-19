from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import random
from datetime import datetime,timedelta

def generate_otp():
    return str(random.randint(100000,999999))

def send_otp_email(email,otp,is_verification=False):
    try:
        html_message = render_to_string('emails/otp_email.html',{'otp':otp,'is_verification':is_verification})
        plain_message = strip_tags(html_message)
        subject= 'Email Verification OTP - ModHub' if is_verification else 'Password Reset OTP - ModHub'
        send_mail(
            subject=subject,
            message = plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        return True, None
    except Exception as e:
        return False, str(e)

def is_otp_expired(otp_created_at,expiry_minutes=10):
    if not otp_created_at:
        return True
    otp_time = datetime.fromisoformat(otp_created_at)
    return datetime.now() - otp_time > timedelta(minutes=expiry_minutes)

def send_verify_email_otp(request):
    email = request.session.get('verify_email')
    if not email:
        return False
    otp = generate_otp()
    request.session['verify_otp']=otp
    request.session['verify_otp_created_at']=datetime.now().isoformat()
    success, _ = send_otp_email(email, otp, is_verification=True)
    return success

def send_reset_otp(request):
    email = request.session.get('reset_email')
    if not email:
        return False
    otp = generate_otp()
    request.session['reset_otp'] = otp
    request.session['otp_created_at'] = datetime.now().isoformat()
    success, _ = send_otp_email(email, otp,is_verification=False)
    return success

def clear_otp_session(request):
    request.session.pop('reset_email',None)
    request.session.pop('reset_otp',None)
    request.session.pop('otp_created_at',None)

def clear_verify_otp_session(request):
    request.session.pop('verify_email', None)
    request.session.pop('verify_otp', None)
    request.session.pop('verify_otp_created_at', None)