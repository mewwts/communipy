from collections import defaultdict
from modularity_communities import ModCommunities as ModComs
import time

def community_dissolve(A, m, n, k, args):
    """
    Find the communities of the graph with adjacency matrix A by using
    the community-dissolve algorithm.

    Args:
    A: Adjacency matrix in CSR format
    m: 0.5 * A.sum()
    n: A.shape[1] the number of vertices in the graph
    k: degree sequence
    args: named tuple of flags and objects for data export etc.

    """

    t = time.time()
    C = ModComs(xrange(n), k, A, m)
    num_moves = 0
    # q = sum(C.modularity.values())
    while True:

        c, (seen, q_c) = C.pop()
        (node2c, c2node, movein,
         moveout, quv, best) = mass_modularity(C[c], c, A, m, k, C)

        quv.pop(c) # Use this value for correct moveout (if moving subsets)

        if sum(movein.values()) + sum(quv.values()) > q_c:
            for dest, nodes in c2node.iteritems():
                for i in nodes:
                    num_moves += 1
                    if dest != -1:
                        C.move(i, dest, k[i], movein[i],
                               moveout[i], quv[dest])
                    else:
                        C.move(i, dest, k[i], movein[i],
                                  moveout[i], C.node_mods[i])
                    quv[dest] = 0.00 # Only add this the first time.

        else:
            i, dest = best
            if movein[i] - moveout[i] > 0:
                num_moves += 1
                C.move(i, dest, k[i], movein[i],
                       moveout[i], C.node_mods[i])

        if num_moves == 0:
            break

        if seen:
            num_moves = 0
            C.unsee_all()

    if args.exporter:
        args.exporter.write_nodelist(C.dict_renamed)
    print C.dict_renamed
    print("It took {} seconds.".format(time.time() - t))
    print("Modularity = {}".format(sum(j for i,j in C.modularity.values())))

def mass_modularity(nodes, c, A, m, k, C):
    """
    Calculates the modularity gain of moving each of the nodes 
    to the best match.

    Args:
    nodes: list of nodes in community
    A: Adjacency matrix in CSR format
    m: 0.5 * A.sum()
    k: degree sequence
    C: Community structure

    Returns:
    node2c: dict holding best match for vertex i
    c2node: dict holding vertices of community c
    dqins: holds the gain of moving vertex i to it's alternative.
    dqouts: holds the loss of  --"--
    quv: the modularity of the subsets that is moved. If only one vertex
         is moved to a community, this is q_i.
    best_move: the (node, community) move that has the highest
               modularity gain associated to it
    """

    node2c = {}
    c2node = defaultdict(set)
    dqins = {}
    dqouts = {}
    quv = defaultdict(float)
    best_move = (-1, -1)

    for i in nodes:
        indices = A.indices[A.indptr[i]:A.indptr[i+1]]
        data = A.data[A.indptr[i]:A.indptr[i+1]]
        nbs = set([])
        crossterms = defaultdict(float)
        movein = {}
        k_i = k[i]
        moveout = -(k_i/(2.0*m**2))*(C.strength[c] - k_i)
        max_movein = (-1, 0.0)

        for ind, j in enumerate(indices):
            aij = data[ind]
            k_j = k[j]
            c_j = C.nodes[j]
            if c_j == c:
                if i != j:
                    moveout += aij/m
                    qij = aij/(2*m) - (k_i*k_j)/((2*m)**2)
                    quv[c] += qij

                    try:
                        nc_j = node2c[j]
                    except KeyError:
                        continue
                    else:
                        if nc_j != -1:
                            nbs.add(j)
                            crossterms[nc_j] += 2*qij
                continue

            try:
                movein[c_j] += aij/m
            except KeyError:
                movein[c_j] = aij/m - (k_i/(2.0*m**2))*C.strength[c_j]

            if movein[c_j] > max_movein[1]:
                max_movein = (c_j, movein[c_j])

        dest, q_in = max_movein
        node2c[i] = dest
        c2node[dest].add(i)
        dqins[i] = q_in
        dqouts[i] = moveout

        if q_in - moveout > best_move[1]:
            best_move = (i, dest)

        quv[dest] += crossterms[dest]

        qi = C.node_mods[i]
        quv[dest] += qi
        quv[c] += qi

        for node in c2node[dest] - (nbs | set([i])):
            # if there's nodes going to my community that I'm not connected to
            qij = -2*k[i]*k[node]/(2*m)**2
            quv[dest] += qij
            quv[c] += qij

    return node2c, c2node, dqins, dqouts, quv, best_move
