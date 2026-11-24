import json,re,glob,statistics,collections,sys
LAB={'CAMERA':'cam','CAM':'cam','LIGHT':'light','LIT':'light','SOUND':'sound','SND':'sound','SFX':'sound','MUSIC':'music','MUS':'music',
 'ACTING':'act','WARDROBE':'act','NOTE':'note','TIMING':'note','SEQ':'note','NGUỒN':'note','Ý NGHĨA CHÍNH TRỊ':'note','LOC':'loc','VO':'vo','VFX':'cam','PROP':'act','PROPS':'act'}
LABRE=re.compile(r'^\[(CAM|LIT|SND|MUS|ACT|SFX|VFX|NOTE|VO)\]:?\s*|^(Ý NGHĨA CHÍNH TRỊ|CAMERA|LIGHT|SOUND|MUSIC|ACTING|WARDROBE|NOTE|TIMING|SEQ|NGUỒN|LOC|VO|SFX|VFX|PROPS?)(?::|\s{1,}|$)(?!-)')
ACTRE=re.compile(r'^(ACT [IVX]+\b|CHƯƠNG [IVX]+\b|POST[ -]?CREDIT|EPILOGUE|HỒI [IVX]+\b)')
SCRE=re.compile(r'^(S\d{2}[a-zA-Z]?|PC)\s+(?:—\s+)?(.+?)\s*(\[[^\]]*\])?\s*$')
UP=re.compile(r"^[A-ZÀ-ỸĐ0-9 ,\.\-—'’\(\)/&:·]+$")
def isup(t): 
    t=t.strip(); return bool(t) and UP.match(t) and t.upper()==t and any(c.isalpha() for c in t)
def load(f):
    L=json.load(open(f))
    out=[]
    for l in L:
        t=l['t'].rstrip()
        if not t.strip(): continue
        if re.match(r'^(Quách Bốc chi loạn -|ArcII - EP|1214-1216$)',t.strip()) or (l['y']<58 and len(t.strip())<12):
            continue
        if set(t.strip())<=set('─—-'): l['hr']=1
        l['t']=t.strip(); out.append(l)
    return out
def parse(f):
    L=load(f)
    gaps=collections.Counter(round(b['y']-a['y']) for a,b in zip(L,L[1:]) if a['p']==b['p'] and 8<b['y']-a['y']<30)
    m=gaps.most_common(1)[0][0]
    thr=m+1.7
    xs=sorted(l['x1'] for l in L); R=xs[int(len(xs)*.9)]
    cx=collections.Counter(round(l['x0']) for l in L)
    lm=min(x for x,c in cx.items() if c>=len(L)*0.04)
    blocks=[];cur=None;prev=None
    def push(b):
        nonlocal cur; blocks.append(b); cur=b
    for l in L:
        t=l['t']; x0=l['x0']
        if l.get('hr'): push({'k':'hr'}); prev=l; continue
        gap = (l['y']-prev['y']) if prev and prev['p']==l['p'] else (99 if not prev else 0)
        prevshort = prev is not None and prev['x1'] < R-75
        newpage = prev is not None and prev['p']!=l['p']
        bold = l['s'][0][2].startswith('B') if l['s'] else False
        centered = x0>lm+60 and l['x1']<R-30
        m1=LABRE.match(t); a=ACTRE.match(t); s=SCRE.match(t)
        k=None
        if a and (bold or isup(t.split('[')[0])): push({'k':'act','t':t}); prev=l; continue
        if s and bold: push({'k':'scene','id':s.group(1),'t':s.group(2).strip(),'time':(s.group(3) or '').strip('[] '),'raw':t}); prev=l; continue
        if m1:
            lab=(m1.group(1) or m1.group(2)); cat=LAB.get(lab,'note')
            if m1.group(1)=='ACT': cat='act'; lab='ACTING'
            if m1.group(1): lab={'CAM':'CAMERA','LIT':'LIGHT','SND':'SOUND','MUS':'MUSIC'}.get(lab,lab)
            push({'k':'lab','c':cat,'l':lab,'t':t[m1.end():].strip()}); prev=l; continue
        if t.startswith(('→','·','•','- ')) :
            push({'k':'arrow' if t.startswith('→') else 'bullet','t':t.lstrip('→·•- ').strip()}); prev=l; continue
        # dialogue
        if x0>lm+15 and isup(t) and len(t)<45 and bold and not t.startswith('—'):
            push({'k':'dlg','who':t,'lines':[]}); prev=l; continue
        if cur and cur['k']=='dlg' and x0>lm+15 and gap<thr+6:
            if t.startswith('(') or (cur['lines'] and cur['lines'][-1][0]=='p' and not cur['lines'][-1][1].endswith(')')):
                if t.startswith('(') or (cur['lines'] and cur['lines'][-1][0]=='p'):
                    if cur['lines'] and cur['lines'][-1][0]=='p' and not cur['lines'][-1][1].endswith(')'): cur['lines'][-1][1]+=' '+t
                    else: cur['lines'].append(['p',t])
                    prev=l; continue
            if cur['lines'] and cur['lines'][-1][0]=='d' and gap<thr: cur['lines'][-1][1]+=' '+t
            else: cur['lines'].append(['d',t])
            prev=l; continue
        # slug
        if isup(t) and re.match(r'^(INTERIOR|EXTERIOR|INT\.|EXT\.|INT/EXT)',t): push({'k':'slug','t':t}); prev=l; continue
        cont = cur is not None and cur['k'] in ('p','lab','arrow','bullet','head','center') and 't' in cur and not prevshort and (gap<=thr if not newpage else True) and not (centered and cur['k']!='center')
        if cont and cur['k']=='head' and not bold: cont=False
        if cont:
            cur['t']+=' '+t
        else:
            if centered: push({'k':'center','t':t})
            elif bold and (isup(t) or len(t)<70): push({'k':'head','t':t})
            else: push({'k':'p','t':t})
        prev=l
    return blocks
if __name__=='__main__':
    out={}
    for f in sorted(glob.glob('L_*.json')):
        out[f[2:-5]]=parse(f)
    json.dump(out,open('parsed.json','w'),ensure_ascii=False,indent=0)
    for k,v in out.items(): print(k,len(v),collections.Counter(b['k'] for b in v))
