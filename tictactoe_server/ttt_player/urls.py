from django.urls import path
from ttt_player import views


urlpatterns = [
    path('', views.home, name='home'),
    path('play/<int:game_id>', views.currentgame, name='currentgame'),
    path('activegames/', views.active_games, name='activegames'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('create_team/', views.create_team, name='create_team'),
    path('game/<int:game_id>/<int:team_id>/', views.game_detail, name='game_detail'),
    path('game_ids', views.game_ids, name='game_ids'),
]