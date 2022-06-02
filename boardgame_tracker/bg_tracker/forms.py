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
