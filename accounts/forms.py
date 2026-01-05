from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm,PasswordResetForm
from django.contrib.auth.models import User

class loginform(AuthenticationForm):

    remember_me = forms.BooleanField(required=False, initial=False, label="Remember Me")

    ## to apply custom css to input fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""  # removes the colon globally 'remember me:' is now 'remember me'

        ##custom css for username
        self.fields['username'].widget.attrs.update({
            'class' : 'username-input',
            'placeholder' : 'Username'
        })

        ##custom css for password
        self.fields['password'].widget.attrs.update({
            'class' : 'password-input',
            'placeholder' : 'Password'
        })

        # Custom CSS for remember_me
        self.fields['remember_me'].widget.attrs.update({
            'class': 'remember-me-checkbox'
        })

class signupform(UserCreationForm):

    ## to apply custom css to input fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ##custom css for username
        self.fields['username'].widget.attrs.update({
            'class' : 'username-input',
            'placeholder' : 'Username'
        })

        ##custom css for email
        self.fields['email'].widget.attrs.update({
            'class' : 'email-input',
            'placeholder' : 'Email'
        })

        ##custom css for password
        self.fields['password1'].widget.attrs.update({
            'class' : 'password-input',
            'placeholder' : 'Password'
        })

        ##custom css for password (confirmation)
        self.fields['password2'].widget.attrs.update({
            'class' : 'confirm-password-input',
            'placeholder' : 'Password'
        })

    # ## the metadata for the class
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


############ forgot form #####################

# accounts/forms.py
from django.contrib.auth.forms import PasswordResetForm

class forgotPassword(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email'].widget.attrs.update({
            'class': 'email-input', 
            'placeholder': 'Enter your email'
        })


