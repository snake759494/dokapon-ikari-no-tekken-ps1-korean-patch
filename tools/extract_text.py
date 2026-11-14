import os,sys,struct,json,re
sys.path.insert(0,os.path.dirname(__file__))
from scan16 import strings
from tbl import dec,DEC
SKIP=('ram1.bin','.txt','files.txt')
def width_lines(b):
    half=False; lines=[0]
    for i in range(0,len(b),2):
        v=struct.unpack_from('<H',b,i)[0]
        if v==0xffff: break
        if v>=0x8000:
            h=v>>8
            if h==0x93: half=True
            elif h==0x94: half=False
            elif h==0x90: lines.append(0)
            elif h==0x92: lines.append(0)
            elif v==0x81ff: lines[-1]+=12
            elif h==0x80: lines[-1]+=4
            continue
        if v<0x100: lines[-1]+= 1 if half else 2
        elif v<0x200 and half: lines[-1]+=1
        else: lines[-1]+=2
    return lines
out=[]
for root,_,fs in os.walk('orig'):
    for f in sorted(fs):
        p=os.path.join(root,f).replace(os.sep,'/')
        if p.endswith(SKIP): continue
        b=open(p,'rb').read()
        ss=strings(b)
        for k,(s,e) in enumerate(ss):
            cap=e-s
            # use zero padding up to 4-byte alignment
            while (s+cap)%4 and s+cap+2<=len(b) and b[s+cap:s+cap+2]==b'\0\0': cap+=2
            ja=dec(b[s:e])
            out.append(dict(id='%s:%x'%(p[5:],s),cap=cap//2,ja=ja,w=max(width_lines(b[s:e]))))
json.dump(out,open('text/ja.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
print(len(out))
