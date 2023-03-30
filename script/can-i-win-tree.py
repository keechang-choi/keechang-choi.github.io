import igraph as ig
import matplotlib.pyplot as plt
n = 12
g = ig.Graph(directed=True)
# before adding edge
g.add_vertices(n)

label_num = [0]*n
for i in range(n):
    label_num[i] = i*2

g.add_edges([(1,0),(2,1), (3,2), (4,3),(4,6),
            (5,1),
            (6,2), (7,6), (8,7),
            (9,0),
            (10,0), (11,10)])

name = ["A", "B", "A", "B", "C", "F", "C", "B", "D", "C", "D", "F"]
label = [a+str(b) for a,b in zip(name, label_num)]
g.vs["label"] = label
g.vs["size"] = 0.5
g.vs["label_size"] = 10
fig, ax = plt.subplots()

# ig.plot(g, layout="kk", target=ax)
ig.plot(g, layout=g.layout_reingold_tilford(mode="in", root=[0]), target=ax)
plt.show()

if __name__ == "__main__":

    max_choosable_int = 3
    state = 0
    q = []
    q.append(state)
    while(len(q) != 0):
        state = q.pop(0)
        print(state)
        for i in range(max_choosable_int):
            nth_bit = 1<<i
            if state & nth_bit == 0:
                q.append(state | nth_bit)


