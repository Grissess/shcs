# Randomly fill out a freq-generated key

import random
sr = random.SystemRandom()

def randkfill(key):
	letters = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
	for k in key:
		letters.discard(k.upper())
	return key + ''.join(sr.sample(list(letters), len(letters)))

if __name__ == '__main__':
	import sys
	sys.stdout.write(randkfill(sys.stdin.read()))
