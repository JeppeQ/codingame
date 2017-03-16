from __future__ import division
import sys
import numpy as np
import math
import random
from heapq import nsmallest

def distance(p1, p2):
    return math.hypot(p2[0]-p1[0], p2[1]-p1[1])

class simulation:

    def __init__(self, my_id, goal):
        #0:Id, 1:Type, 2:x, 3:y, 4:vx, 5:vy, 6:state, 7:end_pos, 8:radius, 9:mass, 10:grabcd
        self.my_id = my_id
        self.poles = [[500, "pole", 0, 1750, 0, 0, 0, 0, 300, 9999999, 0],
                      [500, "pole", 0, 5750, 0, 0, 0, 0, 300, 9999999, 0],
                      [500, "pole", 16000, 1750, 0, 0, 0, 0, 300, 9999999, 0],
                      [500, "pole", 16000, 5750, 0, 0, 0, 0, 300, 9999999, 0]]
        self.goal = goal
        self.score = 0
        self.activespells = list()
        self.manapoints = 0

    def new_entities(self, entities):
        self.entities = entities
        self.manapoints += 1
        self.snaffles = [i for i in self.entities if i[1] == 'SNAFFLE']
        self.wizards = [i for i in self.entities if 'WIZARD' in i[1]]
        self.bludgers = [i for i in self.entities if 'BLUDGER' in i[1]]
        for snaff in self.snaffles:
            snaff[10] = self.check_grabbed(snaff)
    
    def check_grabbed(self, snaff):
        for wiz in self.wizards:
            if snaff[2:4] == wiz[2:4] and wiz[6]:
                return 10
        return 0
        
    def update_entities(self, actions):
        self.apply_spells()
        self.bludger_target()
        for action in actions:
            self.action(action[0], action[1])
            
        self.end_positions()
        for t in range(0, 20):
            for e in self.entities:
                e[2], e[3] = self.new_position(e, t)
            self.check_collision()
            
        self.next_round()

    def end_positions(self):
        for e in self.entities:
            e[7] = (e[2]+e[4], e[3]+e[5])

    def new_position(self, e, t):
        xlen = e[7][0]-e[2]
        ylen = e[7][1]-e[3]
        return round(e[2] + xlen/(20-t)), round(e[3] + ylen/(20-t))

    def next_round(self):
        for wizard in self.wizards:
            wizard[10] -= 1
            for snaff in self.snaffles:
                if snaff[10]-1 == wizard[0]:
                    snaff[2], snaff[3], snaff[4], snaff[5] = wizard[2], wizard[3], wizard[4], wizard[5]
            
        for e in self.entities:
            if 'WIZARD' in e[1] or 'SNAFFLE' in e[1]:
                e[4] = round(e[4]*0.75)
                e[5] = round(e[5]*0.75)
            elif 'BLUDGER' in e[1]:
                e[4] = round(e[4]*0.9)
                e[5] = round(e[5]*0.9)

    def apply_spells(self):
        #wizz, type, target, duration
        for i in self.activespells:
            for e in self.entities:
                if i[2] == e[0]:
                    if e[10] == "g":
                        self.activespells.remove(i)
                        break
                    break

        for obli in [s for s in self.activespells if s[1] == 'OBLIVIATE']:
            for e in self.entities:
                if e[0] == obli[2]:
                    e[6] = obli[0][1]
                    break
                
        for petr in [s for s in self.activespells if s[1] == 'PETRIFICUS']:
            for e in self.entities:
                if e[0] == petr[2]:
                    e[4] = 0
                    e[5] = 0
                    break
  
        for accio in [s for s in self.activespells if s[1] == 'ACCIO']:
            if accio[0][6]:
                self.activespells.remove( accio )
                continue
            
            for e in self.entities:
                if e[0] == accio[2]:
                    power = min(3000/(distance( (e[2], e[3]), (accio[0][2], accio[0][3]) )/1000)**2, 1000)
                    speed = self.thrustvector( e[2], e[3], accio[0][2], accio[0][3], power, e[9] )
                    e[4] += speed[0]
                    e[5] += speed[1]
                    break

        for flip in [s for s in self.activespells if s[1] == 'FLIPENDO']:
            for e in self.entities:
                if e[0] == flip[2]:
                    power = min(6000/(distance( (e[2], e[3]), (flip[0][2], flip[0][3]) )/1000)**2, 1000)
                    speed = self.thrustvector( flip[0][2], flip[0][3], e[2], e[3], power, e[9] )
                    e[4] += speed[0]
                    e[5] += speed[1]
                    break

        for i in self.activespells:
            i[3] -= 1
        self.activespells = [i for i in self.activespells if i[3] > 0]
                
                
    def thrustvector(self, x1, y1, x2, y2, thrust, mass):
        v = np.array( (x2-x1, y2-y1) )
        l = np.linalg.norm(v)
        vn = ( (v[0]/l)*thrust/mass, (v[1]/l)*thrust/mass)
        return vn
        
    def action(self, move, wizz):
        if move[0] == "MOVE":
            speed = self.thrustvector( wizz[2], wizz[3], move[1], move[2], move[3], wizz[9] )
            wizz[4] += speed[0]
            wizz[5] += speed[1]
        elif move[0] == "THROW":
            for e in self.entities:
                if e[1] == 'SNAFFLE' and (e[2], e[3]) == (wizz[2], wizz[3]):
                    speed = self.thrustvector( e[2], e[3], move[1], move[2], move[3], e[9] )
                    e[4] += speed[0]
                    e[5] += speed[1]
                    e[10] = 0
                    break
            
        elif move[0] == "OBLIVIATE":
            self.activespells.append( [wizz, move[0], move[1], 3] )
        elif move[0] == "PETRIFICUS":
            self.activespells.append( [wizz, move[0], move[1], 1] )
        elif move[0] == "ACCIO":
            self.activespells.append( [wizz, move[0], move[1], 6] )
        elif move[0] == "FLIPENDO":
            self.activespells.append( [wizz, move[0], move[1], 3] )

    def bludger_target(self):
        for b in self.bludgers:
            d = [distance( (x[2], x[3]), (b[2], b[3]) ) for x in self.wizards]
            closest = nsmallest(len(d), d)
            for i in range(4):
                wa = self.wizards[d.index(closest[i])]
                if wa[1] != b[6] and wa[0] != b[10]:
                    target = wa
                    break
            
            speed = self.thrustvector(b[2], b[3], target[2], target[3], 1000, b[9])
            b[4] += speed[0]
            b[5] += speed[1]
    
    def angle(self, p1, p2):
        xdiff = p2[0]-p1[0]
        ydiff = p2[1]-p1[1]
        return math.atan2(ydiff, xdiff)*180.0/math.pi
    
    def new_velocity(self, o1, o2):
        vx, vx2 = o1[4], o2[4]
        vy, vy2 = o1[5], o2[5]
        rev = False
        ma1 = self.angle(o1[2:4], o1[7])
        ma2 = self.angle(o2[2:4], o2[7])
        ca = self.angle(o1[2:4], o2[2:4])
        
        if ma2 > 0:
            ma2 -= 180
            rev = True
            
        if ca < 90:
            ca += 180
        elif ca > 270:
            ca -= 180
            
        mass1, mass2 = o1[9], o2[9]
        
        new_vx = ((( vx * math.cos(ma1-ca)*(mass1-mass2)+2*mass2*abs(vx2)*math.cos(ma2-ca)) /
                    (mass1+mass2))*math.cos(ca)) + vx*math.sin(ma1-ca)*math.cos(ca+math.pi/2)
        new_vy = ((( vy * math.cos(ma1-ca)*(mass1-mass2)+2*mass2*vy2*math.cos(ma2-ca)) /
                    (mass1+mass2))*math.sin(ca)) + vy*math.sin(ma1-ca)*math.sin(ca+math.pi/2)
        
        if rev:
            new_vx*=-1
            
        return new_vx, new_vy
        
    def check_collision(self):
        for e in self.entities:
            #Snaffle is on a wizz
            if e[10]:
                continue
            epos = (e[2], e[3])
            for o in self.entities + self.poles:
                if e[0] == o[0]:
                    continue
                #collision
                if distance( (e[2], e[3]), (o[2], o[3]) ) < e[8]+o[8]:
                    if e[1] == 'SNAFFLE' and 'WIZARD' in o[1]:    
                        if distance( (e[2], e[3]), (o[2], o[3]) ) < o[8] and o[10] < 1 and o[6] == 0:
                            o[10] = 3
                            o[6] = 1
                            e[10] = o[0]+1
                        continue
                        
                    elif 'WIZARD' in e[1] and o[1] == 'SNAFFLE':
                        continue
                    elif e[1] == 'BLUDGER' and o[1] == 'WIZARD':
                        e[10] = o[0]
                    
                    #new_vx = ( e[4] * (e[9] - o[9] ) + (2 * o[9] * o[4]))/(e[9]+o[9])
                    #new_vy = ( e[5] * (e[9] - o[9] ) + (2 * o[9] * o[5]))/(e[9]+o[9])
                    new_vx, new_vy = self.new_velocity(e, o)
                    new_vx += e[4]
                    new_vy += e[5]
                    
                    new_x = e[2] + new_vx 
                    new_y = e[3] + new_vy

                    e[7] = (new_x, new_y)
 
            
            #Edge collisions
            if e[1] == 'SNAFFLE' and e[3] < 5750 and e[3] > 1700:
                #goal
                if e[2] < 0 or e[2] > 16000:
                    if e[2] < 0 and goal == 0:
                        self.score += 1
                    elif e[2] > 16000 and goal == 16000:
                        self.score += 1
                    self.entities.remove(e)
                continue
                
            #UP - DOWN - LEFT - RIGHT
            if distance( epos, (e[2], 0) ) < e[8] or distance( epos, (e[2], 9000) ) < e[8] or distance( epos, (0, e[3]) ) < e[8] or distance( epos, (16000, e[3]) ) < e[8]:
                e[4], e[5] = e[4]*-1, e[5]*-1
                e[7] = (e[2]+e[4], e[3]+e[5])

    def get_moves(self, wizard):
        possible_moves = list()
        if wizard[6]:
            for i in range(2100, 5400, 200):
                possible_moves.append(["THROW", goal, 2100, 500])
        else:
            if self.manapoints > 4:
                for i in self.bludgers:
                    possible_moves.append(["OBLIVIATE", i[0]])
            if self.manapoints > 9:
                for i in self.entities:
                    if i[1] == 'WIZARD':
                        continue
                    possible_moves.append(["PETRIFICUS", i[0]])
            if self.manapoints > 19:
                for i in self.entities:
                    if i[1] == 'BLUDGER' or i[1] == 'SNAFFLE':
                        possible_moves.append(["ACCIO", i[0]])
                        possible_moves.append(["FLIPENDO", i[0]])
                    if i[1] == 'OPPONENT_WIZARD':
                        possible_moves.append(["FLIPENDO", i[0]])

            for i in self.snaffles:
                possible_moves.append(["MOVE", i[2], i[3], 150])

        return possible_moves

    def set_state(self):
        self.og_score = self.score
        self.og_entities = list([list(e) for e in self.entities])
        self.og_snaffles = [list(i) for i in self.entities if i[1] == 'SNAFFLE']
        self.og_wizards = [list(i) for i in self.entities if 'WIZARD' in i[1]]
        self.og_bludgers = [list(i) for i in self.entities if 'BLUDGER' in i[1]]

    def reset_state(self):
        self.score = self.og_score
        self.entities = list([list(e) for e in self.og_entities])
        self.snaffles = [list(i) for i in self.og_entities if i[1] == 'SNAFFLE']
        self.wizards = [list(i) for i in self.og_entities if 'WIZARD' in i[1]]
        self.bludgers = [list(i) for i in self.og_entities if 'BLUDGER' in i[1]]
        
    def tree_search(self):
        defender = False
        best_score = 99999999999
        possible_moves = list()
        le_moves = list()
        start = int(round(time.time() * 1000))
        for wizard in self.wizards:
            if wizard[1] == 'OPPONENT_WIZARD':
                continue
            possible_moves.append( self.get_moves(wizard) )  

        snaff_dist = [distance( (s[2], s[3]), (goal, 3750) ) for s in self.snaffles]
        target_snaffles = nsmallest( int(round(len(self.snaffles)/2)), snaff_dist )
        snoof = [ self.snaffles[snaff_dist.index(i)] for i in target_snaffles ]
        self.set_state()
        while int(round(time.time() * 1000)) - start < 95:
            p = random.choice(possible_moves[0])
            tmpmana = self.manapoints
            if p[0] == "OBLIVIATE":
                tmpmana = self.manapoints - 5
            elif p[0] == "PETRIFICUS":
                tmpmana = self.manapoints - 10
            elif p[0] in ["ACCIO", "FLIPENDO"]:
                tmpmana = self.manapoints - 20
                        
            p2 = random.choice(possible_moves[1])
            bonus = 0
            le_score = 0
            self.reset_state()
            if p2[0] == "OBLIVIATE" and tmpmana < 5:
                continue
            elif p2[0] == "PETRIFICUS" and tmpmana < 10:
                continue
            elif p2[0] in ["ACCIO", "FLIPENDO"] and tmpmana < 20:
                continue

            if p2[0] == "MOVE":
                if p2[1:3] == snoof[-1][2:4]:
                    bonus -= 50
            
            if p[0] == "MOVE":
                wizz = [ses for ses in self.wizards if ses[1] == 'WIZARD'][0]
                dists = [distance(wizz[2:4], disc[2:4]) for disc in self.snaffles]
                coords = self.snaffles[ dists.index(min(dists)) ][2:4]
                if p[1:3] == coords:
                    bonus -= 50
                    
            self.update_entities([p, p2])
            if self.score > self.og_score:
                bonus -= 500
            for snoo in snoof:
                le_score += distance( snoo[2:4], (goal, 3750) )**2 + bonus

            if le_score < best_score:
                best_score = le_score
                le_moves = [p, p2]
        
        for qq in le_moves:
            if qq[0] == 'OBLIVIATE':
                self.manapoints -= 5
            elif qq[0] == 'PETRIFICUS':
                self.manapoints -= 10
            elif qq[0] in ["ACCIO", "FLIPENDO"]:
                self.manapoints -= 20
                
        return le_moves
    
