# 이미지(TIM) 속 일본어를 한글로 다시 그린다
import os,struct
from PIL import Image,ImageDraw,ImageFont
from tim import scan
W=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
FD=os.path.join(W,'..')
def font(name,size):
    p=os.path.join(FD,name)
    if not os.path.exists(p): p=os.path.join(W,'fonts',name)
    return ImageFont.truetype(p,size)
BOLD='NanumSquareNeo-eHv.ttf'

def pal(b,t,n=0):
    cx,cy,cw,ch,cp=t['clut']
    out=[]
    for i in range(16 if t['bpp']==0 else 256):
        v=struct.unpack_from('<H',b,cp+2*(n*(16 if t['bpp']==0 else 256)+i))[0]
        out.append(((v&31)<<3,((v>>5)&31)<<3,((v>>10)&31)<<3))
    return out
def size(t):
    ix,iy,iw,ih,po=t['img']
    return ({0:iw*4,1:iw*2}[t['bpp']],ih,po)
def getpx(b,t,x,y):
    w,h,po=size(t)
    if t['bpp']==0: v=b[po+y*w//2+x//2]; return (v>>((x&1)*4))&15
    return b[po+y*w+x]
def setpx(b,t,x,y,v):
    w,h,po=size(t)
    if t['bpp']==0:
        o=po+y*w//2+x//2; sh=(x&1)*4
        b[o]=(b[o]&~(15<<sh)&255)|(v<<sh)
    else: b[po+y*w+x]=v

def bands(b,t,x0,y0,x1,y1):
    """내용 있는 행들을 띠(band)로 묶어 (top,bottom,left,right) 목록"""
    rows=[]
    for y in range(y0,y1):
        xs=[x for x in range(x0,x1) if getpx(b,t,x,y)]
        rows.append((y,min(xs),max(xs)) if xs else None)
    out=[];cur=None
    for r in rows:
        if r and cur is None: cur=[r[0],r[0],r[1],r[2]]
        elif r: cur[1]=r[0];cur[2]=min(cur[2],r[1]);cur[3]=max(cur[3],r[2])
        elif cur: out.append(cur);cur=None
    if cur: out.append(cur)
    return out

def draw_text(b,t,box,text,fill,stroke,fsize,fname=BOLD,align='c',sw=1,pals=None):
    """box=(x0,y0,x1,y1) 를 투명(0)으로 지우고 텍스트를 팔레트 최근접 색으로 그림"""
    x0,y0,x1,y1=box
    for y in range(y0,y1):
        for x in range(x0,x1): setpx(b,t,x,y,0)
    p=pals or pal(b,t)
    bw=x1-x0
    while True:
        f=font(fname,fsize)
        l,tp,r,bt=f.getbbox(text,stroke_width=sw)
        if r-l<=bw-4 or fsize<8: break
        fsize-=1
    im=Image.new('RGBA',(x1-x0,y1-y0),(0,0,0,0)); d=ImageDraw.Draw(im)
    tw=r-l; th=bt-tp
    if align=='l': ox=-l
    elif align=='r': ox=bw-tw-l
    else: ox=(bw-tw)//2-l
    oy=(y1-y0-th)//2-tp
    d.text((ox,oy),text,font=f,fill=fill,stroke_width=sw,stroke_fill=stroke)
    cand=[i for i in range(1,len(p))]
    px=im.load()
    for y in range(y1-y0):
        for x in range(bw):
            r_,g_,b_,a=px[x,y]
            if a<100: continue
            best=min(cand,key=lambda i:(p[i][0]-r_)**2+(p[i][1]-g_)**2+(p[i][2]-b_)**2)
            setpx(b,t,x0+x,y0+y,best)

def relayout(b,t,lines,fill,stroke,keep=0,fsize=None,sw=1,margin=1,force=None):
    """기존 텍스트 띠 위치에 줄 단위로 교체. keep=앞에서부터 보존할 띠 수"""
    w,h,_=size(t)
    bs=bands(b,t,0,0,w,h)[keep:]
    assert len(bs)==len(lines),(len(bs),len(lines),bs)
    for (top,bot,l,r),txt in zip(bs,lines):
        if txt is None: continue
        cx=(l+r)//2
        al='l' if l<w*0.2 and cx<w*0.5 else 'r' if r>w*0.8 and cx>w*0.5 else 'c'
        if force: al=force
        hh=bot-top+1
        draw_text(b,t,(0,max(0,top-margin),w,min(h,bot+1+margin)),txt,fill,stroke,fsize or hh,align=al,sw=sw)
        if al=='l':  # 왼쪽 정렬 시 원래 왼쪽 여백 유지: 오른쪽으로 이동
            shift(b,t,max(0,top-margin),min(h,bot+1+margin),l)
        elif al=='r':
            shift(b,t,max(0,top-margin),min(h,bot+1+margin),-(w-1-r))

def shift(b,t,y0,y1,dx):
    w,h,_=size(t)
    for y in range(y0,y1):
        row=[getpx(b,t,x,y) for x in range(w)]
        for x in range(w):
            sx=x-dx
            setpx(b,t,x,y,row[sx] if 0<=sx<w else 0)

def render_text(w,h,text,fill,stroke,fsize,fname=BOLD,sw=1,align='c'):
    while True:
        f=font(fname,fsize); l,tp,r,bt=f.getbbox(text,stroke_width=sw)
        if (r-l<=w-2 and bt-tp<=h) or fsize<8: break
        fsize-=1
    im=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(im)
    if fname.startswith('Galmuri'): d.fontmode='1'
    ox={'l':1-l,'r':w-1-r,'c':(w-(r-l))//2-l}[align]
    d.text((ox,(h-(bt-tp))//2-tp),text,font=f,fill=fill,stroke_width=sw,stroke_fill=stroke)
    return im
def blit(b,t,im,x0,y0,sx=0,w=None,h=None,clear=True,pals=None):
    p=pals or pal(b,t); px=im.load()
    w=w or im.width; h=h or im.height
    cache={}
    for y in range(h):
        for x in range(w):
            r_,g_,b_,a=px[sx+x,y]
            if a<100:
                if clear: setpx(b,t,x0+x,y0+y,0)
                continue
            k=(r_,g_,b_)
            if k not in cache: cache[k]=min(range(1,len(p)),key=lambda i:(p[i][0]-r_)**2+(p[i][1]-g_)**2+(p[i][2]-b_)**2)
            setpx(b,t,x0+x,y0+y,cache[k])
def rects_text(b,t,rects,text,fill,stroke,fsize,sw=1,fname=BOLD,align='c'):
    """여러 사각형(가로로 이어붙인 조각)에 한 문자열을 나눠 그림"""
    tw=sum(r[2] for r in rects); h=rects[0][3]
    im=render_text(tw,h,text,fill,stroke,fsize,fname,sw,align)
    sx=0
    for x,y,w,hh in rects:
        blit(b,t,im,x,y,sx,w,hh); sx+=w

# ---------------- 작업 목록 ----------------
TIT=[
 ['결전!','돈즈마리 동굴','왈사를 해치워라!'],
 ['헤매는 숲의 헬하우스','우리 돈을 되찾아라!'],
 ['사막에 솟은','피라미드','악마의 제물!'],
 ['구하라! 고래 베이스타','미크로 결사대!'],
 ['영구동토의','레이조코 동굴','영하 256도의 대결!'],
 ['꿈의 천계','하렘이다, 전원 집합!'],
 ['작열지옥의','사우난 유적','계란프라이를 손에 넣어라!'],
 ['바다에 잠든','전설의 신전','해저 2만 마일!'],
 ['잠입! 버블탑','왈사를 뒤쫓아라!'],
 ['자, 마계로!','평화까지 앞으로 한 걸음!?'],
]
OP2=['…어느 곳에','돈이 전부인','「도카폰 왕국」이','있었습니다.','어느 날, 이 나라의 왕이','온갖 사치를 다 부리며','손쓸 수 없게','되어 버렸습니다.']
OP3=['그런 왕에게','「돈 돌려줘!」','하고 분노한','용사(?)들은','왕을 혼내 주려고','도카폰 성으로','쳐들어갔습니다…']

def autocolor(b,t,x0,y0,w,h):
    import collections
    p=pal(b,t); c=collections.Counter(getpx(b,t,x,y) for y in range(y0,y0+h) for x in range(x0,x0+w))
    c.pop(0,None)
    lum=lambda i:p[i][0]*.3+p[i][1]*.59+p[i][2]*.11
    dark=[i for i,_ in c.most_common() if lum(i)<90]
    lite=[i for i,_ in c.most_common() if lum(i)>=90]
    return p[lite[0]],p[dark[0]] if dark else (0,0,0)
def names(b,t,items,fsize,sw=2,fname=BOLD):
    for (x0,x1,y0,y1),txt in items:
        f,s_=autocolor(b,t,x0,y0,x1-x0,y1-y0)
        fn,fs=fname,fsize
        if fn.startswith('Galmuri'):
            l,tp,r,bt=font(fn,fs).getbbox(txt,stroke_width=sw)
            if r-l>x1-x0-1: fn,fs='NanumSquareNeo-dEb.ttf',10
        rects_text(b,t,[(x0,y0,x1-x0,y1-y0)],txt,f,s_,fs,sw=sw,fname=fn); continue
        rects_text(b,t,[(x0,y0,x1-x0,y1-y0)],txt,f,s_,fsize,sw=sw,fname=fname)
def button(b,t,x0,x1,y0,y1,txt,fsize,fname=BOLD,col=None,sw=0,stroke=None):
    """배경을 가장 흔한 색으로 메우고 글자를 그 위에 그림"""
    import collections
    p=pal(b,t); c=collections.Counter(getpx(b,t,x,y) for y in range(y0,y1) for x in range(x0,x1))
    bg=c.most_common(1)[0][0]
    lum=lambda i:p[i][0]*.3+p[i][1]*.59+p[i][2]*.11
    if col is None: col=p[min(c,key=lum)]
    for y in range(y0,y1):
        for x in range(x0,x1): setpx(b,t,x,y,bg)
    im=render_text(x1-x0,y1-y0,txt,col,stroke or col,fsize,fname,sw)
    blit(b,t,im,x0,y0,clear=False)
GAL9='Galmuri9.ttf'; GAL11='Galmuri11.ttf'
def wood(b,t,x,y,w,h,txt,ins=(2,4),fname=None,cols=None,byidx=False,idx=None):
    """나무 버튼: 글자 픽셀을 같은 행의 나뭇결로 메운 뒤 원래 글자색으로 다시 씀"""
    import collections
    p=pal(b,t); ix,iy=ins
    X0,X1,Y0,Y1=x+ix,x+w-ix,y+iy,y+h-iy
    g=lambda xx,yy:getpx(b,t,xx,yy)
    woodset=set(g(xx,yy) for yy in (Y0-2,Y0-1,Y1,Y1+1) for xx in range(X0,X1))
    txtpx=[(xx,yy) for yy in range(Y0,Y1) for xx in range(X0,X1) if g(xx,yy) not in woodset]
    T=set(txtpx)
    edge=collections.Counter(); inner=collections.Counter()
    for xx,yy in txtpx:
        adj=any((xx+dx,yy+dy) not in T and X0<=xx+dx<X1 and Y0<=yy+dy<Y1 for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)))
        (edge if adj else inner)[g(xx,yy)]+=1
    if cols: fc,sc=cols
    else:
        sc=p[edge.most_common(1)[0][0]] if edge else (220,220,220)
        inn=[i for i,_ in inner.most_common() if p[i]!=sc]
        fc=p[inn[0]] if inn else (40,40,90)
    for yy in range(Y0,Y1):
        row=[g(xx,yy) for xx in range(X0,X1)]
        woodrow=[v for v in row if v in woodset] or [g(X0,Y0-1)]
        last=None;k=0
        for i,v in enumerate(row):
            if v in woodset: last=v
            else:
                if last is None:
                    nxt=[u for u in row[i:] if u in woodset]; last=nxt[0] if nxt else woodrow[0]
                setpx(b,t,X0+i,yy,last)
    for fn,fs in ((fname or GAL11,12),(GAL9,10)):
        f=font(fn,fs); l,tp,r,bt=f.getbbox(txt)
        if r-l<=w-6: break
    fi=si=None
    if idx: fi,si=idx
    elif byidx and inner and edge:
        # 게임은 이 시트를 여러 팔레트로 그리므로 색이 아니라 원본 글자의 색 번호를 그대로 쓴다
        si=edge.most_common(1)[0][0]
        ii=[i for i,_ in inner.most_common() if i!=si]
        fi=ii[0] if ii else None
    if fi is not None:
        im=render_text(w,h,txt,(255,0,0),(0,0,255),fs,fn,1); px=im.load()
        for yy in range(h):
            for xx in range(w):
                r_,g_,b_,a=px[xx,yy]
                if a<100: continue
                setpx(b,t,x+xx,y+yy,fi if r_>b_ else si)
        return fc,sc
    im=render_text(w,h,txt,fc,sc,fs,fn,1)
    blit(b,t,im,x,y,clear=False)
    return fc,sc
NAVY=(16,32,104)
def sheet_idx(b,t,boxes,ins=(2,4)):
    """시트 안 모든 버튼의 원본 글자 픽셀을 모아 (글자 색 번호, 테두리 색 번호)를 정함"""
    import collections
    E=collections.Counter(); I=collections.Counter(); ix,iy=ins
    g=lambda xx,yy:getpx(b,t,xx,yy)
    for x,y,w,h in boxes:
        X0,X1,Y0,Y1=x+ix,x+w-ix,y+iy,y+h-iy
        ws=set(g(xx,yy) for yy in (Y0-2,Y0-1,Y1,Y1+1) for xx in range(X0,X1))
        T=set((xx,yy) for yy in range(Y0,Y1) for xx in range(X0,X1) if g(xx,yy) not in ws)
        for xx,yy in T:
            adj=any((xx+dx,yy+dy) not in T for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)))
            (E if adj else I)[g(xx,yy)]+=1
    si=E.most_common(1)[0][0]
    fi=[i for i,_ in I.most_common() if i!=si][0]
    return fi,si
