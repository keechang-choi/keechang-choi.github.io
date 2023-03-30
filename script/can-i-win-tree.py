import igraph as ig
import matplotlib.pyplot as plt


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
    while(len(q) != 0):
        state, one_cnt = q.pop(0)
        depth = one_cnt
        same_depth_cnt += 1
        if(same_depth_cnt >= nPi[depth]):
            same_depth_cnt = 0
        pidx = GetVIdx(depth, same_depth_cnt)
        num_children = n - depth
        for i in range(max_choosable_int):
            nth_bit = 1<<i
            if state & nth_bit == 0:
                q.append((state | nth_bit, one_cnt+1))
        edges_to_add = []
        for child_cnt in range(num_children):
            cidx = GetVIdx(depth+1, same_depth_cnt*num_children + child_cnt)
            edges_to_add.append((cidx, pidx))
        if(len(edges_to_add) > 0):
            g.add_edges(edges_to_add)


    g.vs["label"] = list(range(num_vertices))
    g.vs["size"] = 0.5
    g.vs["label_size"] = 10

    return g

if __name__ == "__main__":

    n = 3
    nPi = [1]
    for i in range(n):
        nPi.append(nPi[-1]*(n-i))

    acc_nPi = [0]
    for i in range(n+1):
        acc_nPi.append(acc_nPi[-1] + nPi[i])

    num_vertices = acc_nPi[n+1]

    g = GetFullGraph()

    
    fig, ax = plt.subplots()

    # ig.plot(g, layout="kk", target=ax)
    ig.plot(g, layout=g.layout_reingold_tilford(mode="in", root=[0]), target=ax)
    plt.show()
