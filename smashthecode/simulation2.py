import sys
import time
import itertools
import random

possible_moves = [(0, 0), (0,1), (0, 3), (1,0), (1,1), (1,2), (1,3), (2,0), (2,1), (2,2), (2,3), (3,0), (3,1), (3,2), (3,3), (4,0), (4,1), (4,2), (4,3), (5,1), (5,2), (5,3)]
moves_set = False

class player:

    def __init__(self, grid):
        self.score = 0
        self.skulls = 0
        self.rotations = [1, 0, -1, 0]
        self.grid = [list(g) for g in grid]
        self.brickcount = [11 for i in range(6)]
        self.currentscore = 0
        self.positionsscore = 0
        self.update_brickcount()

    def other_grid(self, grid):
        self.grid = [list(q) for q in grid]
        
    def new_grid(self, grid):
        self.grid = [list(q) for q in grid]
        self.update_brickcount()
        
    def prev_grid(self):
        self.grid = [list(q) for q in self.pregrid]

    def show_prev_grid(self):
        for i in self.pregrid:
            print i
            
    def show_grid(self):
        for i in self.grid:
            print i
        
    def get_score(self):
        return self.score

    def get_skulls(self):
        return self.skulls

    def update_checks(self, c):
        checks = list()
        for col in range(6):
            if c[col] > 0:
                for row in reversed(range(c[col]+1)):
                    if self.grid[row][col] != ".":
                        checks.append( (row, col) )
                    else:
                        break
        return checks

    def turn(self, brick, move):
        b1 = move[0]
        b2 = move[0]+self.rotations[move[1]]
        self.pregrid = [list(g) for g in self.grid]   
        #Do we die?
        if move[1] == 1 or move[1] == 3:
            if self.brickcount[b1] < 1:
                return -1
        if self.brickcount[b1] < 0 or self.brickcount[b2] < 0:
            return -1
        else:
            self.set_grid(brick, move)
            score = self.update_grid(False)       
            return score
        
    def set_grid(self, brick, move):
        if move[1] == 3:
            brick = (brick[1], brick[0])
        b1 = move[0]
        b2 = move[0]+self.rotations[move[1]]
        self.grid[self.brickcount[b1]][b1] = brick[0]
        self.lastpos1 = (self.brickcount[b1], b1)
        self.brickcount[b1] -= 1
        self.grid[self.brickcount[b2]][b2] = brick[1]
        self.lastpos2 = (self.brickcount[b2], b2)
        self.brickcount[b2] -= 1

    def add_skulls(self):
        for i in range(6):
            if self.brickcount[i] > 0:
                self.grid[self.brickcount[i]][i] = "0"
                self.brickcount[i] -= 1
    
    def update_grid(self, test):
        chain = 0
        self.currentscore = 0
        if test:
            checks = list()
            for i in range(4, 12):
                for x in range(1, 4):
                    checks.append( (i, x) )
        else:
            checks = [self.lastpos1, self.lastpos2]

        while(checks != list()):
            new_checks = [0 for i in range(6)]
            balls = list()
            #Check all changed positions in grid
            for i in checks:
                if i in [item for sublist in balls for item in sublist]:
                    continue
                else:
                    balls.append(self.remove_balls(i))

            #Only take group of blocks with 4 or more
            self.positionsscore += len([grp for grp in balls if len(grp) > 1])
            self.positionsscore += sum([len(grp) for grp in balls])
            
            balls = [grp for grp in balls if len(grp)>3]
            
            if len(balls) == 0:
                break
            self.positionsscore = 0
            #Calculate score
            chain += 1
            self.currentscore += self.score_points(balls, chain)
            
            #Remove blocks
            for grp in balls:
                for ball in grp:
                    self.grid[ball[0]][ball[1]] = "."
                    self.remove_skull(ball[0], ball[1])
                    if new_checks[ball[1]] < ball[0]:
                        new_checks[ball[1]] = ball[0]

            #Blocks fall down
            self.balls_falls()
            checks = self.update_checks(new_checks)
        return chain

    def remove_skull(self, y, x):
        if y < 11:
            if self.grid[y+1][x] == "0":
                self.grid[y+1][x] = "."
        if y > 0:
            if self.grid[y-1][x] == "0":
                self.grid[y-1][x] = "."
        if x < 5:
            if self.grid[y][x+1] == "0":
                self.grid[y][x+1] = "."
        if x > 0:
            if self.grid[y][x-1] == "0":
                self.grid[y][x-1] = "."
        
    def score_points(self, balls, chain):
        #Calculate chain points
        if chain < 2:
            chainpoints = 0
        else:
            chainpoints = 2**(chain+1)
        
        #Calculate Color_Bonus
        diff_colors = len(set([self.grid[grp[0][0]][grp[0][1]] for grp in balls]))
        if diff_colors < 2:
            ColorBonus = 0
        else:
            ColorBonus = 2**(diff_colors-1)

        grpblocks = [len(grp) for grp in balls]
        #Calculate group bonus and number of blocks
        GroupBonus = sum( [i-4 if i < 11 else 8 for i in grpblocks] )
        blocks = sum( grpblocks )
        #print blocks, chainpoints, ColorBonus, GroupBonus
        return (10*blocks) * max((chainpoints+ColorBonus+GroupBonus),1)
        

    def balls_falls(self):
        self.brickcount = [11 for i in range(6)]
        side = [[row[i] for row in self.grid] for i in range(6)]
        [[col.insert(0, col.pop(i)) for i in range(12) if col[i] == "."] for col in side]
        self.grid = [[row[i] for row in side] for i in range(12)]

        for col in range(6):
            for pos in reversed(range(12)):
                if self.grid[pos][col] == ".":
                    self.brickcount[col] = pos
                    break
            
    def remove_balls(self, x):
        points = list()
        points.append( x )
        color = self.grid[x[0]][x[1]]
        
        for i in points:
            if i[0] > 0 and self.grid[i[0]-1][i[1]] == color and (i[0]-1,i[1]) not in points:
                points.append( (i[0]-1,i[1]) )
            
            if i[1] > 0 and self.grid[i[0]][i[1]-1] == color and (i[0],i[1]-1) not in points:
                points.append( (i[0],i[1]-1) )
        
            try:
                if self.grid[i[0]+1][i[1]] == color and (i[0]+1,i[1]) not in points:
                    points.append( (i[0]+1,i[1]) )
            except: pass
        
            try:
                if self.grid[i[0]][i[1]+1] == color and (i[0],i[1]+1) not in points:
                    points.append( (i[0],i[1]+1) )
            except: pass

        return points

    def update_brickcount(self):
        for col in range(6):
            for pos in reversed(range(12)):
                if self.grid[pos][col] == ".":
                    self.brickcount[col] = pos
                    break

