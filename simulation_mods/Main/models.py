from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .utils import image_directory_path,profile_image_directory_path
# Create your models here.
class Vehicle(models.Model):
    vehicle_type = models.CharField(max_length=20,verbose_name="Vehicle Type",
                                        help_text="The Type of the vehicle (eg: Car, Truck, Bus).",default='')
    def __str__(self):
        return self.vehicle_type
    
class ModCategory(models.Model):
    mod_category=models.CharField(max_length=20,verbose_name="Mod Category",
                              help_text="The Category of the mod(eg: Maps,Skin,Routes).",default='')
    
    def __str__(self):
        return self.mod_category
class Modsinfo(models.Model): 
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,editable=False)
    title = models.CharField(max_length=100)
    version = models.CharField(max_length=15)
    description = models.TextField()
    uploaded_on = models.DateTimeField(default=timezone.now)
    type = models.ForeignKey('Vehicle',on_delete=models.SET_NULL,null=True,blank=True)
    download_link = models.URLField(max_length=500,blank=True,null=True)
    is_public = models.BooleanField(default = True)
    category = models.ForeignKey('ModCategory',on_delete=models.SET_NULL,null=True,blank=True)
    thumbnail_img = models.ImageField(
        upload_to=image_directory_path,
        verbose_name="Thumbnail_Image",
        default="img/default_placeholder.jpg",
    )
    img_1 = models.ImageField(
        upload_to=image_directory_path,
        verbose_name="Image_1",
        blank=True, null=False,
    )
    img_2 = models.ImageField(
        upload_to=image_directory_path,
        verbose_name="Image_2",
        blank=True, null=False,
    )
    img_3 = models.ImageField(
        upload_to=image_directory_path,
        verbose_name="Image_3",
        blank=True, null=False,
    )
    downloads= models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to=profile_image_directory_path,
                                      blank=True,null=True)
    
    def __str__(self):
        return f'{self.user.username} Profile'
    
@receiver(post_save, sender=User)
def create_or_save_profile(sender, instance, created, **kwargs):
    Profile.objects.get_or_create(user=instance)


@receiver(post_delete, sender=Modsinfo)
def delete_mod_images(sender, instance, **kwargs):
    default_thumb = sender._meta.get_field('thumbnail_img').get_default()
    for field in instance._meta.fields:
        if isinstance(field, models.ImageField):
            img_file = getattr(instance, field.name)
            if img_file and img_file.name != default_thumb:
                img_file.delete(save=False)

@receiver(post_delete, sender=Profile)
def delete_profile_image(sender, instance, **kwargs):
    if instance.profile_image:
        instance.profile_image.delete(save=False)
