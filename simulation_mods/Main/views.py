from django.shortcuts import render,redirect,get_object_or_404
from .forms import modform
from .models import Modsinfo
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from .filters import ModsFilter
import os
# Create your views here.
#=============DASHBOARD===============#

#============= CREATE ================
@login_required(login_url="user_login")
def create_mods(request):
    if request.method == "POST":
        frm = modform(request.POST,request.FILES)
        if frm.is_valid():
            frm.instance.user = request.user
            frm.save()
            messages.success(request,"Mod Added Successfully")
            return redirect('dashboard_page')
    else:
        frm = modform()
    return render(request,"main/create_edit.html",{"frm":frm})
  
#============ DASHBOARD ===============
@never_cache
@login_required(login_url="user_login")
def dashboard_page(request):
    order = request.GET.get('order', '-uploaded_on')
    mods = Modsinfo.objects.filter(user=request.user).order_by(order)
    count = mods.count()
    mods_filter = ModsFilter(request.GET,queryset=mods)
    filtered_mods = mods_filter.qs
    filtered_count = filtered_mods.count()
    has_filters = bool(request.GET and any(request.GET.values()))
    context = {"mods":filtered_mods,"filter":mods_filter,"count":count,"filtered_count":filtered_count,"has_filters":has_filters,"current_order":order}
    return render(request,"main/dashboard.html",context)

#=============== EDIT =================
@login_required(login_url="user_login")
def edit_mods(request,pk):
    edited_mods = get_object_or_404(Modsinfo,pk=pk,user=request.user)
    is_edit = True
    if request.method == "POST":
        frm = modform(request.POST,request.FILES,instance=edited_mods)
        if frm.is_valid():
            frm.save()
            return redirect("dashboard_page")
    else:
        frm = modform(instance=edited_mods)
    return render(request,"main/create_edit.html",{"frm": frm,"mod": edited_mods,"is_edit":is_edit })

#=============== DELETE =================
@require_POST
@login_required(login_url="user_login")
def delete_mods(request,pk):
    deleted_mods = get_object_or_404(Modsinfo,pk=pk,user=request.user)
    mod_title = deleted_mods.title
    title_folder = os.path.dirname(deleted_mods.thumbnail_img.path)
    for field in ["thumbnail_img","img_1","img_2","img_3"]:
        img = getattr(deleted_mods,field)
        if img and os.path.exists(img.path):
            os.remove(img.path)
    try:
        os.rmdir(title_folder)
    except OSError:
        pass
    deleted_mods.delete()
    messages.success(request, f"'{mod_title}' has been deleted successfully!")
    return redirect("dashboard_page")
