from django.contrib.auth import login
from django.shortcuts import redirect
from django.views.generic import CreateView

from boardgame_tracker.auth_user.forms import SignUpForm


class SignUp(CreateView):
    template_name = 'registration/signup.html'
    form_class = SignUpForm

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')
