from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from services.queries import get_first_instance, create_user

User = get_user_model()


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    email_exists_error = {
        'email_exists': _('email already exists')
    }

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if get_first_instance(model=User, email=email) is not None:
            raise ValidationError(
                self.email_exists_error['email_exists'],
                code='email_exists'
            )
        return email

    def save(self, commit=True):
        username, email, password = self.cleaned_data.get('username'), self.cleaned_data.get(
            'email'), self.cleaned_data.get('password1')
        user = create_user(password=password, username=username, email=email)
        return user
