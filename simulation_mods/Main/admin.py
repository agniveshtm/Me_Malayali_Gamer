from django.contrib import admin
from .models import *
# Register your models here.
class ModsinfoAdmin(admin.ModelAdmin):
    list_display=['title','version','type','category','is_public','likes','downloads']
    readonly_fields = ['downloads','likes']
admin.site.register(Modsinfo,ModsinfoAdmin)
admin.site.register(Vehicle)
admin.site.register(ModCategory)
admin.site.register(Profile)
