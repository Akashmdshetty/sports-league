# league/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    api_home,
    TeamViewSet,
    PlayerViewSet,
    MatchViewSet,
    teams_list,
    players_list,
    matches_list,
    match_detail,
)

router = DefaultRouter()
router.register(r"teams", TeamViewSet)
router.register(r"players", PlayerViewSet)
router.register(r"matches", MatchViewSet)

urlpatterns = [
    path("", api_home, name="api-home"),
] + router.urls + [
    path("teams/", teams_list, name="teams-list-in-api"),   # not strictly used; main pages are top-level
    path("players/", players_list, name="players-list-in-api"),
    path("matches/", matches_list, name="matches-list-in-api"),
    path("matches/<int:pk>/", match_detail, name="match-detail-in-api"),
]
