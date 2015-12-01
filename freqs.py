# Simple frequency counter
def freqs(buf):
    d = {}
    for c in buf:
        if c.isalpha():
            d[c.upper()] = d.get(c.upper(), 0) + 1
    return d

if __name__ == '__main__':
	import sys
	d = freqs(open(sys.argv[1]).read())
	l = sorted(d.items(), key=lambda pair: pair[1], reverse=True)
	print ''.join(map(lambda pair: pair[0], l))
	for k, v in l:
		print k, ':', v
