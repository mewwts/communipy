from modularity import mass_modularity

def community_dissolve(G, C, init_q, args):
    """
    Find the communities of the graph with adjacency matrix A using
    the community-dissolve algorithm.

    Args:
    G: Graph object
    C: Community object
    init_q: the modularity of the network when it starts.
    args: named tuple of flags and objects for data export etc.

    """
    def move(i, dest):
        """ Move vertex i to dest in our community object """
        if dest != -1:
            C.move(i, dest, k[i], movein[i],
                   moveout[i], quv[dest])
        else:
            C.move(i, dest, k[i], movein[i],
                   moveout[i], C.node_mods[i])
        quv[dest] = 0.00 # Only add this the first time.

    k = G.k
    q = init_q

    while True:
        c, (seen, q_c) = C.pop()

        if seen:
            if C.network_modularity - q < args.tsh:
                break
            else:
                q = C.network_modularity
            C.unsee_all()

        (node2c, c2node, movein,
         moveout, quv) = mass_modularity(G, C, C[c], c)

        quv.pop(c) # Use this value for correct moveout (if moving subsets)


        if sum(movein.values()) + sum(quv.values()) > q_c:
            # print stats on this
            for dest, nodes in c2node.iteritems():
                for i in nodes:
                    move(i, dest)
        else:
            for i in movein:
                if movein[i] - moveout[i] > 0:
                    move(i, node2c[i]) 
                    # I am not sure if the modularity is right here

    return q