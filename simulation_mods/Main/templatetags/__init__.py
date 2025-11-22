from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
def is_recent(value):
    """
    Returns True if value (a datetime) is within the last 1 day from now.
    """
    if not value:
        return False
    now = timezone.now()
    difference = now - value
    return difference <= timedelta(days=1)
