# Simple substitution translator
def trans(buf, key):
    l = [None] * len(buf)
    for idx, c in enumerate(buf):
        l[idx] = key.get(c.upper(), c)
    return ''.join(l)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 3:
        fromset = sys.argv[3]
    else:
        fromset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if len(sys.argv[2]) != len(fromset):
        raise ValueError('Must be equal replacement codepoints in second arg (toset=%d%r, fromset=%d%r)'%(len(sys.argv[2]), sys.argv[2], len(fromset), fromset))
    key = dict(zip(fromset, sys.argv[2]))
    print trans(open(sys.argv[1]).read(), key)
