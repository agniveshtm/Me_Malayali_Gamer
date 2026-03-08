import os
import re
def image_directory_path(instance,filename):
    username=instance.user.username if instance.user and instance.user.username else 'unknown_user'
    type_name = instance.type.vehicle_type.lower().replace(' ','_') if instance.type and instance.type.vehicle_type else 'uncategorized'
    title_name = re.sub(r'[\s]+', '_', re.sub(r'[^\w\s-]', '', instance.title)).strip('_').lower() if instance.title else 'untitled'
    return os.path.join('images', username, type_name,title_name,filename)