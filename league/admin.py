# league/admin.py
from django.contrib import admin
from .models import Sport, Team, Player, Match

@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

class PlayerInline(admin.TabularInline):
    model = Player
    extra = 0
    fields = ('first_name', 'last_name', 'position', 'number')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_sports', 'city', 'founded')
    search_fields = ('name', 'city')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [PlayerInline]
    filter_horizontal = ('sports',)

    def get_sports(self, obj):
        return ", ".join([s.name for s in obj.sports.all()])
    get_sports.short_description = 'Sports'

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'team', 'position', 'number')
    list_filter = ('position', 'team')
    search_fields = ('first_name', 'last_name')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('sport', 'home_team', 'away_team', 'date_time', 'status', 'home_score', 'away_score')
    list_filter = ('sport', 'status', 'date_time')
    search_fields = ('home_team__name', 'away_team__name')
