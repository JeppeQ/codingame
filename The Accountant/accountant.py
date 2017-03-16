import sys
import copy
import math
import time
import random
# Shoot enemies before they collect all the incriminating data!
# The closer you are to an enemy, the more damage you do but don't get too close or you'll get killed.
def distance(p1, p2):
    return math.hypot(p2[0]-p1[0], p2[1]-p1[1])

def dist2(enemy,dp):
    return distance( (enemy.x,enemy.y),(dp.x, dp.y) )
   
def next_point(p1, p2, dist):
    v = (p1[0]-p2[0], p1[1]-p2[1])
    sq = math.sqrt(v[0]**2+v[1]**2)
    return (math.floor(p1[0]-dist*v[0]/sq), math.floor(p1[1]-dist*v[1]/sq))

def bond_entities(enemies,packages):
    for enemy in enemies:
        min_dist = 99999999
        min_package = None
        for dp in packages:
            e_dist = dist2(enemy,dp)
            if e_dist < min_dist:
                min_dist = e_dist
                min_package = dp
        if min_package != None:
            min_package.enemies.append(enemy)
 
def good_man(enemies, packages, pos):
    max_value = 0
    max_enemy = None
    for enemy in enemies:
        value = enemy.nearby_packages(packages) / enemy.time_to_kill(pos)+enemy.time_to_kill(pos)
        if value > max_value:
            max_value = value
            max_enemy = enemy
    return max_enemy
 
def simulate_round(packages):
    unbound_enemies = []
    for package in packages:
        package.move_enemies()
        if package.taken:
            unbound_enemies = unbound_enemies + package.enemies
            packages.remove(package)
    bond_entities(unbound_enemies,packages)
    
class Enemy:
    def __init__(self,enemy_id,enemy_x,enemy_y,enemy_life):
        self._id = enemy_id
        self.x = enemy_x
        self.y = enemy_y
        self.life = enemy_life
        self.pos = (self.x, self.y)

    def update_life(self, life):
        self.life = enemy_life
        
    def point(self):
        return (self.x,self.y)
   
    def move(self, point):
        self.x = point[0]
        self.y = point[1]
        self.pos = (self.x, self.y)
       
    def turns_to_datapacket(self,dp):
        return math.ceil(distance(self.x,dp.x,self.y,dp.y)/500.)
       
    def nearby_packages(self, packages, limit=2000):
        nearby_packages = []
        for package in packages:
            if dist2(self,package) < limit:
                nearby_packages.append(package)
        return len(nearby_packages)
       
    def time_to_kill(self, pos):
        return math.ceil(self.life / round(125000/(distance(pos, self.pos)**1.2)))
 
class Datapackage:
    def __init__(self, data_id, data_x, data_y):
        self._id = data_id
        self.x = data_x
        self.y = data_y
        self.enemies = []
        self.taken = False
   
    def point(self):
        return (self.x, self.y)
           
    def move_enemies(self):
        dp_point = self.point()
        for enemy in self.enemies:
            if enemy.life <= 0:
                self.enemies.remove(enemy)
            dist = distance(enemy.pos, dp_point)
            if dist < 500:
                enemy.move(dp_point)
                self.taken = True
            else:
                enemy.move(next_point(enemy.point(),dp_point,500))
           
class Player:
    
    def __init__(self, x, y, packages):
        self.startpos = (x, y)
        self.packages = packages
        
    def update_pos(self, x, y):
        self.pos = (x, y)
    
    def reset_player(self, packages):
        self.kills = 0
        self.shots = 0
        self.pos = self.startpos
        self.packages = packages
    
    def set_target(self, target):
        self.target = target
        
    def target_distance(self):
        turns = 0
        self.saved_positions = [self.pos]
        dmg_done = [[]]
        
        if distance( self.pos, self.target.pos ) < 2001:
            self.pos = next_point(self.pos, self.target.pos, -1000)
            simulate_round(self.packages)
            
        while sum(dmg_done[0]) < self.target.life:
            if self.pos != self.saved_positions[-1]:
                self.saved_positions.append(self.pos)
                dmg_done.append(list())
            for i in range(len(self.saved_positions)):
                if sum(dmg_done[i]) < self.target.life:
                    dmg_done[i].append( self.damage( self.saved_positions[i] ) )
            if distance( self.pos, self.target.pos ) > 2000:
                self.pos = next_point( self.pos, self.target.pos, 1000 )
            simulate_round(self.packages)
        dmg = list(reversed([len(i)+dmg_done.index(i) if sum(i) >= self.target.life else 500 for i in dmg_done]))
        self.kills += 1
        self.shots += min(dmg) - dmg.index(min(dmg))
        return self.saved_positions[ dmg.index(min(dmg)) ]
    
    def target_turns(self):
        return self.target_distance() + self.kill()
        
    def damage(self, pos):
        return round(125000/(distance(pos, self.target.pos)**1.2))
        
