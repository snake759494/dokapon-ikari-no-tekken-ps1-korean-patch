import sys,os,re
pat=re.compile(rb'(?:[\x81-\x9f\xe0-\xea][\x40-\xfc]){4,}')
tot={}
for root,_,fs in os.walk('orig'):
    for f in fs:
        p=os.path.join(root,f); b=open(p,'rb').read()
        ms=[m for m in pat.finditer(b)]
        good=[]
        for m in ms:
            try: s=m.group().decode('cp932')
            except: continue
            if sum(1 for c in s if '぀'<=c<='ヿ')>=len(s)//2: good.append(s)
        if good: tot[p]=(len(good),good[:3])
for p,(n,g) in sorted(tot.items(),key=lambda x:-x[1][0]): print(n,p,g)
