from django import forms
from api.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm


PASSWORD_ERROR_MESSAGES = {
    "This password is too short. It must contain at least 8 characters.": "رمز عبور خیلی کوتاه است. حداقل باید ۸ کاراکتر باشد.",
    "This password is too common.": "این رمز عبور خیلی ساده و رایج است.",
    "This password is entirely numeric.": "رمز عبور نباید فقط شامل عدد باشد.",
    "The password is too similar to the username.": "رمز عبور بیش از حد شبیه نام کاربری است.",
    "The password is too similar to the first name.": "رمز عبور بیش از حد شبیه نام کوچک است.",
    "The password is too similar to the last name.": "رمز عبور بیش از حد شبیه نام خانوادگی است.",
    "The password is too similar to the phone.": "رمز عبور بیش از حد شبیه شماره تلفن است.",
}


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput,
        help_text="رمز عبور باید حداقل ۸ کاراکتر باشد و نمی‌تواند بیش از حد ساده باشد."
    )

    class Meta:
        model = User
        fields = ('phone', 'first_name', 'last_name', 'password')

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password:
            try:
                temp_user = User(
                    **{User.USERNAME_FIELD: self.cleaned_data.get(User.USERNAME_FIELD)},
                    first_name=self.cleaned_data.get('first_name'),
                    last_name=self.cleaned_data.get('last_name'),
                )
                validate_password(password, user=temp_user)
            except ValidationError as e:
                translated = [PASSWORD_ERROR_MESSAGES.get(msg, msg) for msg in e.messages]
                raise ValidationError(translated)
        return password

    def save(self, commit=True):
        user = User.objects.create_user(
            phone=self.cleaned_data['phone'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        return user


class UserLoginForm(AuthenticationForm):
    """
    Custom login form to use 'phone' as the username field.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Change the label and widget for the 'username' field
        self.fields['username'].label = "شماره تلفن"
        self.fields['username'].widget = forms.TextInput(attrs={
            'class': 'form-control', # You can add classes for styling
            'placeholder': '09123456789',
            'autofocus': True
        })

        # Change the label and widget for the 'password' field
        self.fields['password'].label = "رمز عبور"
        self.fields['password'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••'
        })

