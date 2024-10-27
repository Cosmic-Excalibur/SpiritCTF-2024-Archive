import random
import hashlib
import pickle
import math
import primefac
import itertools
from tqdm import tqdm, trange
from functools import reduce
from Crypto.Util.number import *

N = 233333

class FeatherStitching:
    def __init__(self, stitching):
        self.stitching = list(stitching)
        self.unstitching = None
        
        # sanity check (slooooooowwww)
        # assert set(self.stitching) == set(range(N))
    
    def __mul__(self, other):
        new = FeatherStitching([other.stitching[s] for s in self.stitching])
        return new
    
    def __pow__(self, n):
        new = UNIT
        if n == 0: return UNIT
        if n > 0:
            double = self
        else:
            double = self.inverse()
            n = -n
        while n > 0:
            if n & 1:
                new *= double
            double *= double
            n >>= 1
        return new

    def inverse(self):
        if self.unstitching == None:
            self.unstitching = [0]*N
            for i, j in enumerate(stitching):
                self.unstitching[j] = i
        return FeatherStitching(self.unstitching)
    
    def __eq__(self, other):
        return self.stitching == other.stitching
    
    def __repr__(self):
        return 'FeatherStitching(%s)' % repr(self.stitching)
        
    def __str__(self):
        return 'FeatherStitching(%s)' % str(self.stitching)
    
    def __reduce__(self):
        return (self.__class__, (self.stitching,))

UNIT = FeatherStitching(range(N))

pad = lambda m, l: m + bytes(random.randrange(256)*bool(i) for i in range(l - len(m)))
unpad = lambda m: m[:m.index(0)] if 0 in m else m

def stitch(msg, stitching):
    assert len(msg) == 128
    return bytes(a ^ b for a, b in zip(msg, hashlib.sha512(' :p '.join(map(str, stitching.stitching)).encode()).digest() + hashlib.sha512(' XD '.join(map(str, stitching.stitching)).encode()).digest()))

def unstitch(ct, stitching):
    assert len(ct) == 128
    return bytes(a ^ b for a, b in zip(ct, hashlib.sha512(' :p '.join(map(str, stitching.stitching)).encode()).digest() + hashlib.sha512(' XD '.join(map(str, stitching.stitching)).encode()).digest()))

def get_cycles(stitching):
    start = None
    lengths = {}
    l = None
    i = 0
    tmp = []
    visited = set()
    while i < N:
        if start == None or start[0] == j:
            if l != None:
                #lengths.update({l: lengths.get(l, 0) + 1})
                lengths.update({l: lengths.get(l, []) + [tuple(tmp)]})
                tmp = []
            l = 0
            while i < N and (j := stitching.stitching[i]) in visited:
                i += 1
            start = (j, i)
        l += 1
        tmp.append(j)
        visited.add(j)
        j = stitching.stitching[j]
    return lengths

prod = lambda p: reduce(lambda a, b: a*b, p)

def order(cycles):
    facs = {}
    for i in cycles.keys():
        e = {}
        for pp in primefac.primefac(i):
            e.update({pp: e.get(pp, 0) + 1})
        for pp, ee in e.items():
            facs.update({pp: max(facs.get(pp, 0), ee)})
    return prod(pp**ee for pp, ee in facs.items())

exec(open("ct.txt", "r").read())
with open("gift.pickle", "rb") as f:
    gift = pickle.load(f)

cycles = get_cycles(gift)
o1 = order(cycles)
o0 = o1 * 2

k = 1337133713371337133713371337713371337133713371337133702
g = math.gcd(k, o1)

assert g == 2    # for simplicity
assert [(x, len(cycles[x])) for x in sorted(cycles.keys())] == [
 (1, 1),
 (3, 4),
 (4, 2),
 (34, 2),
 (687, 1),
 (48605, 1),
 (66053, 1),
 (117899, 1)
]    # for simplicity

fs2 = gift**pow(k//g, -1, o0//g)

cycles = get_cycles(fs2)
print("lengths: %s" % [(x, len(cycles[x])) for x in sorted(cycles.keys())])
print("true order: %s" % o0)
print("gcd: %s" % g)

def test(s):
    flag = unstitch(ct, s)
    if flag.startswith(b'Spirit{'):
        print()
        print(flag)
        print()

def update_s(s, cs):
    for c in cs:
        for i in range(len(c)):
            s.stitching[c[i-1]] = c[i]

def g(a, b):
    assert len(a) == len(b)
    n = len(a)
    s = [0]*n*2
    s[0:2*n:2] = a
    for i in range(n):
        s[1:2*(n-i):2] = b[i:]
        s[2*(n-i)+1:2*n:2] = b[:i]
        yield tuple(s)

def f(s, c):
    cc = [0]*len(c)
    cc[1::2] = c[:len(c)//2]
    cc[0::2] = c[len(c)//2:]
    update_s(s, [cc])

for i in [1, 687, 48605, 66053, 117899]:
    f(fs2, cycles[i][0])

for i1 in tqdm(g(*cycles[34]), total = 34):
    for i2 in g(*cycles[4]):
        for i3 in itertools.combinations(cycles[3], 2):
            for i4 in g(*i3):
                i5 = list(set(cycles[3]) - set(i3))
                cs = [
                    (i5[0][1], i5[0][0], i5[0][2]),
                    (i5[1][1], i5[1][0], i5[1][2]),
                    i1, i2, i4
                ]
                update_s(fs2, cs)
                test(fs2)