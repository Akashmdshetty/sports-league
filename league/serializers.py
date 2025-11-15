# league/serializers.py
from rest_framework import serializers
from .models import Team, Player, Match, Sport

class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = ['id', 'name', 'slug']

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'

class TeamSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)
    sport = SportSerializer(read_only=True)
    sport_id = serializers.PrimaryKeyRelatedField(queryset=Sport.objects.all(), source='sport', write_only=True, required=False, allow_null=True)
    sports = SportSerializer(many=True, read_only=True)
    sports_ids = serializers.PrimaryKeyRelatedField(queryset=Sport.objects.all(), many=True, source='sports', write_only=True, required=False)

    class Meta:
        model = Team
        fields = ['id', 'name', 'city', 'founded', 'logo', 'slug', 'sport', 'sport_id', 'sports', 'sports_ids', 'players']

    def create(self, validated_data):
        # handle write-only sports_ids field
        sports_data = validated_data.pop('sports', None)
        team = super().create(validated_data)
        # if sports provided in raw data they will be in initial_data under 'sports_ids' — DRF handles assignment automatically if present
        return team

class MatchSerializer(serializers.ModelSerializer):
    home_team = serializers.PrimaryKeyRelatedField(queryset=Team.objects.all())
    away_team = serializers.PrimaryKeyRelatedField(queryset=Team.objects.all())
    sport = serializers.PrimaryKeyRelatedField(queryset=Sport.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Match
        fields = '__all__'

    def validate(self, data):
        if data.get('home_team') == data.get('away_team'):
            raise serializers.ValidationError('Home and away team must be different')
        return data
