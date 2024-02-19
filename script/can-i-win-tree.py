import igraph as ig
import matplotlib.pyplot as plt
import plotly.graph_objects as go


def GetVIdx(depth, left_order):
    return acc_nPi[depth] + left_order

def GetFullGraph():
    g = ig.Graph(num_vertices, directed=True)

    max_choosable_int = n
    state = 0 
    one_cnt = 0
    same_depth_cnt = 0
    q = []
    q.append((state, one_cnt))
    label = [0]*num_vertices
    e_label = []
    while(len(q) != 0):
        state, one_cnt = q.pop(0)
        depth = one_cnt
        pidx = GetVIdx(depth, same_depth_cnt)

        label[pidx] = state
        num_children = n - depth
        added_bits = []
        for i in range(max_choosable_int):
            nth_bit = 1<<i
            if state & nth_bit == 0:
                added_bits.append(i)
                q.append((state | nth_bit, one_cnt+1))
        edges_to_add = []
        for child_cnt in range(num_children):
            cidx = GetVIdx(depth+1, same_depth_cnt*num_children + child_cnt)
            edges_to_add.append((cidx, pidx))
        if(len(edges_to_add) > 0):
            g.add_edges(edges_to_add)
            e_label.extend(added_bits)

        same_depth_cnt += 1
        if(same_depth_cnt >= nPi[depth]):
            same_depth_cnt = 0

    g.vs["label"] = label
    g.vs["size"] = 0.5
    g.vs["label_size"] = 10
    g.es["label"] = e_label

    return g


def GetStateGraph():
    g = ig.Graph(num_vertices, directed=True)

    max_choosable_int = n
    state = 0 
    one_cnt = 0
    same_depth_cnt = 0
    q = []
    q.append((state, one_cnt))
    label = [0]*num_vertices
    e_label = []

    visited = [0] * num_vertices
    while(len(q) != 0):
        state, one_cnt = q.pop(0)
        if visited[state] != 0:
            continue
        visited[state] = 1
        depth = one_cnt
        pidx = state

        label[pidx] = state
        num_children = n - depth
        added_bits = []
        for i in range(max_choosable_int):
            nth_bit = 1<<i
            if state & nth_bit == 0:
                added_bits.append(i)
                q.append((state | nth_bit, one_cnt+1))
        edges_to_add = []
        for child_cnt in range(num_children):
            cidx = state | (1<<added_bits[child_cnt])
            edges_to_add.append((cidx, pidx))
        if(len(edges_to_add) > 0):
            g.add_edges(edges_to_add)
            e_label.extend(added_bits)

        same_depth_cnt += 1
        if(same_depth_cnt >= nPi[depth]):
            same_depth_cnt = 0

    g.vs["label"] = label
    g.vs["size"] = 0.5
    g.vs["label_size"] = 10
    g.es["label"] = e_label

    return g

def make_annotations(pos, text, font_size=10, font_color='rgb(250,250,250)', offset=0):
    L=len(pos)
    if len(text)!=L:
        raise ValueError('The lists pos and text must have the same len')
    annotations = []
    for k in range(L):
        annotations.append(
            dict(
                text=text[k], # or replace labels with a different list for the text within the circle
                x=pos[k][0], y=pos[k][1]-offset,
                xref='x1', yref='y1',
                font=dict(color=font_color, size=font_size),
                showarrow=False)
        )
    return annotations

def count_ones(bit):
    cnt = 0
    for i in range(n):
        if bit & (1 << i):
            cnt += 1
    return cnt

def convert_state_to_string(state):
    selected = []
    for i in range(n):
        if state & (1 << i):
            selected.append(i+1)

    value = can_win[state]
    if value == 0:
        value = -1
    elif value == 2:
        value = 'E'
    msg = f"{value}<br>["
    msg += ", ".join(list(map(str, selected)))
    msg += f"]<br>=>{sum(selected)}"
    return msg

