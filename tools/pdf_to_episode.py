"""Chuyển một file PDF kịch bản (định dạng Full script v3) thành data/episodes/<id>.json.

Cách dùng (chạy trong thư mục loanquachboc/):
    pip install pdfplumber
    python3 tools/pdf_to_episode.py "Scpt_EP09_....pdf" ep09 EP09 "Tên tập" "Phụ đề" "Arc II" "9:30 · 12 scenes"

Script sẽ:
  - đọc PDF (màu chữ + vị trí dòng) bằng tools/lines.py
  - nhận diện ACT / Scene / CAMERA / LIGHT / SOUND / MUSIC / ACTING / NOTE / VO / thoại bằng tools/parse.py
  - gắn chip nhân vật theo từ khoá "kw" trong data/manifest.json
  - ghi data/episodes/<id>.json và thêm tập vào data/manifest.json (nếu chưa có)
Sau đó mở trang, bật ✎ Sửa để soát lại và chọn ảnh bối cảnh cho từng cảnh.
Định dạng PDF mới khác nhiều so với v3 thì có thể cần chỉnh parse.py.
"""
import sys, os, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lines, parse  # noqa: E402

def group_misc(items):
    out = []; i = 0
    while i < len(items):
        b = items[i]
        if b['k'] == 'lab' and not b['t'].strip():
            j = i + 1; li = []
            while j < len(items) and items[j]['k'] == 'bullet':
                li.append(items[j]['t']); j += 1
            nb = dict(b); nb['list'] = li; out.append(nb); i = j; continue
        if b['k'] in ('center', 'head') and 'OPENING QUOTE' in b.get('t', ''):
            j = i + 1; li = []
            while j < len(items) and items[j]['k'] in ('center', 'p') and len(li) < 6:
                li.append(items[j]['t']); j += 1
            out.append({'k': 'quote', 'lines': li}); i = j; continue
        out.append(b); i += 1
    return out

def norm_front(bl):
    out = []
    for b in bl:
        b = dict(b)
        if b['k'] == 'scene': b = {'k': 'p', 't': b.get('raw', b['id'] + ' ' + b['t'])}
        if b['k'] == 'dlg': b = {'k': 'center', 't': ' · '.join([b['who']] + [x[1] for x in b['lines']])}
        out.append(b)
    return out

def main():
    if len(sys.argv) < 4:
        print(__doc__); sys.exit(1)
    pdf, eid, code = sys.argv[1], sys.argv[2], sys.argv[3]
    title = sys.argv[4] if len(sys.argv) > 4 else code
    sub = sys.argv[5] if len(sys.argv) > 5 else ''
    arc = sys.argv[6] if len(sys.argv) > 6 else 'Arc II'
    meta = sys.argv[7] if len(sys.argv) > 7 else ''
    root = os.path.dirname(HERE)
    tmp = os.path.join(root, '.tmp_lines.json')
    json.dump(lines.run(pdf), open(tmp, 'w'), ensure_ascii=False)
    bl = parse.parse(tmp); os.remove(tmp)
    fa = next((i for i, x in enumerate(bl) if x['k'] == 'act'), 0)
    pn = next((i for i, x in enumerate(bl) if i > fa and x['k'] == 'head' and re.match(r'^PRODUCTION NOTES', x['t'])), len(bl))
    front = group_misc(norm_front(bl[:fa])); back = norm_front(bl[pn:])
    acts = []; act = None; scene = None
    for b in bl[fa:pn]:
        if b['k'] == 'act':
            m = re.match(r'^(.*?)\s*\[([^\]]+)\]\s*$', b['t'])
            act = {'t': (m.group(1) if m else b['t']).strip(), 'time': (m.group(2) if m else ''), 'intro': [], 'scenes': []}
            acts.append(act); scene = None; continue
        if act is None:
            act = {'t': 'ACT I', 'time': '', 'intro': [], 'scenes': []}; acts.append(act)
        if b['k'] == 'scene':
            scene = {'id': b['id'], 't': b['t'], 'time': b.get('time', ''), 'loc': '', 'items': []}
            act['scenes'].append(scene); continue
        if b['k'] == 'hr': continue
        if scene is not None:
            if b['k'] == 'lab' and b['l'] == 'LOC' and not scene['loc']:
                scene['loc'] = b['t']; continue
            scene['items'].append(b)
        else:
            act['intro'].append(b)
    man_path = os.path.join(root, 'data', 'manifest.json')
    man = json.load(open(man_path))
    alltext = ''
    for a in acts:
        a['intro'] = group_misc(a['intro'])
        for s in a['scenes']:
            s['items'] = group_misc(s['items'])
            txt = json.dumps(s, ensure_ascii=False); alltext += txt
            s['chips'] = [c['id'] for c in man['characters'] if any(k in txt for k in c.get('kw', []))]
    cast = [c['id'] for c in man['characters'] if sum(alltext.count(k) for k in c.get('kw', [])) >= 2]
    ep = dict(id=eid, code=code, title=title, sub=sub, arc=arc, meta=meta, front=front, acts=acts, back=back, cast=cast, rev=1)
    out = os.path.join(root, 'data', 'episodes', eid + '.json')
    json.dump(ep, open(out, 'w'), ensure_ascii=False, indent=1)
    if not any(e['id'] == eid for e in man['episodes']):
        man['episodes'].append({'id': eid, 'file': 'data/episodes/' + eid + '.json'})
        json.dump(man, open(man_path, 'w'), ensure_ascii=False, indent=1)
    n = sum(len(a['scenes']) for a in acts)
    print(f'Đã ghi {out}: {len(acts)} act, {n} scene.')

if __name__ == '__main__':
    main()