BTN={
 'BIN/S_ARMS.BIN':(2,[(0,32,'구입'),(48,32,'판매'),(96,32,'털기'),(144,32,'그만'),(192,32,'장비'),(0,56,'마법'),(48,56,'아이템')]),
 'BIN/S_MAGIC.BIN':(2,[(0,32,'구입'),(48,32,'판매'),(96,32,'털기'),(144,32,'그만'),(192,32,'장비'),(0,56,'공격마법'),(48,56,'방어마법'),(96,56,'마법'),(144,56,'아이템')]),
 'BIN/S_BANK.BIN':(2,[(0,32,'예금'),(48,32,'인출'),(96,32,'털기'),(144,32,'그만'),(192,32,'환전'),(0,56,'공격마법'),(48,56,'방어마법'),(96,56,'마법'),(144,56,'아이템')]),
 'BIN/S_ITEM.BIN':(2,[(0,32,'구입'),(48,32,'판매'),(96,32,'털기'),(144,32,'그만'),(192,32,'장비'),(0,56,'감정'),(48,56,'보물'),(96,56,'마법'),(144,56,'아이템')]),
 'BIN/S_CHURCH.BIN':(2,[(96,8,'워프'),(0,32,'참회'),(48,32,'치료'),(96,32,'그만')]),
 'BIN/S_INN.BIN':(2,[(0,32,'숙박'),(48,32,'그만')]),
 'BIN/VILLAGE.BIN':(1,[(0,32,'구입'),(48,32,'털기'),(96,32,'그만')]),
 'BIN/S_CASTLE.BIN':(1,[(120,64,'워프'),(168,64,'치료'),(120,88,'부활'),(168,88,'그만')]),
 'EVDAT/EVSHEEP.DAT':(0,[(120,64,'워프'),(168,64,'치료'),(120,88,'부활'),(168,88,'그만')]),
 'EVBIN/EV33.BIN':(1,[(0,0,'구입'),(48,0,'판매'),(96,0,'털기'),(144,0,'그만'),(192,0,'아이템'),(0,24,'마법'),(48,24,'보물'),(96,24,'장비')]),
}
BCOL={'BIN/S_MAGIC.BIN':((248,176,48),(48,16,8)),'BIN/S_MAGIC.BIN@':((248,176,48),(48,16,8)),'BIN/S_INN.BIN':((248,224,64),(16,16,16))}
PLQ=[('BIN/S_ARMS.BIN',2,12,6,56,22,'무기점'),('BIN/S_ITEM.BIN',2,14,8,52,20,'아이템점'),('BIN/S_CHURCH.BIN',2,12,6,44,20,'교회'),
     ('BIN/S_INN.BIN',2,20,5,36,22,'여관'),('BIN/S_MAGIC.BIN',2,12,5,56,22,'마법점'),
     ('BIN/VILLAGE.BIN',1,84,6,24,20,'마을'),('BIN/VILLAGE.BIN',1,78,64,18,16,'읍'),('BIN/VILLAGE.BIN',1,78,94,34,18,'도시')]
