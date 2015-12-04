# Functions for/on primes.

import math
import random

sr = random.SystemRandom()

def pow2_factor(n):
    d = n
    r = 0
    while (d & 1) == 0:
        r += 1
        d >>= 1
    return r, d

def mr_test(n, k = None):
    if k is None:
        k = int(math.log(math.log(n)))
    r, d = pow2_factor(n - 1)
    for i in xrange(k):
        a = sr.randint(2, n - 2)
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for j in xrange(r - 1):
            x = pow(x, 2, n)
            if x == 1:
                return False
            if x == n - 1:
                break
        else:
            return False
    return True

def rand_prime(bits, attempts = 1000, k = None):
    for i in xrange(attempts):
        p = 2 ** bits + 2 * sr.getrandbits(bits - 1) + 1
        if mr_test(p, k):
            return p
    raise RuntimeError('Failed to produce prime in reasonable time')
