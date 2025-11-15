# league/models.py
from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class Sport(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Sport"
        verbose_name_plural = "Sports"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Team(models.Model):
    name = models.CharField(max_length=150)
    city = models.CharField(max_length=120, blank=True)
    founded = models.IntegerField(blank=True, null=True)
    logo = models.ImageField(upload_to="team_logos/", blank=True, null=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True)

    # primary sport (optional) and also multi-sport support
    sport = models.ForeignKey(Sport, on_delete=models.SET_NULL, blank=True, null=True, related_name="primary_teams")
    sports = models.ManyToManyField(Sport, blank=True, related_name="teams")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            counter = 1
            # ensure unique slug
            while Team.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("team_detail", args=[self.pk])


class Player(models.Model):
    # position stored as short code (display via choices)
    POSITION_CHOICES = [
        ("GK", "Goalkeeper"),
        ("DF", "Defender"),
        ("MF", "Midfielder"),
        ("FW", "Forward"),

        # cricket
        ("BAT", "Batsman"),
        ("BWL", "Bowler"),
        ("AR", "All-rounder"),
        ("WK", "Wicketkeeper"),

        # rugby
        ("PR", "Prop"),
        ("HK", "Hooker"),
        ("LO", "Lock"),
        ("FL", "Flanker"),
        ("SH", "Scrum-half"),
        ("FH", "Fly-half"),
        ("CE", "Centre"),
        ("WG", "Wing"),
        ("FB", "Fullback"),

        # badminton (examples)
        ("MS", "Mens Singles"),
        ("WS", "Womens Singles"),
        ("MD", "Mens Doubles"),
        ("WD", "Womens Doubles"),
        ("XD", "Mixed Doubles"),

        # baseball
        ("P", "Pitcher"),
        ("C", "Catcher"),
        ("1B", "First Base"),
        ("2B", "Second Base"),
        ("3B", "Third Base"),
        ("SS", "Shortstop"),
        ("LF", "Left Field"),
        ("CF", "Center Field"),
        ("RF", "Right Field"),
    ]

    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120, blank=True)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, blank=True, null=True, related_name="players")
    position = models.CharField(max_length=10, choices=POSITION_CHOICES, blank=True)
    number = models.IntegerField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["team__name", "last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()


class Match(models.Model):
    STATUS_CHOICES = [
        ("SCHEDULED", "Scheduled"),
        ("ONGOING", "Ongoing"),
        ("FINISHED", "Finished"),
        ("CANCELLED", "Cancelled"),
    ]

    sport = models.ForeignKey(Sport, on_delete=models.SET_NULL, blank=True, null=True, related_name="matches")
    home_team = models.ForeignKey(Team, on_delete=models.SET_NULL, blank=True, null=True, related_name="home_matches")
    away_team = models.ForeignKey(Team, on_delete=models.SET_NULL, blank=True, null=True, related_name="away_matches")
    date_time = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="SCHEDULED")
    home_score = models.IntegerField(blank=True, null=True)
    away_score = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date_time"]

    def __str__(self):
        ht = self.home_team.name if self.home_team else "TBD"
        at = self.away_team.name if self.away_team else "TBD"
        return f"{ht} vs {at} — {self.date_time:%Y-%m-%d %H:%M}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("match_detail", args=[self.pk])
