"""
Functions for generating the cyclic group [0,...n-1]. Use instead of
random.

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
    i = 0
    while i < n:
        yield i*rand % n
        i += 1

def bin_gcd(a, b):
    """
    Return the greatest common divisor of a and b using the binary
    gcd algorithm.

    """
    if a == b:
        return a
    if a == 0:
        return b
    if b == 0:
        return a

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
