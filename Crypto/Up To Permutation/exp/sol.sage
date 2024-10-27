from subprocess import check_output
from re import findall
import hashlib

def flatter(M):
    # compile https://github.com/keeganryan/flatter and put it in $PATH
    z = "[[" + "]\n[".join(" ".join(map(str, row)) for row in M) + "]]"
    ret = check_output(["flatter"], input=z.encode())
    return matrix(M.nrows(), M.ncols(), map(ZZ, findall(b"-?\\d+", ret)))

with open("output.txt", "r") as f:
    exec(f.read())

pbits = 360
nbits = 3840
n = 16

vec = []

P = prod(primes)

for i in range(n):
    p = primes[i]
    Pi = P // p
    for j in range(n):
        vec.append(data[i][j] * Pi * pow(Pi, -1, p))

A = block_matrix([
[P, 0],
[column_matrix(vec), 2**nbits]
])

print("(%d, %d)" % A.dimensions())

A_ = flatter(A)

def decrypt(ct, secrets):
    return bytes(x ^^ y for x, y in zip(ct, hashlib.sha512(str(list(secrets)).encode()).digest()))

print(decrypt(ct, sorted([abs(x) for x in A_.column(0)[:n]])))
