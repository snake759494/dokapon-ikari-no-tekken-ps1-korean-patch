# 한국어 번역 검증/폭 계산 공용 모듈
import re,json,os,sys
W=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
TOK=re.compile(r'\{[0-9a-f]{4}\}|⏎|.',re.S)
# 원본 글꼴에 있는 기호(코드 0x100~0x15f) - 전각 폭
BASE='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz！ヴ♥♛％○×△□＋－✕／？～＆：。．゜、・ー（）〈〉［］｛｝「」'
HALFP=",.!?'\""
ASCII_MAP={'~':'～','&':'＆',':':'：','%':'％','+':'＋','-':'－','/':'／','(':'（',')':'）','[':'［',']':'］'}
def norm(s):
    return ''.join(ASCII_MAP.get(c,c) for c in s)
def toks(s): return TOK.findall(s)
def codes(s): return [t for t in toks(s) if t.startswith('{')]
def units(s): return len(toks(norm(s)))
def is_hangul(c): return '가'<=c<='힣'
def width_lines(s):
    half=False; pages=[[0]]
    for t in toks(norm(s)):
        if t=='⏎': pages[-1].append(0); continue
        if t.startswith('{'):
            v=int(t[1:5],16)
            if v==0x9300: half=True
            elif v==0x9400: half=False
            elif v==0x9200: pages.append([0])
            elif v==0x81ff: pages[-1][-1]+=12
            elif (v>>8)==0x80: pages[-1][-1]+=4
            continue
        if t==' ' or t in HALFP: pages[-1][-1]+=1
        elif half and (t in BASE or t=='　'): pages[-1][-1]+=1
        else: pages[-1][-1]+=2
    return pages
def check(ja,ko,cap,w):
    errs=[]
    if re.search(r'[぀-ヺー-ヿ一-鿿]',ko): errs.append('일본어 문자 포함')
    # {81xx}(문자열 삽입)의 xx는 칸 폭이라 넓혀도 된다 → 종류만 비교
    nm=lambda c:c[:3]+'..}' if c[:3] in ('{81','{80') and c[3:5]!='ff' else c
    cj=[nm(c) for c in codes(ja) if c not in ('{9300}','{9400}')]
    ck=[nm(c) for c in codes(ko) if c not in ('{9300}','{9400}')]
    if cj!=ck: errs.append('제어코드 불일치 %s != %s'%(''.join(cj),''.join(ck)))
    if units(ko)>cap-1: errs.append('길이 초과 %d > %d'%(units(ko),cap-1))
    pj=width_lines(ja); pk=width_lines(ko)
    mw=max(max(p) for p in pk)
    if mw>max(w,4): errs.append('줄 폭 초과 %d > %d'%(mw,w))
    if len(pk)==len(pj):
        for a,b in zip(pj,pk):
            if len(b)>len(a): errs.append('페이지 줄 수 증가 %d > %d'%(len(b),len(a))); break
    bad=[c for c in norm(ko) if not (is_hangul(c) or c in BASE or c in ' …♥・「」×　' or c in HALFP or c in '⏎{}0123456789abcdef')]
    if bad: errs.append('허용되지 않는 문자 %r'%''.join(sorted(set(bad))))
    return errs
def load_ko(path):
    d={}
    for l in open(path,encoding='utf-8'):
        l=l.rstrip('\n')
        if not l or l.startswith('#'): continue
        k,v=l.split('\t',1); d[k]=v
    return d
if __name__=='__main__':
    # 사용: python tools/ko.py text/ko/파일.tsv  → 원문(ja.json)과 대조 검사
    J={e['id']:e for e in json.load(open(os.path.join(W,'text/ja.json'),encoding='utf-8'))}
    n=0
    for p in sys.argv[1:]:
        for k,v in load_ko(p).items():
            if k not in J: print('알 수 없는 id',k); n+=1; continue
            e=J[k]; er=check(e['ja'],v,e['cap'],e['w'])
            if er: n+=1; print(k,'|',' / '.join(er),'|',v)
    print('오류',n)
