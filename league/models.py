# league/models.py
from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError

class Sport(models.Model):
    """
    A sport type (Football, Cricket, Basketball...). Editable in admin.
    """
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Sport'
        verbose_name_plural = 'Sports'

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or 'sport'
            slug = base
            i = 1
            while Sport.objects.filter(slug=slug).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Team(models.Model):
    """
    Team can now play multiple sports (sports M2M). `sport` FK kept for backward-compat.
    """
    name = models.CharField(max_length=100, unique=True)
    city = models.CharField(max_length=100, blank=True)
    founded = models.PositiveIntegerField(null=True, blank=True)
    logo = models.ImageField(upload_to='team_logos/', null=True, blank=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    # optional single sport field (backward compatibility)
    sport = models.ForeignKey(Sport, on_delete=models.SET_NULL, null=True, blank=True, related_name="primary_teams")

    # NEW: many-to-many so a team may play multiple sports
    sports = models.ManyToManyField(Sport, related_name='teams', blank=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or 'team'
            slug = base
            i = 1
            while Team.objects.filter(slug=slug).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Player(models.Model):
    POSITION_CHOICES = [
        ('GK', 'Goalkeeper'),
        ('DF', 'Defender'),
        ('MF', 'Midfielder'),
        ('FW', 'Forward'),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True)
    team = models.ForeignKey(Team, related_name='players', on_delete=models.SET_NULL, null=True, blank=True)
    position = models.CharField(max_length=2, choices=POSITION_CHOICES, default='MF')
    number = models.PositiveSmallIntegerField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['team', 'number']
        unique_together = (('team', 'number'),)

    def __str__(self):
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name


class Match(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed'),
        ('POSTPONED', 'Postponed'),
        ('CANCELLED', 'Cancelled'),
    ]

    # sport nullable initially to avoid migration pain; you can make it required later
    sport = models.ForeignKey(Sport, on_delete=models.PROTECT, related_name="matches", null=True, blank=True)
    home_team = models.ForeignKey(Team, related_name='home_matches', on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name='away_matches', on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    home_score = models.PositiveSmallIntegerField(null=True, blank=True)
    away_score = models.PositiveSmallIntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='SCHEDULED')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_time']
        constraints = [
            models.CheckConstraint(check=~models.Q(home_team=models.F('away_team')), name='prevent_same_team'),
        ]

    def clean(self):
        if self.home_team_id and self.away_team_id and self.home_team_id == self.away_team_id:
            raise ValidationError('Home team and away team must be different')
        # optionally ensure team sports match match.sport if team.sport/sports set
        if self.sport:
            if self.home_team and self.home_team.sports.exists() and self.sport not in self.home_team.sports.all():
                raise ValidationError('Home team does not play this sport')
            if self.away_team and self.away_team.sports.exists() and self.sport not in self.away_team.sports.all():
                raise ValidationError('Away team does not play this sport')

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} — {self.date_time.date()}"

    @property
    def winner(self):
        if self.home_score is None or self.away_score is None:
            return None
        if self.home_score > self.away_score:
            return self.home_team
        if self.away_score > self.home_score:
            return self.away_team
        return 'Draw'

    def is_past(self):
        from django.utils import timezone
        return self.date_time < timezone.now()
