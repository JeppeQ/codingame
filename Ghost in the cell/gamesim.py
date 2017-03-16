import math
import random
import pickle
import copy
import numpy as np
import time
from keras.models import Sequential

def distance(p1, p2):
    return int(round(math.hypot(p2[0]-p1[0], p2[1]-p1[1])))

def valid_pos(factories, position):
    for p in factories:
        if distance(p, position) < 1 or distance(p, position) > 20:
            return False
    return True

def vulnerability(_id, factories, distances):
    vulnerable = 0
    my_factories = [i for i in factories if i[0] == _id]
    for f in my_factories:
        vul_level = -f[1]
        for all in factories:
            if all[4] == f[4]:
                continue
            if all[0] not in [0,_id]:
                vul_level += all[1] / distances[f[4]][all[4]]
        vulnerable += vul_level
    return vulnerable

def get_features(_id, state, future=False):
    factories, troops, distances = copy.deepcopy(state)
    #print (factories)
    #print (troops)
    #print (troops)
    opp = 2 if _id == 1 else 1
    #CURRENT FEATURES
    current_P = sum([i[2] for i in factories if i[0] == _id]) - sum([i[2] for i in factories if i[0] == opp])
    current_T = (sum([i[1] for i in factories if i[0] == _id]) + sum([i[3] for i in troops if i[0] == _id])) - \
                (sum([i[1] for i in factories if i[0] == opp]) + sum([i[3] for i in troops if i[0] == opp]))
    availeble_T = sum([i[1] for i in factories if i[0] == _id]) - sum([i[1] for i in factories if i[0] == opp])
    Travel_T = max([i[3] for i in troops if i[0] == _id]+[0]) - max([i[1] for i in factories if i[0] == opp]+[0])
    current_V = vulnerability(_id, factories, distances)-vulnerability(opp, factories, distances)

    product = [0, 0]
    troopaloopa = [0, 0]
    alternative_facts = [[],[]]
    longest_D = [0, 0] #it's okay
    while len([i for i in troops if i[4] > 0]) > 0:
        battles = [[0, 0, 0] for i in range(len(factories))]

        # move troops
        for troop in troops:
            troop[4] -= 1
        # decrease factory cd
        for f in factories:
            if f[3] > 0:
                f[3] -= 1

        # create new units
        for f in factories:
            if f[0] != 0 and f[3] == 0:
                f[1] += f[2]

        # solve battles
        for troop in troops:
            if troop[4] <= 0:
                if troop[0] == factories[troop[2]][0]:
                    battles[troop[2]][0] += troop[3]
                else:
                    if troop[0] != 0 and battles[troop[2]][2] != troop[0]:
                        if troop[3] > battles[troop[2]][1]:
                            battles[troop[2]][1] = troop[3] - battles[troop[2]][1]
                            battles[troop[2]][2] = troop[0]
                        elif troop[3] < battles[troop[2]][1]:
                            battles[troop[2]][1] -= troop[3]
                        else:
                            battles[troop[2]] = [0, 0, 0]
                    else:
                        battles[troop[2]][1] += troop[3]
                        battles[troop[2]][2] = troop[0]

        for f in range(len(factories)):
            factory = factories[f]
            if battles[f][0] + factory[1] >= battles[f][1]:
                factory[1] = (factory[1] + battles[f][0]) - battles[f][1]
            else:
                factory[1] = battles[f][1] - (factory[1] + battles[f][0])
                factory[0] = 1 if battles[f][2] == 1 else 2

    for f in range(len(factories)):
        if factories[f][0] == _id:
            product[0] += factories[f][2]
            troopaloopa[0] += factories[f][1]
            alternative_facts[0].append(f)
        elif factories[f][0] == opp:
            product[1] += factories[f][2]
            troopaloopa[1] += factories[f][1]
            alternative_facts[1].append(f)

    for i in alternative_facts[0]:
        if len(alternative_facts[0]) > 1:
            num = min([distances[i][b] for b in range(len(distances[i])) if b in alternative_facts[0] if
                       distances[i][b] != 0])
            if num > longest_D[0]:
                longest_D[0] = num

    for i in alternative_facts[1]:
        if len(alternative_facts[1]) > 1:
            num = min([distances[i][b] for b in range(len(distances[i])) if b in alternative_facts[1] if
                       distances[i][b] != 0])
            if num > longest_D[1]:
                longest_D[1] = num

    future_P = product[0]-product[1]
    future_T = troopaloopa[0]-troopaloopa[1]
    future_V = vulnerability(_id, factories, distances)-vulnerability(opp, factories, distances)
    if future:
        #print ([future_P, future_T, future_V, current_P, current_T, current_V, availeble_T, Travel_T])
        return factories, [future_P, future_T, future_V, current_P, current_T, current_V, availeble_T, Travel_T]
    else:
        return [product[0]-product[1], troopaloopa[0]-troopaloopa[1], longest_D[0]-longest_D[1]]


