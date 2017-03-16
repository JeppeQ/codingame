import sys
import math
import itertools as it

def distance(p1, p2):
    return math.hypot(p2[0]-p1[0], p2[1]-p1[1])

def reversecoord(p):
    return (16000-p[0], 9000-p[1])

def revID(i):
    if i % 2 == 0:
        return i-1
    else:
        return i+1
    
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
    
def move_away(p1, p2, dist):
    return next_point(p1, p2, -dist)

def best_targets(n):
    ghost_distance = list()
    loweststam = 40
    for i in ghosts:
        loweststam = min(loweststam, ghosts[i]['stamina'])
        dist = distance(home_coords, ( ghosts[i]['x'], ghosts[i]['y'] ))
        turns = (max(0, dist-1760)//800+1) + ghosts[i]['stamina']
        if i in currentghosts:
            turns -= 5
        ghost_distance.append( (max(0, turns), i) )
    if loweststam == 40:
        n = 1
    return [i[1] for i in sorted(ghost_distance)][:n]
    
def assign_targets(targets, bindex):
    bindex.sort()
    original_targets = list(targets)
    bestdist = 999999
    lowturns = 999
    if len(targets) == len(bindex):
        for i in it.permutations(targets):
            currentdist = 0
            for x in i:
                dist = distance( (busters[bindex[i.index(x)]]['x'], busters[bindex[i.index(x)]]['y']),
                                         (ghosts[x]['x'], ghosts[x]['y']) )
                if dist < 1760:
                    dist -= 500
                currentdist += dist
                turns = (max(0, currentdist-1760)//800+1) + ghosts[x]['stamina']
                #print >> sys.stderr, turns, rounds
                if turns > rounds:
                    currentdist = 9999999
                    break
            if currentdist < bestdist:
                bestdist = currentdist
                targets = i
        if bestdist == 999999 and len(original_targets) > 1:
            #print >> sys.stderr, "WOOP"
            return assign_targets(original_targets[:-1], bindex)
        
    else:
        for product in [i for i in it.product(targets, repeat=len(bindex)) if len(set(i)) == len(targets)]:
            currentturns = 0
            for i in product:
                avg = sum([distance( (ghosts[i]['x'], ghosts[i]['y']), (busters[bindex[product.index(x)]]['x'], busters[bindex[product.index(x)]]['y']) )//800+1 for x in product if x == i])/product.count(i)
                turncount = ghosts[i]['stamina']/product.count(i)+1+avg
                if turncount > currentturns:
                    currentturns = turncount
            if currentturns < lowturns:
                lowturns = currentturns
                targets = product
        if lowturns > rounds and len(original_targets) > 1:
            return assign_targets(original_targets[:-1], bindex)
            
    return targets


def find_him(buster):
    pos = (busters[buster]['x'], busters[buster]['y'])
    for i in oppbust:
        if distance( (oppbust[i]['x'], oppbust[i]['y']), (busters[buster]['x'], busters[buster]['y']) ) < 1760 and stuncd[int(buster)-bonus] < 1:
            if oppbust[i]['state'] == 1:
                stuncd[int(buster)-bonus] = 20
                oppbust[i]['state'] = 2
                oppbust[i]['value'] = 10
                print "STUN "+i+" nope"
                return 1
    if stun_opp(buster):
        return
    
    for i in oppbust:
        if oppbust[i]['state'] == 1:
            print "MOVE "+str(oppbust[i]['x'])+" "+str(oppbust[i]['y'])
            return 1
            
    #SCATTER
    scatter = ["MOVE " +str(opp_base[0])+" "+ str(opp_base[1]) +" SCATTER", "MOVE 16000 0", "MOVE 0 9000", "MOVE 8000 4500"]
    print scatter[int(buster)-bonus]

def add_ep_to_stolen(pos, target):
    closest = 99999
    ep = opp_base
    for i in oppbust:
        if oppbust[i]['state'] == 2:
            continue
        dist = distance( pos, (oppbust[i]['x'], oppbust[i]['y']) )
        if dist < closest:
            closest = dist
            ep = (oppbust[i]['x'], oppbust[i]['y'])
    if closest > 2200:
        print >> sys.stderr, "going around boys"
        mp = next_point(pos, home_coords, 800)
        ep = next_point(ep, mp, 800)
        stolen_ghosts[target]['ep'] = (int(ep[0]), int(ep[1]))
    
def move_to_target(buster, target):
    pos = (busters[buster]['x'], busters[buster]['y'])
    if target in currentghosts:
        dist = distance( pos, (currentghosts[target]['x'], currentghosts[target]['y']) )
        if dist < 2200:
            if combat_on_target(buster, target):
                return 1
            if dist < 1760 and dist > 899:
                print "BUST " + target
                if target in stolen_ghosts:
                    add_ep_to_stolen(pos, target)
                return 1
            else:
                move = move_to_ghost( pos, (currentghosts[target]['x'],currentghosts[target]['y']) )
                print "MOVE " + str(int(move[0])) + " " +str(int(move[1]))
                return 1
    if stun_opp(buster):
        return 1
    elif pos[0] == ghosts[target]['x'] and pos[1] == ghosts[target]['y']:
        targets_to_be_removed.append( target )
        print "MOVE "+str(home_coords[0])+" "+str(home_coords[1])
    else:
        print "MOVE "+str(ghosts[target]['x'])+" "+str(ghosts[target]['y'])

def roadpoints(pos, target, road):
    if distance(pos, target) < 1600:
        return road
    else:
        road.append( (int(pos[0]), int(pos[1])) )
        return roadpoints(next_point(pos, target, 800), target, road)

def ETA(pos, target, turns):
    for i in range(turns):
        pos = next_point(pos, target, 800)
        if distance(pos, target) < 1760:
            return 1
    return 0
    
def resteal(buster):
    pos = (oppcarries[buster]['x'], oppcarries[buster]['y'])
    lowturn = 999
    #Calculate their roads
    for i in busters:
        mypos = (busters[i]['x'], busters[i]['y'])
        if busters[i]['state'] != 1 and busters[i]['state'] != 2:
            rp = roadpoints(pos, opp_base, [])
            for point in range(0+max(stuncd[int(i)-bonus],0), len(rp)):
                if ETA(mypos, rp[point], point) and point < lowturn and i not in [x[0] for x in stealers]:
                    lowturn = point
                    mybest = i
                    predist = rp[point-1]
                    destination = rp[point]
    if lowturn == 999:
        return []
    else:
        return (mybest, destination, predist)
    
    
def punch(buster):
    pos = (busters[buster]['x'], busters[buster]['y'])
    bestdist = 99999
    target = 999
    for i in ghosts:
        dist = distance( (busters[str(buster)]['x'], busters[str(buster)]['y']), 
                                         (ghosts[i]['x'], ghosts[i]['y']) )
        if dist < bestdist:
            bestdist = dist
            target = i
    if target != 999:
        if target in currentghosts:
            dist = distance( pos, (currentghosts[target]['x'], currentghosts[target]['y']) )
            if dist < 2200:
                if dist < 1760 and dist > 899:
                    print "BUST " + target
                    return 1
                else:
                    move = move_to_ghost( pos, (currentghosts[target]['x'],currentghosts[target]['y']) )
                    print "MOVE " + str(int(move[0])) + " " +str(int(move[1]))
                    return 1
        if stun_opp(buster):
            return 1
        elif pos[0] == ghosts[target]['x'] and pos[1] == ghosts[target]['y']:
            targets_to_be_removed.append( target )
            print "MOVE "+str(home_coords[0])+" "+str(home_coords[1])
        else:
            print "MOVE "+str(ghosts[target]['x'])+" "+str(ghosts[target]['y'])
    else:    
        print "MOVE 8000 4500"

#This is how you program.
def initialscout(buster):
    global iniscout
    if bc == 2:
        num = [[242, 240, 237], [244, 237]]
        if not base:
            routes = [[(1500, 7500), (3000, 7500), (3000, 5000)],
                      [(6500, 1600), (6500, 7500)]]          
        else:
            routes = [[(14500, 1500), (13000, 1500), (13000, 4000)],
                      [(9500, 7400), (9500, 1500)]]
    elif bc == 3:
        num = [[240], [244, 240], [243, 240]]
        if not base:
            routes = [[(6500, 7500)],
                      [(6500, 1600), (6500, 7500)], 
                     [(1500, 7500), (6000, 7500)]]          
        else:
            routes = [[(9500, 1500)],
                      [(9500, 7400), (9500, 1500)], 
                     [(14500, 1500), (10000, 1500)]]
    
    elif bc == 4:
        num = [[240], [244, 240], [243, 240], ['6yu57']]
        if not base:
            routes = [[(6500, 7500)],
                      [(6500, 1600), (6500, 7500)], 
                     [(1500, 7500), (6000, 7500)],
                     []]          
        else:
            routes = [[(9500, 1500)],
                      [(9500, 7400), (9500, 1500)], 
                     [(14500, 1500), (10000, 1500)],
                     []]

    for i in num[int(buster)-bonus]:
        if int(buster)-bonus == 3:
            punch('3')
            return 1
        elif bc == 4 and int(buster)-bonus == -1:
            punch('7')
            return 1
        if rounds > i:
            print "MOVE " + str(routes[int(buster)-bonus][num[int(buster)-bonus].index(i)][0])+" "+str(routes[int(buster)-bonus][num[int(buster)-bonus].index(i)][1])
            return 1
    return 0

def stun_opp(buster):
    for i in oppbust:
        if distance( (oppbust[i]['x'], oppbust[i]['y']), (busters[buster]['x'], busters[buster]['y']) ) < 1760 and stuncd[int(buster)-bonus] < 1:
            if oppbust[i]['state'] == 2 and oppbust[i]['value'] > 0:
                continue
            if oppbust[i]['state'] == 0 and oppstuncd[int(i)-bc+bonus] > 2:
                continue
            try:
                if oppbust[i]['state'] == 3 and ghosts[str(oppbust[i]['value'])]['stamina'] > 9 and oppstuncd[int(i)-bc+bonus] > 2:
                    continue
            except:
                continue
            stuncd[int(buster)-bonus] = 20
            oppbust[i]['state'] = 2
            oppbust[i]['value'] = 10
            print "STUN "+i
            return 1
    return 0

def go_for_stun(buster, target):
    move = move_away( (currentghosts[target]['x'], currentghosts[target]['y']), (busters[buster]['x'], busters[buster]['y']), 800)
    print "MOVE " + str(int(move[0])) + " " +str(int(move[1]))

def bait_stun(buster, target):
    for i in oppbust:
        dist = distance( (oppbust[i]['x'], oppbust[i]['y']), (busters[buster]['x'], busters[buster]['y']) ) 
        if dist < 2200:
            if oppbust[i]['state'] == 2:
                return 0
            else:
                print "MOVE "+str(oppbust[i]['x'])+" "+str(oppbust[i]['y'])
                return 1
    go_for_stun(buster, target)
    return 1
    
def equal_fight(buster, target, opp):
    hp = currentghosts[target]['stamina']
    nostun = False
    inrange = False
    stun = stuncd[int(buster)-bonus]
    
    for i in oppbust:
        dist = distance( (oppbust[i]['x'], oppbust[i]['y']), (busters[buster]['x'], busters[buster]['y']) ) 
        if dist < 2200:
            if dist < 1760:
                inrange = True
                
            if oppstuncd[int(i)-bc+bonus] > 1:
                nostun = True
             
    #Bait stun
    if hp/opp > 9 and hp/opp < 20 and not nostun:
        if bait_stun(buster, target):
            return 1
        else:
            return 0
    #Opp doesn't have stun.
    elif hp < 10 and nostun and stun < 2:
        go_for_stun(buster, target)
        return 1
    #Trade Stuns
    elif hp < 10 and inrange and stun < 1:
        if stun_opp(buster):
            return 1
        else:
            return 0
    #Bust ghost until 0
    elif hp > 0 and not inrange:
        return 0
    #Go for stun trades
    elif hp == 0 and not inrange and stun < 1:
        go_for_stun(buster, target)
        return 1
    return 0

def advantage_fight(buster, target):
    for i in oppbust:
        dist = distance( (oppbust[i]['x'], oppbust[i]['y']), (busters[buster]['x'], busters[buster]['y']) ) 
        ghostdist = distance( (oppbust[i]['x'], oppbust[i]['y']), (ghosts[target]['x'], ghosts[target]['y']) )
        if ghostdist < 1760 and dist < 1760 and oppbust[i]['state'] != 2 and oppstuncd[int(i)-bc+bonus] < 1 and stuncd[int(buster)-bonus] < 1:
            if oppbust[i]['state'] == 2 and oppbust[i]['value'] > 1:
                continue
            stuncd[int(buster)-bonus] = 20
            oppbust[i]['state'] = 2
            oppbust[i]['value'] = 10
            print "STUN "+i
            return 1
    return 0
    
def combat_on_target(buster, target):
    mybusters = globaltargets.count(target)
    for i in busters:
        if distance( (busters[i]['x'], busters[i]['y']), (busters[buster]['x'], busters[buster]['y']) ) < 2200:
            if busters[i]['state'] == 2:
                mybusters += 1
    
    oppbusters = max(currentghosts[target]['value'] - mybusters, 0)
    for i in oppbust:
        if distance( (oppbust[i]['x'], oppbust[i]['y']), (busters[buster]['x'], busters[buster]['y']) ) < 2200:
            if oppbust[i]['state'] != 2 and oppbust[i]['state'] != 3 and oppstuncd[int(i)-bc+bonus] < 1: 
                oppbusters+=1
            if oppbust[i]['state'] == 3:
                oneopponent = i
            
    #print >> sys.stderr, oppbusters, mybusters+extra
    #No opponents
    if oppbusters == 0:
        return 0
    #Equal fight
    elif oppbusters == mybusters:
        if equal_fight(buster, target, oppbusters):
            return 1
        else:
            return 0
    #Advantage
    elif oppbusters < mybusters:
        print >> sys.stderr, "ADVANTAGE"
        if advantage_fight(buster, target):
            return 1
        else:
            return 0
    #Disadvantage
    elif oppbusters > mybusters:
        add_future_carry(target, oppbusters, buster)
        if stun_opp(buster):
            return 1
        if dodge(buster):
            return 1
        else:
            move = move_away( (busters[buster]['x'], busters[buster]['y']), (ghosts[target]['x'], ghosts[target]['y']), 800 )
            print "MOVE "+str(int(move[0]))+" "+str(int(move[1]))
            return 1
    return 0

def add_future_carry(target, opp, buster):
    closest = 9999
    non_focus = 9999
    non_carry = 999
    carry = 999
    for i in oppbust:
        if oppbust[i]['state'] == 3 and str(oppbust[i]['value']) == target: 
            dist = distance( (oppbust[i]['x'], oppbust[i]['y']), (ghosts[target]['x'], ghosts[target]['y']) )
            if dist < closest:
                closest = dist
                carry = i
        else:
            dist = distance( (oppbust[i]['x'], oppbust[i]['y']), (ghosts[target]['x'], ghosts[target]['y']) )
            if dist < non_focus:
                non_focus = dist
                non_carry = i
    if carry != 999:
        dominated.append( [target, ghosts[target]['stamina']/opp+1, carry, oppbust[carry] ] )
    elif non_carry != 999:
        dominated.append( [target, ghosts[target]['stamina']/opp+1, non_carry, oppbust[non_carry] ] )
    else:
        dummycoords = move_away( (ghosts[target]['x'], ghosts[target]['y']), (busters[buster]['x'],busters[buster]['y']), 1400) 
        dummy = {'id':Id, 'x':int(dummycoords[0]),'y':int(dummycoords[1]),'state':1,'value':value}
        dominated.append( [target, ghosts[target]['stamina']/opp+1, first_guy, dummy] )
        
def go_for_steal(stuff):
    buster = stuff[0]
    target = stuff[1]
    
    for i in oppbust:
        if distance( (oppbust[i]['x'], oppbust[i]['y']), (busters[buster]['x'], busters[buster]['y']) ) < 1760 and stuncd[int(buster)-bonus] < 1:
            if oppbust[i]['state'] == 1:
                stuncd[int(buster)-bonus] = 20
                oppbust[i]['state'] = 2
                nexp = next_point( (oppbust[i]['x'], oppbust[i]['y']), opp_base, 800 )
                ghosts[str(oppbust[i]['value'])] = {'x':int(nexp[0]),'y':int(nexp[1]), 'stamina':0, 'value':-1}
                stolen_ghosts[ str(oppbust[i]['value']) ] = {'ep':opp_base}
                oppbust[i]['value'] = 10
                print "STUN "+i+" I'll take that one"
                return 1
    print "MOVE " + str(int(target[0])) + " "+str(int(target[1]))    
    
def check_edge(pos, ep, to_base):
    bestdist = 0
    home_close = 99999
    homepoint = 2000
    for i in range(360):
        x = min(16000, max(pos[0] + 800 * math.cos(math.radians(i)), 0))
        y = min(9000, max(pos[1] + 800 * math.sin(math.radians(i)), 0))
        if distance(ep, (x,y)) > bestdist:
            bestdist = distance(ep, (x,y))
            point = (x,y)
        if distance( (x, y), home_coords) < home_close and distance( (x,y), next_point(ep, pos, 800) ) > 2199:
            home_close = distance( (x, y), home_coords)
            homepoint = (x,y)
    if to_base and homepoint != 2000:
        return homepoint
    else:
        return point

def home_dodge(pos, ep):
    home_close = 99999
    homepoint = 2000
    for i in range(360):
        x = min(16000, max(pos[0] + 800 * math.cos(math.radians(i)), 0))
        y = min(9000, max(pos[1] + 800 * math.sin(math.radians(i)), 0))
        if distance( (x, y), home_coords) < home_close and distance( (x,y), ep ) > 2199:
            home_close = distance( (x, y), home_coords)
            homepoint = (x,y)
    if homepoint != 2000:
        print "MOVE "+str(int(homepoint[0]))+" "+str(int(homepoint[1]))
        return 1
    else:
        return 0
    
def dodge(mybuster):
    pos = (busters[mybuster]['x'], busters[mybuster]['y'])
    danger = False
    for buster in oppbust:
        if distance( pos, (oppbust[buster]['x'],oppbust[buster]['y']) ) < 2200 and oppbust[buster]['state'] != 2 and oppbust[buster]['state'] != 1 and oppstuncd[int(buster)-bc+bonus] < 2:
            print >> sys.stderr, "I see one"
            danger = True
            emergencypoint = (oppbust[buster]['x'],oppbust[buster]['y'])
            if busters[mybuster]['state'] == 1:
                move = check_edge(pos, emergencypoint, True)
            else:
                move = check_edge(pos, emergencypoint, False)
                
            if (distance( (oppbust[buster]['x'],oppbust[buster]['y']), pos ) < 1760 or distance( move, emergencypoint ) < 1760) and stuncd[int(mybuster)-bonus] < 1:
                print "STUN "+buster+" Final Spark!"
                stuncd[int(mybuster)-bonus] = 20
                oppbust[buster]['state'] = 2
                oppbust[buster]['value'] = 10
                return 1
    if danger:
        print "MOVE " + str(int(move[0])) + " " +str(int(move[1])) + " Not Today!"
        return 1
    return 0
    
def get_home(buster):
    global victory
    pos = (busters[buster]['x'], busters[buster]['y'])
    if distance(pos, home_coords) < 1600:
        victory -= 1
        print "RELEASE "+str(victory)+" more!"
        return
    elif dodge(buster):
        return
    elif distance(pos, home_coords) < 2400:
        move = next_point(pos, home_coords, int(distance(pos, home_coords))-1590)
        print "MOVE "+str(int(move[0]))+" "+str(int(move[1]))+" just one more step.."
        return
    elif str(busters[buster]['value']) in stolen_ghosts:
        if home_dodge(pos, stolen_ghosts[str(busters[buster]['value'])]['ep']):
            return
    print "MOVE "+str(home_coords[0])+" "+str(home_coords[1])
    
def protect(buster):
    if stun_opp(buster):
        return
    
    bestdist = 99999
    for i in busters:
        if busters[i]['state'] == 1:
            dist = distance( (busters[buster]['x'], busters[buster]['y']), (busters[i]['x'], busters[i]['y']) )
            if dist < bestdist:
                bestdist = dist
                target = i
    point = next_point( (busters[target]['x'], busters[target]['y']), home_coords, 800)
    print "MOVE "+str(int(point[0]))+" "+str(int(point[1]))
    
def pregnant():
    num = 0
    for buster in busters:
        if busters[buster]['state'] == 1:
            num+=1
    return num

def potential_base_camp():
    if dodge(buster):
        return
    if len(oppbust) < 1:
        for i in range(bc):
            pos = (busters[str(i+bonus)]['x'], busters[str(i+bonus)]['y'])
            if busters[str(i+bonus)]['state'] == 1 and distance( pos, home_coords )/800-1 > rounds:
                if distance( pos, (16000, 0) ) < distance( pos, (0, 9000) ):
                    print "MOVE 16000 0"
                else:
                    print "MOVE 0 9000"
            else:
                protect(str(i+bonus))
    else:
        return 0
 
def is_reachable(bindex, targets):
    reachable = list()
    for i in targets:
        avg = sum([distance( (ghosts[i]['x'], ghosts[i]['y']), (busters[x]['x'], busters[x]['y']) )/800+1 for x in bindex if targets[bindex.index(x)] == i]) / targets.count(i)
        turncount = ghosts[i]['stamina']/targets.count(i)+1+avg
        reachable.append( turncount < rounds )
    return reachable
    
def main():
    global globaltargets
    
    if rounds > scoutnum[bc-2]:
        for i in range(bc):
            initialscout(i)
    else:
        if victory-pregnant() < 1:
            #Potential base camp?
            if len(oppbust) < 1 and rounds < 10:
                potential_base_camp()
            else:
                for i in range(bc):
                    if busters[str(i+bonus)]['state'] == 1:
                        get_home(str(i+bonus))
                    else:
                        protect(str(i+bonus))
        else:
            for opp in oppcarries:
                if oppcarries[opp]['state'] == 1:
                    stealer = resteal(opp)
                    if len(stealer) > 0:
                        stealers.append(stealer)
            func_busters = [i for i in busters if busters[i]['state'] != 2 and busters[i]['state'] != 1 and i not in [x[0] for x in stealers]]
            besttargets = best_targets( min(victory, len(func_busters)) )
            targets = list(assign_targets(besttargets, func_busters))
            globaltargets = list(targets)
            if len(func_busters)+pregnant() == bc:
                reachable = is_reachable( func_busters, targets )
            else:
                reachable = [True for i in range(bc)]
            print >> sys.stderr, targets
            for i in range(bc):
                if busters[str(i+bonus)]['state'] == 1:
                    get_home(str(i+bonus))
                elif busters[str(i+bonus)]['state'] == 2:
                    print "MOVE 1337 1337"
                elif str(i+bonus) in [x[0] for x in stealers]:
                    go_for_steal(stealers[ [x[0] for x in stealers].index(str(i+bonus)) ])
                elif len(targets) != 0 and reachable[0]:
                    reachable = reachable[1:]
                    move_to_target(str(i+bonus), targets.pop(0))
                elif pregnant() > 0:
                    protect(str(i+bonus))
                else:
                    find_him(str(i+bonus))


bc = int(raw_input())  # the amount of busters you control
ghost_count = int(raw_input())  # the amount of ghosts on the map
base = int(raw_input())  # if this is 0, your base is on the top left of the map, if it is one, on the bottom right
if base:
    home_coords = (16000, 9000)
    opp_base = (0, 0)
    first_guy = '0'
    bonus = bc
else:
    home_coords = (0, 0)
    first_guy = str(bc)
    opp_base = (16000, 9000)
    bonus = 0

# game loop
ghosts = dict()
busters = dict()
prevghost = dict()
oppcarries = dict()
stuncd = [0 for i in range(bc)]
iniscout = True
start = True
mirror = [1, -1]
rounds = 250
victory = ghost_count / 2 +1
oppstuncd = [0 for i in range(bc)]
scoutnum = [237, 240, 240]
dominated = list()
globaltargets = list()
stolen_ghosts = dict()

while True:
    targets_to_be_removed = list()
    rounds -= 1
    oppstuncd = [i-1 for i in oppstuncd]
    stuncd = [i-1 for i in stuncd]
    currentghosts = dict()
    oppbust = dict()
    stealers = list()
    entities = int(raw_input())  # the number of busters and ghosts visible to you
    if rounds == 187:
        for ghous in [i for i in ghosts if distance( (ghosts[i]['x'], ghosts[i]['y']), opp_base) < 8000 and ghosts[i]['stamina'] == 3]:
            del ghosts[ghous]
    
    for i in xrange(entities):
        Id, x, y, Type, state, value = [int(j) for j in raw_input().split()]
        if Type == base:
            busters[str(Id)] = {'id':Id, 'x':x,'y':y,'state':state,'value':value}
            if state == 1 and str(value) in ghosts:
                del ghosts[str(value)]
        elif Type == -1:
            if str(Id) not in ghosts and str(revID(Id)) not in ghosts and scoutnum[bc-2] < rounds:
                if Id != 0:    
                    rc = reversecoord((x,y))
                    ghosts[str(revID(Id))] = {'x':rc[0],'y':rc[1], 'stamina':state, 'value':value}
            if str(Id) not in [gem[0] for gem in dominated]:
                ghosts[str(Id)] = {'x':x,'y':y, 'stamina':state, 'value':value}
                currentghosts[str(Id)] = {'x':x,'y':y, 'stamina':state, 'value':value}
        else:
            oppbust[str(Id)] = {'id':Id, 'x':x,'y':y,'state':state,'value':value}
            oppcarries[str(Id)] = {'id':Id, 'x':x,'y':y,'state':state,'value':value, 'cd':0}
            if state == 1 and str(value) in ghosts:
                del ghosts[str(value)]
    
    for i in dominated:
        if i[0] in ghosts:
            del ghosts[i[0]]
        i[1] -= 1
        if i[1] == 0:
            oppcarries[i[2]] = i[3]
            oppcarries[i[2]]['state'] = 1
    dominated = [i for i in dominated if i[1] > 0]
        
    for opp in oppcarries:
        if oppcarries[opp]['state'] == 1 and opp not in oppbust:
            nexp = next_point( (oppcarries[opp]['x'], oppcarries[opp]['y']), opp_base, 800)
            oppcarries[opp]['x'], oppcarries[opp]['y'] = int(nexp[0]), int(nexp[1])
            if distance( (oppcarries[opp]['x'], oppcarries[opp]['y']), opp_base) < 1600:
                oppcarries[opp]['state'] = 0
    
    print >> sys.stderr, stuncd
    #Try to keep track of opponents stuns
    for buster in busters:
        if busters[buster]['state'] == 2 and busters[buster]['value'] > 9:
            if len([gem for gem in oppbust if distance( (oppbust[gem]['x'], oppbust[gem]['y']), (busters[buster]['x'], busters[buster]['y']) ) < 1760 and oppstuncd[int(gem)-bc+bonus] < 1]) > 1:
                break
            for opp in range(bc):
                if str(opp+bc-bonus) in oppbust:
                    if oppstuncd[opp] < 0 and distance( (oppbust[str(opp+bc-bonus)]['x'], oppbust[str(opp+bc-bonus)]['y']), (busters[buster]['x'], busters[buster]['y']) ) < 1760:
                        oppstuncd[opp] = 20
                        break
    
    #Some ghosts might have moved away or just gone
    for buster in busters:
        for ghost in ghosts:
            if distance( (busters[buster]['x'], busters[buster]['y']), (ghosts[ghost]['x'], ghosts[ghost]['y']) ) < 2200 \
            and ghost not in currentghosts and ghost in prevghost and prevghost[ghost]['value'] == 0:
                point = move_away( (ghosts[ghost]['x'], ghosts[ghost]['y']), (busters[buster]['x'], busters[buster]['y']), 400 )
                ghosts[ghost]['x'], ghosts[ghost]['y'] = min(16000, max(int(point[0]),0)), min(9000, max(int(point[1]),0))
        for bulgu in [q for q in ghosts if distance( (busters[buster]['x'], busters[buster]['y']), (ghosts[q]['x'], ghosts[q]['y']) ) < 1000 and q not in currentghosts]:
            del ghosts[bulgu]            
                                
    main()
    for rt in targets_to_be_removed:
        if rt in ghosts:
            del ghosts[rt]
    prevghost = currentghosts
    
                
