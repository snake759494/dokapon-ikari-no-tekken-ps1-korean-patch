import struct
from PIL import Image
def parse(b,o):
    """TIM 파싱 → dict 또는 None"""
    if o+8>len(b): return None
    magic,flag=struct.unpack_from('<II',b,o)
    if magic!=0x10 or flag not in (0,1,2,3,8,9): return None
    bpp=flag&3; hasc=flag&8; p=o+8; cl=None
    if hasc:
        ln,cx,cy,cw,ch=struct.unpack_from('<I4H',b,p)
        if ln!=12+cw*ch*2 or cw==0 or ch==0 or cw>256: return None
        cl=(cx,cy,cw,ch,p+12); p+=ln
    if p+12>len(b): return None
    ln,ix,iy,iw,ih=struct.unpack_from('<I4H',b,p)
    if ln!=12+iw*ih*2 or iw==0 or ih==0 or iw>1024 or ih>512: return None
    return dict(off=o,bpp=bpp,clut=cl,img=(ix,iy,iw,ih,p+12),end=p+ln)
def render(b,t,pal=0):
    ix,iy,iw,ih,po=t['img']; bpp=t['bpp']
    cols=None
    if t['clut']:
        cx,cy,cw,ch,cp=t['clut']
        n=16 if bpp==0 else 256
        cols=[struct.unpack_from('<H',b,cp+2*(pal*n+i))[0] for i in range(min(n,cw*ch-pal*n))]
    def c15(v): return ((v&31)<<3,((v>>5)&31)<<3,((v>>10)&31)<<3, 0 if v==0 else 255)
    w={0:iw*4,1:iw*2,2:iw}[bpp] if bpp<3 else iw
    im=Image.new('RGBA',(w,ih)); px=im.load()
    for y in range(ih):
        row=b[po+y*iw*2:po+(y+1)*iw*2]
        for x in range(w):
            if bpp==0: v=(row[x//2]>>((x&1)*4))&15; px[x,y]=c15(cols[v]) if cols and v<len(cols) else (v*17,)*3+(255,)
            elif bpp==1: v=row[x]; px[x,y]=c15(cols[v]) if cols and v<len(cols) else (v,v,v,255)
            else: v=struct.unpack_from('<H',row,x*2)[0]; px[x,y]=c15(v)
    return im
def scan(b):
    out=[];o=0
    while o<len(b)-8:
        t=parse(b,o)
        if t: out.append(t); o=t['end']; o=(o+3)&~3
        else: o+=4
    return out
