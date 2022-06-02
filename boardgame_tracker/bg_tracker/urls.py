from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomePage.as_view(), name='home'),
    path('game_list/', views.GameList.as_view(), name='game_list'),
    path('game/<slug:game_slug>', views.GamePage.as_view(), name='game_page'),
    path('add-player/', views.AddPlayer.as_view(), name='add_player'),
    path('players-list/', views.PlayersList.as_view(), name='players_list'),
    path('add-game/', views.AddGame.as_view(), name='add_game'),
    path('game/<slug:game_slug>/add-stats/', views.AddStats.as_view(), name='add_stats'),
    path('game/<slug:game_slug>/statistic/<int:stats_id>/add-score/', views.AddScore.as_view(), name='add_score'),
]
