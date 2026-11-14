# 도카폰! 분노의 철검 (SLPS-01559) 한글패치 빌드
import os,sys,json,struct,shutil,re,glob
from PIL import Image,ImageDraw,ImageFont
import keystone
W=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(W,'tools'))
from tbl import DEC
from ko import norm,toks,load_ko,check,HALFP
from disc import Writer
SRC=os.path.join(W,'..','Dokapon! Ikari no Tekken (Japan) (Rev 2).bin')
OUT=os.path.join(W,'..','Dokapon! Ikari no Tekken (Japan) (Rev 2) [KR].bin')
log=open(os.path.join(W,'build.log'),'w',encoding='utf-8')
ks=keystone.Ks(keystone.KS_ARCH_MIPS,keystone.KS_MODE_MIPS32+keystone.KS_MODE_LITTLE_ENDIAN)
def asm(src,addr):
    enc,_=ks.asm('.set noreorder;'+src,addr); return bytes(enc)

files={}
def F(path):
    if path not in files:
        fp=os.path.join(W,'orig',path)
        if os.path.exists(fp): files[path]=bytearray(open(fp,'rb').read())
        else:
            # 추출하지 않은 파일(F_xx 등)은 원본 디스크에서 직접 읽음
            from iso import Disc
            d=Disc(SRC); _,l,sz,_,_=[e for e in d.walk() if e[0]=='/'+path][0]
            files[path]=bytearray(d.read(l,sz))
    return files[path]

# ---------- 번역 로드 ----------
J={e['id']:e for e in json.load(open(os.path.join(W,'text/ja.json'),encoding='utf-8'))}
KO={}
for p in sorted(glob.glob(os.path.join(W,'text/ko/*.tsv'))):
    KO.update(load_ko(p))
nerr=0
for k,v in KO.items():
    e=J.get(k)
    if not e: print('unknown id',k,file=log); continue
    er=check(e['ja'],v,e['cap'],e['w'])
    if er: nerr+=1; print('ERR',k,er,v,file=log)

# ---------- 글자표 ----------
ENC={}
for c,ch in DEC.items():
    if c<0x160 and ch not in ENC: ENC[ch]=c
ENC['　']=0x100

# ---------- 이름 입력 격자 (NAMEIN.BIN) ----------
GRID1='가나다라마바사아자차카타파하거너더러머버서어저처커터퍼허고노도로모보소오조초코토포호구누두루무부수우주추쿠투푸후그느드르므브스으즈츠크트프흐기니디리미비시이지치키티피히개내대래매배'
GRID2='새애재채태해게네데레메베세에제체케테페헤강건경광규근길김남동란련령린명문민박범별병봉빈산상석선성손송순슬승식신실심안양연영옥완용운원윤율은의인일장전정종준중진찬창철현형혜홍화환훈희'
assert len(GRID1)==90 and len(GRID2)==90
newchars=[]
for k,v in KO.items():
    for t in toks(norm(v)):
        if len(t)==1 and t not in ENC and t!=' ' and t not in newchars: newchars.append(t)
for c in GRID1+GRID2:
    if c not in ENC and c not in newchars: newchars.append(c)
newchars.sort()
halfs=[c for c in HALFP]
# 요일 코드(0x200=일 … 0x206=토)는 게임이 직접 계산해 찍으므로 그 자리에 한글 요일을 둔다
WEEK='일월화수목금토'
newchars=list(WEEK)+halfs+[c for c in newchars if c not in halfs and c not in WEEK]
GBASE=0x200
HALFSTART=GBASE+len(WEEK)
HALFEND=HALFSTART+len(halfs)
assert HALFEND<=0x210
for i,c in enumerate(newchars): ENC[c]=GBASE+i
json.dump({c:v for c,v in ENC.items()},open(os.path.join(W,'enc.json'),'w',encoding='utf-8'),ensure_ascii=False)
NG=len(newchars)
SPACE=GBASE+NG   # 글리프 뒤 빈 코드를 공백으로
GLYPH_OFF=0x3c00
assert GLYPH_OFF+NG*32<=0x10000,('글자 수 초과',NG)
print('새 글자',NG,file=log)

def encode(s):
    out=bytearray()
    for t in toks(norm(s)):
        if t=='⏎': v=0x9000
        elif t.startswith('{'): v=int(t[1:5],16)
        elif t==' ': v=SPACE
        else: v=ENC[t]
        out+=struct.pack('<H',v)
    return bytes(out+b'\xff\xff')

