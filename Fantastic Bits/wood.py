import sys
import math

def distance(p1, p2):
    return math.hypot(p2[0]-p1[0], p2[1]-p1[1])

# Grab Snaffles and try to throw them through the opponent's goal!
# Move towards a Snaffle and use your team id to determine where you need to throw it.

my_team_id = int(raw_input())  # if 0 you need to score on the right of the map, if 1 you need to score on the left
if my_team_id:
    goal = "0 4500"
else:
    goal = "16000 4500"

class simulation
# game loop
while True:
    discs = list()
    wizards = list()
    opponents = list()
    entities = int(raw_input())  # number of entities still in game
    for i in xrange(entities):
        # entity_id: entity identifier
        # entity_type: "WIZARD", "OPPONENT_WIZARD" or "SNAFFLE" (or "BLUDGER" after first league)
        # x: position
        # y: position
        # vx: velocity
        # vy: velocity
        # state: 1 if the wizard is holding a Snaffle, 0 otherwise
        entity_id, entity_type, x, y, vx, vy, state = raw_input().split()
        values = ( int(entity_id), (int(x), int(y)), int(vx), int(vy), int(state) )
        if entity_type == 'WIZARD':
            wizards.append( values )
        elif entity_type == 'OPPONENT_WIZARD':
            opponents.append( values )
        elif entity_type == 'SNAFFLE':
            discs.append( values )
        
    for wizz in wizards:
        if wizz[4]:
            print "THROW " + goal + " 500"
        else:
            dists = [distance(wizz[1], disc[1]) for disc in discs]
            coords = discs[ dists.index(min(dists)) ][1]
            print "MOVE %s %s 150" % (str(coords[0]), str(coords[1]))