SKILL=['기모으기','원기','마력충전','마름쇠','시치미',
 '경질화','덥석','떠나기','화염','몸지키기',
 '가시돌기','독','안개','액체화','석화',
 '왕촌티','깨물기','부르르','사라지기','장비노림',
 '목노림','매료','간질간질','함성','공포',
 '노래','참철검','잠재우기','마력빼기','변신',
 '흡혈','회복광','빈틈찌름','급소찌름','날뛰기']
MAGIC=['메테오','메테오라','메테오다라','프리즈','프리즈라',
 '프리즈다라','플라스마','플라스마라','플라스다라','마호케스A',
 '마호케스D','배틀도리','배틀꾸벅',None,'제니겟',
 '도제니겟','에너겟','에너체인지','고투헬','텔레포잔',
 '배니싱','녹슬라','버서크','브레스','트위스터',
 '웨이브','퀘이크','일렉스파크','참철검','제니다운',
 '엄청메테오','엄청프리즈','초플라스마','기가드레인','소드댄서',
 '헤븐게이트','삼철검','칭칭','갓시프',None,
 '마호세이프','마호가드','마호귀환','원기쑥쑥','도원기쑥쑥',
 '마호타스','마호타스라','마호타다라','마호원기','마호봉인',
 '도마호봉인','매직풀','가드풀','마호단단','마호미러']