class Player_v2:
    def __init__(self, _id, model):
        self._id = _id
        self.score = 0
        self.production = 0
        self.bombpath = list()
        self.bombsused = 0
        self.model = model

    def get_next_turn(self, factories, troops, distances, actions):
        # Reset and clean up
        battles = [[0, 0, 0] for i in range(len(factories))]
        # move troops
        for troop in troops:
            troop[4] -= 1
        # decrease factory cd
        for f in factories:
            if f[3] > 0:
                f[3] -= 1
        for action in actions:
            if action[0] == 'MOVE':
                units = min(action[3], factories[action[1]][1])
                if units > 0 and self.bombpath != action[1:2]:
                    factories[action[1]][1] -= units
                    troops.append(
                        [self._id, action[1], action[2], action[3], distances[action[1]][action[2]]])
            elif action[0] == 'INC':
                factory = factories[action[1]]
                if factory[1] >= 10 and factory[2] < 3:
                    factory[1] -= 10
                    factory[2] += 1

        # solve battles
        for troop in troops:
            if troop[4] <= 0:
                if troop[0] == factories[troop[2]][0]:
                    battles[troop[2]][0] += troop[3]
                else:
                    if troop[0] != 0 and battles[troop[2]][2] != troop[0]:
                        if troop[3] > battles[troop[2]][1]:
                            battles[troop[2]][1] = troop[3] - battles[troop[2]][1]
                            battles[troop[2]][2] = troop[0]
                        elif troop[3] < battles[troop[2]][1]:
                            battles[troop[2]][1] -= troop[3]
                        else:
                            battles[troop[2]] = [0, 0, 0]
                    else:
                        battles[troop[2]][1] += troop[3]
                        battles[troop[2]][2] = troop[0]

        for f in range(len(factories)):
            factory = factories[f]
            if battles[f][0] + factory[1] >= battles[f][1]:
                factory[1] = (factory[1] + battles[f][0]) - battles[f][1]
            else:
                factory[1] = battles[f][1] - (factory[1] + battles[f][0])
                factory[0] = 1 if battles[f][2] == 1 else 2
        return get_features(self._id, [factories, troops, distances], True)[1]

    def decision(self, factories, troops, distances):
        highscore = 0
        start = int(round(time.time() * 1000))
        count = 0
        bestmove = list()
        my_factories = [i for i in factories if i[0] == self._id]
        targeted_factories = list(set([i[2] for i in troops if i[1] not in [0, self._id] and factories[i[2]][0] == self._id]))
        vulnerable = list()
        for f in factories:
            max_dist = 0
            vul_level = -f[2]
            if f[0] == self._id:
                continue
            for all in factories:
                if all[0] not in [0, self._id]:
                    vul_level += all[1] / max(1, distances[f[4]][all[4]])
                elif all[0] == self._id:
                    if max_dist < distances[f[4]][all[4]]:
                        max_dist = distances[f[4]][all[4]]
                    vul_level -= all[1] / max(1, distances[f[4]][all[4]])
            vulnerable.append([f[4], vul_level+(max_dist*3)])
        vulnerable.sort(key=lambda x:x[1])
        best_targets = [i[0] for i in vulnerable[:2]] + targeted_factories
        # Random Action
        while int(round(time.time() * 1000)) - start < 95:
            desc = [["Wait"]]
            for f in my_factories:
                np.random.shuffle(best_targets)
                targets = [i for i in best_targets if i != f[4]]
                r = random.randint(0, 2)
                if r == 0:
                    continue
                elif r == 1:
                    desc.append(["MOVE", f[4], targets[0], f[1]])
                elif r == 2:
                    for b in targets[:2]:
                        desc.append(["MOVE", f[4], b, f[1] // 2])

            score = self.model.predict(
                np.array([self.get_next_turn(copy.deepcopy(factories), copy.deepcopy(troops), distances, desc)]))
            if score > highscore:
                highscore = score
                bestmove = desc
        return bestmove


class Player_v1:
    def __init__(self, _id, model):
        self._id = _id
        self.score = 0
        self.production = 0
        self.bombpath = list()
        self.bombsused = 0
        self.model = model

    def get_next_turn(self, factories, troops, distances, actions):
        # Reset and clean up
        battles = [[0, 0, 0] for i in range(len(factories))]
        # move troops
        for troop in troops:
            troop[4] -= 1
        # decrease factory cd
        for f in factories:
            if f[3] > 0:
                f[3] -= 1
        for action in actions:
            if action[0] == 'MOVE':
                units = min(action[3], factories[action[1]][1])
                if units > 0 and self.bombpath != action[1:2]:
                    factories[action[1]][1] -= units
                    troops.append(
                        [self._id, action[1], action[2], action[3], distances[action[1]][action[2]]])
            elif action[0] == 'INC':
                factory = factories[action[1]]
                if factory[1] >= 10 and factory[2] < 3:
                    factory[1] -= 10
                    factory[2] += 1

        # solve battles
        for troop in troops:
            if troop[4] <= 0:
                if troop[0] == factories[troop[2]][0]:
                    battles[troop[2]][0] += troop[3]
                else:
                    if troop[0] != 0 and battles[troop[2]][2] != troop[0]:
                        if troop[3] > battles[troop[2]][1]:
                            battles[troop[2]][1] = troop[3] - battles[troop[2]][1]
                            battles[troop[2]][2] = troop[0]
                        elif troop[3] < battles[troop[2]][1]:
                            battles[troop[2]][1] -= troop[3]
                        else:
                            battles[troop[2]] = [0, 0, 0]
                    else:
                        battles[troop[2]][1] += troop[3]
                        battles[troop[2]][2] = troop[0]

        for f in range(len(factories)):
            factory = factories[f]
            if battles[f][0] + factory[1] >= battles[f][1]:
                factory[1] = (factory[1] + battles[f][0]) - battles[f][1]
            else:
                factory[1] = battles[f][1] - (factory[1] + battles[f][0])
                factory[0] = 1 if battles[f][2] == 1 else 2
        return get_features(self._id, [factories, troops, distances], True)[1]

    def hard_decision(self, factories, troops, distances):
        potential_actions = list()
        highscore = 0
        bestmove = list()
        potential_actions.append(["WAIT"])
        #Random Action
        for i in range(100):
            desc = list()
            for f in range(len(factories)):
                if factories[f][0] == self._id:
                    if random.randint(1, 10) < 2 and factories[f][1] > 12 and factories[f][2] < 3:
                        desc.append(["INC", f])

                    random_facts = [i for i in range(len(factories)) if i != f]
                    random.shuffle(random_facts)
                    for i in range(random.randint(1, 3)):
                        desc.append(["MOVE", f, random_facts[i], random.randint(1, max(1, factories[f][1]))])
            score = self.model.validate( [self.get_next_turn(copy.deepcopy(factories), copy.deepcopy(troops), distances)] )
            if score > highscore:
                highscore = score
                bestmove = desc
        return bestmove

    def decision(self, factories, s_troops, distances):
        factories = copy.deepcopy(factories)
        s_troops = copy.deepcopy(s_troops)
        total_production = sum([i[2] for i in factories])
        my_factories = [f for f in factories if f[0] == self._id]
        future_factories, position = get_features(self._id, [factories, s_troops, distances], True)
        my_future_factories = [f for f in future_factories if f[0] == self._id]
        highstrength = 0.0
        bestmove = [['WAIT']]
        move = [['WAIT']]
        # DEFENSE, VULNERABILITY
        if position[0] > 1 and sum([i[2] for i in my_future_factories]) >= total_production // 2 and position[1] < 10:
            vulnerable = list()
            for f in my_future_factories:
                vul_level = -f[1]
                for all in factories:
                    if all[4] == f[4]:
                        continue
                    if all[0] not in [0, self._id]:
                        vul_level += all[1] / distances[f[4]][all[4]]
                vulnerable.append([f[4], vul_level, f[1]])
            for v in my_factories:
                vulnerable.sort(key=lambda x: x[1], reverse=True)
                if v[4] == vulnerable[-1][0]:
                    continue
                else:
                    send_count = min(v[1], max(0, (vulnerable[-1][0] - v[1]) / 2))
                    move.append(["MOVE", v[4], vulnerable[-1][0], int(send_count)])
                    vulnerable[-1][1] -= send_count
        else:
            # DEFEND FACTORIES
            factories_lost = [F for F in future_factories if
                              F[4] in [i[4] for i in my_factories] and F[4] not in [i[4] for i in my_future_factories]]
            if len(factories_lost) > 0:
                opp_target = [i[2] for i in s_troops if i[1] not in [0, self._id]]
                factories_under_attack = [i for i in my_factories if i[4] in opp_target]
                need_help = [[i[1] + i[2] + 1, i[4]] for i in factories_lost]
                for f in my_factories:
                    for n in need_help:
                        if f[4] == n[1]:
                            break
                        send_troops = min(f[1], n[0])
                        move.append(["MOVE", f[4], n[1], min(f[1], int(send_troops))])
                        n[0] -= send_troops
                        f[1] -= send_troops
                        if 0 < f[1]:
                            continue
                        else:
                            break
            else:
                # INCREASE PRODUCTION
                extra_units = position[1]
                while extra_units > 9:
                    tmp_units = extra_units
                    for f in my_factories:
                        if f[1] >= 10 and f[2] < 3:
                            move.append(["INC", f[4]])
                            extra_units -= 10
                            position[1] += 1
                            break
                    if tmp_units == extra_units:
                        break

                # CAPTURE FACTORIES
                if position[0] < 100:
                    possible_factories = [f for f in factories if f[4] not in [i[4] for i in my_future_factories]]
                    my_troops = sum([f[1] for f in my_factories])
                    best_targets = [(i[2] * 5 - (distances[self._id][i[4]] + i[1]), i[4]) for i in possible_factories]
                    best_targets.sort(key=lambda x: x[0], reverse=True)
                    #print ("BEST TARGETS: ", best_targets)
                    for target in best_targets[:2]:
                        send_troops = 0
                        if factories[target[1]][1] > my_troops:
                            continue
                        else:
                            for f in my_factories:
                                move.append(["MOVE", f[4], target[1], max(int(factories[target[1]][1]+1), f[1]//2)])
                                send_troops += f[1]
                                if send_troops > factories[target[1]][1]:
                                    break
                                else:
                                    continue

        return move

class RandomPlayer:
    def __init__(self, _id):
        self._id = _id
        self.score = 0
        self.production = 0
        self.bombpath = list()
        self.bombsused = 0

    def decision(self, factories, troops, distances):
        desc = list()
        for f in range(len(factories)):
            if factories[f][0] == self._id:
                if random.randint(1, 10) < 2 and factories[f][1] > 12 and factories[f][2] < 3:
                    desc.append(["INC", f])

                random_facts = [i for i in range(len(factories)) if i != f]
                random.shuffle(random_facts)
                for i in range(random.randint(1, 3)):
                    desc.append(["MOVE", f, random_facts[i], random.randint(1, max(1, factories[f][1]) )])
        return desc

class game:

    def __init__(self, p1, p2, r=0):
        self.players = [p1, p2]
        self.startround = r

    def random_init(self):
        # Initialize random start configuration
        self.troops = list()
        self.bombs = list()
        factories = list()
        positions = list()

        #7 to 15 factories, always odd
        factories_count = random.randint(7, 15)
        if factories_count % 2 == 0:
            factories_count+=1

        # Place one in middle with all zeros
        factories.append([0, 0, 0, 0, 0])
        positions.append( (0, 0) )

        while len(factories) < factories_count:
            position = (random.randint(-7, 7), random.randint(-7, 7))
            position2 = ( position[0]*-1, position[1]*-1 )
            if valid_pos(positions, position):
                production_rate = random.randint(0, 3)
                if len(factories) == 1:
                    units = random.randint(15, 30)
                    factories.append( [1, units, production_rate, 0, len(factories)] )
                    positions.append(position)
                    factories.append( [2, units, production_rate, 0, len(factories)] )
                    positions.append(position2)
                else:
                    units = random.randint(0, production_rate*5)
                    factories.append([0, units, production_rate, 0, len(factories)])
                    factories.append([0, units, production_rate, 0, len(factories)])
                    positions.append(position)
                    positions.append(position2)

        totalproduction = sum([i[2] for i in factories])

        while totalproduction < 4:
            for f in range(1, len(factories), 2):
                if factories[f][2] < 3:
                    factories[f][2] += 1
                    factories[f+1][2] += 1
                    totalproduction += 2
                    break

        self.distances = list()
        for a in range(len(factories)):
            self.distances.append( [distance(positions[a], positions[b]) for b in range(len(factories))] )
        self.factories = factories

    def set_gamestate(self, factories, troops, distances):
        self.factories = factories
        self.distances = distances
        self.troops = troops
        #self.bombs = bombs

    def get_gamestate(self):
        return self.factories, self.troops, self.bombs

    def update(self):
        #Reset and clean up
        battles = [[0, 0, 0] for i in range(len(self.factories))]
        self.troops = [i for i in self.troops if i[4] > 0]
        self.bombs = [i for i in self.bombs if i[3] > 0]
        #print ([f for f in self.factories if f[0] == 1])
        #print([f for f in self.factories if f[0] == 2])
        #print([f for f in self.factories if f[0] == 0])

        #move troops
        for troop in self.troops:
            troop[4] -= 1

        #move bombs
        for bomb in self.bombs:
            bomb[3] -= 1

        #decrease factory cd
        for f in self.factories:
            if f[3] > 0:
                f[3] -= 1

        #player actions
        tmpstates = (copy.deepcopy(self.factories), copy.deepcopy(self.troops), self.distances)
        for player in self.players:
            actions = player.decision(*tmpstates)
            for action in actions:
                if action[0] == 'BOMB' and player.bombsused < 2 and player.bombpath != action[1:]:
                    self.bombs.append( [player._id, action[1], action[2], self.distances[action[1]][action[2]]] )
                    player.bombpath = action[1:]
                    player.bombsused += 1
                elif action[0] == 'MOVE':
                    units = min( action[3], self.factories[action[1]][1] )
                    if units > 0 and player.bombpath != action[1:2]:
                        self.factories[action[1]][1] -= units
                        self.troops.append( [player._id, action[1], action[2], action[3], self.distances[action[1]][action[2]]] )
                elif action[0] == 'INC':
                    factory = self.factories[action[1]]
                    if factory[1] >= 10 and factory[2] < 3:
                        factory[1] -= 10
                        factory[2] += 1

        #create new units
        for f in self.factories:
            if f[0] != 0 and f[3] == 0:
                f[1]+=f[2]

        #solve battles
        for troop in self.troops:
            if troop[4] <= 0:
                if troop[0] == self.factories[troop[2]][0]:
                    battles[troop[2]][0] += troop[3]
                else:
                    if troop[0] != 0 and battles[troop[2]][2] != troop[0]:
                        if troop[3] > battles[troop[2]][1]:
                            battles[troop[2]][1] = troop[3]-battles[troop[2]][1]
                            battles[troop[2]][2] = troop[0]
                        elif troop[3] < battles[troop[2]][1]:
                            battles[troop[2]][1] -= troop[3]
                        else:
                            battles[troop[2]] = [0, 0, 0]
                    else:
                        battles[troop[2]][1] += troop[3]
                        battles[troop[2]][2] = troop[0]

        for f in range(len(self.factories)):
            factory = self.factories[f]
            if battles[f][0]+factory[1] >= battles[f][1]:
                factory[1] = (factory[1]+battles[f][0]) - battles[f][1]
            else:
                factory[1] = battles[f][1] - (factory[1]+battles[f][0])
                factory[0] = 1 if battles[f][2] == 1 else 2

        #solve bombs
        for bomb in self.bombs:
            if bomb[3] <= 0:
                factory = self.factories[bomb[2]]
                unitslost = max(10, factory[1]//2)
                factory[1] = max(0, factory-unitslost)
                factory[3] = 5

        #end conditions
        for player in self.players:
            player.score = 0
            player.production = 0
            for troop in self.troops:
                if troop[0] == player._id:
                    player.score += troop[3]

            for fact in self.factories:
                if fact[0] == player._id:
                    player.score += fact[1]
                    player.production += fact[2]

    def main(self):
        for round in range(self.startround, 100):
            self.update()
            for p in self.players:
                if p.score + p.production <= 0:
                    return

    def run_games(self, state = []):
        score = [0, 0]
        for i in range(20):
            self.random_init()
            self.main()
            res = [p.score for p in self.players]
            print (res)
            if res[0] == res[1]:
                score[0] += 1
                score[1] += 1
            else:
                score[res.index(max(res))] += 1
        return score

    def save_states(self):
        states = list()
        self.random_init()
        for round in range(16):
            self.update()
            for p in self.players:
                if p.score + p.production <= 0:
                    return states
            if round > 14:
                states.append([copy.deepcopy(self.factories), copy.deepcopy(self.troops), copy.deepcopy(self.distances)])
        return states

    def calculate_positions(self, states):
        count = 0
        res = list()
        print (len(states))
        for s in states:
            count += 1
            if count % 200 == 0:
                print(count)
            res.append(self.run_games(s))
        pickle.dump(states, open('data4_training_x', 'wb'))
        pickle.dump(res, open('data4_training_y', 'wb'))
        print (len(states), len(res))

if __name__ == '__main__':
    # p1 = Player_v2(1)
    # p2 = Player_v2(2)
    # g = game(p1, p2)
    # g.calculate_positions(500)

    res = pickle.load(open('data4_training_y', 'rb'))
    states = pickle.load(open('data4_training_x', 'rb'))
    training_x = list()
    training_y = list()
    for s in range(len(states)):
        training_x.append( get_features(1, states[s], True)[1] )
        training_y.append( res[s][0]/sum(res[s]) )

        training_x.append( get_features(2, states[s], True)[1] )
        training_y.append( res[s][1]/sum(res[s]) )

    pickle.dump(training_x, open('training4_x', 'wb'))
    pickle.dump(training_y, open('training4_y', 'wb'))
