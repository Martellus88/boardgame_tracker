from django.shortcuts import render, redirect
from django.views.generic import ListView, View, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages

from .forms import AddPlayerForm, AddGameForm
from .models import Game, Score, Statistic, Player
from services.bgg_info import get_bgg_info


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


class AddGame(LoginRequiredMixin, View):

    def get(self, request):
        form = AddGameForm()
        return render(request, 'bg_tracker/add_game.html', {'form': form})

    def post(self, request):
        form = AddGameForm(request.POST)
        if form.is_valid():
            game_name = form.cleaned_data['game_name']
            try:
                game_img = get_bgg_info(game_name)
            except KeyError:
                messages.error(self.request, 'The name of the game is incorrect or the game does not exist')
                return redirect('add_game')
            else:
                form.cleaned_data['user_id'] = self.request.user
                form.cleaned_data['image'] = game_img
                form.save()
                return redirect('game_list')
