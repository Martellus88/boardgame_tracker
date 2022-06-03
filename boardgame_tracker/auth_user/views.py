from django.contrib.auth import login
from django.shortcuts import redirect
from django.views.generic import CreateView

from .forms import SignUpForm
from bg_tracker.models import Player


class SignUp(CreateView):
    template_name = 'registration/signup.html'
    form_class = SignUpForm

    def form_valid(self, form):
        user = form.save()
        Player.objects.create(username=form.cleaned_data['username'], user_friend=user)
        login(self.request, user)
        return redirect('home')
