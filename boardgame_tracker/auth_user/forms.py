from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

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

        if User.objects.filter(email=email).first():
            raise ValidationError(
                self.email_exists_error['email_exists'],
                code='email_exists'
            )
        return email

    def save(self, commit=True):
        username, email, password = self.cleaned_data.get('username'), self.cleaned_data.get(
            'email'), self.cleaned_data.get('password1')
        user = User(username=username, email=email)
        user.set_password(password)
        user.save()
        return user
