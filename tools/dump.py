import os,sys,struct
sys.path.insert(0,os.path.dirname(__file__))
from scan16 import strings
from tbl import dec
out=open('text/dump_ja.txt','w',encoding='utf-8')
for root,_,fs in os.walk('orig'):
    for f in sorted(fs):
        p=os.path.join(root,f).replace(os.sep,'/')
        if p.endswith(('ram1.bin','.txt')): continue
        b=open(p,'rb').read()
        for s,e in strings(b):
            out.write('%s:%x: %s\n'%(p[5:],s,dec(b[s:e]).replace('\n','⏎')))
