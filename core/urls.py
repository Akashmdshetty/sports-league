# core/urls.py
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from league import views as league_views

urlpatterns = [
    path("", league_views.home, name="home"),

    # Teams
    path("teams/", league_views.teams_list, name="teams_list"),
    path("teams/add/", league_views.add_team, name="add_team"),
    path("teams/<int:pk>/", league_views.team_detail, name="team_detail"),

    # Players
    path("players/", league_views.players_list, name="players_list"),
    path("players/add/", league_views.add_player, name="add_player"),
    path("players/<int:pk>/", league_views.player_detail, name="player_detail"),

    # Matches
    path("matches/", league_views.matches_list, name="matches_list"),
    path("matches/add/", league_views.add_match, name="add_match"),
    path("matches/<int:pk>/", league_views.match_detail, name="match_detail"),

    # Admin
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
