import sys, optparse, multiprocessing, random

import trans, freqs, randkfill

parser = optparse.OptionParser()
parser.add_option('--select-alpha', dest='select_alpha', type='float', help='Alpha parameter for selection PDF')
parser.add_option('--select-beta', dest='select_beta', type='float', help='Beta parameter for selection PDF')
parser.add_option('--swap-alpha', dest='swap_alpha', type='float', help='Alpha parameter for swapion PDF')
parser.add_option('--swap-beta', dest='swap_beta', type='float', help='Beta parameter for swapion PDF')
parser.add_option('-t', '--to-set', dest='to_set', help='To set; sets the sequence order (use lang letter frequency)')
parser.add_option('-f', '--from-set', dest='from_set', help='From set; initial best guess at key (tr from to), use cipher letter frequency')
parser.add_option('-F', '--fix', '-p', '--pin', dest='pin', help='Don\'t swap these letters (in the to set, or plaintext)')
parser.add_option('-T', '--threads', dest='threads', type='int', help='Threads to spawn per file')
parser.add_option('-w', '--words', dest='words', help='Comma-separated list of words known in the plaintext')
parser.add_option('-R', '--rand', dest='rand', help='Which random class to use (see docs)')
parser.add_option('-v', '--verbose', action='store_true', dest='verbose', help='Be very verbose')
parser.set_defaults(select_alpha=0.8, select_beta=0.9, swap_alpha=2, swap_beta=24, threads=multiprocessing.cpu_count(), pin='', rand='Random')

options, args = parser.parse_args()

if not (options.from_set and options.to_set and options.words and args):
    raise ValueError('All of the following are required: from set, to set, words, file to translate (positional)')

from_set = list(options.from_set)
from_indices = {idx: c for idx, c in enumerate(from_set)}
to_set = list(options.to_set)
for pin in options.pin:
    del from_indices[to_set.index(pin)]
from_indices = sorted(from_indices.keys())
buffers = map(lambda fname: open(fname).read(), args)
words = options.words.split(',')
rand = getattr(random, options.rand)()

class SearchProcess(multiprocessing.Process):
    def run(self):
        buf, key, rand, queue = self._args
        sel_a, sel_b, swp_a, swp_b = options.select_alpha, options.select_beta, options.swap_alpha, options.swap_beta
        while True:
            plain = trans.trans(buf, dict(zip(key, to_set)))
            do_break = True
            for word in words:
                if word in plain:
                    break
            else:
                do_break = False
            if do_break:
                queue.put((key, plain))
                break
            moving_indices = from_indices
            sel_idx = int((len(from_indices)-1)*rand.betavariate(sel_a, sel_b))
            select = from_indices[sel_idx]
            swp_idx = min(len(from_indices)-1, sel_idx + 1 + len(from_indices) * int(rand.betavariate(swp_a, swp_b)))
            swap = from_indices[swp_idx]
            if options.verbose:
                print 'Swap step:'
                print ''.join(key)
                print (' '*(select))+'^'+('-'*(swap-select-1))+'^'
            temp = key[select]
            key[select] = key[swap]
            key[swap] = temp
            if swap == select:
                print "you're a tool"

main_queue = multiprocessing.Queue()
processes = [None] * options.threads
for i in xrange(options.threads):
    processes[i] = SearchProcess(args=(buffers[0], from_set, rand, main_queue))
for pro in processes:
    pro.start()
while True:
    key, plain = main_queue.get()
    print '!!!TRANSLATION FOUND!!!'
    print 'Key:', key
    print 'Printable:', ''.join(key)
    print 'Plaintext:'
    print plain
