# league/forms.py
from django import forms
from .models import Team, Player, Match, Sport

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["name", "city", "logo", "sport", "sports"]

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ["first_name", "last_name", "team", "position", "number", "date_of_birth", "nationality"]

class MatchForm(forms.ModelForm):
    date_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={"type": "datetime-local"}))

    class Meta:
        model = Match
        fields = ["sport", "home_team", "away_team", "date_time", "location", "status", "home_score", "away_score", "notes"]
