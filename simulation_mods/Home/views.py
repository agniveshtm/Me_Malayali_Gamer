from django.shortcuts import render,get_object_or_404,redirect
from Main.models import Modsinfo
from django.http import JsonResponse
from django.views.decorators.http import require_POST
#=============HOME PAGE===============#
#============= DISPLAY HOME PAGE ===============#
def home_page(request):
    mod_set = Modsinfo.objects.filter(is_public = True).order_by('-uploaded_on')
    return render(request,'main/index.html',{'public_mods':mod_set})

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
    