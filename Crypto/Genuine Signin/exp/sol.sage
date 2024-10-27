from Crypto.Util.number import *
exec(open('output.txt', 'r').read())

P.<x> = PolynomialRing(Zmod(N), 1)

for k in range(3):
    f = x^3 - a
    g = (k*x+1)^3 - e^3*b
    fg = gcd(f, g)
    if fg == 1: continue
    phi = ZZ(-fg[0] / fg[1])
    if gcd(e, phi) != 1: continue
    d = pow(e, -1, phi)
    print(long_to_bytes(pow(c, d, N)))