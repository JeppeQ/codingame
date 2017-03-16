import sys
import math
import random
import time

width, height, my_id = [int(i) for i in raw_input().split()]

def distance(p1, p2):
    return math.hypot(p2[0]-p1[0], p2[1]-p1[1])

def map_boxes(grid):
    boxes = list()
    for w in range(width):
        for h in range(height):
            if grid[w][h] == '0':
                boxes.append( (w, h) )
    return boxes

#OBS!
#Two players can get the same box

class bomberman:

    def __init__(self, myid):
        self.myid = myid

    def update_state(self, grid, me):
        self.grid = grid
        self.x, self.y = me[0], me[1]
        self.range = me[3]
        self.bombsleft = me[2]

    def update_pos(self, pos):
        self.x, self.y = pos[0], pos[1]
        
    def add_entities(self, bombs, items):
        self.bombs = bombs
        self.items = items
        for bomb in bombs:
            self.grid[bomb[1]][bomb[2]] = 'B'
        for item in items:
            self.grid[item[0]][item[1]] = 'T'+str(item[2])
        
    def remove_stuff(self, burn, friendly):
        for f in burn:
            point = self.grid[f[0]][f[1]]
            self.fire.append(f)
            if point in ['X', '0', '1', '2']:
                if point.isdigit():
                    if int(point):
                        self.grid[f[0]][f[1]] = "T"+point
                        if friendly:
                            self.value += 5
                    else:
                        if friendly:
                            self.value += 3
                else:
                    self.grid[f[0]][f[1]] = '.'
                    return
            elif point == 'B':
                le_bomb = [b for b in self.bombs if (b[1],b[2]) == f][0] 
                self.bomb_explosion(le_bomb)
            else:
                self.grid[f[0]][f[1]] = '.'
        
    def bomb_explosion(self, bomb):
        C = False
        if bomb[0] == self.myid:
            self.bombsleft += 1
            C = True
        self.bombs.remove(bomb)
        self.grid[ bomb[1] ][ bomb[2] ] = '.'
        self.remove_stuff( [(bomb[1],bomb[2]-i) for i in range(1, bomb[4]) if bomb[2]-i > -1], C )
        self.remove_stuff( [(bomb[1],bomb[2]+i) for i in range(1, bomb[4]) if bomb[2]+i < 11], C )
        self.remove_stuff( [(bomb[1]+i,bomb[2]) for i in range(1, bomb[4]) if bomb[1]+i < 13], C )
        self.remove_stuff( [(bomb[1]-i,bomb[2]) for i in range(1, bomb[4]) if bomb[1]-i > -1], C )
        
    def future_grid(self):
        self.fire = list()
        for bomb in self.bombs:
            bomb[3] -= 1
            if bomb[3] == 0:
                self.bomb_explosion(bomb)

    def random_move(self, last):
        x, y = self.x, self.y
        moves = [(x,y+1), (x,y-1), (x+1,y), (x-1,y)]
        eligible = [m for m in moves if 13 > m[0] > -1 and 10 > m[1] > -1 and m != last]
        eligible = [e for e in eligible if self.grid[e[0]][e[1]] in ['.', 'T1', 'T2']] + [(x,y)]
        return random.choice(eligible)
        
    def monte_carlo(self):
        sequence = list()
        cmd = ['MOVE', 'BOMB']
        start = int(round(time.time() * 1000))
        grid = self.grid
        pos = (self.x, self.y)
        bombs = self.bombs
        
        best = -1
        while int(round(time.time() * 1000)) - start < 95:
            tmp = list()
            self.grid = [list(g) for g in grid]
            self.update_pos(pos)
            self.bombs = [list(h) for h in bombs]
            self.value = 0
            lastmove = ""
            for i in range(10):
                self.future_grid()
                if (self.x, self.y) in self.fire:
                    self.value = -1
                    break

                closest_box = min([distance(box, (self.x, self.y)) for box in map_boxes(self.grid)]) 
                cmd = random.choice(['MOVE', 'BOMB'])  
                if self.bombsleft > 0 and cmd == 'BOMB':
                    move = self.random_move("")
                    tmp.append("BOMB %s %s" % (str(move[0]), str(move[1])) )
                    self.grid[ self.x ][ self.y ] = 'B'
                    self.bombsleft -= 1
                    self.bombs.append([self.myid, self.x, self.y, 8, self.range]) 
                else:
                    move = self.random_move(lastmove)
                    tmp.append("MOVE %s %s" % (str(move[0]), str(move[1])) )

                
                if move != (self.x, self.y):
                    self.value += 1
                    lastmove = (self.x, self.y)
                    
                self.update_pos(move)

                if closest_box > min([distance(box, (self.x, self.y)) for box in map_boxes(self.grid)]):
                    self.value += 1
                if 'T' in self.grid[self.x][self.y]:
                    if '1' in self.grid[self.x][self.y]:
                        self.range += 1
                        self.value += 4
                    elif '2' in self.grid[self.x][self.y]:
                        self.value += 5
                        self.bombsleft += 1
                    self.grid[self.x][self.y] = '.'
                    lastmove = ""

            if self.value > best:
                best = self.value
                sequence = list(tmp)
                
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
    seq = bm.monte_carlo()
    print >> sys.stderr, seq
    print seq[0]

    

