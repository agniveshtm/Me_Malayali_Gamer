from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
def mod_user_required(view_func):
    @wraps(view_func)
    @login_required(login_url='Users:user_login')
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
           return redirect('admin_panel:admin_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper