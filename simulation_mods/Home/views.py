from django.shortcuts import render,get_object_or_404,redirect
from Main.models import Modsinfo
from .filters import PublicModsFilter
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.conf import settings
from googleapiclient.discovery import build
#=============HOME PAGE===============#
def youtube_video(request):
    try:
        youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
        
        # Get uploads playlist ID
        channel_response = youtube.channels().list(
            part='contentDetails',
            id=settings.YOUTUBE_CHANNEL_ID
        ).execute()
        
        if not channel_response.get('items'):
            return {'latest_video': None, 'trending_video': None}
        
        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # Get recent videos from playlist
        videos_response = youtube.playlistItems().list(
            part='snippet',
            playlistId=uploads_playlist_id,
            maxResults=15  # Increased to get more videos
        ).execute()
        
        if not videos_response.get('items'):
            return {'latest_video': None, 'trending_video': None}
        
        # Find first regular video (not live, not shorts)
        latest_video = _get_first_regular_video(youtube, videos_response['items'])
        
        return {
            'latest_video': latest_video,
            'trending_video': None
        }
    
    except Exception as e:
        print(f"YouTube API Error: {e}")
        return {'latest_video': None, 'trending_video': None}


def _get_first_regular_video(youtube, video_items):
    """Extract first non-live, non-shorts video from playlist items."""
    for item in video_items:
        video_id = item['snippet']['resourceId']['videoId']
        video_title = item['snippet']['title']
        
        stats_response = youtube.videos().list(
            part='statistics,snippet,liveStreamingDetails,contentDetails',
            id=video_id
        ).execute()
        
        if not stats_response.get('items'):
            continue
        
        video = stats_response['items'][0]
        
        # Skip live streams
        if 'liveStreamingDetails' in video:
            print(f"Skipping LIVE: {video_title}")
            continue
        
        # Get duration info for debugging
        duration_str = video.get('contentDetails', {}).get('duration', '')
        duration_seconds = _parse_duration(duration_str)
        
        print(f"Video: {video_title}")
        print(f"  Duration: {duration_str} ({duration_seconds} seconds)")
        
        # Skip YouTube Shorts (duration <= 90 seconds to be safe)
        if duration_seconds <= 90:
            print(f"  -> Skipping SHORT (≤90s)")
            continue
        
        print(f"  -> Selected as regular video!")
        return video
    
    print("No regular videos found in the fetched items")
    return None


def _parse_duration(duration_str):
    """Parse ISO 8601 duration and return total seconds."""
    if not duration_str:
        return 0
    
    import re
    
    # Extract hours, minutes, seconds
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    
    if not match:
        return 0
    
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    
    total_seconds = hours * 3600 + minutes * 60 + seconds
    
    return total_seconds


def _is_short_video(video):
    """Check if video is a YouTube Short based on duration."""
    duration_str = video.get('contentDetails', {}).get('duration', '')
    duration_seconds = _parse_duration(duration_str)
    
    # YouTube Shorts can be up to 90 seconds (increased from 60)
    return duration_seconds <= 90
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
    
