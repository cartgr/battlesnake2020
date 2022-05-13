import json
import os
import random
import bottle

from api import ping_response, start_response, move_response, end_response


@bottle.route('/')
def index():
    return


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.get('/')
def get():
    return {
        "apiversion": "1",
        "author" : "bartercud",
        "color": "#ff00c7",
        "head" : "bendr",
        "tail": "round-bum"
    }


@bottle.post('/move')
def move():
    data = bottle.request.json
     # print(json.dumps(data))

     #collect board info
    boardsize = data['board']['height']
    food = []
    for f in data['board']['food']:
         foodtuple = (int(f['x']), int(f['y']))
         food.append(foodtuple)

    #collect my info
    me = data['you']
    body = []
    for b in me['body']:
        bodytuple = (int(b['x']), int(b['y']))
        body.append(bodytuple)
    myhead = body[0]
    mytail = body[-1]
    mysize = len(body)
    myhealth = me['health']

    #collect others info
    othersnakes = data["board"]["snakes"]
    # for s in othersnakes:


    #Make a move
    validmoves = []
    foodmoves = []
    wallsafemoves = []
    othersnakebodysafemoves = []
    othersnakeheadsafemoves = []
    selfsafemoves = []
    tmpmoves = []
    openmoves = []
    finalmoves = []
    linemoves = []
    linevalidmoves = []
    foodlinevalidmoves = []


    print("calling time_to_eat")
    time_to_eat(food, myhead, foodmoves)
    print("foodmoves 1")
    print(foodmoves)
    wall_detection(boardsize, myhead, wallsafemoves)
    snake_body_detection(myhead, othersnakebodysafemoves, othersnakes)
    snake_head_detection(myhead, othersnakeheadsafemoves, othersnakes)
    self_check(myhead, body, selfsafemoves)
    check_open(othersnakes, myhead, openmoves, boardsize)
    check_last(me, myhead, linemoves)


    if ("left" in wallsafemoves) and ("left" in othersnakebodysafemoves) and ("left" in othersnakeheadsafemoves) and ("left" in selfsafemoves):
        validmoves.append("left")
    if ("right" in wallsafemoves) and ("right" in othersnakebodysafemoves) and ("right" in othersnakeheadsafemoves) and ("right" in selfsafemoves):
        validmoves.append("right")
    if ("up" in wallsafemoves) and ("up" in othersnakebodysafemoves) and ("up" in othersnakeheadsafemoves) and ("up" in selfsafemoves):
        validmoves.append("up")
    if ("down" in wallsafemoves) and ("down" in othersnakebodysafemoves) and ("down" in othersnakeheadsafemoves) and ("down" in selfsafemoves):
        validmoves.append("down")

    if ("left" in validmoves) and ("left" in linemoves):
        linevalidmoves.append('left')
    if ("right" in validmoves) and ("right" in linemoves):
        linevalidmoves.append('right')
    if ("up" in validmoves) and ("up" in linemoves):
        linevalidmoves.append('up')
    if ("down" in validmoves) and ("down" in linemoves):
        linevalidmoves.append('down')

    if me['health'] < 10:

        if ("left" in foodmoves) and ("left" in validmoves):
            tmpmoves.append("left")
        if ("right" in foodmoves) and ("right" in validmoves):
            tmpmoves.append("right")
        if ("up" in foodmoves) and ("up" in validmoves):
            tmpmoves.append("up")
        if ("down" in foodmoves) and ("down" in validmoves):
            tmpmoves.append("down")

        if ("left" in foodmoves) and ("left" in linevalidmoves):
            foodlinevalidmoves.append("left")
        if ("right" in foodmoves) and ("right" in linevalidmoves):
            foodlinevalidmoves.append("right")
        if ("up" in foodmoves) and ("up" in linevalidmoves):
            foodlinevalidmoves.append("up")
        if ("down" in foodmoves) and ("down" in linevalidmoves):
            foodlinevalidmoves.append("down")

    masterlist = []

    if (len(foodlinevalidmoves) != 0):
        masterlist.append("foodlinevalidmoves")
    if (len(tmpmoves) != 0):
        masterlist.append("tmpmoves")
    if (len(linevalidmoves) != 0):
        masterlist.append("linevalidmoves")
    if (len(validmoves) != 0):
        masterlist.append("validmoves")

    if ("validmoves" in masterlist):
        finalmoves = validmoves
    if ("linevalidmoves" in masterlist):
        finalmoves = linevalidmoves
    if ("tmpmoves" in masterlist):
        finalmoves = tmpmoves
    if ("foodlinevalidmoves" in masterlist):
        finalmoves = foodlinevalidmoves
    if (len(masterlist) == 0):
        finalmoves = openmoves

    try:
        direction = random.choice(finalmoves)
        return move_response(direction)
    except IndexError:
        dead = "right"
        return move_response(dead)

