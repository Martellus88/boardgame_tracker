from django.db.models import Max, Min, Count, Q

from bg_tracker.models import Statistic, Player, Score


class StatsFromModels:
    def __init__(self, game_slug, user):
        self._played_game = Statistic.objects.filter(game__slug=game_slug)
        self._user_player = Player.objects.get(
            Q(username__contains=user.username) & Q(user_friend=user.pk))
        self._scores = Score.objects.filter(stats__in=self._played_game)
        self._count_played_game = self._played_game.filter(players=self._user_player).aggregate(Count('id'))

    def get_sum_played_times(self):
        played_time = self._played_game.filter(players=self._user_player)
        minutes = sum(map(lambda time: time.duration.hour * 60 + time.duration.minute, played_time))
        sum_played_time = f'{minutes // 60:02}:{minutes % 60:02}'
        return sum_played_time

    def get_count_win(self):
        return self._played_game.filter(winner=self._user_player).aggregate(Count('id'))

    def get_count_lose(self, count_win):
        return self._count_played_game.get('id__count') - count_win.get('id__count')

    def get_percent_win(self, count_win):
        try:
            percent_win = round(count_win.get('id__count') / self._count_played_game.get('id__count') * 100, 2)
        except ZeroDivisionError:
            percent_win = 0
        return percent_win

    def get_percent_lose(self, count_lose):
        try:
            percent_lose = round(count_lose / self._count_played_game.get('id__count') * 100, 2)
        except ZeroDivisionError:
            percent_lose = 0
        return percent_lose

    def get_max_score(self):
        return self._scores.filter(player=self._user_player).aggregate(mx=Max('score'))

    def get_min_score(self):
        return self._scores.filter(player=self._user_player).aggregate(mn=Min('score'))

    def get_count_played_game(self):
        return self._count_played_game
