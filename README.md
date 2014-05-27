#communitydetection

Implementation of some community detection algorithms for my project and master's thesis.

2014-01-15: Implementation of the Louvain method is complete.

##Todo:
- [ ] General:
    - [x] Generate weighted networks
    - [x] Symmetrize by reciprocal ties

- [ ] Labelpropagation
    - [x] Best match = -1: let's just don't care.
    - [x] Infinite recursion
- [ ] Degree-Rank
    - [ ] What subset of the vertices should be fed to the inner loop?
- [ ] Community-Dissolve


## Ideas:
- [x] CSR-matrix with Python lists? Doable, but what we really want is O(1) access to indiv. elements. DOK-format does this, perhaps it should be considered.
