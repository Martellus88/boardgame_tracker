from django.urls import path

from rest_framework.routers import SimpleRouter

from .views import PayerAPIView, ScoreAPIView, OverallGameStatAPIView, GameViewSet, StatsAPIView

router = SimpleRouter()
router.register(r'game', GameViewSet, basename='game')
router.register(r'game/(?P<game_slug>[^/.]+)/stats', StatsAPIView, basename='stats')

urlpatterns = [
    path('players/', PayerAPIView.as_view(), name='players'),
    path('game/<slug:game_slug>/stats/<int:pk>/score/', ScoreAPIView.as_view(), name='score'),
    path('game/<slug:game_slug>/overall/', OverallGameStatAPIView.as_view(), name='overall_stat'),
] + router.urls

