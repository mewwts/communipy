"""
Functions for generating the cyclic group [0,...n-1]. Use instead of
random.

Functions:
    yield_random_modulo(n) <- generate the numbers in 0,...n-1
    bin_gcd(a, b) <- calculate the gcd of a and b fast

"""
import random

def yield_random_modulo(n):
    """
    Generates the cyclic group 0 through n-1 using a number
    which is relative prime to n.

    """
    while True:
        rand = random.random()
        rand = int(rand * n) # number between 0 and n
        if bin_gcd(rand, n) == 1:
            break
    i = 1
    while i <= n:
        yield i*rand % n
        i += 1

def bin_gcd(a, b):
    """
    Return the greatest common divisor of a and b using the binary
    gcd algorithm.

    """
    if a == b or b == 0:
        return a
    if a == 0:
        return b

    if not a & 1:
        if not b & 1:
            return bin_gcd(a >> 1, b >> 1) << 1
        else: # b is odd
            return bin_gcd(a >> 1, b)
    if not b & 1:
        return bin_gcd(a, b >> 1)
    if a > b:
        return bin_gcd((a - b) >> 1, b)

    return bin_gcd((b - a) >> 1, a)

# unsure if working correctly
def kth_largest(nums, k):
    if len(nums) <= 5:
        return sorted(nums)[k-1] 

    B = [kth_largest(nums[i:i+5], (len(nums[i:i+5])/2)+1) for i in xrange(0, len(nums), 5)]
    pivot = kth_largest(B, (len(B)/2) + 1)
    l, r, numpiv = _split(nums, pivot)

    if k <= len(l):
        return kth_largest(l, k)
    elif k <= len(l) + numpiv:
        return pivot
    else:
        return kth_largest(r, k - len(l) - numpiv)


def _split(coos, pivot):
    left = []
    right = []
    numpiv = 0
    for i in coos:
        if i < pivot:
            left.append(i)
        elif i > pivot:
            right.append(i)
        else:
            numpiv += 1
    return left, right, numpiv
