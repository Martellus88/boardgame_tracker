from django import forms
from django.forms import BaseModelFormSet, modelformset_factory

from .models import Player, Statistic, Game, Score
from services.queries import create_model_instance, get_players_from_stat, add_players_in_stats, \
    add_user_in_game_set, filter_model_or_qs


class AddPlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['username']

    def save(self, commit=True):
        player = create_model_instance(Player, **self.cleaned_data)
        return player


class AddGameForm(forms.Form):
    game_name = forms.CharField(max_length=255)

    def save(self):
        user = self.cleaned_data.pop('user_id')
        game = create_model_instance(Game, **self.cleaned_data)
        add_user_in_game_set(game, user=user)


class AddStatisticForm(forms.ModelForm):
    players = forms.ModelMultipleChoiceField(queryset=Player.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Statistic
        fields = ['stats_name', 'game_date', 'duration', 'comments', 'winner', 'players']
        widgets = {
            'comments': forms.Textarea(attrs={'cols': 60, 'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        choices_fields_queryset = filter_model_or_qs(Player, user_friend=user)
        self.fields['players'].queryset = choices_fields_queryset
        self.fields['winner'].queryset = choices_fields_queryset

    def save(self, commit=True):
        players = self.cleaned_data.pop('players')
        players_id = [player.id for player in players]
        stats = create_model_instance(Statistic, **self.cleaned_data)
        add_players_in_stats(stats, *players_id)
        return stats


class ScoreForm(forms.ModelForm):
    class Meta:
        model = Score
        fields = ['player', 'score']

    def __init__(self, *args, **kwargs):
        self._last_stat = kwargs.pop('last_stat')
        super().__init__(*args, **kwargs)
        self.fields['player'].queryset = get_players_from_stat(self._last_stat)

    def save(self, commit=True):
        score = create_model_instance(Score, **self.cleaned_data)
        return score


class ScoreFormSet(BaseModelFormSet):
    def __init__(self, *args, extra, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra = extra
        self.queryset = Score.objects.none()


ScoreSet = modelformset_factory(Score, ScoreForm, fields=('player', 'score'), formset=ScoreFormSet)
