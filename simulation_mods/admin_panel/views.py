from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required(login_url='/admin/login/')
def admin_dashboard(request):
    return render(request, 'admin_panel/admin-panel.html')
