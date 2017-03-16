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
        self.myid = myid

    def update_state(self, grid, me):
        self.grid = grid
        self.fire = list()
        self.x, self.y = me[0], me[1]
        self.range = me[3]
        self.bombsleft = me[2]
        self.start_distance = distance_to_boxes(grid, me[:2])[0]

    def update_pos(self, pos):
        self.x, self.y = pos[0], pos[1]
        
    def add_entities(self, bombs, items):
        self.bombs = bombs
        self.items = items
        for bomb in bombs:
            self.grid[bomb[1]][bomb[2]] = 'B'
        for item in items:
            self.grid[item[0]][item[1]] = 'T'+str(item[2])

    def potential_paths(self, point, count = 0):
        if count > 3:
            return True
        x, y = point[0], point[1]
        points = [p for p in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)] if 13 > p[0] > -1 and  11 > p[1] > -1]
        availeble = [i for i in points if self.grid[i[0]][i[1]] in ['.', 'T1', 'T2']]
        for a in availeble:
            self.potential_paths(a, count+len(availeble))
        return False
        
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
        
    def future_grid(self, move): 
        self.fire = list()
        self.friendlyfire = list()
        self.bombpop = list()
        
        if len(move) == 3:
            self.grid[self.x][self.y] = 'B'
            self.bombs.append( [self.myid, self.x, self.y, 8, self.range] )
            self.value -= 4
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
                self.value += max(2, (10-self.range))
            elif '2' in self.grid[self.x][self.y]:
                self.bombsleft += 1
                self.value += max(2, (8-self.bombsleft))
            self.grid[self.x][self.y] = "."
            self.lastmove = ""
            
        if (self.x, self.y) != self.lastmove:
            self.value += 1
        self.bombs = [list(b) for b in self.bombs if b not in self.bombpop]

    def evaluate_state(self):  
        self.explode_bombs()

        #Can't avoid fire
        if self.potential_paths((self.x, self.y)) or (self.x, self.y) not in self.fire:
            self.value += 0
        else:
            self.value -= 1000
        #Move closer to boxes
        new_dist = distance_to_boxes(self.grid, (self.x, self.y))
        if self.start_distance > new_dist[0]:
            self.value += self.start_distance - new_dist[0]
        

    def possible_moves(self, last):
        x, y = self.x, self.y
        moves = [(x,y+1), (x,y-1), (x+1,y), (x-1,y)]
        eligible = [m for m in moves if 13 > m[0] > -1 and 11 > m[1] > -1 and m != last]
        eligible = [e for e in eligible if self.grid[e[0]][e[1]] in ['.', 'T1', 'T2']] + [(x,y)]
        bomb = [(e[0],e[1],'B') for e in eligible if self.bombsleft > 0 and self.grid[x][y] != 'B']
        if last != "" and self.bombsleft > 0 and self.grid[last[0]][last[1]] in ['.', 'T1', 'T2']:
            bomb += [(last[0], last[1], 'B')]
        return eligible+bomb

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
        
    def tree_search(self):
        sequence = list()
        start = int(round(time.time() * 1000))
        best = -10
        state1 = self.save_state()  
            
        for move1 in self.possible_moves(""):
            values = [0, 0, 0, 0]
            self.set_previous_state(state1)
            self.future_grid(move1)
            values[0] = self.value
            state2 = self.save_state()
            
            for move2 in self.possible_moves(self.lastmove):
                self.set_previous_state(state2)
                self.future_grid(move2)
                values[1] = self.value
                state3 = self.save_state()
                
                for move3 in self.possible_moves(self.lastmove):
                    self.set_previous_state(state3)
                    self.future_grid(move3)
                    values[2] = self.value
                    state4 = self.save_state()
                    
                    for move4 in self.possible_moves(self.lastmove):        
                        self.set_previous_state(state4)
                        self.future_grid(move4)
                        self.evaluate_state()
                        values[3] = self.value
                        
                        tmp = [move1, move2, move3, move4]
                        try:
                            values[3] += (3-([len(m) for m in tmp].index(3)))*2
                        except:
                            pass
                        
                        if sum(values) > best:
                            best = sum(values)
                            sequence = tmp
                            
                        if int(round(time.time() * 1000)) - start > 94:
                            return sequence
        return sequence
 
# game loop
bm = bomberman(my_id)
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

    bm.update_state(grid, myman)
    bm.add_entities(bombs, items)
    seq = bm.tree_search()
    if len(seq[0]) == 3:
        print "BOMB %s %s" % (str(seq[0][0]), str(seq[0][1]))
    else:
        print "MOVE %s %s" % (str(seq[0][0]), str(seq[0][1]))
    

