from pwn import *
from tqdm import trange

#io = process(["python", "task.py"])
io = remote("202.198.27.90", 40141)

io.recvuntil(b'if `P = (')
Px = int(io.recvuntil(b', ', drop = 1))
Py = int(io.recvuntil(b')`', drop = 1))
Qxs = []
Qys = []
for i in range(5):
    io.recvuntil(b's*P = (')
    Qxs.append(int(io.recvuntil(b', ', drop = 1)))
    Qys.append(int(io.recvuntil(b')`', drop = 1)))

P.<a, b> = ZZ[]
gb = P.ideal([x**3 + a*x + b - y**2 for x, y in zip(Qxs, Qys)]).groebner_basis()
P.<q> = ZZ[]

p = int(sage.rings.factorint.factor_trial_division(gb[2], 300000)[-1][0])
a = gb[0](q, 0).roots()[0][0]%p
b = gb[1](0, q).roots()[0][0]%p
GFp = GF(p)

print("p: 0x%x" % p)
print("a: 0x%x" % a)
print("b: 0x%x" % b)

m = 100
u = p**2
B = 100000000

visited = set()

def oracle(x, y):
    io.recvuntil(b'>>> ')
    io.sendline(b'1')
    io.recvuntil(b'P = ')
    io.sendline(', '.join(map(str, [x, y])).encode())
    line = io.recvline()
    if b'Invalid' in line: return None
    return ZZ(line.split(b'Qx = ')[1].decode().strip())

moduli = []
remainders = []
N = 1
visited = set()

for i in trange(1, m+1):
    bi = i
    try:
        Ei = EllipticCurve(GFp, [a, bi])
    except ArithmeticError:
        continue
    oi = Ei.order()
    G = Ei.gens()[0]
    facs = sage.rings.factorint.factor_trial_division(oi, B)
    if len(facs) == 1: continue
    G *= facs[-1][0]
    tmp = G.order()
    facs = factor(tmp)
    t = []
    for pp, ee in facs:
        if pp in visited:
            G *= pp**ee
            tmp //= pp**ee
        else:
            t.append(pp)
    if not G: continue
    assert G.order() == tmp
    x = oracle(*G.xy())
    if x == None: continue
    
    H = Ei.lift_x(x)
    for pp in t: visited.add(pp)
    moduli.append(tmp)
    h = ZZ(G.discrete_log(H))
    print()
    print('Ord:', tmp)
    print('Facs:', sorted(visited))
    print('Dist:', u // N)
    print('Dlog:', h)
    remainders.append(pow(h, 2, tmp))
    N *= tmp
    if N > u: break

s2 = ZZ(crt(remainders, moduli))
s = sqrt(GF(p)(s2))

print()
print('s1:', s)
print('s2:', -s)

io.interactive()