def find_chain(bricks):
    chain = 0
    keks = [0 for i in range(6)]
    
    for i in range(8):
        keks[int(bricks[i][0])] += 1
        keks[int(bricks[i][1])] += 1
        
        if sum(i > 3 for i in keks) > 2:
            foundation = bricks[:i]
            next_brick = bricks[i]
            return [sum(i > 3 for i in keks)], foundation, [next_brick], [22], True 

    # 4x4x3(x3)
    if sum(i > 3 for i in keks) > 1 and sum(i == 3 for i in keks) > 0:
        colors = [str(i) for i in range(6) if keks[i] == 3]
        randoms = [i for i in range(1, 6) if str(i) not in colors]
        if sum(i == 3 for i in keks) > 1:
            next_brick = [ ( str(colors[0]), str(colors[1]) ), ( str(colors[0]), str(randoms[0]) ), ( str(colors[1]), str(randoms[0]) ) ]
            chain = [4,3,3]
        elif sum(i == 3 for i in keks) == 1:
            next_brick = [ ( str(colors[0]), str(randoms[0]) ) ]
            chain = [3]
        return chain, bricks, next_brick, colors, False
    
    # 4x3x3x3x3x3
    elif sum(i > 3 for i in keks) == 1 and sum(i == 3 for i in keks) > 1:
        next_brick = bricks[-1]
        chain = [3]
        return chain, bricks[:-1], [next_brick], [22], True
        
