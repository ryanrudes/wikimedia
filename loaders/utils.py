import random
import math

def prime_factor_generator(n):
    yield 2
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        yield i

def prime_factors(n):
    for i in prime_factor_generator(n):
        if n % i == 0:
            yield i
            while True:
                n //= i
                if n % i != 0:
                    break
    if n > 2:
        yield n

def coprimes(n, maxx=None):
    if maxx == None:
        maxx = n
    sieve = [True] * (maxx - 1)
    for p in prime_factors(n):
        m = p
        while m < maxx:
            sieve[m - 1] = False
            m += p
    res = []
    for i, coprime in enumerate(sieve):
        if coprime:
            res.append(i + 1)
    return res

def maxcoprime(n, maxx=None):
    if maxx == None:
        maxx = n
    sieve = [True] * maxx
    for p in prime_factors(n):
        m = p
        while m <= maxx:
            sieve[m - 1] = False
            m += p
    for i, coprime in enumerate(reversed(sieve)):
        if coprime:
            return maxx - i

def cycle(n):
    """
    https://en.wikipedia.org/wiki/Full_cycle
    """
    seed = random.randrange(n)
    inc = maxcoprime(n, n + random.randint(n, n * 10))
    for _ in range(n):
        yield seed
        seed = (seed + inc) % n
