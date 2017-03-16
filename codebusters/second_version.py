import sys
import math

def distance(p1, p2):
    return math.hypot(p2[0]-p1[0], p2[1]-p1[1])
  
def next_point(p1, p2, dist):
    if p1 == p2:
        p1 = (p1[0]+1, p1[1])
    v = (p1[0]-p2[0], p1[1]-p2[1])
    sq = math.sqrt(v[0]**2+v[1]**2)
    return (p1[0]-dist*v[0]/sq, p1[1]-dist*v[1]/sq)

def move_to_ghost(p1, p2):
    dist = distance(p1, p2)
    if dist > 1760:
        return next_point(p1, p2, 800)
    else:
        return next_point(p1, p2, dist-901)

def move_away(p1, p2):
    return next_point(p1, p2, -800)

def get_area(p):
    return p[1]/3001*2+1+p[0]/8001
        
class scout:

    def __init__(self, area):
        self.initial = True
        self.area = area
        if self.area > 2:
            self.area = 1
            
    def setcoords(self, x, y):
        self.x = x
        self.y = y
        self.pos = (self.x, self.y)
        
    def initialscout(self):
        if not base:
            #My watch has ended
            if self.x > 13000 and self.y > 6000:
                self.initial = False
            elif self.x > 13000:
                print "MOVE 14000 7000"
                return
            if self.area == 0:      
                if self.y != 1500:
                    print "MOVE "+str(int(self.x+math.sqrt(abs(799**2 - (self.y-1500)**2))))+" 1500"
                else:
                    print "MOVE 16000 1500"
            elif self.area == 1:
                if self.x > 10500:
                    self.initial = False
                if self.y != 4500:
                    print "MOVE "+str(int(self.x+math.sqrt(abs(799**2 - (self.y-4500)**2))))+" 4500"
                else:
                    print "MOVE 16000 4500"
            elif self.area == 2:
                if self.y != 7500:
                    print "MOVE "+str(int(self.x+math.sqrt(abs(799**2 - (self.y-7500)**2))))+" 7500"
                else:
                    print "MOVE 16000 7500"
        else:
            #My watch has ended
            if self.x < 3000 and self.y < 3000:
                self.initial = False
            elif self.x < 3000:
                print "MOVE 2000 2000"
                return
            if self.area == 0:      
                if self.y != 7500:
                    print "MOVE "+str(int(self.x+math.sqrt(abs(799**2 - (self.y-7500)**2))))+" 7500"
                else:
                    print "MOVE 0 7500"
            elif self.area == 1:
                if self.x < 5500:
                    self.initial = False
                if self.y != 4500:
                    print "MOVE "+str(int(self.x+math.sqrt(abs(799**2 - (self.y-4500)**2))))+" 4500"
                else:
                    print "MOVE 0 4500"
            elif self.area == 2:
                if self.y != 1500:
                    print "MOVE "+str(int(self.x+math.sqrt(abs(799**2 - (self.y-1500)**2))))+" 1500"
                else:
                    print "MOVE 0 1500"

    def stun(self):
        
        for buster in oppbust:
            if distance( self.pos, (oppbust[buster]['x'],oppbust[buster]['y']) ) < 1761:
                print >> sys.stderr, self.pos, (oppbust[buster]['x'],oppbust[buster]['y']), distance( self.pos, (oppbust[buster]['x'],oppbust[buster]['y']) )
                if oppbust[buster]['state'] == 2 and oppbust[buster]['value'] > 1:
                    continue
                else:
                    print "STUN " + buster
                    return 1
        return 0
    
    def decision(self):
        
        if self.initial:
            self.initialscout()
            if self.initial:
                return 0
            else:
                return 1

class thief:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.pos = (self.x, self.y)

    def move(self):
        if base:
            print "MOVE 1395 784"
        else:
            print "MOVE 14605 7216"
            
    def steal(self):
        for buster in oppbust:
            if distance( self.pos, (oppbust[buster]['x'],oppbust[buster]['y']) ) < 2201:
                if oppbust[buster]['state'] == 1:
                    print "STUN " + buster
                    break

    def trap(self):
        for ghost in ghosts:
            dist = distance( self.pos, (ghosts[ghost]['x'],ghosts[ghost]['y']) )
            if dist < 2201:
                if dist < 1761 and dist > 899:
                    print "BUST " + ghost
                    break
                else:
                    move = move_to_ghost( self.pos, (ghosts[ghost]['x'],ghosts[ghost]['y']) )
                    print "MOVE " + str(int(move[0])) + " " +str(int(move[1]))
                    break

    def home(self):
        if base:
            if distance(self.pos, (0,0)) < 1601:
                print "RELEASE"
            else:
                print "MOVE 16000 9000"
        else:
            if distance(self.pos, (16000, 9000)) < 1601:
                print "RELEASE"
            else:
                print "MOVE 0 0"

