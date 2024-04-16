# tasks.py

from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import Game, Team  # replace '.' with the name of your Django app if 'tasks.py' is not in the same directory as 'models.py'
import requests
import logging 

# create a logger object
logger = logging.getLogger(__name__)


#function to clean up orphaned teams
@shared_task
def clean_up():
    #if there are any teams with no games, delete them
    teams = Team.objects.all()
    for team in teams:
        if team.games.count() == 0:
            team.delete()
            logger.info(f'Team {team.team_id} has been deleted')



@shared_task
def update_game_statuses():
    
    #get all games from the database without a 'completed' or 'expired' status
    games = Game.objects.exclude(status__in=['Completed', 'Expired'])

    #iterate through the games and send a request to the external server to get the game status.
    #if the request is successful, update the game status in the database, otherwise log the error

    for game in games:
        print(f'Updating game status for game {game.game_id}')

        url = f'https://xo.fullyaccountable.com/game/{game.game_id}/status'

        try:
            response = requests.get(url)
            game.status = response.json()['status']

            game.save()
        
        except Exception as e:
            logger.error(f'Error updating game status for game {game.game_id}: {e}')
            print(f'Error updating game status for game {game.game_id}: {e}')
            continue


