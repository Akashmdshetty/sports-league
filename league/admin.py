# league/admin.py
from django.contrib import admin
from .models import Sport, Team, Player, Match

@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "sport")
    search_fields = ("name", "city")
    list_filter = ("sport",)
    filter_horizontal = ("sports",)
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "team", "position", "number")
    list_filter = ("team", "position")
    search_fields = ("first_name", "last_name", "team__name")

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("__str__", "sport", "date_time", "status")
    list_filter = ("sport", "status")
    search_fields = ("home_team__name", "away_team__name", "location")
