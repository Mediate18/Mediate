from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django_registration.forms import RegistrationForm
from django.core.exceptions import ValidationError


User = get_user_model()


class CustomRegistrationForm(RegistrationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        fields = [
            "first_name",
            "last_name",
            User.USERNAME_FIELD,
            User.get_email_field_name(),
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'autofocus': True})
        self.fields[User.USERNAME_FIELD].widget.attrs.pop('autofocus')

    def clean(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            self.add_error('email', ValidationError("The email address already exists"))
        return self.cleaned_data
