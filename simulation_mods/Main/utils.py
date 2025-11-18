import os
import re
def image_directory_path(instance,filename):
    username=instance.user.username if instance.user and instance.user.username else 'unknown_user'
    category_name = instance.category.vehicle_category.lower().replace(' ','_') if instance.category and instance.category.vehicle_category else 'uncategorized'
    title_name = re.sub(r'[\s]+', '_', re.sub(r'[^\w\s-]', '', instance.title)).strip('_').lower() if instance.title else 'untitled'
    return os.path.join('images', username, category_name,title_name,filename)