# ---------- 문자열 삽입 ----------
for k,v in KO.items():
    e=J.get(k)
    if not e: continue
    path,off=k.rsplit(':',1); off=int(off,16)
    b=F(path); data=encode(v)
    cap=e['cap']*2
    if len(data)>cap:
        print('OVER',k,len(data),cap,file=log); data=data[:cap-2]+b'\xff\xff'
    b[off:off+len(data)]=data

def grid(chars):
    out=[0x9300]
    for r in range(9):
        out+=[0x8407,0x8500+2*r]
        row=chars[r*10:r*10+10]
        for k in range(5): out+=[ENC[row[k]],0x9300]
        out[-1]=0x9300; out+=[0x100]
        for k in range(5,10): out+=[ENC[row[k]],0x9300]
        out.pop()
    return struct.pack('<%dH'%len(out),*out)+bytes([255,255])
nm=F('BIN/NAMEIN.BIN')
for off,chars in ((0x11a4,GRID1),(0x1334,GRID2)):
    g=grid(chars); assert len(g)<=0x190,len(g)
    assert nm[off:off+2]==bytes([0,0x93])
    nm[off:off+len(g)]=g

# ---------- 글꼴 ----------
font=F('DATA/FONT.DAT')
FB=0x20c   # 글꼴 시작(파일 오프셋)
TTF=ImageFont.truetype(os.path.join(W,'..','NanumSquareNeo-bRg.ttf'),14)
def glyph(c):
    im=Image.new('L',(16,16),0); d=ImageDraw.Draw(im); d.fontmode='1'
    if c in HALFP:
        bb=TTF.getbbox(c); d.text(((8-(bb[2]-bb[0]))//2-bb[0],0),c,font=TTF,fill=255)
    else:
        d.text((1,0),c,font=TTF,fill=255)
    px=im.load(); out=b''
    for y in range(16):
        m=0
        for x in range(16):
            if px[x,y]>=110: m|=1<<x
        out+=struct.pack('<H',m)
    return out
gl=b''.join(glyph(c) for c in newchars)
font[FB+0x3800:FB+0x3c00]=bytes(0x400)          # 스크래치 영역
font[FB+GLYPH_OFF:FB+GLYPH_OFF+len(gl)]=gl

# ---------- 실행파일 패치 ----------
exe=F('SLPS_015.59')
def eoff(a): return a-0x80024bc0+0x800
HOOK=0x800254f0
hook=f'''
 sltiu $t0,$a2,0x200
 bnez $t0,done
 addiu $t0,$zero,{SPACE:#x}
 beq $a2,$t0,space
 nop
 lw $t1,0x26c($gp)
 addiu $t2,$a2,{-GBASE}
 sll $t2,$t2,5
 addu $t2,$t2,$t1
 addiu $t2,$t2,{GLYPH_OFF}
 addiu $s0,$t1,0x3800
 move $t3,$s0
 addiu $t4,$zero,16
row:
 lhu $t5,0($t2)
 addiu $t2,$t2,2
 addiu $t6,$zero,-1
 addiu $t7,$zero,3
bit:
 beqz $t5,store
 andi $t9,$t5,1
 beqz $t9,skip
 srl $t5,$t5,1
 nor $t9,$t7,$zero
 and $t6,$t6,$t9
skip:
 j bit
 sll $t7,$t7,2
store:
 sw $t6,0($t3)
 addiu $t4,$t4,-1
 bnez $t4,row
 addiu $t3,$t3,0x40
 sltiu $t0,$a2,{HALFEND:#x}
 beqz $t0,done
 sltiu $t0,$a2,{HALFSTART:#x}
 bnez $t0,done
 nop
 jal 0x80055584
 move $a2,$s0
 j 0x80052088
 addiu $s3,$zero,1
done:
 j 0x80055584
 move $a2,$s0
space:
 addiu $s3,$zero,1
 j 0x80052088
 nop
'''
code=asm(hook,HOOK)
assert len(code)<0x5d0
exe[eoff(HOOK):eoff(HOOK)+len(code)]=code
exe[eoff(0x80052030):eoff(0x80052030)+8]=asm('jal %#x; nop'%HOOK,0x80052030)
import gfx; gfx.apply(F)
# ---------- 디스크 ----------
shutil.copyfile(SRC,OUT)
w=Writer(OUT)
for path,new in files.items():
    _,lba,size,_,_=w.files['/'+path]
    assert len(new)==size,(path,len(new),size)
    old=w.read(lba,size)
    for k in range(0,size,2048):
        if old[k:k+2048]!=new[k:k+2048]:
            w.wsec(lba+k//2048,bytes(new[k:k+2048]),keep_sub=True)
w.f.close()
print('완료 새글자',NG,'오류',nerr)
