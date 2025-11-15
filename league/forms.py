# league/forms.py
from django import forms
from .models import Team, Player, Match, Sport

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["name", "city", "logo", "sport", "sports"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Team name", "required": True}),
            "city": forms.TextInput(attrs={"class": "form-control", "placeholder": "City"}),
            "sport": forms.Select(attrs={"class": "form-control"}),
            "sports": forms.CheckboxSelectMultiple(),
        }

class PlayerForm(forms.ModelForm):
    position = forms.ChoiceField(choices=[], required=False, widget=forms.Select(attrs={"class": "form-select"}))

    class Meta:
        model = Player
        fields = ["first_name", "last_name", "team", "position", "number", "date_of_birth", "nationality"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "First name", "required": True}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"}),
            "team": forms.Select(attrs={"class": "form-select"}),
            "number": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Jersey number"}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "nationality": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nationality"}),
        }

class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ["sport", "home_team", "away_team", "date_time", "location", "status", "home_score", "away_score"]
        widgets = {
            "sport": forms.Select(attrs={"class": "form-control"}),
            "home_team": forms.Select(attrs={"class": "form-control"}),
            "away_team": forms.Select(attrs={"class": "form-control"}),
            "date_time": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "home_score": forms.NumberInput(attrs={"class": "form-control"}),
            "away_score": forms.NumberInput(attrs={"class": "form-control"}),
        }
