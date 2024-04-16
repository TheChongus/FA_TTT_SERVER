from django.db import models
from django.contrib.auth.models import User


class Team(models.Model):
    #The team class has a name and auth key
    name = models.CharField(max_length=255)
    auth_key = models.CharField(max_length=255)
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teams')

    def __str__(self):
        return self.name, self.auth_key

class Opponent(models.Model):
    '''
    The opponent class is simple as it contains only the values we can get from the game server api endpoint
    '''
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Game(models.Model):
    '''
    This is the game class containing the game_id, the status of the game, the opponent's name, the current team name (to indicate whose turn it is)
    and the team name of the player
    '''
    game_id = models.IntegerField()
    status = models.CharField(max_length=25)
    opponent = models.ForeignKey(Opponent, on_delete=models.CASCADE, null=True, blank=True)
    turn = models.CharField(max_length=100, null=True, blank=True)
    player_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='games')
    
    def __str__(self):
        return self.game_id, self.status, self.opponent, self.current_team, self.player_team
    
    #When a team record has no games associated with it, remove the team record
    def delete(self, *args, **kwargs):
        team = self.player_team
        super().delete(*args, **kwargs)
        if not Game.objects.filter(team=team).exists():
            team.delete()


class Move(models.Model):
    '''
    Each game has a series of moves. The move class has 9 possible moves: rows A-C and columns 1-3
    Moves have a game id, team name, row, and space value
    '''
    ROW_CHOICES = [(i, i) for i in 'ABC']
    COLUMN_CHOICES = [(i, i) for i in range(1, 4)]

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='moves')
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    row = models.CharField(max_length=1, choices=ROW_CHOICES)
    column = models.CharField(max_length=1, choices=COLUMN_CHOICES)
    value = models.CharField(max_length=1, null=True, blank=True)

    class Meta:
        unique_together = ('game', 'row', 'column')
    
    def __str__(self):
        return f'{self.team.name} moved at {self.row}{self.column} in game {self.game.game_id}'