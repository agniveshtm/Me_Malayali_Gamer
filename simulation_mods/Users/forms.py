from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django import forms
from django.contrib.auth.models import User

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

class ModAuthenticationForm(AuthenticationForm):
    pass