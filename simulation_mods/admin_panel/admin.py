from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'mobile_number', 'submitted_at', 'is_read')
    list_filter = ('is_read', 'submitted_at')
    search_fields = ('name', 'subject', 'mobile_number', 'message')
    readonly_fields = ('submitted_at',)
    ordering = ('-submitted_at',)
