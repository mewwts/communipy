import random
import time

def yield_random_list(iterable):
    """ Yield the numbers in the iterable in a random pseduorandom
    fashion """

    not_seen = list(iterable)
    random.seed(time.time())

    while not_seen:
        choice = random.choice(not_seen)
        not_seen.remove(choice)
        yield choice

def yield_random_modulo(n):
    """ generate the group 0 through n-1. pseudorandom.
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
    """ This calculates the gcd of a and b using the binary gcd
    algorithm"""
    if a == b:
        return a
    if a == 0:
        return b
    if b == 0:
        return a

    if not a & 1: # a is even
        if not b & 1: # b is even too
            return bin_gcd(a >> 1, b >> 1) << 1 # a and b share 2
        else: # b is odd
            return bin_gcd(a >> 1, b) # check a/2 and b

    if not b & 1:
        return bin_gcd(a, b >> 1) # check a and b/2

    if a > b:
        return bin_gcd((a - b) >> 1, b)

    return bin_gcd((b - a) >> 1, a)
