import sys
import math


def simple_bot(myfact, factories, troops, factpos):
    total_troop = sum([myfact[i]['cyborgs'] for i in myfact])
    for mf in myfact:
        for opp in reversed(factpos[int(mf)]):
            if opp[0] in factories and opp[0] not in troops:
                overtake_count = factories[opp[0]]['cyborgs'] + factories[opp[0]]['production'] * opp[1]
                if total_troop > overtake_count:
                    return ["MOVE %s %s %s" % (mf, opp[0], max(5, overtake_count*2)) for mf in myfact]
    return ["WAIT"]


distances = dict()

factory_count = int(input())  # the number of factories
link_count = int(input())  # the number of links between factories

factpos = [list() for i in range(factory_count)]

for i in range(link_count):
    factory_1, factory_2, distance = [int(j) for j in input().split()]
    if factory_1 in distances:
        distances[factory_1].update({factory_2: distance})
    else:
        distances[factory_1] = {factory_2: distance}


sendbomb = 0
# game loop
while True:
    my_factories = dict()
    factories = dict()
    troops = list()
    factpos = [list() for i in range(factory_count)]

    entity_count = int(input())  # the number of entities (e.g. factories and troops)
    for i in range(entity_count):
        entity_id, entity_type, arg_1, arg_2, arg_3, arg_4, arg_5 = input().split()
        if entity_type == 'FACTORY':
            if arg_1 == '1':
                my_factories[int(entity_id)] = {'cyborgs': int(arg_2), 'production': int(arg_3)}
            else:
                factories[int(entity_id)] = {'cyborgs': int(arg_2), 'production': int(arg_3)}
        elif entity_type == 'TROOP':
            if arg_1 == '1':
                troops.append( arg_3 )

    for i in range(factory_count):
        for a in range(factory_count):
            if i == a:
                continue
            if a in factories:
                factpos[i].append([a, factories[a]['production']])

    for i in factpos:
        i.sort(key=lambda x: x[1])
    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)


    # Any valid action, such as "WAIT" or "MOVE source destination cyborgs"

    cmd = ""


    for i in simple_bot(my_factories, factories, troops, factpos):
        cmd += i + ";"
    print (cmd[:-1])