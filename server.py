#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import time
import zmq

gameFlow = [
"-1|Dealer|50",
"-1|Player|25|12|67",
"-1|Enemy|35|10|127",
"0|Enemy|3|256|78",
"0|PlayerRequest|0,1,3,4|0.65",
"0|Player|0.65|28|305",
"1|Dealer|49|5|10|84",
"1|PlayerRequest|0,1,3,4,5|0.4",
"1|Player|0.29|405|105",
"1|Enemy|4|21|25",
"2|Dealer|35|17",
"2|Enemy|2|31|25",
"2|PlayerRequest|0,3,5|0.8",
"2|Player|0.5|23|23",
"3|Dealer|3|33",
"3|PlayerRequest|0,1,3,4|0.35",
"3|Player|1.0|29|45",
"3|Enemy|4|36|45",
"End|Player"
]

# Some Init
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
serverUp = True

# Server should always answer, it always gets message first
while serverUp:
    # Used to parse string list with example game flow
    messageID = 0
    gameOver = False
    messageID = 0
    while not gameOver:
        
        # Wait for message
        # If server got any message it unfreezes,
        # in reality we should check message,
        # do something with information and then unfreeze
        # not just print it, at this point first message have some information others are just "Gotcha"
        message = socket.recv()
        print (message)

        # If player exited game before legit end
        if message == (b"Abort"):
            gameOver = True
            socket.send(b"Bye")

        #  Default answer of Unity, when it just updates gui
        if message == (b"Gotcha"):
            frame = bytes(gameFlow[messageID], 'utf-8')
            socket.send(frame)
            messageID = messageID + 1

        # When game starts, in demo we just send message
        if message == (b"Start|Mode|Difficulty"):
            frame = bytes(gameFlow[messageID], 'utf-8')
            socket.send(frame)
            messageID = messageID + 1

        # Possible Player actions, in demo we do the same as with standart Gotcha
        if message == (b"0") or message == (b"1") or message == (b"2") or message == (b"3") or message == (b"4"):
            frame = bytes(gameFlow[messageID], 'utf-8')
            socket.send(frame)
            messageID = messageID + 1


# Peiramathse opos to vlepeis na tairiaksei, den ksero polla gia to pos trexei, alla trexei
