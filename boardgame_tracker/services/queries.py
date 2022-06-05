from django.contrib.auth import get_user_model

from bg_tracker.models import Game

User = get_user_model()

def filter_model(model, **fields):
    return model.objects.filter(**fields)

def get_game_stat(instance_game):
    return instance_game.game_stat.all()

def instance_get(model, **fields):
    return model.objects.get(**fields)

def get_last_instance_id(model):
    return model.objects.last().id

def get_last(model):
    return model.objects.last()

def get_count_players_in_stat(instance_stat):
    return instance_stat.players.count()

def delete_instance(model, **fields):
    tuple = filter_model(model, **fields)
    tuple.delete()

def game_added_by_user(game_name, user):
    user_ = User.objects.get(pk=user.pk)
    return user_.game_set.filter(game_name=game_name).first() is not None

def game_exists_in_db(game_name):
    return Game.objects.filter(game_name=game_name).first()

def add_game_to_user(game, user):
    user_ = User.objects.get(pk=user.pk)
    user_.game_set.add(game)