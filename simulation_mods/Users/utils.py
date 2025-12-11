from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import random
from datetime import datetime,timedelta

def generate_otp():
    return str(random.randint(100000,999999))

def send_otp_email(email,otp):
    try:
        html_message = render_to_string('emails/otp_email.html',{'otp':otp})
        plain_message = strip_tags(html_message)
        send_mail(
            subject='Password Reset OTP - ModHub',
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

def clear_otp_session(request):
    request.session.pop('reset_email',None)
    request.session.pop('reset_otp',None)
    request.session.pop('otp_created_at',None)