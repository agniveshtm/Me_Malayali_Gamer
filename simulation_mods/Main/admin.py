from django.contrib import admin
from .models import Modsinfo,Vehicle,Modtype
# Register your models here.
class ModsinfoAdmin(admin.ModelAdmin):
    readonly_fields = ['downloads','likes']
admin.site.register(Modsinfo,ModsinfoAdmin)
admin.site.register(Vehicle)
admin.site.register(Modtype)