class collector:
    
    def __init__(self):
        self.targetarea = 0
        self.targetstamina = 0
        self.destination = (0, 0)
        self.stuncd = 0
        self.ghostid = 999
        self.emergency = False
        self.areas = [ [(2000, 1500), (6200, 1500)], [(9800, 1500), (14500, 1500)], [(2000, 4500), (6200, 4500)],
                  [(9800, 4500), (14500, 4500)], [(2000, 7500), (6200, 7500)], [(9800, 7500), (14500, 7500)]]

    def setcoords(self, x, y, state, value):
        self.x = x
        self.y = y
        self.pos = (self.x, self.y)
        self.state = state
        self.value = value
        self.stuncd -= 1

    def move_to_target(self, target):
        targetarea = ghosts[target]['area']-1
        distances = [distance(self.pos, self.areas[targetarea][0]), distance(self.pos, self.areas[targetarea][1])]
        if self.y != self.areas[targetarea][0][1]:
            point = self.areas[targetarea][ distances.index(min(distances)) ]
            self.destination = self.areas[targetarea][ distances.index(max(distances)) ]
            print "MOVE " + str(point[0]) + " " + str(point[1]) + " 1"
        elif self.x == self.destination[0]:
            try:
                del ghosts[target]
            except:
                pass
            point = self.destination
            print "MOVE " + str(point[0]) + " " + str(point[1]+100) + " 2"
        else:
            point = self.destination
            print "MOVE " + str(point[0]) + " " + str(point[1]) + " 3"

    def trap_ghost(self, target):

        if target in currentghosts:
            dist = distance( self.pos, (currentghosts[target]['x'],currentghosts[target]['y']) )
            if dist < 2201:
                if self.state == 3 and self.value == int(target):
                    #Only one opponent - go for the steal
                    if currentghosts[target]['value'] == 2 and currentghosts[target]['stamina'] < 4:
                        if self.stun(True):
                            return 1
                        print "MOVE " + str(currentghosts[target]['x']) + " " + str(currentghosts[target]['y'])+ " 4"
                        return 1
                    
                elif currentghosts[target]['value'] == 1 and currentghosts[target]['stamina'] < 4:
                    #One guy trying to take a ghost
                    if self.stun(True):
                        return 1
                    print "MOVE " + str(currentghosts[target]['x']) + " " + str(currentghosts[target]['y']) + " 5"
                    return 1

                if dist < 1761 and dist > 899:
                    print "BUST " + target + " 6"
                    return 1
                else:
                    move = move_to_ghost( self.pos, (currentghosts[target]['x'],currentghosts[target]['y']) )
                    print "MOVE " + str(int(move[0])) + " " +str(int(move[1])) + " 7"
                    return 1
        return 0
    
    def stun(self, steal):
        for buster in oppbust:
            if not steal:
                if distance( self.pos, (oppbust[buster]['x'],oppbust[buster]['y']) ) < 1761 and self.stuncd < 1:
                    if oppbust[buster]['state'] == 2 and oppbust[buster]['value'] > 3 or oppbust[buster]['state'] == 3:
                        continue
                    else:
                        print "STUN " + buster
                        self.stuncd = 20
                        return 1
            else:
                if distance( self.pos, (oppbust[buster]['x'],oppbust[buster]['y']) ) < 1761 and self.stuncd < 1:
                    if oppbust[buster]['state'] == 3:
                        print "STUN " + buster
                        self.stuncd = 20
                        return 1
        return 0

    def home(self, target):
        if (distance( self.pos, (0,0) ) < 3000 or distance( self.pos, (16000, 9000) ) < 3000) and target == 113:
            if not self.stun(False):
                if base:
                    if distance(self.pos, (16000,9000)) < 1601:
                        print "RELEASE"
                    else:
                        print "MOVE 16000 9000"
                else:
                    if distance(self.pos, (0, 0)) < 1601:
                        print "RELEASE"
                    else:
                        print "MOVE 0 0"
        else:
            for buster in oppbust:
                if distance( self.pos, (oppbust[buster]['x'],oppbust[buster]['y']) ) < 2200 and oppbust[buster]['state'] != 2:
                    self.emergency = True
                    self.emergencypoint = (oppbust[buster]['x'],oppbust[buster]['y'])
                    move = move_away( self.pos, (oppbust[buster]['x'],oppbust[buster]['y']) )
                    print "MOVE " + str(int(move[0])) + " " +str(int(move[1])) + " 7"
                    return
            if base:
                if distance(self.pos, (16000,9000)) < 1601:
                    print "RELEASE"
                    self.emergency = False
                elif self.emergency and self.y < 8500:
                    print "MOVE "+str(self.x)+" 9000"    
                else:
                    print "MOVE 16000 9000"
            else:
                if distance(self.pos, (0, 0)) < 1601:
                    print "RELEASE"
                    self.emergency = False
                elif self.emergency and self.y > 500:
                    print "MOVE "+str(self.x)+" 0"
                else:
                    print "MOVE 0 0"
                
    def decision(self, target):
        if target == 112 or target == 113:
            self.home(target)
            return
        
        if self.stun(False):
            return

        if target == 999:
            if not base:
                print "MOVE 14400 7400"
            else:
                print "MOVE 1600 1600"
            return
 
        if not self.trap_ghost(target):
            self.move_to_target(target)

