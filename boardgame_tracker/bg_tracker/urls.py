from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomePage.as_view(), name='home'),
    path('game_list/', views.GameList.as_view(), name='game_list'),
    path('game/<slug:game_slug>', views.GamePage.as_view(), name='game_page'),
]
