import pdfplumber,sys,json
def col(c):
    if c is None: return '000000'
    if isinstance(c,(int,float)): c=(c,c,c)
    if len(c)==1: c=(c[0],)*3
    if len(c)==4:
        C,M,Y,K=c; c=((1-C)*(1-K),(1-M)*(1-K),(1-Y)*(1-K))
    return ''.join('%02X'%round(v*255) for v in c[:3])
def run(f):
    pdf=pdfplumber.open(f); L=[]
    for pn,pg in enumerate(pdf.pages):
        H=pg.height
        ch=[c for c in pg.chars if c['size']<40]
        ch.sort(key=lambda c:(round(c['bottom']),c['x0']))
        lines=[]
        for c in ch:
            b=c['bottom']
            for ln in lines:
                if abs(ln['b']-b)<3.2 and True: ln['c'].append(c); break
            else: lines.append({'b':b,'c':[c]})
        for ln in sorted(lines,key=lambda l:l['b']):
            cs=sorted(ln['c'],key=lambda c:c['x0'])
            spans=[]
            for c in cs:
                fn=c['fontname'].split('+')[-1]
                st=(col(c.get('non_stroking_color')),'B' if ('Bold' in fn) else '', 'I' if ('Italic' in fn or 'Oblique' in fn) else '', round(c['size'],1))
                if spans and spans[-1][1]==st[:3]: spans[-1][0]+=c['text']
                elif spans and c['text']==' ': spans[-1][0]+=' '
                else: spans.append([c['text'],st[:3],st[3]])
            txt=''.join(s[0] for s in spans)
            L.append({'p':pn,'y':round(ln['b'],1),'x0':round(cs[0]['x0'],1),'x1':round(cs[-1]['x1'],1),'H':H,'t':txt,'s':[[s[0],s[1][0],s[1][1]+s[1][2],s[2]] for s in spans]})
    return L
if __name__=='__main__':
    json.dump(run(sys.argv[1]),open(sys.argv[2],'w'),ensure_ascii=False)
