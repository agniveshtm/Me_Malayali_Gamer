from Main.filters import ModsFilter
from Main.models import Modsinfo
class PublicModsFilter(ModsFilter):
    class Meta:
        model = Modsinfo
        fields = ['category','type','uploaded_on']

    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.filters.pop('is_public',None)
        self.form.fields.pop('is_public',None)
