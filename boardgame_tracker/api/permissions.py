import logging

from rest_framework import permissions

from bg_tracker.models import Statistic
from services.queries import instance_get

logger = logging.getLogger(__name__)


class IsOwnerStatistic(permissions.BasePermission):
    def has_permission(self, request, view):
        stat_id = request.resolver_match.kwargs.get('pk')
        try:
            obj = instance_get(Statistic, pk=stat_id)
        except Statistic.DoesNotExist as e:
            logger.warning(f'{type(e)}, {e}; fields: [id] - {stat_id}')
        else:
            return request.user and request.user.is_authenticated and obj.user_id == request.user


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_authenticated and obj.user_id == request.user
