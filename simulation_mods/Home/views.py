from django.shortcuts import render,get_object_or_404,redirect
from Main.models import Modsinfo
from .filters import PublicModsFilter
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
#=============HOME PAGE===============#
#============= DISPLAY HOME PAGE ===============#
def home_page(request):
    mod_set = Modsinfo.objects.filter(is_public = True).order_by('-uploaded_on')
    mods_filter = PublicModsFilter(request.GET,queryset=mod_set)
    filtered_mods = mods_filter.qs
    paginator = Paginator(filtered_mods,5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request,'main/index.html',{"public_mods":page_obj,"filter":mods_filter,"page_obj":page_obj})

def download_count(request,pk):
    mod = get_object_or_404(Modsinfo,pk=pk)
    session_key = f'downloaded_mod_{pk}'
    if not request.session.get(session_key,False):
        mod.downloads +=1
        mod.save()
        request.session[session_key]=True
    return redirect(mod.download_link)

@require_POST
def like_count(request,pk):
    mod = get_object_or_404(Modsinfo,pk=pk)
    session_key = f'liked_mod_{pk}'
    already_liked = request.session.get(session_key,False)
    if already_liked:
        mod.likes = max(0,mod.likes-1)
        mod.save()
        request.session[session_key]=False
        liked = False
    else:
        mod.likes += 1
        mod.save()
        request.session[session_key]=True
        liked = True

    return JsonResponse({'success':True,'likes':mod.likes,'liked':liked})
    