def time_to_eat(food, myhead, foodmoves):
    closestfoodindex = nearest_food(myhead, food)
    thefood = food[closestfoodindex]
    if ((thefood[0] - myhead[0])< 0):
        foodmoves.append("left")
    if ((thefood[0] - myhead[0]) > 0):
        foodmoves.append("right")
    if ((thefood[1] - myhead[1]) < 0):
        foodmoves.append("down")
    if ((thefood[1] - myhead[1])>0):
        foodmoves.append("up")




def nearest_food(myhead, food):
    smallestdist = None
    count = 0
    closestfoodindex = 0
    for f in food:
        myxdist = f[0] - myhead[0]
        myydist = f[1] - myhead[1]
        mydist = ((myxdist)**2 + (myydist**2))**(1/2)
        if (mydist< smallestdist):
            smallestdist = mydist
            closestfoodindex = count
        count += 1
    return closestfoodindex


# def is_other_closer(othersnakes, myhead, food):
#     closestfoodindex = nearest_food(myhead, food)
#     result = False
#     for s in othersnakes:
#         head = s['body'][0]
#         otherxdist = food[closestfoodindex][0] - head["x"]
#         otherydist = food[closestfoodindex][1] - head["y"]
#         otherdist = ((otherxdist)**2 + (otherydist**2))**(1/2)
#         if (otherdist < smallestdist):
#             result = True
#
#     return result

def wall_detection(boardsize, myhead, wallsafemoves):
    if (myhead[0] != 0):
        wallsafemoves.append('left')
    if (myhead[0] != boardsize-1):
        wallsafemoves.append('right')
    if (myhead[1] != 0):
        wallsafemoves.append('down')
    if (myhead[1] != boardsize-1):
        wallsafemoves.append('up')

def snake_body_detection(myhead, othersnakebodysafemoves, othersnakes):
    xleftcount = 0
    xrightcount = 0
    yupcount = 0
    ydowncount = 0
    for s in othersnakes:
        for b in s['body']:
            if (((b['x']) == myhead[0]+1) and (b['y'] == myhead[1])):
                xrightcount += 1
            if (((b['x']) == myhead[0]-1) and (b['y'] == myhead[1])):
                xleftcount += 1
            if (((b['y']) == myhead[1]-1) and (b['x'] == myhead[0])):
                ydowncount += 1
            if (((b['y']) == myhead[1]+1) and (b['x'] == myhead[0])):
                yupcount += 1
    if (xleftcount == 0):
        othersnakebodysafemoves.append('left')
    if (xrightcount == 0):
        othersnakebodysafemoves.append('right')
    if (yupcount == 0):
        othersnakebodysafemoves.append('up')
    if (ydowncount == 0):
        othersnakebodysafemoves.append('down')



