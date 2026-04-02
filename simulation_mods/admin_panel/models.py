from django.db import models


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=300)
    mobile_number = models.CharField(max_length=20)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.name} – {self.subject}"
