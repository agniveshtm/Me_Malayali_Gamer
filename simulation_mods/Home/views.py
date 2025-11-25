from django.shortcuts import render,get_object_or_404,redirect
from Main.models import Modsinfo
from .filters import PublicModsFilter
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.conf import settings
from googleapiclient.discovery import build
#=============HOME PAGE===============#
#============= DISPLAY HOME PAGE ===============#
def home_page(request):
    order = request.GET.get('order', '-uploaded_on')
    mod_set = Modsinfo.objects.filter(is_public = True).order_by(order)
    mods_filter = PublicModsFilter(request.GET,queryset=mod_set)
    filtered_mods = mods_filter.qs
    paginator = Paginator(filtered_mods,5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    youtube_data = youtube_video(request)
    return render(request,'main/index.html',{"public_mods":page_obj,"filter":mods_filter,"page_obj":page_obj,"current_order":order,
                                             "latest_video":youtube_data['latest_video'],"trending_video":youtube_data['trending_video']})
def download_count(request,pk):
    mod = get_object_or_404(Modsinfo,pk=pk)
    session_key = f'downloaded_mod_{pk}'
    if not request.session.get(session_key,False):
        mod.downloads +=1
        mod.save()
        request.session[session_key]=True
        request.session.modified = True
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
    request.session.modified = True
    return JsonResponse({'success':True,'likes':mod.likes,'liked':liked})
    
def youtube_video(request):
    try:
        youtube = build('youtube','v3',developerKey = settings.YOUTUBE_API_KEY)
        channel_response = youtube.channels().list(part = 'contentDetails',id = settings.YOUTUBE_CHANNEL_ID).execute()
        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        videos_response = youtube.playlistItems().list(
            part = 'snippet',
            playlistId = uploads_playlist_id,
            maxResults = 1
        ).execute()

        if videos_response['items']:
            video_id = videos_response['items'][0]['snippet']['resourceId']['videoId']
            stats_response = youtube.videos().list(
                part='statistics,snippet',
                id=video_id
            ).execute()
                
            latest_video = stats_response['items'][0] if stats_response['items'] else None
                
            return {
                    'latest_video': latest_video,
                    'trending_video': None   
            }
            
        return {'latest_video': None, 'trending_video': None}
    
    except Exception as e:
        print(f"Youtube API Error:: {e}")
        return {'latest_video':None,'trending_video':None}