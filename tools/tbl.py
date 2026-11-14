import os,struct
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','text')
DEC={}
for l in open(os.path.join(D,'table.txt'),encoding='utf-8'):
    l=l.rstrip('\n')
    if not l: continue
    base=int(l[:3],16)
    for i,c in enumerate(l[4:]): DEC[base+i]=c
def dec(b):
    out=[]
    for i in range(0,len(b),2):
        v=struct.unpack_from('<H',b,i)[0]
        if v==0xffff: break
        if v in DEC: out.append(DEC[v])
        elif v==0x9000: out.append('\n')
        else: out.append('{%04x}'%v)
    return ''.join(out)
