# RSA cryptosystem

from random import SystemRandom

from .. import modular
from .. import prime

sr = SystemRandom()

class Cipher(object):
    def __init__(self, n, e, d = None):
        self.n = n
        self.e = e
        self.d = d

    def is_private(self):
        return self.d is not None

    def to_public(self):
        return type(self)(self.n, self.e)

    def save(self, f, priv = False):
        if priv:
            if not self.is_private():
                raise ValueError('Can\'t save private parts of public-only key')
            l = [self.n, self.e, self.d]
        else:
            l = [self.n, self.e]
        f.write('\n'.join(map(str, l)))
        f.flush()

    @classmethod
    def load(cls, f):
        lines = [int(i.strip()) for i in f.readlines()]
        assert len(lines) >= 2

        n, e = lines[:2]

        if len(lines) >= 3:
            d = lines[2]
        else:
            d = None

        return cls(n, e, d)

    @classmethod
    def new(cls, bits, e=65537):
        p, q = prime.rand_prime(bits), prime.rand_prime(bits)
        n, phi = p * q, (p - 1) * (q - 1)
        if e is None:
            e = sr.randint(2, phi - 1)
        d = modular.modinv(e, phi)
        return cls(n, e, d)

    def encrypt(self, inf, outf):
        while True:
            ch = inf.read(1)
            if not ch:
                break
            x = ord(ch)
            y = pow(x, self.e, self.n)
            outf.write('%d\n'%(y,))
        outf.flush()

    def decrypt(self, inf, outf):
        if not self.is_private():
            raise ValueError('Can\'t decrypt with public-only key')
        for line in inf:
            y = int(line.strip())
            x = pow(y, self.d, self.n)
            outf.write(chr(x))
        outf.flush()