def snake_head_detection(myhead, othersnakeheadsafemoves, othersnakes):
    xleftcount = 0
    xrightcount = 0
    yupcount = 0
    ydowncount = 0
    for s in othersnakes:
        if ((s['body'][0]['x'] == myhead[0]-1) and (s['body'][0]['y'] == myhead[1]+1)):
            xleftcount += 1
            yupcount += 1
        if ((s['body'][0]['x'] == myhead[0]-1) and (s['body'][0]['y'] == myhead[1])):
            xleftcount += 1
        if ((s['body'][0]['x'] == myhead[0]-2) and (s['body'][0]['y'] == myhead[1])):
            xleftcount += 1
        if ((s['body'][0]['x'] == myhead[0]-1) and (s['body'][0]['y'] == myhead[1]-1)):
            xleftcount += 1
            ydowncount += 1
        if ((s['body'][0]['x'] == myhead[0]) and (s['body'][0]['y'] == myhead[1]-1)):
            ydowncount += 1
        if ((s['body'][0]['x'] == myhead[0]) and (s['body'][0]['y'] == myhead[1]-2)):
            ydowncount += 1
        if ((s['body'][0]['x'] == myhead[0]+1) and (s['body'][0]['y'] == myhead[1]-1)):
            ydowncount += 1
            xrightcount += 1
        if ((s['body'][0]['x'] == myhead[0]+1) and (s['body'][0]['y'] == myhead[1])):
            xrightcount += 1
        if ((s['body'][0]['x'] == myhead[0]+2) and (s['body'][0]['y'] == myhead[1])):
            xrightcount += 1
        if ((s['body'][0]['x'] == myhead[0]+1) and (s['body'][0]['y'] == myhead[1]+1)):
            xrightcount += 1
            yupcount += 1
        if ((s['body'][0]['x'] == myhead[0]) and (s['body'][0]['y'] == myhead[1]+1)):
            yupcount += 1
        if ((s['body'][0]['x'] == myhead[0]) and (s['body'][0]['y'] == myhead[1]+2)):
            yupcount += 1

    if (xleftcount == 0):
        othersnakeheadsafemoves.append('left')
    if (xrightcount == 0):
        othersnakeheadsafemoves.append('right')
    if (yupcount == 0):
        othersnakeheadsafemoves.append('up')
    if (ydowncount == 0):
        othersnakeheadsafemoves.append('down')

def self_check(myhead, body, selfsafemoves):
    xleftcount = 0
    xrightcount = 0
    yupcount = 0
    ydowncount = 0
    for b in body:
        if (b[0] == myhead[0]) and (b[1] == myhead[1]-1):
            ydowncount += 1
        if (b[0] == myhead[0]) and (b[1] == myhead[1]+1):
            yupcount += 1
        if (b[0] == myhead[0]-1) and (b[1] == myhead[1]):
            xleftcount += 1
        if (b[0] == myhead[0]+1) and (b[1] == myhead[1]):
            xrightcount += 1
    if (xleftcount == 0):
        selfsafemoves.append('left')
    if (xrightcount == 0):
        selfsafemoves.append('right')
    if (yupcount == 0):
        selfsafemoves.append('up')
    if (ydowncount == 0):
        selfsafemoves.append('down')

def check_open(othersnakes, myhead, openmoves, boardsize):
    xleftcount = 0
    xrightcount = 0
    yupcount = 0
    ydowncount = 0
    if (myhead[0] == 0):
        xleftcount += 1
    if (myhead[0] == boardsize-1):
        xrightcount += 1
    if (myhead[1] == 0):
        ydowncount += 1
    if (myhead[1] == boardsize-1):
        yupcount += 1
    for s in othersnakes:
        for b in s['body']:
            if (((b['x']) == myhead[0]+1) and (b['y'] == myhead[1])):
                xrightcount += 1
            if (((b['x']) == myhead[0]-1) and (b['y'] == myhead[1])):
                xleftcount += 1
            if (((b['y']) == myhead[1]-1) and (b['x'] == myhead[0])):
                ydowncount += 1
            if (((b['y']) == myhead[1]+1) and (b['x'] == myhead[0])):
                yupcount += 1
    if (xleftcount == 0):
        openmoves.append('left')
    if (xrightcount == 0):
        openmoves.append('right')
    if (yupcount == 0):
        openmoves.append('up')
    if (ydowncount == 0):
        openmoves.append('down')

def check_last(me, myhead, linemoves):
    neck = me['body'][1]
    if ((neck['x'] == myhead[0]) and (neck['y']) == myhead[1] + 1):
        linemoves.append('down')
    if ((neck['x'] == myhead[0]) and (neck['y']) == myhead[1] - 1):
        linemoves.append('up')
    if ((neck['x'] == myhead[0] + 1) and (neck['y']) == myhead[1]):
        linemoves.append('left')
    if ((neck['x'] == myhead[0] - 1) and (neck['y']) == myhead[1]):
        linemoves.append('right')





@bottle.post('/end')
def end():
    data = bottle.request.json
    # print(json.dumps(data))

    return end_response()


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
