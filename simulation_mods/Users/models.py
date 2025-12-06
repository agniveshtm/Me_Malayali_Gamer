from django.db import models
from django.utils import timezone
from datetime import timedelta
class OTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    attempts = models.IntegerField(default=0)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        if self.is_used:
            return False
        if self.attempts >= 3:
            return False
        return timezone.now() < self.created_at + timedelta(minutes=20)
    
    def __str__(self):
        return f"OTP for {self.email}"