def apply(F):
    for f,(ti,lst) in BTN.items():
        b=F(f); t=scan(b)[ti]
        cols=BCOL.get(f,((48,40,112),(232,224,208)))
        ix=sheet_idx(b,t,[(x,y,48,24) for x,y,_ in lst])
        for x,y,txt in lst:
            c=wood(b,t,x,y,48,24,txt,cols=cols,idx=ix); cols=cols or c
    b=F('BATTLE/B_CMD.BIN'); t=scan(b)[0]
    for i,txt in enumerate(SKILL):
        x=(i%5)*48+(2 if i%5==4 else 0); y=128+(i//5)*16
        if len(txt)<=3: names(b,t,[((x,x+48,y,y+16),txt)],12,sw=0,fname=GAL11)
        else: names(b,t,[((x,x+48,y,y+16),txt)],10,sw=0,fname=GAL9)
    names(b,t,[((0,64,0,24),'공격'),((0,64,24,48),'방어')],22,sw=2)
    names(b,t,[((0,32,48,64),'항복')],12,sw=1,fname=GAL11)
    for x,y,w,h,txt in [(178,66,34,16,'선택'),(216,66,36,16,'결정'),(106,108,40,18,'선택')]: button(b,t,x,x+w,y,y+h,txt,12,GAL11,col=(255,255,255),sw=1,stroke=(40,16,96))
    button(b,t,178,240,89,100,'어느 걸로?',10,GAL9,col=(255,255,255),sw=1,stroke=(40,16,96))
    names(b,t,[((160,194,16,32),'카운터'),((194,226,16,32),'방어'),((160,194,32,48),'필살'),((194,226,32,48),'공격')],10,sw=1,fname=GAL9)
    t=scan(b)[1]
    for i,txt in enumerate(MAGIC):
        if txt is None: continue
        x=(i%5)*48+(2 if i%5==4 else 0); y=(i//5)*16
        names(b,t,[((x,x+48,y,y+16),txt)],10,sw=1,fname=GAL9)
    names(b,t,[((0,32,208,224),'매료'),((32,64,208,224),'공포'),((64,96,208,224),'금지'),((96,160,208,224),'함성')],12,sw=1,fname=GAL11)
    names(b,t,[((8,96,228,252),'제니다운')],16,sw=1)
    b=F('EVDAT/EVCASINO.DAT'); t=scan(b)[2]
    for k,txt in enumerate(['페어페어','셔플','하이&로우','그만']): wood(b,t,162,3+k*24,74,20,txt,ins=(1,1),cols=((104,104,104),(16,16,16)))
    b=F('DATA/WIN.DAT'); t=scan(b)[0]
    wood(b,t,9,113,16,16,'위',ins=(1,1),cols=((56,40,24),(212,188,132)))
    wood(b,t,47,210,17,15,'주',ins=(1,1),cols=((56,40,24),(212,188,132)))
    for f,ti,x,y,w,h,txt in PLQ:
        b=F(f); t=scan(b)[ti]; wood(b,t,x,y,w,h,txt,ins=(1,1),cols=BCOL.get(f+'@'),byidx=True)
    # 은행 카운터 위 금색 간판 '預金' → '예금' (배경색은 줄마다 원래 색 유지, 글자는 금색 번호)
    import collections
    b=F('BIN/S_BANK.BIN'); t=scan(b)[0]
    for yy in range(7,17):
        c=collections.Counter(getpx(b,t,xx,yy) for xx in range(74,116) if not 0x36<=getpx(b,t,xx,yy)<=0x3c).most_common(1)[0][0]
        for xx in range(74,116):
            if 0x36<=getpx(b,t,xx,yy)<=0x3c: setpx(b,t,xx,yy,c)
    im=render_text(40,10,'예금',(255,0,0),(0,0,255),12,GAL11,0); px=im.load()
    for yy in range(10):
        for xx in range(40):
            if px[xx,yy][3]>=100: setpx(b,t,75+xx,7+yy,0x3b if yy<5 else 0x39)
    # 성 화면 위 간판 'ドカポン城' → '도카폰성' (S_CASTLE·EVSHEEP 공통 시트, 바탕 d, 글자 9 + 밝은 그림자 f)
    for f,ti in (('BIN/S_CASTLE.BIN',1),('EVDAT/EVSHEEP.DAT',0)):
        b=F(f); t=scan(b)[ti]
        if getpx(b,t,150,124)==0: continue
        for yy in range(116,132):
            for xx in range(131,220):
                if getpx(b,t,xx,yy) in (9,10,11,14,15): setpx(b,t,xx,yy,13)
        im=render_text(78,15,'도카폰성',(255,0,0),(0,0,255),14,BOLD,0); px=im.load()
        on=lambda xx,yy:0<=xx<78 and 0<=yy<15 and px[xx,yy][3]>=100
        for yy in range(16):
            for xx in range(79):
                if on(xx,yy): setpx(b,t,139+xx,116+yy,9)
                elif on(xx-1,yy-1): setpx(b,t,139+xx,116+yy,15)
    # 아이템점 오른쪽 현수막 '鑑定' → '감정' (S_ITEM TIM0 x56~95,y128~183. 원 테두리(노랑)+보라 띠(41~46) 오른쪽이 안쪽)
    b=F('BIN/S_ITEM.BIN'); t=scan(b)[0]
    if getpx(b,t,64,129)==0x0e:
        k=10
        for yy in range(128,184):
            row=[getpx(b,t,xx,yy) for xx in range(56,96)]
            k=max((i for i,v in enumerate(row[:30]) if 0x41<=v<=0x46),default=k)
            for xx in range(56+k+1,96):
                if 0x04<=getpx(b,t,xx,yy)<=0x0e: setpx(b,t,xx,yy,3)
        # 현수막 윗부분 조각(x166~191,y128~159): 세로로 훑어 원 테두리 아래 안쪽의 옛 글자 획 제거
        for xx in range(166,192):
            col=[getpx(b,t,xx,yy) for yy in range(128,160)]
            s=next((i for i,v in enumerate(col) if v>=0x0c),None)
            if s is None: continue
            g=next((i for i in range(s,32) if col[i]<=0x04),32); g=min(g,s+5)
            for i in range(g,32):
                if 0x04<=col[i]<=0x0e: setpx(b,t,xx,128+i,3)
        for ch,x0,y0,fs in (('감',69,133,19),('정',77,157,17)):
            im=render_text(24,24,ch,(255,0,0),(0,0,255),fs,BOLD,0); px=im.load()
            on=lambda xx,yy:0<=xx<24 and 0<=yy<24 and px[xx,yy][3]>=100
            for yy in range(25):
                for xx in range(25):
                    X,Y=x0+xx,y0+yy
                    if X>95 or Y>183 or getpx(b,t,X,Y) not in (1,2,3,0x1f,0x41,0x42,0x43): continue
                    if on(xx,yy): setpx(b,t,X,Y,0x0e if yy<14 else 0x0c)
                    elif on(xx-1,yy) or on(xx,yy-1): setpx(b,t,X,Y,0x07)
    # 보드 지도의 마을 이름 간판 (F_00_FD.DAT 안 헤더 없는 4bpp 240x200 시트, 48x16 칸 5열×11줄, 실행파일 지명 목록 순서)
    b=F('DATA/F_00_FD.DAT'); o=0x1e6e0
    def lp(x,y,v=None):
        i=o+(y*240+x)//2; sh=(x&1)*4
        if v is None: return (b[i]>>sh)&15
        b[i]=(b[i]&~(15<<sh)&0xff)|(v<<sh)
    TOWN=['유로','노우스','라시안','트라리아','에이자','난키쿠','에프리카','사스','호렌소','파파세리',
     '피망','큐리','브로코리','바쿠사','라닥','후잉크','미드라','히카라베','파페루스','비트론',
     '우니우니','라이크','가완','아비완','마하치','에비아','시벳','파피','초코사','카키고리',
     '아이스라','라페','이잉카','카스테아','만야','무무','트란치','파이스','칠리페파','김치무',
     '카린','통가라','반자','비치','사하','코나츠','트로피카','차모로','텐카쿠','고주',
     '사샤피','에프엘','토키우','도마크']
    for k,txt in enumerate(TOWN):
        X=(k%5)*48; Y=28+(k//5)*16
        for yy in range(Y+2,Y+11):
            for xx in range(X+2,X+46): lp(xx,yy,1)
        im=render_text(44,10,txt,(255,0,0),(0,0,255),10,GAL9,0); px=im.load()
        on=lambda xx,yy:0<=xx<44 and 0<=yy<10 and px[xx,yy][3]>=100
        for yy in range(10):
            for xx in range(44):
                if on(xx,yy): lp(X+2+xx,Y+2+yy if yy<9 else Y+10,2)
                elif on(xx-1,yy-1) and Y+2+yy<=Y+10: lp(X+2+xx,Y+2+yy,9)
    b=F('BIN/INTROPI.DAT'); ts=scan(b); t=ts[1]
    rects_text(b,t,[(0,216,112,24)],'도카폰 하자!',(255,255,255),NAVY,17,sw=2)
    rects_text(b,t,[(112,216,88,24)],'이어서 하기',(255,255,255),NAVY,17,sw=2)
    rects_text(b,t,[(192,144,64,24)],'데이터',(255,255,255),NAVY,17,sw=2,align='l')
    rects_text(b,t,[(192,168,64,24)],' 보기!',(255,255,255),NAVY,17,sw=2,align='l')
    t=ts[0]
    names(b,t,[((2,71,172,192),'스콥'),((72,143,172,192),'브리킨'),((144,215,172,192),'발츠'),
               ((2,57,196,216),'우라라'),((58,112,196,216),'모르데'),((114,181,196,216),'우이우이'),
               ((2,72,218,240),'가마마루'),((74,111,218,240),'돈')],18)
    names(b,t,[((216,244,170,188),'특기'),((184,248,154,168),'프로필')],12,sw=1,fname=GAL11)
    t=ts[4]
    names(b,t,[((198,226,175,192),'특기'),((168,228,192,207),'프로필')],12,sw=1,fname=GAL11)
    t=ts[5]
    button(b,t,38,90,38,54,'삭  제',14)
    names(b,t,[((60,112,228,250),'1인용')],18)
    for i,lines in enumerate(TIT):
        b=F('DATA/S_TIT%02d.DAT'%i); t=scan(b)[0]
        relayout(b,t,lines,(255,255,255),(16,16,16),keep=1)
    b=F('EVDAT/EVOP.DAT'); ts=scan(b)
    relayout(b,ts[2],OP2,(255,255,255),(40,24,8),sw=2,margin=2,force='c')
    relayout(b,ts[3],OP3,(255,255,255),(40,24,8),sw=2,margin=2,force='c')

if __name__=='__main__':
    # 미리보기: python tools/gfx.py → shots/gfx_*.png
    import sys
    sys.path.insert(0,os.path.dirname(__file__))
    from tim import render
    files={}
    def F(p):
        if p not in files: files[p]=bytearray(open(os.path.join(W,'orig',p),'rb').read())
        return files[p]
    apply(F)
    for p,b in files.items():
        for i,t in enumerate(scan(b)):
            render(b,t).resize((size(t)[0]*2,size(t)[1]*2),Image.NEAREST).save(os.path.join(W,'shots','gfx_%s_%d.png'%(p.replace('/','_'),i)))
