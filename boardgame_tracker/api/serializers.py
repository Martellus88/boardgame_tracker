from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from bg_tracker.models import Game, Player, Statistic, Score
from services.queries import filter_model_or_qs, create_model_instance, filter_game_stat


class PlayerSerializer(ModelSerializer):
    user_friend = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Player
        fields = ('username', 'user_friend')


class ScoreSerializer(ModelSerializer):
    stats_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Score
        fields = ('stats_id', 'player', 'score')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['player'] = instance.player.username
        return response


class StatsSerializer(ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    scores = serializers.SerializerMethodField('get_score', read_only=True)
    players = PlayerSerializer(many=True)
    winner = PlayerSerializer()

    class Meta:
        model = Statistic
        fields = ('id', 'stats_name', 'game_date', 'duration', 'comments', 'winner', 'players', 'scores', 'user_id')

    def get_score(self, stat):
        scores = filter_model_or_qs(Score, stats=stat)
        return [ScoreSerializer(score).data for score in scores]


class GameSerializer(serializers.Serializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    game_name = serializers.CharField(max_length=255)
    image = serializers.URLField()

    def create(self, validated_data):
        return create_model_instance(Game, **validated_data)


class GameRetrieveSerializer(ModelSerializer):
    game_stats = serializers.SerializerMethodField('get_stat_url')
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Game
        fields = ('id', 'game_name', 'url', 'image', 'game_stats')

    def get_stat_url(self, game):
        return [stat.get_absolute_url(game) for stat in filter_game_stat(game, user_id=self.context['request'].user)]
