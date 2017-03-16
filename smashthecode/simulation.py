from player import player
import random
import itertools

possible_moves = [(0, 0), (0,1), (0, 3), (1,0), (1,1), (1,2), (1,3), (2,0), (2,1), (2,2), (2,3), (3,0), (3,1), (3,2), (3,3), (4,0), (4,1), (4,2), (4,3), (5,1), (5,2), (5,3)]

def find_patterns():
    for i in range(10000):
        grid = [["." for i in range(6)] for i in range(12)]
        for i in range(4, 12):
            grid[i] = [str(random.randint(1, 5)) if x < 3 and x > 0 else "." for x in range(6)]

        brick = ( str(random.randint(1, 5)), str(random.randint(1,5)) )
        for move in possible_moves:    
            p = player(grid)
            p.update_grid(True)
            score = p.turn(brick, move)
            if p.currentscore > 70*6 and score < 3:
                p.other_grid( [[p.pregrid[row][i] if (p.pregrid[row][i] != "." and p.grid[row][i] != p.pregrid[row][i]) else "." for i in range(6) ] for row in range(12)] )
                print brick, move, score
                p.show_grid()
   
def create_random_grids(grid, bricks):
    chain = 0
    Nochain = False
    keks = [0 for i in range(6)]
    #Update the keks
    for pos in reversed(range(12)):
        if grid[pos].count(".") == 6:
            break
        for bok in range(6):
            if grid[pos][bok] != "." and grid[pos][bok] != "0":
                keks[int(grid[pos][bok])] += 1
                
    for i in range(8):
        if keks[int(bricks[i][0])] + 1 == 4:
            popper = bricks[i][0]
        elif keks[int(bricks[i][1])] + 1 == 4:
            popper = bricks[i][1]
                  
        keks[int(bricks[i][0])] += 1
        keks[int(bricks[i][1])] += 1
        if sum(i > 3 for i in keks) > 2 or sum(i > 7 for i in keks)*2 + sum(i > 3 for i in keks) > 2:
            foundation = bricks[:i]
            next_brick = bricks[i]
            Nochain = True
            break
        
        elif i == 7 and sum(i > 3 for i in keks) > 1 and sum(i == 3 for i in keks) > 0:
            next_brick = (str(keks.index(3)), str(random.randint(1, 5)))
            keks[keks.index(3)] += 1
            keks[int(next_brick[1])] += 1                    
            foundation = bricks
        
        elif i == 7 and sum(i > 3 for i in keks) > 1 and sum(i == 2 for i in keks) > 0:
            next_brick = (str(keks.index(2)), str(keks.index(2)))
            keks[keks.index(2)] += 1
            keks[int(next_brick[1])] += 1                    
            foundation = bricks
        
        elif i == 7 and sum(i > 3 for i in keks) > 0 and sum(i == 3 for i in keks) > 1:
            c1 = str(keks.index(3))
            keks[keks.index(3)] += 1
            c2 = str(keks.index(3))
            keks[keks.index(3)] += 1
            next_brick = (c1, c2)                 
            foundation = bricks
            
        elif i == 7 and sum(i > 3 for i in keks) > 0 and sum(i == 7 for i in keks) > 0:
            next_brick = (str(keks.index(7)), str(random.randint(1, 5)))
            keks[keks.index(7)] += 1
            keks[int(next_brick[1])] += 1                    
            foundation = bricks
       
    chain = sum(i > 7 for i in keks)*2 + sum(i > 3 for i in keks)       
    
def find_chain(bricks):
    chain = 0
    keks = [0 for i in range(6)]
    
    for i in range(8):
        keks[int(bricks[i][0])] += 1
        keks[int(bricks[i][1])] += 1
        
        if sum(i > 3 for i in keks) > 2:
            foundation = bricks[:i]
            next_brick = bricks[i]
            moves_set = True
            return [sum(i > 3 for i in keks)], foundation, [next_brick], "hej"

    if sum(i > 3 for i in keks) > 1 and sum(i == 3 for i in keks) > 0:
        colors = [i for i in range(6) if keks[i] == 3]
        randoms = [i for i in range(1, 6) if i not in colors]
        if sum(i == 3 for i in keks) > 1:
            next_brick = [ ( str(colors[0]), str(colors[1]) ), ( str(colors[0]), str(randoms[0]) ), ( str(colors[1]), str(randoms[0]) ) ]
        elif sum(i == 3 for i in keks) == 1:
            next_brick = [ ( str(colors[0]), str(randoms[0]) ) ]
        return [4, 3, 3], bricks, next_brick, colors
    
    elif i == 7 and sum(i > 3 for i in keks) > 1 and sum(i == 3 for i in keks) > 0:
        next_brick = (str(keks.index(3)), str(random.randint(1, 5)))
        keks[keks.index(3)] += 1
        keks[int(next_brick[1])] += 1                    
        foundation = bricks
    
    elif i == 7 and sum(i > 3 for i in keks) > 1 and sum(i == 2 for i in keks) > 0:
        next_brick = (str(keks.index(2)), str(keks.index(2)))
        keks[keks.index(2)] += 1
        keks[int(next_brick[1])] += 1                    
        foundation = bricks
    
    elif i == 7 and sum(i > 3 for i in keks) > 0 and sum(i == 3 for i in keks) > 1:
        c1 = str(keks.index(3))
        keks[keks.index(3)] += 1
        c2 = str(keks.index(3))
        keks[keks.index(3)] += 1
        next_brick = (c1, c2)                 
        foundation = bricks
        
    elif i == 7 and sum(i > 3 for i in keks) > 0 and sum(i == 7 for i in keks) > 0:
        next_brick = (str(keks.index(7)), str(random.randint(1, 5)))
        keks[keks.index(7)] += 1
        keks[int(next_brick[1])] += 1                    
        foundation = bricks
   
