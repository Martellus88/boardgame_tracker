import datetime

from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class Game(models.Model):
    game_name = models.CharField(max_length=255, unique=True)
    image = models.URLField()
    slug = models.SlugField(max_length=255)
    user_id = models.ManyToManyField(User)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.game_name)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('game_page', kwargs={'game_slug': self.slug})

    def __str__(self):
        return self.game_name


class Player(models.Model):
    username = models.CharField(max_length=100)
    user_friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_friends')
    game_played = models.ManyToManyField(Game, blank=True)

    def __str__(self):
        return self.username


class Statistic(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_owner')
    stats_name = models.CharField(max_length=100)
    game_date = models.DateField(default=timezone.now)
    duration = models.TimeField(default=datetime.time())
    comments = models.TextField(blank=True, null=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='game_stat')
    winner = models.ForeignKey(Player, on_delete=models.PROTECT, related_name='winner')
    players = models.ManyToManyField(Player)

    def __str__(self):
        return f"{self.game_date}-{self.game}: winner - {self.winner}"

    def get_absolute_url(self, game):
        return reverse('stats-detail', kwargs={'pk': self.id, 'game_slug': game.slug})


class Score(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player')
    stats = models.ForeignKey(Statistic, on_delete=models.CASCADE)
    score = models.IntegerField()

    def __str__(self):
        return f"*{self.player}* in [{self.stats.stats_name}] with score: {self.score}"
