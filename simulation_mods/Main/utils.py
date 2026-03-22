import os, re, base64
from django.core.files.base import ContentFile
def apply_cropped_image(post_data,files_data):
    crop_map = {
        'cropped_thumbnail_img':'thumbnail_img',
        'cropped_img_1':'img_1',
        'cropped_img_2':'img_2',
        'cropped_img_3':'img_3',
    }
    for cropped_key,original_key in crop_map.items():
        cropped_b64 = post_data.get(cropped_key,'')
        if cropped_b64:
            try:
                header,imgstr = cropped_b64.split(';base64,')
                ext = header.split('/')[-1]
                decoded = base64.b64decode(imgstr)
                files_data[original_key] = ContentFile(decoded,name=f'{original_key}.{ext}')
            except Exception:
                pass
    return files_data

def apply_cropped_profile_image(post_data, files_data):
    cropped_b64 = post_data.get('cropped_profile_image', '')
    if cropped_b64:
        try:
            header, imgstr = cropped_b64.split(';base64,')
            ext = header.split('/')[-1]
            decoded = base64.b64decode(imgstr)
            files_data['profile_image'] = ContentFile(decoded, name=f'profile_image.{ext}')
        except Exception:
            pass
    return files_data

def image_directory_path(instance,filename):
    username=instance.user.username if instance.user and instance.user.username else 'unknown_user'
    type_name = instance.type.vehicle_type.lower().replace(' ','_') if instance.type and instance.type.vehicle_type else 'uncategorized'
    title_name = re.sub(r'[\s]+', '_', re.sub(r'[^\w\s-]', '', instance.title)).strip('_').lower() if instance.title else 'untitled'
    return os.path.join('images', username, type_name,title_name,filename)

def profile_image_directory_path(instance,filename):
    username = instance.user.username if instance.user and instance.user.username else 'unknown_user'
    return os.path.join('images', username, 'profile_image', filename)