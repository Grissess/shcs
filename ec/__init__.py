# Basic elliptic curve functionality
from .. import modular

class Curve(object):
    def __init__(self, a, b, q):
        self.a = a
        self.b = b
        self.q = q

    class _Point(object):
        def __init__(self, curve, x, y):
            self._curve = curve

            if x is None and y is None:
                self._x = None
                self._y = None
            else:
                self._x = x % curve.q
                self._y = y % curve.q

        def _get_x(self):
            return self._x

        def _get_y(self):
            return self._y

        def _set_x(self, x):
            if x is None:
                self._x = None
            else:
                self._x = x % self._curve.q

        def _set_y(self, y):
            if y is None:
                self._y = None
            else:
                self._y = y % self._curve.q

        x = property(_get_x, _set_x)
        y = property(_get_y, _set_y)

        @property
        def curve(self):
            return self._curve

        def __getitem__(self, index):
            return [self._x, self._y][index]

        def __setitem__(self, index, val):
            setattr(self, ['x', 'y'][item], val)

        def is_at_infinity(self):
            return self.x is None and self.y is None

        def __add__(self, other):
            assert isinstance(other, Curve._Point)

            # Properties (point at infinity is an identity element)
            if self.is_at_infinity():
                return other
            if other.is_at_infinity():
                return self

            # Case 1
            if self.x != other.x:
                m = ((other.y - self.y) * modular.modinv(other.x - self.x, self.curve.q)) % self.curve.q
                x = (m * m - (self.x + other.x)) % self.curve.q
                y = (other.y + m * (x - other.x)) % self.curve.q
                return self.curve.Point(x, self.curve.q - y)
            else:
                # Case 2
                if self.y == -other.y:
                    return self.curve.POINT_AT_INFINITY
                # Case 3 (equality)
                elif self.y == other.y:
                    m = ((3 * self.x * self.x + self.curve.a) * modular.modinv(2 * self.y, self.curve.q)) % self.curve.q
                    x = (m * m - 2 * self.x) % self.curve.q
                    y = (self.y + m * (x - self.x)) % self.curve.q
                    return self.curve.Point(x, self.curve.q - y)

        def __mul__(self, other):
            assert isinstance(other, (int, long))

            if other == 0:
                return self.curve.POINT_AT_INFINITY
            elif (other & 1) == 0:  # Even
                halfp = self * (other / 2)
                return halfp + halfp
            else:  # Odd (and nonzero)
                return self + (self * (other - 1))

        def inv(self):
            return self.curve.Point(self.x, self.curve.q - self.y)

        def __sub__(self, other):
            assert isinstance(other, Curve._Point)
            return self + other.inv()

        def __repr__(self):
            return '%r.Point(%r, %r)'%(self.curve, self.x, self.y)

    @property
    def POINT_AT_INFINITY(self):
        return self.Point(None, None)

    def Point(self, x, y):
        return Curve._Point(self, x, y)

    def __repr__(self):
        return 'Curve(%r, %r, %r)'%(self.a, self.b, self.q)
