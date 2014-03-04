Improvements:
- [x] implement louvain.make_C_matrix with a COO to make it much faster
- [x] store np.sum(k[c]) for all communities c.
- [ ] parallelize some calculation
- [x] initialize C with generator
- [ ] make new A directly?
- [x] Consider rewriting movein, moveout and get_max_gain to same f.
- [x] Slice matrix by indptr or "for row in A": No gain
- [x] Get number of communities and print
- [x] m*(m-1) vs m**2
- [x] CSD histograms
- [x] "random" order by selecting i < n and generate the group mod n
- [ ] Generate Erdoz-Renyi random graphs for benchmarking
- [ ] Generate Benchmark graphs.
- [ ] "Test suite" for testing against random graphs. Output NMI, NVI etc.
- [ ] Data structure in modularity.py, max/min-heap to avoid O(n) max search?
- [ ] Fix median in functions.py

Issues:
- [x] Absolute gain in modularity in louvain.py
- [x] map with lambda apparantly slower than list comprehension
- [x] gains are too high // modularity is not calculated right
- [x] should moveinmodularity include aii? NO
- [x] weighted/directed networks do not work well