class Path:

    def __init__(self, p, enemies, packages):
        self.player = p
        self.enemies = enemies
        self.total_life = sum([e.life for e in self.enemies])
        self.packages = packages
        self.og_enemies = copy.deepcopy(self.enemies)
        self.og_packages = copy.deepcopy(self.packages)
    
    def move_to_enemy(self, enemy):
        self.player.set_target(enemy)
        self.player.update_pos(*self.player.target_distance())

    def reset_stuff(self):
        self.enemies = copy.deepcopy(self.og_enemies)
        self.packages = copy.deepcopy(self.og_packages)
        
    def next_enemy(self, enemies):
        if not len(enemies) or not self.packages:
            return

        nt = good_man(enemies, self.packages, self.player.pos)
        self.move_to_enemy(nt)
        self.path.append(nt)
        enemies.remove(nt)
        self.next_enemy( enemies )
    
    def path(self):
        bestscore = 0
        bestpath = 0
        for enemy in self.og_enemies:
            self.reset_stuff()
            self.player.reset_player(self.packages)
            self.path = [enemy]
            self.move_to_enemy(enemy)
            self.next_enemy(list([e for e in self.enemies if e != enemy]) )
            
            score = len(self.packages)*100+self.player.kills*10+\
                    len(self.packages)*max(0, (self.total_life - 3*self.player.shots)) * 3
                    
            if score > bestscore:
                bestscore = score
                bestpath = list(self.path)
        return bestpath

    def kill_enemy(self, enemy):
        bestvalue = 0
        bestmoves = list()
        life = enemy.life
        self.player.set_target(enemy)
        start = int(round(time.time() * 1000))
        while int(round(time.time() * 1000)) - start < 95:
            value = 0
            moves = list()
            self.reset_stuff()
            enemy.life = life
            self.player.reset_player(self.packages)
            while enemy.life > 0:
                if random.randint(0, 1):
                    enemy.life -= self.player.damage(self.player.pos)
                    moves.append("shoot")
                else:
                    self.player.pos = next_point( self.player.pos, enemy.pos, 1000 )
                    moves.append( self.player.pos )
                simulate_round(self.packages)
                
                if True in [distance(self.player.pos, enemie.pos) < 2500 for enemie in self.enemies]:
                    value -= 200000000
                    break

            value += len(self.packages)*100 - moves.count("shoot")*2 - len(moves)
            if value > bestvalue:
                bestvalue = value
                bestmoves = list(moves)
        
        if bestmoves[0] == 'shoot':
            return "SHOOT %s" % (str(enemy._id))
        else:
            return "MOVE %s %s" % (str(int(bestmoves[0][0])), 
                                    str(int(bestmoves[0][1])))
        
# game loop
init = True
while True:
    x, y = [int(i) for i in raw_input().split()]
    data_count = int(raw_input())
    packages = [Datapackage(*[int(j) for j in raw_input().split()]) for i in xrange(data_count)]
    enemy_count = int(raw_input())
    enemies = [Enemy(*[int(j) for j in raw_input().split()]) for i in xrange(enemy_count)]
    bond_entities(enemies, packages)
    player = Player(x,y,packages)
    path = Path(player, enemies, packages)
    if init:
        mypath = path.path()
        init = False
        print path.kill_enemy(mypath[0])
    else:
        mypath = [mp for mp in mypath if mp._id in [i._id for i in enemies]]
        if len(mypath) < 1:
            print "MOVE 5000 5000"
        print path.kill_enemy([i for i in enemies if i._id == mypath[0]._id][0])
