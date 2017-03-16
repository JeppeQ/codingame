class player:

    def __init__(self, grid):
        self.score = 0
        self.skulls = 0
        self.rotations = [1, 0, -1, 0]
        self.grid = [list(g) for g in grid]
        self.brickcount = [11 for i in range(6)]
        self.currentscore = 0
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

    def check_popper(self, popindex, poppers, popper):
        if popindex == 0:
            pos = self.lastpos1
        else:
            pos = self.lastpos2
            
        if len(poppers) > 0:
            if pos[0] < 11 and self.grid[pos[0]+1][pos[1]] == popper:
                return True
            elif self.grid[pos[0]-1][pos[1]] == popper:
                return True
            elif self.grid[pos[0]][pos[1]+1] == popper:
                return True
            elif self.grid[pos[0]][pos[1]-1] == popper:
                return True
            else:
                return False
        else:
            if pos[0] < 11 and self.grid[pos[0]+1][pos[1]] == ".":
                return True
            elif self.grid[pos[0]-1][pos[1]] == ".":
                return True
            elif self.grid[pos[0]][pos[1]+1] == ".":
                return True
            elif self.grid[pos[0]][pos[1]-1] == ".":
                return True
            else:
                return False
            
        
    def block_neighbours(self, popper, poppers):
        pass
        
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
            checks = [(10, 1), (10, 2), (10, 3), (10, 4), (11, 1), (11, 2), (11, 3), (11, 4)] 
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
            balls = [grp for grp in balls if len(grp)>3]
            if len(balls) == 0:
                break

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



