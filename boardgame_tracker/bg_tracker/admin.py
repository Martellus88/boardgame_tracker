from django.contrib import admin

from .models import Game, Player, Statistic, Score

admin.site.register(Game)
admin.site.register(Player)
admin.site.register(Score)
admin.site.register(Statistic)