def find_moves(grid, chain, foundation, next_brick, first_move = 0):
    safety = list()
    structure_score = 0
    p = player(grid)
    p1 = player(grid)
    for iterations in range(500):
        p.new_grid(grid)
        mymoves = list()
        if first_move != 0:
            p.turn(first_move[0], first_move[1])
            mymoves.append(first_move[1])
            
        for i in foundation:
            move = grid_moves[random.randint(0, 9)]
            score = p.turn(i, move)
            if score > 0 or score < 0:
                break

            mymoves.append(move)

        if len(mymoves) < len(foundation):
            continue

        for move in possible_moves:
            p1.new_grid(p.grid)
            score = p1.turn(next_brick, move)
            if score >= chain:
                return mymoves+[move]
            elif p1.currentscore > 70*6:
                safety = mymoves+[move]
 #           else:
#                p1.update_grid(True)
#                if p1.positionsscore > structure_score:
#                    structure_score = p1.positionsscore
#                    safety = mymoves + [move]
    return safety     
    
def change_move(move):
    if move[1] == 1:
        return (move[0], 3)
    elif move[1] == 3:
        return (move[0], 1)
    elif move[1] == 0:
        return (move[0], 2)
    elif move[1] == 2:
        return (move[0], 0)

def add_extra_moves(extra_moves, moves):
    b = moves[-1]
    moves = moves[max(len(extra_moves)-1, 0):-1]
    for i in extra_moves:
        moves.append(i)
    moves.append(b)
    return moves
    
moves = list()
extra_moves = list()
first_move = 0
first = True
routes = list()    
grid_moves = [(1,0), (1,1), (1,3), (2,0), (2,1), (2,2), (2,3), (3,1), (3,2), (3,3)]
grid_moves2 = [(1,0), (1,1), (1,3), (2,0), (2,1), (2,2), (2,3), (3,0), (3,1), (3,2), (3,3), (4,1), (4,2), (4,3)]

while True:

    starttime = int(round(time.time() * 1000))
    colors = list()
    for i in xrange(8):
        # color_a: color of the first block
        # color_b: color of the attached block
        color_a, color_b = [j for j in raw_input().split()]
        colors.append( (color_a, color_b) )
        
    mygrid = [[x for x in raw_input()] for i in xrange(12)]
    
    for i in xrange(12):
        row = raw_input()  # One line of the map ('.' = empty, '0' = skull block, '1' to '5' = colored block)

    
    if first:
        chain, foundation, potential_bricks, colors_needed, moves_set = find_chain(colors)
        for i in range(max(len(potential_bricks), 3)):
            if i == 1 and routes[0] != []:
                first_move = (foundation[0], routes[0][0])
                foundation = foundation[1:]
            routes.append( find_moves(mygrid, chain[i], foundation, potential_bricks[i], first_move) )
        moves = routes[0]

    if not first and not moves_set:
        print >> sys.stderr, colors_needed, colors[-1]
        if colors[-1][0] in colors_needed or colors[-1][1] in colors_needed:
            for i in range(len(potential_bricks)):
                print >> sys.stderr, chain[i]
                if colors[-1][0] != potential_bricks[i][0]:
                    routes[i][-1] = change_move(routes[i][-1])        
                if chain[i] == 4:
                    if colors[-1][0] in potential_bricks[i] and colors[-1][1] in potential_bricks[i]:
                        moves = routes[i]
                        moves_set = True
                        moves = add_extra_moves(extra_moves, moves)
                        break
                elif chain[i] == 3:
                    if colors[-1][0] in potential_bricks[i] or colors[-1][1] in potential_bricks[i]:
                        moves = routes[i]
                        moves_set = True
                        moves = add_extra_moves(extra_moves, moves)
                        break
        else:
            extra_moves.append( (5, 1) )
    

    first = False
    pop = moves.pop(0)
    print pop[0], pop[1]
        

