from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework import generics, mixins
from rest_framework.response import Response

from api.permissions import IsOwnerStatistic, IsOwner
from api.serializers import GameSerializer, PlayerSerializer, StatsSerializer, GameRetrieveSerializer, ScoreSerializer
from bg_tracker.models import Game, Player, Statistic
from services.overall_stat import StatsFromModels
from services.queries import add_user_in_game_set, game_exists_in_db, add_game_to_user, instance_get, \
    filter_model_or_qs, remove_user_from_game_set, game_added_by_user

User = get_user_model()


class StatsAPIView(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    serializer_class = StatsSerializer
    permission_classes = (IsOwner,)

    def get_queryset(self):
        return filter_model_or_qs(Statistic, game__slug=self.kwargs.get('game_slug'), user_id=self.request.user)

    def perform_create(self, serializer):
        serializer.validated_data['game'] = instance_get(Game, slug=self.kwargs.get('game_slug'))
        serializer.validated_data['players'] = [instance_get(Player, **player) for player in
                                                serializer.validated_data['players']]
        serializer.validated_data['winner'] = instance_get(Player, **serializer.validated_data['winner'])
        serializer.save()


class GameViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet):
    serializer_class = GameSerializer
    retrieve_serializer_class = GameRetrieveSerializer
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action in ["retrieve"]:
            return self.retrieve_serializer_class
        return self.serializer_class

    def get_queryset(self):
        return filter_model_or_qs(Game, user_id=self.request.user)

    def perform_create(self, serializer):
        game_name = serializer.validated_data['game_name']
        game = game_exists_in_db(game_name)

        if game is not None and game_added_by_user(game, self.request.user):
            return Response(game)

        if game is not None:
            add_game_to_user(game, self.request.user)
            return Response(game)

        serializer.save()
        game = instance_get(Game, game_name=game_name)
        add_user_in_game_set(game, user=self.request.user)

    def perform_destroy(self, instance):
        instance_user = instance_get(User, pk=self.request.user.pk)
        remove_user_from_game_set(instance_user, instance)


class PayerAPIView(generics.ListCreateAPIView):
    serializer_class = PlayerSerializer

    def get_queryset(self):
        return filter_model_or_qs(Player, user_friend=self.request.user)


class ScoreAPIView(generics.CreateAPIView):
    serializer_class = ScoreSerializer
    permission_classes = (IsOwnerStatistic,)


class OverallGameStatAPIView(APIView):

    def get(self, request, **kwargs):
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

        return Response({'count_win': count_win['id__count'], 'percent_win': percent_win,
                         'count_played_game': count_played_game['id__count'],
                         'count_lose': count_lose, 'percent_lose': percent_lose, 'sum_played_time': sum_played_time,
                         'best_score': best_score['mx'], 'min_score': min_score['mn']})
