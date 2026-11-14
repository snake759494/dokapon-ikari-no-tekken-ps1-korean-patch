import os,struct,sys,collections
def strings(b):
    out=[];i=0;n=len(b)&~1
    while i<n:
        j=i;good=0;bad=0
        while j<n:
            v=struct.unpack_from('<H',b,j)[0]
            if v==0xffff: break
            if 0x100<=v<0x490: good+=1
            elif (v>>8) in range(0x80,0x96): pass
            elif v<0x100 and v>=0x20: bad+=0.5
            else: bad+=1
            if bad>0: break
            j+=2
        if j<n and good>=2 and bad==0 and struct.unpack_from('<H',b,j)[0]==0xffff:
            out.append((i,j+2)); i=j+2
        else: i+=2
    return out
if __name__=='__main__':
    tot=collections.Counter();cnt=collections.Counter()
    for root,_,fs in os.walk('orig'):
        for f in fs:
            p=os.path.join(root,f)
            if p.endswith('ram1.bin') or p.endswith('.txt'): continue
            b=open(p,'rb').read()
            for al in (0,):
                ss=strings(b[al:])
                if ss: tot[p]=sum(e-s for s,e in ss); cnt[p]=len(ss)
    for p,v in tot.most_common(): print(p,cnt[p],v)
    print(sum(tot.values()),sum(cnt.values()))
