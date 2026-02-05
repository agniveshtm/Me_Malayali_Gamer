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
        html_message = render_to_string('messages/otp_email.html',{'otp':otp,'is_verification':is_verification})
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
    try:
        otp_time = datetime.fromisoformat(otp_created_at)
        return datetime.now() - otp_time > timedelta(minutes=expiry_minutes)
    except (ValueError,TypeError):
        return True
    
def can_resend_otp(request, timestamp_key, min_interval_seconds=60):
    last_sent = request.session.get(timestamp_key)
    if not last_sent:
        return True
    
    try:
        last_sent_time = datetime.fromisoformat(last_sent)
        time_since = datetime.now() - last_sent_time
        return time_since.total_seconds() >= min_interval_seconds
    except (ValueError, TypeError):
        return True
    
def send_verify_email_otp(request):
    email = request.session.get('verify_email')
    if not email:
        return False
    otp = generate_otp()
    request.session['verify_otp']=otp
    request.session['verify_otp_created_at']=datetime.now().isoformat()
    request.session.modified=True
    success, error = send_otp_email(email, otp, is_verification=True)
    return success

def send_reset_otp(request):
    email = request.session.get('reset_email')
    if not email:
        return False
    otp = generate_otp()
    request.session['reset_otp'] = otp
    request.session['otp_created_at'] = datetime.now().isoformat()
    request.session.modified=True
    success, error = send_otp_email(email, otp,is_verification=False)
    return success

def clear_otp_session(request):
    keys_to_remove = ['reset_email', 'reset_otp', 'otp_created_at', 'otp_verified']
    for key in keys_to_remove:
        request.session.pop(key, None)
    request.session.modified = True

def clear_verify_otp_session(request):
    keys_to_remove = ['verify_email', 'verify_otp', 'verify_otp_created_at', 'verify_user_id']
    for key in keys_to_remove:
        request.session.pop(key, None)
    request.session.modified = True