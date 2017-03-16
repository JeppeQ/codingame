import sys
import math
import random
import time

width, height, my_id = [int(i) for i in raw_input().split()]

def distance(p1, p2):
    return math.hypot(p2[0]-p1[0], p2[1]-p1[1])

def distance_to_boxes(grid, pos):
    sumdistance = list()
    boxes = 0
    for w in range(width):
        for h in range(height):
            if grid[w][h].isdigit():
                boxes += 1
                sumdistance.append( distance( (w, h), pos ))
    if boxes == 0:
        return 0, boxes
    else:
        return min(sumdistance), boxes

#OBS!
#Two players can get the same box

class bomberman:

    def __init__(self, myid):
        self.ogid = myid
        self.runtime = 93
        self.opp_bombsleft = [1 for i in range(5)]
        self.oppmoves = list()
        self.target = (0, 0, 0, 0, 0)
        
    def update_state(self, grid, me, opp):
        self.myid = self.ogid
        self.grid = grid
        self.fire = list()
        self.x, self.y = me[0], me[1]
        self.range = me[3]
        self.bombsleft = me[2]
        self.opp = opp
        self.value = 0
        self.banned_move = ""
        self.target_distance = distance( (self.x, self.y), (self.target[1], self.target[2]) ) 
        boxes = distance_to_boxes(grid, me[:2])
        self.start_distance = boxes[0]
        self.boxcount = boxes[1]

    def update_pos(self, pos):
        self.x, self.y = pos[0], pos[1]
        
    def add_entities(self, bombs, items, players):
        self.bombs = bombs
        self.items = items
        for bomb in bombs:
            self.grid[bomb[1]][bomb[2]] = 'B'
        for item in items:
            self.grid[item[0]][item[1]] = 'T'+str(item[2])

    def opp_next_moves(self, opp):
        if opp[3] != self.opp_bombsleft[opp[0]]:
            lastmove = (opp[1], opp[2], 'B')
        else:
            lastmove = (opp[1], opp[2])
        
        for i in self.oppmoves:
            if i[0] == opp[0]:
                try:
                    return [x for x in i[1] if x[0] == lastmove][0]
                except:
                    break
                
        return [0 for i in range(5)]
        
    def potential_paths(self, point, count = 0):
        if count > 4:
            return True
        x, y = point[0], point[1]
        points = [p for p in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)] if 13 > p[0] > -1 and  11 > p[1] > -1]
        availeble = [i for i in points if self.grid[i[0]][i[1]] in ['.', 'T1', 'T2']]
        for a in availeble:
            self.potential_paths(a, count+len(availeble))
        return False
    
    def outs(self, point):
        x, y = point[0], point[1]
        points = [p for p in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)] if 13 > p[0] > -1 and  11 > p[1] > -1]
        availeble = [i for i in points if self.grid[i[0]][i[1]] in ['.', 'T1', 'T2']]
        return len(availeble)
        
    def remove_stuff(self, burn, friendly):
        for f in burn:
            point = self.grid[f[0]][f[1]]
            self.fire.append(f)
            if friendly:
                self.friendlyfire.append(f)
            if point in ['X', '0', '1', '2', 'T1', 'T2', 'BB']:
                return
            elif point == 'B':
                le_bomb = [b for b in self.bombs if (b[1],b[2]) == f][0]
                self.bomb_explosion(le_bomb)
                return
            elif 'T' in point:
                return
        
    def bomb_explosion(self, bomb):
        C = False
        if bomb[0] == self.myid:
            self.bombsleft += 1
            C = True
        self.fire.append( (bomb[1], bomb[2]) )
        self.grid[ bomb[1] ][ bomb[2] ] = 'BB'
        #Up, Down, Right, Left
        self.remove_stuff( [(bomb[1],bomb[2]-i) for i in range(1, bomb[4]) if bomb[2]-i > -1], C )
        self.remove_stuff( [(bomb[1],bomb[2]+i) for i in range(1, bomb[4]) if bomb[2]+i < 11], C )
        self.remove_stuff( [(bomb[1]+i,bomb[2]) for i in range(1, bomb[4]) if bomb[1]+i < 13], C )
        self.remove_stuff( [(bomb[1]-i,bomb[2]) for i in range(1, bomb[4]) if bomb[1]-i > -1], C )
        self.bombpop.append(bomb)
   
    def count_all(self):
        self.value += sum([12 for f in self.friendlyfire if self.grid[f[0]][f[1]].isdigit()])
        for f in self.fire:
            if self.grid[f[0]][f[1]] in ['1', '2']:
                self.grid[f[0]][f[1]] = "T"+self.grid[f[0]][f[1]]
            elif self.grid[f[0]][f[1]] != "X":
                self.grid[f[0]][f[1]] = "."
        
    def update_opp(self, n):
        for opp in self.opp:
            move = self.opp_next_moves(opp)
            if not move[n]:
                return
            
            if len(move[n]) == 3:
                self.grid[move[n-1][0]][move[n-1][1]] == 'B'
                self.bombs.append( [opp[0], move[n-1][0], move[n-1][1], 8, opp[4]] )
            self.opp[ self.opp.index(opp) ] = (opp[0], move[n][0], move[n][1], opp[3], opp[4])
        
    def future_grid(self, move, n): 
        self.fire = list()
        self.friendlyfire = list()
        self.bombpop = list()
        #Don't get baited into a corner
        if self.outs(move[:2]) < 2:
            if self.target_distance < 1:
                self.value -= 1000
                
        if n < 4:
            self.update_opp(n)
        
        if len(move) == 3:
            self.grid[self.x][self.y] = 'B'
            self.bombs.append( [self.myid, self.x, self.y, 8, self.range] )
            if self.boxcount < 1 and n == 1:
                self.value += 3
            self.value -= 3
            self.bombsleft -= 1
    
        for bomb in self.bombs:
            bomb[3] -= 1
            
        for bomb in self.bombs:
            if bomb[3] == 0:
                self.bomb_explosion(bomb)
        self.count_all()
        
        self.lastmove = (self.x, self.y)
        self.update_pos(move[:2])
        self.current_state()
        return self.value > -500
        
    def explode_bombs(self):
        self.fire = list()
        self.friendlyfire = list()
        self.bombpop = list()
        
        for i in range(8):
            for bomb in self.bombs:
                bomb[3] -= 1
                
            for bomb in self.bombs:
                if bomb[3] == 0:
                    self.bomb_explosion(bomb)
            self.count_all()
        
    def current_state(self):
        if self.lastmove in self.fire:
            self.value -= 1000
        elif 'T' in self.grid[self.x][self.y]:
            if '1' in self.grid[self.x][self.y]:
                self.range += 1
                self.value += max(1, (6-self.range))
            elif '2' in self.grid[self.x][self.y]:
                self.bombsleft += 1
                self.value += max(1, (5-self.bombsleft))
            self.grid[self.x][self.y] = "."
            self.lastmove = ""
            
        if (self.x, self.y) != self.lastmove:
            self.value += 0.5
        self.bombs = [list(b) for b in self.bombs if b not in self.bombpop]

    def evaluate_state(self):
        self.outs((self.x, self.y))
        if self.boxcount == 0 and len([b[3] for b in self.bombs if b[0] == self.myid]) > 0:
            self.value -= max([b[3] for b in self.bombs if b[0] == self.myid]) 
        
        self.explode_bombs()

        #Can't avoid fire
        if self.potential_paths((self.x, self.y)) or (self.x, self.y) not in self.fire:
            self.value += 0
        else:
            self.value -= 10000
            
        #opp trapped?
        for opp in self.opp:
            if not self.potential_paths((opp[1], opp[2])) or (opp[1], opp[2]) in self.fire:
                self.value += 500
        #New value system
        if self.boxcount == 0:
            if self.target_distance > 3:
                self.value += self.target_distance - distance( (self.x, self.y), (self.target[1],self.target[2]) )
            else:
                self.value += distance( (self.x, self.y), (self.target[1],self.target[2]) ) - self.target_distance
            self.value += len(self.friendlyfire)*5
            
        #Move closer to boxes
        new_dist = distance_to_boxes(self.grid, (self.x, self.y))
        if self.start_distance > new_dist[0]:
            self.value += self.start_distance - new_dist[0]
        
    def possible_moves(self, last):
        x, y = self.x, self.y
        moves = [(x,y+1), (x,y-1), (x+1,y), (x-1,y)]
        eligible = [m for m in moves if 13 > m[0] > -1 and 11 > m[1] > -1 and m != last and m!=self.banned_move]
        eligible = [e for e in eligible if self.grid[e[0]][e[1]] in ['.', 'T1', 'T2']] + [(x,y)]
        bomb = [(e[0],e[1],'B') for e in eligible if self.bombsleft > 0 and self.grid[x][y] != 'B']
        if last != "" and self.bombsleft > 0 and self.grid[last[0]][last[1]] in ['.', 'T1', 'T2']:
            bomb += [(last[0], last[1], 'B')]
        return bomb+eligible

    def save_state(self):
        prev_grid = [list(g) for g in self.grid]
        prev_pos = (self.x, self.y)
        prev_bombs = [list(b) for b in self.bombs]
        left = self.bombsleft
        brange = self.range
        return prev_grid, prev_pos, prev_bombs, left, brange

    def set_previous_state(self, state):
        self.value = 0
        self.grid = [list(g) for g in state[0]]
        self.update_pos(state[1])
        self.bombs = [list(b) for b in state[2]]
        self.bombsleft = state[3]
        self.range = state[4]
        
    def opp_move(self):
        self.oppmoves = list()
        d = [distance( (self.x, self.y), (opp[1], opp[2]) ) for opp in self.opp]
        opp = self.opp[d.index(min(d))]
        self.target = opp
        self.x = opp[1]
        self.y = opp[2]
        self.myid = opp[0]
        self.bombsleft = opp[3]
        self.range = opp[4]
        self.opp_bombsleft[opp[0]] = opp[3]
        self.oppmoves.append( [opp[0], self.tree_search(True)] )
        
    def tree_search(self, opp=False):
        sequence = list()
        oppsequence = [[0] for i in range(10)]
        start = int(round(time.time() * 1000))
        best = -10
        count = -1
        state1 = self.save_state()  
            
        for move1 in self.possible_moves(""):
            values = [0, 0, 0, 0]
            oppbest = -10
            count += 1
            self.set_previous_state(state1)
            self.future_grid(move1, 1)
            values[0] = self.value
            state2 = self.save_state()
            
            for move2 in self.possible_moves(self.lastmove):
                self.set_previous_state(state2)
                self.future_grid(move2, 2)
                values[1] = self.value
                state3 = self.save_state()
                
                for move3 in self.possible_moves(self.lastmove):
                    self.set_previous_state(state3)
                    self.future_grid(move3, 3)
                    values[2] = self.value
                    state4 = self.save_state()
                    
                    for move4 in self.possible_moves(self.lastmove):        
                        self.set_previous_state(state4)
                        self.future_grid(move4, 4)
                        self.evaluate_state()
                        values[3] = self.value
                        
                        tmp = [move1, move2, move3, move4]
                        try:
                            values[3] += 3-([len(m) for m in tmp].index(3))
                        except:
                            pass

                        if opp: 
                            if sum(values) > oppbest:
                                oppbest = sum(values)
                                oppsequence[count] = tmp
                        elif sum(values) > best:
                            best = sum(values)
                            sequence = tmp
                            
                        if int(round(time.time() * 1000)) - start > self.runtime:
                            if opp:
                                return oppsequence
                            else:
                                return sequence

        if opp:
            return oppsequence
        else:
            return sequence

    def decision(self, seq):
        if len(seq) > 2 and self.boxcount > 1:
            state = self.save_state()
            if self.future_grid(seq[0], 1):
                self.opp_move()
                return seq
            else:
                self.set_previous_state(state)
                self.banned_move = seq[0][:2]
                return self.tree_search()
        else:
            return self.tree_search()   

       
# game loop
bm = bomberman(my_id)
seq = list()
while True:
    opp = list()
    bombs = list()
    items = list()
    
    grid = [raw_input() for i in xrange(height)]
    grid = [list(q) for q in zip(*grid)]
    entities = int(raw_input())

    for i in xrange(entities):
        entity_type, owner, x, y, param_1, param_2 = [int(j) for j in raw_input().split()]
        if not entity_type:
            if owner == my_id:
                myman = (x, y, param_1, param_2)
            else:
                opp.append( (owner, x, y, param_1, param_2) )
        elif entity_type == 1:
            bombs.append( [owner, x, y, param_1, param_2] )
        else:
            items.append( (x, y, param_1) )

    bm.update_state(grid, myman, opp)
    bm.add_entities(bombs, items, opp)
    decision = bm.decision(seq)
    seq = decision[1:]
    if len(decision) < 1:
        print "MOVE 5 5" 
    elif len(decision[0]) == 3:
        print "BOMB %s %s" % (str(decision[0][0]), str(decision[0][1]))
    else:
        print "MOVE %s %s" % (str(decision[0][0]), str(decision[0][1]))
    