if __name__ == "__main__":

    # 5-11
    # can_win = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 2, 1, 0, 2, 2, 2, 2, 2, 2, ]
    
    # 5-12
    can_win = [1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 2, 2, 2, 2, 2, ]
    
    # 4-8
    # can_win = [1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 2, 2, 2, ]
    
    # 4-9
    # can_win = [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 2, 2, ]
    
    # 10-12
    # can_win = [1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 2, 2, 2, 2, 2, 0, 1, 1, 0, 1, 0, 0, 2, 1, 0, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 1, 1, 0, 1, 0, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 1, 1, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, ]
    
    # 10-20
    # can_win = [1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 2, 2, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 2, 2, 2, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 2, 2, 2, 2, 2, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 2, 2, 2, 2, 2, 1, 0, 0, 1, 0, 1, 1, 2, 0, 1, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0, 1, 0, 1, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 2, 0, 1, 2, 2, 2, 2, 2, 2, 1, 0, 0, 1, 0, 1, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0, 1, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 2, 1, 0, 0, 1, 0, 1, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0, 1, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, ]
    print(len(can_win))

    n = 5
    desired_total = 12

    nPi = [1]
    for i in range(n):
        nPi.append(nPi[-1]*(n-i))

    acc_nPi = [0]
    for i in range(n+1):
        acc_nPi.append(acc_nPi[-1] + nPi[i])

    # full graph
    # num_vertices = acc_nPi[n+1]
    # g = GetFullGraph()

    # state graph
    num_vertices = 1 << n
    g = GetStateGraph()


    # fig, ax = plt.subplots()
    # # ig.plot(g, layout="kk", target=ax)
    # ig.plot(g, layout=g.layout_reingold_tilford(mode="in", root=[0]), target=ax)
    # plt.show()

    v_label = list(map(str, range(num_vertices)))
    # lay = g.layout_reingold_tilford(mode="in", root=[0])
    lay = g.layout_sugiyama()

    position = {k: lay[k] for k in range(num_vertices)}
    Y = [lay[k][1] for k in range(num_vertices)]
    M = max(Y)

    es = ig.EdgeSeq(g) # sequence of edges
    E = [e.tuple for e in g.es] # list of edges

    # pos_y_map = lambda y: 2*M-y
    pos_y_map = lambda y: y
    L = len(position)
    Xn = [position[k][0] for k in range(L)]
    Yn = [pos_y_map(position[k][1]) for k in range(L)]
    v_annotation_pos = list([x,y] for x,y in zip(Xn, Yn))
    Xe = []
    Ye = []
    edge_label_pos = []
    for edge in E:
        x1 = position[edge[0]][0]
        y1 = pos_y_map(position[edge[0]][1])
        x2 = position[edge[1]][0]
        y2 = pos_y_map(position[edge[1]][1])
        Xe+=[x2, x1, None]
        Ye+=[y2, y1, None]
        edge_label_pos.append([(x1*0.1+x2*0.9), (y1*0.1+y2*0.9)])
    edge_label = [str(l+1) for l in g.es["label"]]



    fig = go.Figure()
    fig.add_trace(go.Scatter(x=Xe,
                    y=Ye,
                    mode='lines+markers',
                    line=dict(color='rgb(210,210,210)', width=2),
                    hoverinfo='none',
                    marker=dict(size=20,
                                symbol= "arrow", 
                                angleref="previous"),
                    )
                )
    
        


    Xn1 = []
    Yn1 = []
    label1 = []

    Xn2 = []
    Yn2 = []
    label2 = []

    print(g.vs["label"]) 
    for i in range(num_vertices):
        state = g.vs["label"][i]
        bit_count = count_ones(state)
        if bit_count % 2 == 0:
            Xn1.append(Xn[i])
            Yn1.append(Yn[i])
            label1.append(i)
        else:
            Xn2.append(Xn[i])
            Yn2.append(Yn[i])
            label2.append(i)

    fig.add_trace(go.Scatter(x=Xn1,
                    y=Yn1,
                    mode='markers',
                    name='Player 1',
                    marker=dict(symbol='circle-dot',
                                    size=25,
                                    color='#DB4551',
                                    line=dict(color='rgb(50,50,50)', width=1)
                                    ),
                    text=label1,
                    hoverinfo='text',
                    opacity=0.8
                    ))
    fig.add_trace(go.Scatter(x=Xn2,
                    y=Yn2,
                    mode='markers',
                    name='Player 2',
                    marker=dict(symbol='circle-dot',
                                    size=25,
                                    color='#6175c1',    #'#DB4551',
                                    line=dict(color='rgb(50,50,50)', width=1)
                                    ),
                    text=label2,
                    hoverinfo='text',
                    opacity=0.8
                    ))



    axis = dict(showline=False, # hide axis line, grid, ticklabels and  title
                zeroline=False,
                showgrid=False,
                showticklabels=False,
                )

    v_label = list(map(convert_state_to_string, g.vs["label"]))
    annotations = make_annotations(
        v_annotation_pos, v_label, 10, "black", 0
        ) + make_annotations(
            edge_label_pos, edge_label, 10, "gray"
        )
    fig.update_layout(title=f'Game Tree for {n}, {desired_total}',
                annotations=annotations,
                font_size=15,
                showlegend=True,
                xaxis=axis,
                yaxis=axis,
                margin=dict(l=40, r=40, b=85, t=100),
                hovermode='closest',
                plot_bgcolor='rgb(248,248,248)'
                )
    # fig.show()
    fig.write_html("game-tree.html")