import sys,os
sys.path.insert(0,os.path.dirname(__file__))
from iso import Disc
d=Disc(sys.argv[1]); out=sys.argv[2]
for p,l,sz,_,_ in d.walk():
    if p.startswith(('/SND','/MOV','/SAFTY','/BATTLE/BOSS','/BATTLE/ENE','/BATTLE/PLAYER','/DATA/TRS','/DATA/F_','/DATA/EFFECT')): continue
    fp=os.path.join(out,p.lstrip('/')); os.makedirs(os.path.dirname(fp),exist_ok=True)
    open(fp,'wb').write(d.read(l,sz))
