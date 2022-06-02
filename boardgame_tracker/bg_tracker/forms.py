from django import forms
from django.forms import BaseModelFormSet, modelformset_factory

from .models import Player, Statistic, Game, Score


class AddPlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['username']

    def save(self, commit=True):
        player = Player(**self.cleaned_data)
        player.save()
        return player


class AddGameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['game_name']

    def save(self, commit=True):
        user = self.cleaned_data.pop('user_id')
        game = Game(**self.cleaned_data)
        game.save()
        game.user_id.add(user)


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

        choices_fields_queryset = Player.objects.filter(user_friend=user)
        self.fields['players'].queryset = choices_fields_queryset
        self.fields['winner'].queryset = choices_fields_queryset

    def save(self, commit=True):
        players = self.cleaned_data.pop('players')
        players_id = [player.id for player in players]

        stats = Statistic(**self.cleaned_data)
        stats.save()

        stats.players.add(*players_id)
        return stats


class ScoreForm(forms.ModelForm):
    class Meta:
        model = Score
        fields = ['player', 'score']

    def __init__(self, *args, **kwargs):
        self._last_stat = kwargs.pop('last_stat')
        super().__init__(*args, **kwargs)

        self.fields['player'].queryset = self._last_stat.players.all()

    def save(self, commit=True):
        score = Score(**self.cleaned_data)
        score.save()
        return score


class ScoreFormSet(BaseModelFormSet):
    def __init__(self, *args, extra, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra = extra
        self.queryset = Score.objects.none()


ScoreSet = modelformset_factory(Score, ScoreForm, fields=('player', 'score'), formset=ScoreFormSet)
