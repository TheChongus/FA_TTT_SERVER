from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .services.create_team import register_team, check_last_game_id
from ttt_player.models import Team, Game, Move
from django.http import JsonResponse
from django.contrib import messages


# Create your views here.


#first view is the home page that will display a login form if the user is not logged in
#a register form if the user is not logged in
#or a welcome message if the user is logged in
def home(request):
    return render(request, 'player/home.html', {})

#second view is a list of games that the user is currently enrolled in
def active_games(request):
    return render(request, 'player/activegames.html', {})

#third view is the game board where the user can play the game
def currentgame(request, game_id):
    return render(request, 'player/currentgame.html', {})

#Create the view for the user registration
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registration.html', {'form': form})
    

#Create the view for the user profile
#The decorator makes it so the user must be logged in to view the profile
@login_required
def profile(request):
    teams = Team.objects.filter(player=request.user).prefetch_related('games')
    #completed_games = request.user.games.filter(status='completed')
    #in_progress_games = request.user.games.filter(status='in_progress')

    return render(request, 'player/profile.html', {'teams': teams})

#This view is for creating a team and it pulls in the create_team function from the services folder
#The if request is a post sends the request to the create_team function if the form is valid
'''
    One big catch with this logic: there's no way to know how long it will take to find an opponent, and we don't want to play against ourselves. 
    In order to avoid a me versus me game, we are going to check if there is an open game with another player.
'''
def create_team(request):
    if request.method == 'POST':

        #Get the largest game_id from the database
        last_game_id = Game.objects.latest('game_id').game_id

        # Check if the last game is still pending
        if check_last_game_id(last_game_id) == False:
            messages.error(request, 'The previous game is still pending. \nPlease wait for an opponent to join')
            return redirect('profile')

        else:
            response = register_team(request.POST['team_name'])

            #if the response is successful, create a new team object and save it to the database
            if response:
                #The response contains the game_id and secret, which is the auth key. There is no team name in the response
                team = Team(name=request.POST['team_name'], auth_key=response['secret'], player=request.user)
                team.save()
                game = Game(game_id=response['game_id'], status='Pending', player_team=team)
                game.save()

            else:
                return render(request, 'player/create_team.html', {'error': 'There was an error creating the team'})
            
            return redirect('profile')
        
        #If the method isn't a post (for some reason), just redirect back to the profile page
        return redirect('profile')

#Game Detail View
def game_detail(request, game_id, team_id):
    
    game = get_object_or_404(Game, game_id=game_id)
    player_team = get_object_or_404(Team, id=team_id)
    opponent = game.opponent

    return render(request, 'games/game.html', {'game': game, 'player_team': player_team, 'opponent': opponent})


#other views:
def game_ids(request):
    #return a dict with the key called 'games', with a list value. 
    #each item in the list is a dict with keys 'game_id'
    #filter out the games that are not in Pending status or In Progress status
    return JsonResponse({'games': [{'game_id': game.game_id} for game in Game.objects.filter(status__in=['Pending', 'In Progress'])]})