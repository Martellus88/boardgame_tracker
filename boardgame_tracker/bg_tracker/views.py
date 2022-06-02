from django.shortcuts import render
from django.views.generic import ListView, View, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .forms import AddPlayerForm
from .models import Game, Score, Statistic, Player


class HomePage(View):

    def get(self, request):
        return render(request, 'bg_tracker/index.html')


class GameList(LoginRequiredMixin, ListView):
    model = Game
    template_name = 'bg_tracker/games_list.html'
    context_object_name = 'games'

    def get_queryset(self):
        return Game.objects.filter(user_id=self.request.user)

class GamePage(LoginRequiredMixin, DetailView):
    model = Game
    template_name = 'bg_tracker/game_page.html'
    slug_url_kwarg = 'game_slug'

    def get_queryset(self):
        return Game.objects.filter(user_id=self.request.user)


class AddPlayer(LoginRequiredMixin, CreateView):
    model = Player
    form_class = AddPlayerForm
    template_name = 'bg_tracker/add_player.html'

    def form_valid(self, form):
        form.cleaned_data['user_friend'] = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.GET.get('next', reverse_lazy('home'))


class PlayersList(LoginRequiredMixin, ListView):
    model = Player
    template_name = 'bg_tracker/players_list.html'
    context_object_name = 'players'

    def get_queryset(self):
        return Player.objects.filter(user_friend=self.request.user)


