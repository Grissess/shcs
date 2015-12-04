# ElGamal cryptosystem over prime fields

from random import SystemRandom

from .. import modular
from .. import prime

sr = SystemRandom()

class Cipher(object):
    def __init__(self, p, g, a, b = None):
        self.p = p
        self.g = g
        self.a = a
        self.b = b

    def is_private(self):
        return self.b is not None

    def to_public(self):
        return type(self)(self.p, self.g, self.a)

    def save(self, f, priv = False):
        if priv:
            if not self.is_private():
                raise ValueError('Can\'t save private parts of public-only key')
            l = [self.p, self.g, self.a, self.b]
        else:
            l = [self.p, self.g, self.a]
        f.write('\n'.join(map(str, l)))
        f.flush()

    @classmethod
    def load(cls, f):
        lines = [line.strip() for line in f.readlines()]
        assert len(lines) >= 3

        p, g, a = map(int, lines[:3])

        if len(lines) >= 4:
            b = int(lines[3])
        else:
            b = None

        return cls(p, g, a, b)

    @classmethod
    def new(cls, bits, attempts=100):
        for i in xrange(attempts):
            q = prime.rand_prime(bits - 1)
            p = 2*q + 1
            if prime.mr_test(p):
                break
        else:
            raise RuntimeError('Failed to generate a safe prime in a reasonable amount of time')
        for i in xrange(attempts):
            g = sr.randint(2, self.p - 1)
            if pow(g, q, p) == 1 and pow(g, 2, p) != 1:
                break
        else:
            raise RuntimeError('Failed to generate a group generator in a reasonable amount of time')
        b = sr.randint(2, self.p - 1)
        a = pow(g, b, p)
        return cls(p, g, a, b)

    def encrypt(self, inf, outf):
        while True:
            ch = inf.read(1)
            if not ch:
                break
            x = ord(ch)
            b = sr.randint(2, self.p - 1)
            alpha = pow(self.g, b, self.p)
            omega = pow(alpha, b, self.p)
            y = (x * omega) % self.p
            outf.write('%d %d\n'%(alpha, y))
        outf.flush()

    def decrypt(self, inf, outf):
        if not self.is_private():
            raise ValueError('Can\'t decrypt with public-only key')
        for line in inf:
            alpha, y = [int(part) for part in line.strip().split()]
            x = (y * modular.modinv(pow(alpha, self.b, self.p), self.p)) % self.p
            try:
                outf.write(chr(x))
            except (ValueError, OverflowError):
                outf.write('<?>')
        outf.flush()
