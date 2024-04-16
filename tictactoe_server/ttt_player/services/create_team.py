from django.shortcuts import render, redirect
import requests

def register_team(team_name):
    
    params = {'team_name': team_name}

    #send a request to the game server to create a team
    response = requests.get('https://xo.fullyaccountable.com/game/register', params=params)

    #if the request was successful, return the team name and auth key
    if response.status_code == 200:
        return response.json()
    

def check_last_game_id(last_game_id=None):
    
    #send a request to the server to get the status of the game with the latest id
    #if the game is 'Pending', show a message that the previous game is still waiting for an opponent and a new game cannot be created
    #any other status, create a new game
    try:
        r = requests.get(f'https://xo.fullyaccountable.com/game/{last_game_id}/status')

        if r.status_code == 200 and r.json()['status'] == 'Pending':
            return False
        else:
            return True

    except Exception as e:
        print(f'Error getting game status: {e}')
        return False
    
