from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django_resized import ResizedImageField
import uuid
from .utils import image_directory_path
# Create your models here.
class Vehicle(models.Model):
    vehicle_category = models.CharField(max_length=20,verbose_name="Vehicle Category",
                                        help_text="The category of the vehicle (eg: Car, Truck, Bus).")
    def __str__(self):
        return self.vehicle_category
    
class Modtype(models.Model):
    mod_type=models.CharField(max_length=20,verbose_name="Mod Type",
                              help_text="The type of the mod(eg: Maps,Skin,Routes).")
    
    def __str__(self):
        return self.mod_type
class Modsinfo(models.Model): 
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,editable=False)
    title = models.CharField(max_length=100)
    version = models.CharField(max_length=15)
    description = models.TextField()
    uploaded_on = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey('Vehicle',on_delete=models.SET_NULL,null=True,blank=True)
    download_link = models.URLField(max_length=500,blank=True,null=True)
    is_public = models.BooleanField(default = True)
    type = models.ForeignKey('Modtype',on_delete=models.SET_NULL,null=True,blank=True)
    thumbnail_img = ResizedImageField(
        size=[1280, 720], # The desired size: [width, height]
        crop=['middle', 'center'], # Optional: ensures the image covers the area, cropping as needed
        upload_to=image_directory_path,
        verbose_name="Thumbnail_Image",
        default="img/default_placeholder.jpg",
        blank=False, null=False,
        keep_meta = False
    )
    img_1 = ResizedImageField(
        size=[1280, 720], 
        crop=['middle', 'center'],
        upload_to=image_directory_path,
        verbose_name="Image_1",
        blank=True, null=False,
        keep_meta = False
    )
    img_2 = ResizedImageField(
        size=[1280, 720],
        crop=['middle', 'center'],
        upload_to=image_directory_path,
        verbose_name="Image_2",
        blank=True, null=False,
        keep_meta = False
    )
    img_3 = ResizedImageField(
        size=[1280, 720],
        crop=['middle', 'center'],
        upload_to=image_directory_path,
        verbose_name="Image_3",
        blank=True, null=False,
        keep_meta = False
    )
    downloads= models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    def __str__(self):
        return self.title
    