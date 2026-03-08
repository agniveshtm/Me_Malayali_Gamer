from Main.filters import ModsFilter
from Main.models import Modsinfo
class PublicModsFilter(ModsFilter):
    class Meta:
        model = Modsinfo
        fields = ['type','category','uploaded_on']

    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.filters.pop('is_public',None)
        self.form.fields.pop('is_public',None)

class CategoryPageFilter(ModsFilter):

    class Meta:
        model = Modsinfo
        fields = ['type','uploaded_on']

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.filters.pop('is_public',None)
        self.form.fields.pop('is_public',None) 
        self.filters.pop('category',None)
        self.form.fields.pop('category',None)