class hivemind:

    def __init__(self, bc, gc, base):
        self.bc = bc
        self.gc = gc
        self.base = base
        self.pretargets = [0 for i in range(bc)]
        self.objects = [collector() for i in range(bc)]
        self.classes = ['collector' for i in range(bc)]
        self.areas = [ [(2000, 1500), (6200, 1500)], [(9800, 1500), (14500, 1500)], [(2000, 4500), (6200, 4500)],
                  [(9800, 4500), (14500, 4500)], [(2000, 7500), (6200, 7500)], [(9800, 7500), (14500, 7500)]]
        if base:
            self.bonus = bc
        else:
            self.bonus = 0
        self.initialization = True

    def initialize(self):
        self.initialization = False
        positions = [self.busters[i]['y'] for i in self.busters]
        if not base:
            for i in self.busters:
                if self.busters[i]['y'] == min(positions):
                    self.objects[int(i)] = scout(0)
                    self.classes[int(i)] = 'scout'
                elif self.busters[i]['y'] == max(positions):
                    self.objects[int(i)] = scout(1)
                    self.classes[int(i)] = 'scout'
        else:
            for i in self.busters:
                if self.busters[i]['y'] == max(positions):
                    self.objects[int(i)-self.bonus] = scout(0)
                    self.classes[int(i)-self.bonus] = 'scout'
                elif self.busters[i]['y'] == min(positions):
                    self.objects[int(i)-self.bonus] = scout(1)
                    self.classes[int(i)-self.bonus] = 'scout'

    def collectdata(self, busters, ghosts, oppbusters):
        self.busters = busters
        self.ghosts = ghosts
        self.oppbusters = oppbusters
        if self.initialization:
            self.initialize()

    def collector_targets(self):
        targets = [0 if self.classes[i] == 'collector' else -1 for i in range(self.bc)]

        dist_to_home = [5.0, 15.0, 7.0, 16.0, 10.0, 17.0]
        if base:
            dist_to_home = list(reversed(dist_to_home))

        while 0 in targets:
            for i in range(bc):
                if targets[i] != 0:
                    continue
                if self.busters[str(i+self.bonus)]['state'] == 1:
                    targets[i] = 112
                    continue
                position = (self.busters[str(i+self.bonus)]['x'], self.busters[str(i+self.bonus)]['y'])
                area_distances = [min(distance(position, area[0])//800, distance(position, area[1])//800) for area in self.areas]
                bestturns = 999
                ghostid = 999
                ghosts_unavaileble = list()

                for ghost in ghosts:
                    area = ghosts[ghost]['area']-1
                    turns = area_distances[area] + dist_to_home[area] + ghosts[ghost]['stamina']
                    if turns < bestturns:
                        if self.busters[str(i+self.bonus)]['state'] == 3 and self.busters[str(i+self.bonus)]['value'] == int(ghost) and ghosts[ghost]['value'] > 2:
                            ghosts_unavaileble.append(ghost)
                            continue
                        if self.busters[str(i+self.bonus)]['state'] != 3 and ghosts[ghost]['value'] > 1 or self.busters[str(i+self.bonus)]['state'] == 3 and self.busters[str(i+self.bonus)]['value'] != int(ghost) and ghosts[ghost]['value'] > 1:
                            #More than one guy, let it go
                            ghosts_unavaileble.append(ghost)
                            continue
                        elif ghosts[ghost]['value'] > 2:
                            ghosts_unavaileble.append(ghost)
                            continue
                        
                        if ghost in targets:
                            if distance( (self.busters[str(targets.index(ghost)+self.bonus)]['x'], self.busters[str(targets.index(ghost)+self.bonus)]['y']), (ghosts[ghost]['x'], ghosts[ghost]['y']) ) > \
                            distance( position, (ghosts[ghost]['x'], ghosts[ghost]['y']) )+300:
                                targets[targets.index(ghost)] = 0
                            else:
                                continue
                        bestturns = turns
                        ghostid = ghost
                for x in list(set(ghosts_unavaileble)):
                    del ghosts[x]
                targets[i] = ghostid
        return targets

    def checktargets(self, targets):
        for a in range(len(targets)-1):
            for b in range(a+1, len(targets)):
                if targets[a] == self.pretargets[b] and targets[b] == self.pretargets[a]:
                    targets[a], targets[b] = targets[b], targets[a]
                    return targets
        return targets
        
    def command(self):
        global iniscout
        targets = self.collector_targets()
        targets = self.checktargets(targets)
        if targets.count(112) > 1:
            targets = [i if i != 112 else 113 for i in targets]
        print >> sys.stderr, targets
        self.pretargets = targets
        if 'scout' not in self.classes:
            iniscout = False
        
        for i in range(bc):
            if self.classes[int(i)] == 'scout':
                self.objects[int(i)].setcoords(self.busters[str(i+self.bonus)]['x'], self.busters[str(i+self.bonus)]['y'])
                if self.objects[int(i)].decision():
                    self.objects[int(i)] = collector()
                    self.classes[int(i)] = 'collector'
            elif self.classes[int(i)] == 'collector':
                self.objects[int(i)].setcoords(self.busters[str(i+self.bonus)]['x'], self.busters[str(i+self.bonus)]['y'], self.busters[str(i+self.bonus)]['state'], self.busters[str(i+self.bonus)]['value'])
                self.objects[int(i)].decision(targets[int(i)])

    


bc = int(raw_input())  # the amount of busters you control
ghost_count = int(raw_input())  # the amount of ghosts on the map
base = int(raw_input())  # if this is 0, your base is on the top left of the map, if it is one, on the bottom right

# game loop
ghosts = dict()
busters = dict()
hivemind = hivemind(bc, ghost_count, base)
stuncd = [0 for i in range(bc)]
iniscout = True

while True:
    currentghosts = dict()
    oppbust = dict()
    entities = int(raw_input())  # the number of busters and ghosts visible to you
    for i in xrange(entities):
        Id, x, y, Type, state, value = [int(j) for j in raw_input().split()]
        if Type == base:
            busters[str(Id)] = {'id':Id, 'x':x,'y':y,'state':state,'value':value}
            if state == 1 and str(value) in ghosts:
                del ghosts[str(value)]
        elif Type == -1:
            numpsawe = [1,2,3,4,5,6]
            thisarea = get_area((x,y))
            oppoarea = numpsawe[thisarea*-1]
            if str(Id) and str(Id+1) not in ghosts and Id < ghost_count and iniscout:
                ghosts[str(Id+1)] = {'x':x,'y':y, 'stamina':state, 'value':value, 'area':oppoarea}
            ghosts[str(Id)] = {'x':x,'y':y, 'stamina':state, 'value':value, 'area':thisarea}
            currentghosts[str(Id)] = {'x':x,'y':y, 'stamina':state, 'value':value, 'area':thisarea, 'targeted':False}
        else:
            oppbust[str(Id)] = {'id':Id, 'x':x,'y':y,'state':state,'value':value}
            if state == 1 and str(value) in ghosts:
                del ghosts[str(value)]

    hivemind.collectdata(busters, ghosts, oppbust)
    hivemind.command()

    
