from django.shortcuts import render, redirect
from django.views.generic import ListView, View, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages

from .forms import AddPlayerForm, AddGameForm, AddStatisticForm, ScoreSet
from .models import Game, Score, Statistic, Player

from services.bgg_info import get_bgg_info
from services.queries import get_game_stat, instance_get, get_last_instance_id, get_last, get_count_players_in_stat, \
    delete_instance, game_added_by_user, game_exists_in_db, add_game_to_user, filter_model_or_qs
from services.overall_stat import StatsFromModels


class HomePage(View):
    def get(self, request):
        return render(request, 'bg_tracker/index.html')


class GameList(LoginRequiredMixin, ListView):
    model = Game
    template_name = 'bg_tracker/games_list.html'
    context_object_name = 'games'

    def get_queryset(self):
        return filter_model_or_qs(Game, user_id=self.request.user)


class GamePage(LoginRequiredMixin, DetailView):
    model = Game
    template_name = 'bg_tracker/game_page.html'
    slug_url_kwarg = 'game_slug'

    def get_queryset(self):
        return filter_model_or_qs(Game, user_id=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        game_stat = filter_model_or_qs(get_game_stat(self.object), user_id=self.request.user)
        my_context = {'game': self.object, 'game_stat': game_stat}
        return context | my_context


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
        return filter_model_or_qs(Player, user_friend=self.request.user)


class AddGame(LoginRequiredMixin, View):

    def get(self, request):
        form = AddGameForm()
        return render(request, 'bg_tracker/add_game.html', {'form': form})

    def post(self, request):
        form = AddGameForm(request.POST)
        if form.is_valid():
            game_name = form.cleaned_data['game_name']

            if game_added_by_user(game_name, self.request.user):
                return redirect('game_list')

            game = game_exists_in_db(game_name)
            if game is not None:
                add_game_to_user(game, self.request.user)
                return redirect('game_list')
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


class AddStats(LoginRequiredMixin, CreateView):
    model = Statistic
    form_class = AddStatisticForm
    template_name = 'bg_tracker/add_stats.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.cleaned_data['game'] = instance_get(Game, slug=self.kwargs.get('game_slug'))
        form.cleaned_data['user_id'] = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('add_score', kwargs={'game_slug': self.kwargs.get('game_slug'),
                                                 'stat_id': get_last_instance_id(Statistic)})


class AddScore(LoginRequiredMixin, View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_stat = get_last(Statistic)
        self._last_stat_player_count = get_count_players_in_stat(self._last_stat)

    def get(self, request, **kwargs):
        score_form = ScoreSet(form_kwargs={'last_stat': self._last_stat},
                              extra=self._last_stat_player_count)
        return render(request, 'bg_tracker/add_score.html', {'form': score_form})

    def post(self, request, **kwargs):
        score_form = ScoreSet(request.POST, form_kwargs={'last_stat': self._last_stat},
                              extra=self._last_stat_player_count)
        if score_form.is_valid():
            last_stat_id = get_last_instance_id(Statistic)
            for score in score_form.cleaned_data:
                score.update({'stats_id': last_stat_id})
            score_form.save()
        return redirect('game_page', game_slug=self.kwargs.get('game_slug'))


class GameStatPage(LoginRequiredMixin, DetailView):
    model = Statistic
    template_name = 'bg_tracker/game_stat.html'
    pk_url_kwarg = 'stat_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        scores = filter_model_or_qs(Score, stats=self.object)
        my_context = {'game_stat': self.object, 'scores': scores}
        return context | my_context

    def post(self, *args, **kwargs):
        stat_id_ = self.request.POST.get('stat_id')
        delete_instance(Statistic, id=stat_id_)
        return redirect('game_page', game_slug=self.kwargs.get('game_slug'))


class OverallGameStats(LoginRequiredMixin, DetailView):
    model = Game
    template_name = 'bg_tracker/overall_game_stat.html'
    slug_url_kwarg = 'game_slug'

    def get_queryset(self):
        return filter_model_or_qs(Game, user_id=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        overall_game_stat = StatsFromModels(game_slug=self.kwargs['game_slug'],
                                            user=self.request.user)
        count_win = overall_game_stat.get_count_win()
        percent_win = overall_game_stat.get_percent_win(count_win=count_win)
        count_lose = overall_game_stat.get_count_lose(count_win=count_win)
        percent_lose = overall_game_stat.get_percent_lose(count_lose=count_lose)
        best_score = overall_game_stat.get_max_score()
        min_score = overall_game_stat.get_min_score()
        sum_played_time = overall_game_stat.get_sum_played_times()
        count_played_game = overall_game_stat.get_count_played_game()

        my_context = {'count_win': count_win, 'percent_win': percent_win, 'count_played_game': count_played_game,
                      'count_lose': count_lose, 'percent_lose': percent_lose, 'sum_played_time': sum_played_time,
                      'best_score': best_score, 'min_score': min_score}

        return context | my_context
