import sys

while True:
	ch = sys.stdin.read(1)
	if not ch:
		break
	if ch in ('\r', '\n'):
		continue
	sys.stdout.write(ch)
