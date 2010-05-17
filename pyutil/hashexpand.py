#  Copyright (c) 2000 Autonomous Zone Industries
#  Copyright (c) 2002-2009 Zooko Wilcox-O'Hearn
#  This file is part of pyutil; see README.txt for licensing terms.

"""
Cryptographically strong pseudo-random number generator based on SHA256.
"""

class SHA256Expander:
    """
    Provide a cryptographically strong pseudo-random number generator based on
    SHA256.  Hopefully this means that no attacker will be able to predict any
    bit of output that he hasn't seen, given that he doesn't know anything about
    the seed and given that he can see as many bits of output as he desires
    except for the bit that he is trying to predict.  Further it is hoped that
    an attacker will not even be able to determine whether a given stream of
    random bytes was generated by this PRNG or by flipping a coin repeatedly.
    The safety of this technique has not been verified by a Real Cryptographer.
    ... but it is similar to the PRNG in FIPS-186...

    The seed and counter are encoded in DJB's netstring format so that I
    don't have to think about the possibility of ambiguity.
    
    Note: I've since learned more about the theory of secure hash functions and
    the above is a strong assumption about a secure hash function.  Use of this
    class should be considered deprecated and you should use a more
    well-analyzed KDF or stream cipher or whatever it is that you need.
    """
    def __init__(self, seed=None):
        if seed is not None:
            self.seed(seed)

    def seed(self, seed):
        import hashlib
        self.starth = hashlib.sha256('24:pyutil hash expansion v2,10:algorithm:,6:SHA256,6:value:,')
        seedlen = len(seed)
        seedlenstr = str(seedlen)
        self.starth.update(seedlenstr)
        self.starth.update(':')
        self.starth.update(seed)
        self.starth.update(',')

        self.avail = ""
        self.counter = 0

    def get(self, bytes):
        bytesleft = bytes

        res = []

        while bytesleft > 0:
            if len(self.avail) == 0:
                h = self.starth.copy()
                counterstr = str(self.counter)
                counterstrlen = len(counterstr)
                counterstrlenstr = str(counterstrlen)
                h.update(counterstrlenstr)
                h.update(':')
                h.update(counterstr)
                h.update(',')
                self.avail = h.digest()
                self.counter += 1

            numb = min(len(self.avail), bytesleft)

            (chunk, self.avail,) = (self.avail[:numb], self.avail[numb:],)

            res.append(chunk)
            
            bytesleft = bytesleft - numb

        resstr = ''.join(res)
        assert len(resstr) == bytes

        return resstr

def sha256expand(inpstr, expbytes):
    return SHA256Expander(inpstr).get(expbytes)
