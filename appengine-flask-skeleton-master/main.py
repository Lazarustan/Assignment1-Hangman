"""`main` is the top level module for your Flask application."""

# Import the Flask Framework
from flask import Flask
from flask import render_template
from flask import request
from flask import json
from flask import session
import urllib2
from datetime import datetime

app = Flask(__name__)

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

app.secret_key = '141153L'

#This section used for keeping a bunch of arrays used throughout the web
#This also contains the "Default" value
def SessionVariables():
	session['word_to_guess'] 	= ""			#String containing answer
	session['current_correct']  = ""			#String containing correctly guessed letters
	session['wrong_guess']		= 0				#Int containing number of wrong guesses
	session['total_win']		= 0				#Int containing number of fully corrected words
	session['total_lost']		= 0				#Int containing number of times lost.
	
@app.route('/', methods=['GET'])
def home():
	SessionVariables()
	return render_template('index.html')

@app.route('/new_game', methods = ['POST'])
def new_game():
	#Call url
	request_url = urllib2.Request('http://randomword.setgetgo.com/get.php')
	#Get response from url
	urlResponse = urllib2.urlopen(request_url)
	
	letter_list   = {}										#Array of letters
	answer_string = (urlResponse.read()).upper()			#The Answer
	answer_length = len(answer_string)						#The length of the Answer
	session['word_to_guess'] = answer_string				#Put the answer in the variable container
	
	total_letters = ""										#Total blanks per letter
	for i in range (0,answer_length):						#Basically a for loop to check the total length of the word
			total_letters += "_"							#for each letter add a "_" until guessed
	
		
	session['current_correct'] = total_letters
	letter_list.update({'word_length':answer_length})
	tempString = json.dumps(letter_list)
	return tempString

@app.route('/check_letter' , methods = ['POST'])
def check_letter():

	tempVariable = json.loads(request.data)						#Load client data and stores into tempVariable
	letterGuessed = tempVariable.get('guess')					#Gets data of each letter player selects
	
	letter_array 			= list(session['word_to_guess'])	#Stores the word in letter_array
	letter_array_guesssed 	= list(session['current_correct'])	#Stores current correctly guessed letters in letter_array_guesssed
	word_length  			= len(session['word_to_guess'])		#Stores the word length in word_length
	
	wordTrue = False
	
	for i in range(0,word_length):								#Loop to check all the letters
		if letter_array[i] == letterGuessed:
			letter_array_guesssed[i] = letterGuessed			#If so make blank = that letter
		if letter_array[i] != letterGuessed:
			session['wrong_guess'] += 1
			break
		
		 
	session['current_correct'] = "".join(letter_array_guesssed)	#Combines back the list of letters	
	
	
	
	#Check if game not ended		
	if session['wrong_guess'] <= 7:
	
		#Check if ONGOING
		if session['current_correct'] != session['word_to_guess']:
		 game_state = {}
		 game_state.update({'game_state':"ONGOING"})
		 game_state.update({'word_state':session['current_correct']})
		 game_state.update({'bad_guesses':session['wrong_guess']})
		 current_game_state = json.dumps(game_state)
		#Or check if WIN
		elif session['current_correct'] == session['word_to_guess']:
		 game_state = {}
		 game_state.update({'game_state':"WIN"})
		 game_state.update({'word_state':session['current_correct']})
		 session['total_won'] += 1
		 session['wrong_guess'] = 0
		 current_game_state = json.dumps(game_state)		
		
	#If not ONGOING or WIN check for lost
	elif session['wrong_guess'] >= 8:
	 game_state = {}
	 game_state.update({'game_state':"LOSE"})
	 game_state.update({'word_state':session['current_correct']})
	 game_state.update({'bad_guesses':session['wrong_guess']})
	 session['total_lost'] += 1
	 session['wrong_guess'] = 0
	 current_game_state = json.dumps(game_state)
	
			
	return current_game_state
	
@app.route('/score' , methods = ['GET'])
def score():
	game_counter = {}
	game_counter.update({'games_won':session['total_win']})
	game_counter.update({'games_lost':session['total_lost']})
	total_score = json.dumps(game_counter)
	
	return total_score

@app.route('/score' , methods = ['DELETE'])
def delscore():
	#######################RESET EVERYTHING BACK TO DEFAULT#########################
	game_counter = {}
	game_counter.update({'games_won':0})
	game_counter.update({'games_lost':0})
	total_score = json.dumps(game_counter)
	
	return total_score
	
@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500
