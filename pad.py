from random import SystemRandom()

sr = SystemRandom()

class LSBPadder(object):
    def __init__(self, bits):
        self.bits = bits

    def pad(self, val):
        return val << self.bits | sr.getrandbits(self.bits)

    def unpad(self, val):
        return val >> self.bits
