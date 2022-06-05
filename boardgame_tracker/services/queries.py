from django.contrib.auth import get_user_model
from django.db import models

from bg_tracker.models import Game

User = get_user_model()


def create_user(password, **fields):
    user = User(**fields)
    user.set_password(password)
    user.save()
    return user


def filter_model_or_qs(model_or_qs, **fields):
    if isinstance(model_or_qs, models.query.QuerySet):
        return model_or_qs.filter(**fields)
    return model_or_qs.objects.filter(**fields)


def get_game_stat(instance_game):
    return instance_game.game_stat.all()


def instance_get(model, **fields):
    return model.objects.get(**fields)


def get_last_instance_id(model):
    return model.objects.last().id


def get_first_instance(model, **fields):
    instance = filter_model_or_qs(model, **fields)
    return instance.first()


def get_last(model):
    return model.objects.last()


def get_count_players_in_stat(instance_stat):
    return instance_stat.players.count()


def get_players_from_stat(instance_stat):
    return instance_stat.players.all()


def delete_instance(model, **fields):
    tuple = filter_model_or_qs(model, **fields)
    tuple.delete()


def game_added_by_user(game_name, user):
    user_ = User.objects.get(pk=user.pk)
    return user_.game_set.filter(game_name=game_name).first() is not None


def game_exists_in_db(game_name):
    return Game.objects.filter(game_name=game_name).first()


def add_game_to_user(game, user):
    user_ = User.objects.get(pk=user.pk)
    user_.game_set.add(game)


def create_model_instance(model, **fields):
    instance = model(**fields)
    instance.save()
    return instance


def add_players_in_stats(instance_stat, *players):
    instance_stat.players.add(*players)


def add_user_in_game_set(instance_game, user):
    instance_game.user_id.add(user)
