# DEFEND FACTORIES
factories_lost = [F for F in future_factories if
                  F[4] in [i[4] for i in my_factories] and F[4] not in [i[4] for i in my_future_factories]]
if len(factories_lost) > 0:
    print("DEFENDING", file=sys.stderr)
    opp_target = [i[2] for i in s_troops if i[1] not in [0, _id]]
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

    for f in my_future_factories:
        vul_level = -f[1]
        for all in factories:
            if all[4] == f[4]:
                continue
            if all[0] not in [0, _id]:
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
    if position[0] < 1 or sum([i[2] for i in my_future_factories]) <= total_production // 2:
        possible_factories = [f for f in factories if f[4] not in [i[4] for i in my_future_factories]]
        my_troops = sum([f[1] for f in my_factories])
        production_needed = 1 - position[1]
        best_targets = [(i[2] * 2 - (distances[_id][i[4]] + i[1]), i[4]) for i in possible_factories]
        best_targets.sort(key=lambda x: x[0], reverse=True)
        for target in best_targets:
            send_troops = 0
            if factories[target[1]][1] > my_troops:
                continue
            else:
                for f in my_factories:
                    move.append(["MOVE", f[4], target[1], int(f[1])])
                    send_troops += f[1]
                    if send_troops > factories[target[1]][1]:
                        production_needed -= factories[target[1]][2]
                        break
                    else:
                        continue
            if production_needed <= 0:
                break