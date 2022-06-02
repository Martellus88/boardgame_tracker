from django.shortcuts import render
from django.views.generic import ListView, View, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

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




