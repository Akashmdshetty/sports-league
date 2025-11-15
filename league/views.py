# league/views.py
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils import timezone
from django.http import JsonResponse

from .models import Team, Player, Match, Sport
from .forms import TeamForm, PlayerForm, MatchForm

# helper pagination
def paginate_qs(request, queryset, per_page=10):
    paginator = Paginator(queryset, per_page)
    page = request.GET.get("page", 1)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
    return items

def home(request):
    return render(request, "home.html")

# Teams
def teams_list(request):
    qs = Team.objects.all().order_by("name").select_related('sport')
    page_obj = paginate_qs(request, qs, per_page=12)
    return render(request, "league/teams_list.html", {"page_obj": page_obj})

def team_detail(request, pk):
    team = get_object_or_404(Team, pk=pk)
    players = team.players.all().order_by('number', 'last_name')
    return render(request, "league/team_detail.html", {"team": team, "players": players})

def add_team(request):
    if request.method == "POST":
        form = TeamForm(request.POST, request.FILES)
        if form.is_valid():
            team = form.save(commit=False)
            team.save()
            form.save_m2m()
            return redirect("teams_list")
    else:
        initial = {}
        sport_q = request.GET.get("sport")
        if sport_q:
            sport = None
            if sport_q.isdigit():
                sport = Sport.objects.filter(id=int(sport_q)).first()
            else:
                sport = Sport.objects.filter(slug=sport_q).first()
            if sport:
                initial["sport"] = sport.id
                initial["sports"] = [sport.id]
        form = TeamForm(initial=initial)
    return render(request, "league/add_team.html", {"form": form})

# Players
def players_list(request):
    qs = Player.objects.select_related("team").order_by("team__name", "number", "last_name")
    page_obj = paginate_qs(request, qs, per_page=20)
    return render(request, "league/players_list.html", {"page_obj": page_obj})

def player_detail(request, pk):
    player = get_object_or_404(Player, pk=pk)
    return render(request, "league/player_detail.html", {"player": player})

def add_player(request):
    # mapping for UI and validation
    sport_positions = {
        "football": [("GK", "Goalkeeper"), ("DF", "Defender"), ("MF", "Midfielder"), ("FW", "Forward")],
        "cricket": [("BAT", "Batsman"), ("BWL", "Bowler"), ("AR", "All-rounder"), ("WK", "Wicketkeeper")],
        "rugby": [("PR", "Prop"), ("HK", "Hooker"), ("LO", "Lock"), ("FL", "Flanker"), ("SH", "Scrum-half"), ("FH", "Fly-half"), ("CE", "Centre"), ("WG", "Wing"), ("FB", "Fullback")],
        "badminton": [("MS", "Men's Singles"), ("WS", "Women's Singles"), ("MD", "Men's Doubles"), ("WD", "Women's Doubles"), ("XD", "Mixed Doubles")],
        "baseball": [("P", "Pitcher"), ("C", "Catcher"), ("1B", "First Base"), ("2B", "Second Base"), ("3B", "Third Base"), ("SS", "Shortstop"), ("LF", "Left Field"), ("CF", "Center Field"), ("RF", "Right Field")],
    }
    sport_positions = {k.lower(): v for k,v in sport_positions.items()}

    union_choices = []
    seen = set()
    for positions in sport_positions.values():
        for code, label in positions:
            if code not in seen:
                union_choices.append((code, label))
                seen.add(code)
    union_choices = [("", "---------")] + union_choices

    if request.method == "POST":
        form = PlayerForm(request.POST)
        form.fields['position'].choices = union_choices
        if form.is_valid():
            form.save()
            return redirect("players_list")
    else:
        form = PlayerForm()
        form.fields['position'].choices = union_choices

    teams = Team.objects.prefetch_related('sports').order_by('name')
    team_sports = {}
    for t in teams:
        team_sports[t.id] = [ (s.slug or s.name).lower() for s in t.sports.all() ]

    js_sport_positions = {}
    for k, poslist in sport_positions.items():
        js_sport_positions[k] = [{"code": c, "label": l} for c, l in poslist]

    context = {
        "form": form,
        "teams": teams,
        "team_sports_json": json.dumps(team_sports),
        "sport_positions_json": json.dumps(js_sport_positions),
    }
    return render(request, "league/add_player.html", context)

# Matches
def matches_list(request):
    sport_q = request.GET.get("sport")
    filter_by = request.GET.get("filter", "upcoming")
    now = timezone.now()

    qs = Match.objects.all().select_related('sport', 'home_team', 'away_team')
    if sport_q:
        if sport_q.isdigit():
            qs = qs.filter(sport__id=int(sport_q))
        else:
            qs = qs.filter(sport__slug=sport_q)

    if filter_by == "past":
        qs = qs.filter(date_time__lt=now).order_by("-date_time")
    elif filter_by == "all":
        qs = qs.order_by("-date_time")
    else:
        qs = qs.filter(date_time__gte=now).order_by("date_time")

    page_obj = paginate_qs(request, qs, per_page=12)
    sports = Sport.objects.all()
    return render(request, "league/matches_list.html", {"page_obj": page_obj, "sports": sports, "selected_sport": sport_q, "filter": filter_by})

def match_detail(request, pk):
    match = get_object_or_404(Match, pk=pk)
    return render(request, "league/match_detail.html", {"match": match})

def add_match(request):
    if request.method == "POST":
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("matches_list")
    else:
        form = MatchForm()
    return render(request, "league/add_match.html", {"form": form})
