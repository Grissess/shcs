# Actual ECC/ElGamal cryptosystem

from .. import ec

class Cipher(object):
    def __init__(self, curve, gen, pub, n = None):
        self.curve = curve  # ec.Curve object
        self.gen = gen      # Generator point on curve
        self.pub = pub      # Public point
        self.n = n          # Secret multiplier

    def is_private(self):
        return self.n is not None

    def save(self, f, priv = False):
        if priv:
            if not self.is_private():
                raise ValueError('Can\'t save private parts of public-only key')
            f.write('%d\n%d\n%d\n%d %d\n%d %d\n%d'%(self.curve.a, self.curve.b, self.curve.q,
                self.gen.x, self.gen.y, self.pub.x, self.pub.y, self.n))
        else:
            f.write('%d\n%d\n%d\n%d %d\n%d %d'%(self.curve.a, self.curve.b, self.curve.q,
                self.gen.x, self.gen.y, self.pub.x, self.pub.y))

        f.flush()

    @classmethod
    def load(cls, f):
        lines = [line.strip() for line in f.readlines()]
        assert len(lines) >= 5

        curve = ec.Curve(*map(int, lines[:3]))
        gen = curve.Point(*map(int, lines[3].split()))
        pub = curve.Point(*map(int, lines[4].split()))

        if lines >= 6:  # Private key
            n = int(lines[5])
        else:
            n = None
        return cls(curve, gen, pub, n)

    def decrypt(self, inf, xoutf = None, youtf = None):
        if xoutf is None and youtf is None:
            raise ValueError('Useless decryption')

        for line in inf:
            components = line.strip().split()
            cpair = self.curve.Point(*map(int, components[:2]))
            hmpair = self.curve.Point(*map(int, components[2:]))
            plain = cpair - hmpair * self.n
            if xoutf:
                xoutf.write(chr(plain.x))
            if youtf:
                youtf.write(chr(plain.y))

        if xoutf:
            xoutf.flush()
        if youtf:
            youtf.flush()

    def __repr__(self):
        return 'Cipher(%r, %r, %r, %r)'%(self.curve, self.gen, self.pub, self.n)
