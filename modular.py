# Borrowed algorithms for modular arithmetic

# http://anh.cs.luc.edu/331/notes/xgcd.pdf
def xgcd(a,b):
    prevx, x = 1, 0;  prevy, y = 0, 1
    while b:
        q = a/b
        x, prevx = prevx - q*x, x
        y, prevy = prevy - q*y, y
        a, b = b, a % b
    return a, prevx, prevy
# ...Python is cool, m'kay

def modinv(a, m):
    g, x, y = xgcd(a, m)
    if g != 1:
        raise ValueError('modular inverse does not exist')
    else:
        return x % m