def find_moves(grid, chain, foundation, next_brick, first_move = 0):
    safety = list()
    p = player(grid)
    p1 = player(grid)
    for iterations in range(1000):
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
            if score >= 3:
                return mymoves+[move]
            elif p1.currentscore > 70*6:
                safety = mymoves+[move]
    return safety
              
def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def create_possible_grids(grid, bricks, diff_colors):
    keks = [i[0] for i in bricks] + [i[1] for i in bricks]
    keks = [keks.count(str(i)) for i in range(5)]
    alpha = ['a', 'b', 'c', 'd', 'e']
    combos = list()
    possible_grids = list()
    for i in f7(diff_colors):
        combos.append( [q for q in range(5) if keks[q] == i] )

    combis = [subset for subset in itertools.permutations([item for sublist in combos for item in sublist])]
    for x in [i for i in combis if i[0] in combos[0]]:
        newgrid = [list(g) for g in grid]
        for i in range(len(x)):
            for row in range(len(grid)):
                for col in range(len(grid[0])):
                    try:
                        if alpha.index(newgrid[row][col]) == i:
                            newgrid[row][col] = str(x[i])
                    except:
                        continue
        possible_grids.append( newgrid )      
    return possible_grids

def show_grid(grid):
    for i in grid:
        print i
            
def check_viable(p, brick, move, possible_grids): 
    try:
        p.turn(brick, move)
        x, y = p.lastpos1, p.lastpos2
    except:
        return False
    for i in possible_grids:
        if p.grid[x[0]][x[1]] == i[x[0]][x[1]] and p.grid[y[0]][y[1]] == i[y[0]][y[1]]:
            return True
    return False

def change_move(move):
    if move[1] == 1:
        return (move[0], 3)
    elif move[1] == 3:
        return (move[0], 1)
    elif move[1] == 0:
        return (move[0], 2)
    elif move[1] == 2:
        return (move[0], 0)
    
def check_possible_grid(pg, brick):
    moves = [(0, 0), (0,1), (0, 3), (1,0), (1,1), (1,2), (1,3), (2,1), (2,2), (2,3)]
    same_moves = [(0, 0), (0,1), (1,0), (1,1), (2,1)]

    for move in moves:
        p = player( [["." for i in range(3)] for x in range(4)] )
        if check_viable(p, brick[0], move, pg) == False:
            continue   
        for move in moves:
            p1 = player(p.grid)
            if not check_viable(p1, brick[1], move, pg):
                continue
            for move in moves:
                p2 = player(p1.grid)
                if not check_viable(p2, brick[2], move, pg):
                    continue
                for move in moves:
                    p3 = player(p2.grid)
                    if not check_viable(p3, brick[3], move, pg):
                        continue
                    for move in moves:
                        p4 = player(p3.grid)
                        if not check_viable(p4, brick[4], move, pg):
                            continue
                        else:
                            print bricks
                            return
                            
##                        for move in moves:
##                            p5 = player(p4.grid)
##                            if not check_viable(p5, brick[5], move, pg):
##                                continue
##                            for move in moves:
##                                p6 = player(p5.grid)
##                                if not check_viable(p6, brick[6], move, pg):
##                                    continue
##                                else:
##                                    print bricks
##                                    return
    print "DIDNT WORK", bricks
        
if __name__ == '__main__':
    first_move = 0
    first = True
    moves_set = False
    bricks_calculated = list()
    routes = list()
    
    grid_moves = [(1,0), (1,1), (1,3), (2,0), (2,1), (2,2), (2,3), (3,1), (3,2), (3,3)]
    grid_moves2 = [(1,0), (1,1), (1,3), (2,0), (2,1), (2,2), (2,3), (3,0), (3,1), (3,2), (3,3), (4,1), (4,2), (4,3)]
    #find_patterns()
    grid = [['.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.']]

    
    bricks = [('1', '5'), ('4', '2'), ('4', '1'), ('2', '4'), ('5', '4'), ('5', '4'), ('1', '1'), ('5', '4')]

    if first:
        chain, foundation, potential_bricks, colors_needed = find_chain(bricks)
        for i in range(len(potential_bricks)):
            if i == 1 and routes[0] != []:
                first_move = (foundation[0], routes[0][0])
                foundation = foundation[1:]
            routes.append( find_moves(grid, chain[i], foundation, potential_bricks[i], first_move) )
        first = False
        
    if not first and not moves_set:
        if colors[-1][0] in colors_needed or colors[-1][1] in colors_needed:
            for i in range(len(potential_bricks)):
                if colors[-1][0] != potential_bricks[i][0]:
                    routes[i][-1] = change_move(routes[i][-1])        
                if chain[i] == 4:
                    if colors[-1][0] in potential_bricks[i] and colors[-1][1] in potential_bricks[i]:
                        moves = routes[i]
                        moves_set = True
                        break
                elif chain[i] == 3:
                    if colors[-1][0] in potential_bricks[i] or colors[-1][1] in potential_bricks[i]:
                        moves = routes[i]
                        moves_set = True
                        break
        else:
            moves.append( (5, 1) )

    
##    for x in range(100):
##        grid = [['a', 'b', '.'],
##                ['c', 'c', '.'],
##                ['b', 'b', 'c'],
##                ['a', 'a', 'a']]
##        diff_colors = [4,3,3]
##        bricks = [2, 2, 2, 2, 3, 3, 3, 1, 1, 1]
##        random.shuffle(bricks)
##        bricks = [(str(bricks[i]), str(bricks[i+1])) for i in range(0, len(bricks), 2)]
##        check_possible_grid(create_possible_grids(grid, bricks, diff_colors), bricks)