my_team_id = int(raw_input())  # if 0 you need to score on the right of the map, if 1 you need to score on the left
if my_team_id:
    goal = 0
else:
    goal = 16000

init = True
sim = simulation(my_team_id, goal)
all_entities = list()
_round = 0
# game loop
while True:
    _round += 1
    discs = list()
    wizards = list()
    opponents = list()
    actions = list()
    output = list()
    entities = int(raw_input())  # number of entities still in game
    for i in xrange(entities):
        entity_id, entity_type, x, y, vx, vy, state = raw_input().split()
        values = ( int(entity_id), (int(x), int(y)), int(vx), int(vy), int(state) )
        
        if init:
            _allvalues = [ int(entity_id), entity_type, int(x), int(y), int(vx), int(vy), int(state), 0 ]
            if 'WIZARD' in entity_type:
                all_entities.append( _allvalues + [400, 1, 0, _round, 0.75] )
            elif entity_type == 'SNAFFLE':
                all_entities.append( _allvalues + [150, 0.5, 0, _round, 0.75] )
            elif entity_type == 'BLUDGER':
                all_entities.append( _allvalues + [200, 8, 80, _round, 0.9] )
        else:
            for e in [ae for ae in all_entities if ae[0] == int(entity_id)]:
                e[2], e[3], e[4], e[5], e[11] = int(x), int(y), int(vx), int(vy), _round
                if 'WIZARD' in e[1]:
                    e[6] = int(state)
    
    all_entities = [x for x in all_entities if x[11] == _round]
    sim.new_entities(all_entities)
        
    moves = sim.tree_search()
    print >> sys.stderr, moves
    for op in moves:
        print ' '.join( [str(x) for x in op] )
        
    init = False


            
