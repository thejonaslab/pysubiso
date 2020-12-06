import numpy as np

import pysubiso
import time


def reference_gen_possible_next_edges(adj, colors):
    """

    """
    out = []
    for i in range(adj.shape[0]):
        for j in range(i +1, adj.shape[1]):
            if adj[i, j] == 0:
                for c in colors:
                    out.append([i, j, c])
    return np.array(out, dtype=np.int32).reshape((len(out), 3))
    

def test_possible_next_edges():
    np.random.seed(10)

    for N in [1, 5, 10, 20, 32, 64, 100]:
        for color_n in [1, 4, 10]:

            # color_n * 3 to generate sparsity
            adj = np.random.randint(color_n*3, size=(N,N)).astype(np.int32)
            adj[adj > color_n] = 0 

            adj = np.triu(adj, k=1)
            possible_colors =np.arange(color_n, dtype=np.int32) + 1

            t1 = time.time()
            possible_edges = pysubiso.gen_possible_next_edges(adj, possible_colors)
            t2 = time.time()
            correct =reference_gen_possible_next_edges(adj, possible_colors)
            t3 = time.time()

            old_time = t3-t2
            new_time = t2-t1
            print(f"{old_time/new_time:3.1f} times faster ({old_time*1e6:3.1f} us vs {new_time*1e6:3.1f} us)")

            np.testing.assert_array_equal(possible_edges, correct)
