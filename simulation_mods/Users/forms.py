from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django import forms
from django.contrib.auth.models import User
from Main.models import Profile
from django.contrib.auth import authenticate

class ModUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True,help_text="Required. Enter a valid email address.")

    class Meta:
        model = User
        fields = ('email','username','password1','password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Account with this email already exists, Please use another email")
        return email

class UserAdminChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User

class UserAdminForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_image']

class ModAuthenticationForm(AuthenticationForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['username'].label="Username or Email"
        self.fields['username'].help_text="Enter your username or email address"

    def clean(self):
        username=self.cleaned_data.get('username')
        password=self.cleaned_data.get('password')
        if username is not None and password:
            self.user_cache= authenticate(self.request,username=username,password=password)
            if self.user_cache is None:
                try:
                    user = User.objects.get(email__iexact=username)
                    self.user_cache = authenticate(self.request,username=user.username,password=password)
                except User.DoesNotExist:
                    pass
            
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data
