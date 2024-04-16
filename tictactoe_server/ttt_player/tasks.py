# tasks.py

from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import Game, Team, Opponent, Move  # replace '.' with the name of your Django app if 'tasks.py' is not in the same directory as 'models.py'
import requests
import logging 
from django.contrib import messages

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
        print(f'\nUpdating game status for game {game.game_id}')
        
        url = f'https://xo.fullyaccountable.com/game/{game.game_id}/status'
        
        try:
            response = requests.get(url)
            print(response.json())
            game_data = response.json()
            status = response.json()['status']

            #if the game status is no longer the same, update the game status in the database

            if status:
                game.status = status
                game.save()

                print(f'Game status updated to {status} for game {game.game_id}')

            #if there is a value for current team:
            if game_data['current_team']:
                
                response_team = game_data['current_team']

                game_team = Team.objects.get(id=game.player_team_id).name
                #if the currdent_team is the same as the player's team, update the game turn 'player' in the database
                #we need to get the id of the team from the game object and use it to look up the team name in the Team model
                
                if response_team == game_team:
                    game.turn = 'player'
                    game.save()
                    print(f'Game turn updated to player for game {game.game_id}')
            
                    #if the game has a 'last_move' key in the response, update the move in the database'
                    if game_data['last_move']:
                        print(f'Last move by {game_team}: {game_data["last_move"]}')
                        #the moves come in as B2, C3, etc. We need to split the string into row and column
                        row = game_data['last_move'][0]
                        column = game_data['last_move'][1]

                        #the server manages the history of moves, so we don't need to check if the move already exists
                        #we can just create a new move record
                        Move.objects.create(game=game, team_id=game.player_team_id, row=row, column=column)

                elif response_team != game_team:
                    game.turn = 'opponent'
                    game.save()
                    
                    #check to see if the opponent exists in the database
                    #if not, create a new opponent record
                    if not Opponent.objects.filter(name=response_team).exists():
                        Opponent.objects.create(name=response_team)

                        print(f'Opponent {response_team} created')

                    #get the opponent object from the database
                    opponent = Opponent.objects.get(name=response_team)
                    game.opponent = opponent
                    game.save()
                    print(f'Game turn updated to opponent for game {game.game_id}')

                    '''
                    #if the game has a 'last_move' key in the response, update the move in the database'
                    if game_data['last_move']:
                        #the moves come in as B2, C3, etc. We need to split the string into row and column
                        row = game_data['last_move'][0]
                        column = game_data['last_move'][1]

                        #the server manages the history of moves, so we don't need to check if the move already exists
                        #we can just create a new move record
                        Move.objects.create(game=game, opponent=opponent, row=row, column=column)
                    '''




        except requests.exceptions.RequestException as e:
            logger.error(f'Error updating game status for game {game.game_id}: {e}')
            continue
        except Exception as e:
            logger.error(f'Error updating game status for game {game.game_id}: {e}')
            continue

    return 'Game statuses updated successfully'

