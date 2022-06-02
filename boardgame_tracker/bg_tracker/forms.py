from django import forms

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