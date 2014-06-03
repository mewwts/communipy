#communitydetection

Implementation of some community detection algorithms for my project and master's thesis.

2014-01-15: Implementation of the Louvain method is complete.

##Todo:
- [ ] General:
    - [x] Generate weighted networks
    - [x] Symmetrize by reciprocal ties
    - [x] Test suite: file crawling doesn't work perfect 

##Analytics:
- [ ] Plots
    - [ ] Unweighted networks
        - [ ] Plot NMI/NVI vs. mu_t
    - [ ] Weighted networks
        - [ ] Plot NMI/NVI vs. mu_w for mu_t = 0.5 and 0.8
    - [ ] Plot NVI for A, A^2, A^3 and exp(A) for Louvain

## Ideas:
- [x] CSR-matrix with Python lists? Doable, but what we really want is O(1) access to indiv. elements. DOK-format does this, perhaps it should be considered.
