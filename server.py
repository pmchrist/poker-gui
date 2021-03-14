#
#   Binds REP socket to tcp://*:1916 (because 19/16 play)
#   Server first expects message from client and then answers
#

# Import dependencies
import time
import zmq
import rlcard
import random
import os
import json
with open(os.path.join(rlcard.__path__[0], 'games/limitholdem/card2index.json'), 'r') as file:
    card2index = json.load(file)

# Environment Init
env = rlcard.make("no-limit-holdem")
env.reset()

# Server Init
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:1916")
serverUp = True

# Correct message generator
def getRequest():
    global action
    # Get Stage
    stage = str(env.game.stage.value)
    # Get Pot
    pot = str(int(env.get_state(0)["obs"][52] + env.get_state(0)["obs"][53]))
    # Get Cards
    dealer_cards = [card2index[card.get_index()] for card in env.game.public_cards]
    dealer_cards = str(dealer_cards).strip('[]')
    # Get Player Chips
    player_chips = str(env.game.players[0].remained_chips)
    # Get Player Cards
    player_cards = [card2index[card.get_index()] for card in env.game.players[0].hand]
    player_cards = str(player_cards).strip('[]')
    # Get Enemy Chips
    enemy_chips = str(env.game.players[1].remained_chips)
    # Get Enemy Cards
    enemy_cards = [card2index[card.get_index()] for card in env.game.players[1].hand]
    enemy_cards = str(enemy_cards).strip('[]')
    # Get Player Win Chance (not working now)
    playerWinChance = str(0.0)
    if env.get_player_id() == 0:
        # Get Legal Actions
        legal_actions = [action.value for action in env._get_legal_actions()]
        # Pass them to Player to choose
        legal_actions = str(legal_actions).strip('[]')
        # Creating message ending
        messageSub = "Player" + '|' + legal_actions
    if env.get_player_id() == 1:
        # Get Legal Actions
        legal_actions = [action.value for action in env._get_legal_actions()]
        # Choose Random Action
        action = random.choice(legal_actions)
        messageSub = "Enemy" + '|' + str(action)
    # Stage|Pot|DealerCards|PlayerChips|PlayerCards|EnemyChips|EnemyCards|playerWinChance|Player/Enemy|legal_actions/enemy_action
    message = stage + '|' + pot + '|' + dealer_cards + '|' + player_chips + '|' + player_cards +'|' + enemy_chips + '|' + enemy_cards + '|' + playerWinChance + '|' + messageSub
    print("Server:", message)
    # If it was Enemy's turn we should pass action to Environment
    if env.get_player_id() == 1: env.step(action)
    return(message)  

gameOver = False
busy = False

# Server should always answer, it always gets message first
while serverUp:
   
    # Busy checker
    while busy:
        time.sleep(5)
    print("-----------------")
    print("Server: New Game")

    # While Game Exists
    while not env.is_over():
        # Block Server
        busy = True

        # Wait for message, if server got any message it unfreezes
        print("-----------------")
        message = (socket.recv()).decode("utf-8")
        print ("Unity:", message)
        messageArr = message.split('|')

        # If game Starts, we just generate first message
        # (We should also set Mode and Difficulty, but currently it is inactive)
        if messageArr[0] == ("Start"):
            print("Mpainei sto Start")
            frame = getRequest()
            socket.send(bytes(frame, encoding='utf8'))

        #  Default answer of Unity, when it just updates GUI, we just continue
        if messageArr[0] == ("Gotcha"):
            print("Mpainei sto Gotcha")
            frame = getRequest()
            socket.send(bytes(frame, encoding='utf8'))
        
        # If Someone in Unity made a move, we should update Action and continue
        if (messageArr[0] == ("0") or messageArr[0] == ("1") or messageArr[0] == ("2") or messageArr[0] == ("3") or messageArr[0] == ("4") or messageArr[0] == ("5")):
            print("Mpainei sto Player Action")
            # Assign chosen action
            action = int(messageArr[0])
            # Update Action
            env.step(action)
            # Getting Next Game State
            frame = getRequest()
            socket.send(bytes(frame, encoding='utf8'))
    
    # If Game was finished correctly we must send Results
    if env.is_over():
        # Wait for message, if server got any message it unfreezes
        print("-----------------")
        message = (socket.recv()).decode("utf-8")
        print ("Unity:", message)
        messageArr = message.split('|')
        # Send Results
        end = env.get_payoffs()
        message = "End" + '|' + str(end[0]) + '|' + str(end[1])
        print("Server:", message)
        socket.send(bytes(message, encoding='utf8'))   
        # reset environment
        env.reset()
        busy = False
